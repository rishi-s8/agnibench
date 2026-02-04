"""
Simulated environment base class for benchmark suites.

Provides state tracking and tool execution context.
"""

from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class StateChange:
    """Record of a state change in the environment."""

    key: str
    old_value: Any
    new_value: Any
    timestamp: datetime = field(default_factory=datetime.now)
    source_tool: Optional[str] = None


class SimulatedEnvironment(ABC):
    """
    Base class for simulated environments in benchmark suites.

    Manages state, provides data for tools, and tracks changes.
    """

    def __init__(self):
        """Initialize the environment."""
        self._state: Dict[str, Any] = {}
        self._initial_state: Dict[str, Any] = {}
        self._state_history: List[StateChange] = []
        self._tool_call_log: List[Dict[str, Any]] = []

    def initialize(self, initial_state: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize or reset the environment with initial state.

        Args:
            initial_state: Optional initial state dictionary
        """
        self._state = deepcopy(initial_state) if initial_state else {}
        self._initial_state = deepcopy(self._state)
        self._state_history = []
        self._tool_call_log = []
        self._setup_default_state()

    @abstractmethod
    def _setup_default_state(self) -> None:
        """Set up default state for the environment. Override in subclasses."""
        pass

    def reset(self) -> None:
        """Reset environment to initial state."""
        self._state = deepcopy(self._initial_state)
        self._state_history = []
        self._tool_call_log = []

    # State management methods

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a value from the state."""
        return self._state.get(key, default)

    def set_state(
        self, key: str, value: Any, source_tool: Optional[str] = None
    ) -> None:
        """
        Set a value in the state and record the change.

        Args:
            key: State key to set
            value: New value
            source_tool: Optional name of the tool that caused this change
        """
        old_value = self._state.get(key)
        self._state[key] = value
        self._state_history.append(
            StateChange(
                key=key,
                old_value=old_value,
                new_value=value,
                source_tool=source_tool,
            )
        )

    def update_state(
        self, updates: Dict[str, Any], source_tool: Optional[str] = None
    ) -> None:
        """Update multiple state values at once."""
        for key, value in updates.items():
            self.set_state(key, value, source_tool)

    def delete_state(self, key: str, source_tool: Optional[str] = None) -> None:
        """Delete a key from the state."""
        if key in self._state:
            old_value = self._state.pop(key)
            self._state_history.append(
                StateChange(
                    key=key,
                    old_value=old_value,
                    new_value=None,
                    source_tool=source_tool,
                )
            )

    def has_state(self, key: str) -> bool:
        """Check if a key exists in the state."""
        return key in self._state

    @property
    def state(self) -> Dict[str, Any]:
        """Get a copy of the current state."""
        return deepcopy(self._state)

    @property
    def state_history(self) -> List[StateChange]:
        """Get the state change history."""
        return self._state_history.copy()

    # Tool call logging

    def log_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        result: Any,
        success: bool,
        error: Optional[str] = None,
    ) -> None:
        """Log a tool call for later verification."""
        self._tool_call_log.append(
            {
                "tool_name": tool_name,
                "arguments": arguments,
                "result": result,
                "success": success,
                "error": error,
                "timestamp": datetime.now(),
            }
        )

    @property
    def tool_call_log(self) -> List[Dict[str, Any]]:
        """Get the tool call log."""
        return self._tool_call_log.copy()

    # Verification helpers

    def get_state_changes_for_key(self, key: str) -> List[StateChange]:
        """Get all changes for a specific state key."""
        return [sc for sc in self._state_history if sc.key == key]

    def get_tool_calls_by_name(self, tool_name: str) -> List[Dict[str, Any]]:
        """Get all calls to a specific tool."""
        return [tc for tc in self._tool_call_log if tc["tool_name"] == tool_name]

    def verify_state_contains(self, key: str, expected_value: Any) -> bool:
        """Verify that state contains expected value (supports partial matching for collections)."""
        actual = self.get_state(key)
        if actual is None:
            return False

        if isinstance(expected_value, dict) and isinstance(actual, dict):
            # Check if all expected keys/values are present
            for k, v in expected_value.items():
                if k not in actual or actual[k] != v:
                    return False
            return True
        elif isinstance(expected_value, (list, set)) and isinstance(
            actual, (list, set)
        ):
            # Check if all expected items are present
            return all(item in actual for item in expected_value)
        else:
            return actual == expected_value

    def verify_tool_was_called(
        self,
        tool_name: str,
        with_arguments: Optional[Dict[str, Any]] = None,
        min_times: int = 1,
        max_times: Optional[int] = None,
    ) -> bool:
        """
        Verify that a tool was called with optional argument matching.

        Args:
            tool_name: Name of the tool to check
            with_arguments: Optional arguments that must be present (partial match)
            min_times: Minimum number of times tool must be called
            max_times: Optional maximum number of times
        """
        calls = self.get_tool_calls_by_name(tool_name)

        if with_arguments:
            # Filter to calls matching the specified arguments
            matching_calls = []
            for call in calls:
                args = call["arguments"]
                if all(k in args and args[k] == v for k, v in with_arguments.items()):
                    matching_calls.append(call)
            calls = matching_calls

        count = len(calls)
        if count < min_times:
            return False
        if max_times is not None and count > max_times:
            return False
        return True

    def get_final_state_diff(self) -> Dict[str, Any]:
        """Get the difference between initial and final state."""
        diff = {}
        all_keys = set(self._initial_state.keys()) | set(self._state.keys())

        for key in all_keys:
            initial = self._initial_state.get(key)
            final = self._state.get(key)
            if initial != final:
                diff[key] = {"initial": initial, "final": final}

        return diff

    # Context manager support for test isolation

    def __enter__(self) -> "SimulatedEnvironment":
        """Enter context - creates a checkpoint."""
        self._checkpoint_state = deepcopy(self._state)
        self._checkpoint_history_len = len(self._state_history)
        self._checkpoint_log_len = len(self._tool_call_log)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context - optionally restore checkpoint on error."""
        # Don't restore on normal exit, only clean up
        pass

    def restore_checkpoint(self) -> None:
        """Restore to the last checkpoint created by context manager."""
        if hasattr(self, "_checkpoint_state"):
            self._state = deepcopy(self._checkpoint_state)
            self._state_history = self._state_history[: self._checkpoint_history_len]
            self._tool_call_log = self._tool_call_log[: self._checkpoint_log_len]
