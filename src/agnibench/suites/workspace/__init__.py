"""
Workspace Benchmark Suite

Tests email, calendar, and Slack coordination tasks.
Selected as the most common agentic use case, testing planning abilities.
"""

from agnibench.core.abstractions import BenchmarkSuite
from agnibench.suites.workspace.environment import WorkspaceEnvironment
from agnibench.suites.workspace.tasks import get_workspace_tasks
from agnibench.suites.workspace.tools import get_workspace_tools


def WorkspaceSuite() -> BenchmarkSuite:
    """Create the workspace benchmark suite."""
    return BenchmarkSuite(
        name="workspace",
        description="Email, calendar, and Slack coordination testing planning and multi-tool orchestration",
        tasks=get_workspace_tasks(),
        tools=get_workspace_tools(),
        environment_class=WorkspaceEnvironment,
        version="1.0.0",
        tags=["workspace", "email", "calendar", "slack", "coordination"],
    )


__all__ = [
    "WorkspaceSuite",
    "WorkspaceEnvironment",
    "get_workspace_tools",
    "get_workspace_tasks",
]
