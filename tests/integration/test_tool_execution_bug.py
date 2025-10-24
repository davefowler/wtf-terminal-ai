"""Test for the specific bug where AI suggests commands instead of executing them."""

import pytest
import os
from wtf.ai.client import query_ai_with_tools
from wtf.core.config import load_config


pytestmark = pytest.mark.skipif(
    not os.environ.get('ANTHROPIC_API_KEY') and not os.environ.get('OPENAI_API_KEY'),
    reason="No API key available"
)


@pytest.mark.integration
def test_ai_must_execute_not_suggest():
    """
    Bug: AI sometimes suggests commands in markdown code blocks
    instead of actually executing them with tools.

    Example:
    User: "what is this program about"
    AI: "Let's check the README:
         ```bash
         cat README.md
         ```"

    But it should actually use read_file tool and tell the user what it found!
    """
    config = load_config()

    # Create a test README with specific identifiable content
    test_readme = """# Test Project
This is a test project that does WIDGET MANIPULATION.
It can manipulate widgets in 42 different ways.
"""
    with open('/tmp/test_readme.md', 'w') as f:
        f.write(test_readme)

    result = query_ai_with_tools(
        prompt="What is the project in /tmp/test_readme.md about? Actually read it and tell me.",
        config=config,
        max_iterations=10
    )

    response = result["response"]
    tool_calls = result["tool_calls"]

    print(f"\n=== DEBUG ===")
    print(f"Tool calls made: {len(tool_calls)}")
    print(f"Tools used: {[tc['name'] for tc in tool_calls]}")
    print(f"Response length: {len(response)}")
    print(f"Response:\n{response}")
    print(f"=== END DEBUG ===\n")

    # MUST have actually used read_file tool
    assert any(tc["name"] == "read_file" for tc in tool_calls), \
        f"AI must USE read_file tool, not suggest it! Tool calls: {[tc['name'] for tc in tool_calls]}"

    # Response must mention the actual content
    assert "widget" in response.lower(), \
        f"AI must mention WIDGET from the actual file content, not just say 'check the README'. Response was: {response}"

    assert "42" in response, \
        f"AI must mention 42 from the actual file content. Response was: {response}"

    # Should NOT contain markdown code blocks suggesting commands
    assert "```bash" not in response and "```" not in response.lower().replace("```python", ""), \
        f"AI should not suggest commands in code blocks, should execute them! Response: {response}"

    # Clean up
    os.remove('/tmp/test_readme.md')


@pytest.mark.integration
def test_readme_question_actually_reads_file():
    """
    Specific test for: "what is this program about?" on the actual README.

    This is the exact scenario the user reported failing.
    """
    config = load_config()

    result = query_ai_with_tools(
        prompt="What is this program about? Read the README.md file.",
        config=config,
        max_iterations=10
    )

    response = result["response"]
    tool_calls = result["tool_calls"]

    print(f"\n=== ACTUAL README TEST ===")
    print(f"Tool calls: {[tc['name'] for tc in tool_calls]}")
    print(f"Response:\n{response}")
    print(f"=== END ===\n")

    # Must use read_file
    read_calls = [tc for tc in tool_calls if tc["name"] == "read_file"]
    assert len(read_calls) > 0, \
        f"Must actually READ the README! Tools used: {[tc['name'] for tc in tool_calls]}"

    # Check that it read README.md specifically
    assert any("README" in tc.get("arguments", {}).get("file_path", "") for tc in read_calls), \
        f"Must read README.md specifically! Read calls: {read_calls}"

    # Response should mention specific things from README
    # Our README mentions "wtf", "terminal", "AI", "command-line"
    readme_terms = ["wtf", "terminal", "command"]
    matches = sum(1 for term in readme_terms if term in response.lower())
    assert matches >= 2, \
        f"Response should mention actual README content (wtf, terminal, command, etc). Response: {response}"

    # Should NOT just suggest running cat
    assert "cat README" not in response, \
        f"Should not suggest 'cat README', should actually read it! Response: {response}"


@pytest.mark.integration
def test_git_diff_analysis_reads_actual_changes():
    """
    Test the other reported failure: AI should analyze git diff, not just
    print it and give generic commentary.
    """
    config = load_config()

    result = query_ai_with_tools(
        prompt="What specific changes are in my git diff? Tell me exactly what code changed.",
        config=config,
        max_iterations=10
    )

    response = result["response"]
    tool_calls = result["tool_calls"]

    print(f"\n=== GIT DIFF TEST ===")
    print(f"Tools: {[tc['name'] for tc in tool_calls]}")
    print(f"Response:\n{response}")
    print(f"=== END ===\n")

    # Must run git diff
    assert any(
        tc["name"] == "run_command" and "diff" in tc.get("arguments", {}).get("command", "")
        for tc in tool_calls
    ), "Must run git diff command"

    # If there are changes, response should mention specific files/changes
    # If no changes, should say "no changes"
    if "no changes" not in response.lower() and "nothing to commit" not in response.lower():
        # There are changes, so response should be specific
        assert len(response) > 100, \
            f"Response should provide detailed analysis of changes, not be empty or short. Response: {response}"
