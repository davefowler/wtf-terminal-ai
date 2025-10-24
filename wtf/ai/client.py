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


def query_ai(
    prompt: str,
    config: Dict[str, Any],
    model: Optional[str] = None,
    stream: bool = True
) -> Union[str, Iterator[str]]:
    """
    Query the AI model with the given prompt.

    Args:
        prompt: The prompt to send to the AI
        config: Configuration dictionary with API settings
        model: Optional model override (uses config default if not provided)
        stream: Whether to stream the response (default: True)

    Returns:
        If stream=True: Iterator yielding response chunks
        If stream=False: Complete response string

    Raises:
        ValueError: If API key is not configured
        Exception: If API call fails
    """
    # Get API configuration
    api_config = config.get('api', {})
    provider = api_config.get('provider', 'anthropic')
    key_source = api_config.get('key_source', 'env')
    configured_model = model or api_config.get('model')

    # Get API key
    if key_source == 'env':
        # Load from environment variable
        env_var_map = {
            'anthropic': 'ANTHROPIC_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'google': 'GOOGLE_API_KEY'
        }
        env_var = env_var_map.get(provider)
        api_key = os.environ.get(env_var) if env_var else None

        if not api_key:
            raise InvalidAPIKeyError(
                f"API key not found in environment variable {env_var}. "
                f"Please set it or run 'wtf --setup' to configure.",
                provider=provider
            )
    else:
        # Load from config
        api_key = api_config.get('key')
        if not api_key:
            raise InvalidAPIKeyError(
                "API key not configured. Please run 'wtf --setup' to configure.",
                provider=provider
            )

    # Get the model using llm library
    try:
        model_obj = llm.get_model(configured_model)

        # Set API key if needed
        if hasattr(model_obj, 'key') and api_key:
            model_obj.key = api_key

    except Exception as e:
        raise NetworkError(f"Failed to load model '{configured_model}': {e}")

    # Query the model
    try:
        if stream:
            # Return streaming response iterator
            response = model_obj.prompt(prompt, stream=True)
            return response.stream()
        else:
            # Return complete response
            response = model_obj.prompt(prompt)
            return response.text()

    except Exception as e:
        # Parse and re-raise as appropriate error type
        wtf_error = parse_api_error(e, provider)
        raise wtf_error


def query_ai_safe(
    prompt: str,
    config: Dict[str, Any],
    model: Optional[str] = None,
    stream: bool = True,
    max_retries: int = 3
) -> Union[str, Iterator[str]]:
    """
    Query AI with automatic retry logic for transient failures.

    This is a wrapper around query_ai() that adds retry logic with exponential
    backoff for network errors and rate limiting.

    Args:
        prompt: The prompt to send to the AI
        config: Configuration dictionary with API settings
        model: Optional model override
        stream: Whether to stream the response
        max_retries: Maximum number of retries (default: 3)

    Returns:
        AI response (string or iterator)

    Raises:
        InvalidAPIKeyError: If API key is invalid (not retried)
        NetworkError: If network fails after all retries
        RateLimitError: If rate limited after all retries
    """
    return query_ai_with_retry(
        query_func=query_ai,
        prompt=prompt,
        config=config,
        max_retries=max_retries,
        model=model,
        stream=stream
    )


def query_ai_with_tools(
    prompt: str,
    config: Dict[str, Any],
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    max_iterations: int = 10
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

    Returns:
        Dict with:
        - response: Final agent response text
        - tool_calls: List of all tool calls made
        - iterations: Number of iterations used
    """
    # Get API configuration
    api_config = config.get('api', {})
    provider = api_config.get('provider', 'anthropic')
    key_source = api_config.get('key_source', 'env')
    configured_model = model or api_config.get('model')

    # Get API key
    if key_source == 'env':
        env_var_map = {
            'anthropic': 'ANTHROPIC_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'google': 'GOOGLE_API_KEY'
        }
        env_var = env_var_map.get(provider)
        api_key = os.environ.get(env_var) if env_var else None

        if not api_key:
            raise InvalidAPIKeyError(
                f"API key not found in environment variable {env_var}",
                provider=provider
            )
    else:
        api_key = api_config.get('key')
        if not api_key:
            raise InvalidAPIKeyError("API key not configured", provider=provider)

    # Get model
    try:
        model_obj = llm.get_model(configured_model)
        if hasattr(model_obj, 'key') and api_key:
            model_obj.key = api_key
    except Exception as e:
        raise NetworkError(f"Failed to load model '{configured_model}': {e}")

    # Create llm.Tool objects from our tool definitions
    # Wrap tool implementations to handle dict returns
    import sys
    debug = os.environ.get('WTF_DEBUG') == '1'
    llm_tools = []
    if debug:
        print(f"[DEBUG] Creating tools from {len(get_tool_definitions())} definitions", file=sys.stderr)
    for tool_def in get_tool_definitions():
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
                    if 'output' in result:
                        return result['output']
                    elif 'content' in result:
                        return result['content'] or "(empty)"
                    elif 'matches' in result:
                        return '\n'.join(result['matches']) if result['matches'] else "(no matches)"
                    elif 'files' in result:
                        return '\n'.join(result['files']) if result['files'] else "(no files found)"
                    elif 'error' in result and result['error']:
                        return f"Error: {result['error']}"
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
        wtf_error = parse_api_error(e, provider)
        raise wtf_error


def test_api_connection(config: Dict[str, Any]) -> bool:
    """
    Test if the API connection works.

    Args:
        config: Configuration dictionary with API settings

    Returns:
        True if connection successful, False otherwise
    """
    try:
        response = query_ai(
            "Say 'OK' if you can read this.",
            config=config,
            stream=False
        )
        return bool(response)
    except Exception:
        return False
