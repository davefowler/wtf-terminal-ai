"""Integration tests for web instant answers functionality."""

import pytest
from wtf.ai.tools import web_instant_answers


class TestWebInstantAnswersTool:
    """Test the web_instant_answers tool directly."""

    def test_encyclopedic_query(self):
        """Test DuckDuckGo API for encyclopedic queries."""
        result = web_instant_answers("python programming language")

        print(f"\n=== Encyclopedic Query Test ===")
        print(f"Result: {result}")

        assert result is not None
        assert "results" in result
        # Should get some kind of result (even if it's "No results found")
        assert len(result["results"]) > 0

    def test_no_results_query(self):
        """Test what happens when no instant answer available."""
        result = web_instant_answers("xyzabc123notreal")

        print(f"\n=== No Results Test ===")
        print(f"Result: {result}")

        assert result is not None
        assert "results" in result

    def test_error_handling(self):
        """Test that errors are handled gracefully."""
        # Empty query
        result = web_instant_answers("")

        print(f"\n=== Error Handling Test ===")
        print(f"Result: {result}")

        assert result is not None
        assert "results" in result or "error" in result
