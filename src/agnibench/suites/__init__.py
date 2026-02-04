"""
Benchmark suites for evaluating agentic capabilities.

Phase 1 includes 5 suites selected for maximum SLM vs LLM differentiation:
- math_reasoning: Mathematical calculation chains
- workspace: Email, calendar, Slack coordination
- research_synthesis: Information retrieval and synthesis
- customer_service: Issue resolution with incomplete info
- data_analysis: Data exploration and insight generation
"""

from agnibench.suites.math_reasoning import MathReasoningSuite
from agnibench.suites.workspace import WorkspaceSuite
from agnibench.suites.research_synthesis import ResearchSynthesisSuite
from agnibench.suites.customer_service import CustomerServiceSuite
from agnibench.suites.data_analysis import DataAnalysisSuite

__all__ = [
    "MathReasoningSuite",
    "WorkspaceSuite",
    "ResearchSynthesisSuite",
    "CustomerServiceSuite",
    "DataAnalysisSuite",
]

# Registry of all available suites
SUITE_REGISTRY = {
    "math_reasoning": MathReasoningSuite,
    "workspace": WorkspaceSuite,
    "research_synthesis": ResearchSynthesisSuite,
    "customer_service": CustomerServiceSuite,
    "data_analysis": DataAnalysisSuite,
}


def get_suite(name: str):
    """Get a benchmark suite by name."""
    if name not in SUITE_REGISTRY:
        raise ValueError(f"Unknown suite: {name}. Available: {list(SUITE_REGISTRY.keys())}")
    return SUITE_REGISTRY[name]()


def get_all_suites():
    """Get instances of all benchmark suites."""
    return [suite_class() for suite_class in SUITE_REGISTRY.values()]
