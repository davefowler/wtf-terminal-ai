"""Tests for conversation state machine."""

import pytest
from wtf.conversation.state import (
    ConversationState,
    ConversationContext,
    ConversationStateMachine,
)


@pytest.fixture
def basic_context():
    """Create a basic conversation context."""
    return ConversationContext(
        user_query="test query",
        cwd="/test/dir",
        shell_history=["git status", "ls"],
        git_status={"branch": "main"},
        env_context={"project_type": "python"},
        config={"api": {"provider": "openai"}},
    )


def test_conversation_state_enum():
    """Test that all conversation states exist."""
    assert ConversationState.INITIALIZING
    assert ConversationState.QUERYING_AI
    assert ConversationState.STREAMING_RESPONSE
    assert ConversationState.AWAITING_PERMISSION
    assert ConversationState.EXECUTING_COMMAND
    assert ConversationState.PROCESSING_OUTPUT
    assert ConversationState.RESPONDING
    assert ConversationState.COMPLETE
    assert ConversationState.ERROR


def test_conversation_context_creation(basic_context):
    """Test creating a conversation context."""
    assert basic_context.user_query == "test query"
    assert basic_context.cwd == "/test/dir"
    assert len(basic_context.shell_history) == 2
    assert basic_context.ai_response == ""
    assert basic_context.commands_to_run == []


def test_state_machine_initialization(basic_context):
    """Test state machine starts in INITIALIZING state."""
    sm = ConversationStateMachine(basic_context)
    assert sm.state == ConversationState.INITIALIZING
    assert sm.error is None


def test_state_machine_basic_flow_no_commands(basic_context):
    """Test state machine with no commands (just response)."""
    sm = ConversationStateMachine(basic_context)

    # INITIALIZING -> QUERYING_AI
    sm._execute_current_state()
    assert sm.state == ConversationState.QUERYING_AI

    # QUERYING_AI -> STREAMING_RESPONSE
    sm._execute_current_state()
    assert sm.state == ConversationState.STREAMING_RESPONSE

    # STREAMING_RESPONSE -> RESPONDING (no commands)
    sm._execute_current_state()
    assert sm.state == ConversationState.RESPONDING

    # RESPONDING -> COMPLETE
    sm._execute_current_state()
    assert sm.state == ConversationState.COMPLETE


def test_state_machine_with_single_command(basic_context):
    """Test state machine with one command to execute."""
    basic_context.commands_to_run = [
        {"command": "git status", "pattern": "git status"}
    ]

    sm = ConversationStateMachine(basic_context)

    # INITIALIZING -> QUERYING_AI -> STREAMING_RESPONSE
    sm._execute_current_state()
    sm._execute_current_state()
    sm._execute_current_state()

    # Should be waiting for permission
    assert sm.state == ConversationState.AWAITING_PERMISSION

    # AWAITING_PERMISSION -> EXECUTING_COMMAND
    sm._execute_current_state()
    assert sm.state == ConversationState.EXECUTING_COMMAND

    # EXECUTING_COMMAND -> RESPONDING (no more commands)
    sm._execute_current_state()
    assert sm.state == ConversationState.RESPONDING
    assert sm.context.current_command_index == 1


def test_state_machine_with_multiple_commands(basic_context):
    """Test state machine with multiple commands."""
    basic_context.commands_to_run = [
        {"command": "git status", "pattern": "git status"},
        {"command": "git add .", "pattern": "git add"},
    ]

    sm = ConversationStateMachine(basic_context)

    # Get to first command execution
    sm._execute_current_state()  # INIT -> QUERY
    assert sm.state == ConversationState.QUERYING_AI

    sm._execute_current_state()  # QUERY -> STREAM
    assert sm.state == ConversationState.STREAMING_RESPONSE

    sm._execute_current_state()  # STREAM -> AWAIT
    assert sm.state == ConversationState.AWAITING_PERMISSION

    # Execute first command
    sm._execute_current_state()
    assert sm.state == ConversationState.EXECUTING_COMMAND

    sm._execute_current_state()
    assert sm.state == ConversationState.AWAITING_PERMISSION  # Back to permission for cmd 2
    assert sm.context.current_command_index == 1

    # Execute second command
    sm._execute_current_state()
    assert sm.state == ConversationState.EXECUTING_COMMAND

    sm._execute_current_state()
    assert sm.state == ConversationState.RESPONDING  # All done
    assert sm.context.current_command_index == 2


def test_state_machine_run_method(basic_context):
    """Test the run() method executes full flow."""
    basic_context.ai_response = "Test response"

    sm = ConversationStateMachine(basic_context)
    result = sm.run()

    assert sm.state == ConversationState.COMPLETE
    assert result == "Test response"


def test_state_machine_error_handling(basic_context):
    """Test state machine handles errors."""
    sm = ConversationStateMachine(basic_context)

    # Simulate an error
    sm.error = ValueError("Test error")
    sm.state = ConversationState.ERROR

    error_msg = sm._handle_error()
    assert "Test error" in error_msg


def test_state_machine_manual_transition(basic_context):
    """Test manually transitioning states."""
    sm = ConversationStateMachine(basic_context)

    sm.transition_to(ConversationState.RESPONDING)
    assert sm.state == ConversationState.RESPONDING

    sm.transition_to(ConversationState.ERROR)
    assert sm.state == ConversationState.ERROR


def test_state_machine_is_complete(basic_context):
    """Test is_complete() method."""
    sm = ConversationStateMachine(basic_context)

    assert not sm.is_complete()

    sm.state = ConversationState.COMPLETE
    assert sm.is_complete()

    sm.state = ConversationState.ERROR
    assert sm.is_complete()

    sm.state = ConversationState.EXECUTING_COMMAND
    assert not sm.is_complete()
