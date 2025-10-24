"""Tests for conversation history."""

import pytest
import json
import tempfile
import os
from pathlib import Path
from datetime import datetime

from wtf.conversation.history import (
    append_to_history,
    get_recent_conversations,
    maybe_rotate_history,
    cleanup_old_history,
)


@pytest.fixture
def temp_history_dir(monkeypatch):
    """Create a temporary directory for history files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Monkeypatch get_config_dir in both modules
        from wtf.core import config as config_module
        from wtf.conversation import history as history_module

        monkeypatch.setattr(config_module, 'get_config_dir', lambda: tmpdir)
        monkeypatch.setattr(history_module, 'get_config_dir', lambda: tmpdir)
        yield tmpdir


def test_append_to_history(temp_history_dir):
    """Test appending conversation to history."""
    conversation = {
        "query": "test query",
        "response": "test response",
        "commands": ["git status"],
        "exit_code": 0
    }

    append_to_history(conversation)

    # Check file was created and contains the conversation
    history_path = Path(temp_history_dir) / "history.jsonl"
    assert history_path.exists()

    with open(history_path, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 1

        data = json.loads(lines[0])
        assert data["query"] == "test query"
        assert data["response"] == "test response"
        assert "timestamp" in data


def test_append_multiple_conversations(temp_history_dir):
    """Test appending multiple conversations."""
    for i in range(3):
        conversation = {
            "query": f"query {i}",
            "response": f"response {i}",
            "commands": [],
            "exit_code": 0
        }
        append_to_history(conversation)

    history_path = Path(temp_history_dir) / "history.jsonl"
    with open(history_path, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 3


def test_get_recent_conversations(temp_history_dir):
    """Test reading recent conversations."""
    # Append some conversations
    for i in range(5):
        conversation = {
            "query": f"query {i}",
            "response": f"response {i}",
            "commands": [],
            "exit_code": 0
        }
        append_to_history(conversation)

    # Get last 3
    recent = get_recent_conversations(count=3)
    assert len(recent) == 3

    # Should be in reverse order (most recent first)
    assert recent[0]["query"] == "query 4"
    assert recent[1]["query"] == "query 3"
    assert recent[2]["query"] == "query 2"


def test_get_recent_conversations_empty(temp_history_dir):
    """Test reading from empty history."""
    recent = get_recent_conversations(count=10)
    assert recent == []


def test_maybe_rotate_history_small_file(temp_history_dir):
    """Test that small files don't get rotated."""
    # Add one conversation
    conversation = {
        "query": "test",
        "response": "test",
        "commands": [],
        "exit_code": 0
    }
    append_to_history(conversation)

    # Try to rotate - should not rotate
    maybe_rotate_history()

    # Check that no rotation file was created
    history_dir = Path(temp_history_dir)
    rotation_files = list(history_dir.glob("history.jsonl.*"))
    assert len(rotation_files) == 0


def test_maybe_rotate_history_large_file(temp_history_dir):
    """Test that large files get rotated."""
    history_path = Path(temp_history_dir) / "history.jsonl"

    # Create a file larger than 10MB
    with open(history_path, 'w') as f:
        # Write 11MB of data
        for _ in range(11000):  # 11000 lines of ~1KB each
            line = json.dumps({
                "query": "x" * 1000,
                "response": "y" * 1000,
                "commands": [],
                "exit_code": 0,
                "timestamp": "2024-01-01T00:00:00"
            }) + "\n"
            f.write(line)

    # File should be > 10MB now
    assert history_path.stat().st_size > 10 * 1024 * 1024

    # Rotate
    maybe_rotate_history()

    # Check that rotation file was created
    history_dir = Path(temp_history_dir)
    rotation_files = list(history_dir.glob("history.jsonl.*"))
    assert len(rotation_files) == 1

    # Original file should be empty or not exist
    if history_path.exists():
        assert history_path.stat().st_size == 0


def test_cleanup_old_history(temp_history_dir):
    """Test cleaning up old rotation files."""
    history_dir = Path(temp_history_dir)

    # Create 7 fake rotation files
    for i in range(7):
        rotation_file = history_dir / f"history.jsonl.{i}"
        rotation_file.write_text("test data")

    # Cleanup, keeping only 5
    cleanup_old_history(keep_n=5)

    # Should have only 5 files remaining
    rotation_files = sorted(history_dir.glob("history.jsonl.*"))
    assert len(rotation_files) == 5

    # Should keep the most recent ones (higher numbers)
    assert rotation_files[-1].name == "history.jsonl.6"
    assert rotation_files[0].name == "history.jsonl.2"
