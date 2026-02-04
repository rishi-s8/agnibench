"""
Research Synthesis Benchmark Suite

Tests information retrieval, cross-referencing, and synthesis capabilities.
Selected for testing context integration and multi-source synthesis.
"""

from agnibench.core.abstractions import BenchmarkSuite
from agnibench.suites.research_synthesis.environment import ResearchEnvironment
from agnibench.suites.research_synthesis.tasks import get_research_tasks
from agnibench.suites.research_synthesis.tools import get_research_tools


def ResearchSynthesisSuite() -> BenchmarkSuite:
    """Create the research synthesis benchmark suite."""
    return BenchmarkSuite(
        name="research_synthesis",
        description="Information retrieval and synthesis testing context integration",
        tasks=get_research_tasks(),
        tools=get_research_tools(),
        environment_class=ResearchEnvironment,
        version="1.0.0",
        tags=["research", "synthesis", "documents", "cross-reference"],
    )


__all__ = [
    "ResearchSynthesisSuite",
    "ResearchEnvironment",
    "get_research_tools",
    "get_research_tasks",
]
