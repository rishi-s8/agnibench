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
