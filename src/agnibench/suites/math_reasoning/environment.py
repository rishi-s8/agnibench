"""
Simulated environment for the math reasoning benchmark suite.
"""

from typing import Any, Dict

from agnibench.core.environment import SimulatedEnvironment
from agnibench.suites.math_reasoning.tools import reset_scratchpad


class MathEnvironment(SimulatedEnvironment):
    """
    Environment for math reasoning tasks.

    Manages scratchpad state and tracks calculation history.
    """

    def _setup_default_state(self) -> None:
        """Set up default state for math environment."""
        # Reset the scratchpad
        reset_scratchpad()

        # Initialize state tracking
        self._state["scratchpad"] = {}
        self._state["calculation_history"] = []
        self._state["formulas_looked_up"] = []
        self._state["conversions_performed"] = []
        self._state["equations_solved"] = []

    def reset(self) -> None:
        """Reset the environment."""
        super().reset()
        reset_scratchpad()

    def record_calculation(self, expression: str, result: Any) -> None:
        """Record a calculation in history."""
        history = self._state.get("calculation_history", [])
        history.append({"expression": expression, "result": result})
        self.set_state("calculation_history", history, source_tool="calculator")

    def record_formula_lookup(self, formula_name: str) -> None:
        """Record a formula lookup."""
        lookups = self._state.get("formulas_looked_up", [])
        lookups.append(formula_name)
        self.set_state("formulas_looked_up", lookups, source_tool="formula_lookup")

    def record_conversion(
        self, value: float, from_unit: str, to_unit: str, result: float
    ) -> None:
        """Record a unit conversion."""
        conversions = self._state.get("conversions_performed", [])
        conversions.append(
            {
                "value": value,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "result": result,
            }
        )
        self.set_state(
            "conversions_performed", conversions, source_tool="unit_converter"
        )

    def record_equation_solved(self, equation: str, solutions: list) -> None:
        """Record an equation solution."""
        solved = self._state.get("equations_solved", [])
        solved.append({"equation": equation, "solutions": solutions})
        self.set_state("equations_solved", solved, source_tool="equation_solver")

    def update_scratchpad(self, key: str, value: str) -> None:
        """Update scratchpad state tracking."""
        scratchpad = self._state.get("scratchpad", {})
        scratchpad[key] = value
        self.set_state("scratchpad", scratchpad, source_tool="scratchpad")

    def sync_state_from_math(self) -> None:
        """Sync environment state from tool calls."""
        calculation_history = []
        formulas_looked_up = []
        conversions_performed = []
        equations_solved = []
        scratchpad = {}

        def _as_dict(result: Any) -> Dict[str, Any]:
            if result is None:
                return {}
            if isinstance(result, dict):
                return result
            if hasattr(result, "model_dump"):
                return result.model_dump()
            if hasattr(result, "dict"):
                return result.dict()
            if hasattr(result, "__dict__"):
                return {
                    k: v for k, v in result.__dict__.items() if not k.startswith("_")
                }
            return {}

        for call in self.tool_call_log:
            tool = call.get("tool_name")
            args = call.get("arguments", {}) or {}
            data = _as_dict(call.get("result"))

            if tool == "calculator":
                expression = args.get("expression") or data.get("expression")
                result = data.get("result")
                calculation_history.append(
                    {"expression": expression, "result": result}
                )
            elif tool == "formula_lookup":
                formula_name = args.get("formula_name") or data.get("formula_name")
                if formula_name:
                    formulas_looked_up.append(formula_name)
            elif tool == "unit_converter":
                conversions_performed.append(
                    {
                        "value": args.get("value", data.get("original_value")),
                        "from_unit": args.get("from_unit", data.get("from_unit")),
                        "to_unit": args.get("to_unit", data.get("to_unit")),
                        "result": data.get("converted_value"),
                    }
                )
            elif tool == "equation_solver":
                equations_solved.append(
                    {
                        "equation": args.get("equation", data.get("equation")),
                        "solutions": data.get("solutions"),
                    }
                )
            elif tool == "scratchpad":
                operation = args.get("operation", data.get("operation"))
                if operation == "store":
                    key = args.get("key", data.get("key"))
                    value = args.get("value", data.get("value"))
                    if key is not None:
                        scratchpad[key] = value
                elif operation == "clear":
                    scratchpad = {}

        self._state["calculation_history"] = calculation_history
        self._state["formulas_looked_up"] = formulas_looked_up
        self._state["conversions_performed"] = conversions_performed
        self._state["equations_solved"] = equations_solved
        self._state["scratchpad"] = scratchpad

    @property
    def calculation_count(self) -> int:
        """Number of calculations performed."""
        return len(self._state.get("calculation_history", []))

    @property
    def last_result(self) -> Any:
        """Get the last calculation result."""
        history = self._state.get("calculation_history", [])
        if history:
            return history[-1]["result"]
        return None
