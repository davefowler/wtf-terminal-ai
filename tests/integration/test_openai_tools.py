"""Integration tests for OpenAI tool usage.

These tests verify that OpenAI models correctly use the available tools
(especially search tools) instead of trying to use curl or other workarounds.

Run with: pytest tests/integration/test_openai_tools.py -v
Requires: OPENAI_API_KEY environment variable
"""

import os
import pytest
from unittest.mock import patch

# Skip all tests if no OpenAI key
pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)


class TestOpenAISearchTools:
    """Test that OpenAI uses search tools correctly."""

    @pytest.fixture
    def config(self):
        """Return a config dict for OpenAI."""
        return {
            "api": {"model": "gpt-4o-mini"},
            "behavior": {
                "auto_execute_allowlist": True,
                "auto_allow_readonly": True,
            }
        }

    def test_weather_query_uses_search_tool(self, config):
        """Weather queries should use duckduckgo_search, not curl."""
        from wtf.ai.client import query_ai_with_tools
        from wtf.ai.prompts import build_system_prompt

        result = query_ai_with_tools(
            prompt="What is the weather in San Francisco right now?",
            config=config,
            system_prompt=build_system_prompt(),
            max_iterations=5
        )

        tool_names = [tc["name"] for tc in result["tool_calls"]]
        
        # Should use a search tool
        search_tools = ["duckduckgo_search", "tavily_search", "serper_search", "brave_search"]
        used_search = any(t in search_tools for t in tool_names)
        
        # Should NOT use run_command with curl
        used_curl = any(
            tc["name"] == "run_command" and "curl" in tc.get("arguments", {}).get("command", "")
            for tc in result["tool_calls"]
        )
        
        assert used_search, f"Expected search tool, got: {tool_names}"
        assert not used_curl, f"Should not use curl for weather, got: {tool_names}"
        assert result["response"], "Should have a response"

    def test_history_query_uses_search_tool(self, config):
        """History queries should use duckduckgo_search, not curl."""
        from wtf.ai.client import query_ai_with_tools
        from wtf.ai.prompts import build_system_prompt

        result = query_ai_with_tools(
            prompt="What happened on January 9th in history?",
            config=config,
            system_prompt=build_system_prompt(),
            max_iterations=5
        )

        tool_names = [tc["name"] for tc in result["tool_calls"]]
        
        # Should use a search tool
        search_tools = ["duckduckgo_search", "tavily_search", "serper_search", "brave_search"]
        used_search = any(t in search_tools for t in tool_names)
        
        # Should NOT use run_command with curl
        used_curl = any(
            tc["name"] == "run_command" and "curl" in tc.get("arguments", {}).get("command", "")
            for tc in result["tool_calls"]
        )
        
        assert used_search, f"Expected search tool, got: {tool_names}"
        assert not used_curl, f"Should not use curl for history, got: {tool_names}"

    def test_news_query_uses_search_tool(self, config):
        """News queries should use duckduckgo_search."""
        from wtf.ai.client import query_ai_with_tools
        from wtf.ai.prompts import build_system_prompt

        result = query_ai_with_tools(
            prompt="What's the latest news about AI?",
            config=config,
            system_prompt=build_system_prompt(),
            max_iterations=5
        )

        tool_names = [tc["name"] for tc in result["tool_calls"]]
        
        # Should use a search tool
        search_tools = ["duckduckgo_search", "tavily_search", "serper_search", "brave_search"]
        used_search = any(t in search_tools for t in tool_names)
        
        assert used_search, f"Expected search tool for news, got: {tool_names}"

    def test_duckduckgo_search_returns_results(self, config):
        """DuckDuckGo search should return actual results."""
        from wtf.ai.tools import duckduckgo_search

        result = duckduckgo_search("weather san francisco")
        
        assert result.get("results"), f"Expected results, got: {result}"
        assert "error" not in result or result.get("error") is None
        # Results should contain actual weather info
        assert "francisco" in result["results"].lower() or "weather" in result["results"].lower()

    def test_search_result_contains_temperature(self, config):
        """Weather search should return temperature data."""
        from wtf.ai.client import query_ai_with_tools
        from wtf.ai.prompts import build_system_prompt

        result = query_ai_with_tools(
            prompt="What is the temperature in New York City right now?",
            config=config,
            system_prompt=build_system_prompt(),
            max_iterations=5
        )

        response = result["response"].lower()
        
        # Response should mention temperature in some form
        has_temp = any(indicator in response for indicator in [
            "°f", "°c", "degrees", "fahrenheit", "celsius", 
            "temperature", "cold", "warm", "hot", "cool"
        ])
        
        assert has_temp, f"Expected temperature info in response: {result['response'][:200]}"


class TestOpenAIToolSelection:
    """Test that OpenAI selects appropriate tools for different queries."""

    @pytest.fixture
    def config(self):
        return {
            "api": {"model": "gpt-4o-mini"},
            "behavior": {
                "auto_execute_allowlist": True,
                "auto_allow_readonly": True,
            }
        }

    def test_file_query_uses_read_file(self, config, tmp_path):
        """File reading queries should use read_file tool."""
        from wtf.ai.client import query_ai_with_tools
        from wtf.ai.prompts import build_system_prompt

        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello from test file!")

        # Change to tmp_path so the AI can find the file
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            result = query_ai_with_tools(
                prompt=f"Read the file test.txt and tell me what it says",
                config=config,
                system_prompt=build_system_prompt(),
                max_iterations=5
            )

            tool_names = [tc["name"] for tc in result["tool_calls"]]
            
            # Should use read_file
            assert "read_file" in tool_names, f"Expected read_file, got: {tool_names}"
            
            # Response should contain file content
            assert "hello" in result["response"].lower() or "test file" in result["response"].lower()
        finally:
            os.chdir(original_cwd)

    def test_git_query_uses_run_command(self, config):
        """Git queries should use run_command with git."""
        from wtf.ai.client import query_ai_with_tools
        from wtf.ai.prompts import build_system_prompt

        result = query_ai_with_tools(
            prompt="What's my git status?",
            config=config,
            system_prompt=build_system_prompt(),
            max_iterations=5
        )

        tool_names = [tc["name"] for tc in result["tool_calls"]]
        
        # Should use run_command or get_git_info
        used_git_tool = "get_git_info" in tool_names or any(
            tc["name"] == "run_command" and "git" in tc.get("arguments", {}).get("command", "")
            for tc in result["tool_calls"]
        )
        
        assert used_git_tool, f"Expected git-related tool, got: {tool_names}"


class TestSearchToolDirect:
    """Direct tests for search tool functionality."""

    def test_duckduckgo_search_basic(self):
        """Basic DuckDuckGo search works."""
        from wtf.ai.tools import duckduckgo_search

        result = duckduckgo_search("python programming language")
        
        assert "results" in result
        assert result["results"] is not None
        assert len(result["results"]) > 0

    def test_duckduckgo_search_weather(self):
        """DuckDuckGo can search for weather."""
        from wtf.ai.tools import duckduckgo_search

        result = duckduckgo_search("weather los angeles today")
        
        assert "results" in result
        assert result["results"] is not None
        # Should contain weather-related content
        results_lower = result["results"].lower()
        assert any(word in results_lower for word in ["weather", "temperature", "forecast", "angeles"])

    def test_duckduckgo_search_current_events(self):
        """DuckDuckGo can search for current events."""
        from wtf.ai.tools import duckduckgo_search

        result = duckduckgo_search("latest technology news 2025")
        
        assert "results" in result
        assert result["results"] is not None
        assert len(result["results"]) > 50  # Should have substantial results
