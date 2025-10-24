"""Tools for the AI agent to use."""

import os
import subprocess
from typing import Dict, Any, List
from pathlib import Path

from wtf.conversation.history import get_recent_conversations
from wtf.core.config import load_config, save_config


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

    Args:
        file_path: Path to the file to read

    Returns:
        Dict with:
        - content: File contents
        - error: Error message if failed
        - should_print: False (internal tool)
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
}


def get_tool_definitions() -> List[Dict[str, Any]]:
    """
    Get tool definitions in the format expected by LLM providers.

    Returns:
        List of tool definition dicts
    """
    return [
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
            "description": "Search the web for current information (weather, news, facts, current events). Use this when the user asks about real-time information you don't have.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'weather in San Francisco', 'Python 3.12 release date')"
                    }
                },
                "required": ["query"]
            }
        }
    ]
