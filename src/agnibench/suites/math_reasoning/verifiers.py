"""
Custom verifiers for the math reasoning benchmark suite.
"""

from typing import Any, Dict, List
from agnibench.core.abstractions import TaskResult, VerificationResult
from agnibench.core.environment import SimulatedEnvironment
from agnibench.core.evaluation import (
    Verifier,
    ExactMatchVerifier,
    EnvironmentStateVerifier,
    ToolCallSequenceVerifier,
    CompositeVerifier,
    CustomFunctionVerifier,
    create_multi_layer_verifier,
)


class NumericToleranceVerifier(Verifier):
    """
    Verifies numeric answers within a tolerance.

    More sophisticated than ExactMatchVerifier for math problems.
    """

    def __init__(
        self,
        tolerance: float = 0.01,
        relative_tolerance: bool = True,
    ):
        """
        Initialize the verifier.

        Args:
            tolerance: Acceptable deviation from expected
            relative_tolerance: If True, tolerance is a percentage; if False, absolute
        """
        self.tolerance = tolerance
        self.relative_tolerance = relative_tolerance

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify numeric answer within tolerance."""
        import re

        response = result.final_response
        details = {"response": response, "expected": expected}

        # Extract numbers from response
        numbers = re.findall(r'-?\d+\.?\d*', response.replace(',', ''))
        numbers = [float(n) for n in numbers]

        if not numbers:
            return VerificationResult(
                passed=False,
                score=0.0,
                details={**details, "error": "No numbers found in response"},
            )

        # Handle single expected value
        if isinstance(expected, (int, float)):
            expected = [expected]

        # Handle dict of expected values
        if isinstance(expected, dict):
            expected = list(expected.values())

        # Check if any expected value is found within tolerance
        matches = []
        for exp in expected:
            if not isinstance(exp, (int, float)):
                continue

            for num in numbers:
                if self.relative_tolerance:
                    if exp != 0:
                        rel_diff = abs(num - exp) / abs(exp)
                        if rel_diff <= self.tolerance:
                            matches.append((exp, num, rel_diff))
                    elif num == 0:
                        matches.append((exp, num, 0))
                else:
                    abs_diff = abs(num - exp)
                    if abs_diff <= self.tolerance:
                        matches.append((exp, num, abs_diff))

        if matches:
            score = len(matches) / len([e for e in expected if isinstance(e, (int, float))])
            return VerificationResult(
                passed=True,
                score=min(1.0, score),
                details={**details, "matches": matches},
            )

        return VerificationResult(
            passed=False,
            score=0.0,
            details={**details, "numbers_found": numbers, "error": "No matching values"},
        )


class CalculationChainVerifier(Verifier):
    """
    Verifies that calculations followed a logical chain.

    Checks that intermediate results build toward the final answer.
    """

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify calculation chain logic."""
        calculator_calls = [
            tc for tc in result.tool_calls if tc.tool_name == "calculator"
        ]

        if not calculator_calls:
            return VerificationResult(
                passed=False,
                score=0.0,
                details={"error": "No calculator calls found"},
            )

        # Extract results from each calculation
        results = []
        for call in calculator_calls:
            if call.success and call.result:
                if isinstance(call.result, dict) and "result" in call.result:
                    results.append(call.result["result"])

        # Check if results form a logical progression
        # (Later calculations should reference earlier results)
        details = {
            "calculation_count": len(calculator_calls),
            "results": results,
        }

        # Basic check: ensure we got results
        if results:
            return VerificationResult(
                passed=True,
                score=1.0,
                details=details,
            )

        return VerificationResult(
            passed=False,
            score=0.5,
            details={**details, "warning": "Calculations made but no results extracted"},
        )


class ScratchpadUsageVerifier(Verifier):
    """
    Verifies proper use of scratchpad for state tracking.

    Rewards storing intermediate results when required.
    """

    def __init__(self, required_keys: List[str] = None, min_entries: int = 0):
        self.required_keys = required_keys or []
        self.min_entries = min_entries

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify scratchpad usage."""
        scratchpad_calls = [
            tc for tc in result.tool_calls if tc.tool_name == "scratchpad"
        ]

        store_calls = [
            tc for tc in scratchpad_calls
            if tc.arguments.get("operation") == "store"
        ]

        stored_keys = [tc.arguments.get("key") for tc in store_calls]

        details = {
            "scratchpad_calls": len(scratchpad_calls),
            "store_operations": len(store_calls),
            "stored_keys": stored_keys,
            "required_keys": self.required_keys,
        }

        # Check minimum entries
        if len(store_calls) < self.min_entries:
            return VerificationResult(
                passed=False,
                score=len(store_calls) / self.min_entries if self.min_entries else 0,
                details={**details, "error": f"Expected at least {self.min_entries} stored values"},
            )

        # Check required keys
        if self.required_keys:
            missing = [k for k in self.required_keys if k not in stored_keys]
            if missing:
                return VerificationResult(
                    passed=False,
                    score=(len(self.required_keys) - len(missing)) / len(self.required_keys),
                    details={**details, "missing_keys": missing},
                )

        return VerificationResult(
            passed=True,
            score=1.0,
            details=details,
        )


class FormulaApplicationVerifier(Verifier):
    """
    Verifies correct formula lookup and application.
    """

    def __init__(self, expected_formulas: List[str] = None):
        self.expected_formulas = expected_formulas or []

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify formula usage."""
        formula_calls = [
            tc for tc in result.tool_calls if tc.tool_name == "formula_lookup"
        ]

        looked_up = [
            tc.arguments.get("formula_name", "").lower()
            for tc in formula_calls
        ]

        details = {
            "formulas_looked_up": looked_up,
            "expected_formulas": self.expected_formulas,
        }

        if not self.expected_formulas:
            # No specific formulas required, just check if any were used
            return VerificationResult(
                passed=len(formula_calls) > 0,
                score=1.0 if formula_calls else 0.5,
                details=details,
            )

        # Check for expected formulas
        found = [f for f in self.expected_formulas if f.lower() in looked_up]
        score = len(found) / len(self.expected_formulas)

        return VerificationResult(
            passed=score >= 0.5,
            score=score,
            details={**details, "found": found},
        )


def create_math_verifier(task_config: Dict[str, Any]) -> CompositeVerifier:
    """
    Factory function to create appropriate verifier for a math task.

    Args:
        task_config: Task verifier configuration

    Returns:
        CompositeVerifier configured for the task
    """
    verifiers = []

    # Numeric answer verification
    if "answer" in task_config:
        numeric_verifier = NumericToleranceVerifier(
            tolerance=task_config.get("numeric_tolerance", 0.01),
            relative_tolerance=True,
        )
        verifiers.append((numeric_verifier, 0.4, task_config["answer"]))

    # Tool sequence verification
    if "tools" in task_config:
        tool_verifier = ToolCallSequenceVerifier(
            strict_order=task_config.get("strict_order", False),
            allow_extra_calls=True,
        )
        verifiers.append((tool_verifier, 0.2, task_config["tools"]))

    # Calculation chain verification
    if task_config.get("verify_chain", False):
        chain_verifier = CalculationChainVerifier()
        verifiers.append((chain_verifier, 0.2, None))

    # Scratchpad usage
    if task_config.get("require_scratchpad", False):
        scratchpad_verifier = ScratchpadUsageVerifier(
            required_keys=task_config.get("scratchpad_keys", []),
            min_entries=task_config.get("min_scratchpad_entries", 1),
        )
        verifiers.append((scratchpad_verifier, 0.1, None))

    # Formula verification
    if "expected_formulas" in task_config:
        formula_verifier = FormulaApplicationVerifier(
            expected_formulas=task_config["expected_formulas"]
        )
        verifiers.append((formula_verifier, 0.1, None))

    if not verifiers:
        # Fallback to basic exact match
        basic_verifier = ExactMatchVerifier(match_mode="contains")
        verifiers.append((basic_verifier, 1.0, task_config.get("answer", "")))

    return CompositeVerifier(verifiers, mode="weighted", pass_threshold=0.5)
