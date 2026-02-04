"""
Verification system for benchmark task evaluation.

Provides multi-layer verification with different verifier types.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union

from agnibench.core.abstractions import (TaskResult, ToolCall,
                                         VerificationResult)
from agnibench.core.environment import SimulatedEnvironment


class Verifier(ABC):
    """Base class for all verifiers."""

    @abstractmethod
    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """
        Verify task execution results.

        Args:
            result: The task execution result
            environment: The simulated environment with state
            expected: Expected value or configuration

        Returns:
            VerificationResult with pass/fail and details
        """
        pass

    @property
    def name(self) -> str:
        """Name of the verifier for reporting."""
        return self.__class__.__name__


class ExactMatchVerifier(Verifier):
    """
    Verifies that the final response contains or matches expected values.

    Supports:
    - Exact string matching
    - Substring containment
    - Numeric tolerance
    - List of acceptable answers
    - Rejection patterns (negative matching)
    """

    def __init__(
        self,
        case_sensitive: bool = False,
        match_mode: str = "contains",  # "exact", "contains", "regex"
        numeric_tolerance: float = 0.001,
        rejection_patterns: Optional[List[str]] = None,
    ):
        self.case_sensitive = case_sensitive
        self.match_mode = match_mode
        self.numeric_tolerance = numeric_tolerance
        self.rejection_patterns = rejection_patterns or []

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify the response matches expected value."""
        response = result.final_response
        details = {"response": response, "expected": expected, "mode": self.match_mode}

        # Check rejection patterns FIRST - if any match, fail immediately
        for pattern in self.rejection_patterns:
            pattern_to_check = pattern if self.case_sensitive else pattern.lower()
            response_to_check = response if self.case_sensitive else response.lower()
            if pattern_to_check in response_to_check:
                return VerificationResult(
                    passed=False,
                    score=0.0,
                    details={
                        **details,
                        "rejected_by": pattern,
                        "error": f"Response contains rejection pattern: {pattern}",
                    },
                )

        # Handle list of acceptable answers
        if isinstance(expected, list):
            for exp in expected:
                sub_result = self._check_match(response, exp)
                if sub_result:
                    return VerificationResult(
                        passed=True,
                        score=1.0,
                        details={**details, "matched": exp},
                    )
            return VerificationResult(
                passed=False,
                score=0.0,
                details={**details, "error": "No acceptable answer matched"},
            )

        passed = self._check_match(response, expected)
        return VerificationResult(
            passed=passed,
            score=1.0 if passed else 0.0,
            details=details,
        )

    def _check_match(self, response: str, expected: Any) -> bool:
        """Check if response matches a single expected value."""
        # Numeric matching
        if isinstance(expected, (int, float)):
            try:
                # Extract numbers from response
                numbers = re.findall(r"-?\d+\.?\d*", response)
                for num_str in numbers:
                    num = float(num_str)
                    if abs(num - expected) <= self.numeric_tolerance:
                        return True
                return False
            except (ValueError, TypeError):
                return False

        # String matching
        expected_str = str(expected)
        response_str = response

        if not self.case_sensitive:
            expected_str = expected_str.lower()
            response_str = response_str.lower()

        if self.match_mode == "exact":
            return response_str.strip() == expected_str.strip()
        elif self.match_mode == "contains":
            return expected_str in response_str
        elif self.match_mode == "regex":
            flags = 0 if self.case_sensitive else re.IGNORECASE
            return bool(re.search(expected_str, response, flags))
        else:
            return expected_str in response_str


class OutcomeVerifier(Verifier):
    """
    Pass/fail based purely on environment state.

    Does NOT consider tool calls - only final outcome.
    This is the primary metric for benchmark discrimination.

    All state conditions must pass for the task to be considered passed.
    """

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected_state: Dict[str, Any],
    ) -> VerificationResult:
        """
        Verify environment state matches expected conditions.

        Args:
            result: The task execution result (used for response checks)
            environment: The simulated environment with state
            expected_state: Dict mapping state keys to expected values or conditions

        Returns:
            VerificationResult with binary pass/fail (all must pass)
        """
        if not expected_state:
            # No expected state defined - pass by default
            return VerificationResult(
                passed=True,
                score=1.0,
                details={"note": "No expected_state defined"},
            )

        all_passed = True
        details = {"checks": []}

        for key, condition in expected_state.items():
            actual = environment.get_state(key)
            check_result = self._check_condition(key, actual, condition)
            details["checks"].append(check_result)
            if not check_result["passed"]:
                all_passed = False

        return VerificationResult(
            passed=all_passed,  # Binary - ALL must pass
            score=1.0 if all_passed else 0.0,
            details=details,
        )

    def _check_condition(self, key: str, actual: Any, condition: Any) -> Dict[str, Any]:
        """Check a single condition against actual value."""
        result = {"key": key, "actual": actual, "condition": condition}

        # If condition is a dict with operators
        if isinstance(condition, dict):
            operator = next((k for k in condition.keys() if k.startswith("$")), None)
            if operator:
                passed = self._apply_operator(actual, operator, condition[operator])
                result["passed"] = passed
                result["operator"] = operator
                return result

        # Simple equality check
        result["passed"] = actual == condition
        return result

    def _apply_operator(self, actual: Any, operator: str, operand: Any) -> bool:
        """Apply an operator to check the condition."""
        if operator == "$eq":
            return actual == operand

        elif operator == "$contains":
            if actual is None:
                return False
            if isinstance(actual, str):
                return operand in actual
            elif isinstance(actual, (list, tuple, set)):
                return operand in actual
            elif isinstance(actual, dict):
                if isinstance(operand, dict):
                    return all(
                        k in actual and actual[k] == v for k, v in operand.items()
                    )
                return operand in actual
            return False

        elif operator == "$regex":
            if not isinstance(actual, str):
                return False
            return bool(re.search(operand, actual))

        elif operator == "$range":
            if not isinstance(actual, (int, float)):
                return False
            min_val, max_val = operand
            return min_val <= actual <= max_val

        elif operator == "$exists":
            return (actual is not None) == operand

        elif operator == "$type":
            type_map = {
                "str": str,
                "string": str,
                "int": int,
                "integer": int,
                "float": float,
                "bool": bool,
                "boolean": bool,
                "list": list,
                "array": list,
                "dict": dict,
                "object": dict,
                "none": type(None),
                "null": type(None),
            }
            expected_type = type_map.get(
                operand.lower() if isinstance(operand, str) else operand
            )
            return isinstance(actual, expected_type) if expected_type else False

        elif operator == "$length":
            if not hasattr(actual, "__len__"):
                return False
            length = len(actual)
            if isinstance(operand, int):
                return length == operand
            elif isinstance(operand, dict):
                # Support $gte, $lte, $gt, $lt
                for op, val in operand.items():
                    if op == "$gte" and not length >= val:
                        return False
                    elif op == "$lte" and not length <= val:
                        return False
                    elif op == "$gt" and not length > val:
                        return False
                    elif op == "$lt" and not length < val:
                        return False
                return True
            return False

        return False


class EnvironmentStateVerifier(Verifier):
    """
    Verifies that environment state matches expected conditions.

    Supports operators:
    - $eq: Exact equality
    - $contains: Contains value (for strings, lists, dicts)
    - $regex: Regex match (for strings)
    - $range: Numeric range [min, max]
    - $exists: Key exists (value should be True/False)
    - $type: Value is of specified type
    - $length: Collection length comparison
    """

    OPERATORS = {"$eq", "$contains", "$regex", "$range", "$exists", "$type", "$length"}

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Dict[str, Any],
    ) -> VerificationResult:
        """
        Verify environment state matches expected conditions.

        Args:
            expected: Dict mapping state keys to expected values or operator conditions
                     e.g., {"emails_sent": {"$length": {"$gte": 1}}}
        """
        details = {"checks": []}
        all_passed = True

        for key, condition in expected.items():
            actual = environment.get_state(key)
            check_result = self._check_condition(key, actual, condition)
            details["checks"].append(check_result)
            if not check_result["passed"]:
                all_passed = False

        passed_count = sum(1 for c in details["checks"] if c["passed"])
        total = len(details["checks"])
        score = passed_count / total if total > 0 else 0.0

        return VerificationResult(
            passed=all_passed,
            score=score,
            details=details,
        )

    def _check_condition(self, key: str, actual: Any, condition: Any) -> Dict[str, Any]:
        """Check a single condition against actual value."""
        result = {"key": key, "actual": actual, "condition": condition}

        # If condition is a dict with operators
        if isinstance(condition, dict):
            operator = next((k for k in condition.keys() if k.startswith("$")), None)
            if operator:
                passed = self._apply_operator(actual, operator, condition[operator])
                result["passed"] = passed
                result["operator"] = operator
                return result

        # Simple equality check
        result["passed"] = actual == condition
        return result

    def _apply_operator(self, actual: Any, operator: str, operand: Any) -> bool:
        """Apply an operator to check the condition."""
        if operator == "$eq":
            return actual == operand

        elif operator == "$contains":
            if actual is None:
                return False
            if isinstance(actual, str):
                return operand in actual
            elif isinstance(actual, (list, tuple, set)):
                return operand in actual
            elif isinstance(actual, dict):
                if isinstance(operand, dict):
                    return all(
                        k in actual and actual[k] == v for k, v in operand.items()
                    )
                return operand in actual
            return False

        elif operator == "$regex":
            if not isinstance(actual, str):
                return False
            return bool(re.search(operand, actual))

        elif operator == "$range":
            if not isinstance(actual, (int, float)):
                return False
            min_val, max_val = operand
            return min_val <= actual <= max_val

        elif operator == "$exists":
            return (actual is not None) == operand

        elif operator == "$type":
            type_map = {
                "str": str,
                "string": str,
                "int": int,
                "integer": int,
                "float": float,
                "bool": bool,
                "boolean": bool,
                "list": list,
                "array": list,
                "dict": dict,
                "object": dict,
                "none": type(None),
                "null": type(None),
            }
            expected_type = type_map.get(
                operand.lower() if isinstance(operand, str) else operand
            )
            return isinstance(actual, expected_type) if expected_type else False

        elif operator == "$length":
            if not hasattr(actual, "__len__"):
                return False
            length = len(actual)
            if isinstance(operand, int):
                return length == operand
            elif isinstance(operand, dict):
                # Support $gte, $lte, $gt, $lt
                for op, val in operand.items():
                    if op == "$gte" and not length >= val:
                        return False
                    elif op == "$lte" and not length <= val:
                        return False
                    elif op == "$gt" and not length > val:
                        return False
                    elif op == "$lt" and not length < val:
                        return False
                return True
            return False

        return False


class ToolCallSequenceVerifier(Verifier):
    """
    Verifies that required tools were called in the expected order.

    Supports:
    - Required tool calls (must be present)
    - Optional tool calls (can be present)
    - Strict ordering or loose ordering
    - Minimum/maximum call counts
    """

    def __init__(
        self,
        strict_order: bool = False,
        allow_extra_calls: bool = True,
    ):
        self.strict_order = strict_order
        self.allow_extra_calls = allow_extra_calls

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Dict[str, Any],
    ) -> VerificationResult:
        """
        Verify tool call sequence.

        Args:
            expected: Dict with:
                - required: List of required tool names (in order if strict_order)
                - optional: List of optional tool names
                - min_calls: Minimum total calls
                - max_calls: Maximum total calls
        """
        actual_calls = [tc.tool_name for tc in result.tool_calls]
        required = expected.get("required", [])
        optional = expected.get("optional", [])
        min_calls = expected.get("min_calls")
        max_calls = expected.get("max_calls")

        details = {
            "actual_calls": actual_calls,
            "required": required,
            "checks": [],
        }

        all_passed = True

        # Check minimum calls
        if min_calls is not None and len(actual_calls) < min_calls:
            details["checks"].append(
                {
                    "check": "min_calls",
                    "passed": False,
                    "expected": min_calls,
                    "actual": len(actual_calls),
                }
            )
            all_passed = False
        elif min_calls is not None:
            details["checks"].append(
                {
                    "check": "min_calls",
                    "passed": True,
                    "expected": min_calls,
                    "actual": len(actual_calls),
                }
            )

        # Check maximum calls
        if max_calls is not None and len(actual_calls) > max_calls:
            details["checks"].append(
                {
                    "check": "max_calls",
                    "passed": False,
                    "expected": max_calls,
                    "actual": len(actual_calls),
                }
            )
            all_passed = False
        elif max_calls is not None:
            details["checks"].append(
                {
                    "check": "max_calls",
                    "passed": True,
                    "expected": max_calls,
                    "actual": len(actual_calls),
                }
            )

        # Check required tools
        if self.strict_order:
            # Must appear in exact order (but other tools can be interspersed)
            passed = self._check_ordered_sequence(actual_calls, required)
            details["checks"].append(
                {
                    "check": "required_ordered",
                    "passed": passed,
                    "expected": required,
                }
            )
            if not passed:
                all_passed = False
        else:
            # Just check presence
            missing = [t for t in required if t not in actual_calls]
            passed = len(missing) == 0
            details["checks"].append(
                {
                    "check": "required_present",
                    "passed": passed,
                    "missing": missing,
                }
            )
            if not passed:
                all_passed = False

        # Check for disallowed calls
        if not self.allow_extra_calls:
            allowed = set(required + optional)
            extra = [t for t in actual_calls if t not in allowed]
            if extra:
                details["checks"].append(
                    {
                        "check": "no_extra_calls",
                        "passed": False,
                        "extra": extra,
                    }
                )
                all_passed = False

        # Calculate score
        required_found = sum(1 for t in required if t in actual_calls)
        score = required_found / len(required) if required else 1.0

        return VerificationResult(
            passed=all_passed,
            score=score,
            details=details,
        )

    def _check_ordered_sequence(self, actual: List[str], required: List[str]) -> bool:
        """Check if required tools appear in order within actual calls."""
        if not required:
            return True

        req_idx = 0
        for call in actual:
            if call == required[req_idx]:
                req_idx += 1
                if req_idx >= len(required):
                    return True
        return req_idx >= len(required)


class CompositeVerifier(Verifier):
    """
    Combines multiple verifiers with weights.

    Supports:
    - AND logic (all must pass)
    - OR logic (any must pass)
    - Weighted scoring
    """

    def __init__(
        self,
        verifiers: List[tuple],  # List of (verifier, weight, expected) tuples
        mode: str = "and",  # "and", "or", "weighted"
        pass_threshold: float = 0.5,  # For weighted mode
    ):
        self.verifiers = verifiers
        self.mode = mode
        self.pass_threshold = pass_threshold

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any = None,  # Ignored, each verifier has its own expected
    ) -> VerificationResult:
        """Run all verifiers and combine results."""
        sub_results = []
        total_weight = sum(w for _, w, _ in self.verifiers)

        for verifier, weight, verifier_expected in self.verifiers:
            sub_result = verifier.verify(result, environment, verifier_expected)
            sub_results.append(
                {
                    "verifier": verifier.name,
                    "weight": weight,
                    "passed": sub_result.passed,
                    "score": sub_result.score,
                    "details": sub_result.details,
                }
            )

        details = {"sub_results": sub_results, "mode": self.mode}

        if self.mode == "and":
            passed = all(sr["passed"] for sr in sub_results)
            score = sum(sr["score"] * sr["weight"] for sr in sub_results) / total_weight
        elif self.mode == "or":
            passed = any(sr["passed"] for sr in sub_results)
            score = max(sr["score"] for sr in sub_results)
        else:  # weighted
            score = sum(sr["score"] * sr["weight"] for sr in sub_results) / total_weight
            passed = score >= self.pass_threshold

        return VerificationResult(
            passed=passed,
            score=score,
            details=details,
            layer_results={sr["verifier"]: sr["passed"] for sr in sub_results},
        )


class CustomFunctionVerifier(Verifier):
    """
    Verifier that uses a custom function for verification.

    Useful for task-specific verification logic.
    """

    def __init__(self, verify_fn: Callable, name: str = "CustomFunction"):
        """
        Initialize with a custom verification function.

        Args:
            verify_fn: Function(result, environment, expected) -> VerificationResult
            name: Name for this verifier
        """
        self._verify_fn = verify_fn
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Run the custom verification function."""
        try:
            return self._verify_fn(result, environment, expected)
        except Exception as e:
            return VerificationResult(
                passed=False,
                score=0.0,
                error=f"Verification function error: {str(e)}",
            )


class ExecutionLayerVerifier(Verifier):
    """Verifies that execution completed without errors."""

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any = None,
    ) -> VerificationResult:
        """Check for execution errors."""
        # Check for errors in result
        has_error = result.error is not None

        # Check for failed tool calls
        failed_calls = [tc for tc in result.tool_calls if not tc.success]

        passed = not has_error and len(failed_calls) == 0
        details = {
            "error": result.error,
            "failed_tool_calls": [
                {"tool": tc.tool_name, "error": tc.error} for tc in failed_calls
            ],
        }

        return VerificationResult(
            passed=passed,
            score=1.0 if passed else 0.0,
            details=details,
        )


class ReasoningQualityVerifier(Verifier):
    """
    Verifies the quality of the reasoning/tool sequence.

    Checks:
    - No redundant tool calls
    - Logical progression
    - Efficiency (not too many unnecessary calls)
    """

    def __init__(self, max_redundancy_ratio: float = 0.3):
        self.max_redundancy_ratio = max_redundancy_ratio

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any = None,
    ) -> VerificationResult:
        """Analyze reasoning quality."""
        tool_calls = result.tool_calls
        if not tool_calls:
            return VerificationResult(
                passed=True, score=1.0, details={"note": "No tool calls"}
            )

        # Check for exact duplicate consecutive calls
        duplicates = 0
        for i in range(1, len(tool_calls)):
            if (
                tool_calls[i].tool_name == tool_calls[i - 1].tool_name
                and tool_calls[i].arguments == tool_calls[i - 1].arguments
            ):
                duplicates += 1

        redundancy_ratio = duplicates / len(tool_calls)
        passed = redundancy_ratio <= self.max_redundancy_ratio

        details = {
            "total_calls": len(tool_calls),
            "duplicate_consecutive_calls": duplicates,
            "redundancy_ratio": redundancy_ratio,
            "max_allowed": self.max_redundancy_ratio,
        }

        score = max(0, 1.0 - (redundancy_ratio / self.max_redundancy_ratio))

        return VerificationResult(
            passed=passed,
            score=score,
            details=details,
        )


def create_multi_layer_verifier(
    answer_verifier: Optional[tuple] = None,
    state_verifier: Optional[tuple] = None,
    tool_verifier: Optional[tuple] = None,
    custom_verifiers: Optional[List[tuple]] = None,
) -> CompositeVerifier:
    """
    Factory function to create a standard multi-layer verifier.

    Args:
        answer_verifier: (ExactMatchVerifier, weight, expected) or None
        state_verifier: (EnvironmentStateVerifier, weight, expected) or None
        tool_verifier: (ToolCallSequenceVerifier, weight, expected) or None
        custom_verifiers: List of (Verifier, weight, expected) tuples

    Returns:
        CompositeVerifier configured for multi-layer verification
    """
    verifiers = []

    # Always include execution layer
    verifiers.append((ExecutionLayerVerifier(), 0.1, None))

    if tool_verifier:
        verifiers.append(tool_verifier)

    if state_verifier:
        verifiers.append(state_verifier)

    if answer_verifier:
        verifiers.append(answer_verifier)

    # Add reasoning quality check
    verifiers.append((ReasoningQualityVerifier(), 0.1, None))

    if custom_verifiers:
        verifiers.extend(custom_verifiers)

    return CompositeVerifier(verifiers, mode="weighted", pass_threshold=0.6)
