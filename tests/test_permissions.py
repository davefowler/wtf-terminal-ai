"""Tests for permission system."""

import pytest
from wtf.core.permissions import (
    is_command_allowed,
    is_command_denied,
    is_safe_readonly_command,
    should_auto_execute,
    is_command_chained,
    has_output_redirection,
)


def test_is_command_allowed():
    """Test allowlist pattern matching."""
    allowlist = ['git status', 'git commit', 'ls']

    assert is_command_allowed('git status', allowlist)
    assert is_command_allowed('git status -v', allowlist)
    assert is_command_allowed('git commit -m "test"', allowlist)
    assert is_command_allowed('ls -la', allowlist)

    assert not is_command_allowed('git push', allowlist)
    assert not is_command_allowed('rm file', allowlist)


def test_is_command_denied():
    """Test denylist pattern matching."""
    denylist = ['rm -rf /', 'sudo rm', 'dd if=']

    assert is_command_denied('rm -rf /', denylist)
    assert is_command_denied('sudo rm -rf /tmp', denylist)
    assert is_command_denied('dd if=/dev/zero', denylist)

    assert not is_command_denied('git status', denylist)
    assert not is_command_denied('ls -la', denylist)


def test_is_command_chained():
    """Test command chaining detection."""
    assert is_command_chained('git status && git add .')
    assert is_command_chained('ls || echo fail')
    assert is_command_chained('cat file | grep text')
    assert is_command_chained('echo $(whoami)')
    assert is_command_chained('echo `date`')
    assert is_command_chained('ls; rm file')

    assert not is_command_chained('git status')
    assert not is_command_chained('ls -la')


def test_has_output_redirection():
    """Test output redirection detection."""
    assert has_output_redirection('echo hello > file.txt')
    assert has_output_redirection('cat file >> output.log')

    assert not has_output_redirection('git status')
    assert not has_output_redirection('echo hello')


def test_is_safe_readonly_command():
    """Test safe readonly command detection."""
    # Safe commands
    assert is_safe_readonly_command('git status')
    assert is_safe_readonly_command('git log')
    assert is_safe_readonly_command('ls -la')
    assert is_safe_readonly_command('cat package.json')
    assert is_safe_readonly_command('command -v node')
    assert is_safe_readonly_command('pwd')

    # Not safe (dangerous or write operations)
    assert not is_safe_readonly_command('git commit')
    assert not is_safe_readonly_command('rm file')
    assert not is_safe_readonly_command('npm install')

    # Not safe due to chaining
    assert not is_safe_readonly_command('git status && rm file')

    # Not safe due to redirection
    assert not is_safe_readonly_command('cat file > output')


def test_should_auto_execute():
    """Test auto-execution decision logic."""
    allowlist = ['git commit']
    denylist = ['rm -rf /']
    config = {'behavior': {'auto_allow_readonly': True}}

    # Denied commands
    assert should_auto_execute('rm -rf /', allowlist, denylist, config) == 'deny'

    # Safe readonly commands (auto)
    assert should_auto_execute('git status', allowlist, denylist, config) == 'auto'
    assert should_auto_execute('ls -la', allowlist, denylist, config) == 'auto'

    # Allowlist commands (auto)
    assert should_auto_execute('git commit -m "test"', allowlist, denylist, config) == 'auto'

    # Unknown commands (ask)
    assert should_auto_execute('npm install', allowlist, denylist, config) == 'ask'

    # Chained commands (ask even if parts are safe)
    assert should_auto_execute('git status && git add .', allowlist, denylist, config) == 'ask'


def test_should_auto_execute_with_readonly_disabled():
    """Test that disabling auto_allow_readonly works."""
    config = {'behavior': {'auto_allow_readonly': False}}

    # Even safe commands should ask when disabled
    assert should_auto_execute('git status', [], [], config) == 'ask'
