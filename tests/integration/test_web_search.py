"""Integration tests for web search functionality."""

import pytest
from wtf.ai.tools import web_search


class TestWebSearchTool:
    """Test the web_search tool directly."""

    def test_web_search_doc_lookup_django(self):
        """Test that Django docs are found."""
        result = web_search("find me the docs for django")

        print(f"\n=== Django Docs Test ===")
        print(f"Result: {result}")

        assert result is not None
        assert "results" in result
        assert "django" in result["results"].lower()
        assert "https://docs.djangoproject.com" in result["results"]

    def test_web_search_doc_lookup_react(self):
        """Test that React docs are found."""
        result = web_search("react documentation")

        print(f"\n=== React Docs Test ===")
        print(f"Result: {result}")

        assert result is not None
        assert "results" in result
        assert "https://react.dev" in result["results"]

    def test_web_search_doc_lookup_python(self):
        """Test that Python docs are found."""
        result = web_search("python docs")

        print(f"\n=== Python Docs Test ===")
        print(f"Result: {result}")

        assert result is not None
        assert "results" in result
        assert "https://docs.python.org" in result["results"]

    def test_web_search_duckduckgo_fallback(self):
        """Test DuckDuckGo API for non-doc queries."""
        result = web_search("python programming language")

        print(f"\n=== DuckDuckGo Fallback Test ===")
        print(f"Result: {result}")

        assert result is not None
        assert "results" in result
        # Should get some kind of result (even if it's "No results found")
        assert len(result["results"]) > 0

    def test_web_search_no_match(self):
        """Test what happens when no doc match is found."""
        result = web_search("docs for xyzabc123notreal")

        print(f"\n=== No Match Test ===")
        print(f"Result: {result}")

        assert result is not None
        assert "results" in result
        # Should fall back to DuckDuckGo or return "No results found"

    def test_web_search_error_handling(self):
        """Test that errors are handled gracefully."""
        # Empty query
        result = web_search("")

        print(f"\n=== Error Handling Test ===")
        print(f"Result: {result}")

        assert result is not None
        assert "results" in result or "error" in result


@pytest.mark.integration
class TestWebSearchEndToEnd:
    """End-to-end tests with actual AI."""

    def test_ai_uses_web_search_for_docs(self):
        """Test that AI actually uses web_search tool for doc queries."""
        from wtf.ai.client import query_ai_with_tools
        from wtf.core.config import load_config

        config = load_config()

        result = query_ai_with_tools(
            prompt="Find me the Django documentation",
            config=config,
            max_iterations=5
        )

        print(f"\n=== AI Web Search Test ===")
        print(f"Tool calls: {[tc['name'] for tc in result['tool_calls']]}")
        print(f"Response: {result['response']}")

        # Should have used web_search tool
        assert any(tc['name'] == 'web_search' for tc in result['tool_calls'])

        # Response should mention Django docs
        response_lower = result['response'].lower()
        assert 'django' in response_lower
        assert 'docs.djangoproject.com' in response_lower or 'documentation' in response_lower
