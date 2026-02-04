"""
Agentic Benchmarking Framework

A comprehensive framework for evaluating SLMs vs LLMs on multi-step tool-calling tasks.
"""

from agnibench.core.abstractions import (BenchmarkSuite, DifficultyLevel,
                                         InformationFlow, Task,
                                         TaskCharacteristics, TaskResult)
from agnibench.core.environment import SimulatedEnvironment
from agnibench.core.evaluation import (CompositeVerifier,
                                       CustomFunctionVerifier,
                                       EnvironmentStateVerifier,
                                       ExactMatchVerifier,
                                       ToolCallSequenceVerifier, Verifier)
from agnibench.core.reporting import BenchmarkReport, ComparisonReport
from agnibench.core.runner import BenchmarkRunner

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
