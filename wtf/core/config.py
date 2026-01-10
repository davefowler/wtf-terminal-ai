"""Configuration management for wtf."""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


def get_config_dir() -> Path:
    """Get the configuration directory path (~/.config/wtf/)."""
    config_home = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
    config_dir = Path(config_home) / 'wtf'
    return config_dir


def get_config_path() -> Path:
    """Get the config.json file path."""
    return get_config_dir() / 'config.json'


def get_allowlist_path() -> Path:
    """Get the allowlist.json file path."""
    return get_config_dir() / 'allowlist.json'


def get_wtf_md_path() -> Path:
    """Get the wtf.md file path."""
    return get_config_dir() / 'wtf.md'


def get_memories_path() -> Path:
    """Get the memories.json file path."""
    return get_config_dir() / 'memories.json'


def get_history_path() -> Path:
    """Get the history.jsonl file path."""
    return get_config_dir() / 'history.jsonl'


def get_default_config() -> Dict[str, Any]:
    """Get the default configuration."""
    return {
        "version": "0.1.0",
        "api": {
            "provider": "anthropic",
            "key_source": "env",
            "key": None,
            "model": "claude-opus-4"
        },
        "behavior": {
            "auto_execute_allowlist": True,
            "auto_allow_readonly": True,
            "context_history_size": 5,
            "verbose": False,
            "default_permission": "ask"
        },
        "shell": {
            "type": "zsh",
            "history_file": "~/.zsh_history"
        },
        "file_permissions": {
            "require_permission": [
                "*.env",
                ".env*",
                "*secret*",
                "*password*",
                "*credentials*",
                "*.key",
                "*.pem",
                "*.p12",
                "*.pfx",
                "*token*",
                "id_rsa*",
                "id_ed25519*",
                "*.ppk",
                "*.keystore",
                "config/master.key",
                ".aws/credentials",
                ".ssh/config"
            ],
            "always_block": [
                "/etc/shadow",
                "/etc/passwd",
                "*.kdbx",
                "*.wallet"
            ]
        }
    }


def get_default_allowlist() -> Dict[str, Any]:
    """Get the default allowlist configuration."""
    return {
        "patterns": [],
        "denylist": [
            "rm -rf /",
            "sudo rm",
            "dd if=",
            "mkfs",
            ":(){ :|:& };:"
        ]
    }


def get_default_wtf_md() -> str:
    """Get the default wtf.md template."""
    return """# My Custom Instructions for wtf

Add your custom instructions here. These will be included in every AI prompt.

## Examples:

- I prefer verbose explanations.
- I'm working on a Python project using Django.
- Always suggest type hints when showing Python code.
- I use npm instead of yarn.
- I prefer single quotes over double quotes in JavaScript.

wtf will remember these preferences and tailor its suggestions accordingly.
"""


def create_default_config() -> None:
    """Create default configuration files in ~/.config/wtf/."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    # Create config.json
    config_path = get_config_path()
    if not config_path.exists():
        with open(config_path, 'w') as f:
            json.dump(get_default_config(), f, indent=2)

    # Create allowlist.json
    allowlist_path = get_allowlist_path()
    if not allowlist_path.exists():
        with open(allowlist_path, 'w') as f:
            json.dump(get_default_allowlist(), f, indent=2)

    # Create wtf.md
    wtf_md_path = get_wtf_md_path()
    if not wtf_md_path.exists():
        with open(wtf_md_path, 'w') as f:
            f.write(get_default_wtf_md())

    # Create empty memories.json
    memories_path = get_memories_path()
    if not memories_path.exists():
        with open(memories_path, 'w') as f:
            json.dump({}, f, indent=2)

    # Create empty history.jsonl
    history_path = get_history_path()
    if not history_path.exists():
        history_path.touch()


def load_config() -> Dict[str, Any]:
    """
    Load configuration from config.json.

    Returns:
        Configuration dictionary with all expected keys.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        json.JSONDecodeError: If config file is corrupt.
    """
    config_path = get_config_path()

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = json.load(f)

    # Merge with defaults to ensure all keys exist
    default = get_default_config()

    # Deep merge to preserve nested structure
    def deep_merge(default: Dict, config: Dict) -> Dict:
        """Recursively merge config into default."""
        result = default.copy()
        for key, value in config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    return deep_merge(default, config)


def save_config(config: Dict[str, Any]) -> None:
    """
    Save configuration to config.json with backup.

    Args:
        config: Configuration dictionary to save.
    """
    config_path = get_config_path()

    # Create backup if config exists
    if config_path.exists():
        backup_path = config_path.parent / f"config.json.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(config_path, backup_path)

        # Keep only last 5 backups
        backups = sorted(config_path.parent.glob("config.json.backup.*"))
        if len(backups) > 5:
            for old_backup in backups[:-5]:
                old_backup.unlink()

    # Write new config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)


def config_exists() -> bool:
    """Check if configuration directory and files exist."""
    config_path = get_config_path()
    return config_path.exists()


def check_file_permission(file_path: str, config: Optional[Dict[str, Any]] = None) -> str:
    """
    Check if a file requires permission to read.

    Args:
        file_path: Path to the file to check
        config: Optional config dict (will load if not provided)

    Returns:
        "allow" - File can be read without asking
        "ask" - File requires user permission
        "block" - File should never be read
    """
    import fnmatch

    if config is None:
        config = load_config()

    file_permissions = config.get("file_permissions", {})

    # Normalize path for matching
    normalized_path = str(Path(file_path).expanduser())
    file_name = Path(file_path).name

    # Check always_block patterns first
    always_block = file_permissions.get("always_block", [])
    for pattern in always_block:
        if fnmatch.fnmatch(normalized_path, pattern) or fnmatch.fnmatch(file_name, pattern):
            return "block"

    # Check require_permission patterns
    require_permission = file_permissions.get("require_permission", [])
    for pattern in require_permission:
        if fnmatch.fnmatch(normalized_path, pattern) or fnmatch.fnmatch(file_name, pattern):
            return "ask"

    # Default: allow
    return "allow"
