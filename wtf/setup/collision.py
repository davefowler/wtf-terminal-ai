"""Detect and handle name collisions during installation."""

import os
import re
from typing import Optional, Dict, List
from pathlib import Path


def get_shell_config_files() -> List[Path]:
    """
    Get list of shell config files to check.

    Returns:
        List of Path objects for existing shell config files
    """
    home = Path.home()
    potential_files = [
        home / ".zshrc",
        home / ".bashrc",
        home / ".bash_profile",
        home / ".profile",
        home / ".config" / "fish" / "config.fish",
    ]

    return [f for f in potential_files if f.exists()]


def detect_wtf_collision() -> Optional[Dict[str, any]]:
    """
    Detect if 'wtf' is already defined in shell config.

    Returns:
        Dict with collision info if found, None otherwise:
        {
            "type": "alias" | "function" | "command",
            "location": path to file,
            "line_number": int,
            "definition": str (the actual line)
        }
    """
    config_files = get_shell_config_files()

    for config_file in config_files:
        try:
            with open(config_file, 'r') as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                # Check for alias wtf=
                if re.match(r'^\s*alias\s+wtf\s*=', line):
                    return {
                        "type": "alias",
                        "location": str(config_file),
                        "line_number": i,
                        "definition": line.strip()
                    }

                # Check for function wtf()
                if re.match(r'^\s*(function\s+)?wtf\s*\(\s*\)', line):
                    return {
                        "type": "function",
                        "location": str(config_file),
                        "line_number": i,
                        "definition": line.strip()
                    }

        except Exception:
            # Skip files we can't read
            continue

    # Check if wtf exists as a command in PATH
    wtf_in_path = check_command_exists("wtf")
    if wtf_in_path:
        return {
            "type": "command",
            "location": wtf_in_path,
            "line_number": None,
            "definition": f"wtf command found at {wtf_in_path}"
        }

    return None


def check_command_exists(command: str) -> Optional[str]:
    """
    Check if a command exists in PATH.

    Args:
        command: Command name to check

    Returns:
        Path to command if found, None otherwise
    """
    import subprocess

    try:
        result = subprocess.run(
            ["which", command],
            capture_output=True,
            text=True,
            timeout=2
        )

        if result.returncode == 0:
            return result.stdout.strip()

    except Exception:
        pass

    return None


def suggest_alternatives(preferred: Optional[str] = None) -> List[str]:
    """
    Suggest alternative names if 'wtf' is taken.

    Args:
        preferred: User's preferred alternative name

    Returns:
        List of suggested alternative names
    """
    alternatives = ["wtfai", "wai", "w", "wtfhelp"]

    if preferred and preferred not in alternatives:
        alternatives.insert(0, preferred)

    # Filter out names that are also taken
    available = []
    for alt in alternatives:
        if not check_command_exists(alt):
            available.append(alt)

    return available


def create_alias(name: str, target_command: str = "wtf") -> str:
    """
    Generate shell alias definition.

    Args:
        name: Alias name (e.g., "wtfai")
        target_command: Command to alias to (default: "wtf")

    Returns:
        Shell alias definition string
    """
    return f"alias {name}='noglob {target_command}'"


def handle_collision_interactive(collision: Dict[str, any]) -> Optional[str]:
    """
    Interactively handle a detected collision.

    Prompts user for how to resolve the collision.

    Args:
        collision: Collision info from detect_wtf_collision()

    Returns:
        Alternative name chosen by user, or None to abort
    """
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel

    console = Console()

    console.print()
    console.print("[yellow]⚠ Name Collision Detected[/yellow]")
    console.print()

    # Show collision details
    collision_info = f"""
Type: {collision['type']}
Location: {collision['location']}
"""
    if collision['line_number']:
        collision_info += f"Line: {collision['line_number']}\n"
    collision_info += f"Definition: {collision['definition']}"

    console.print(Panel(collision_info, title="Existing 'wtf'", border_style="yellow"))
    console.print()

    console.print("The command 'wtf' is already in use. You have a few options:")
    console.print()
    console.print("  1. Use an alternative name (recommended)")
    console.print("  2. Remove the existing 'wtf' (if safe)")
    console.print("  3. Abort installation")
    console.print()

    choice = Prompt.ask(
        "What would you like to do?",
        choices=["1", "2", "3"],
        default="1"
    )

    if choice == "1":
        # Suggest alternatives
        alternatives = suggest_alternatives()

        console.print()
        console.print("Available alternative names:")
        for i, alt in enumerate(alternatives[:5], 1):
            console.print(f"  {i}. [cyan]{alt}[/cyan]")
        console.print(f"  {len(alternatives[:5]) + 1}. Custom name")
        console.print()

        alt_choice = Prompt.ask(
            "Choose an alternative",
            choices=[str(i) for i in range(1, len(alternatives[:5]) + 2)],
            default="1"
        )

        if alt_choice == str(len(alternatives[:5]) + 1):
            # Custom name
            custom = Prompt.ask("Enter custom name")
            return custom
        else:
            # Use suggested alternative
            idx = int(alt_choice) - 1
            return alternatives[idx]

    elif choice == "2":
        # Warn about removing existing
        console.print()
        console.print("[yellow]Warning:[/yellow] This will modify your shell configuration.")
        console.print(f"Location: [cyan]{collision['location']}[/cyan]")
        console.print()

        if Confirm.ask("Are you sure you want to remove the existing 'wtf'?"):
            return "wtf"  # Keep using wtf
        else:
            return None  # Abort

    else:
        # Abort
        return None
