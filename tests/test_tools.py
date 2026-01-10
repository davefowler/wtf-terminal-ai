"""Tests for AI agent tools."""

import pytest
import tempfile
import os
from pathlib import Path

from wtf.ai.tools import (
    run_command,
    read_file,
    grep,
    glob_files,
    lookup_history,
    get_config,
    update_config,
    TOOLS,
    get_tool_definitions
)


class TestRunCommand:
    """Tests for run_command tool."""

    @pytest.fixture(autouse=True)
    def skip_permissions(self):
        """Skip permission prompts in tests."""
        os.environ['WTF_SKIP_PERMISSIONS'] = '1'
        yield
        os.environ.pop('WTF_SKIP_PERMISSIONS', None)

    def test_simple_command(self):
        """Test running a simple command."""
        result = run_command("echo 'hello'")

        assert result["exit_code"] == 0
        assert "hello" in result["output"]
        assert result["should_print"] is True

    def test_command_with_error(self):
        """Test command that fails."""
        result = run_command("false")

        assert result["exit_code"] != 0
        assert result["should_print"] is True

    def test_command_timeout(self):
        """Test command that times out."""
        result = run_command("sleep 60")

        assert "timed out" in result["output"].lower()
        assert result["exit_code"] == 124
        assert result["should_print"] is True


class TestReadFile:
    """Tests for read_file tool."""

    def test_read_existing_file(self):
        """Test reading an existing file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("test content\n")
            f.flush()
            filepath = f.name

        try:
            result = read_file(filepath)

            assert result["content"] == "test content\n"
            assert result["error"] is None
            assert result["should_print"] is False
        finally:
            os.unlink(filepath)

    def test_read_nonexistent_file(self):
        """Test reading a file that doesn't exist."""
        result = read_file("/tmp/nonexistent_file_xyz.txt")

        assert result["content"] is None
        assert "not found" in result["error"].lower()
        assert result["should_print"] is False

    def test_read_directory(self):
        """Test reading a directory (should fail)."""
        result = read_file("/tmp")

        assert result["content"] is None
        assert "not a file" in result["error"].lower()
        assert result["should_print"] is False


class TestGrep:
    """Tests for grep tool."""

    def test_grep_basic(self):
        """Test basic grep functionality."""
        # Create temp directory with test files
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("hello world\nfoo bar\nhello again\n")

            result = grep("hello", tmpdir)

            assert result["count"] >= 1  # At least one match
            assert result["should_print"] is False

    def test_grep_no_matches(self):
        """Test grep with no matches."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("foo bar\n")

            result = grep("xyz", tmpdir)

            assert result["count"] == 0
            assert result["should_print"] is False


class TestGlobFiles:
    """Tests for glob_files tool."""

    def test_glob_simple_pattern(self):
        """Test glob with simple pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            (Path(tmpdir) / "test1.txt").touch()
            (Path(tmpdir) / "test2.txt").touch()
            (Path(tmpdir) / "other.log").touch()

            result = glob_files("*.txt", tmpdir)

            assert result["count"] == 2
            assert all("txt" in f for f in result["files"])
            assert result["should_print"] is False

    def test_glob_recursive(self):
        """Test glob with recursive pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested structure
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()
            (Path(tmpdir) / "test.py").touch()
            (subdir / "nested.py").touch()

            result = glob_files("**/*.py", tmpdir)

            assert result["count"] == 2
            assert result["should_print"] is False

    def test_glob_no_matches(self):
        """Test glob with no matches."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = glob_files("*.xyz", tmpdir)

            assert result["count"] == 0
            assert result["files"] == []
            assert result["should_print"] is False


class TestLookupHistory:
    """Tests for lookup_history tool."""

    def test_lookup_history(self):
        """Test looking up conversation history."""
        result = lookup_history(limit=5)

        # Should return a valid structure even if empty
        assert "conversations" in result
        assert "count" in result
        assert isinstance(result["conversations"], list)
        assert result["count"] == len(result["conversations"])
        assert result["should_print"] is False


class TestConfigTools:
    """Tests for config get/update tools."""

    def test_get_config(self):
        """Test getting config."""
        result = get_config()

        # Should return config structure
        assert "value" in result
        assert isinstance(result["value"], dict)
        assert result["should_print"] is False

    def test_get_specific_config_key(self):
        """Test getting specific config key."""
        result = get_config("api")

        # Should return api config section
        assert "value" in result
        assert result["should_print"] is False


class TestToolRegistry:
    """Tests for tool registry and definitions."""

    def test_tools_dict(self):
        """Test TOOLS dictionary contains all tools."""
        expected_tools = [
            "run_command",
            "read_file",
            "grep",
            "glob_files",
            "lookup_history",
            "get_config",
            "update_config"
        ]

        for tool_name in expected_tools:
            assert tool_name in TOOLS
            assert callable(TOOLS[tool_name])

    def test_tool_definitions(self):
        """Test get_tool_definitions returns valid definitions."""
        definitions = get_tool_definitions()

        assert len(definitions) == 21  # Updated to 21: added memory tools (save, get, delete, clear) + search tools

        for tool_def in definitions:
            # Each definition should have required fields
            assert "name" in tool_def
            assert "description" in tool_def
            assert "parameters" in tool_def

            # Parameters should be a valid schema
            params = tool_def["parameters"]
            assert params["type"] == "object"
            assert "properties" in params
            assert "required" in params

    def test_tool_should_print_flags(self):
        """Test that tools correctly set should_print flag."""
        # run_command should print
        result = run_command("echo test")
        assert result["should_print"] is True

        # Internal tools should not print
        result = read_file("/tmp/test.txt")
        assert result["should_print"] is False

        result = glob_files("*.txt", "/tmp")
        assert result["should_print"] is False

        result = lookup_history()
        assert result["should_print"] is False

        result = get_config()
        assert result["should_print"] is False
