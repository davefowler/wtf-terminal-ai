"""Shell detection and history gathering."""

import os
import subprocess
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple


class HistoryFailureReason(Enum):
    """Reasons why history gathering might fail."""
    FC_COMMAND_FAILED = "fc_failed"
    FILE_NOT_FOUND = "file_not_found"
    PERMISSION_DENIED = "permission_denied"
    HISTORY_DISABLED = "history_disabled"
    EMPTY_HISTORY = "empty_history"
    UNKNOWN = "unknown"


def detect_shell() -> str:
    """
    Detect the current shell type.

    Returns:
        Shell type: "zsh", "bash", "fish", or "unknown"
    """
    # Check SHELL environment variable
    shell_env = os.environ.get('SHELL', '')

    if 'zsh' in shell_env:
        return 'zsh'
    elif 'bash' in shell_env:
        return 'bash'
    elif 'fish' in shell_env:
        return 'fish'

    # Fallback: try to detect by running shell command
    try:
        for shell in ['zsh', 'bash', 'fish']:
            result = subprocess.run(
                ['which', shell],
                capture_output=True,
                timeout=1
            )
            if result.returncode == 0:
                return shell
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return 'unknown'


def get_history_file_path(shell_type: str) -> Optional[str]:
    """
    Get expected history file path for shell type.

    Args:
        shell_type: The shell type ("zsh", "bash", "fish")

    Returns:
        Path to history file, or None if unknown
    """
    home = os.path.expanduser('~')

    if shell_type == 'zsh':
        # Check common locations
        candidates = [
            os.environ.get('HISTFILE'),
            os.path.join(home, '.zsh_history'),
            os.path.join(home, '.zhistory'),
        ]
    elif shell_type == 'bash':
        candidates = [
            os.environ.get('HISTFILE'),
            os.path.join(home, '.bash_history'),
        ]
    elif shell_type == 'fish':
        candidates = [
            os.path.join(home, '.local', 'share', 'fish', 'fish_history'),
        ]
    else:
        return None

    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate

    # Return default even if doesn't exist
    if shell_type == 'zsh':
        return os.path.join(home, '.zsh_history')
    elif shell_type == 'bash':
        return os.path.join(home, '.bash_history')
    elif shell_type == 'fish':
        return os.path.join(home, '.local', 'share', 'fish', 'fish_history')

    return None


def parse_zsh_history_line(line: str) -> Optional[str]:
    """
    Parse a zsh history line.

    Zsh format: `: timestamp:duration;command`

    Args:
        line: Raw line from history file

    Returns:
        Command string, or None if invalid
    """
    line = line.strip()
    if not line:
        return None

    # Zsh extended history format
    if line.startswith(': '):
        # Format: : 1234567890:0;command
        parts = line.split(';', 1)
        if len(parts) == 2:
            return parts[1].strip()

    # Plain format
    return line


def parse_bash_history_line(line: str) -> Optional[str]:
    """
    Parse a bash history line.

    Bash format: Simple commands, one per line

    Args:
        line: Raw line from history file

    Returns:
        Command string, or None if invalid
    """
    line = line.strip()
    if not line:
        return None
    return line


def parse_history_lines(lines: List[str], shell_type: str) -> List[str]:
    """
    Parse history lines based on shell type.

    Args:
        lines: Raw lines from history file
        shell_type: The shell type

    Returns:
        List of parsed commands
    """
    commands = []

    if shell_type == 'zsh':
        for line in lines:
            cmd = parse_zsh_history_line(line)
            if cmd:
                commands.append(cmd)
    elif shell_type == 'bash':
        for line in lines:
            cmd = parse_bash_history_line(line)
            if cmd:
                commands.append(cmd)
    else:
        # Default: simple line parsing
        for line in lines:
            line = line.strip()
            if line:
                commands.append(line)

    return commands


def get_shell_history(count: int = 5) -> Tuple[Optional[List[str]], Optional[HistoryFailureReason]]:
    """
    Get recent shell history with detailed failure reason.

    Args:
        count: Number of recent commands to retrieve

    Returns:
        Tuple of (commands, failure_reason)
        - commands is a list of command strings if successful, None otherwise
        - failure_reason is None if successful, HistoryFailureReason otherwise
    """
    shell_type = detect_shell()

    if shell_type == 'unknown':
        return (None, HistoryFailureReason.UNKNOWN)

    # Try fc command first (most reliable)
    try:
        result = subprocess.run(
            [shell_type, '-i', '-c', f'fc -ln -{count}'],
            capture_output=True,
            text=True,
            timeout=2
        )

        if result.returncode == 0:
            commands = [cmd.strip() for cmd in result.stdout.strip().split('\n')]
            commands = [cmd for cmd in commands if cmd]

            if commands:
                return (commands, None)
            else:
                return (None, HistoryFailureReason.EMPTY_HISTORY)

    except (subprocess.TimeoutExpired, FileNotFoundError):
        # fc failed, fall through to file method
        pass

    # Fallback: Try reading history file
    history_file = get_history_file_path(shell_type)

    if not history_file:
        return (None, HistoryFailureReason.HISTORY_DISABLED)

    if not os.path.exists(history_file):
        return (None, HistoryFailureReason.FILE_NOT_FOUND)

    try:
        with open(history_file, 'r', errors='ignore') as f:
            lines = f.readlines()

        if not lines:
            return (None, HistoryFailureReason.EMPTY_HISTORY)

        # Parse based on shell type
        commands = parse_history_lines(lines, shell_type)

        if commands:
            return (commands[-count:], None)
        else:
            return (None, HistoryFailureReason.EMPTY_HISTORY)

    except PermissionError:
        return (None, HistoryFailureReason.PERMISSION_DENIED)
    except Exception:
        return (None, HistoryFailureReason.UNKNOWN)


def build_history_context(
    commands: Optional[List[str]],
    failure_reason: Optional[HistoryFailureReason],
    shell_type: str
) -> str:
    """
    Build context string for AI agent based on history results.

    Args:
        commands: List of commands if successful
        failure_reason: Reason for failure if unsuccessful
        shell_type: The shell type

    Returns:
        Context string to include in AI prompt
    """
    if commands:
        cmd_list = '\n'.join(f'  {i+1}. {cmd}' for i, cmd in enumerate(commands))
        return f"""SHELL HISTORY (last {len(commands)} commands):
{cmd_list}"""

    # Build specific failure context
    history_file = get_history_file_path(shell_type)

    if failure_reason == HistoryFailureReason.FILE_NOT_FOUND:
        return f"""SHELL HISTORY: Not available

Reason: History file doesn't exist yet
Expected location: {history_file}
Shell: {shell_type}

Instructions for user:
Tell the user their history file doesn't exist yet. They can run a few commands
first, or provide more context in their query.

Example response: "Your shell history is empty (file doesn't exist yet).
Run a few commands first, or tell me what you need help with."
"""

    elif failure_reason == HistoryFailureReason.PERMISSION_DENIED:
        return f"""SHELL HISTORY: Not available

Reason: Permission denied reading history file
File: {history_file}

Instructions for user:
Tell user to fix permissions:
  chmod 600 {history_file}

Or tell them to provide more context in their query since you can't see history.
"""

    elif failure_reason == HistoryFailureReason.HISTORY_DISABLED:
        if shell_type == 'zsh':
            return f"""SHELL HISTORY: Not available

Reason: History appears to be disabled
Shell: zsh

Instructions for user:
Tell them to enable history by adding to ~/.zshrc:
  export HISTFILE=~/.zsh_history
  export HISTSIZE=10000
  export SAVEHIST=10000
  setopt SHARE_HISTORY

Then reload: source ~/.zshrc

Or tell them to provide more context since you can't see history.
"""
        else:  # bash
            return f"""SHELL HISTORY: Not available

Reason: History appears to be disabled
Shell: bash

Instructions for user:
Tell them to enable history by adding to ~/.bashrc:
  export HISTFILE=~/.bash_history
  export HISTSIZE=10000
  export HISTFILESIZE=20000

Then reload: source ~/.bashrc

Or tell them to provide more context since you can't see history.
"""

    elif failure_reason == HistoryFailureReason.EMPTY_HISTORY:
        return f"""SHELL HISTORY: Not available

Reason: History file is empty (no commands recorded yet)
Shell: {shell_type}

Instructions for user:
Tell them their history is empty. They can run a few commands first, or provide
more context in their query.

Example: "Your shell history is empty. Run a few commands first, or tell me
specifically what you need help with."
"""

    else:  # UNKNOWN
        return f"""SHELL HISTORY: Not available

Reason: Unknown error reading history
Shell: {shell_type}

Instructions for user:
Tell them history couldn't be read. Ask them to provide more context in their query.
"""
