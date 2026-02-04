"""
Data Analysis Benchmark Suite

Tests data exploration, insight generation, and iterative refinement.
Selected for testing discovery-based workflows and pattern recognition.
"""

from agnibench.core.abstractions import BenchmarkSuite
from agnibench.suites.data_analysis.tools import get_data_analysis_tools
from agnibench.suites.data_analysis.environment import DataAnalysisEnvironment
from agnibench.suites.data_analysis.tasks import get_data_analysis_tasks


def DataAnalysisSuite() -> BenchmarkSuite:
    """Create the data analysis benchmark suite."""
    return BenchmarkSuite(
        name="data_analysis",
        description="Data exploration and insight generation testing iterative refinement",
        tasks=get_data_analysis_tasks(),
        tools=get_data_analysis_tools(),
        environment_class=DataAnalysisEnvironment,
        version="1.0.0",
        tags=["data", "analysis", "exploration", "insights"],
    )


__all__ = ["DataAnalysisSuite", "DataAnalysisEnvironment", "get_data_analysis_tools", "get_data_analysis_tasks"]
