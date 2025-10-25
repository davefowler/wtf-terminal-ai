"""AI client for querying language models."""

import os
from typing import Iterator, Union, Optional, Dict, Any, List
import llm

from wtf.ai.errors import (
    NetworkError,
    InvalidAPIKeyError,
    RateLimitError,
    parse_api_error,
    query_ai_with_retry,
)
from wtf.ai.tools import TOOLS, get_tool_definitions



def query_ai_with_tools(
    prompt: str,
    config: Dict[str, Any],
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    max_iterations: int = 10,
    env_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Query AI with tool support - agent can use tools in a loop.

    The agent runs in iterations:
    1. Agent responds or requests tool calls
    2. Tools execute (some print output, some are internal)
    3. Tool results go back to agent
    4. Loop until agent provides final response (max 10 iterations)

    Args:
        prompt: User's query/prompt
        config: Configuration dictionary
        system_prompt: System prompt (optional)
        model: Optional model override
        max_iterations: Max tool call loops (default: 10)
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

    # Get model - llm library handles key management unless we override
    try:
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
    import sys
    debug = os.environ.get('WTF_DEBUG') == '1'
    llm_tools = []
    tool_definitions = get_tool_definitions(env_context)
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
                result = func(*args, **kwargs)
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

    # Track tool usage with callbacks
    def after_tool_call(tool: llm.Tool, tool_call: llm.ToolCall, result: llm.ToolResult):
        """Track tool calls for our records."""
        debug = os.environ.get('WTF_DEBUG') == '1'
        if debug:
            import sys
            print(f"[DEBUG] after_tool_call FIRED: tool={tool.name}", file=sys.stderr)

        # Get the original function result (as dict) by calling it again
        # This is a bit wasteful but ensures we track the proper structure
        tool_func = original_tools.get(tool.name)
        if tool_func:
            try:
                original_result = tool_func(**tool_call.arguments)
            except:
                original_result = {"output": result.output if hasattr(result, 'output') else str(result)}
        else:
            original_result = {"output": result.output if hasattr(result, 'output') else str(result)}

        all_tool_calls.append({
            "name": tool.name,
            "arguments": tool_call.arguments if hasattr(tool_call, 'arguments') else {},
            "result": original_result if isinstance(original_result, dict) else {"output": str(original_result)},
            "iteration": len(all_tool_calls) + 1
        })

        if debug:
            print(f"[DEBUG] Tracked tool call #{len(all_tool_calls)}: {tool.name}", file=sys.stderr)

    try:
        # Create conversation with automatic tool execution
        debug = os.environ.get('WTF_DEBUG') == '1'

        if debug:
            import sys
            print(f"[DEBUG] Creating conversation with {len(llm_tools)} tools", file=sys.stderr)
            print(f"[DEBUG] Tool names: {[t.name for t in llm_tools]}", file=sys.stderr)

        conversation = model_obj.conversation(
            tools=llm_tools,
            after_call=after_tool_call,
            chain_limit=max_iterations  # Limit tool chaining
        )

        if debug:
            print(f"[DEBUG] Conversation created, has tools: {hasattr(conversation, 'tools')}", file=sys.stderr)
            print(f"[DEBUG] Conversation tools count: {len(conversation.tools) if hasattr(conversation, 'tools') else 'N/A'}", file=sys.stderr)

        # Use chain() for automatic tool execution, not prompt()!
        import sys
        debug = os.environ.get('WTF_DEBUG') == '1'

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


