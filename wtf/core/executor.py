"""Command execution with timeout and output capture."""

import subprocess
import time
from typing import Tuple
from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live

console = Console()


def execute_command(cmd: str, timeout: int = 30, show_spinner: bool = True) -> Tuple[str, int]:
    """
    Execute a shell command with timeout.

    Args:
        cmd: Command string to execute
        timeout: Timeout in seconds (default: 30)
        show_spinner: Whether to show a spinner while running

    Returns:
        Tuple of (output, exit_code)
        - output: Combined stdout and stderr
        - exit_code: Command exit code, or -1 for timeout
    """
    try:
        if show_spinner and timeout > 1:
            # Show spinner for commands expected to take time
            with console.status("⚙️  Running command...", spinner="dots"):
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
        else:
            # No spinner for quick commands
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )

        # Combine stdout and stderr
        output = result.stdout
        if result.stderr:
            output += result.stderr

        return (output, result.returncode)

    except subprocess.TimeoutExpired:
        return (f"⏱️  Command timed out after {timeout}s", -1)
    except Exception as e:
        return (f"❌ Error executing command: {e}", -1)


def execute_command_interactive(cmd: str, timeout: int = 30) -> Tuple[str, int]:
    """
    Execute a command that requires interactive input.

    Args:
        cmd: Command string to execute
        timeout: Timeout in seconds

    Returns:
        Tuple of (output, exit_code)
    """
    try:
        # Run without capturing output to allow interaction
        result = subprocess.run(
            cmd,
            shell=True,
            timeout=timeout
        )

        return ("", result.returncode)

    except subprocess.TimeoutExpired:
        return (f"⏱️  Command timed out after {timeout}s", -1)
    except Exception as e:
        return (f"❌ Error executing command: {e}", -1)
