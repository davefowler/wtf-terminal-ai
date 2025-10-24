"""Tools for the AI agent to use."""

import os
import subprocess
import shutil
import stat
from typing import Dict, Any, List, Optional
from pathlib import Path

from wtf.conversation.history import get_recent_conversations
from wtf.core.config import load_config, save_config, check_file_permission


def run_command(command: str) -> Dict[str, Any]:
    """
    Execute a terminal command and return its output.

    This tool PRINTS output to the user - it's for running actual commands
    that the user wants to see the results of.

    Args:
        command: The shell command to execute

    Returns:
        Dict with:
        - output: Command stdout/stderr
        - exit_code: Exit code
        - should_print: True (output should be shown to user)
    """
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


def web_search(query: str) -> Dict[str, Any]:
    """
    Search the web for current information.

    Internal tool - use this for weather, news, current events, etc.

    Args:
        query: Search query

    Returns:
        Dict with:
        - results: Search results
        - should_print: False (internal tool)
    """
    try:
        import urllib.parse
        import json
        import urllib.request

        query_lower = query.lower()

        # Quick lookup for common documentation queries
        doc_urls = {
            'django': 'https://docs.djangoproject.com',
            'react': 'https://react.dev',
            'python': 'https://docs.python.org',
            'javascript': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript',
            'typescript': 'https://www.typescriptlang.org/docs/',
            'vue': 'https://vuejs.org/guide/',
            'node': 'https://nodejs.org/docs/',
            'express': 'https://expressjs.com',
            'flask': 'https://flask.palletsprojects.com',
            'fastapi': 'https://fastapi.tiangolo.com',
            'nextjs': 'https://nextjs.org/docs',
            'svelte': 'https://svelte.dev/docs',
            'rust': 'https://doc.rust-lang.org',
            'go': 'https://go.dev/doc/',
            'docker': 'https://docs.docker.com',
            'kubernetes': 'https://kubernetes.io/docs/',
            'postgres': 'https://www.postgresql.org/docs/',
            'mysql': 'https://dev.mysql.com/doc/',
            'mongodb': 'https://docs.mongodb.com',
            'redis': 'https://redis.io/docs/',
        }

        # Check if query is asking for docs
        if 'docs' in query_lower or 'documentation' in query_lower:
            for framework, url in doc_urls.items():
                if framework in query_lower:
                    return {
                        "results": f"Documentation: {url}",
                        "should_print": False
                    }

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


# Tool registry for llm library
TOOLS = {
    "run_command": run_command,
    "read_file": read_file,
    "grep": grep,
    "glob_files": glob_files,
    "lookup_history": lookup_history,
    "get_config": get_config,
    "update_config": update_config,
    "web_search": web_search,
    "check_command_exists": check_command_exists,
    "get_file_info": get_file_info,
    "list_directory": list_directory,
    "check_package_installed": check_package_installed,
    "get_git_info": get_git_info,
}


def get_tool_definitions(env_context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Get tool definitions in the format expected by LLM providers.

    Optionally filters tools based on environment context to avoid
    offering irrelevant tools (e.g., git tools when not in a repo).

    Args:
        env_context: Optional environment info with keys like:
            - is_git_repo: bool
            - has_package_json: bool
            - has_requirements_txt: bool

    Returns:
        List of tool definition dicts
    """
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
            "name": "web_search",
            "description": "Search for documentation URLs and general knowledge. Has built-in lookups for 20+ frameworks (Django, React, Python, etc.). Also searches for encyclopedic facts. NOTE: Does NOT work for weather, news, local searches, or real-time data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'django docs', 'python programming language')"
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

    # Filter tools based on environment if context provided
    if env_context:
        filtered_tools = []

        for tool in base_tools:
            tool_name = tool["name"]

            # Git tool only in git repos
            if tool_name == "get_git_info":
                if env_context.get("is_git_repo"):
                    filtered_tools.append(tool)
                continue

            # Package manager tools only if relevant files exist
            if tool_name == "check_package_installed":
                has_package_file = (
                    env_context.get("has_package_json") or
                    env_context.get("has_requirements_txt") or
                    env_context.get("has_cargo_toml") or
                    env_context.get("has_gemfile")
                )
                if has_package_file:
                    filtered_tools.append(tool)
                continue

            # All other tools always included
            filtered_tools.append(tool)

        return filtered_tools

    # No filtering - return all tools
    return base_tools
