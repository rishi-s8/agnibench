"""
Math Reasoning Benchmark Suite

Tests mathematical calculation chains, working memory, and multi-step reasoning.
Selected for clear measurable outcomes and testing working memory capacity.
"""

from agnibench.core.abstractions import BenchmarkSuite
from agnibench.suites.math_reasoning.tools import get_math_tools
from agnibench.suites.math_reasoning.environment import MathEnvironment
from agnibench.suites.math_reasoning.tasks import get_math_tasks


def MathReasoningSuite() -> BenchmarkSuite:
    """Create the math reasoning benchmark suite."""
    return BenchmarkSuite(
        name="math_reasoning",
        description="Mathematical calculation chains testing working memory and multi-step reasoning",
        tasks=get_math_tasks(),
        tools=get_math_tools(),
        environment_class=MathEnvironment,
        version="1.0.0",
        tags=["math", "reasoning", "calculation", "memory"],
    )


__all__ = ["MathReasoningSuite", "MathEnvironment", "get_math_tools", "get_math_tasks"]
