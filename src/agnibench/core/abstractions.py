"""
Core abstractions for the benchmarking framework.

Defines Task, BenchmarkSuite, TaskCharacteristics, and related data structures.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime


class DifficultyLevel(Enum):
    """Task difficulty levels based on tool call complexity."""
    SIMPLE = "simple"      # 2-3 tool calls, straightforward logic
    MEDIUM = "medium"      # 4-6 tool calls, some ambiguity
    HARD = "hard"          # 7-10 tool calls, requires planning
    EXPERT = "expert"      # 11-15+ tool calls, complex reasoning + adaptation


class InformationFlow(Enum):
    """How information flows in the task."""
    PROMPT_FULL = "prompt_full"                     # Both control flow and data in user prompt
    PROMPT_CONTROL_TOOL_DATA = "prompt_control_tool_data"  # Control from prompt, data via tools
    TOOL_DISCOVERY = "tool_discovery"              # Both control and data discovered via tools


@dataclass
class TaskCharacteristics:
    """Boolean flags describing task characteristics for analysis."""

    # Information flow flags
    control_flow_from_prompt: bool = True      # Control flow described in user prompt
    data_flow_from_prompt: bool = False        # Data provided directly in prompt
    control_flow_from_tools: bool = False      # Must discover what to do via tools
    data_flow_from_tools: bool = True          # Must discover data via tools

    # Capability requirement flags
    requires_error_recovery: bool = False      # Must handle and recover from failures
    requires_disambiguation: bool = False      # Prompt is ambiguous, needs clarification
    requires_state_tracking: bool = False      # Must track state across multiple calls
    requires_multi_constraint: bool = False    # Must satisfy multiple constraints
    requires_cross_reference: bool = False     # Must combine info from multiple sources
    requires_conditional_logic: bool = False   # Complex if/then decision making
    requires_long_reasoning_chain: bool = False  # 5+ step reasoning chain
    requires_plan_adaptation: bool = False     # Must change approach mid-execution

    def to_dict(self) -> Dict[str, bool]:
        """Convert to dictionary for serialization."""
        return {
            "control_flow_from_prompt": self.control_flow_from_prompt,
            "data_flow_from_prompt": self.data_flow_from_prompt,
            "control_flow_from_tools": self.control_flow_from_tools,
            "data_flow_from_tools": self.data_flow_from_tools,
            "requires_error_recovery": self.requires_error_recovery,
            "requires_disambiguation": self.requires_disambiguation,
            "requires_state_tracking": self.requires_state_tracking,
            "requires_multi_constraint": self.requires_multi_constraint,
            "requires_cross_reference": self.requires_cross_reference,
            "requires_conditional_logic": self.requires_conditional_logic,
            "requires_long_reasoning_chain": self.requires_long_reasoning_chain,
            "requires_plan_adaptation": self.requires_plan_adaptation,
        }

    @classmethod
    def from_information_flow(cls, flow: InformationFlow) -> "TaskCharacteristics":
        """Create characteristics based on information flow type."""
        if flow == InformationFlow.PROMPT_FULL:
            return cls(
                control_flow_from_prompt=True,
                data_flow_from_prompt=True,
                control_flow_from_tools=False,
                data_flow_from_tools=False,
            )
        elif flow == InformationFlow.PROMPT_CONTROL_TOOL_DATA:
            return cls(
                control_flow_from_prompt=True,
                data_flow_from_prompt=False,
                control_flow_from_tools=False,
                data_flow_from_tools=True,
            )
        else:  # TOOL_DISCOVERY
            return cls(
                control_flow_from_prompt=False,
                data_flow_from_prompt=False,
                control_flow_from_tools=True,
                data_flow_from_tools=True,
            )


@dataclass
class ToolCall:
    """Record of a single tool call during execution."""
    tool_name: str
    arguments: Dict[str, Any]
    result: Any
    success: bool
    error: Optional[str] = None
    timestamp: Optional[datetime] = None


@dataclass
class Task:
    """
    A single benchmark task.

    Contains the prompt, expected behavior, and verification criteria.
    """
    id: str
    name: str
    prompt: str
    difficulty: DifficultyLevel
    information_flow: InformationFlow
    characteristics: TaskCharacteristics
    expected_tool_calls: List[str]  # List of expected tool names in order
    expected_answer: Any  # Expected final answer or key parts of it
    verifier_config: Dict[str, Any]  # Configuration for verification

    # Optional fields
    description: Optional[str] = None
    min_tool_calls: int = 1
    max_tool_calls: int = 20
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "prompt": self.prompt,
            "difficulty": self.difficulty.value,
            "information_flow": self.information_flow.value,
            "characteristics": self.characteristics.to_dict(),
            "expected_tool_calls": self.expected_tool_calls,
            "expected_answer": self.expected_answer,
            "verifier_config": self.verifier_config,
            "description": self.description,
            "min_tool_calls": self.min_tool_calls,
            "max_tool_calls": self.max_tool_calls,
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class VerificationResult:
    """Result of verifying a task execution."""
    passed: bool
    score: float  # 0.0 to 1.0
    details: Dict[str, Any] = field(default_factory=dict)
    layer_results: Dict[str, bool] = field(default_factory=dict)  # Per-layer pass/fail
    error: Optional[str] = None


@dataclass
class TaskResult:
    """
    Result of executing a single task.

    Contains the execution trace, final response, and verification results.
    """
    task_id: str
    task_name: str
    success: bool
    final_response: str
    tool_calls: List[ToolCall]
    verification: VerificationResult

    # Timing and metadata
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time_ms: Optional[float] = None
    model_name: Optional[str] = None
    error: Optional[str] = None

    @property
    def tool_call_count(self) -> int:
        """Number of tool calls made."""
        return len(self.tool_calls)

    @property
    def tool_names_used(self) -> List[str]:
        """List of unique tool names used."""
        return list(dict.fromkeys(tc.tool_name for tc in self.tool_calls))

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "success": self.success,
            "final_response": self.final_response,
            "tool_calls": [
                {
                    "tool_name": tc.tool_name,
                    "arguments": tc.arguments,
                    "result": tc.result,
                    "success": tc.success,
                    "error": tc.error,
                }
                for tc in self.tool_calls
            ],
            "verification": {
                "passed": self.verification.passed,
                "score": self.verification.score,
                "details": self.verification.details,
                "layer_results": self.verification.layer_results,
                "error": self.verification.error,
            },
            "tool_call_count": self.tool_call_count,
            "tool_names_used": self.tool_names_used,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "execution_time_ms": self.execution_time_ms,
            "model_name": self.model_name,
            "error": self.error,
        }


@dataclass
class BenchmarkSuite:
    """
    A collection of related benchmark tasks.

    Represents a thematic benchmark (e.g., math_reasoning, workspace).
    """
    name: str
    description: str
    tasks: List[Task]
    tools: List[Any]  # List of Tool objects
    environment_class: type  # SimulatedEnvironment subclass

    # Metadata
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)

    @property
    def task_count(self) -> int:
        """Total number of tasks in the suite."""
        return len(self.tasks)

    @property
    def difficulty_distribution(self) -> Dict[str, int]:
        """Count of tasks per difficulty level."""
        distribution = {level.value: 0 for level in DifficultyLevel}
        for task in self.tasks:
            distribution[task.difficulty.value] += 1
        return distribution

    @property
    def information_flow_distribution(self) -> Dict[str, int]:
        """Count of tasks per information flow type."""
        distribution = {flow.value: 0 for flow in InformationFlow}
        for task in self.tasks:
            distribution[task.information_flow.value] += 1
        return distribution

    def get_tasks_by_difficulty(self, difficulty: DifficultyLevel) -> List[Task]:
        """Get all tasks of a specific difficulty."""
        return [t for t in self.tasks if t.difficulty == difficulty]

    def get_tasks_by_information_flow(self, flow: InformationFlow) -> List[Task]:
        """Get all tasks with a specific information flow."""
        return [t for t in self.tasks if t.information_flow == flow]

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert suite to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "task_count": self.task_count,
            "difficulty_distribution": self.difficulty_distribution,
            "information_flow_distribution": self.information_flow_distribution,
            "tasks": [t.to_dict() for t in self.tasks],
            "tool_count": len(self.tools),
            "tags": self.tags,
        }
