"""Tests for permission system."""

import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile

from wtf.core.permissions import (
    is_command_allowed,
    is_command_denied,
    is_safe_readonly_command,
    should_auto_execute,
    is_command_chained,
    has_output_redirection,
    prompt_for_permission,
    add_to_allowlist,
    load_allowlist,
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


class TestPromptForPermission:
    """Tests for the prompt_for_permission function."""

    @patch('wtf.core.permissions.Prompt.ask')
    @patch('wtf.core.permissions.console')
    def test_yes_response_lowercase_y(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """Test that 'y' returns 'yes'."""
        mock_ask.return_value = 'y'
        result = prompt_for_permission('echo hello', 'test explanation')
        assert result == 'yes'

    @patch('wtf.core.permissions.Prompt.ask')
    @patch('wtf.core.permissions.console')
    def test_yes_response_uppercase_y(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """Test that 'Y' returns 'yes'."""
        mock_ask.return_value = 'Y'
        result = prompt_for_permission('echo hello', 'test explanation')
        assert result == 'yes'

    @patch('wtf.core.permissions.Prompt.ask')
    @patch('wtf.core.permissions.console')
    def test_yes_response_full_word(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """Test that 'yes' returns 'yes'."""
        mock_ask.return_value = 'yes'
        result = prompt_for_permission('echo hello', 'test explanation')
        assert result == 'yes'

    @patch('wtf.core.permissions.Prompt.ask')
    @patch('wtf.core.permissions.console')
    def test_always_response_lowercase_a(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """Test that 'a' returns 'yes_always' when allowlist_pattern provided."""
        mock_ask.return_value = 'a'
        result = prompt_for_permission('lsof -ti:8080', 'kill port', allowlist_pattern='lsof')
        assert result == 'yes_always'

    @patch('wtf.core.permissions.Prompt.ask')
    @patch('wtf.core.permissions.console')
    def test_always_response_uppercase_a(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """Test that 'A' returns 'yes_always' when allowlist_pattern provided."""
        mock_ask.return_value = 'A'
        result = prompt_for_permission('lsof -ti:8080', 'kill port', allowlist_pattern='lsof')
        assert result == 'yes_always'

    @patch('wtf.core.permissions.Prompt.ask')
    @patch('wtf.core.permissions.console')
    def test_always_response_full_word(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """Test that 'always' returns 'yes_always' when allowlist_pattern provided."""
        mock_ask.return_value = 'always'
        result = prompt_for_permission('npm install', 'install deps', allowlist_pattern='npm install')
        assert result == 'yes_always'

    @patch('wtf.core.permissions.Prompt.ask')
    @patch('wtf.core.permissions.console')
    def test_no_response_lowercase_n(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """Test that 'n' returns 'no'."""
        mock_ask.return_value = 'n'
        result = prompt_for_permission('rm -rf /', 'dangerous command')
        assert result == 'no'

    @patch('wtf.core.permissions.Prompt.ask')
    @patch('wtf.core.permissions.console')
    def test_no_response_uppercase_n(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """Test that 'N' returns 'no'."""
        mock_ask.return_value = 'N'
        result = prompt_for_permission('rm -rf /', 'dangerous command')
        assert result == 'no'

    @patch('wtf.core.permissions.Prompt.ask')
    @patch('wtf.core.permissions.console')
    def test_no_response_full_word(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """Test that 'no' returns 'no'."""
        mock_ask.return_value = 'no'
        result = prompt_for_permission('rm -rf /', 'dangerous command')
        assert result == 'no'

    @patch('wtf.core.permissions.Prompt.ask')
    @patch('wtf.core.permissions.console')
    def test_without_allowlist_pattern_no_always_option(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """Test that without allowlist_pattern, the 'always' option is not included."""
        mock_ask.return_value = 'y'
        result = prompt_for_permission('echo hello', 'test', allowlist_pattern=None)
        
        # Check that the choices passed to Prompt.ask don't include 'a' variants
        call_kwargs = mock_ask.call_args[1]
        choices = call_kwargs.get('choices', [])
        assert 'a' not in choices
        assert 'A' not in choices
        assert 'always' not in choices

    @patch('wtf.core.permissions.Prompt.ask')
    @patch('wtf.core.permissions.console')
    def test_with_allowlist_pattern_has_always_option(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """Test that with allowlist_pattern, the 'always' option is included."""
        mock_ask.return_value = 'y'
        result = prompt_for_permission('npm install', 'install', allowlist_pattern='npm install')
        
        # Check that the choices passed to Prompt.ask include 'a' variants
        call_kwargs = mock_ask.call_args[1]
        choices = call_kwargs.get('choices', [])
        assert 'a' in choices
        assert 'A' in choices
        assert 'always' in choices

    @patch('wtf.core.permissions.Prompt.ask')
    @patch('wtf.core.permissions.console')
    def test_default_is_y(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """Test that the default choice is 'y' (yes)."""
        mock_ask.return_value = 'y'
        prompt_for_permission('echo hello', 'test')
        
        call_kwargs = mock_ask.call_args[1]
        assert call_kwargs.get('default') == 'y'

    @patch('wtf.core.permissions.Prompt.ask')
    @patch('wtf.core.permissions.console')
    def test_case_insensitive_response(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """Test that responses are case-insensitive (converted to lowercase)."""
        # Test YES (uppercase)
        mock_ask.return_value = 'YES'
        result = prompt_for_permission('echo hello', 'test')
        assert result == 'yes'

        # Test ALWAYS (uppercase) with allowlist pattern
        mock_ask.return_value = 'ALWAYS'
        result = prompt_for_permission('npm install', 'test', allowlist_pattern='npm')
        assert result == 'yes_always'

        # Test NO (uppercase)
        mock_ask.return_value = 'NO'
        result = prompt_for_permission('rm file', 'test')
        assert result == 'no'


class TestAddToAllowlist:
    """Tests for the add_to_allowlist function."""

    def test_add_pattern_to_empty_allowlist(self) -> None:
        """Test adding a pattern when allowlist doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            allowlist_path = Path(tmpdir) / 'allowlist.json'
            
            with patch('wtf.core.permissions.get_allowlist_path', return_value=allowlist_path):
                with patch('wtf.core.permissions.console'):
                    add_to_allowlist('lsof')
                
                # Verify the file was created with the pattern
                assert allowlist_path.exists()
                with open(allowlist_path) as f:
                    data = json.load(f)
                assert 'lsof' in data.get('patterns', [])

    def test_add_pattern_to_existing_allowlist(self) -> None:
        """Test adding a pattern to existing allowlist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            allowlist_path = Path(tmpdir) / 'allowlist.json'
            
            # Create existing allowlist
            existing_data = {'patterns': ['git status'], 'denylist': []}
            with open(allowlist_path, 'w') as f:
                json.dump(existing_data, f)
            
            with patch('wtf.core.permissions.get_allowlist_path', return_value=allowlist_path):
                with patch('wtf.core.permissions.console'):
                    add_to_allowlist('npm install')
                
                # Verify both patterns exist
                with open(allowlist_path) as f:
                    data = json.load(f)
                assert 'git status' in data.get('patterns', [])
                assert 'npm install' in data.get('patterns', [])

    def test_no_duplicate_patterns(self) -> None:
        """Test that duplicate patterns are not added."""
        with tempfile.TemporaryDirectory() as tmpdir:
            allowlist_path = Path(tmpdir) / 'allowlist.json'
            
            # Create existing allowlist with pattern
            existing_data = {'patterns': ['lsof'], 'denylist': []}
            with open(allowlist_path, 'w') as f:
                json.dump(existing_data, f)
            
            with patch('wtf.core.permissions.get_allowlist_path', return_value=allowlist_path):
                with patch('wtf.core.permissions.console'):
                    add_to_allowlist('lsof')  # Same pattern
                
                # Verify no duplicate
                with open(allowlist_path) as f:
                    data = json.load(f)
                assert data.get('patterns', []).count('lsof') == 1


class TestLoadAllowlist:
    """Tests for the load_allowlist function."""

    def test_load_nonexistent_allowlist(self) -> None:
        """Test loading when allowlist file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            allowlist_path = Path(tmpdir) / 'nonexistent.json'
            
            with patch('wtf.core.permissions.get_allowlist_path', return_value=allowlist_path):
                result = load_allowlist()
                assert result == []

    def test_load_valid_allowlist(self) -> None:
        """Test loading a valid allowlist file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            allowlist_path = Path(tmpdir) / 'allowlist.json'
            
            data = {'patterns': ['git commit', 'npm install', 'lsof']}
            with open(allowlist_path, 'w') as f:
                json.dump(data, f)
            
            with patch('wtf.core.permissions.get_allowlist_path', return_value=allowlist_path):
                result = load_allowlist()
                assert result == ['git commit', 'npm install', 'lsof']

    def test_load_corrupted_allowlist(self) -> None:
        """Test loading a corrupted allowlist file returns empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            allowlist_path = Path(tmpdir) / 'allowlist.json'
            
            # Write invalid JSON
            with open(allowlist_path, 'w') as f:
                f.write('not valid json {{{')
            
            with patch('wtf.core.permissions.get_allowlist_path', return_value=allowlist_path):
                result = load_allowlist()
                assert result == []


class TestPermissionIntegration:
    """Integration tests for the full permission flow."""

    @patch('wtf.core.permissions.Prompt.ask')
    @patch('wtf.core.permissions.console')
    def test_always_adds_to_allowlist(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """Test that choosing 'always' actually adds to allowlist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            allowlist_path = Path(tmpdir) / 'allowlist.json'
            
            with patch('wtf.core.permissions.get_allowlist_path', return_value=allowlist_path):
                mock_ask.return_value = 'a'
                
                result = prompt_for_permission(
                    cmd='lsof -ti:8080 | xargs kill -9',
                    explanation='kill port',
                    allowlist_pattern='lsof'
                )
                
                assert result == 'yes_always'
                
                # Now add_to_allowlist should be called by the caller (tools.py)
                # Let's verify by calling it manually as the flow would
                add_to_allowlist('lsof')
                
                # Verify it was added
                patterns = load_allowlist()
                assert 'lsof' in patterns

    def test_command_allowed_after_adding_to_allowlist(self) -> None:
        """Test that a command is auto-executed after being added to allowlist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            allowlist_path = Path(tmpdir) / 'allowlist.json'
            
            with patch('wtf.core.permissions.get_allowlist_path', return_value=allowlist_path):
                # Use a command that's not in the safe read-only list
                # npm install is NOT safe (it modifies node_modules)
                result = should_auto_execute('npm install express', [], [], {})
                assert result == 'ask'
                
                # Add to allowlist
                with patch('wtf.core.permissions.console'):
                    add_to_allowlist('npm install')
                
                # Now should be allowed
                allowlist = load_allowlist()
                result = should_auto_execute('npm install express', allowlist, [], {})
                assert result == 'auto'
