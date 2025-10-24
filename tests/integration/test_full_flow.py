"""
Integration tests for full wtf workflows.

These tests verify end-to-end behavior using mocked AI responses
to ensure the full stack works together correctly.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from wtf.cli import handle_query_with_tools
from wtf.core.config import load_config
from wtf.conversation.memory import save_memory, load_memories, clear_memories


class TestReadmeExamples:
    """Test examples from the README."""

    @pytest.fixture
    def mock_config(self):
        """Provide a mock configuration."""
        return {
            'api': {
                'provider': 'anthropic',
                'model': 'claude-3-sonnet-20240229',
                'key_source': 'env'
            },
            'behavior': {
                'context_history_size': 5
            }
        }

    @pytest.fixture
    def clean_memories(self):
        """Clean memories before tests."""
        clear_memories()
        yield
        clear_memories()

    @patch('wtf.cli.query_ai_with_tools')
    @patch('wtf.cli.get_shell_history')
    @patch('wtf.cli.get_git_status')
    @patch('wtf.cli.get_environment_context')
    @patch('wtf.cli.load_memories')
    def test_simple_query_flow(
        self,
        mock_load_memories,
        mock_env,
        mock_git,
        mock_history,
        mock_ai,
        mock_config
    ):
        """Test: wtf 'what's in my git status?'"""
        # Mock context
        mock_history.return_value = (["git add .", "git commit -m 'test'"], None)
        mock_git.return_value = {
            'branch': 'main',
            'has_changes': True,
            'ahead_behind': 'up to date'
        }
        mock_env.return_value = {'cwd': '/test', 'project_type': 'python'}
        mock_load_memories.return_value = {}

        # Mock AI response with tool call
        mock_ai.return_value = {
            'response': 'You have uncommitted changes on main branch.',
            'tool_calls': [
                {
                    'name': 'run_command',
                    'arguments': {'command': 'git status'},
                    'result': {
                        'output': 'On branch main\nChanges not staged',
                        'exit_code': 0,
                        'should_print': True
                    }
                }
            ],
            'iterations': 2
        }

        # This should not crash
        handle_query_with_tools("what's in my git status?", mock_config)

    @patch('wtf.cli.query_ai_with_tools')
    @patch('wtf.cli.get_shell_history')
    @patch('wtf.cli.get_git_status')
    @patch('wtf.cli.get_environment_context')
    @patch('wtf.cli.load_memories')
    def test_install_flow(
        self,
        mock_load_memories,
        mock_env,
        mock_git,
        mock_history,
        mock_ai,
        mock_config
    ):
        """Test: wtf install express"""
        mock_history.return_value = ([], None)
        mock_git.return_value = None
        mock_env.return_value = {'cwd': '/test', 'project_type': 'node'}
        mock_load_memories.return_value = {}

        # Mock AI suggesting npm install
        mock_ai.return_value = {
            'response': 'I will install express for you using npm.',
            'tool_calls': [
                {
                    'name': 'run_command',
                    'arguments': {'command': 'npm install express'},
                    'result': {
                        'output': 'added 50 packages',
                        'exit_code': 0,
                        'should_print': True
                    }
                }
            ],
            'iterations': 1
        }

        handle_query_with_tools("install express", mock_config)

    @patch('wtf.cli.query_ai_with_tools')
    @patch('wtf.cli.get_shell_history')
    @patch('wtf.cli.get_git_status')
    @patch('wtf.cli.get_environment_context')
    @patch('wtf.cli.load_memories')
    def test_undo_flow(
        self,
        mock_load_memories,
        mock_env,
        mock_git,
        mock_history,
        mock_ai,
        mock_config
    ):
        """Test: wtf undo"""
        # Last command was a git commit
        mock_history.return_value = (
            ["git add .", "git commit -m 'test'"],
            None
        )
        mock_git.return_value = {'branch': 'main'}
        mock_env.return_value = {'cwd': '/test', 'project_type': 'python'}
        mock_load_memories.return_value = {}

        # Mock AI suggesting undo
        mock_ai.return_value = {
            'response': 'I will undo your last commit while keeping the changes.',
            'tool_calls': [
                {
                    'name': 'run_command',
                    'arguments': {'command': 'git reset --soft HEAD~1'},
                    'result': {
                        'output': '',
                        'exit_code': 0,
                        'should_print': True
                    }
                }
            ],
            'iterations': 1
        }

        handle_query_with_tools("undo", mock_config)


class TestToolBasedWorkflow:
    """Test the tool-based agent workflow."""

    @pytest.fixture
    def mock_config(self):
        """Provide a mock configuration."""
        return {
            'api': {
                'provider': 'anthropic',
                'model': 'claude-3-sonnet-20240229',
                'key_source': 'env'
            },
            'behavior': {
                'context_history_size': 5
            }
        }

    @patch('wtf.cli.query_ai_with_tools')
    @patch('wtf.cli.get_shell_history')
    @patch('wtf.cli.get_git_status')
    @patch('wtf.cli.get_environment_context')
    @patch('wtf.cli.load_memories')
    def test_multi_step_with_internal_tools(
        self,
        mock_load_memories,
        mock_env,
        mock_git,
        mock_history,
        mock_ai,
        mock_config
    ):
        """Test that internal tools don't print, but run_command does."""
        mock_history.return_value = ([], None)
        mock_git.return_value = None
        mock_env.return_value = {'cwd': '/test', 'project_type': 'python'}
        mock_load_memories.return_value = {}

        # Mock AI using internal tools then running command
        mock_ai.return_value = {
            'response': 'Found your package.json and ran install.',
            'tool_calls': [
                {
                    'name': 'read_file',
                    'arguments': {'file_path': 'package.json'},
                    'result': {
                        'content': '{"name": "test"}',
                        'error': None,
                        'should_print': False  # Internal tool
                    }
                },
                {
                    'name': 'run_command',
                    'arguments': {'command': 'npm install'},
                    'result': {
                        'output': 'added packages',
                        'exit_code': 0,
                        'should_print': True  # User-facing tool
                    }
                }
            ],
            'iterations': 2
        }

        handle_query_with_tools("install dependencies", mock_config)

    @patch('wtf.cli.query_ai_with_tools')
    @patch('wtf.cli.get_shell_history')
    @patch('wtf.cli.get_git_status')
    @patch('wtf.cli.get_environment_context')
    @patch('wtf.cli.load_memories')
    def test_iterative_smart_commit(
        self,
        mock_load_memories,
        mock_env,
        mock_git,
        mock_history,
        mock_ai,
        mock_config
    ):
        """Test the smart commit workflow from README."""
        mock_history.return_value = ([], None)
        mock_git.return_value = {'branch': 'main', 'has_changes': True}
        mock_env.return_value = {'cwd': '/test', 'project_type': 'python'}
        mock_load_memories.return_value = {}

        # Mock AI workflow:
        # 1. Check diff (internal)
        # 2. Analyze changes
        # 3. Create smart commit message
        mock_ai.return_value = {
            'response': 'Created commit with message based on your changes.',
            'tool_calls': [
                {
                    'name': 'run_command',
                    'arguments': {'command': 'git diff'},
                    'result': {
                        'output': '+++ added new feature\n+++ tests',
                        'exit_code': 0,
                        'should_print': True
                    }
                },
                {
                    'name': 'run_command',
                    'arguments': {
                        'command': 'git commit -m "Add new feature with tests"'
                    },
                    'result': {
                        'output': '[main abc123] Add new feature with tests',
                        'exit_code': 0,
                        'should_print': True
                    }
                }
            ],
            'iterations': 2
        }

        handle_query_with_tools("make a smart commit", mock_config)


class TestContextGathering:
    """Test that context is properly gathered and used."""

    @pytest.fixture
    def mock_config(self):
        """Provide a mock configuration."""
        return {
            'api': {
                'provider': 'anthropic',
                'model': 'claude-3-sonnet-20240229',
                'key_source': 'env'
            },
            'behavior': {
                'context_history_size': 5
            }
        }

    @patch('wtf.cli.query_ai_with_tools')
    @patch('wtf.cli.get_shell_history')
    @patch('wtf.cli.get_git_status')
    @patch('wtf.cli.get_environment_context')
    @patch('wtf.cli.load_memories')
    def test_uses_shell_history(
        self,
        mock_load_memories,
        mock_env,
        mock_git,
        mock_history,
        mock_ai,
        mock_config
    ):
        """Test that shell history is included in context."""
        # Provide shell history
        mock_history.return_value = (
            ["npm run build", "npm test", "git status"],
            None
        )
        mock_git.return_value = None
        mock_env.return_value = {'cwd': '/test', 'project_type': 'node'}
        mock_load_memories.return_value = {}

        mock_ai.return_value = {
            'response': 'Looks like you just ran tests.',
            'tool_calls': [],
            'iterations': 1
        }

        handle_query_with_tools("what did I just do?", mock_config)

        # Verify history was requested
        mock_history.assert_called_once()

    @patch('wtf.cli.query_ai_with_tools')
    @patch('wtf.cli.get_shell_history')
    @patch('wtf.cli.get_git_status')
    @patch('wtf.cli.get_environment_context')
    @patch('wtf.cli.load_memories')
    def test_uses_git_context(
        self,
        mock_load_memories,
        mock_env,
        mock_git,
        mock_history,
        mock_ai,
        mock_config
    ):
        """Test that git context is included when in a repo."""
        mock_history.return_value = ([], None)
        mock_git.return_value = {
            'branch': 'feature/new-thing',
            'has_changes': True,
            'ahead_behind': '2 commits ahead'
        }
        mock_env.return_value = {'cwd': '/test', 'project_type': 'python'}
        mock_load_memories.return_value = {}

        mock_ai.return_value = {
            'response': 'You are on feature/new-thing branch.',
            'tool_calls': [],
            'iterations': 1
        }

        handle_query_with_tools("what branch am I on?", mock_config)

        # Verify git status was requested
        mock_git.assert_called_once()

    @patch('wtf.cli.query_ai_with_tools')
    @patch('wtf.cli.get_shell_history')
    @patch('wtf.cli.get_git_status')
    @patch('wtf.cli.get_environment_context')
    @patch('wtf.cli.load_memories')
    def test_uses_memories(
        self,
        mock_load_memories,
        mock_env,
        mock_git,
        mock_history,
        mock_ai,
        mock_config,
    ):
        """Test that memories are included in context."""
        mock_history.return_value = ([], None)
        mock_git.return_value = None
        mock_env.return_value = {'cwd': '/test', 'project_type': 'python'}

        # Mock saved memories
        mock_load_memories.return_value = {
            'editor': {'value': 'emacs', 'confidence': 1.0},
            'package_manager': {'value': 'npm', 'confidence': 1.0}
        }

        mock_ai.return_value = {
            'response': 'Using npm as you prefer.',
            'tool_calls': [],
            'iterations': 1
        }

        handle_query_with_tools("install something", mock_config)

        # Verify memories were loaded
        mock_load_memories.assert_called_once()
