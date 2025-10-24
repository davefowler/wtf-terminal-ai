"""Error handling and retry logic for AI queries."""

import time
from typing import Callable, Any, Dict, Optional


class WtfAIError(Exception):
    """Base exception for wtf AI errors."""
    pass


class RateLimitError(WtfAIError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, message: str, retry_after: Optional[int] = None):
        """
        Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
        """
        super().__init__(message)
        self.retry_after = retry_after


class NetworkError(WtfAIError):
    """Raised when network request fails."""
    pass


class InvalidAPIKeyError(WtfAIError):
    """Raised when API key is invalid or missing."""

    def __init__(self, message: str, provider: Optional[str] = None):
        """
        Initialize invalid API key error.

        Args:
            message: Error message
            provider: AI provider name (anthropic, openai, google)
        """
        super().__init__(message)
        self.provider = provider


def query_ai_with_retry(
    query_func: Callable,
    prompt: str,
    config: Dict[str, Any],
    max_retries: int = 3,
    base_delay: float = 1.0,
    **kwargs
) -> str:
    """
    Query AI with automatic retry on transient failures.

    Args:
        query_func: Function to call for querying AI
        prompt: Prompt to send to AI
        config: Configuration dictionary
        max_retries: Maximum number of retries (default: 3)
        base_delay: Base delay in seconds for exponential backoff (default: 1.0)
        **kwargs: Additional arguments to pass to query_func

    Returns:
        AI response string

    Raises:
        InvalidAPIKeyError: If API key is invalid (no retry)
        NetworkError: If network fails after all retries
        RateLimitError: If rate limited after all retries
    """
    last_error = None

    for attempt in range(max_retries + 1):  # Initial try + retries
        try:
            return query_func(prompt, config, **kwargs)

        except InvalidAPIKeyError:
            # Don't retry on API key errors
            raise

        except RateLimitError as e:
            last_error = e
            if attempt < max_retries:
                # Use retry_after if provided, otherwise use exponential backoff
                wait_time = e.retry_after if e.retry_after else base_delay * (2 ** attempt)
                time.sleep(wait_time)
                continue
            raise

        except NetworkError as e:
            last_error = e
            if attempt < max_retries:
                # Exponential backoff: base_delay, base_delay*2, base_delay*4, ...
                wait_time = base_delay * (2 ** attempt)
                time.sleep(wait_time)
                continue
            raise

        except Exception as e:
            # Wrap unknown errors as NetworkError
            last_error = NetworkError(f"Unexpected error: {str(e)}")
            if attempt < max_retries:
                wait_time = base_delay * (2 ** attempt)
                time.sleep(wait_time)
                continue
            raise last_error

    # This should not be reached, but just in case
    if last_error:
        raise last_error
    raise NetworkError("Query failed after all retries")


def parse_api_error(error: Exception, provider: str) -> WtfAIError:
    """
    Parse API provider error and convert to wtf error type.

    Args:
        error: Exception from API provider
        provider: AI provider name

    Returns:
        Appropriate WtfAIError subclass
    """
    error_str = str(error).lower()

    # Check for rate limit
    if "rate limit" in error_str or "429" in error_str:
        # Try to extract retry_after
        retry_after = None
        if "retry after" in error_str:
            # Simple extraction, can be improved
            try:
                parts = error_str.split("retry after")
                if len(parts) > 1:
                    retry_after = int(parts[1].split()[0])
            except (ValueError, IndexError):
                pass
        return RateLimitError(f"Rate limit exceeded for {provider}", retry_after=retry_after)

    # Check for invalid API key
    if any(keyword in error_str for keyword in ["api key", "unauthorized", "401", "403", "authentication"]):
        return InvalidAPIKeyError(f"Invalid API key for {provider}", provider=provider)

    # Check for network errors
    if any(keyword in error_str for keyword in ["connection", "timeout", "network", "unreachable"]):
        return NetworkError(f"Network error when connecting to {provider}: {str(error)}")

    # Default to network error
    return NetworkError(f"Error from {provider}: {str(error)}")
