"""Tests for memory system."""

import pytest
import json
import tempfile
from pathlib import Path

from wtf.conversation.memory import (
    save_memory,
    load_memories,
    search_memories,
    delete_memory,
    clear_memories,
)


@pytest.fixture
def temp_config_dir(monkeypatch):
    """Create a temporary directory for config files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Monkeypatch get_config_dir in both modules
        from wtf.core import config as config_module
        from wtf.conversation import memory as memory_module

        monkeypatch.setattr(config_module, 'get_config_dir', lambda: tmpdir)
        monkeypatch.setattr(memory_module, 'get_config_dir', lambda: tmpdir)
        yield tmpdir


def test_save_memory(temp_config_dir):
    """Test saving a memory."""
    save_memory("editor", "emacs", confidence=0.9)

    # Check file was created and contains the memory
    memory_path = Path(temp_config_dir) / "memories.json"
    assert memory_path.exists()

    with open(memory_path, 'r') as f:
        data = json.load(f)
        assert "editor" in data
        assert data["editor"]["value"] == "emacs"
        assert data["editor"]["confidence"] == 0.9
        assert "timestamp" in data["editor"]


def test_save_multiple_memories(temp_config_dir):
    """Test saving multiple memories."""
    save_memory("editor", "emacs")
    save_memory("package_manager", "npm")
    save_memory("python_version", "3.11")

    memories = load_memories()
    assert len(memories) == 3
    assert memories["editor"]["value"] == "emacs"
    assert memories["package_manager"]["value"] == "npm"
    assert memories["python_version"]["value"] == "3.11"


def test_load_memories_empty(temp_config_dir):
    """Test loading from empty memory file."""
    memories = load_memories()
    assert memories == {}


def test_load_memories(temp_config_dir):
    """Test loading memories."""
    save_memory("editor", "vim")
    save_memory("shell", "zsh")

    memories = load_memories()
    assert len(memories) == 2
    assert "editor" in memories
    assert "shell" in memories


def test_search_memories(temp_config_dir):
    """Test searching memories."""
    save_memory("editor_preference", "emacs")
    save_memory("package_manager", "npm")
    save_memory("editor_theme", "dark")

    # Search for "editor" should find both editor-related memories
    results = search_memories("editor")
    assert len(results) == 2
    assert any("editor_preference" in key for key in results.keys())
    assert any("editor_theme" in key for key in results.keys())


def test_search_memories_no_results(temp_config_dir):
    """Test searching with no matches."""
    save_memory("editor", "vim")

    results = search_memories("python")
    assert len(results) == 0


def test_delete_memory(temp_config_dir):
    """Test deleting a memory."""
    save_memory("editor", "vim")
    save_memory("shell", "zsh")

    # Delete one
    delete_memory("editor")

    memories = load_memories()
    assert len(memories) == 1
    assert "editor" not in memories
    assert "shell" in memories


def test_delete_nonexistent_memory(temp_config_dir):
    """Test deleting a memory that doesn't exist."""
    save_memory("editor", "vim")

    # Should not raise an error
    delete_memory("nonexistent")

    memories = load_memories()
    assert len(memories) == 1


def test_clear_memories(temp_config_dir):
    """Test clearing all memories."""
    save_memory("editor", "vim")
    save_memory("shell", "zsh")
    save_memory("package_manager", "npm")

    # Clear all
    clear_memories()

    memories = load_memories()
    assert len(memories) == 0


def test_memory_update_overwrites(temp_config_dir):
    """Test that saving the same key overwrites the previous value."""
    save_memory("editor", "vim")
    save_memory("editor", "emacs")

    memories = load_memories()
    assert memories["editor"]["value"] == "emacs"
    assert len(memories) == 1


def test_memory_with_complex_value(temp_config_dir):
    """Test saving memory with complex value."""
    complex_value = {
        "primary": "emacs",
        "fallback": "vim",
        "plugins": ["magit", "evil"]
    }

    save_memory("editor_config", complex_value)

    memories = load_memories()
    assert memories["editor_config"]["value"] == complex_value
