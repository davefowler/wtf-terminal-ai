"""
Tests for meta commands (memory management).

These tests verify that wtf can handle memory operations
via AI tools (save_user_memory, get_user_memories, delete_user_memory, clear_user_memories).
"""

import pytest
from pathlib import Path
from wtf.core.config import get_config_dir
from wtf.conversation.memory import load_memories, save_memory, delete_memory, clear_memories


class TestMemoryCommands:
    """Test memory management via natural language."""

    @pytest.fixture
    def clean_memories(self):
        """Ensure clean memories for tests."""
        config_dir = get_config_dir()
        memories_file = config_dir / "memories.json"

        # Backup existing memories
        backup = None
        if memories_file.exists():
            backup = memories_file.read_text()

        # Clear memories
        clear_memories()

        yield

        # Restore
        if backup:
            memories_file.write_text(backup)
        else:
            if memories_file.exists():
                memories_file.unlink()

    def test_remember_command_simple(self, clean_memories):
        """Test: save_user_memory tool saves single memory"""
        from wtf.ai.tools import save_user_memory

        result = save_user_memory("editor", "emacs")

        assert result["success"] is True
        assert "editor" in result["message"].lower()

        # Verify memory was saved
        memories = load_memories()
        assert "editor" in memories
        assert memories["editor"]["value"] == "emacs"

    def test_remember_command_preference(self, clean_memories):
        """Test: save_user_memory tool saves preferences"""
        from wtf.ai.tools import save_user_memory

        result = save_user_memory("package_manager", "npm")

        assert result["success"] is True

        memories = load_memories()
        assert "package_manager" in memories
        assert memories["package_manager"]["value"] == "npm"

    def test_show_memories_command(self, clean_memories):
        """Test: get_user_memories tool"""
        from wtf.ai.tools import get_user_memories

        # Set up some memories
        save_memory("editor", "emacs")
        save_memory("shell", "zsh")

        # Get memories via tool
        result = get_user_memories()

        assert result["success"] is True
        assert result["count"] == 2
        assert "editor" in result["memories"]
        assert "shell" in result["memories"]

    def test_show_memories_empty(self, clean_memories):
        """Test get_user_memories when none exist."""
        from wtf.ai.tools import get_user_memories

        result = get_user_memories()

        assert result["success"] is True
        assert result["count"] == 0

    def test_forget_specific_command(self, clean_memories):
        """Test: delete_user_memory tool"""
        from wtf.ai.tools import delete_user_memory

        # Set up a memory
        save_memory("editor", "emacs")

        # Verify it exists
        memories = load_memories()
        assert "editor" in memories

        # Delete via tool
        result = delete_user_memory("editor")

        assert result["success"] is True

        # Verify it's gone
        memories = load_memories()
        assert "editor" not in memories

    def test_clear_memories(self, clean_memories):
        """Test: clear_user_memories tool"""
        from wtf.ai.tools import clear_user_memories

        # Set up some memories
        save_memory("editor", "emacs")
        save_memory("shell", "zsh")
        save_memory("package_manager", "npm")

        memories = load_memories()
        assert len(memories) > 0

        # Clear via tool
        result = clear_user_memories()

        assert result["success"] is True

        # Verify all cleared
        memories = load_memories()
        assert len(memories) == 0

    def test_forget_everything(self, clean_memories):
        """Test: clear_user_memories tool (alias test)"""
        from wtf.ai.tools import clear_user_memories

        # Set up memories
        save_memory("editor", "emacs")
        save_memory("shell", "zsh")

        result = clear_user_memories()

        assert result["success"] is True

        memories = load_memories()
        assert len(memories) == 0


class TestMemoryPersistence:
    """Test that memories persist across invocations."""

    @pytest.fixture
    def clean_memories(self):
        """Ensure clean memories for tests."""
        config_dir = get_config_dir()
        memories_file = config_dir / "memories.json"

        backup = None
        if memories_file.exists():
            backup = memories_file.read_text()

        clear_memories()

        yield

        if backup:
            memories_file.write_text(backup)
        else:
            if memories_file.exists():
                memories_file.unlink()

    def test_memory_persists(self, clean_memories):
        """Test that saved memories persist."""
        # Save a memory
        save_memory("test_key", "test_value")

        # Load in a fresh call
        memories = load_memories()

        assert "test_key" in memories
        assert memories["test_key"]["value"] == "test_value"

    def test_multiple_memories(self, clean_memories):
        """Test saving multiple memories."""
        save_memory("key1", "value1")
        save_memory("key2", "value2")
        save_memory("key3", "value3")

        memories = load_memories()

        assert len(memories) >= 3
        assert "key1" in memories
        assert "key2" in memories
        assert "key3" in memories

    def test_overwrite_memory(self, clean_memories):
        """Test that saving same key overwrites."""
        save_memory("editor", "vim")
        save_memory("editor", "emacs")

        memories = load_memories()

        assert memories["editor"]["value"] == "emacs"


class TestMemoryOperations:
    """Test low-level memory operations."""

    @pytest.fixture
    def clean_memories(self):
        """Ensure clean memories for tests."""
        config_dir = get_config_dir()
        memories_file = config_dir / "memories.json"

        backup = None
        if memories_file.exists():
            backup = memories_file.read_text()

        clear_memories()

        yield

        if backup:
            memories_file.write_text(backup)
        else:
            if memories_file.exists():
                memories_file.unlink()

    def test_save_and_load(self, clean_memories):
        """Test basic save and load operations."""
        save_memory("test", "data")

        memories = load_memories()
        assert "test" in memories

    def test_delete_memory(self, clean_memories):
        """Test deleting a specific memory."""
        save_memory("temp", "data")

        memories = load_memories()
        assert "temp" in memories

        delete_memory("temp")

        memories = load_memories()
        assert "temp" not in memories

    def test_delete_nonexistent(self, clean_memories):
        """Test deleting a memory that doesn't exist."""
        # Should not crash
        delete_memory("nonexistent_key")

    def test_load_empty(self, clean_memories):
        """Test loading when no memories exist."""
        memories = load_memories()

        assert isinstance(memories, dict)
        assert len(memories) == 0
