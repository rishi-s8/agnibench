"""
Difficulty profiles that map DifficultyLevel to DAG structural constraints.
"""

from dataclasses import dataclass
from typing import Tuple

from agnibench.core.abstractions import DifficultyLevel, InformationFlow


@dataclass
class DifficultyProfile:
    """Structural constraints for DAG generation at a given difficulty."""

    depth_range: Tuple[int, int]
    breadth_range: Tuple[int, int]
    tool_call_range: Tuple[int, int]
    information_flow: InformationFlow
    p_conditional: float  # Probability of conditional branching
    p_error_recovery: float  # Probability of error recovery pattern
    p_cross_reference: float  # Probability of cross-reference pattern
    p_plan_adaptation: float  # Probability of plan adaptation

    @property
    def min_depth(self) -> int:
        return self.depth_range[0]

    @property
    def max_depth(self) -> int:
        return self.depth_range[1]

    @property
    def min_tool_calls(self) -> int:
        return self.tool_call_range[0]

    @property
    def max_tool_calls(self) -> int:
        return self.tool_call_range[1]


# Default difficulty profiles matching the plan spec
DIFFICULTY_PROFILES = {
    DifficultyLevel.SIMPLE: DifficultyProfile(
        depth_range=(1, 2),
        breadth_range=(1, 1),
        tool_call_range=(2, 3),
        information_flow=InformationFlow.PROMPT_FULL,
        p_conditional=0.0,
        p_error_recovery=0.0,
        p_cross_reference=0.0,
        p_plan_adaptation=0.0,
    ),
    DifficultyLevel.MEDIUM: DifficultyProfile(
        depth_range=(2, 4),
        breadth_range=(1, 2),
        tool_call_range=(4, 6),
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        p_conditional=0.2,
        p_error_recovery=0.0,
        p_cross_reference=0.3,
        p_plan_adaptation=0.0,
    ),
    DifficultyLevel.HARD: DifficultyProfile(
        depth_range=(3, 6),
        breadth_range=(2, 3),
        tool_call_range=(7, 10),
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        p_conditional=0.5,
        p_error_recovery=0.3,
        p_cross_reference=0.5,
        p_plan_adaptation=0.2,
    ),
    DifficultyLevel.EXPERT: DifficultyProfile(
        depth_range=(5, 10),
        breadth_range=(2, 4),
        tool_call_range=(11, 15),
        information_flow=InformationFlow.TOOL_DISCOVERY,
        p_conditional=0.7,
        p_error_recovery=0.5,
        p_cross_reference=0.7,
        p_plan_adaptation=0.4,
    ),
}


def get_profile(difficulty: DifficultyLevel) -> DifficultyProfile:
    """Get the difficulty profile for a given level."""
    return DIFFICULTY_PROFILES[difficulty]
