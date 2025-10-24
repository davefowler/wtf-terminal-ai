"""Tests for error handling and retry logic."""

import pytest
import time
from unittest.mock import patch, Mock

from wtf.ai.errors import (
    RateLimitError,
    NetworkError,
    InvalidAPIKeyError,
    query_ai_with_retry,
)


def test_rate_limit_error():
    """Test RateLimitError exception."""
    error = RateLimitError("Rate limit exceeded", retry_after=60)
    assert "Rate limit exceeded" in str(error)
    assert error.retry_after == 60


def test_network_error():
    """Test NetworkError exception."""
    error = NetworkError("Connection timeout")
    assert "Connection timeout" in str(error)


def test_invalid_api_key_error():
    """Test InvalidAPIKeyError exception."""
    error = InvalidAPIKeyError("Invalid API key", provider="openai")
    assert "Invalid API key" in str(error)
    assert error.provider == "openai"


def test_query_ai_with_retry_success():
    """Test successful query without retries."""
    mock_query = Mock(return_value="Success response")

    result = query_ai_with_retry(
        query_func=mock_query,
        prompt="test prompt",
        config={"api": {"provider": "openai"}},
        max_retries=3
    )

    assert result == "Success response"
    assert mock_query.call_count == 1


def test_query_ai_with_retry_network_error():
    """Test retry on network error."""
    mock_query = Mock(side_effect=[
        NetworkError("Connection failed"),
        NetworkError("Connection failed"),
        "Success response"
    ])

    result = query_ai_with_retry(
        query_func=mock_query,
        prompt="test prompt",
        config={"api": {"provider": "openai"}},
        max_retries=3
    )

    assert result == "Success response"
    assert mock_query.call_count == 3


def test_query_ai_with_retry_max_retries_exceeded():
    """Test that max retries is respected."""
    mock_query = Mock(side_effect=NetworkError("Connection failed"))

    with pytest.raises(NetworkError):
        query_ai_with_retry(
            query_func=mock_query,
            prompt="test prompt",
            config={"api": {"provider": "openai"}},
            max_retries=3
        )

    # Should try: initial + 3 retries = 4 total
    assert mock_query.call_count == 4


def test_query_ai_with_retry_no_retry_on_invalid_key():
    """Test that InvalidAPIKeyError doesn't trigger retries."""
    mock_query = Mock(side_effect=InvalidAPIKeyError("Invalid key", provider="openai"))

    with pytest.raises(InvalidAPIKeyError):
        query_ai_with_retry(
            query_func=mock_query,
            prompt="test prompt",
            config={"api": {"provider": "openai"}},
            max_retries=3
        )

    # Should not retry on API key errors
    assert mock_query.call_count == 1


def test_query_ai_with_retry_rate_limit():
    """Test handling of rate limit errors."""
    mock_query = Mock(side_effect=[
        RateLimitError("Rate limited", retry_after=1),
        "Success response"
    ])

    start_time = time.time()
    result = query_ai_with_retry(
        query_func=mock_query,
        prompt="test prompt",
        config={"api": {"provider": "openai"}},
        max_retries=3
    )
    elapsed = time.time() - start_time

    assert result == "Success response"
    assert mock_query.call_count == 2
    # Should have waited at least 1 second
    assert elapsed >= 1.0


def test_query_ai_with_retry_exponential_backoff():
    """Test exponential backoff timing."""
    mock_query = Mock(side_effect=[
        NetworkError("Failed"),
        NetworkError("Failed"),
        NetworkError("Failed"),
        "Success"
    ])

    start_time = time.time()
    result = query_ai_with_retry(
        query_func=mock_query,
        prompt="test prompt",
        config={"api": {"provider": "openai"}},
        max_retries=3,
        base_delay=0.1  # Use short delay for testing
    )
    elapsed = time.time() - start_time

    assert result == "Success"
    # Should have delays: 0.1 + 0.2 + 0.4 = 0.7s minimum
    assert elapsed >= 0.7
