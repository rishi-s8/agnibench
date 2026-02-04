"""
Custom verifiers for the data analysis benchmark suite.
"""

from typing import Any, Dict, List

from agnibench.core.abstractions import TaskResult, VerificationResult
from agnibench.core.environment import SimulatedEnvironment
from agnibench.core.evaluation import (CompositeVerifier,
                                       EnvironmentStateVerifier,
                                       ExactMatchVerifier,
                                       ToolCallSequenceVerifier, Verifier)


class InsightQualityVerifier(Verifier):
    """Verifies that insights were saved with appropriate quality."""

    def __init__(self, min_insights: int = 1, required_tags: List[str] = None):
        self.min_insights = min_insights
        self.required_tags = required_tags or []

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify insight quality."""
        insights = environment.get_state("insights", [])

        details = {
            "insights_saved": len(insights),
            "min_required": self.min_insights,
        }

        if len(insights) < self.min_insights:
            return VerificationResult(
                passed=False,
                score=len(insights) / self.min_insights,
                details={
                    **details,
                    "error": f"Expected at least {self.min_insights} insights",
                },
            )

        # Check insight quality (has title and description)
        quality_issues = []
        for i, insight in enumerate(insights):
            if not insight.get("title"):
                quality_issues.append(f"Insight {i+1} missing title")
            if (
                not insight.get("description")
                or len(insight.get("description", "")) < 20
            ):
                quality_issues.append(f"Insight {i+1} has insufficient description")

        if quality_issues:
            details["quality_issues"] = quality_issues

        return VerificationResult(
            passed=True,
            score=1.0 if not quality_issues else 0.8,
            details=details,
        )


class VisualizationVerifier(Verifier):
    """Verifies that visualizations were created appropriately."""

    def __init__(self, min_visualizations: int = 1, required_types: List[str] = None):
        self.min_visualizations = min_visualizations
        self.required_types = required_types or []

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify visualization creation."""
        visualizations = environment.get_state("visualizations", [])

        details = {
            "visualizations_created": len(visualizations),
            "min_required": self.min_visualizations,
            "types_created": [v.get("chart_type") for v in visualizations],
        }

        if len(visualizations) < self.min_visualizations:
            return VerificationResult(
                passed=False,
                score=len(visualizations) / self.min_visualizations,
                details={
                    **details,
                    "error": f"Expected at least {self.min_visualizations} visualizations",
                },
            )

        # Check for required types
        if self.required_types:
            types_created = set(v.get("chart_type") for v in visualizations)
            missing = [t for t in self.required_types if t not in types_created]
            if missing:
                details["missing_types"] = missing

        return VerificationResult(
            passed=True,
            score=1.0,
            details=details,
        )


class DataExplorationVerifier(Verifier):
    """Verifies proper data exploration workflow."""

    def __init__(
        self,
        require_describe: bool = True,
        require_statistics: bool = True,
        min_datasets_explored: int = 1,
    ):
        self.require_describe = require_describe
        self.require_statistics = require_statistics
        self.min_datasets_explored = min_datasets_explored

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify data exploration."""
        describe_calls = [
            tc for tc in result.tool_calls if tc.tool_name == "describe_dataset"
        ]
        stats_calls = [
            tc for tc in result.tool_calls if tc.tool_name == "compute_statistics"
        ]

        # Count unique datasets explored
        datasets_explored = set()
        for tc in result.tool_calls:
            if tc.tool_name in ["describe_dataset", "query_data", "compute_statistics"]:
                ds_id = tc.arguments.get("dataset_id")
                if ds_id:
                    datasets_explored.add(ds_id)

        details = {
            "describe_calls": len(describe_calls),
            "statistics_calls": len(stats_calls),
            "datasets_explored": list(datasets_explored),
        }

        score = 1.0
        issues = []

        if self.require_describe and len(describe_calls) == 0:
            score -= 0.2
            issues.append("No dataset description performed")

        if self.require_statistics and len(stats_calls) == 0:
            score -= 0.2
            issues.append("No statistics computed")

        if len(datasets_explored) < self.min_datasets_explored:
            score -= 0.3
            issues.append(
                f"Only explored {len(datasets_explored)} datasets, expected {self.min_datasets_explored}"
            )

        if issues:
            details["issues"] = issues

        return VerificationResult(
            passed=score >= 0.6,
            score=max(0, score),
            details=details,
        )


class CorrelationAnalysisVerifier(Verifier):
    """Verifies that correlation analysis was performed."""

    def __init__(self, require_strong_correlation_identification: bool = True):
        self.require_strong_correlation = require_strong_correlation_identification

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify correlation analysis."""
        correlation_calls = [
            tc for tc in result.tool_calls if tc.tool_name == "correlate_columns"
        ]

        details = {
            "correlation_calls": len(correlation_calls),
        }

        if len(correlation_calls) == 0:
            return VerificationResult(
                passed=False,
                score=0.0,
                details={**details, "error": "No correlation analysis performed"},
            )

        # Check if response mentions correlation findings
        response_lower = result.final_response.lower()
        mentions_correlation = any(
            word in response_lower
            for word in [
                "correlation",
                "correlate",
                "related",
                "relationship",
                "associated",
            ]
        )

        if self.require_strong_correlation and not mentions_correlation:
            details["warning"] = "Response doesn't clearly discuss correlations"

        return VerificationResult(
            passed=True,
            score=1.0 if mentions_correlation else 0.8,
            details=details,
        )


class QueryEfficiencyVerifier(Verifier):
    """Verifies that queries were used efficiently."""

    def __init__(self, max_redundant_queries: int = 2):
        self.max_redundant = max_redundant_queries

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify query efficiency."""
        query_calls = [tc for tc in result.tool_calls if tc.tool_name == "query_data"]

        # Check for duplicate queries
        query_signatures = []
        for tc in query_calls:
            sig = (
                tc.arguments.get("dataset_id"),
                tc.arguments.get("where"),
                tc.arguments.get("group_by"),
            )
            query_signatures.append(sig)

        unique_queries = len(set(query_signatures))
        redundant = len(query_signatures) - unique_queries

        details = {
            "total_queries": len(query_calls),
            "unique_queries": unique_queries,
            "redundant_queries": redundant,
        }

        if redundant > self.max_redundant:
            return VerificationResult(
                passed=False,
                score=0.7,
                details={
                    **details,
                    "warning": f"Too many redundant queries ({redundant})",
                },
            )

        return VerificationResult(
            passed=True,
            score=1.0,
            details=details,
        )


class ComprehensiveAnalysisVerifier(Verifier):
    """Verifies a comprehensive analysis was performed."""

    def __init__(
        self,
        require_statistics: bool = True,
        require_visualization: bool = True,
        require_insight: bool = True,
        min_tool_diversity: int = 3,
    ):
        self.require_statistics = require_statistics
        self.require_visualization = require_visualization
        self.require_insight = require_insight
        self.min_tool_diversity = min_tool_diversity

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify comprehensive analysis."""
        tool_names = [tc.tool_name for tc in result.tool_calls]
        unique_tools = set(tool_names)

        has_stats = "compute_statistics" in unique_tools
        has_viz = "create_visualization" in unique_tools
        has_insight = "save_insight" in unique_tools

        details = {
            "unique_tools_used": list(unique_tools),
            "tool_diversity": len(unique_tools),
            "has_statistics": has_stats,
            "has_visualization": has_viz,
            "has_insight": has_insight,
        }

        score = 1.0
        issues = []

        if self.require_statistics and not has_stats:
            score -= 0.2
            issues.append("No statistics computed")

        if self.require_visualization and not has_viz:
            score -= 0.2
            issues.append("No visualization created")

        if self.require_insight and not has_insight:
            score -= 0.2
            issues.append("No insights saved")

        if len(unique_tools) < self.min_tool_diversity:
            score -= 0.2
            issues.append(
                f"Low tool diversity ({len(unique_tools)} < {self.min_tool_diversity})"
            )

        if issues:
            details["issues"] = issues

        return VerificationResult(
            passed=score >= 0.6,
            score=max(0, score),
            details=details,
        )


def create_data_analysis_verifier(task_config: Dict[str, Any]) -> CompositeVerifier:
    """
    Factory function to create appropriate verifier for a data analysis task.

    Args:
        task_config: Task verifier configuration

    Returns:
        CompositeVerifier configured for the task
    """
    verifiers = []

    # Response content verification
    if "answer" in task_config:
        response_verifier = ExactMatchVerifier(
            case_sensitive=False,
            match_mode=task_config.get("match_mode", "contains"),
        )
        verifiers.append((response_verifier, 0.3, task_config["answer"]))

    # Tool sequence verification
    if "tools" in task_config:
        tool_verifier = ToolCallSequenceVerifier(
            strict_order=False,
            allow_extra_calls=True,
        )
        verifiers.append((tool_verifier, 0.2, task_config["tools"]))

    # State verification
    if "state" in task_config:
        state_verifier = EnvironmentStateVerifier()
        verifiers.append((state_verifier, 0.2, task_config["state"]))

    # Insight verification
    if task_config.get("verify_insights"):
        insight_verifier = InsightQualityVerifier(
            min_insights=task_config.get("min_insights", 1),
        )
        verifiers.append((insight_verifier, 0.15, None))

    # Visualization verification
    if task_config.get("verify_visualizations"):
        viz_verifier = VisualizationVerifier(
            min_visualizations=task_config.get("min_visualizations", 1),
        )
        verifiers.append((viz_verifier, 0.15, None))

    # Correlation verification
    if task_config.get("verify_correlation"):
        corr_verifier = CorrelationAnalysisVerifier()
        verifiers.append((corr_verifier, 0.1, None))

    # Comprehensive analysis verification
    if task_config.get("verify_comprehensive"):
        comp_verifier = ComprehensiveAnalysisVerifier(
            require_statistics=task_config.get("require_statistics", True),
            require_visualization=task_config.get("require_visualization", True),
            require_insight=task_config.get("require_insight", True),
        )
        verifiers.append((comp_verifier, 0.2, None))

    if not verifiers:
        # Fallback to basic response match
        basic_verifier = ExactMatchVerifier(match_mode="contains")
        verifiers.append((basic_verifier, 1.0, task_config.get("answer", "")))

    return CompositeVerifier(verifiers, mode="weighted", pass_threshold=0.5)
