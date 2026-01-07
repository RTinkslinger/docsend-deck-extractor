"""Application state machine.

Manages the current state of the application and validates state transitions.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from PySide6.QtCore import QObject, Signal


class State(Enum):
    """Application states corresponding to different screens."""

    HOME = "home"
    PROGRESS = "progress"
    AUTH_EMAIL = "auth_email"
    AUTH_PASSCODE = "auth_passcode"
    COMPLETE = "complete"
    ERROR = "error"


# Valid state transitions
VALID_TRANSITIONS: dict[State, list[State]] = {
    State.HOME: [State.PROGRESS],
    State.PROGRESS: [State.AUTH_EMAIL, State.COMPLETE, State.ERROR],
    State.AUTH_EMAIL: [State.PROGRESS, State.AUTH_PASSCODE],
    State.AUTH_PASSCODE: [State.PROGRESS],
    State.COMPLETE: [State.HOME],
    State.ERROR: [State.PROGRESS, State.HOME],
}


class StateManager(QObject):
    """Manages application state and emits signals on state changes."""

    state_changed = Signal(State)

    def __init__(self, parent: Optional[QObject] = None):
        """Initialize state manager.

        Args:
            parent: Optional parent QObject
        """
        super().__init__(parent)
        self._state = State.HOME

    @property
    def state(self) -> State:
        """Get the current state."""
        return self._state

    def set_state(self, new_state: State, force: bool = False) -> bool:
        """Transition to a new state.

        Args:
            new_state: The state to transition to
            force: If True, skip transition validation

        Returns:
            True if transition was successful, False otherwise
        """
        if not force and not self.can_transition(self._state, new_state):
            return False

        old_state = self._state
        self._state = new_state
        self.state_changed.emit(new_state)
        return True

    def can_transition(self, from_state: State, to_state: State) -> bool:
        """Check if a state transition is valid.

        Args:
            from_state: Current state
            to_state: Target state

        Returns:
            True if transition is valid
        """
        return to_state in VALID_TRANSITIONS.get(from_state, [])

    def reset(self) -> None:
        """Reset to home state."""
        self._state = State.HOME
        self.state_changed.emit(State.HOME)
