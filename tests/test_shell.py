"""Tests for shell context gathering."""

import pytest
from wtf.context.shell import (
    detect_shell,
    parse_zsh_history_line,
    parse_bash_history_line,
    HistoryFailureReason,
)


def test_detect_shell():
    """Test shell detection."""
    shell = detect_shell()
    # Should detect one of the known shells or unknown
    assert shell in ['zsh', 'bash', 'fish', 'unknown']


def test_parse_zsh_history_line():
    """Test parsing zsh history format."""
    # Extended format
    line = ': 1234567890:0;git status'
    assert parse_zsh_history_line(line) == 'git status'

    # Plain format
    line = 'git commit -m "test"'
    assert parse_zsh_history_line(line) == 'git commit -m "test"'

    # Empty lines
    assert parse_zsh_history_line('') is None
    assert parse_zsh_history_line('   ') is None


def test_parse_bash_history_line():
    """Test parsing bash history format."""
    line = 'git status'
    assert parse_bash_history_line(line) == 'git status'

    # Empty lines
    assert parse_bash_history_line('') is None
    assert parse_bash_history_line('   ') is None


def test_history_failure_reason_enum():
    """Test HistoryFailureReason enum."""
    assert HistoryFailureReason.FILE_NOT_FOUND
    assert HistoryFailureReason.PERMISSION_DENIED
    assert HistoryFailureReason.HISTORY_DISABLED
    assert HistoryFailureReason.EMPTY_HISTORY
