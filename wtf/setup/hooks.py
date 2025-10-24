"""Shell hook setup for automatic wtf triggering."""

import os
from pathlib import Path
from typing import Optional, Tuple
from rich.console import Console
from rich.panel import Panel

console = Console()


def get_shell_config_file(shell_type: str) -> Optional[Path]:
    """
    Get the config file path for a given shell.

    Args:
        shell_type: Shell type (zsh, bash, fish)

    Returns:
        Path to shell config file or None if not found
    """
    home = Path.home()

    config_files = {
        'zsh': [
            home / '.zshrc',
            home / '.zsh_profile',
        ],
        'bash': [
            home / '.bashrc',
            home / '.bash_profile',
            home / '.profile',
        ],
        'fish': [
            home / '.config' / 'fish' / 'config.fish',
        ]
    }

    files = config_files.get(shell_type, [])

    # Return first existing file, or first in list as default
    for f in files:
        if f.exists():
            return f

    # Return first option as default if none exist
    return files[0] if files else None


def setup_error_hook(shell_type: str) -> Tuple[bool, str]:
    """
    Set up error hook to automatically trigger wtf on command failures.

    This adds a hook that runs after every command and checks if it failed.
    If it did, it offers to run wtf automatically.

    Args:
        shell_type: Shell type (zsh, bash, fish)

    Returns:
        Tuple of (success: bool, message: str)
    """
    config_file = get_shell_config_file(shell_type)

    if not config_file:
        return False, f"Could not find config file for {shell_type}"

    # Create parent directory if needed
    config_file.parent.mkdir(parents=True, exist_ok=True)

    # Check if hook already exists
    if config_file.exists():
        content = config_file.read_text()
        if 'wtf-error-hook' in content:
            return False, f"Error hook already exists in {config_file}"

    # Shell-specific hook implementations
    if shell_type == 'zsh':
        hook = """
# wtf error hook - automatically suggest wtf on command failures
# Added by: wtf --setup-error-hook
# Remove with: wtf --remove-hooks
# wtf-error-hook-start
function wtf_error_hook() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo ""
        echo "💥 Command failed with exit code $exit_code"
        echo "   Run 'wtf' to analyze what went wrong"
        echo ""
    fi
}

# Hook into precmd (runs before each prompt)
precmd_functions+=(wtf_error_hook)
# wtf-error-hook-end

"""
    elif shell_type == 'bash':
        hook = """
# wtf error hook - automatically suggest wtf on command failures
# Added by: wtf --setup-error-hook
# Remove with: wtf --remove-hooks
# wtf-error-hook-start
wtf_error_hook() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo ""
        echo "💥 Command failed with exit code $exit_code"
        echo "   Run 'wtf' to analyze what went wrong"
        echo ""
    fi
}

# Hook into PROMPT_COMMAND (runs before each prompt)
if [[ ! "$PROMPT_COMMAND" =~ "wtf_error_hook" ]]; then
    PROMPT_COMMAND="wtf_error_hook${PROMPT_COMMAND:+; $PROMPT_COMMAND}"
fi
# wtf-error-hook-end

"""
    elif shell_type == 'fish':
        hook = """
# wtf error hook - automatically suggest wtf on command failures
# Added by: wtf --setup-error-hook
# Remove with: wtf --remove-hooks
# wtf-error-hook-start
function wtf_error_hook --on-event fish_postexec
    set -l exit_code $status
    if test $exit_code -ne 0
        echo ""
        echo "💥 Command failed with exit code $exit_code"
        echo "   Run 'wtf' to analyze what went wrong"
        echo ""
    end
end
# wtf-error-hook-end

"""
    else:
        return False, f"Unsupported shell type: {shell_type}"

    # Append hook to config file
    try:
        with open(config_file, 'a') as f:
            f.write(hook)

        return True, f"Error hook added to {config_file}"
    except Exception as e:
        return False, f"Failed to write to {config_file}: {e}"


def setup_not_found_hook(shell_type: str) -> Tuple[bool, str]:
    """
    Set up command-not-found hook to automatically trigger wtf.

    This adds a hook that runs when a command is not found and suggests
    using wtf to figure out what you meant.

    Args:
        shell_type: Shell type (zsh, bash, fish)

    Returns:
        Tuple of (success: bool, message: str)
    """
    config_file = get_shell_config_file(shell_type)

    if not config_file:
        return False, f"Could not find config file for {shell_type}"

    # Create parent directory if needed
    config_file.parent.mkdir(parents=True, exist_ok=True)

    # Check if hook already exists
    if config_file.exists():
        content = config_file.read_text()
        if 'wtf-not-found-hook' in content:
            return False, f"Not-found hook already exists in {config_file}"

    # Shell-specific hook implementations
    if shell_type == 'zsh':
        hook = """
# wtf command-not-found hook - suggest wtf when command not found
# Added by: wtf --setup-not-found-hook
# Remove with: wtf --remove-hooks
# wtf-not-found-hook-start
command_not_found_handler() {
    local cmd=$1
    echo ""
    echo "❌ Command not found: $cmd"
    echo "   Try: wtf how do I $cmd"
    echo ""
    return 127
}
# wtf-not-found-hook-end

"""
    elif shell_type == 'bash':
        hook = """
# wtf command-not-found hook - suggest wtf when command not found
# Added by: wtf --setup-not-found-hook
# Remove with: wtf --remove-hooks
# wtf-not-found-hook-start
command_not_found_handle() {
    local cmd=$1
    echo ""
    echo "❌ Command not found: $cmd"
    echo "   Try: wtf how do I $cmd"
    echo ""
    return 127
}
# wtf-not-found-hook-end

"""
    elif shell_type == 'fish':
        hook = """
# wtf command-not-found hook - suggest wtf when command not found
# Added by: wtf --setup-not-found-hook
# Remove with: wtf --remove-hooks
# wtf-not-found-hook-start
function fish_command_not_found
    set -l cmd $argv[1]
    echo ""
    echo "❌ Command not found: $cmd"
    echo "   Try: wtf how do I $cmd"
    echo ""
    return 127
end
# wtf-not-found-hook-end

"""
    else:
        return False, f"Unsupported shell type: {shell_type}"

    # Append hook to config file
    try:
        with open(config_file, 'a') as f:
            f.write(hook)

        return True, f"Not-found hook added to {config_file}"
    except Exception as e:
        return False, f"Failed to write to {config_file}: {e}"


def remove_hooks(shell_type: str) -> Tuple[bool, str]:
    """
    Remove all wtf hooks from shell config.

    Args:
        shell_type: Shell type (zsh, bash, fish)

    Returns:
        Tuple of (success: bool, message: str)
    """
    config_file = get_shell_config_file(shell_type)

    if not config_file or not config_file.exists():
        return False, f"Config file not found for {shell_type}"

    try:
        content = config_file.read_text()

        # Check if any hooks exist
        if 'wtf-error-hook' not in content and 'wtf-not-found-hook' not in content:
            return False, f"No wtf hooks found in {config_file}"

        # Remove error hook
        lines = content.split('\n')
        new_lines = []
        skip = False

        for line in lines:
            if 'wtf-error-hook-start' in line or 'wtf-not-found-hook-start' in line:
                skip = True
                continue
            if 'wtf-error-hook-end' in line or 'wtf-not-found-hook-end' in line:
                skip = False
                continue
            if not skip:
                new_lines.append(line)

        # Write back
        config_file.write_text('\n'.join(new_lines))

        return True, f"Hooks removed from {config_file}"

    except Exception as e:
        return False, f"Failed to remove hooks: {e}"


def show_hook_info(shell_type: str) -> None:
    """
    Display information about available hooks.

    Args:
        shell_type: Shell type (zsh, bash, fish)
    """
    config_file = get_shell_config_file(shell_type)

    console.print()
    console.print(Panel.fit(
        f"""[bold]Shell Hooks for {shell_type}[/bold]

Want wtf available at all times? Set up automatic hooks!

[bold cyan]Error Hook[/bold cyan] - Suggest wtf when commands fail
  • Detects failed commands (exit code ≠ 0)
  • Reminds you to run 'wtf' to diagnose
  • Setup: [green]wtf --setup-error-hook[/green]

[bold cyan]Command Not Found Hook[/bold cyan] - Suggest wtf for unknown commands
  • Triggers when command doesn't exist
  • Suggests using wtf to figure it out
  • Setup: [green]wtf --setup-not-found-hook[/green]

[bold cyan]Remove Hooks[/bold cyan]
  • Remove all hooks: [red]wtf --remove-hooks[/red]

Config file: [dim]{config_file}[/dim]

[yellow]Note:[/yellow] You'll need to restart your shell or run:
  source {config_file}
""",
        border_style="cyan"
    ))
    console.print()
