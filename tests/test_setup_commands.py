"""
Tests for setup command detection.

These tests verify that wtf can detect natural language requests
to run setup/reconfigure and handle them appropriately.
"""

import pytest
from unittest.mock import patch, MagicMock
from wtf.cli import handle_setup_command


class TestSetupCommandDetection:
    """Test detection of setup/configuration commands."""

    @patch('wtf.cli.run_setup_wizard')
    @patch('wtf.cli.console')
    def test_change_provider(self, mock_console, mock_setup):
        """Test: wtf change my AI provider"""
        result = handle_setup_command("change my AI provider")
        # Should trigger setup wizard
        assert result is True
        mock_setup.assert_called_once()

    @patch('wtf.cli.run_setup_wizard')
    @patch('wtf.cli.console')
    def test_change_model(self, mock_console, mock_setup):
        """Test: wtf change my model"""
        result = handle_setup_command("change my model")
        assert result is True
        mock_setup.assert_called_once()

    @patch('wtf.cli.run_setup_wizard')
    @patch('wtf.cli.console')
    def test_switch_provider(self, mock_console, mock_setup):
        """Test: wtf switch to a different AI provider"""
        result = handle_setup_command("switch to a different AI provider")
        assert result is True
        mock_setup.assert_called_once()

    @patch('wtf.cli.run_setup_wizard')
    @patch('wtf.cli.console')
    def test_switch_to_openai(self, mock_console, mock_setup):
        """Test: wtf switch to OpenAI"""
        result = handle_setup_command("switch to OpenAI")
        assert result is True
        mock_setup.assert_called_once()

    @patch('wtf.cli.run_setup_wizard')
    @patch('wtf.cli.console')
    def test_use_different_provider(self, mock_console, mock_setup):
        """Test: wtf I want to use a different AI provider"""
        result = handle_setup_command("I want to use a different AI provider")
        assert result is True
        mock_setup.assert_called_once()

    @patch('wtf.cli.run_setup_wizard')
    @patch('wtf.cli.console')
    def test_use_another_model(self, mock_console, mock_setup):
        """Test: wtf use another model"""
        result = handle_setup_command("use another model")
        assert result is True
        mock_setup.assert_called_once()

    @patch('wtf.cli.run_setup_wizard')
    @patch('wtf.cli.console')
    def test_reconfigure(self, mock_console, mock_setup):
        """Test: wtf reconfigure"""
        result = handle_setup_command("reconfigure")
        assert result is True
        mock_setup.assert_called_once()

    @patch('wtf.cli.run_setup_wizard')
    @patch('wtf.cli.console')
    def test_reconfigure_everything(self, mock_console, mock_setup):
        """Test: wtf reconfigure everything"""
        result = handle_setup_command("reconfigure everything")
        assert result is True
        mock_setup.assert_called_once()

    @patch('wtf.cli.run_setup_wizard')
    @patch('wtf.cli.console')
    def test_setup_natural_language(self, mock_console, mock_setup):
        """Test: wtf setup (without flag)"""
        result = handle_setup_command("run setup")
        assert result is True
        mock_setup.assert_called_once()

    @patch('wtf.cli.run_setup_wizard')
    @patch('wtf.cli.console')
    def test_reset_config(self, mock_console, mock_setup):
        """Test: wtf reset my config"""
        result = handle_setup_command("reset my config")
        assert result is True
        mock_setup.assert_called_once()

    @patch('wtf.cli.run_setup_wizard')
    @patch('wtf.cli.console')
    def test_reset_settings(self, mock_console, mock_setup):
        """Test: wtf reset all settings"""
        result = handle_setup_command("reset all settings")
        assert result is True
        mock_setup.assert_called_once()


class TestNonSetupCommands:
    """Test that non-setup commands are not detected as setup."""

    def test_regular_query(self):
        """Test that regular queries are not setup commands."""
        result = handle_setup_command("what is my git status")
        assert result is False

    def test_model_query(self):
        """Test: wtf what model am I using?"""
        # This is asking a question, not requesting setup
        result = handle_setup_command("what model am I using")
        assert result is False

    def test_provider_question(self):
        """Test: wtf what provider do I have?"""
        result = handle_setup_command("what provider do I have")
        assert result is False

    def test_help_query(self):
        """Test: help me with something"""
        result = handle_setup_command("help me fix this error")
        assert result is False

    def test_use_command(self):
        """Test: wtf use git to push"""
        # "use" in context of running a command, not changing provider
        result = handle_setup_command("use git to push my changes")
        assert result is False

    def test_change_personality(self):
        """Test: wtf change your personality"""
        # This should be handled by AI, not setup wizard
        result = handle_setup_command("change your personality")
        assert result is False

    def test_cli_flag_not_detected(self):
        """Test: --setup flag should not trigger natural language handler"""
        # CLI flags are handled separately
        result = handle_setup_command("--setup")
        assert result is False


class TestSetupPatternVariations:
    """Test various ways users might express wanting to change setup."""

    @patch('wtf.cli.run_setup_wizard')
    @patch('wtf.cli.console')
    def test_switch_from_to(self, mock_console, mock_setup):
        """Test: wtf switch from Claude to GPT-4"""
        result = handle_setup_command("switch from Claude to GPT-4")
        assert result is True
        mock_setup.assert_called_once()

    @patch('wtf.cli.run_setup_wizard')
    @patch('wtf.cli.console')
    def test_change_to_specific_model(self, mock_console, mock_setup):
        """Test: wtf change to gpt-4"""
        result = handle_setup_command("change to gpt-4")
        assert result is True
        mock_setup.assert_called_once()

    @patch('wtf.cli.run_setup_wizard')
    @patch('wtf.cli.console')
    def test_want_to_use_different(self, mock_console, mock_setup):
        """Test: wtf I want to use a different model here"""
        result = handle_setup_command("I want to use a different model here")
        assert result is True
        mock_setup.assert_called_once()

    @patch('wtf.cli.run_setup_wizard')
    @patch('wtf.cli.console')
    def test_need_to_switch(self, mock_console, mock_setup):
        """Test: wtf I need to switch AI providers"""
        result = handle_setup_command("I need to switch AI providers")
        assert result is True
        mock_setup.assert_called_once()

    @patch('wtf.cli.run_setup_wizard')
    @patch('wtf.cli.console')
    def test_uppercase_variations(self, mock_console, mock_setup):
        """Test that detection is case-insensitive."""
        result = handle_setup_command("CHANGE MY PROVIDER")
        assert result is True
        mock_setup.assert_called_once()

    @patch('wtf.cli.run_setup_wizard')
    @patch('wtf.cli.console')
    def test_mixed_case(self, mock_console, mock_setup):
        """Test: wtf Change My AI Provider"""
        result = handle_setup_command("Change My AI Provider")
        assert result is True
        mock_setup.assert_called_once()


class TestSetupEdgeCases:
    """Test edge cases in setup command detection."""

    def test_empty_query(self):
        """Test empty string doesn't trigger setup."""
        result = handle_setup_command("")
        assert result is False

    def test_whitespace_only(self):
        """Test whitespace-only query doesn't trigger setup."""
        result = handle_setup_command("   ")
        assert result is False

    def test_partial_match_insufficient(self):
        """Test that partial matches don't incorrectly trigger."""
        # Just "change" without context shouldn't trigger
        result = handle_setup_command("how do I change a file")
        assert result is False

    def test_ambiguous_use(self):
        """Test: wtf use (ambiguous)"""
        # "use" alone is too ambiguous
        result = handle_setup_command("use")
        assert result is False
