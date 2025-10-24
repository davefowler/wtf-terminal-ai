"""
Integration tests that use the REAL llm library (not mocked).

These tests would have caught the tool_calls() bug because they use actual
Response objects from the llm library, not mocked dictionaries.
"""

import pytest
import os
from unittest.mock import patch
from wtf.core.config import load_config
from wtf.ai.client import query_ai_with_tools
from wtf.ai.prompts import build_system_prompt


# Skip if no API key available
pytestmark = pytest.mark.skipif(
    not os.environ.get('ANTHROPIC_API_KEY') and
    not os.environ.get('OPENAI_API_KEY'),
    reason="No API key available for real tool calling tests"
)


@pytest.mark.integration
class TestRealToolCalling:
    """Tests that use real llm library Response objects."""

    def test_query_without_tools(self):
        """Test simple query that doesn't need tools."""
        config = load_config()

        result = query_ai_with_tools(
            prompt="Just say 'Hello' and nothing else",
            config=config,
            system_prompt="You are a helpful assistant. Be concise.",
            max_iterations=1
        )

        assert result is not None
        assert 'response' in result
        assert 'tool_calls' in result
        assert 'iterations' in result
        assert isinstance(result['tool_calls'], list)
        assert result['iterations'] == 1

    def test_query_with_file_read_tool(self):
        """Test query that should use read_file tool."""
        config = load_config()

        # Create a test file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test content for integration test")
            test_file = f.name

        try:
            result = query_ai_with_tools(
                prompt=f"What are the contents of the file {test_file}?",
                config=config,
                system_prompt=build_system_prompt(),
                max_iterations=5
            )

            assert result is not None
            assert 'tool_calls' in result

            # Should have called read_file tool
            tool_names = [tc['name'] for tc in result['tool_calls']]
            assert 'read_file' in tool_names, f"Expected read_file in {tool_names}"

            # Check that response mentions the file content
            assert 'Test content' in result['response'] or 'integration test' in result['response']

        finally:
            # Clean up
            os.unlink(test_file)

    def test_query_with_run_command_tool(self):
        """Test query that should use run_command tool."""
        config = load_config()

        result = query_ai_with_tools(
            prompt="Run the command 'echo hello world' and tell me what it outputs",
            config=config,
            system_prompt=build_system_prompt(),
            max_iterations=5
        )

        assert result is not None
        assert 'tool_calls' in result

        # Should have called run_command tool
        tool_names = [tc['name'] for tc in result['tool_calls']]
        assert 'run_command' in tool_names, f"Expected run_command in {tool_names}"

        # Check that tool was called with right command
        run_command_calls = [tc for tc in result['tool_calls'] if tc['name'] == 'run_command']
        assert len(run_command_calls) > 0

        # Verify output contains "hello world"
        for tc in run_command_calls:
            if 'echo' in tc['arguments'].get('command', ''):
                assert 'hello world' in tc['result'].get('output', '').lower()

    def test_multiple_tool_iterations(self):
        """Test that agent can use multiple tools in sequence."""
        config = load_config()

        # Create test file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("apple\nbanana\ncherry")
            test_file = f.name

        try:
            result = query_ai_with_tools(
                prompt=f"Read {test_file} and then count how many lines it has using wc -l",
                config=config,
                system_prompt=build_system_prompt(),
                max_iterations=10
            )

            assert result is not None
            assert len(result['tool_calls']) >= 2, "Should use multiple tools"

            tool_names = [tc['name'] for tc in result['tool_calls']]
            # Should read file first, then run wc command
            assert 'read_file' in tool_names or 'run_command' in tool_names

        finally:
            os.unlink(test_file)

    def test_tool_should_print_flag(self):
        """Test that tools properly set should_print flag."""
        config = load_config()

        result = query_ai_with_tools(
            prompt="Run 'echo test' for me",
            config=config,
            system_prompt=build_system_prompt(),
            max_iterations=3
        )

        # Find run_command calls
        run_commands = [tc for tc in result['tool_calls'] if tc['name'] == 'run_command']
        if run_commands:
            # run_command should have should_print=True
            for tc in run_commands:
                assert tc['result'].get('should_print') is True, \
                    "run_command must have should_print=True"

        # Find read_file calls if any
        read_files = [tc for tc in result['tool_calls'] if tc['name'] == 'read_file']
        if read_files:
            # read_file should have should_print=False
            for tc in read_files:
                assert tc['result'].get('should_print') is False, \
                    "read_file must have should_print=False"


@pytest.mark.integration
class TestResponseObjectHandling:
    """Tests that specifically verify Response object method calls work."""

    def test_response_text_is_callable(self):
        """Verify that response.text() works (it's a method)."""
        config = load_config()

        result = query_ai_with_tools(
            prompt="Say OK",
            config=config,
            system_prompt="Be brief.",
            max_iterations=1
        )

        # The fact that we got a response means text() worked
        assert isinstance(result['response'], str)
        assert len(result['response']) > 0

    def test_response_tool_calls_is_callable(self):
        """Verify that response.tool_calls() works (it's a method, not property)."""
        config = load_config()

        # This should trigger tool usage
        result = query_ai_with_tools(
            prompt="Run 'echo test' and show me the output",
            config=config,
            system_prompt=build_system_prompt(),
            max_iterations=3
        )

        # The fact that we got here without "'method' object is not iterable"
        # means tool_calls() was called correctly
        assert 'tool_calls' in result
        assert isinstance(result['tool_calls'], list)
