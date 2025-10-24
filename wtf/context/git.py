"""Git context gathering."""

import os
import subprocess
from typing import Optional, Dict, Any
from pathlib import Path


def is_git_repo(path: str = ".") -> bool:
    """
    Check if the current directory is a git repository.

    Args:
        path: Directory to check (defaults to current directory)

    Returns:
        True if directory is inside a git repository
    """
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            cwd=path,
            capture_output=True,
            timeout=2
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def get_git_status(path: str = ".") -> Optional[Dict[str, Any]]:
    """
    Get git repository status.

    Args:
        path: Directory to check (defaults to current directory)

    Returns:
        Dictionary with git status information, or None if not a git repo
        Contains:
        - branch: current branch name
        - status: output of git status --short
        - has_changes: bool indicating if there are uncommitted changes
        - ahead_behind: string like "ahead 2, behind 1" or None
    """
    if not is_git_repo(path):
        return None

    status_dict: Dict[str, Any] = {
        'branch': None,
        'status': '',
        'has_changes': False,
        'ahead_behind': None
    }

    try:
        # Get current branch
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            status_dict['branch'] = result.stdout.strip()

        # Get short status
        result = subprocess.run(
            ['git', 'status', '--short'],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            status_dict['status'] = result.stdout.strip()
            status_dict['has_changes'] = bool(result.stdout.strip())

        # Get ahead/behind info
        result = subprocess.run(
            ['git', 'rev-list', '--left-right', '--count', 'HEAD...@{upstream}'],
            cwd=path,
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split()
            if len(parts) == 2:
                ahead, behind = int(parts[0]), int(parts[1])
                if ahead > 0 or behind > 0:
                    parts_str = []
                    if ahead > 0:
                        parts_str.append(f"ahead {ahead}")
                    if behind > 0:
                        parts_str.append(f"behind {behind}")
                    status_dict['ahead_behind'] = ", ".join(parts_str)

    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return status_dict
