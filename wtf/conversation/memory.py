"""Memory system for user preferences."""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from wtf.core.config import get_config_dir


def get_memory_path() -> Path:
    """
    Get path to memories.json file.

    Returns:
        Path to memory file
    """
    return Path(get_config_dir()) / "memories.json"


def save_memory(key: str, value: Any, confidence: float = 1.0) -> None:
    """
    Save a memory to memories.json.

    Args:
        key: Memory key (e.g., "editor", "package_manager")
        value: Memory value (can be any JSON-serializable type)
        confidence: Confidence score 0-1 (default: 1.0)
    """
    memories = load_memories()

    memories[key] = {
        "value": value,
        "confidence": confidence,
        "timestamp": datetime.now().isoformat()
    }

    memory_path = get_memory_path()
    with open(memory_path, 'w') as f:
        json.dump(memories, f, indent=2)


def load_memories() -> Dict[str, Any]:
    """
    Load all memories from memories.json.

    Returns:
        Dictionary of all memories
    """
    memory_path = get_memory_path()

    if not memory_path.exists():
        return {}

    try:
        with open(memory_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def search_memories(query: str) -> Dict[str, Any]:
    """
    Search for memories matching a query.

    Args:
        query: Search string

    Returns:
        Dictionary of matching memories
    """
    memories = load_memories()
    query_lower = query.lower()

    results = {}
    for key, memory_data in memories.items():
        # Search in key and value
        if query_lower in key.lower():
            results[key] = memory_data
        elif isinstance(memory_data.get("value"), str):
            if query_lower in memory_data["value"].lower():
                results[key] = memory_data

    return results


def delete_memory(key: str) -> None:
    """
    Delete a memory by key.

    Args:
        key: Memory key to delete
    """
    memories = load_memories()

    if key in memories:
        del memories[key]

        memory_path = get_memory_path()
        with open(memory_path, 'w') as f:
            json.dump(memories, f, indent=2)


def clear_memories() -> None:
    """Clear all memories."""
    memory_path = get_memory_path()

    # Write empty dict
    with open(memory_path, 'w') as f:
        json.dump({}, f, indent=2)
