"""Tools for the AI agent to use."""

import os
import subprocess
import shutil
import stat
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from wtf.conversation.history import get_recent_conversations
from wtf.core.config import load_config, save_config, check_file_permission
from wtf.core.permissions import (
    load_allowlist,
    load_denylist,
    should_auto_execute,
    prompt_for_permission,
    add_to_allowlist,
)


class UserCancelledError(Exception):
    """Raised when user cancels a command - stops AI from trying alternatives."""
    pass


# OpenAI models with built-in web search (search works automatically)
OPENAI_SEARCH_MODELS = [
    "gpt-4o-search-preview",
    "gpt-4o-mini-search-preview",
]

# Our custom search tool names (excluded when using models with native search)
CUSTOM_SEARCH_TOOLS = [
    "duckduckgo_search",
    "tavily_search",
    "serper_search",
    "bing_search", 
    "brave_search",
    "web_instant_answers",
]


def detect_native_search_support(model_name: str) -> Tuple[str, bool]:
    """
    Detect if a model has native web search support that we can use.
    
    Currently supported:
    - OpenAI search models (gpt-4o-search-preview, gpt-4o-mini-search-preview):
      These have built-in search that works automatically.
    
    Not yet supported (uses custom search tools instead):
    - Anthropic Claude: Has native web_search tool, but the llm library doesn't
      support passing it through. Would require direct SDK usage.
    
    Args:
        model_name: The model identifier (e.g., "gpt-4o-search-preview", "claude-sonnet-4")
    
    Returns:
        Tuple of (provider, has_native_search):
        - provider: "openai_search", "openai", "anthropic", "gemini", "local", or "other"
        - has_native_search: True if model has built-in search we can use
    """
    model_lower = model_name.lower()
    
    # Check OpenAI search models (have built-in search, no extra config needed)
    for search_model in OPENAI_SEARCH_MODELS:
        if search_model in model_lower:
            return ("openai_search", True)
    
    # Check for other OpenAI models (no native search)
    if "gpt" in model_lower or "o1" in model_lower or "o3" in model_lower or "o4" in model_lower:
        return ("openai", False)
    
    # Check if it's an Anthropic model
    # NOTE: Claude has native web_search tool, but llm library doesn't support it yet.
    # For now, we use our custom search tools with Anthropic.
    # TODO: Add direct Anthropic SDK support for native web_search in the future.
    if "claude" in model_lower:
        return ("anthropic", False)
    
    # Check for Gemini models
    if "gemini" in model_lower:
        return ("gemini", False)
    
    # Check for Ollama/local models
    if "llama" in model_lower or "mistral" in model_lower or "qwen" in model_lower:
        return ("local", False)
    
    return ("other", False)


def run_command(command: str) -> Dict[str, Any]:
    """
    Execute a terminal command and return its output.

    This tool PRINTS output to the user - it's for running actual commands
    that the user wants to see the results of.

    Permission system:
    - Safe read-only commands (ls, cat, git status, etc.) auto-execute
    - Commands in user's allowlist auto-execute
    - Commands in denylist are blocked
    - Other commands prompt the user (with option to "always allow")

    Args:
        command: The shell command to execute

    Returns:
        Dict with:
        - output: Command stdout/stderr
        - exit_code: Exit code
        - should_print: True (output should be shown to user)
    """
    # Skip permission checks in test mode
    skip_permissions = os.environ.get('WTF_SKIP_PERMISSIONS') == '1'
    
    if not skip_permissions:
        # Load config and permission lists (with fallbacks for tests/first run)
        try:
            config = load_config()
        except FileNotFoundError:
            config = {}  # Use defaults
        allowlist = load_allowlist()
        denylist = load_denylist()
        
        # Check if command should auto-execute, ask, or deny
        permission = should_auto_execute(command, allowlist, denylist, config)
        
        if permission == "deny":
            return {
                "output": f"Command blocked by denylist: {command}",
                "exit_code": 1,
                "should_print": True,
                "blocked": True
            }
        
        if permission == "ask":
            # Extract base command for allowlist pattern (first word or first two for git/npm/etc)
            parts = command.strip().split()
            if len(parts) >= 2 and parts[0] in ("git", "npm", "pip", "cargo", "go", "docker", "kubectl"):
                allowlist_pattern = f"{parts[0]} {parts[1]}"
            else:
                allowlist_pattern = parts[0] if parts else command
            
            # Prompt user for permission
            response = prompt_for_permission(
                cmd=command,
                explanation="",  # AI should have explained already
                allowlist_pattern=allowlist_pattern
            )
            
            if response == "no":
                # Raise exception to stop AI from trying more commands
                raise UserCancelledError(
                    "Command cancelled. If you want a different approach, try being more specific.\n"
                    "Example: wtf use grep instead of ripgrep to search for 'foo'"
                )
            elif response == "yes_always":
                add_to_allowlist(allowlist_pattern)
    
    # Execute the command
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr

        return {
            "output": output or "(no output)",
            "exit_code": result.returncode,
            "should_print": True  # User should see this
        }
    except subprocess.TimeoutExpired:
        return {
            "output": "Command timed out after 30 seconds",
            "exit_code": 124,
            "should_print": True
        }
    except Exception as e:
        return {
            "output": f"Error executing command: {e}",
            "exit_code": 1,
            "should_print": True
        }


def read_file(file_path: str) -> Dict[str, Any]:
    """
    Read the contents of a file.

    Internal tool - output not printed to user by default.
    Some sensitive files (*.env, *secret*, etc.) may require user permission.

    Args:
        file_path: Path to the file to read

    Returns:
        Dict with:
        - content: File contents
        - error: Error message if failed
        - should_print: False (internal tool)
        - requires_permission: True if file needs permission (will prompt user)
    """
    try:
        path = Path(file_path).expanduser()

        if not path.exists():
            return {
                "content": None,
                "error": f"File not found: {file_path}",
                "should_print": False
            }

        if not path.is_file():
            return {
                "content": None,
                "error": f"Not a file: {file_path}",
                "should_print": False
            }

        # Check file permissions
        permission = check_file_permission(file_path)

        if permission == "block":
            return {
                "content": None,
                "error": f"Access denied: This file type is blocked for security reasons: {file_path}",
                "should_print": False
            }

        if permission == "ask":
            return {
                "content": None,
                "error": None,
                "requires_permission": True,
                "should_print": False,
                "message": f"This file may contain sensitive data: {file_path}"
            }

        with open(path, 'r') as f:
            content = f.read()

        return {
            "content": content,
            "error": None,
            "should_print": False
        }
    except Exception as e:
        return {
            "content": None,
            "error": f"Error reading file: {e}",
            "should_print": False
        }


def grep(pattern: str, path: str = ".", file_pattern: str = "*") -> Dict[str, Any]:
    """
    Search for a pattern in files.

    Internal tool - output not printed to user by default.

    Args:
        pattern: Regex pattern to search for
        path: Directory to search in (default: current directory)
        file_pattern: Glob pattern for files to search (default: all files)

    Returns:
        Dict with:
        - matches: List of matching lines with file paths
        - count: Number of matches
        - should_print: False (internal tool)
    """
    try:
        # Use grep command for simplicity
        result = subprocess.run(
            f"grep -r '{pattern}' {path}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )

        matches = result.stdout.strip().split('\n') if result.stdout else []

        return {
            "matches": matches,
            "count": len(matches),
            "should_print": False
        }
    except Exception as e:
        return {
            "matches": [],
            "count": 0,
            "error": str(e),
            "should_print": False
        }


def glob_files(pattern: str, path: str = ".") -> Dict[str, Any]:
    """
    Find files matching a glob pattern.

    Internal tool - output not printed to user by default.

    Args:
        pattern: Glob pattern (e.g., "*.py", "**/*.js")
        path: Directory to search in (default: current directory)

    Returns:
        Dict with:
        - files: List of matching file paths
        - count: Number of matches
        - should_print: False (internal tool)
    """
    try:
        base_path = Path(path).expanduser()

        if '**' in pattern:
            # Recursive glob
            files = list(base_path.rglob(pattern.replace('**/', '')))
        else:
            # Non-recursive glob
            files = list(base_path.glob(pattern))

        file_paths = [str(f) for f in files if f.is_file()]

        return {
            "files": file_paths,
            "count": len(file_paths),
            "should_print": False
        }
    except Exception as e:
        return {
            "files": [],
            "count": 0,
            "error": str(e),
            "should_print": False
        }


def lookup_history(limit: int = 10) -> Dict[str, Any]:
    """
    Look up recent conversation history.

    Internal tool - used by agent to see past interactions, not printed to user.

    Args:
        limit: Number of recent conversations to retrieve (default: 10)

    Returns:
        Dict with:
        - conversations: List of recent conversations
        - count: Number of conversations
        - should_print: False (internal tool)
    """
    try:
        conversations = get_recent_conversations(limit)

        return {
            "conversations": conversations,
            "count": len(conversations),
            "should_print": False
        }
    except Exception as e:
        return {
            "conversations": [],
            "count": 0,
            "error": str(e),
            "should_print": False
        }


def get_config(key: str = None) -> Dict[str, Any]:
    """
    Get configuration value(s).

    Internal tool - not printed to user.

    Args:
        key: Specific config key to get (optional, returns all if not provided)

    Returns:
        Dict with:
        - value: Config value or full config dict
        - should_print: False (internal tool)
    """
    try:
        config = load_config()

        if key:
            # Get specific key
            value = config.get(key)
        else:
            # Return full config
            value = config

        return {
            "value": value,
            "should_print": False
        }
    except Exception as e:
        return {
            "value": None,
            "error": str(e),
            "should_print": False
        }


def update_config(key: str, value: Any) -> Dict[str, Any]:
    """
    Update a configuration value.

    Internal tool - not printed to user.

    Args:
        key: Config key to update
        value: New value

    Returns:
        Dict with:
        - success: Whether update succeeded
        - should_print: False (internal tool)
    """
    try:
        config = load_config()

        # Update the key
        keys = key.split('.')
        current = config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value

        # Save config
        save_config(config)

        return {
            "success": True,
            "should_print": False
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "should_print": False
        }


def wtf_config(action: str, key: Optional[str] = None, value: Optional[str] = None) -> Dict[str, Any]:
    """
    Manage wtf configuration - API keys, settings, preferences.

    This is the primary tool for handling wtf-specific configuration.
    Use this when user says "here is my X key" or "save my Y setting".

    Args:
        action: Action to perform - "set_api_key", "get_api_key", "set_setting", "get_setting"
        key: Key name (e.g., "brave_search", "anthropic", "openai")
        value: Value to set (for set actions)

    Returns:
        Dict with:
        - success: Whether action succeeded
        - value: Retrieved value (for get actions)
        - message: User-friendly message
        - should_print: False (internal tool)
    """
    try:
        config = load_config()

        if action == "set_api_key":
            if not key or not value:
                return {
                    "success": False,
                    "error": "Both key and value required for set_api_key",
                    "should_print": False
                }

            # Store API keys in config under api_keys section
            if "api_keys" not in config:
                config["api_keys"] = {}

            config["api_keys"][key] = value
            save_config(config)

            return {
                "success": True,
                "message": f"Saved {key} API key to config",
                "should_print": False
            }

        elif action == "get_api_key":
            if not key:
                return {
                    "success": False,
                    "error": "Key required for get_api_key",
                    "should_print": False
                }

            api_keys = config.get("api_keys", {})
            value = api_keys.get(key)

            return {
                "success": True,
                "value": value,
                "message": f"Retrieved {key} API key" if value else f"No {key} API key stored",
                "should_print": False
            }

        elif action == "set_setting":
            if not key or value is None:
                return {
                    "success": False,
                    "error": "Both key and value required for set_setting",
                    "should_print": False
                }

            # Use update_config for general settings
            return update_config(key, value)

        elif action == "get_setting":
            if not key:
                return {
                    "success": False,
                    "error": "Key required for get_setting",
                    "should_print": False
                }

            # Navigate config dict with dot notation
            keys = key.split('.')
            current = config
            for k in keys:
                if k not in current:
                    return {
                        "success": False,
                        "value": None,
                        "message": f"Setting {key} not found",
                        "should_print": False
                    }
                current = current[k]

            return {
                "success": True,
                "value": current,
                "message": f"Retrieved {key} setting",
                "should_print": False
            }

        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "should_print": False
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "should_print": False
        }


def save_user_memory(key: str, value: str) -> Dict[str, Any]:
    """
    Save a single user preference or fact to memory.

    IMPORTANT: This tool saves ONE memory at a time. If the user provides multiple
    facts/preferences, call this tool multiple times (once per fact).

    Use this when user says "remember that..." or provides preferences.
    Examples:
    - "remember I live in San Francisco" -> key="location", value="San Francisco"
    - "I prefer emacs" -> key="editor", value="emacs"
    - "I use pytest for testing" -> key="test_framework", value="pytest"

    Args:
        key: Memory key (e.g., "location", "editor", "package_manager")
        value: Memory value (e.g., "San Francisco", "emacs", "npm")

    Returns:
        Dict with:
        - success: Whether save succeeded
        - message: Confirmation message
        - should_print: False (internal tool)
    """
    try:
        from wtf.conversation.memory import save_memory

        if not key or not value:
            return {
                "success": False,
                "error": "Both key and value required",
                "should_print": False
            }

        save_memory(key, value)

        return {
            "success": True,
            "message": f"Saved memory: {key} = {value}",
            "should_print": False
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "should_print": False
        }


def get_user_memories() -> Dict[str, Any]:
    """
    Get all saved user memories/preferences.

    Use when user asks "what do you remember?" or "show my preferences".

    Returns:
        Dict with:
        - memories: Dict of all memories {key: {value, timestamp, confidence}}
        - count: Number of memories
        - should_print: False (internal tool)
    """
    try:
        from wtf.conversation.memory import load_memories

        memories = load_memories()

        return {
            "success": True,
            "memories": memories,
            "count": len(memories),
            "should_print": False
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "should_print": False
        }


def delete_user_memory(key: str) -> Dict[str, Any]:
    """
    Delete a specific user memory by key.

    Use when user says "forget about X" or "delete my Y preference".

    Args:
        key: Memory key to delete (e.g., "editor", "location")

    Returns:
        Dict with:
        - success: Whether deletion succeeded
        - message: Confirmation message
        - should_print: False (internal tool)
    """
    try:
        from wtf.conversation.memory import delete_memory, load_memories

        memories = load_memories()

        if key not in memories:
            return {
                "success": False,
                "error": f"Memory '{key}' not found",
                "available_keys": list(memories.keys()),
                "should_print": False
            }

        delete_memory(key)

        return {
            "success": True,
            "message": f"Deleted memory: {key}",
            "should_print": False
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "should_print": False
        }


def clear_user_memories() -> Dict[str, Any]:
    """
    Clear ALL user memories.

    Use when user says "forget everything" or "clear all my memories".

    Returns:
        Dict with:
        - success: Whether clearing succeeded
        - message: Confirmation message
        - should_print: False (internal tool)
    """
    try:
        from wtf.conversation.memory import clear_memories

        clear_memories()

        return {
            "success": True,
            "message": "Cleared all memories",
            "should_print": False
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "should_print": False
        }


def check_command_exists(command: str) -> Dict[str, Any]:
    """
    Check if a command/tool is installed on the system.

    Internal tool - safer than running shell commands to check.

    Args:
        command: Name of the command to check (e.g., "git", "npm", "docker")

    Returns:
        Dict with:
        - exists: Whether command exists
        - path: Path to command if found
        - should_print: False (internal tool)
    """
    try:
        cmd_path = shutil.which(command)

        return {
            "exists": cmd_path is not None,
            "path": cmd_path,
            "should_print": False
        }
    except Exception as e:
        return {
            "exists": False,
            "path": None,
            "error": str(e),
            "should_print": False
        }


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get information about a file without reading its contents.

    Internal tool - provides metadata like size, type, permissions.

    Args:
        file_path: Path to the file

    Returns:
        Dict with:
        - exists: Whether file exists
        - type: "file", "directory", "symlink", etc.
        - size: Size in bytes
        - permissions: Permission string (e.g., "rw-r--r--")
        - modified: Last modified timestamp
        - should_print: False (internal tool)
    """
    try:
        path = Path(file_path).expanduser()

        if not path.exists():
            return {
                "exists": False,
                "error": f"File not found: {file_path}",
                "should_print": False
            }

        # Get file stats
        file_stat = path.stat()

        # Determine type
        if path.is_file():
            file_type = "file"
        elif path.is_dir():
            file_type = "directory"
        elif path.is_symlink():
            file_type = "symlink"
        else:
            file_type = "other"

        # Get permission string
        mode = file_stat.st_mode
        perms = stat.filemode(mode)

        return {
            "exists": True,
            "type": file_type,
            "size": file_stat.st_size,
            "permissions": perms,
            "modified": file_stat.st_mtime,
            "should_print": False
        }
    except Exception as e:
        return {
            "exists": False,
            "error": f"Error getting file info: {e}",
            "should_print": False
        }


def list_directory(path: str = ".", pattern: Optional[str] = None) -> Dict[str, Any]:
    """
    List files and directories with their metadata.

    Internal tool - more informative than glob_files.

    Args:
        path: Directory to list (default: current directory)
        pattern: Optional glob pattern to filter (e.g., "*.py")

    Returns:
        Dict with:
        - entries: List of dicts with name, type, size
        - count: Number of entries
        - should_print: False (internal tool)
    """
    try:
        dir_path = Path(path).expanduser()

        if not dir_path.exists():
            return {
                "entries": [],
                "count": 0,
                "error": f"Directory not found: {path}",
                "should_print": False
            }

        if not dir_path.is_dir():
            return {
                "entries": [],
                "count": 0,
                "error": f"Not a directory: {path}",
                "should_print": False
            }

        # Get entries
        if pattern:
            entries_iter = dir_path.glob(pattern)
        else:
            entries_iter = dir_path.iterdir()

        entries = []
        for entry in sorted(entries_iter):
            try:
                entry_stat = entry.stat()
                entries.append({
                    "name": entry.name,
                    "path": str(entry),
                    "type": "file" if entry.is_file() else "directory" if entry.is_dir() else "other",
                    "size": entry_stat.st_size if entry.is_file() else None
                })
            except Exception:
                # Skip entries we can't stat
                continue

        return {
            "entries": entries,
            "count": len(entries),
            "should_print": False
        }
    except Exception as e:
        return {
            "entries": [],
            "count": 0,
            "error": str(e),
            "should_print": False
        }


def check_package_installed(package: str, manager: str = "npm") -> Dict[str, Any]:
    """
    Check if a package is installed.

    Internal tool - checks npm/pip/cargo packages.

    Args:
        package: Package name (e.g., "express", "django")
        manager: Package manager ("npm", "pip", "cargo", "gem")

    Returns:
        Dict with:
        - installed: Whether package is installed
        - version: Version string if found
        - should_print: False (internal tool)
    """
    try:
        commands = {
            "npm": f"npm list {package} --depth=0",
            "pip": f"pip show {package}",
            "cargo": f"cargo tree -p {package} --depth=0",
            "gem": f"gem list -i {package}"
        }

        if manager not in commands:
            return {
                "installed": False,
                "error": f"Unknown package manager: {manager}",
                "should_print": False
            }

        result = subprocess.run(
            commands[manager],
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )

        # Parse output based on manager
        if manager == "npm":
            installed = result.returncode == 0 and package in result.stdout
            # Try to extract version from npm output
            version = None
            if installed:
                for line in result.stdout.split('\n'):
                    if package in line and '@' in line:
                        version = line.split('@')[-1].strip()
                        break

        elif manager == "pip":
            installed = result.returncode == 0
            version = None
            if installed:
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(':', 1)[1].strip()
                        break

        elif manager == "cargo":
            installed = result.returncode == 0 and package in result.stdout
            version = None
            if installed:
                for line in result.stdout.split('\n'):
                    if package in line and 'v' in line:
                        parts = line.split('v')
                        if len(parts) > 1:
                            version = parts[1].split()[0]
                            break

        elif manager == "gem":
            installed = result.stdout.strip() == "true"
            version = None

        return {
            "installed": installed,
            "version": version,
            "should_print": False
        }
    except Exception as e:
        return {
            "installed": False,
            "error": str(e),
            "should_print": False
        }


def write_file(file_path: str, content: str) -> Dict[str, Any]:
    """
    Write content to a file, creating it if it doesn't exist.

    Use this to create new files or completely replace file contents.
    For partial edits, use edit_file instead.

    Args:
        file_path: Path to the file to write
        content: Content to write to the file

    Returns:
        Dict with:
        - success: Whether write succeeded
        - path: Absolute path to the file
        - action: "created" or "overwritten"
        - should_print: True (user should see this)
    """
    try:
        path = Path(file_path).expanduser()
        
        # Make path absolute
        if not path.is_absolute():
            path = (Path.cwd() / path).resolve()
        
        # Check if file exists (for action message)
        existed = path.exists()
        
        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        path.write_text(content, encoding='utf-8')
        
        return {
            "success": True,
            "path": str(path),
            "action": "overwritten" if existed else "created",
            "should_print": True,
            "message": f"{'Overwrote' if existed else 'Created'} {path}"
        }
    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied: {file_path}",
            "should_print": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error writing file: {e}",
            "should_print": True
        }


def edit_file(file_path: str, old_str: str, new_str: str) -> Dict[str, Any]:
    """
    Edit a file by replacing text. For creating new files, use write_file.

    Replaces the FIRST occurrence of old_str with new_str.
    The old_str must match exactly (including whitespace/indentation).

    Args:
        file_path: Path to the file to edit
        old_str: The exact text to find and replace
        new_str: The text to replace it with

    Returns:
        Dict with:
        - success: Whether edit succeeded
        - path: Absolute path to the file
        - action: "edited" or error description
        - should_print: True (user should see this)
    """
    try:
        path = Path(file_path).expanduser()
        
        # Make path absolute
        if not path.is_absolute():
            path = (Path.cwd() / path).resolve()
        
        if not path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}. Use write_file to create new files.",
                "should_print": True
            }
        
        if not path.is_file():
            return {
                "success": False,
                "error": f"Not a file: {file_path}",
                "should_print": True
            }
        
        # Read current content
        original = path.read_text(encoding='utf-8')
        
        # Check if old_str exists
        if old_str not in original:
            # Provide helpful error with preview
            preview = original[:200] + "..." if len(original) > 200 else original
            return {
                "success": False,
                "error": f"Text not found in {file_path}. The old_str must match exactly.",
                "file_preview": preview,
                "should_print": True
            }
        
        # Replace first occurrence
        edited = original.replace(old_str, new_str, 1)
        
        # Write back
        path.write_text(edited, encoding='utf-8')
        
        return {
            "success": True,
            "path": str(path),
            "action": "edited",
            "should_print": True,
            "message": f"Edited {path}"
        }
    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied: {file_path}",
            "should_print": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error editing file: {e}",
            "should_print": True
        }


def get_git_info() -> Dict[str, Any]:
    """
    Get comprehensive git repository information.

    Internal tool - provides structured git status data.

    Returns:
        Dict with:
        - is_repo: Whether current directory is in a git repo
        - branch: Current branch name
        - status: Status summary (clean, modified, etc.)
        - ahead_behind: Tracking branch status
        - has_changes: Whether there are uncommitted changes
        - should_print: False (internal tool)
    """
    try:
        # Check if we're in a git repo
        result = subprocess.run(
            "git rev-parse --is-inside-work-tree",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return {
                "is_repo": False,
                "should_print": False
            }

        # Get branch name
        result = subprocess.run(
            "git branch --show-current",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        branch = result.stdout.strip() or "HEAD"

        # Get status
        result = subprocess.run(
            "git status --porcelain",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        has_changes = bool(result.stdout.strip())

        # Get ahead/behind info
        result = subprocess.run(
            "git status --porcelain --branch",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        ahead_behind = None
        for line in result.stdout.split('\n'):
            if line.startswith('##'):
                if '[ahead' in line or '[behind' in line:
                    ahead_behind = line.split('[')[1].split(']')[0] if '[' in line else None
                break

        return {
            "is_repo": True,
            "branch": branch,
            "has_changes": has_changes,
            "ahead_behind": ahead_behind,
            "status": "modified" if has_changes else "clean",
            "should_print": False
        }
    except Exception as e:
        return {
            "is_repo": False,
            "error": str(e),
            "should_print": False
        }


def brave_search(query: str) -> Dict[str, Any]:
    """
    Search the web using Brave Search API.

    Requires BRAVE_SEARCH_API_KEY to be configured.
    Get free API key at: https://brave.com/search/api/

    Args:
        query: Search query

    Returns:
        Dict with:
        - results: Search results with titles, URLs, descriptions
        - should_print: False (internal tool)
    """
    try:
        import urllib.request
        import urllib.parse
        import json

        # Check for API key in config
        config = load_config()
        api_key = config.get("api_keys", {}).get("brave_search")

        if not api_key:
            # Also check environment variable
            api_key = os.environ.get("BRAVE_SEARCH_API_KEY")

        if not api_key:
            return {
                "results": None,
                "error": (
                    "Brave Search API key not configured.\n\n"
                    "For FREE search with no API key, install duckduckgo-search:\n"
                    "  pip install duckduckgo-search\n\n"
                    "Or get a Brave API key (2,000 free/month):\n"
                    "  https://brave.com/search/api\n"
                    "  Then: wtf here is my brave search api key YOUR_KEY"
                ),
                "should_print": False
            }

        # Call Brave Search API
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.search.brave.com/res/v1/web/search?q={encoded_query}&count=5"

        req = urllib.request.Request(url)
        req.add_header("X-Subscription-Token", api_key)
        req.add_header("Accept", "application/json")

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

        # Extract results
        results = []
        for item in data.get("web", {}).get("results", [])[:5]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", "")
            })

        if not results:
            return {
                "results": "No results found",
                "should_print": False
            }

        # Format results as text
        formatted = "\n\n".join([
            f"{r['title']}\n{r['url']}\n{r['description']}"
            for r in results
        ])

        return {
            "results": formatted,
            "should_print": False
        }

    except urllib.error.HTTPError as e:
        if e.code == 401:
            return {
                "results": None,
                "error": "Brave Search API key is invalid. Check your key at https://brave.com/search/api/",
                "should_print": False
            }
        else:
            return {
                "results": None,
                "error": f"Brave Search API error: {e.code} {e.reason}",
                "should_print": False
            }
    except Exception as e:
        return {
            "results": None,
            "error": f"Brave search failed: {str(e)}",
            "should_print": False
        }


def serper_search(query: str) -> Dict[str, Any]:
    """
    Search the web using Serper.dev API (Google results).

    Requires SERPER_API_KEY to be configured.
    Get free API key at: https://serper.dev (2,500 searches/month free)

    Args:
        query: Search query

    Returns:
        Dict with:
        - results: Search results with titles, URLs, descriptions
        - should_print: False (internal tool)
    """
    try:
        import urllib.request
        import urllib.parse
        import json

        # Check for API key in config
        config = load_config()
        api_key = config.get("api_keys", {}).get("serper")

        if not api_key:
            # Also check environment variable
            api_key = os.environ.get("SERPER_API_KEY")

        if not api_key:
            return {
                "results": None,
                "error": (
                    "Serper API key not configured.\n\n"
                    "For FREE search with no API key, install duckduckgo-search:\n"
                    "  pip install duckduckgo-search\n\n"
                    "Or get a Serper API key (2,500 free/month):\n"
                    "  https://serper.dev\n"
                    "  Then: wtf here is my serper api key YOUR_KEY"
                ),
                "should_print": False
            }

        # Call Serper API
        url = "https://google.serper.dev/search"
        data = json.dumps({"q": query}).encode('utf-8')

        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header("X-API-KEY", api_key)
        req.add_header("Content-Type", "application/json")

        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())

        # Extract results
        results = []
        for item in result.get("organic", [])[:5]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "description": item.get("snippet", "")
            })

        if not results:
            return {
                "results": "No results found",
                "should_print": False
            }

        # Format results as text
        formatted = "\n\n".join([
            f"{r['title']}\n{r['url']}\n{r['description']}"
            for r in results
        ])

        return {
            "results": formatted,
            "should_print": False
        }

    except urllib.error.HTTPError as e:
        if e.code == 401 or e.code == 403:
            return {
                "results": None,
                "error": "Serper API key is invalid. Check your key at https://serper.dev",
                "should_print": False
            }
        else:
            return {
                "results": None,
                "error": f"Serper API error: {e.code} {e.reason}",
                "should_print": False
            }
    except Exception as e:
        return {
            "results": None,
            "error": f"Serper search failed: {str(e)}",
            "should_print": False
        }


def bing_search(query: str) -> Dict[str, Any]:
    """
    Search the web using Bing Search API.

    Requires BING_SEARCH_API_KEY to be configured.
    Get API key from Azure Portal: https://portal.azure.com

    Args:
        query: Search query

    Returns:
        Dict with:
        - results: Search results with titles, URLs, descriptions
        - should_print: False (internal tool)
    """
    try:
        import urllib.request
        import urllib.parse
        import json

        # Check for API key in config
        config = load_config()
        api_key = config.get("api_keys", {}).get("bing_search")

        if not api_key:
            # Also check environment variable
            api_key = os.environ.get("BING_SEARCH_API_KEY")

        if not api_key:
            return {
                "results": None,
                "error": (
                    "Bing Search API key not configured.\n\n"
                    "For FREE search with no API key, install duckduckgo-search:\n"
                    "  pip install duckduckgo-search\n\n"
                    "Or get a Bing API key (1,000 free/month) from Azure Portal:\n"
                    "  https://portal.azure.com\n"
                    "  Then: wtf here is my bing search api key YOUR_KEY"
                ),
                "should_print": False
            }

        # Call Bing Search API
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.bing.microsoft.com/v7.0/search?q={encoded_query}&count=5"

        req = urllib.request.Request(url)
        req.add_header("Ocp-Apim-Subscription-Key", api_key)

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

        # Extract results
        results = []
        for item in data.get("webPages", {}).get("value", [])[:5]:
            results.append({
                "title": item.get("name", ""),
                "url": item.get("url", ""),
                "description": item.get("snippet", "")
            })

        if not results:
            return {
                "results": "No results found",
                "should_print": False
            }

        # Format results as text
        formatted = "\n\n".join([
            f"{r['title']}\n{r['url']}\n{r['description']}"
            for r in results
        ])

        return {
            "results": formatted,
            "should_print": False
        }

    except urllib.error.HTTPError as e:
        if e.code == 401 or e.code == 403:
            return {
                "results": None,
                "error": "Bing Search API key is invalid. Check your key in Azure Portal",
                "should_print": False
            }
        else:
            return {
                "results": None,
                "error": f"Bing Search API error: {e.code} {e.reason}",
                "should_print": False
            }
    except Exception as e:
        return {
            "results": None,
            "error": f"Bing search failed: {str(e)}",
            "should_print": False
        }


def web_instant_answers(query: str) -> Dict[str, Any]:
    """
    Get instant answers for encyclopedic queries using DuckDuckGo.

    Internal tool - only works for well-known encyclopedic facts.

    Args:
        query: Search query

    Returns:
        Dict with:
        - results: Instant answer results
        - should_print: False (internal tool)
    """
    try:
        import urllib.parse
        import json
        import urllib.request

        # Use DuckDuckGo instant answer API (no key required)
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1"

        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())

        # Extract relevant results
        results = []

        # Abstract (direct answer)
        if data.get('Abstract'):
            results.append(f"Answer: {data['Abstract']}")

        # Related topics
        for topic in data.get('RelatedTopics', [])[:3]:
            if isinstance(topic, dict) and topic.get('Text'):
                results.append(topic['Text'])

        result_text = '\n'.join(results) if results else "No results found. Try being more specific."

        return {
            "results": result_text,
            "should_print": False
        }
    except Exception as e:
        return {
            "results": f"Web search failed: {e}",
            "error": str(e),
            "should_print": False
        }


def duckduckgo_search(query: str) -> Dict[str, Any]:
    """
    Search the web using DuckDuckGo (via ddgs library).

    FREE and unlimited - no API key required!
    Requires: pip install ddgs

    Args:
        query: Search query

    Returns:
        Dict with:
        - results: Search results with titles, URLs, descriptions
        - should_print: False (internal tool)
    """
    # Try new ddgs package first, fall back to old duckduckgo_search
    DDGS = None
    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            pass
    
    if DDGS is None:
        return {
            "results": None,
            "error": (
                "DuckDuckGo search not available. Install it with:\n"
                "  pip install ddgs\n\n"
                "This provides FREE unlimited web search with no API key needed!\n\n"
                "Alternative search options:\n"
                "  • Tavily: 1,000 free searches/month - https://tavily.com\n"
                "  • Serper: 2,500 free searches/month - https://serper.dev\n"
                "  • Brave: 2,000 free searches/month - https://brave.com/search/api"
            ),
            "should_print": False
        }

    try:
        # Perform search - new ddgs package doesn't use context manager
        ddgs = DDGS()
        results_list = list(ddgs.text(query, max_results=5))

        if not results_list:
            return {
                "results": "No results found",
                "should_print": False
            }

        # Format results
        results = []
        for item in results_list:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("href", ""),
                "description": item.get("body", "")
            })

        formatted = "\n\n".join([
            f"{r['title']}\n{r['url']}\n{r['description']}"
            for r in results
        ])

        return {
            "results": formatted,
            "should_print": False
        }

    except Exception as e:
        error_str = str(e)
        # Check for rate limiting or blocking
        if "ratelimit" in error_str.lower() or "blocked" in error_str.lower():
            return {
                "results": None,
                "error": (
                    f"DuckDuckGo rate limited: {e}\n\n"
                    "Try again in a few minutes, or use an API-based search:\n"
                    "  • Tavily: 1,000 free/month - https://tavily.com\n"
                    "  • Serper: 2,500 free/month - https://serper.dev"
                ),
                "should_print": False
            }
        return {
            "results": None,
            "error": f"DuckDuckGo search failed: {e}",
            "should_print": False
        }


def tavily_search(query: str) -> Dict[str, Any]:
    """
    Search the web using Tavily API.

    Optimized for AI agents - returns clean, relevant results.
    1,000 free searches/month at https://tavily.com

    Args:
        query: Search query

    Returns:
        Dict with:
        - results: Search results with titles, URLs, descriptions
        - should_print: False (internal tool)
    """
    try:
        import urllib.request
        import urllib.parse
        import json

        # Check for API key in config
        config = load_config()
        api_key = config.get("api_keys", {}).get("tavily")

        if not api_key:
            # Also check environment variable
            api_key = os.environ.get("TAVILY_API_KEY")

        if not api_key:
            return {
                "results": None,
                "error": (
                    "Tavily API key not configured.\n\n"
                    "Get a FREE API key (1,000 searches/month, no credit card):\n"
                    "  https://tavily.com\n\n"
                    "Then save it with:\n"
                    "  wtf here is my tavily api key YOUR_KEY\n\n"
                    "Or for FREE search with no API key, install duckduckgo-search:\n"
                    "  pip install duckduckgo-search"
                ),
                "should_print": False
            }

        # Call Tavily API
        url = "https://api.tavily.com/search"
        data = json.dumps({
            "api_key": api_key,
            "query": query,
            "max_results": 5,
            "include_answer": True
        }).encode('utf-8')

        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header("Content-Type", "application/json")

        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode())

        # Extract results
        results = []
        
        # Include the AI-generated answer if available
        if result.get("answer"):
            results.append(f"Summary: {result['answer']}\n")

        for item in result.get("results", [])[:5]:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("content", "")[:300]  # Truncate long content
            })

        if not results:
            return {
                "results": "No results found",
                "should_print": False
            }

        # Format results
        formatted_results = []
        for r in results:
            if isinstance(r, str):
                formatted_results.append(r)
            else:
                formatted_results.append(f"{r['title']}\n{r['url']}\n{r['description']}")

        return {
            "results": "\n\n".join(formatted_results),
            "should_print": False
        }

    except urllib.error.HTTPError as e:
        if e.code == 401 or e.code == 403:
            return {
                "results": None,
                "error": (
                    "Tavily API key is invalid.\n"
                    "Check your key at https://tavily.com"
                ),
                "should_print": False
            }
        else:
            return {
                "results": None,
                "error": f"Tavily API error: {e.code} {e.reason}",
                "should_print": False
            }
    except Exception as e:
        return {
            "results": None,
            "error": f"Tavily search failed: {str(e)}",
            "should_print": False
        }


# Tool registry for llm library
TOOLS = {
    "run_command": run_command,
    "read_file": read_file,
    "write_file": write_file,
    "edit_file": edit_file,
    "grep": grep,
    "glob_files": glob_files,
    "lookup_history": lookup_history,
    "get_config": get_config,
    "update_config": update_config,
    "wtf_config": wtf_config,
    "save_user_memory": save_user_memory,
    "get_user_memories": get_user_memories,
    "delete_user_memory": delete_user_memory,
    "clear_user_memories": clear_user_memories,
    "duckduckgo_search": duckduckgo_search,
    "tavily_search": tavily_search,
    "brave_search": brave_search,
    "serper_search": serper_search,
    "bing_search": bing_search,
    "web_instant_answers": web_instant_answers,
    "check_command_exists": check_command_exists,
    "get_file_info": get_file_info,
    "list_directory": list_directory,
    "check_package_installed": check_package_installed,
    "get_git_info": get_git_info,
}


def get_tool_definitions(
    env_context: Optional[Dict[str, Any]] = None,
    model_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get tool definitions in the format expected by LLM providers.

    Optionally filters tools based on environment context to avoid
    offering irrelevant tools (e.g., git tools when not in a repo).
    
    Also filters out custom search tools when using a model with
    native web search support (OpenAI search models, Anthropic Claude).

    Args:
        env_context: Optional environment info with keys like:
            - is_git_repo: bool
            - has_package_json: bool
            - has_requirements_txt: bool
        model_name: Optional model name to detect native search support

    Returns:
        List of tool definition dicts
    """
    # Detect if model has native search support
    has_native_search = False
    if model_name:
        _, has_native_search = detect_native_search_support(model_name)
    # Base tools always available
    base_tools = [
        {
            "name": "run_command",
            "description": "Execute a terminal command and see its output. Use this for commands the user wants to run (git, npm, etc.). The output will be shown to the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute"
                    }
                },
                "required": ["command"]
            }
        },
        {
            "name": "read_file",
            "description": "Read the contents of a file. Internal tool - output not shown to user unless you explicitly include it in your response.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["file_path"]
            }
        },
        {
            "name": "write_file",
            "description": "Create a new file or completely replace an existing file's contents. Use this for creating new files. For partial edits to existing files, use edit_file instead.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to create/write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["file_path", "content"]
            }
        },
        {
            "name": "edit_file",
            "description": "Edit an existing file by finding and replacing text. Replaces the FIRST occurrence of old_str with new_str. The old_str must match exactly including whitespace and indentation. For creating new files, use write_file instead.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to edit"
                    },
                    "old_str": {
                        "type": "string",
                        "description": "The exact text to find (must match exactly)"
                    },
                    "new_str": {
                        "type": "string",
                        "description": "The text to replace it with"
                    }
                },
                "required": ["file_path", "old_str", "new_str"]
            }
        },
        {
            "name": "grep",
            "description": "Search for a pattern in files. Internal tool - use this to find code or content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Regex pattern to search for"
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory to search in (default: current directory)"
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "Glob pattern for files to search (default: all files)"
                    }
                },
                "required": ["pattern"]
            }
        },
        {
            "name": "glob_files",
            "description": "Find files matching a glob pattern. Internal tool - use this to discover files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern (e.g., '*.py', '**/*.js')"
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory to search in (default: current directory)"
                    }
                },
                "required": ["pattern"]
            }
        },
        {
            "name": "lookup_history",
            "description": "Look up recent conversation history. Internal tool - use this to remember past interactions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of recent conversations to retrieve (default: 10)"
                    }
                },
                "required": []
            }
        },
        {
            "name": "get_config",
            "description": "Get configuration value(s). Internal tool.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Specific config key to get (optional)"
                    }
                },
                "required": []
            }
        },
        {
            "name": "update_config",
            "description": "Update a configuration value. Internal tool.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Config key to update (use dot notation for nested keys)"
                    },
                    "value": {
                        "type": "string",
                        "description": "New value"
                    }
                },
                "required": ["key", "value"]
            }
        },
        {
            "name": "wtf_config",
            "description": "Manage wtf configuration - save API keys, update settings. Use when user says 'here is my X key' or 'save my Y setting'. Actions: 'set_api_key' (save API key), 'get_api_key' (retrieve key), 'set_setting' (general config), 'get_setting' (read config).",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action: 'set_api_key', 'get_api_key', 'set_setting', 'get_setting'"
                    },
                    "key": {
                        "type": "string",
                        "description": "Key name (e.g., 'brave_search', 'anthropic', 'verbose')"
                    },
                    "value": {
                        "type": "string",
                        "description": "Value to set (for set actions)"
                    }
                },
                "required": ["action"]
            }
        },
        {
            "name": "save_user_memory",
            "description": "Save ONE user preference or fact to memory. CRITICAL: Call this tool multiple times if user provides multiple facts. Use when user says 'remember...' Examples: 'remember I live in SF' -> key='location' value='San Francisco', 'I prefer emacs' -> key='editor' value='emacs', 'I use pytest' -> key='test_framework' value='pytest'. Always call once per fact.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Memory key (e.g., 'location', 'editor', 'package_manager', 'test_framework')"
                    },
                    "value": {
                        "type": "string",
                        "description": "Memory value (e.g., 'San Francisco', 'emacs', 'npm', 'pytest')"
                    }
                },
                "required": ["key", "value"]
            }
        },
        {
            "name": "get_user_memories",
            "description": "Get all saved user memories/preferences. Use when user asks 'what do you remember about me?' or 'show my preferences'.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "delete_user_memory",
            "description": "Delete a specific user memory by key. Use when user says 'forget about X' or 'delete my Y preference'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Memory key to delete (e.g., 'editor', 'location')"
                    }
                },
                "required": ["key"]
            }
        },
        {
            "name": "clear_user_memories",
            "description": "Clear ALL user memories. Use when user says 'forget everything' or 'clear all my memories'. This is destructive and permanent.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "duckduckgo_search",
            "description": "Search the web using DuckDuckGo - FREE and UNLIMITED, no API key required! Works for ANY web search (weather, news, docs, current events, etc.). PREFERRED search tool - try this first. Requires: pip install duckduckgo-search",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Web search query"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "tavily_search",
            "description": "Search the web using Tavily API - optimized for AI agents, returns clean results with summaries. 1,000 free searches/month at https://tavily.com (no credit card required). Use if duckduckgo_search is unavailable.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Web search query"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "serper_search",
            "description": "Search the web using Serper.dev (Google search results) - works for ANY web search (weather, news, docs, current events, etc.). 2,500 free searches/month at https://serper.dev",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Web search query"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "bing_search",
            "description": "Search the web using Bing Search API - works for ANY web search (weather, news, docs, current events, etc.). Use if user has Bing Search API key from Azure. 1,000 free searches/month.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Web search query"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "brave_search",
            "description": "Search the web using Brave Search API - works for ANY web search (weather, news, docs, current events, etc.). Use if user has Brave Search API key. 2,000 free searches/month at https://brave.com/search/api/",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Web search query (works for anything)"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "web_instant_answers",
            "description": "Get instant answers for encyclopedic queries using DuckDuckGo Instant Answer API. LIMITATIONS: Only works for well-known encyclopedic facts (e.g., 'python programming language', 'what is rust'). Does NOT work for: weather, news, documentation URLs, local businesses, current events, or most real-world queries. Use brave_search instead for real web searches.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Encyclopedic query (e.g., 'python programming language', 'what is docker')"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "check_command_exists",
            "description": "Check if a command/tool is installed on the system. Use this before suggesting commands to verify they're available.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Name of the command to check (e.g., 'git', 'npm', 'docker')"
                    }
                },
                "required": ["command"]
            }
        },
        {
            "name": "get_file_info",
            "description": "Get file metadata (type, size, permissions) without reading contents. Use this to check file types or sizes before reading.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file"
                    }
                },
                "required": ["file_path"]
            }
        },
        {
            "name": "list_directory",
            "description": "List files and directories with metadata. More informative than glob_files - shows file types and sizes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory to list (default: current directory)"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Optional glob pattern to filter (e.g., '*.py')"
                    }
                },
                "required": []
            }
        },
        {
            "name": "check_package_installed",
            "description": "Check if a package is installed via npm/pip/cargo/gem. Returns version if found.",
            "parameters": {
                "type": "object",
                "properties": {
                    "package": {
                        "type": "string",
                        "description": "Package name (e.g., 'express', 'django')"
                    },
                    "manager": {
                        "type": "string",
                        "description": "Package manager: 'npm', 'pip', 'cargo', or 'gem' (default: npm)"
                    }
                },
                "required": ["package"]
            }
        },
        {
            "name": "get_git_info",
            "description": "Get comprehensive git repository information (branch, status, changes). Only use in git repositories.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    ]

    # Filter tools based on environment and native search support
    filtered_tools = []
    
    for tool in base_tools:
        tool_name = tool["name"]
        
        # Skip our custom search tools if model has native search
        if has_native_search and tool_name in CUSTOM_SEARCH_TOOLS:
            continue
        
        # Environment-based filtering
        if env_context:
            # Git tool only in git repos
            if tool_name == "get_git_info":
                if not env_context.get("is_git_repo"):
                    continue

            # Package manager tools only if relevant files exist
            if tool_name == "check_package_installed":
                has_package_file = (
                    env_context.get("has_package_json") or
                    env_context.get("has_requirements_txt") or
                    env_context.get("has_cargo_toml") or
                    env_context.get("has_gemfile")
                )
                if not has_package_file:
                    continue
        
        filtered_tools.append(tool)

    return filtered_tools
