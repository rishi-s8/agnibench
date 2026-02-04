"""
Tools for the math reasoning benchmark suite.

Provides 5 tools for mathematical calculations and state management.
"""

import math
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from agentbuilder.Tools.base import Tool, Response


# Pydantic models for tool parameters

class CalculatorParams(BaseModel):
    """Parameters for the calculator tool."""
    expression: str = Field(
        description="Mathematical expression to evaluate. Supports +, -, *, /, ^, parentheses, and common functions like sqrt, sin, cos, log, abs."
    )


class UnitConverterParams(BaseModel):
    """Parameters for the unit converter tool."""
    value: float = Field(description="Numeric value to convert")
    from_unit: str = Field(description="Source unit (e.g., 'km', 'miles', 'kg', 'lbs', 'celsius', 'fahrenheit')")
    to_unit: str = Field(description="Target unit to convert to")


class FormulaLookupParams(BaseModel):
    """Parameters for the formula lookup tool."""
    formula_name: str = Field(
        description="Name of the formula to look up (e.g., 'area_circle', 'pythagorean', 'compound_interest', 'distance')"
    )


class EquationSolverParams(BaseModel):
    """Parameters for the equation solver tool."""
    equation: str = Field(
        description="Equation to solve (e.g., '2x + 5 = 15', 'x^2 - 4 = 0')"
    )
    variable: str = Field(
        default="x",
        description="Variable to solve for"
    )


class ScratchpadParams(BaseModel):
    """Parameters for the scratchpad tool."""
    operation: str = Field(
        description="Operation to perform: 'store', 'retrieve', 'list', or 'clear'"
    )
    key: Optional[str] = Field(
        default=None,
        description="Key for storing/retrieving values"
    )
    value: Optional[str] = Field(
        default=None,
        description="Value to store (for 'store' operation)"
    )


# Tool implementation functions

def calculator(params: CalculatorParams) -> Dict[str, Any]:
    """
    Evaluate a mathematical expression.

    Supports basic arithmetic, exponents, and common math functions.
    """
    expression = params.expression

    # Safety check - only allow math-related characters
    allowed_pattern = r'^[\d\s\+\-\*\/\^\(\)\.\,a-zA-Z_]+$'
    if not re.match(allowed_pattern, expression):
        return {"error": "Invalid characters in expression", "result": None}

    # Replace common notation
    expression = expression.replace('^', '**')

    # Create safe math environment
    safe_dict = {
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log,
        'log10': math.log10,
        'exp': math.exp,
        'abs': abs,
        'pow': pow,
        'pi': math.pi,
        'e': math.e,
        'floor': math.floor,
        'ceil': math.ceil,
        'round': round,
    }

    try:
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        # Round to reasonable precision
        if isinstance(result, float):
            result = round(result, 10)
        return {"result": result, "expression": params.expression}
    except Exception as e:
        return {"error": str(e), "result": None}


def unit_converter(params: UnitConverterParams) -> Dict[str, Any]:
    """
    Convert between different units.

    Supports length, weight, temperature, and time conversions.
    """
    conversions = {
        # Length (to meters)
        ('km', 'm'): lambda x: x * 1000,
        ('m', 'km'): lambda x: x / 1000,
        ('miles', 'km'): lambda x: x * 1.60934,
        ('km', 'miles'): lambda x: x / 1.60934,
        ('feet', 'm'): lambda x: x * 0.3048,
        ('m', 'feet'): lambda x: x / 0.3048,
        ('inches', 'cm'): lambda x: x * 2.54,
        ('cm', 'inches'): lambda x: x / 2.54,
        ('yards', 'm'): lambda x: x * 0.9144,
        ('m', 'yards'): lambda x: x / 0.9144,

        # Weight (to kg)
        ('kg', 'lbs'): lambda x: x * 2.20462,
        ('lbs', 'kg'): lambda x: x / 2.20462,
        ('g', 'kg'): lambda x: x / 1000,
        ('kg', 'g'): lambda x: x * 1000,
        ('oz', 'g'): lambda x: x * 28.3495,
        ('g', 'oz'): lambda x: x / 28.3495,

        # Temperature
        ('celsius', 'fahrenheit'): lambda x: (x * 9/5) + 32,
        ('fahrenheit', 'celsius'): lambda x: (x - 32) * 5/9,
        ('celsius', 'kelvin'): lambda x: x + 273.15,
        ('kelvin', 'celsius'): lambda x: x - 273.15,

        # Time
        ('hours', 'minutes'): lambda x: x * 60,
        ('minutes', 'hours'): lambda x: x / 60,
        ('days', 'hours'): lambda x: x * 24,
        ('hours', 'days'): lambda x: x / 24,
        ('seconds', 'minutes'): lambda x: x / 60,
        ('minutes', 'seconds'): lambda x: x * 60,

        # Area
        ('sqm', 'sqft'): lambda x: x * 10.7639,
        ('sqft', 'sqm'): lambda x: x / 10.7639,
        ('acres', 'sqm'): lambda x: x * 4046.86,
        ('sqm', 'acres'): lambda x: x / 4046.86,

        # Volume
        ('liters', 'gallons'): lambda x: x * 0.264172,
        ('gallons', 'liters'): lambda x: x / 0.264172,
        ('ml', 'liters'): lambda x: x / 1000,
        ('liters', 'ml'): lambda x: x * 1000,
    }

    from_unit = params.from_unit.lower()
    to_unit = params.to_unit.lower()

    # Same unit
    if from_unit == to_unit:
        return {
            "original_value": params.value,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "converted_value": params.value
        }

    key = (from_unit, to_unit)
    if key in conversions:
        converted = round(conversions[key](params.value), 6)
        return {
            "original_value": params.value,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "converted_value": converted
        }

    return {
        "error": f"Conversion from '{from_unit}' to '{to_unit}' not supported",
        "supported_conversions": list(conversions.keys())
    }


def formula_lookup(params: FormulaLookupParams) -> Dict[str, Any]:
    """
    Look up a mathematical formula by name.

    Returns the formula, its variables, and description.
    """
    formulas = {
        "area_circle": {
            "formula": "A = pi * r^2",
            "variables": {"A": "area", "r": "radius"},
            "description": "Area of a circle given radius",
            "example": "For r=5: A = pi * 5^2 = 78.54"
        },
        "area_rectangle": {
            "formula": "A = length * width",
            "variables": {"A": "area", "length": "length", "width": "width"},
            "description": "Area of a rectangle",
            "example": "For length=10, width=5: A = 10 * 5 = 50"
        },
        "area_triangle": {
            "formula": "A = (base * height) / 2",
            "variables": {"A": "area", "base": "base length", "height": "height"},
            "description": "Area of a triangle",
            "example": "For base=10, height=6: A = (10 * 6) / 2 = 30"
        },
        "pythagorean": {
            "formula": "c = sqrt(a^2 + b^2)",
            "variables": {"a": "first leg", "b": "second leg", "c": "hypotenuse"},
            "description": "Pythagorean theorem for right triangles",
            "example": "For a=3, b=4: c = sqrt(9 + 16) = 5"
        },
        "compound_interest": {
            "formula": "A = P * (1 + r/n)^(n*t)",
            "variables": {
                "A": "final amount",
                "P": "principal",
                "r": "annual interest rate (decimal)",
                "n": "compounds per year",
                "t": "time in years"
            },
            "description": "Compound interest formula",
            "example": "For P=1000, r=0.05, n=12, t=10: A = 1000 * (1 + 0.05/12)^(12*10) = 1647.01"
        },
        "simple_interest": {
            "formula": "I = P * r * t",
            "variables": {
                "I": "interest earned",
                "P": "principal",
                "r": "annual interest rate (decimal)",
                "t": "time in years"
            },
            "description": "Simple interest formula",
            "example": "For P=1000, r=0.05, t=3: I = 1000 * 0.05 * 3 = 150"
        },
        "distance": {
            "formula": "d = sqrt((x2-x1)^2 + (y2-y1)^2)",
            "variables": {
                "d": "distance",
                "x1,y1": "first point coordinates",
                "x2,y2": "second point coordinates"
            },
            "description": "Distance between two points in 2D",
            "example": "For (0,0) to (3,4): d = sqrt(9 + 16) = 5"
        },
        "quadratic": {
            "formula": "x = (-b +/- sqrt(b^2 - 4ac)) / (2a)",
            "variables": {"a": "x^2 coefficient", "b": "x coefficient", "c": "constant"},
            "description": "Quadratic formula for ax^2 + bx + c = 0",
            "example": "For x^2 - 5x + 6 = 0: x = (5 +/- sqrt(25-24)) / 2 = 2 or 3"
        },
        "circumference": {
            "formula": "C = 2 * pi * r",
            "variables": {"C": "circumference", "r": "radius"},
            "description": "Circumference of a circle",
            "example": "For r=10: C = 2 * pi * 10 = 62.83"
        },
        "volume_sphere": {
            "formula": "V = (4/3) * pi * r^3",
            "variables": {"V": "volume", "r": "radius"},
            "description": "Volume of a sphere",
            "example": "For r=3: V = (4/3) * pi * 27 = 113.1"
        },
        "percentage": {
            "formula": "percentage = (part / whole) * 100",
            "variables": {"part": "the portion", "whole": "the total"},
            "description": "Calculate percentage",
            "example": "For part=25, whole=200: percentage = (25/200) * 100 = 12.5%"
        },
        "speed": {
            "formula": "speed = distance / time",
            "variables": {"speed": "velocity", "distance": "distance traveled", "time": "time taken"},
            "description": "Calculate speed from distance and time",
            "example": "For distance=100km, time=2hours: speed = 100/2 = 50 km/h"
        },
    }

    name = params.formula_name.lower().replace(" ", "_")

    if name in formulas:
        return {
            "formula_name": name,
            **formulas[name]
        }

    # Try partial match
    matches = [k for k in formulas.keys() if name in k or k in name]
    if matches:
        return {
            "error": f"Formula '{params.formula_name}' not found. Did you mean one of these?",
            "suggestions": matches
        }

    return {
        "error": f"Formula '{params.formula_name}' not found",
        "available_formulas": list(formulas.keys())
    }


def equation_solver(params: EquationSolverParams) -> Dict[str, Any]:
    """
    Solve simple algebraic equations.

    Supports linear and simple quadratic equations.
    """
    equation = params.equation.replace(" ", "")
    var = params.variable

    try:
        # Split by equals sign
        if "=" not in equation:
            return {"error": "Equation must contain '='", "solutions": None}

        left, right = equation.split("=")

        # Try to solve linear equation: ax + b = c
        # Move everything to left side: ax + b - c = 0

        # For simple cases like "2x + 5 = 15"
        # Parse coefficient of x and constant

        # Remove the variable to find coefficient
        import re

        # Pattern for linear: ax + b = c or ax - b = c
        linear_pattern = rf'(-?\d*\.?\d*){var}\s*([\+\-])\s*(\d+\.?\d*)\s*=\s*(-?\d+\.?\d*)'
        match = re.match(linear_pattern, equation)

        if match:
            coef = float(match.group(1)) if match.group(1) not in ['', '-'] else (1 if match.group(1) == '' else -1)
            sign = 1 if match.group(2) == '+' else -1
            const = float(match.group(3)) * sign
            rhs = float(match.group(4))

            # ax + const = rhs => x = (rhs - const) / a
            solution = (rhs - const) / coef
            return {
                "equation": params.equation,
                "variable": var,
                "solutions": [round(solution, 6)],
                "steps": [
                    f"Original: {coef}{var} + {const} = {rhs}",
                    f"Subtract {const}: {coef}{var} = {rhs - const}",
                    f"Divide by {coef}: {var} = {solution}"
                ]
            }

        # Simple form: ax = b
        simple_pattern = rf'(-?\d*\.?\d*){var}\s*=\s*(-?\d+\.?\d*)'
        match = re.match(simple_pattern, equation)
        if match:
            coef = float(match.group(1)) if match.group(1) not in ['', '-'] else (1 if match.group(1) == '' else -1)
            rhs = float(match.group(2))
            solution = rhs / coef
            return {
                "equation": params.equation,
                "variable": var,
                "solutions": [round(solution, 6)]
            }

        # Quadratic: ax^2 + bx + c = 0
        quad_pattern = rf'(-?\d*\.?\d*){var}\^2\s*([\+\-])\s*(\d*\.?\d*){var}\s*([\+\-])\s*(\d+\.?\d*)\s*=\s*0'
        match = re.match(quad_pattern, equation)
        if match:
            a = float(match.group(1)) if match.group(1) not in ['', '-'] else (1 if match.group(1) == '' else -1)
            b_sign = 1 if match.group(2) == '+' else -1
            b = float(match.group(3)) * b_sign if match.group(3) else b_sign
            c_sign = 1 if match.group(4) == '+' else -1
            c = float(match.group(5)) * c_sign

            discriminant = b**2 - 4*a*c
            if discriminant < 0:
                return {
                    "equation": params.equation,
                    "variable": var,
                    "solutions": [],
                    "note": "No real solutions (discriminant < 0)"
                }
            elif discriminant == 0:
                x = -b / (2*a)
                return {
                    "equation": params.equation,
                    "variable": var,
                    "solutions": [round(x, 6)]
                }
            else:
                x1 = (-b + math.sqrt(discriminant)) / (2*a)
                x2 = (-b - math.sqrt(discriminant)) / (2*a)
                return {
                    "equation": params.equation,
                    "variable": var,
                    "solutions": [round(x1, 6), round(x2, 6)]
                }

        return {
            "error": "Could not parse equation. Supported formats: 'ax + b = c', 'ax^2 + bx + c = 0'",
            "equation": params.equation
        }

    except Exception as e:
        return {"error": str(e), "solutions": None}


# Global scratchpad storage (reset per environment)
_scratchpad: Dict[str, str] = {}


def scratchpad(params: ScratchpadParams) -> Dict[str, Any]:
    """
    Store and retrieve intermediate values.

    Useful for multi-step calculations where intermediate results need to be tracked.
    """
    global _scratchpad

    operation = params.operation.lower()

    if operation == "store":
        if not params.key:
            return {"error": "Key is required for store operation"}
        if params.value is None:
            return {"error": "Value is required for store operation"}
        _scratchpad[params.key] = params.value
        return {
            "operation": "store",
            "key": params.key,
            "value": params.value,
            "success": True
        }

    elif operation == "retrieve":
        if not params.key:
            return {"error": "Key is required for retrieve operation"}
        if params.key in _scratchpad:
            return {
                "operation": "retrieve",
                "key": params.key,
                "value": _scratchpad[params.key],
                "found": True
            }
        else:
            return {
                "operation": "retrieve",
                "key": params.key,
                "found": False,
                "available_keys": list(_scratchpad.keys())
            }

    elif operation == "list":
        return {
            "operation": "list",
            "entries": dict(_scratchpad),
            "count": len(_scratchpad)
        }

    elif operation == "clear":
        count = len(_scratchpad)
        _scratchpad.clear()
        return {
            "operation": "clear",
            "cleared_count": count,
            "success": True
        }

    else:
        return {
            "error": f"Unknown operation: {operation}",
            "valid_operations": ["store", "retrieve", "list", "clear"]
        }


def reset_scratchpad():
    """Reset the scratchpad (called by environment)."""
    global _scratchpad
    _scratchpad.clear()


# Tool creation using the existing Tool class

def get_math_tools() -> List[Tool]:
    """Get all math reasoning tools."""
    return [
        Tool(
            name="calculator",
            description="Evaluate mathematical expressions. Supports +, -, *, /, ^ (power), parentheses, and functions like sqrt, sin, cos, log, abs, floor, ceil, round. Constants: pi, e.",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '2 + 3 * 4', 'sqrt(16)', 'sin(pi/2)')"
                    }
                },
                "required": ["expression"]
            },
            function=lambda **kwargs: calculator(CalculatorParams(**kwargs))
        ),
        Tool(
            name="unit_converter",
            description="Convert between different units. Supports length (km, miles, m, feet, inches, cm), weight (kg, lbs, g, oz), temperature (celsius, fahrenheit, kelvin), time (hours, minutes, seconds, days), area (sqm, sqft, acres), and volume (liters, gallons, ml).",
            parameters={
                "type": "object",
                "properties": {
                    "value": {
                        "type": "number",
                        "description": "Numeric value to convert"
                    },
                    "from_unit": {
                        "type": "string",
                        "description": "Source unit (e.g., 'km', 'miles', 'celsius')"
                    },
                    "to_unit": {
                        "type": "string",
                        "description": "Target unit to convert to"
                    }
                },
                "required": ["value", "from_unit", "to_unit"]
            },
            function=lambda **kwargs: unit_converter(UnitConverterParams(**kwargs))
        ),
        Tool(
            name="formula_lookup",
            description="Look up mathematical formulas by name. Available: area_circle, area_rectangle, area_triangle, pythagorean, compound_interest, simple_interest, distance, quadratic, circumference, volume_sphere, percentage, speed.",
            parameters={
                "type": "object",
                "properties": {
                    "formula_name": {
                        "type": "string",
                        "description": "Name of the formula (e.g., 'pythagorean', 'compound_interest')"
                    }
                },
                "required": ["formula_name"]
            },
            function=lambda **kwargs: formula_lookup(FormulaLookupParams(**kwargs))
        ),
        Tool(
            name="equation_solver",
            description="Solve algebraic equations. Supports linear equations (ax + b = c) and quadratic equations (ax^2 + bx + c = 0).",
            parameters={
                "type": "object",
                "properties": {
                    "equation": {
                        "type": "string",
                        "description": "Equation to solve (e.g., '2x + 5 = 15', 'x^2 - 5x + 6 = 0')"
                    },
                    "variable": {
                        "type": "string",
                        "description": "Variable to solve for (default: 'x')",
                        "default": "x"
                    }
                },
                "required": ["equation"]
            },
            function=lambda **kwargs: equation_solver(EquationSolverParams(**kwargs))
        ),
        Tool(
            name="scratchpad",
            description="Store and retrieve intermediate calculation values. Operations: 'store' (save a value), 'retrieve' (get a value), 'list' (show all stored values), 'clear' (remove all values).",
            parameters={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["store", "retrieve", "list", "clear"],
                        "description": "Operation to perform"
                    },
                    "key": {
                        "type": "string",
                        "description": "Key for storing/retrieving (required for store/retrieve)"
                    },
                    "value": {
                        "type": "string",
                        "description": "Value to store (required for store operation)"
                    }
                },
                "required": ["operation"]
            },
            function=lambda **kwargs: scratchpad(ScratchpadParams(**kwargs))
        ),
    ]
