"""Permission system for command execution."""

import json
from typing import List, Dict, Any, Literal
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from wtf.core.config import get_allowlist_path

console = Console()

# Safe read-only commands that can auto-execute without permission
SAFE_READONLY_COMMANDS = {
    # Command existence checks
    "command -v",
    "which",
    "type",

    # File reading
    "cat",
    "head",
    "tail",
    "less",
    "more",
    "file",
    "stat",
    "wc",

    # Directory operations
    "ls",
    "pwd",
    "find",
    "tree",

    # Git operations (read-only)
    "git status",
    "git log",
    "git diff",
    "git branch",
    "git show",
    "git remote",
    "git config --get",

    # System information
    "uname",
    "whoami",
    "hostname",
    "date",
    "uptime",
    "env",
    "printenv",

    # Package managers (list/check only)
    "npm list",
    "npm ls",
    "pip list",
    "pip show",
    "gem list",
    "cargo search",
    "go list",

    # Process information
    "ps",
    "pgrep",

    # Network checks (safe, minimal)
    "ping -c",
    "host",
    "dig",
    "nslookup",

    # Text processing
    "grep",
    "awk",
    "sed -n",
    "sort",
    "uniq",
    "cut",

    # Archive inspection
    "tar -tf",
    "unzip -l",
    "gunzip -l",
}


def load_allowlist() -> List[str]:
    """
    Load allowed command patterns from allowlist.json.

    Returns:
        List of command patterns that are allowed
    """
    allowlist_path = get_allowlist_path()

    if not allowlist_path.exists():
        return []

    try:
        with open(allowlist_path, 'r') as f:
            data = json.load(f)
            return data.get('patterns', [])
    except Exception:
        return []


def load_denylist() -> List[str]:
    """
    Load denied command patterns from allowlist.json.

    Returns:
        List of command patterns that are denied
    """
    allowlist_path = get_allowlist_path()

    if not allowlist_path.exists():
        return []

    try:
        with open(allowlist_path, 'r') as f:
            data = json.load(f)
            return data.get('denylist', [])
    except Exception:
        return []


def is_command_allowed(cmd: str, allowlist: List[str]) -> bool:
    """
    Check if a command matches any pattern in the allowlist.

    Args:
        cmd: Command string to check
        allowlist: List of allowed patterns

    Returns:
        True if command matches an allowed pattern
    """
    cmd_lower = cmd.lower().strip()

    for pattern in allowlist:
        pattern_lower = pattern.lower().strip()
        if cmd_lower.startswith(pattern_lower):
            return True

    return False


def is_command_denied(cmd: str, denylist: List[str]) -> bool:
    """
    Check if a command matches any pattern in the denylist.

    Args:
        cmd: Command string to check
        denylist: List of denied patterns

    Returns:
        True if command matches a denied pattern
    """
    cmd_lower = cmd.lower().strip()

    for pattern in denylist:
        pattern_lower = pattern.lower().strip()
        if pattern_lower in cmd_lower:
            return True

    return False


def prompt_for_permission(
    cmd: str,
    explanation: str,
    allowlist_pattern: str = None
) -> Literal["yes", "yes_always", "no"]:
    """
    Prompt user for permission to run a command.

    Args:
        cmd: The command to run
        explanation: Why the command needs to run
        allowlist_pattern: Pattern to add to allowlist if user chooses "always"

    Returns:
        "yes" - run once
        "yes_always" - run and add to allowlist
        "no" - don't run
    """
    console.print()

    # Show explanation if provided
    if explanation:
        console.print(f"[dim]{explanation}[/dim]")
        console.print()

    # Show command in a box
    console.print(Panel(
        f"[bold cyan]$ {cmd}[/bold cyan]",
        border_style="cyan",
        padding=(0, 1)
    ))

    console.print()

    # Build prompt text
    if allowlist_pattern:
        prompt_text = "Run this command? [[cyan]Y[/cyan]]es / Yes and [[cyan]a[/cyan]]lways / [[cyan]n[/cyan]]o"
        choices = ["y", "Y", "yes", "Yes", "YES", "a", "A", "always", "Always", "ALWAYS", "n", "N", "no", "No", "NO"]
    else:
        prompt_text = "Run this command? [[cyan]Y[/cyan]]es / [[cyan]n[/cyan]]o"
        choices = ["y", "Y", "yes", "Yes", "YES", "n", "N", "no", "No", "NO"]

    response = Prompt.ask(
        prompt_text,
        choices=choices,
        default="y",
        show_choices=False
    ).lower()

    if response in ["y", "yes"]:
        return "yes"
    elif response in ["a", "always"]:
        return "yes_always"
    else:
        return "no"


def add_to_allowlist(pattern: str) -> None:
    """
    Add a pattern to the allowlist.

    Args:
        pattern: Command pattern to allow
    """
    allowlist_path = get_allowlist_path()

    # Load current allowlist
    try:
        with open(allowlist_path, 'r') as f:
            data = json.load(f)
    except Exception:
        data = {"patterns": [], "denylist": []}

    # Add pattern if not already present
    patterns = data.get('patterns', [])
    if pattern not in patterns:
        patterns.append(pattern)
        data['patterns'] = patterns

        # Save back
        with open(allowlist_path, 'w') as f:
            json.dump(data, f, indent=2)

        console.print(f"[green]✓[/green] Added [cyan]{pattern}[/cyan] to allowlist")


def is_command_chained(cmd: str) -> bool:
    """
    Check if command contains chaining operators.

    Args:
        cmd: Command string to check

    Returns:
        True if command is chained
    """
    dangerous_chains = ['&&', '||', ';', '|', '$(',  '`']

    for chain in dangerous_chains:
        if chain in cmd:
            return True

    return False


def has_output_redirection(cmd: str) -> bool:
    """
    Check if command has output redirection.

    Args:
        cmd: Command string to check

    Returns:
        True if command has redirection
    """
    return '>' in cmd or '>>' in cmd


def is_safe_readonly_command(cmd: str, config: Dict[str, Any] = None) -> bool:
    """
    Check if command is safe and read-only (auto-allowed).

    Args:
        cmd: Command string to check
        config: Configuration dictionary (to check if auto_allow_readonly is enabled)

    Returns:
        True if command is safe and read-only
    """
    # Check config if provided
    if config:
        auto_allow = config.get('behavior', {}).get('auto_allow_readonly', True)
        if not auto_allow:
            return False

    cmd_lower = cmd.lower().strip()

    # Check if it starts with any safe prefix
    for safe_prefix in SAFE_READONLY_COMMANDS:
        if cmd_lower.startswith(safe_prefix.lower()):
            # Additional safety checks
            if is_command_chained(cmd):
                return False
            if has_output_redirection(cmd):
                return False

            return True

    return False


def should_auto_execute(
    cmd: str,
    allowlist: List[str],
    denylist: List[str],
    config: Dict[str, Any] = None
) -> Literal["auto", "ask", "deny"]:
    """
    Determine if command should auto-execute, ask, or deny.

    Priority:
    1. Denylist (highest priority)
    2. Safe read-only commands
    3. User's allowlist
    4. Ask (default)

    Args:
        cmd: Command to check
        allowlist: User's allowlist patterns
        denylist: Denied patterns
        config: Configuration dictionary

    Returns:
        "auto" - execute without asking
        "ask" - prompt user for permission
        "deny" - refuse to execute
    """
    # 1. Check denylist first (highest priority)
    if is_command_denied(cmd, denylist):
        return "deny"

    # 2. Check for command chaining (not allowed for auto)
    if is_command_chained(cmd):
        return "ask"

    # 3. Check safe read-only commands
    if is_safe_readonly_command(cmd, config):
        return "auto"

    # 4. Check user's allowlist
    if is_command_allowed(cmd, allowlist):
        return "auto"

    # 5. Default: ask
    return "ask"
