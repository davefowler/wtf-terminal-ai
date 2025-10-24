"""Conversation state machine."""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


class ConversationState(Enum):
    """States in the wtf conversation flow."""

    INITIALIZING = auto()         # Gathering context (history, git, etc.)
    QUERYING_AI = auto()           # API call to AI provider
    STREAMING_RESPONSE = auto()    # Receiving streaming response
    AWAITING_PERMISSION = auto()   # User needs to approve command
    EXECUTING_COMMAND = auto()     # Running approved command
    PROCESSING_OUTPUT = auto()     # AI analyzing command output
    RESPONDING = auto()            # Showing final response
    COMPLETE = auto()              # Conversation finished
    ERROR = auto()                 # Error occurred


@dataclass
class ConversationContext:
    """Context maintained throughout conversation."""
    user_query: str
    cwd: str
    shell_history: List[str]
    git_status: Optional[Dict[str, Any]]
    env_context: Dict[str, Any]
    config: Dict[str, Any]

    # State that gets populated during conversation
    ai_response: str = ""
    commands_to_run: List[Dict[str, str]] = field(default_factory=list)
    current_command_index: int = 0
    command_outputs: List[str] = field(default_factory=list)

    # Permission lists
    allowlist: List[str] = field(default_factory=list)
    denylist: List[str] = field(default_factory=list)


class ConversationStateMachine:
    """Manages conversation flow with explicit state transitions."""

    def __init__(self, context: ConversationContext):
        self.state = ConversationState.INITIALIZING
        self.context = context
        self.error: Optional[Exception] = None

    def run(self) -> str:
        """
        Execute the conversation state machine.

        Returns:
            Final AI response or error message
        """
        while self.state != ConversationState.COMPLETE:
            try:
                self._execute_current_state()
            except Exception as e:
                self.error = e
                self.state = ConversationState.ERROR
                return self._handle_error()

        return self.context.ai_response

    def _execute_current_state(self):
        """Execute logic for current state and transition."""

        if self.state == ConversationState.INITIALIZING:
            # Context is already gathered, just transition
            self.state = ConversationState.QUERYING_AI

        elif self.state == ConversationState.QUERYING_AI:
            # This would call the AI - for now just transition
            # (actual implementation happens in CLI)
            self.state = ConversationState.STREAMING_RESPONSE

        elif self.state == ConversationState.STREAMING_RESPONSE:
            # Check if we have commands to run
            if self.context.commands_to_run and self.context.current_command_index < len(self.context.commands_to_run):
                self.state = ConversationState.AWAITING_PERMISSION
            else:
                self.state = ConversationState.RESPONDING

        elif self.state == ConversationState.AWAITING_PERMISSION:
            # Permission check happens externally
            # Transition to executing current command
            self.state = ConversationState.EXECUTING_COMMAND

        elif self.state == ConversationState.EXECUTING_COMMAND:
            # Execute current command
            self.context.current_command_index += 1

            # Check if more commands to run
            if self.context.current_command_index < len(self.context.commands_to_run):
                # More commands - check permission for next
                self.state = ConversationState.AWAITING_PERMISSION
            else:
                # All commands done
                self.state = ConversationState.RESPONDING

        elif self.state == ConversationState.PROCESSING_OUTPUT:
            # AI analyzes output and may loop back
            self.state = ConversationState.QUERYING_AI

        elif self.state == ConversationState.RESPONDING:
            # Show final response
            self.state = ConversationState.COMPLETE

        elif self.state == ConversationState.ERROR:
            # Error handling
            self.state = ConversationState.COMPLETE

    def _handle_error(self) -> str:
        """
        Handle error state.

        Returns:
            Error message
        """
        if self.error:
            return f"Error: {str(self.error)}"
        return "Unknown error occurred"

    def transition_to(self, new_state: ConversationState) -> None:
        """
        Manually transition to a new state.

        Args:
            new_state: State to transition to
        """
        self.state = new_state

    def is_complete(self) -> bool:
        """
        Check if conversation is complete.

        Returns:
            True if in COMPLETE or ERROR state
        """
        return self.state in (ConversationState.COMPLETE, ConversationState.ERROR)
