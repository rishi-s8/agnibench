"""
ProceduralEnvironment — a SimulatedEnvironment that receives its data
via initial_state dict rather than hardcoded fixture data.

Uses closure-based tool state (shared data_store) instead of module-level globals.
"""

from typing import Any, Dict, Optional

from agnibench.core.environment import SimulatedEnvironment


class ProceduralEnvironment(SimulatedEnvironment):
    """
    Environment for procedurally generated tasks.

    Unlike existing suite environments that use hardcoded fixture data and
    module-level globals, this environment:
    - Receives its data via initial_state dict
    - Shares a data_store dict with tool implementations via closures
    - Has sync_state_from_procedural() for runner integration
    """

    def __init__(self, data_store: Optional[Dict[str, Any]] = None):
        """
        Initialize with an optional data_store reference.

        Args:
            data_store: Shared mutable dict used by tool closures.
                       If None, creates a new empty dict.
        """
        self._data_store = data_store if data_store is not None else {}
        super().__init__()

    def _setup_default_state(self) -> None:
        """Set up default state from the data_store."""
        # Copy initial data from data_store into environment state
        for key, value in self._data_store.items():
            self._state[key] = value

    def initialize(self, initial_state: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize or reset the environment.

        If initial_state is provided, it populates both the data_store
        and the environment state.
        """
        if initial_state is not None:
            # Update data_store in-place so tool closures see the data
            self._data_store.clear()
            self._data_store.update(initial_state)
        super().initialize(initial_state)

    def reset(self) -> None:
        """Reset the environment."""
        super().reset()
        self._setup_default_state()

    def sync_state_from_procedural(self) -> None:
        """
        Sync environment state from the shared data_store.

        Called by BenchmarkRunner._sync_environment_state() after tool executions
        and before verification, to pick up any state mutations made by tools.
        """
        # Sync mutable state keys that tools may have modified
        mutable_keys = ["sent_emails", "created_events", "sent_slack"]
        for key in mutable_keys:
            if key in self._data_store:
                self._state[key] = self._data_store[key]

    @property
    def data_store(self) -> Dict[str, Any]:
        """Get reference to the shared data store."""
        return self._data_store
