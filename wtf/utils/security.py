"""Security checks for commands."""

from typing import List

# Dangerous command patterns
DANGEROUS_PATTERNS = [
    # Filesystem destruction
    "rm -rf /",
    "rm -rf /*",
    "rm -rf ~",
    "rm -rf *",
    "> /dev/sda",
    "dd if=/dev/zero",
    "dd if=/dev/random",
    "mkfs",
    "mkfs.",

    # Fork bombs
    ":(){ :|:& };:",
    "fork while fork",

    # Kernel/system
    "sudo rm",
    "sudo dd",
    "sudo mkfs",
    "/dev/sda",
    "/dev/hda",

    # Dangerous downloads/execution
    "| sh",
    "| bash",
    "| sudo",

    # Permission changes on system files
    "chmod 777 /",
    "chmod -R 777 /",
    "chown -R",

    # Process killing
    "killall -9",
    "pkill -9",

    # Overwrite files
    "cat /dev/urandom >",
]


def is_command_chained(cmd: str) -> bool:
    """
    Check if command contains chaining operators.

    Args:
        cmd: Command string to check

    Returns:
        True if command is chained
    """
    dangerous_chains = ['&&', '||', ';', '$(',  '`', '|']

    for chain in dangerous_chains:
        if chain in cmd:
            return True

    return False


def is_command_dangerous(cmd: str) -> bool:
    """
    Check if command matches dangerous patterns.

    Args:
        cmd: Command string to check

    Returns:
        True if command is potentially dangerous
    """
    cmd_lower = cmd.lower().strip()

    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in cmd_lower:
            return True

    return False
