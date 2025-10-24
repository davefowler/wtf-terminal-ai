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
            # Return streaming response
            response = model_obj.prompt(prompt, stream=True)
            return response
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
    llm_tools = []
    for tool_def in get_tool_definitions():
        tool_name = tool_def["name"]
        tool_impl = TOOLS[tool_name]

        llm_tool = llm.Tool(
            name=tool_name,
            description=tool_def["description"],
            input_schema=tool_def["parameters"],
            implementation=tool_impl
        )
        llm_tools.append(llm_tool)

    # Agent loop
    all_tool_calls = []
    tool_results = []
    iteration = 0

    try:
        while iteration < max_iterations:
            iteration += 1

            # Query model with tools
            response = model_obj.prompt(
                prompt=prompt if iteration == 1 else None,
                system=system_prompt,
                tools=llm_tools,
                tool_results=tool_results if tool_results else None,
                stream=False
            )

            # Check if model wants to use tools
            if response.tool_calls:
                # Execute tool calls
                new_tool_results = []

                for tool_call in response.tool_calls:
                    tool_name = tool_call.name
                    tool_args = tool_call.parameters

                    # Execute the tool
                    tool_func = TOOLS.get(tool_name)
                    if tool_func:
                        result = tool_func(**tool_args)

                        # Track this tool call
                        all_tool_calls.append({
                            "name": tool_name,
                            "arguments": tool_args,
                            "result": result,
                            "iteration": iteration
                        })

                        # Create tool result for next iteration
                        new_tool_results.append(
                            llm.ToolResult(
                                tool_call=tool_call,
                                result=str(result)
                            )
                        )

                # Update tool_results for next iteration
                tool_results = new_tool_results
            else:
                # No more tool calls - agent provided final response
                return {
                    "response": response.text(),
                    "tool_calls": all_tool_calls,
                    "iterations": iteration
                }

        # Hit max iterations
        return {
            "response": response.text() if response else "Maximum iterations reached",
            "tool_calls": all_tool_calls,
            "iterations": iteration
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
