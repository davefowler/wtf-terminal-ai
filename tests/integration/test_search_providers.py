"""Integration tests for web search providers (Serper, Bing, Brave)."""

import pytest
import os
from unittest.mock import patch, MagicMock
from wtf.ai.tools import serper_search, bing_search, brave_search


class TestSerperSearch:
    """Test Serper search provider."""

    def test_no_api_key_configured(self):
        """Test Serper with no API key returns helpful error."""
        # Mock config to return no API key
        with patch('wtf.ai.tools.load_config') as mock_config:
            mock_config.return_value = {}

            # Also ensure no environment variable
            with patch.dict(os.environ, {}, clear=True):
                result = serper_search("test query")

        assert result is not None
        assert "error" in result
        assert "Serper API key not configured" in result["error"]
        assert "serper.dev" in result["error"]
        assert result["should_print"] is False

    @pytest.mark.skipif(
        not os.environ.get("SERPER_API_KEY"),
        reason="SERPER_API_KEY not set - this is optional"
    )
    def test_serper_with_real_api_key(self):
        """Test Serper with real API key (only runs if key is set)."""
        result = serper_search("weather in San Francisco")

        print(f"\n=== Serper Real API Test ===")
        print(f"Result: {result}")

        assert result is not None
        assert "results" in result or "error" in result

        # If successful, should have results
        if "results" in result and result["results"]:
            assert len(result["results"]) > 0
            assert result["should_print"] is True

    def test_serper_with_mock_api(self):
        """Test Serper with mocked API response."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'''{
            "organic": [
                {
                    "title": "Test Result",
                    "link": "https://example.com",
                    "snippet": "This is a test result"
                }
            ]
        }'''
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch('wtf.ai.tools.load_config') as mock_config:
            mock_config.return_value = {"api_keys": {"serper": "test_key"}}

            with patch('urllib.request.urlopen', return_value=mock_response):
                result = serper_search("test query")

        assert result is not None
        assert "results" in result
        assert result["results"] is not None
        assert "Test Result" in result["results"]
        assert "https://example.com" in result["results"]
        assert result["should_print"] is False


class TestBingSearch:
    """Test Bing search provider."""

    def test_no_api_key_configured(self):
        """Test Bing with no API key returns helpful error."""
        with patch('wtf.ai.tools.load_config') as mock_config:
            mock_config.return_value = {}

            with patch.dict(os.environ, {}, clear=True):
                result = bing_search("test query")

        assert result is not None
        assert "error" in result
        assert "Bing Search API key not configured" in result["error"]
        assert "Azure Portal" in result["error"] or "bing search api key" in result["error"]
        assert result["should_print"] is False

    @pytest.mark.skipif(
        not os.environ.get("BING_SEARCH_API_KEY"),
        reason="BING_SEARCH_API_KEY not set - this is optional"
    )
    def test_bing_with_real_api_key(self):
        """Test Bing with real API key (only runs if key is set)."""
        result = bing_search("weather in San Francisco")

        print(f"\n=== Bing Real API Test ===")
        print(f"Result: {result}")

        assert result is not None
        assert "results" in result or "error" in result

        if "results" in result and result["results"]:
            assert len(result["results"]) > 0
            assert result["should_print"] is True

    def test_bing_with_mock_api(self):
        """Test Bing with mocked API response."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'''{
            "webPages": {
                "value": [
                    {
                        "name": "Test Bing Result",
                        "url": "https://example.com",
                        "snippet": "This is a test Bing result"
                    }
                ]
            }
        }'''
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch('wtf.ai.tools.load_config') as mock_config:
            mock_config.return_value = {"api_keys": {"bing_search": "test_key"}}

            with patch('urllib.request.urlopen', return_value=mock_response):
                result = bing_search("test query")

        assert result is not None
        assert "results" in result
        assert result["results"] is not None
        assert "Test Bing Result" in result["results"]
        assert "https://example.com" in result["results"]
        assert result["should_print"] is False


class TestBraveSearch:
    """Test Brave search provider."""

    def test_no_api_key_configured(self):
        """Test Brave with no API key returns helpful error."""
        with patch('wtf.ai.tools.load_config') as mock_config:
            mock_config.return_value = {}

            with patch.dict(os.environ, {}, clear=True):
                result = brave_search("test query")

        assert result is not None
        assert "error" in result
        assert "Brave Search API key not configured" in result["error"]

    @pytest.mark.skipif(
        not os.environ.get("BRAVE_SEARCH_API_KEY"),
        reason="BRAVE_SEARCH_API_KEY not set - this is optional"
    )
    def test_brave_with_real_api_key(self):
        """Test Brave with real API key (only runs if key is set)."""
        result = brave_search("weather in San Francisco")

        print(f"\n=== Brave Real API Test ===")
        print(f"Result: {result}")

        assert result is not None
        assert "results" in result or "error" in result

        if "results" in result and result["results"]:
            assert len(result["results"]) > 0


class TestSearchProviderPriority:
    """Test that search providers are used in correct priority order."""

    def test_serper_preferred_when_available(self):
        """Test that Serper is used when its API key is configured."""
        # This would require integration testing with the AI tool selection
        # For now, we verify the tool definitions indicate Serper is preferred
        from wtf.ai.tools import get_tool_definitions

        tools = get_tool_definitions()
        serper_tool = next((t for t in tools if t["name"] == "serper_search"), None)

        assert serper_tool is not None
        assert "PREFERRED" in serper_tool["description"]

    def test_all_providers_registered(self):
        """Test that all search providers are registered in TOOLS."""
        from wtf.ai.tools import TOOLS

        assert "serper_search" in TOOLS
        assert "bing_search" in TOOLS
        assert "brave_search" in TOOLS
        assert "web_instant_answers" in TOOLS

    def test_all_providers_have_tool_definitions(self):
        """Test that all search providers have tool definitions for AI."""
        from wtf.ai.tools import get_tool_definitions

        tools = get_tool_definitions()
        tool_names = [t["name"] for t in tools]

        assert "serper_search" in tool_names
        assert "bing_search" in tool_names
        assert "brave_search" in tool_names
        assert "web_instant_answers" in tool_names
