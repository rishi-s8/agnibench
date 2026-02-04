"""
Software Development Benchmark Suite

Tests debugging, code navigation, and software engineering tasks.
Evaluates agents on their ability to understand codebases, diagnose bugs,
and reason about code structure and dependencies.
"""

from agnibench.core.abstractions import BenchmarkSuite
from agnibench.suites.software_dev.tools import get_software_dev_tools
from agnibench.suites.software_dev.environment import SoftwareDevEnvironment
from agnibench.suites.software_dev.tasks import get_software_dev_tasks


def SoftwareDevSuite() -> BenchmarkSuite:
    """Create the software development benchmark suite."""
    return BenchmarkSuite(
        name="software_dev",
        description="Debugging, code navigation, and software engineering tasks testing code understanding and diagnostic reasoning",
        tasks=get_software_dev_tasks(),
        tools=get_software_dev_tools(),
        environment_class=SoftwareDevEnvironment,
        version="1.0.0",
        tags=["software_dev", "debugging", "code", "navigation", "engineering"],
    )


__all__ = ["SoftwareDevSuite", "SoftwareDevEnvironment", "get_software_dev_tools", "get_software_dev_tasks"]
