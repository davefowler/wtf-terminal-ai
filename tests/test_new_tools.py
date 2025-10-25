"""Tests for new tools and file permissions."""

import pytest
import tempfile
import os
from pathlib import Path

from wtf.ai.tools import (
    check_command_exists,
    get_file_info,
    list_directory,
    check_package_installed,
    get_git_info,
    get_tool_definitions
)
from wtf.core.config import check_file_permission, get_default_config


class TestFilePermissions:
    """Test file permission checking system."""

    def test_normal_file_allowed(self):
        """Normal files should be allowed."""
        result = check_file_permission("test.py")
        assert result == "allow"

    def test_env_file_requires_permission(self):
        """Environment files should require permission."""
        result = check_file_permission(".env")
        assert result == "ask"

        result = check_file_permission(".env.local")
        assert result == "ask"

        result = check_file_permission("config/.env")
        assert result == "ask"

    def test_secret_files_require_permission(self):
        """Files with 'secret' in name should require permission."""
        result = check_file_permission("api_secrets.json")
        assert result == "ask"

        result = check_file_permission("my_secret_key.txt")
        assert result == "ask"

    def test_key_files_require_permission(self):
        """Key files should require permission."""
        result = check_file_permission("private.key")
        assert result == "ask"

        result = check_file_permission("certificate.pem")
        assert result == "ask"

    def test_blocked_files(self):
        """System files should be blocked."""
        result = check_file_permission("/etc/shadow")
        assert result == "block"

        result = check_file_permission("/etc/passwd")
        assert result == "block"


class TestCheckCommandExists:
    """Test check_command_exists tool."""

    def test_existing_command(self):
        """Test checking for command that exists."""
        # Use 'ls' which exists on all Unix-like systems
        result = check_command_exists("ls")
        assert result["exists"] is True
        assert result["path"] is not None
        assert "ls" in result["path"]

    def test_nonexistent_command(self):
        """Test checking for command that doesn't exist."""
        result = check_command_exists("nonexistent_command_xyz123")
        assert result["exists"] is False
        assert result["path"] is None


class TestGetFileInfo:
    """Test get_file_info tool."""

    def test_file_info(self):
        """Test getting info for a file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            f.flush()
            filepath = f.name

        try:
            result = get_file_info(filepath)
            assert result["exists"] is True
            assert result["type"] == "file"
            assert result["size"] > 0
            assert "permissions" in result
        finally:
            os.unlink(filepath)

    def test_directory_info(self):
        """Test getting info for a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = get_file_info(tmpdir)
            assert result["exists"] is True
            assert result["type"] == "directory"

    def test_nonexistent_file(self):
        """Test getting info for nonexistent file."""
        result = get_file_info("/tmp/nonexistent_xyz123.txt")
        assert result["exists"] is False


class TestListDirectory:
    """Test list_directory tool."""

    def test_list_directory(self):
        """Test listing directory contents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            (Path(tmpdir) / "file1.txt").touch()
            (Path(tmpdir) / "file2.py").touch()
            (Path(tmpdir) / "subdir").mkdir()

            result = list_directory(tmpdir)
            assert result["count"] == 3
            assert len(result["entries"]) == 3

            names = [e["name"] for e in result["entries"]]
            assert "file1.txt" in names
            assert "file2.py" in names
            assert "subdir" in names

    def test_list_with_pattern(self):
        """Test listing with glob pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test1.py").touch()
            (Path(tmpdir) / "test2.py").touch()
            (Path(tmpdir) / "other.txt").touch()

            result = list_directory(tmpdir, pattern="*.py")
            assert result["count"] == 2
            names = [e["name"] for e in result["entries"]]
            assert "test1.py" in names
            assert "test2.py" in names
            assert "other.txt" not in names


class TestGetGitInfo:
    """Test get_git_info tool."""

    def test_not_in_git_repo(self):
        """Test when not in a git repo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            result = get_git_info()
            assert result["is_repo"] is False

    def test_in_git_repo(self):
        """Test when in a git repo (assuming tests run in git repo)."""
        result = get_git_info()
        # This test might be in a git repo
        if result["is_repo"]:
            assert "branch" in result
            assert "status" in result
            assert "has_changes" in result


class TestToolFiltering:
    """Test contextual tool availability."""

    def test_all_tools_without_context(self):
        """When no context provided, all tools should be available."""
        tools = get_tool_definitions()
        tool_names = [t["name"] for t in tools]

        # All tools should be present
        assert "check_command_exists" in tool_names
        assert "get_file_info" in tool_names
        assert "list_directory" in tool_names
        assert "check_package_installed" in tool_names
        assert "get_git_info" in tool_names

    def test_git_tool_filtered_out(self):
        """Git tool should be filtered when not in git repo."""
        env_context = {
            "is_git_repo": False,
            "has_package_json": False
        }
        tools = get_tool_definitions(env_context)
        tool_names = [t["name"] for t in tools]

        assert "get_git_info" not in tool_names

    def test_git_tool_included(self):
        """Git tool should be included when in git repo."""
        env_context = {
            "is_git_repo": True,
            "has_package_json": False
        }
        tools = get_tool_definitions(env_context)
        tool_names = [t["name"] for t in tools]

        assert "get_git_info" in tool_names

    def test_package_tool_filtered_out(self):
        """Package tool should be filtered when no package files."""
        env_context = {
            "is_git_repo": True,
            "has_package_json": False,
            "has_requirements_txt": False,
            "has_cargo_toml": False,
            "has_gemfile": False
        }
        tools = get_tool_definitions(env_context)
        tool_names = [t["name"] for t in tools]

        assert "check_package_installed" not in tool_names

    def test_package_tool_included_with_npm(self):
        """Package tool should be included when package.json exists."""
        env_context = {
            "is_git_repo": True,
            "has_package_json": True,
            "has_requirements_txt": False
        }
        tools = get_tool_definitions(env_context)
        tool_names = [t["name"] for t in tools]

        assert "check_package_installed" in tool_names

    def test_package_tool_included_with_pip(self):
        """Package tool should be included when requirements.txt exists."""
        env_context = {
            "is_git_repo": False,
            "has_package_json": False,
            "has_requirements_txt": True
        }
        tools = get_tool_definitions(env_context)
        tool_names = [t["name"] for t in tools]

        assert "check_package_installed" in tool_names
