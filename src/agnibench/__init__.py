"""
Agentic Benchmarking Framework

A comprehensive framework for evaluating SLMs vs LLMs on multi-step tool-calling tasks.
"""

from agnibench.core.abstractions import (
    Task,
    TaskResult,
    BenchmarkSuite,
    TaskCharacteristics,
    DifficultyLevel,
    InformationFlow,
)
from agnibench.core.environment import SimulatedEnvironment
from agnibench.core.evaluation import (
    Verifier,
    ExactMatchVerifier,
    EnvironmentStateVerifier,
    ToolCallSequenceVerifier,
    CompositeVerifier,
    CustomFunctionVerifier,
)
from agnibench.core.runner import BenchmarkRunner
from agnibench.core.reporting import BenchmarkReport, ComparisonReport

__all__ = [
    # Abstractions
    "Task",
    "TaskResult",
    "BenchmarkSuite",
    "TaskCharacteristics",
    "DifficultyLevel",
    "InformationFlow",
    # Environment
    "SimulatedEnvironment",
    # Evaluation
    "Verifier",
    "ExactMatchVerifier",
    "EnvironmentStateVerifier",
    "ToolCallSequenceVerifier",
    "CompositeVerifier",
    "CustomFunctionVerifier",
    # Runner
    "BenchmarkRunner",
    # Reporting
    "BenchmarkReport",
    "ComparisonReport",
]
