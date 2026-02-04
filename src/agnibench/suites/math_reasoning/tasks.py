"""
Tasks for the math reasoning benchmark suite.

Contains 15 tasks distributed across difficulty levels and information flows.
"""

from typing import List
from agnibench.core.abstractions import (
    Task,
    TaskCharacteristics,
    DifficultyLevel,
    InformationFlow,
)


def get_math_tasks() -> List[Task]:
    """Get all math reasoning tasks."""
    tasks = []

    # ============================================================================
    # SIMPLE TASKS (4 tasks, 2-3 tool calls)
    # ============================================================================

    tasks.append(Task(
        id="math_simple_01",
        name="Basic Percentage Calculation",
        prompt="Calculate 15% of $250 and add $30 shipping. What is the total?",
        difficulty=DifficultyLevel.SIMPLE,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
        ),
        expected_tool_calls=["calculator", "calculator"],
        expected_answer=67.5,
        verifier_config={
            "answer": 67.5,
            "match_mode": "contains",
            "tools": {
                "required": ["calculator"],
                "min_calls": 1,
                "max_calls": 3
            }
        },
        description="Simple two-step arithmetic",
        min_tool_calls=1,
        max_tool_calls=3,
        tags=["arithmetic", "percentage"],
    ))

    tasks.append(Task(
        id="math_simple_02",
        name="Unit Conversion",
        prompt="Convert 100 kilometers to miles.",
        difficulty=DifficultyLevel.SIMPLE,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
        ),
        expected_tool_calls=["unit_converter"],
        expected_answer=62.137,
        verifier_config={
            "answer": [62.137, 62.14, "62.1"],
            "match_mode": "contains",
            "tools": {
                "required": ["unit_converter"],
                "min_calls": 1,
                "max_calls": 2
            }
        },
        description="Single unit conversion",
        min_tool_calls=1,
        max_tool_calls=2,
        tags=["conversion", "length"],
    ))

    tasks.append(Task(
        id="math_simple_03",
        name="Circle Area Calculation",
        prompt="What is the area of a circle with radius 7 cm?",
        difficulty=DifficultyLevel.SIMPLE,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["formula_lookup", "calculator"],
        expected_answer=153.94,
        verifier_config={
            "answer": [153.94, 153.9, "153.9", "154"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator"],
                "optional": ["formula_lookup"],
                "min_calls": 1,
                "max_calls": 3
            }
        },
        description="Formula lookup and calculation",
        min_tool_calls=1,
        max_tool_calls=3,
        tags=["geometry", "formula"],
    ))

    tasks.append(Task(
        id="math_simple_04",
        name="Simple Equation",
        prompt="Solve for x: 3x + 12 = 27",
        difficulty=DifficultyLevel.SIMPLE,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
        ),
        expected_tool_calls=["equation_solver"],
        expected_answer=5,
        verifier_config={
            "answer": [5, "5", "x = 5"],
            "match_mode": "contains",
            "tools": {
                "required": ["equation_solver"],
                "min_calls": 1,
                "max_calls": 2
            }
        },
        description="Linear equation solving",
        min_tool_calls=1,
        max_tool_calls=2,
        tags=["algebra", "equation"],
    ))

    # ============================================================================
    # MEDIUM TASKS (5 tasks, 4-6 tool calls)
    # ============================================================================

    tasks.append(Task(
        id="math_medium_01",
        name="Multi-step Word Problem",
        prompt="A rectangular garden is 15 meters long and 8 meters wide. Calculate its area and perimeter, then convert both to square feet and feet respectively.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["calculator", "calculator", "unit_converter", "unit_converter"],
        expected_answer={"area_sqft": 1291.67, "perimeter_ft": 150.92},
        verifier_config={
            "answer": ["1291", "1292", "150.9", "151"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator", "unit_converter"],
                "min_calls": 3,
                "max_calls": 6
            }
        },
        description="Geometry with unit conversion",
        min_tool_calls=3,
        max_tool_calls=6,
        tags=["geometry", "conversion", "multi-step"],
    ))

    tasks.append(Task(
        id="math_medium_02",
        name="Compound Interest Calculation",
        prompt="Calculate the final amount if $5000 is invested at 6% annual interest, compounded monthly, for 3 years. Use the compound interest formula.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["formula_lookup", "calculator"],
        expected_answer=5983.40,
        verifier_config={
            "answer": [5983, "5983.4", "5983.40", "$5,983"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator"],
                "optional": ["formula_lookup"],
                "min_calls": 2,
                "max_calls": 5
            }
        },
        description="Financial calculation with formula",
        min_tool_calls=2,
        max_tool_calls=5,
        tags=["finance", "formula", "compound"],
    ))

    tasks.append(Task(
        id="math_medium_03",
        name="Pythagorean with Conversion",
        prompt="A right triangle has legs of 5 feet and 12 feet. Find the hypotenuse and convert it to meters.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["formula_lookup", "calculator", "unit_converter"],
        expected_answer=3.96,
        verifier_config={
            "answer": [3.96, "3.96", "3.962", "13 feet", "3.9"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator", "unit_converter"],
                "min_calls": 2,
                "max_calls": 5
            }
        },
        description="Geometry with unit conversion",
        min_tool_calls=2,
        max_tool_calls=5,
        tags=["geometry", "pythagorean", "conversion"],
    ))

    tasks.append(Task(
        id="math_medium_04",
        name="Temperature Chain Conversion",
        prompt="Convert 98.6 degrees Fahrenheit to Celsius, then to Kelvin.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["unit_converter", "unit_converter"],
        expected_answer=310.15,
        verifier_config={
            "answer": [310.15, "310.15", "37", "37°C", "310 K"],
            "match_mode": "contains",
            "tools": {
                "required": ["unit_converter"],
                "min_calls": 2,
                "max_calls": 4
            }
        },
        description="Chain conversions",
        min_tool_calls=2,
        max_tool_calls=4,
        tags=["conversion", "temperature", "chain"],
    ))

    tasks.append(Task(
        id="math_medium_05",
        name="Quadratic Equation",
        prompt="Solve the quadratic equation x^2 - 7x + 12 = 0 and verify both solutions by substituting back.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["equation_solver", "calculator", "calculator"],
        expected_answer=[3, 4],
        verifier_config={
            "answer": ["3", "4", "x = 3", "x = 4"],
            "match_mode": "contains",
            "tools": {
                "required": ["equation_solver"],
                "optional": ["calculator"],
                "min_calls": 1,
                "max_calls": 5
            }
        },
        description="Quadratic solving with verification",
        min_tool_calls=1,
        max_tool_calls=5,
        tags=["algebra", "quadratic", "verification"],
    ))

    # ============================================================================
    # HARD TASKS (4 tasks, 7-10 tool calls)
    # ============================================================================

    tasks.append(Task(
        id="math_hard_01",
        name="Investment Comparison",
        prompt="""Compare two investment options over 5 years:
        Option A: $10,000 at 5% simple interest
        Option B: $10,000 at 4.5% compounded quarterly

        Which option yields more money at the end? By how much?""",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_state_tracking=True,
            requires_cross_reference=True,
        ),
        expected_tool_calls=["formula_lookup", "calculator", "formula_lookup", "calculator", "calculator"],
        expected_answer="Option B",
        verifier_config={
            "answer": ["Option B", "B", "compounded", "12511", "12500"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator"],
                "optional": ["formula_lookup", "scratchpad"],
                "min_calls": 4,
                "max_calls": 10
            }
        },
        description="Financial comparison requiring multiple calculations",
        min_tool_calls=4,
        max_tool_calls=10,
        tags=["finance", "comparison", "multi-step"],
    ))

    tasks.append(Task(
        id="math_hard_02",
        name="Construction Material Calculation",
        prompt="""A circular swimming pool has a diameter of 24 feet and needs to be surrounded by a 4-foot wide walkway.
        Calculate:
        1. The area of just the walkway (not including the pool)
        2. If paving stones cost $15 per square foot, what's the total cost?
        3. Convert the walkway area to square meters.""",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_state_tracking=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["formula_lookup", "calculator", "calculator", "calculator", "calculator", "unit_converter"],
        expected_answer={"walkway_area": 351.86, "cost": 5277.88},
        verifier_config={
            "answer": ["351", "352", "5277", "5278", "32.7", "33"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator", "unit_converter"],
                "optional": ["formula_lookup", "scratchpad"],
                "min_calls": 4,
                "max_calls": 10
            }
        },
        description="Multi-step geometry problem",
        min_tool_calls=4,
        max_tool_calls=10,
        tags=["geometry", "area", "cost", "conversion"],
    ))

    tasks.append(Task(
        id="math_hard_03",
        name="Travel Time and Distance",
        prompt="""A car travels from City A to City B at 60 mph, and returns at 40 mph.
        The total journey (round trip) takes 5 hours.
        1. What is the distance between the cities?
        2. What was the average speed for the entire trip?
        3. Convert the distance to kilometers.""",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
            requires_state_tracking=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["equation_solver", "calculator", "calculator", "unit_converter"],
        expected_answer={"distance": 120, "avg_speed": 48},
        verifier_config={
            "answer": ["120", "48 mph", "193", "48"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator"],
                "optional": ["equation_solver", "unit_converter", "scratchpad"],
                "min_calls": 3,
                "max_calls": 10
            }
        },
        description="Classic rate-time-distance problem",
        min_tool_calls=3,
        max_tool_calls=10,
        tags=["physics", "rate", "distance", "algebra"],
    ))

    tasks.append(Task(
        id="math_hard_04",
        name="Mixed Unit Problem",
        prompt="""A recipe calls for:
        - 2.5 cups of flour (1 cup = 120g)
        - 1.5 liters of milk
        - 500g of sugar

        Calculate the total weight of ingredients in both kilograms and pounds.
        Store intermediate results for verification.""",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
            requires_state_tracking=True,
            requires_multi_constraint=True,
        ),
        expected_tool_calls=["calculator", "calculator", "calculator", "unit_converter", "scratchpad"],
        expected_answer={"kg": 2.3, "lbs": 5.07},
        verifier_config={
            "answer": ["2.3", "2.30", "5.07", "5.1"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator", "unit_converter"],
                "optional": ["scratchpad"],
                "min_calls": 4,
                "max_calls": 10
            }
        },
        description="Unit conversion with multiple ingredients",
        min_tool_calls=4,
        max_tool_calls=10,
        tags=["conversion", "aggregation", "recipe"],
    ))

    # ============================================================================
    # EXPERT TASKS (2 tasks, 11+ tool calls)
    # ============================================================================

    tasks.append(Task(
        id="math_expert_01",
        name="Optimization Problem",
        prompt="""A farmer wants to fence a rectangular field using 200 meters of fencing.
        One side borders a river (no fence needed).

        1. Find the dimensions that maximize the area
        2. Calculate the maximum area in square meters and acres
        3. If the farmer can also use the field for a circular pond (using the shorter dimension as diameter),
           what would be the pond's area in square meters?
        4. What percentage of the rectangular field would the pond occupy?

        Store all intermediate results in the scratchpad.""",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_state_tracking=True,
            requires_long_reasoning_chain=True,
            requires_multi_constraint=True,
        ),
        expected_tool_calls=["calculator"] * 6 + ["unit_converter", "formula_lookup", "calculator", "calculator", "scratchpad"],
        expected_answer={"dimensions": [100, 50], "max_area": 5000, "pond_percentage": 39.27},
        verifier_config={
            "answer": ["5000", "100", "50", "1.236", "1963", "39.2", "39.27"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator", "unit_converter"],
                "optional": ["formula_lookup", "scratchpad"],
                "min_calls": 8,
                "max_calls": 15
            }
        },
        description="Multi-part optimization requiring many steps",
        min_tool_calls=8,
        max_tool_calls=15,
        tags=["optimization", "geometry", "multi-part"],
    ))

    tasks.append(Task(
        id="math_expert_02",
        name="Financial Planning Scenario",
        prompt="""A person is planning their retirement with the following:

        1. Current savings: $50,000
        2. Monthly contribution: $500
        3. Expected return: 7% annually, compounded monthly
        4. Time until retirement: 25 years

        Calculate:
        a) Final value of current savings with compound interest
        b) Future value of monthly contributions (use formula: FV = PMT × (((1 + r)^n - 1) / r))
        c) Total retirement fund
        d) Convert total to Euros (assume 1 USD = 0.92 EUR)
        e) If inflation averages 3% annually, what's the purchasing power in today's dollars?

        Use the scratchpad to track all intermediate values.""",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.PROMPT_FULL,  # FIXED: All data and control flow is in the prompt
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,  # FIXED: Explicit a-e steps with formulas provided
            control_flow_from_tools=False,
            data_flow_from_prompt=True,  # All input values are in the prompt
            data_flow_from_tools=False,
            requires_state_tracking=True,
            requires_long_reasoning_chain=True,
            requires_multi_constraint=True,
        ),
        expected_tool_calls=["formula_lookup", "calculator"] * 5 + ["scratchpad"] * 3,
        expected_answer={"total": 688025, "purchasing_power": 328615},
        verifier_config={
            "answer": ["688", "271", "416", "633", "328"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator"],
                "optional": ["formula_lookup", "scratchpad", "unit_converter"],
                "min_calls": 8,
                "max_calls": 20
            }
        },
        description="Complex financial planning with multiple components",
        min_tool_calls=8,
        max_tool_calls=20,
        tags=["finance", "retirement", "multi-part", "inflation"],
    ))

    # ============================================================================
    # TRUE TOOL-DRIVEN CONTROL FLOW TASKS
    # These tasks require discovering what to do from tool responses
    # ============================================================================

    tasks.append(Task(
        id="math_discovery_01",
        name="Formula-Dependent Calculation",
        prompt="Calculate the surface area of a shape that has a radius of 5 and height of 10. Use the formula lookup to determine the correct formula.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Formula lookup result determines calculation approach
            data_flow_from_tools=True,
            requires_conditional_logic=True,  # Different shapes = different formulas
        ),
        expected_tool_calls=["formula_lookup", "calculator"],  # Formula determines calculation
        expected_answer=["surface area", "471", "formula"],
        verifier_config={
            "answer": ["471", "surface", "area"],
            "match_mode": "contains",
            "tools": {
                "required": ["formula_lookup", "calculator"],
                "min_calls": 2,
                "max_calls": 6
            }
        },
        description="TRUE tool-driven: formula lookup determines calculation method",
        min_tool_calls=2,
        max_tool_calls=6,
        tags=["discovery", "formula", "geometry"],
    ))

    tasks.append(Task(
        id="math_discovery_02",
        name="Equation Type Detection",
        prompt="Solve this equation and verify: x^2 + 6x + k = 0 where k is stored in the scratchpad under key 'k_value'.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: k value determines if equation has real solutions
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["scratchpad", "equation_solver"],  # k value changes solution approach
        expected_answer=["solution", "x =", "verified"],
        verifier_config={
            "answer": ["x", "solution", "equation"],
            "match_mode": "contains",
            "tools": {
                "required": ["scratchpad", "equation_solver"],
                "optional": ["calculator"],
                "min_calls": 2,
                "max_calls": 6
            }
        },
        description="TRUE tool-driven: retrieved value determines equation solvability",
        min_tool_calls=2,
        max_tool_calls=6,
        tags=["discovery", "equation", "conditional"],
    ))

    tasks.append(Task(
        id="math_discovery_03",
        name="Unit-Dependent Calculation",
        prompt="I have a measurement of 50 stored in the scratchpad under 'measurement'. First retrieve it, determine what unit it's in, convert it appropriately, and calculate the area of a square with that side length.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Unit type determines conversion path
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["scratchpad"],  # Retrieved data determines conversion
        expected_answer=["area", "square", "units"],
        verifier_config={
            "answer": ["area", "square"],
            "match_mode": "contains",
            "tools": {
                "required": ["scratchpad", "calculator"],
                "optional": ["unit_converter"],
                "min_calls": 2,
                "max_calls": 6
            }
        },
        description="TRUE tool-driven: retrieved unit type determines conversion approach",
        min_tool_calls=2,
        max_tool_calls=6,
        tags=["discovery", "units", "conditional"],
    ))

    tasks.append(Task(
        id="math_discovery_04",
        name="Iterative Optimization",
        prompt="Find the value of x that minimizes f(x) = x^2 - 4x + 5. Start with an initial guess and iteratively improve until you find the minimum.",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Each calculation result determines if more iterations needed
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_state_tracking=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["calculator"],  # Multiple iterations
        expected_answer=["x = 2", "minimum", "1"],
        verifier_config={
            "answer": ["2", "minimum", "x"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator"],
                "optional": ["scratchpad", "equation_solver"],
                "min_calls": 2,
                "max_calls": 10
            }
        },
        description="TRUE tool-driven: calculation results determine iteration continuation",
        min_tool_calls=2,
        max_tool_calls=10,
        tags=["discovery", "optimization", "iterative"],
    ))

    tasks.append(Task(
        id="math_discovery_05",
        name="Error-Handling Calculation",
        prompt="Try to calculate the square root of the value stored in scratchpad under 'input_value'. If it's negative, calculate its absolute value first. Then convert the result from meters to feet.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Input value sign determines if absolute value step is needed
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_error_recovery=True,
        ),
        expected_tool_calls=["scratchpad", "calculator"],  # Value determines if abs() needed
        expected_answer=["square root", "feet", "converted"],
        verifier_config={
            "answer": ["root", "feet", "result"],
            "match_mode": "contains",
            "tools": {
                "required": ["scratchpad", "calculator", "unit_converter"],
                "min_calls": 3,
                "max_calls": 6
            }
        },
        description="TRUE tool-driven: input sign determines error-handling path",
        min_tool_calls=3,
        max_tool_calls=6,
        tags=["discovery", "error-handling", "conditional"],
    ))

    # ============================================================================
    # GSM8K/MATH-INSPIRED TASKS
    # Multi-step problems that test context maintenance and reasoning chains
    # These specifically target capabilities where LLMs excel but SLMs struggle
    # ============================================================================

    # --- MEDIUM: Multi-step word problems requiring state tracking ---

    tasks.append(Task(
        id="math_gsm_01",
        name="Shopping Cart Calculation",
        prompt="""Sarah is buying supplies for a party. She buys:
- 3 packs of plates at $4.50 each
- 2 packs of cups at $3.25 each
- 5 bags of balloons at $2.00 each

She has a 15% off coupon for her entire purchase. If she pays with a $50 bill, how much change will she receive?

Use the scratchpad to track intermediate calculations.""",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
            requires_state_tracking=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["calculator"] * 5 + ["scratchpad"],
        expected_answer=["$20.49", "20.49", "change"],
        verifier_config={
            "answer": ["20.49", "change"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator"],
                "optional": ["scratchpad"],
                "min_calls": 4,
                "max_calls": 10
            }
        },
        description="GSM8K-style: 5-step calculation with discount and change",
        min_tool_calls=4,
        max_tool_calls=10,
        tags=["gsm8k", "shopping", "multi-step", "state-tracking"],
    ))

    tasks.append(Task(
        id="math_gsm_02",
        name="Work Rate Problem",
        prompt="""Alice can paint a room in 6 hours. Bob can paint the same room in 4 hours.
If they work together for 2 hours, then Alice leaves and Bob finishes alone, how many total hours does it take to complete the room?

Hint: Combined work rate = sum of individual rates. Use the scratchpad to track partial completion.""",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
            requires_state_tracking=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["calculator"] * 4 + ["scratchpad"] * 2,
        expected_answer=["2.8", "2 hours 48 minutes", "total"],
        verifier_config={
            "answer": ["2.8", "hours"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator"],
                "optional": ["scratchpad"],
                "min_calls": 3,
                "max_calls": 10
            }
        },
        description="GSM8K-style: Work rate problem with partial completion tracking",
        min_tool_calls=3,
        max_tool_calls=10,
        tags=["gsm8k", "work-rate", "multi-step"],
    ))

    tasks.append(Task(
        id="math_gsm_03",
        name="Profit Margin Chain",
        prompt="""A manufacturer sells a product to a wholesaler at 20% profit.
The wholesaler sells it to a retailer at 15% profit.
The retailer sells it to a customer for $207.

What was the manufacturer's original cost?

Work backwards through the profit chain, storing each intermediate price.""",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
            requires_state_tracking=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["calculator"] * 3 + ["scratchpad"] * 2,
        expected_answer=["150", "$150", "original cost"],
        verifier_config={
            "answer": ["150", "cost"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator"],
                "optional": ["scratchpad"],
                "min_calls": 2,
                "max_calls": 8
            }
        },
        description="GSM8K-style: Reverse percentage chain calculation",
        min_tool_calls=2,
        max_tool_calls=8,
        tags=["gsm8k", "profit", "reverse-calculation"],
    ))

    # --- HARD: Problems requiring implicit constraint handling ---

    tasks.append(Task(
        id="math_gsm_04",
        name="Meeting Time Problem",
        prompt="""Train A leaves Station X at 9:00 AM traveling east at 60 mph.
Train B leaves Station Y (which is 300 miles east of X) at 10:00 AM traveling west at 40 mph.

At what time will the trains meet? Also calculate how far from Station X they will meet.

Store the key values and track the positions over time.""",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
            requires_state_tracking=True,
            requires_long_reasoning_chain=True,
            requires_multi_constraint=True,
        ),
        expected_tool_calls=["calculator"] * 4 + ["scratchpad"] * 2,
        expected_answer=["12:24", "12:24 PM", "204 miles"],
        verifier_config={
            "answer": ["12:24", "204"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator"],
                "optional": ["scratchpad", "equation_solver"],
                "min_calls": 3,
                "max_calls": 10
            }
        },
        description="Classic train problem with time offset constraint",
        min_tool_calls=3,
        max_tool_calls=10,
        tags=["gsm8k", "distance-rate-time", "constraint"],
    ))

    tasks.append(Task(
        id="math_gsm_05",
        name="Age Word Problem",
        prompt="""Three years ago, Tom was twice as old as Jerry.
In 5 years, Tom will be 1.5 times as old as Jerry.

How old are Tom and Jerry now?

Set up equations and solve systematically.""",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
            requires_state_tracking=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["equation_solver", "calculator"],
        expected_answer=["Tom is 19", "Jerry is 11", "19", "11"],
        verifier_config={
            "answer": ["19", "11"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator"],
                "optional": ["equation_solver", "scratchpad"],
                "min_calls": 2,
                "max_calls": 8
            }
        },
        description="System of equations from age relationships",
        min_tool_calls=2,
        max_tool_calls=8,
        tags=["gsm8k", "algebra", "system-of-equations"],
    ))

    # --- EXPERT: Complex multi-step with unit conversions ---

    tasks.append(Task(
        id="math_gsm_06",
        name="International Shipping Cost",
        prompt="""A company ships packages internationally with the following rates:
- Base fee: $25
- Weight charge: $3.50 per kg for first 10 kg, $2.75 per kg after that
- Volume charge: $0.005 per cubic cm if package exceeds 20,000 cubic cm

A package weighs 35 lbs and measures 18 inches × 14 inches × 12 inches.

Calculate the total shipping cost. Convert units as needed:
- 1 kg = 2.205 lbs
- 1 inch = 2.54 cm

Track all intermediate values in the scratchpad.""",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_state_tracking=True,
            requires_long_reasoning_chain=True,
            requires_multi_constraint=True,
        ),
        expected_tool_calls=["unit_converter"] * 3 + ["calculator"] * 5 + ["scratchpad"] * 3,
        expected_answer=["$112.42", "112.42", "total"],
        verifier_config={
            "answer": ["112", "shipping", "cost"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator", "unit_converter"],
                "optional": ["scratchpad"],
                "min_calls": 6,
                "max_calls": 15
            }
        },
        description="Complex tiered pricing with unit conversions",
        min_tool_calls=6,
        max_tool_calls=15,
        tags=["gsm8k", "shipping", "tiered-pricing", "unit-conversion"],
    ))

    tasks.append(Task(
        id="math_gsm_07",
        name="Investment Portfolio Rebalancing",
        prompt="""An investor has a portfolio worth $100,000 with the following allocation:
- Stocks: 60%
- Bonds: 30%
- Cash: 10%

After market changes:
- Stocks gained 12%
- Bonds lost 3%
- Cash stayed the same

Calculate:
1. The new total portfolio value
2. The new percentage allocation (before rebalancing)
3. How much needs to be moved from stocks to bonds to restore the original 60/30/10 allocation

Use the scratchpad to track all values.""",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
            requires_state_tracking=True,
            requires_long_reasoning_chain=True,
            requires_multi_constraint=True,
        ),
        expected_tool_calls=["calculator"] * 8 + ["scratchpad"] * 4,
        expected_answer=["$106,310", "106310", "$5,676", "5676"],
        verifier_config={
            "answer": ["106310", "106,310", "rebalance"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator"],
                "optional": ["scratchpad"],
                "min_calls": 6,
                "max_calls": 15
            }
        },
        description="Multi-step portfolio calculation with rebalancing",
        min_tool_calls=6,
        max_tool_calls=15,
        tags=["gsm8k", "finance", "portfolio", "multi-step"],
    ))

    # --- EXPERT: MATH competition-style problems ---

    tasks.append(Task(
        id="math_competition_01",
        name="Number Theory: Divisibility",
        prompt="""Find the smallest positive integer n such that:
- n leaves a remainder of 2 when divided by 3
- n leaves a remainder of 3 when divided by 5
- n leaves a remainder of 2 when divided by 7

Use systematic checking or the Chinese Remainder Theorem approach.""",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
            requires_state_tracking=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["calculator"] * 6,
        expected_answer=["23", "n = 23"],
        verifier_config={
            "answer": ["23"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator"],
                "optional": ["scratchpad"],
                "min_calls": 3,
                "max_calls": 15
            }
        },
        description="MATH competition: Chinese Remainder Theorem",
        min_tool_calls=3,
        max_tool_calls=15,
        tags=["math-competition", "number-theory", "modular-arithmetic"],
    ))

    tasks.append(Task(
        id="math_competition_02",
        name="Geometry: Inscribed Shapes",
        prompt="""A circle is inscribed in a square with side length 10 cm.
A smaller square is inscribed in that circle (with vertices touching the circle).

Calculate:
1. The radius of the circle
2. The side length of the inner square
3. The area between the inner square and the circle
4. Convert the final area to square inches

Store intermediate results and verify your answer makes sense.""",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_state_tracking=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["formula_lookup", "calculator"] * 4 + ["unit_converter", "scratchpad"] * 2,
        expected_answer=["28.54", "4.42", "area"],
        verifier_config={
            "answer": ["28.5", "area", "square"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator", "unit_converter"],
                "optional": ["formula_lookup", "scratchpad"],
                "min_calls": 5,
                "max_calls": 15
            }
        },
        description="MATH competition: Nested geometric shapes",
        min_tool_calls=5,
        max_tool_calls=15,
        tags=["math-competition", "geometry", "inscribed-shapes"],
    ))

    tasks.append(Task(
        id="math_competition_03",
        name="Sequence and Series",
        prompt="""A sequence is defined as follows:
- a₁ = 2
- a₂ = 3
- aₙ = aₙ₋₁ + 2·aₙ₋₂ for n ≥ 3

Calculate:
1. The first 8 terms of the sequence
2. The sum of the first 8 terms
3. What is a₈ as a percentage of the total sum?

Store each term as you calculate it.""",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
            requires_state_tracking=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["calculator"] * 10 + ["scratchpad"] * 8,
        expected_answer=["247", "508", "48.6%"],
        verifier_config={
            "answer": ["247", "508", "48"],
            "match_mode": "contains",
            "tools": {
                "required": ["calculator"],
                "optional": ["scratchpad"],
                "min_calls": 8,
                "max_calls": 20
            }
        },
        description="MATH competition: Recursive sequence with summation",
        min_tool_calls=8,
        max_tool_calls=20,
        tags=["math-competition", "sequence", "recursion"],
    ))

    return tasks
