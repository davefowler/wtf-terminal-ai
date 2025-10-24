"""AI client for querying language models."""

import os
from typing import Iterator, Union, Optional, Dict, Any
import llm

from wtf.ai.errors import (
    NetworkError,
    InvalidAPIKeyError,
    RateLimitError,
    parse_api_error,
    query_ai_with_retry,
)


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
