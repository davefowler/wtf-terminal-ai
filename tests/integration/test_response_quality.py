"""Integration tests for response quality - tests that require real AI."""

import pytest
import os
from wtf.ai.client import query_ai_with_tools
from wtf.core.config import load_config


# Skip if no API key
pytestmark = pytest.mark.skipif(
    not os.environ.get('ANTHROPIC_API_KEY') and not os.environ.get('OPENAI_API_KEY'),
    reason="No API key available"
)


@pytest.mark.integration
def test_analyze_command_output_not_just_repeat():
    """
    Test that AI actually analyzes command output, not just repeats it.

    This is the bug: AI runs a command, sees the output, but then just
    says generic stuff instead of actually analyzing what it saw.
    """
    config = load_config()

    # Create a test file with specific content
    test_content = "def hello():\n    print('world')\n    return 42"
    with open('/tmp/test_analyze_me.py', 'w') as f:
        f.write(test_content)

    result = query_ai_with_tools(
        prompt="Read the file /tmp/test_analyze_me.py and tell me what the function returns",
        config=config,
        max_iterations=10
    )

    response = result["response"].lower()
    tool_calls = result["tool_calls"]

    # Should have used read_file tool
    assert any(tc["name"] == "read_file" for tc in tool_calls), \
        "Should have used read_file tool"

    # Response should mention the actual return value (42)
    assert "42" in response, \
        f"AI should mention that function returns 42, but response was: {response}"

    # Clean up
    os.remove('/tmp/test_analyze_me.py')


@pytest.mark.integration
def test_analyze_diff_with_actual_understanding():
    """
    Test that AI analyzes git diff content, not just says 'you have changes'.

    The bug: AI runs 'git diff', sees output, but gives generic response
    instead of analyzing what actually changed.
    """
    config = load_config()

    result = query_ai_with_tools(
        prompt="What specific code changes are in my git diff? Tell me exactly what was modified.",
        config=config,
        max_iterations=10
    )

    response = result["response"].lower()
    tool_calls = result["tool_calls"]

    # Should have run git diff
    assert any(
        tc["name"] == "run_command" and "diff" in tc["arguments"].get("command", "")
        for tc in tool_calls
    ), "Should have run git diff command"

    # Response should mention specific things from the actual diff:
    # - cli.py file
    # - debug output or response_text changes
    # The AI should be talking about ACTUAL changes, not generic "you made changes"
    assert "cli.py" in response or "cli" in response, \
        f"Should mention the actual file that changed (cli.py), but response was: {response}"

    # Should mention something specific about the change
    specific_terms = ["debug", "response", "print", "tool_call", "empty"]
    assert any(term in response for term in specific_terms), \
        f"Should mention specific changes (debug/response/etc), but response was: {response}"


@pytest.mark.integration
def test_multi_step_reasoning_with_tool_results():
    """
    Test that AI uses tool results for multi-step reasoning.

    The bug: AI might execute tools but not properly chain the results
    to answer the original question.
    """
    config = load_config()

    # Create test files
    os.makedirs('/tmp/test_dir', exist_ok=True)
    with open('/tmp/test_dir/file1.txt', 'w') as f:
        f.write('apple banana cherry')
    with open('/tmp/test_dir/file2.txt', 'w') as f:
        f.write('date elderberry fig')

    result = query_ai_with_tools(
        prompt="Find all .txt files in /tmp/test_dir, then tell me if any of them contain the word 'banana'",
        config=config,
        max_iterations=10
    )

    response = result["response"].lower()

    # Should mention finding banana
    assert "banana" in response, \
        f"Should mention finding 'banana', but response was: {response}"

    # Should mention which file
    assert "file1" in response, \
        f"Should mention file1.txt contains banana, but response was: {response}"

    # Clean up
    os.remove('/tmp/test_dir/file1.txt')
    os.remove('/tmp/test_dir/file2.txt')
    os.rmdir('/tmp/test_dir')


@pytest.mark.integration
def test_response_based_on_internal_tool_results():
    """
    Test that AI incorporates results from internal tools (not just run_command).

    Internal tools like read_file, grep, glob_files return data to the AI
    but don't print to user. The AI MUST use this data in its response.
    """
    config = load_config()

    # Create a test file
    test_content = "SECRET_KEY=abc123\nDEBUG=true\nPORT=8080"
    with open('/tmp/test_config.txt', 'w') as f:
        f.write(test_content)

    result = query_ai_with_tools(
        prompt="Read /tmp/test_config.txt and tell me what port is configured",
        config=config,
        max_iterations=10
    )

    response = result["response"]
    tool_calls = result["tool_calls"]

    # Should have read the file
    assert any(tc["name"] == "read_file" for tc in tool_calls), \
        "Should have used read_file"

    # Response MUST mention the actual port number from the file
    assert "8080" in response, \
        f"AI must mention port 8080 from file contents, but response was: {response}"

    # Clean up
    os.remove('/tmp/test_config.txt')


@pytest.mark.integration
def test_empty_or_missing_response_after_tools():
    """
    Test that AI ALWAYS provides a response after using tools.

    This is the core bug: tools execute successfully, but then
    response.text() is empty or generic.
    """
    config = load_config()

    result = query_ai_with_tools(
        prompt="Run 'echo testing123' and tell me what the output was",
        config=config,
        max_iterations=10
    )

    response = result["response"]
    tool_calls = result["tool_calls"]

    # Should have run the command
    assert any(tc["name"] == "run_command" for tc in tool_calls), \
        "Should have run echo command"

    # Response must not be empty
    assert response and len(response) > 0, \
        "Response should not be empty after tool execution"

    # Response should reference the actual output
    assert "testing123" in response.lower(), \
        f"Response should mention the command output 'testing123', but was: {response}"
