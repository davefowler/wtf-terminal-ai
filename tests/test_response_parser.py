"""Tests for AI response parsing."""

import pytest
from wtf.ai.response_parser import extract_commands, _suggest_allowlist_pattern


def test_extract_commands_from_code_blocks():
    """Test extracting commands from markdown code blocks."""
    response = """
Let me help you with that.

```bash
git status
git add .
```
"""

    commands = extract_commands(response)
    assert len(commands) == 2
    assert commands[0]['command'] == 'git status'
    assert commands[1]['command'] == 'git add .'


def test_extract_commands_from_shell_prompts():
    """Test extracting commands from $ prompts."""
    response = """
Try running this:

$ git status
$ ls -la
"""

    commands = extract_commands(response)
    assert len(commands) == 2
    assert commands[0]['command'] == 'git status'
    assert commands[1]['command'] == 'ls -la'


def test_extract_commands_deduplicates():
    """Test that duplicate commands are handled."""
    response = """
```bash
git status
```

Also try:

$ git status
"""

    commands = extract_commands(response)
    # Should have git status only once
    assert len(commands) == 1
    assert commands[0]['command'] == 'git status'


def test_extract_commands_skips_comments():
    """Test that comments are skipped."""
    response = """
```bash
# This is a comment
git status
# Another comment
git add .
```
"""

    commands = extract_commands(response)
    assert len(commands) == 2
    assert all('# ' not in cmd['command'] for cmd in commands)


def test_suggest_allowlist_pattern():
    """Test allowlist pattern suggestions."""
    # Multi-command tools should include subcommand
    assert _suggest_allowlist_pattern('git status') == 'git status'
    assert _suggest_allowlist_pattern('git commit -m "test"') == 'git commit'
    assert _suggest_allowlist_pattern('npm run build') == 'npm run'
    assert _suggest_allowlist_pattern('docker ps -a') == 'docker ps'

    # Simple commands should use base only
    assert _suggest_allowlist_pattern('ls -la') == 'ls'
    assert _suggest_allowlist_pattern('cat file.txt') == 'cat'
    assert _suggest_allowlist_pattern('pwd') == 'pwd'


def test_extract_commands_with_no_commands():
    """Test response with no commands."""
    response = """
This is just a regular text response with no commands.
Just explaining something to the user.
"""

    commands = extract_commands(response)
    assert len(commands) == 0
