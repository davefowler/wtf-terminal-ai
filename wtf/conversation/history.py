"""Conversation history management."""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from wtf.core.config import get_config_dir


def get_history_path() -> Path:
    """
    Get path to history.jsonl file.

    Returns:
        Path to history file
    """
    return Path(get_config_dir()) / "history.jsonl"


def append_to_history(conversation: Dict[str, Any]) -> None:
    """
    Append a conversation to history.jsonl.

    Args:
        conversation: Dictionary with query, response, commands, exit_code
    """
    history_path = get_history_path()

    # Add timestamp if not present
    if "timestamp" not in conversation:
        conversation["timestamp"] = datetime.now().isoformat()

    # Append to file
    with open(history_path, 'a') as f:
        f.write(json.dumps(conversation) + "\n")


def get_recent_conversations(count: int = 10) -> List[Dict[str, Any]]:
    """
    Get the most recent N conversations from history.

    Args:
        count: Number of conversations to retrieve

    Returns:
        List of conversation dictionaries, most recent first
    """
    history_path = get_history_path()

    if not history_path.exists():
        return []

    # Read all lines and return the last N
    try:
        with open(history_path, 'r') as f:
            lines = f.readlines()

        # Get last N lines
        recent_lines = lines[-count:] if len(lines) >= count else lines

        # Parse JSON and reverse (most recent first)
        conversations = []
        for line in reversed(recent_lines):
            line = line.strip()
            if line:
                try:
                    conversations.append(json.loads(line))
                except json.JSONDecodeError:
                    # Skip malformed lines
                    continue

        return conversations

    except Exception:
        return []


def maybe_rotate_history() -> None:
    """
    Rotate history file if it's larger than 10MB.

    Renames history.jsonl to history.jsonl.{timestamp}
    and starts a new history.jsonl file.
    """
    history_path = get_history_path()

    if not history_path.exists():
        return

    # Check file size
    file_size = history_path.stat().st_size
    max_size = 10 * 1024 * 1024  # 10MB

    if file_size <= max_size:
        return

    # Rotate the file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    rotation_path = history_path.parent / f"history.jsonl.{timestamp}"

    # Rename current file to rotation file
    history_path.rename(rotation_path)

    # New history.jsonl will be created on next append


def cleanup_old_history(keep_n: int = 5) -> None:
    """
    Remove old rotation files, keeping only the most recent N.

    Args:
        keep_n: Number of rotation files to keep
    """
    history_dir = Path(get_config_dir())

    # Find all rotation files
    rotation_files = sorted(history_dir.glob("history.jsonl.*"))

    if len(rotation_files) <= keep_n:
        return

    # Remove oldest files
    files_to_remove = rotation_files[:-keep_n]
    for file_path in files_to_remove:
        try:
            file_path.unlink()
        except OSError:
            # Ignore errors when deleting
            pass
