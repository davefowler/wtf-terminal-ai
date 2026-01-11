"""AI client for querying language models."""

import os
import sys
from typing import Iterator, Union, Optional, Dict, Any, List
import llm

from wtf.ai.errors import (
    NetworkError,
    InvalidAPIKeyError,
    RateLimitError,
    parse_api_error,
    query_ai_with_retry,
)
from wtf.ai.tools import TOOLS, get_tool_definitions, detect_native_search_support


class StuckLoopError(Exception):
    """Raised when the agent appears to be stuck in a loop."""
    pass



def query_ai_with_tools(
    prompt: str,
    config: Dict[str, Any],
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    max_iterations: int = 20,
    env_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Query AI with tool support - agent can use tools in a loop.

    The agent runs in iterations:
    1. Agent responds or requests tool calls
    2. Tools execute (some print output, some are internal)
    3. Tool results go back to agent
    4. Loop until agent provides final response (max 20 iterations)

    Includes stuck-loop detection: if the same tool is called 3+ times
    with identical arguments, we abort early to prevent infinite loops.

    Args:
        prompt: User's query/prompt
        config: Configuration dictionary
        system_prompt: System prompt (optional)
        model: Optional model override
        max_iterations: Max tool call loops (default: 20)
        env_context: Optional environment context for tool filtering

    Returns:
        Dict with:
        - response: Final agent response text
        - tool_calls: List of all tool calls made
        - iterations: Number of iterations used
    """
    # Get API configuration
    api_config = config.get('api', {})
    key_source = api_config.get('key_source', 'llm')  # Default to llm's key management
    configured_model = model or api_config.get('model')

    if not configured_model:
        raise ValueError("No model configured. Run 'wtf --setup' to configure.")

    # Detect native search support
    provider, has_native_search = detect_native_search_support(configured_model)
    debug = os.environ.get('WTF_DEBUG') == '1'
    
    if debug:
        print(f"[DEBUG] Model: {configured_model}, Provider: {provider}, Native search: {has_native_search}", file=sys.stderr)

    # Get model - llm library handles key management unless we override
    try:
        # For OpenAI search models, we may need to use a base model and override model_id
        base_model_name = configured_model
        if provider == "openai_search":
            # Use gpt-4o as base since llm might not know about search models yet
            try:
                model_obj = llm.get_model(configured_model)
            except Exception:
                # Fall back to gpt-4o and override the model_id
                if "mini" in configured_model:
                    model_obj = llm.get_model("gpt-4o-mini")
                else:
                    model_obj = llm.get_model("gpt-4o")
                model_obj.model_id = configured_model
                if debug:
                    print(f"[DEBUG] Using {model_obj.model_id} (overridden from base)", file=sys.stderr)
        else:
            model_obj = llm.get_model(configured_model)

        # Only override key if explicitly stored in config (not recommended)
        if key_source == 'config':
            api_key = api_config.get('key')
            if api_key and hasattr(model_obj, 'key'):
                model_obj.key = api_key

        # Otherwise let llm handle keys (from env vars or `llm keys set`)

    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "authentication" in error_msg.lower():
            raise InvalidAPIKeyError(
                f"API key not configured for model '{configured_model}'. "
                f"Set environment variable or use: llm keys set <provider>",
                provider=configured_model.split("-")[0] if "-" in configured_model else "unknown"
            )
        raise NetworkError(f"Failed to load model '{configured_model}': {e}")

    # Create llm.Tool objects from our tool definitions
    # Wrap tool implementations to handle dict returns
    # Pass model name to filter out custom search tools when native search is available
    llm_tools = []
    tool_definitions = get_tool_definitions(env_context, model_name=configured_model)
    if debug:
        print(f"[DEBUG] Creating tools from {len(tool_definitions)} definitions", file=sys.stderr)
    for tool_def in tool_definitions:
        tool_name = tool_def["name"]
        tool_impl = TOOLS[tool_name]
        if debug:
            print(f"[DEBUG] Registering tool: {tool_name}", file=sys.stderr)

        # Wrapper to convert dict returns to strings
        def make_wrapper(func):
            def wrapper(*args, **kwargs):
                from wtf.ai.tools import UserCancelledError
                try:
                    result = func(*args, **kwargs)
                except UserCancelledError:
                    # Re-raise user cancellation - don't convert to string
                    raise
                # If tool returns dict, convert to string
                if isinstance(result, dict):
                    # Check for error first
                    if 'error' in result and result['error']:
                        return f"Error: {result['error']}"
                    # Then check for specific fields
                    elif 'output' in result:
                        return result['output']
                    elif 'results' in result:
                        return result['results'] or "(no results)"
                    elif 'message' in result:
                        return result['message']
                    elif 'content' in result:
                        return result['content'] or "(empty)"
                    elif 'value' in result:
                        import json
                        return json.dumps(result['value'], indent=2)
                    elif 'matches' in result:
                        return '\n'.join(result['matches']) if result['matches'] else "(no matches)"
                    elif 'files' in result:
                        return '\n'.join(result['files']) if result['files'] else "(no files found)"
                    elif 'entries' in result:
                        import json
                        return json.dumps(result['entries'], indent=2)
                    else:
                        # Convert whole dict to string
                        import json
                        return json.dumps(result, indent=2)
                return str(result)
            wrapper.__name__ = func.__name__
            return wrapper

        llm_tool = llm.Tool(
            name=tool_name,
            description=tool_def["description"],
            input_schema=tool_def["parameters"],
            implementation=make_wrapper(tool_impl)
        )
        llm_tools.append(llm_tool)
        if debug:
            print(f"[DEBUG] Tool {tool_name} registered successfully", file=sys.stderr)

    if debug:
        print(f"[DEBUG] Total tools registered: {len(llm_tools)}", file=sys.stderr)

    # Use llm library's built-in tool execution
    # The tools have implementations, so llm will execute them automatically
    all_tool_calls = []

    # Store original tool functions for tracking
    original_tools = {tool_def["name"]: TOOLS[tool_def["name"]] for tool_def in get_tool_definitions()}

    # Tool descriptions for progress messages
    tool_descriptions = {
        "duckduckgo_search": "🔍 Searching the web...",
        "tavily_search": "🔍 Searching the web...",
        "serper_search": "🔍 Searching the web...",
        "brave_search": "🔍 Searching the web...",
        "bing_search": "🔍 Searching the web...",
        "read_file": "📄 Reading file...",
        "run_command": "⚡ Running command...",
        "grep": "🔎 Searching files...",
        "glob_files": "📂 Finding files...",
        "get_git_info": "📊 Checking git status...",
    }
    
    # Show progress BEFORE tool runs
    def before_tool_call(tool: llm.Tool, tool_call: llm.ToolCall):
        """Show progress indicator before tool executes."""
        from rich.console import Console
        console = Console()
        
        if tool and tool.name in tool_descriptions:
            console.print(f"[dim]{tool_descriptions[tool.name]}[/dim]")

    # Track tool usage with callbacks (after tool completes)
    def after_tool_call(tool: llm.Tool, tool_call: llm.ToolCall, result: llm.ToolResult):
        """Track tool calls and detect stuck loops."""
        import json
        
        debug = os.environ.get('WTF_DEBUG') == '1'
        if debug:
            print(f"[DEBUG] after_tool_call FIRED: tool={tool.name}", file=sys.stderr)

        # Get the result from the tool call (don't re-call it!)
        # The result is already available from the llm library
        result_output = result.output if hasattr(result, 'output') else str(result)
        
        # Try to parse as JSON if it looks like a dict
        try:
            import json
            if result_output.strip().startswith('{'):
                original_result = json.loads(result_output)
            else:
                original_result = {"output": result_output}
        except:
            original_result = {"output": result_output}

        current_args = tool_call.arguments if hasattr(tool_call, 'arguments') else {}
        
        all_tool_calls.append({
            "name": tool.name,
            "arguments": current_args,
            "result": original_result if isinstance(original_result, dict) else {"output": str(original_result)},
            "iteration": len(all_tool_calls) + 1
        })

        if debug:
            print(f"[DEBUG] Tracked tool call #{len(all_tool_calls)}: {tool.name}", file=sys.stderr)

        # Stuck loop detection: check if last 3 calls are identical
        if len(all_tool_calls) >= 3:
            last_3 = all_tool_calls[-3:]
            # Check if all 3 have same name and arguments
            try:
                first_sig = (last_3[0]["name"], json.dumps(last_3[0]["arguments"], sort_keys=True))
                all_same = all(
                    (c["name"], json.dumps(c["arguments"], sort_keys=True)) == first_sig
                    for c in last_3
                )
                if all_same:
                    print(f"[WARNING] Stuck loop detected: {tool.name} called 3x with same args", file=sys.stderr)
                    raise StuckLoopError(
                        f"Agent appears stuck - '{tool.name}' called 3 times with identical arguments. "
                        f"Try rephrasing your request or breaking it into smaller steps."
                    )
            except (TypeError, json.JSONDecodeError):
                pass  # Can't serialize args, skip check

    try:
        # Create conversation with automatic tool execution
        debug = os.environ.get('WTF_DEBUG') == '1'

        if debug:
            print(f"[DEBUG] Creating conversation with {len(llm_tools)} tools", file=sys.stderr)
            print(f"[DEBUG] Tool names: {[t.name for t in llm_tools]}", file=sys.stderr)

        conversation = model_obj.conversation(
            tools=llm_tools,
            before_call=before_tool_call,
            after_call=after_tool_call,
            chain_limit=max_iterations  # Limit tool chaining
        )

        if debug:
            print(f"[DEBUG] Conversation created, has tools: {hasattr(conversation, 'tools')}", file=sys.stderr)
            print(f"[DEBUG] Conversation tools count: {len(conversation.tools) if hasattr(conversation, 'tools') else 'N/A'}", file=sys.stderr)

        # Use chain() for automatic tool execution, not prompt()!

        if debug:
            print(f"[DEBUG] About to call conversation.chain()", file=sys.stderr)
            print(f"[DEBUG] Prompt length: {len(prompt)}", file=sys.stderr)
            print(f"[DEBUG] System prompt length: {len(system_prompt) if system_prompt else 0}", file=sys.stderr)

        response = conversation.chain(
            prompt=prompt,
            system=system_prompt
        )

        if debug:
            print(f"[DEBUG] Chain returned, response type: {type(response)}", file=sys.stderr)

        # response.text() is where tools actually execute!
        response_text = response.text()

        # NOW tool calls are populated
        if debug:
            print(f"[DEBUG] After response.text(), tool calls tracked: {len(all_tool_calls)}", file=sys.stderr)
            print(f"[DEBUG] Response text length: {len(response_text)}", file=sys.stderr)
            print(f"[DEBUG] Response preview: {response_text[:100] if response_text else '(empty)'}...", file=sys.stderr)

        return {
            "response": response_text,
            "tool_calls": all_tool_calls,
            "iterations": len(all_tool_calls) + 1
        }

    except Exception as e:
        # Extract provider from model name for error reporting
        provider = configured_model.split("-")[0] if "-" in configured_model else "unknown"
        wtf_error = parse_api_error(e, provider)
        raise wtf_error


