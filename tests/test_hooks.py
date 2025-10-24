"""Tests for shell hook setup."""

import pytest
from pathlib import Path
import tempfile
import os

from wtf.setup.hooks import (
    get_shell_config_file,
    setup_error_hook,
    setup_not_found_hook,
    remove_hooks,
)


class TestGetShellConfigFile:
    """Test shell config file detection."""

    def test_get_zsh_config(self):
        """Test getting zsh config file."""
        config = get_shell_config_file('zsh')
        assert config is not None
        assert '.zshrc' in str(config) or '.zsh_profile' in str(config)

    def test_get_bash_config(self):
        """Test getting bash config file."""
        config = get_shell_config_file('bash')
        assert config is not None
        assert 'bash' in str(config).lower()

    def test_get_fish_config(self):
        """Test getting fish config file."""
        config = get_shell_config_file('fish')
        assert config is not None
        assert 'fish' in str(config)

    def test_get_unknown_shell(self):
        """Test getting config for unknown shell."""
        config = get_shell_config_file('unknown')
        assert config is None


class TestSetupErrorHook:
    """Test error hook setup."""

    def test_setup_error_hook_zsh(self, tmp_path, monkeypatch):
        """Test setting up error hook for zsh."""
        # Create temp config file
        config_file = tmp_path / ".zshrc"
        config_file.write_text("# existing config\n")

        # Mock get_shell_config_file to return our temp file
        def mock_get_config(shell_type):
            return config_file

        monkeypatch.setattr('wtf.setup.hooks.get_shell_config_file', mock_get_config)

        # Setup hook
        success, message = setup_error_hook('zsh')

        assert success is True
        assert "Error hook added" in message

        # Verify hook was added
        content = config_file.read_text()
        assert 'wtf_error_hook' in content
        assert 'wtf-error-hook-start' in content
        assert 'wtf-error-hook-end' in content
        assert 'precmd_functions' in content

    def test_setup_error_hook_bash(self, tmp_path, monkeypatch):
        """Test setting up error hook for bash."""
        config_file = tmp_path / ".bashrc"
        config_file.write_text("# existing config\n")

        def mock_get_config(shell_type):
            return config_file

        monkeypatch.setattr('wtf.setup.hooks.get_shell_config_file', mock_get_config)

        success, message = setup_error_hook('bash')

        assert success is True
        content = config_file.read_text()
        assert 'wtf_error_hook' in content
        assert 'PROMPT_COMMAND' in content

    def test_setup_error_hook_fish(self, tmp_path, monkeypatch):
        """Test setting up error hook for fish."""
        config_file = tmp_path / "config.fish"
        config_file.write_text("# existing config\n")

        def mock_get_config(shell_type):
            return config_file

        monkeypatch.setattr('wtf.setup.hooks.get_shell_config_file', mock_get_config)

        success, message = setup_error_hook('fish')

        assert success is True
        content = config_file.read_text()
        assert 'wtf_error_hook' in content
        assert 'fish_postexec' in content

    def test_setup_error_hook_already_exists(self, tmp_path, monkeypatch):
        """Test that setup fails if hook already exists."""
        config_file = tmp_path / ".zshrc"
        config_file.write_text("# wtf-error-hook\n")

        def mock_get_config(shell_type):
            return config_file

        monkeypatch.setattr('wtf.setup.hooks.get_shell_config_file', mock_get_config)

        success, message = setup_error_hook('zsh')

        assert success is False
        assert "already exists" in message

    def test_setup_error_hook_creates_file(self, tmp_path, monkeypatch):
        """Test that setup creates config file if it doesn't exist."""
        config_file = tmp_path / "new_dir" / ".zshrc"

        def mock_get_config(shell_type):
            return config_file

        monkeypatch.setattr('wtf.setup.hooks.get_shell_config_file', mock_get_config)

        success, message = setup_error_hook('zsh')

        assert success is True
        assert config_file.exists()


class TestSetupNotFoundHook:
    """Test command-not-found hook setup."""

    def test_setup_not_found_hook_zsh(self, tmp_path, monkeypatch):
        """Test setting up not-found hook for zsh."""
        config_file = tmp_path / ".zshrc"
        config_file.write_text("# existing config\n")

        def mock_get_config(shell_type):
            return config_file

        monkeypatch.setattr('wtf.setup.hooks.get_shell_config_file', mock_get_config)

        success, message = setup_not_found_hook('zsh')

        assert success is True
        content = config_file.read_text()
        assert 'command_not_found_handler' in content
        assert 'wtf-not-found-hook-start' in content

    def test_setup_not_found_hook_bash(self, tmp_path, monkeypatch):
        """Test setting up not-found hook for bash."""
        config_file = tmp_path / ".bashrc"
        config_file.write_text("# existing config\n")

        def mock_get_config(shell_type):
            return config_file

        monkeypatch.setattr('wtf.setup.hooks.get_shell_config_file', mock_get_config)

        success, message = setup_not_found_hook('bash')

        assert success is True
        content = config_file.read_text()
        assert 'command_not_found_handle' in content

    def test_setup_not_found_hook_fish(self, tmp_path, monkeypatch):
        """Test setting up not-found hook for fish."""
        config_file = tmp_path / "config.fish"
        config_file.write_text("# existing config\n")

        def mock_get_config(shell_type):
            return config_file

        monkeypatch.setattr('wtf.setup.hooks.get_shell_config_file', mock_get_config)

        success, message = setup_not_found_hook('fish')

        assert success is True
        content = config_file.read_text()
        assert 'fish_command_not_found' in content


class TestRemoveHooks:
    """Test hook removal."""

    def test_remove_hooks_removes_both(self, tmp_path, monkeypatch):
        """Test that remove_hooks removes both error and not-found hooks."""
        config_file = tmp_path / ".zshrc"
        config_file.write_text("""
# existing config
# wtf-error-hook-start
some error hook code
# wtf-error-hook-end

# wtf-not-found-hook-start
some not-found hook code
# wtf-not-found-hook-end

# more config
""")

        def mock_get_config(shell_type):
            return config_file

        monkeypatch.setattr('wtf.setup.hooks.get_shell_config_file', mock_get_config)

        success, message = remove_hooks('zsh')

        assert success is True
        content = config_file.read_text()

        # Hooks should be removed
        assert 'wtf-error-hook-start' not in content
        assert 'some error hook code' not in content
        assert 'wtf-not-found-hook-start' not in content
        assert 'some not-found hook code' not in content

        # Existing config should remain
        assert '# existing config' in content
        assert '# more config' in content

    def test_remove_hooks_no_hooks(self, tmp_path, monkeypatch):
        """Test remove_hooks when no hooks exist."""
        config_file = tmp_path / ".zshrc"
        config_file.write_text("# just normal config\n")

        def mock_get_config(shell_type):
            return config_file

        monkeypatch.setattr('wtf.setup.hooks.get_shell_config_file', mock_get_config)

        success, message = remove_hooks('zsh')

        assert success is False
        assert "No wtf hooks found" in message

    def test_remove_hooks_file_not_found(self, tmp_path, monkeypatch):
        """Test remove_hooks when config file doesn't exist."""
        config_file = tmp_path / "nonexistent.zshrc"

        def mock_get_config(shell_type):
            return config_file

        monkeypatch.setattr('wtf.setup.hooks.get_shell_config_file', mock_get_config)

        success, message = remove_hooks('zsh')

        assert success is False
        assert "not found" in message
