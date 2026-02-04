"""
Benchmark runner for executing tasks and collecting results.

Orchestrates task execution across benchmark suites.
"""

import json
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Type

from agnibench.core.abstractions import (
    Task,
    TaskResult,
    ToolCall,
    VerificationResult,
    BenchmarkSuite,
    DifficultyLevel,
)
from agnibench.core.environment import SimulatedEnvironment
from agnibench.core.evaluation import Verifier, CompositeVerifier


@dataclass
class RunConfig:
    """Configuration for a benchmark run."""
    model_name: str
    max_iterations: int = 15
    timeout_seconds: int = 120
    verbose: bool = True
    save_traces: bool = True
    retry_on_error: bool = False
    max_retries: int = 2


@dataclass
class SuiteResult:
    """Results from running a complete benchmark suite."""
    suite_name: str
    model_name: str
    task_results: List[TaskResult]
    start_time: datetime
    end_time: Optional[datetime] = None
    config: Optional[RunConfig] = None

    @property
    def total_tasks(self) -> int:
        return len(self.task_results)

    @property
    def passed_tasks(self) -> int:
        return sum(1 for r in self.task_results if r.success)

    @property
    def pass_rate(self) -> float:
        return self.passed_tasks / self.total_tasks if self.total_tasks > 0 else 0.0

    @property
    def average_score(self) -> float:
        if not self.task_results:
            return 0.0
        return sum(r.verification.score for r in self.task_results) / len(self.task_results)

    @property
    def average_tool_calls(self) -> float:
        if not self.task_results:
            return 0.0
        return sum(r.tool_call_count for r in self.task_results) / len(self.task_results)

    def results_by_difficulty(self) -> Dict[str, Dict[str, Any]]:
        """Get pass rates and scores grouped by difficulty."""
        by_difficulty = {}
        for result in self.task_results:
            # Get difficulty from task metadata if available
            difficulty = result.task_id.split("_")[1] if "_" in result.task_id else "unknown"
            if difficulty not in by_difficulty:
                by_difficulty[difficulty] = {"passed": 0, "total": 0, "scores": []}
            by_difficulty[difficulty]["total"] += 1
            by_difficulty[difficulty]["scores"].append(result.verification.score)
            if result.success:
                by_difficulty[difficulty]["passed"] += 1

        # Calculate rates
        for diff, data in by_difficulty.items():
            data["pass_rate"] = data["passed"] / data["total"] if data["total"] > 0 else 0
            data["avg_score"] = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0

        return by_difficulty

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "suite_name": self.suite_name,
            "model_name": self.model_name,
            "total_tasks": self.total_tasks,
            "passed_tasks": self.passed_tasks,
            "pass_rate": self.pass_rate,
            "average_score": self.average_score,
            "average_tool_calls": self.average_tool_calls,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "results_by_difficulty": self.results_by_difficulty(),
            "task_results": [r.to_dict() for r in self.task_results],
        }


class BenchmarkRunner:
    """
    Runs benchmark tasks and collects results.

    Can work with any agent implementation that follows the expected interface.
    """

    def __init__(
        self,
        agent_factory: Callable[[List[Any], SimulatedEnvironment], Any],
        verifier_factory: Optional[Callable[[Task], Verifier]] = None,
        config: Optional[RunConfig] = None,
    ):
        """
        Initialize the benchmark runner.

        Args:
            agent_factory: Function that creates an agent given tools and environment
                          Signature: (tools: List[Tool], env: SimulatedEnvironment) -> Agent
                          Agent must have: run(prompt: str) -> str method
            verifier_factory: Optional function to create verifier for a task
            config: Run configuration
        """
        self.agent_factory = agent_factory
        self.verifier_factory = verifier_factory
        self.config = config or RunConfig(model_name="unknown")
        self._current_tool_calls: List[ToolCall] = []

    def run_suite(self, suite: BenchmarkSuite) -> SuiteResult:
        """
        Run all tasks in a benchmark suite.

        Args:
            suite: The benchmark suite to run

        Returns:
            SuiteResult with all task results
        """
        start_time = datetime.now()
        task_results = []

        if self.config.verbose:
            print(f"\n{'='*60}")
            print(f"Running suite: {suite.name}")
            print(f"Tasks: {len(suite.tasks)}")
            print(f"Model: {self.config.model_name}")
            print(f"{'='*60}\n")

        for i, task in enumerate(suite.tasks, 1):
            if self.config.verbose:
                print(f"[{i}/{len(suite.tasks)}] Running: {task.name}")

            result = self.run_task(task, suite)
            task_results.append(result)

            if self.config.verbose:
                status = "PASS" if result.success else "FAIL"
                print(f"  Result: {status} (score: {result.verification.score:.2f})")
                print(f"  Tool calls: {result.tool_call_count}")
                if result.error:
                    print(f"  Error: {result.error}")
                print()

        return SuiteResult(
            suite_name=suite.name,
            model_name=self.config.model_name,
            task_results=task_results,
            start_time=start_time,
            end_time=datetime.now(),
            config=self.config,
        )

    def run_task(self, task: Task, suite: BenchmarkSuite) -> TaskResult:
        """
        Run a single task.

        Args:
            task: The task to run
            suite: The benchmark suite (for tools and environment)

        Returns:
            TaskResult with execution details and verification
        """
        start_time = datetime.now()
        self._current_tool_calls = []

        # Create fresh environment for this task
        environment = suite.environment_class()
        if hasattr(task, 'metadata') and 'initial_state' in task.metadata:
            environment.initialize(task.metadata['initial_state'])
        else:
            environment.initialize()

        # Create tools that log calls to environment
        wrapped_tools = self._wrap_tools_for_logging(suite.tools, environment)

        try:
            # Create agent with wrapped tools
            agent = self.agent_factory(wrapped_tools, environment)

            # Run the task
            final_response = agent.run(task.prompt)

            # Get tool calls from environment log
            tool_calls = [
                ToolCall(
                    tool_name=tc["tool_name"],
                    arguments=tc["arguments"],
                    result=tc["result"],
                    success=tc["success"],
                    error=tc.get("error"),
                    timestamp=tc.get("timestamp"),
                )
                for tc in environment.tool_call_log
            ]

            # Verify the result
            verifier = self._get_verifier(task)
            verification = verifier.verify(
                TaskResult(
                    task_id=task.id,
                    task_name=task.name,
                    success=True,  # Provisional
                    final_response=final_response,
                    tool_calls=tool_calls,
                    verification=VerificationResult(passed=False, score=0.0),
                ),
                environment,
                task.expected_answer,
            )

            end_time = datetime.now()

            return TaskResult(
                task_id=task.id,
                task_name=task.name,
                success=verification.passed,
                final_response=final_response,
                tool_calls=tool_calls,
                verification=verification,
                start_time=start_time,
                end_time=end_time,
                execution_time_ms=(end_time - start_time).total_seconds() * 1000,
                model_name=self.config.model_name,
            )

        except Exception as e:
            end_time = datetime.now()
            error_msg = f"{type(e).__name__}: {str(e)}"
            if self.config.verbose:
                traceback.print_exc()

            return TaskResult(
                task_id=task.id,
                task_name=task.name,
                success=False,
                final_response="",
                tool_calls=self._current_tool_calls,
                verification=VerificationResult(
                    passed=False,
                    score=0.0,
                    error=error_msg,
                ),
                start_time=start_time,
                end_time=end_time,
                execution_time_ms=(end_time - start_time).total_seconds() * 1000,
                model_name=self.config.model_name,
                error=error_msg,
            )

    def _wrap_tools_for_logging(
        self,
        tools: List[Any],
        environment: SimulatedEnvironment,
    ) -> List[Any]:
        """Wrap tools to log their calls to the environment."""
        wrapped = []
        for tool in tools:
            wrapped_tool = self._create_logging_wrapper(tool, environment)
            wrapped.append(wrapped_tool)
        return wrapped

    def _create_logging_wrapper(self, tool: Any, environment: SimulatedEnvironment) -> Any:
        """Create a wrapper that logs tool calls."""
        original_execute = tool.execute

        def logging_execute(**kwargs):
            result = original_execute(**kwargs)
            environment.log_tool_call(
                tool_name=tool.name,
                arguments=kwargs,
                result=result.data if hasattr(result, 'data') else result,
                success=result.success if hasattr(result, 'success') else True,
                error=result.error if hasattr(result, 'error') else None,
            )
            # Also track in runner for error cases
            self._current_tool_calls.append(ToolCall(
                tool_name=tool.name,
                arguments=kwargs,
                result=result.data if hasattr(result, 'data') else result,
                success=result.success if hasattr(result, 'success') else True,
                error=result.error if hasattr(result, 'error') else None,
                timestamp=datetime.now(),
            ))
            return result

        # Create a copy-like wrapper
        class WrappedTool:
            def __init__(self, original):
                self.name = original.name
                self.description = original.description
                self.parameters = original.parameters
                self.function = original.function

            def execute(self, **kwargs):
                return logging_execute(**kwargs)

            def to_openai_format(self):
                return tool.to_openai_format()

        return WrappedTool(tool)

    def _get_verifier(self, task: Task) -> Verifier:
        """Get the appropriate verifier for a task."""
        if self.verifier_factory:
            return self.verifier_factory(task)

        # Default: create verifier from task's verifier_config
        from agnibench.core.evaluation import (
            ExactMatchVerifier,
            EnvironmentStateVerifier,
            ToolCallSequenceVerifier,
            create_multi_layer_verifier,
        )

        config = task.verifier_config

        answer_verifier = None
        if "answer" in config:
            verifier = ExactMatchVerifier(
                case_sensitive=config.get("case_sensitive", False),
                match_mode=config.get("match_mode", "contains"),
            )
            answer_verifier = (verifier, config.get("answer_weight", 0.4), config["answer"])

        state_verifier = None
        if "state" in config:
            verifier = EnvironmentStateVerifier()
            state_verifier = (verifier, config.get("state_weight", 0.3), config["state"])

        tool_verifier = None
        if "tools" in config:
            verifier = ToolCallSequenceVerifier(
                strict_order=config.get("strict_order", False),
                allow_extra_calls=config.get("allow_extra_calls", True),
            )
            tool_verifier = (verifier, config.get("tools_weight", 0.2), config["tools"])

        return create_multi_layer_verifier(
            answer_verifier=answer_verifier,
            state_verifier=state_verifier,
            tool_verifier=tool_verifier,
        )

    def run_multiple_suites(
        self,
        suites: List[BenchmarkSuite],
    ) -> Dict[str, SuiteResult]:
        """Run multiple benchmark suites."""
        results = {}
        for suite in suites:
            results[suite.name] = self.run_suite(suite)
        return results


class MockAgent:
    """
    Mock agent for testing the benchmark framework.

    Can be configured with predefined responses.
    """

    def __init__(
        self,
        tools: List[Any],
        environment: SimulatedEnvironment,
        responses: Optional[Dict[str, Any]] = None,
    ):
        self.tools = {t.name: t for t in tools}
        self.environment = environment
        self.responses = responses or {}

    def run(self, prompt: str) -> str:
        """
        Run the mock agent.

        If responses dict has a matching prompt, execute that script.
        Otherwise return a default response.
        """
        if prompt in self.responses:
            script = self.responses[prompt]
            return self._execute_script(script)

        return "I could not process this request."

    def _execute_script(self, script: Dict[str, Any]) -> str:
        """Execute a predefined script of tool calls and response."""
        tool_calls = script.get("tool_calls", [])

        for call in tool_calls:
            tool_name = call["tool"]
            args = call.get("args", {})

            if tool_name in self.tools:
                self.tools[tool_name].execute(**args)

        return script.get("response", "")
