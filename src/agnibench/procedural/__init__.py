"""
Procedural benchmark generation for agnibench.

Generates benchmark suites with randomized tool API surfaces and
DAG-based task generation. Same seed produces identical benchmarks;
different seeds produce structurally equivalent but surface-different suites.

Usage:
    from agnibench.procedural import create_procedural_suite

    suite = create_procedural_suite(domain="workspace", seed=42)
    # suite is a standard BenchmarkSuite, works with BenchmarkRunner unchanged

    # Different seed = different tool names/params, same capabilities
    suite2 = create_procedural_suite(domain="workspace", seed=99)
"""

from agnibench.procedural.suite_factory import (
    ProceduralSuiteFactory,
    create_procedural_suite,
)

__all__ = [
    "create_procedural_suite",
    "ProceduralSuiteFactory",
]
