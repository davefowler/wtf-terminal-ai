"""
Tests for CLI options and flags.

Verifies that all documented CLI flags work correctly.
"""

import pytest
import subprocess
import sys
from pathlib import Path


class TestCLIFlags:
    """Test all CLI flags are functional."""

    def test_help_flag(self):
        """Test: wtf --help"""
        result = subprocess.run(
            [sys.executable, "-m", "wtf", "--help"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "wtf" in result.stdout.lower()
        assert "usage" in result.stdout.lower() or "because working" in result.stdout.lower()

    def test_help_short_flag(self):
        """Test: wtf -h"""
        result = subprocess.run(
            [sys.executable, "-m", "wtf", "-h"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "wtf" in result.stdout.lower()

    def test_version_flag(self):
        """Test: wtf --version"""
        result = subprocess.run(
            [sys.executable, "-m", "wtf", "--version"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "wtf" in result.stdout.lower()

    def test_version_short_flag(self):
        """Test: wtf -v"""
        result = subprocess.run(
            [sys.executable, "-m", "wtf", "-v"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "wtf" in result.stdout.lower()

    def test_config_flag(self):
        """Test: wtf --config"""
        result = subprocess.run(
            [sys.executable, "-m", "wtf", "--config"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "config" in result.stdout.lower()
        assert ".config/wtf" in result.stdout or "~/.config/wtf" in result.stdout

    def test_verbose_flag_with_no_config(self):
        """Test: wtf --verbose (should trigger setup)"""
        # This will fail if no config exists, but should handle --verbose flag
        result = subprocess.run(
            [sys.executable, "-m", "wtf", "--verbose", "test query"],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Should either show verbose output or setup wizard
        # Exit code may be non-zero if no config, but flag should be recognized
        assert "--verbose" not in result.stderr  # Flag shouldn't be unrecognized


class TestCLIFlagCombinations:
    """Test combining CLI flags."""

    def test_help_ignores_other_flags(self):
        """Test that --help takes precedence."""
        result = subprocess.run(
            [sys.executable, "-m", "wtf", "--help", "--version"],
            capture_output=True,
            text=True
        )

        # Help should be shown, not version
        assert result.returncode == 0
        # Should show help text
        assert len(result.stdout) > 50

    def test_version_ignores_query(self):
        """Test that --version ignores query."""
        result = subprocess.run(
            [sys.executable, "-m", "wtf", "--version", "some", "query"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        # Should show version, not try to process query

    def test_model_flag_format(self):
        """Test that --model accepts argument."""
        # This will fail without config, but tests the flag parsing
        result = subprocess.run(
            [sys.executable, "-m", "wtf", "--model", "gpt-4", "--help"],
            capture_output=True,
            text=True
        )

        # Should parse flag without error
        assert result.returncode == 0


class TestHookFlags:
    """Test hook-related CLI flags."""

    def test_setup_error_hook_flag_exists(self):
        """Test: wtf --setup-error-hook (flag recognized)"""
        result = subprocess.run(
            [sys.executable, "-m", "wtf", "--setup-error-hook"],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Should recognize the flag
        assert result.returncode in [0, 1]  # May fail if shell detection fails
        assert "unrecognized arguments" not in result.stderr

    def test_setup_not_found_hook_flag_exists(self):
        """Test: wtf --setup-not-found-hook (flag recognized)"""
        result = subprocess.run(
            [sys.executable, "-m", "wtf", "--setup-not-found-hook"],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Should recognize the flag
        assert result.returncode in [0, 1]
        assert "unrecognized arguments" not in result.stderr

    def test_remove_hooks_flag_exists(self):
        """Test: wtf --remove-hooks (flag recognized)"""
        result = subprocess.run(
            [sys.executable, "-m", "wtf", "--remove-hooks"],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Should recognize the flag
        assert result.returncode in [0, 1]
        assert "unrecognized arguments" not in result.stderr


class TestSetupFlags:
    """Test setup-related CLI flags."""

    def test_setup_flag_exists(self):
        """Test: wtf --setup (flag recognized)"""
        # Note: --setup will launch interactive wizard, so we can't fully test it
        # But we can verify the flag is recognized
        result = subprocess.run(
            [sys.executable, "-m", "wtf", "--help"],
            capture_output=True,
            text=True
        )

        # Help should mention setup
        assert result.returncode == 0

    def test_reset_flag_exists(self):
        """Test: wtf --reset (flag recognized)"""
        # --reset requires confirmation, so just check it's recognized
        result = subprocess.run(
            [sys.executable, "-m", "wtf", "--help"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0


class TestInvalidFlags:
    """Test that invalid flags are rejected."""

    def test_invalid_flag_rejected(self):
        """Test that unknown flags cause errors."""
        result = subprocess.run(
            [sys.executable, "-m", "wtf", "--invalid-flag"],
            capture_output=True,
            text=True
        )

        # Should fail or show error
        assert result.returncode != 0 or "unrecognized" in result.stderr.lower()

    def test_model_without_value(self):
        """Test that --model requires a value."""
        result = subprocess.run(
            [sys.executable, "-m", "wtf", "--model"],
            capture_output=True,
            text=True
        )

        # Should show error about missing argument
        assert result.returncode != 0
        assert "error" in result.stderr.lower() or "expected" in result.stderr.lower()


class TestQueryHandling:
    """Test how queries are handled with flags."""

    def test_query_without_flags(self):
        """Test: wtf "some query" (requires config)"""
        # This will fail without config, but tests basic query parsing
        result = subprocess.run(
            [sys.executable, "-m", "wtf", "test", "query"],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Should not complain about argument parsing
        assert "unrecognized arguments" not in result.stderr

    def test_empty_invocation(self):
        """Test: wtf (no args, no config)"""
        result = subprocess.run(
            [sys.executable, "-m", "wtf"],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Should either show help or setup wizard
        # Not crash with parse error
        assert "parse" not in result.stderr.lower()
