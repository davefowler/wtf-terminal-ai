"""Tests for configuration management."""

import json
import tempfile
import shutil
from pathlib import Path
import pytest

from wtf.core.config import (
    get_default_config,
    get_default_allowlist,
    create_default_config,
    load_config,
    save_config,
    get_config_dir,
)


@pytest.fixture
def temp_config_dir(monkeypatch):
    """Create a temporary config directory for testing."""
    temp_dir = tempfile.mkdtemp()
    monkeypatch.setenv('XDG_CONFIG_HOME', temp_dir)
    yield Path(temp_dir) / 'wtf'
    shutil.rmtree(temp_dir)


def test_get_default_config():
    """Test default config has all required keys."""
    config = get_default_config()

    assert 'version' in config
    assert 'api' in config
    assert 'behavior' in config
    assert 'shell' in config

    assert config['api']['provider'] == 'anthropic'
    assert config['api']['key_source'] == 'env'
    assert config['behavior']['auto_execute_allowlist'] is True


def test_get_default_allowlist():
    """Test default allowlist has denylist."""
    allowlist = get_default_allowlist()

    assert 'patterns' in allowlist
    assert 'denylist' in allowlist
    assert isinstance(allowlist['patterns'], list)
    assert isinstance(allowlist['denylist'], list)
    assert 'rm -rf /' in allowlist['denylist']


def test_create_default_config(temp_config_dir):
    """Test creating default config files."""
    create_default_config()

    # Check directory was created
    assert temp_config_dir.exists()

    # Check all files were created
    assert (temp_config_dir / 'config.json').exists()
    assert (temp_config_dir / 'allowlist.json').exists()
    assert (temp_config_dir / 'wtf.md').exists()
    assert (temp_config_dir / 'memories.json').exists()
    assert (temp_config_dir / 'history.jsonl').exists()


def test_load_config(temp_config_dir):
    """Test loading config from file."""
    create_default_config()
    config = load_config()

    assert config['version'] == '0.1.0'
    assert 'api' in config
    assert 'behavior' in config


def test_save_config_creates_backup(temp_config_dir):
    """Test that save_config creates backups."""
    create_default_config()

    # Modify and save
    config = load_config()
    config['api']['provider'] = 'openai'
    save_config(config)

    # Check backup was created
    backups = list(temp_config_dir.glob('config.json.backup.*'))
    assert len(backups) == 1


def test_config_merge_with_defaults(temp_config_dir):
    """Test that loading config merges with defaults."""
    create_default_config()

    # Write incomplete config
    config_path = temp_config_dir / 'config.json'
    with open(config_path, 'w') as f:
        json.dump({'version': '0.1.0', 'api': {'provider': 'openai'}}, f)

    # Load should merge with defaults
    config = load_config()
    assert config['api']['provider'] == 'openai'
    assert 'behavior' in config  # From defaults
    assert config['behavior']['auto_execute_allowlist'] is True
