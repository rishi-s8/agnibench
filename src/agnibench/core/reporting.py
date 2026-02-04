"""
Reporting and analysis for benchmark results.

Provides comparative analysis between models.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

from agnibench.core.abstractions import DifficultyLevel, InformationFlow
from agnibench.core.runner import SuiteResult


@dataclass
class BenchmarkReport:
    """Report for a single model's benchmark results."""
    model_name: str
    suite_results: Dict[str, SuiteResult]
    generated_at: datetime = field(default_factory=datetime.now)

    @property
    def overall_pass_rate(self) -> float:
        """Calculate overall pass rate across all suites."""
        total_passed = sum(sr.passed_tasks for sr in self.suite_results.values())
        total_tasks = sum(sr.total_tasks for sr in self.suite_results.values())
        return total_passed / total_tasks if total_tasks > 0 else 0.0

    @property
    def overall_average_score(self) -> float:
        """Calculate overall average score across all suites."""
        all_scores = []
        for sr in self.suite_results.values():
            all_scores.extend(r.verification.score for r in sr.task_results)
        return sum(all_scores) / len(all_scores) if all_scores else 0.0

    @property
    def total_tasks(self) -> int:
        """Total number of tasks across all suites."""
        return sum(sr.total_tasks for sr in self.suite_results.values())

    @property
    def total_passed(self) -> int:
        """Total number of passed tasks across all suites."""
        return sum(sr.passed_tasks for sr in self.suite_results.values())

    def by_difficulty(self) -> Dict[str, Dict[str, float]]:
        """Aggregate results by difficulty level."""
        by_diff = {}
        for sr in self.suite_results.values():
            diff_results = sr.results_by_difficulty()
            for diff, data in diff_results.items():
                if diff not in by_diff:
                    by_diff[diff] = {"passed": 0, "total": 0, "scores": []}
                by_diff[diff]["passed"] += data["passed"]
                by_diff[diff]["total"] += data["total"]
                by_diff[diff]["scores"].extend(data["scores"])

        # Calculate rates
        for diff, data in by_diff.items():
            data["pass_rate"] = data["passed"] / data["total"] if data["total"] > 0 else 0
            data["avg_score"] = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
            del data["scores"]  # Remove raw scores from output

        return by_diff

    def by_suite(self) -> Dict[str, Dict[str, float]]:
        """Get summary statistics per suite."""
        return {
            name: {
                "pass_rate": sr.pass_rate,
                "average_score": sr.average_score,
                "total_tasks": sr.total_tasks,
                "average_tool_calls": sr.average_tool_calls,
            }
            for name, sr in self.suite_results.items()
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "model_name": self.model_name,
            "generated_at": self.generated_at.isoformat(),
            "summary": {
                "overall_pass_rate": self.overall_pass_rate,
                "overall_average_score": self.overall_average_score,
                "total_tasks": self.total_tasks,
                "total_passed": self.total_passed,
            },
            "by_difficulty": self.by_difficulty(),
            "by_suite": self.by_suite(),
            "suite_results": {
                name: sr.to_dict() for name, sr in self.suite_results.items()
            },
        }

    def save(self, path: str) -> None:
        """Save report to JSON file."""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "BenchmarkReport":
        """Load report from JSON file (partial reconstruction)."""
        with open(path, "r") as f:
            data = json.load(f)
        # Note: This returns the dict, full reconstruction would need more work
        return data


@dataclass
class ComparisonReport:
    """Comparison report between multiple models."""
    reports: List[BenchmarkReport]
    generated_at: datetime = field(default_factory=datetime.now)

    @property
    def model_names(self) -> List[str]:
        """List of model names being compared."""
        return [r.model_name for r in self.reports]

    def overall_comparison(self) -> Dict[str, Dict[str, float]]:
        """Compare overall metrics across models."""
        return {
            report.model_name: {
                "pass_rate": report.overall_pass_rate,
                "average_score": report.overall_average_score,
                "total_tasks": report.total_tasks,
            }
            for report in self.reports
        }

    def suite_comparison(self, suite_name: str) -> Dict[str, Dict[str, float]]:
        """Compare metrics for a specific suite across models."""
        comparison = {}
        for report in self.reports:
            if suite_name in report.suite_results:
                sr = report.suite_results[suite_name]
                comparison[report.model_name] = {
                    "pass_rate": sr.pass_rate,
                    "average_score": sr.average_score,
                    "average_tool_calls": sr.average_tool_calls,
                }
        return comparison

    def difficulty_comparison(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Compare performance by difficulty across models."""
        comparison = {}
        for report in self.reports:
            comparison[report.model_name] = report.by_difficulty()
        return comparison

    def get_winner_by_suite(self) -> Dict[str, str]:
        """Get the best performing model for each suite."""
        winners = {}
        suite_names = set()
        for report in self.reports:
            suite_names.update(report.suite_results.keys())

        for suite_name in suite_names:
            best_model = None
            best_score = -1
            for report in self.reports:
                if suite_name in report.suite_results:
                    score = report.suite_results[suite_name].average_score
                    if score > best_score:
                        best_score = score
                        best_model = report.model_name
            winners[suite_name] = best_model

        return winners

    def get_delta_analysis(self, baseline_model: str) -> Dict[str, Dict[str, float]]:
        """
        Calculate performance delta from a baseline model.

        Args:
            baseline_model: Name of the model to use as baseline

        Returns:
            Dict mapping model names to their delta from baseline
        """
        baseline_report = None
        for report in self.reports:
            if report.model_name == baseline_model:
                baseline_report = report
                break

        if not baseline_report:
            raise ValueError(f"Baseline model '{baseline_model}' not found")

        deltas = {}
        for report in self.reports:
            if report.model_name == baseline_model:
                continue

            deltas[report.model_name] = {
                "pass_rate_delta": report.overall_pass_rate - baseline_report.overall_pass_rate,
                "score_delta": report.overall_average_score - baseline_report.overall_average_score,
            }

            # Per-suite deltas
            suite_deltas = {}
            for suite_name, sr in report.suite_results.items():
                if suite_name in baseline_report.suite_results:
                    baseline_sr = baseline_report.suite_results[suite_name]
                    suite_deltas[suite_name] = {
                        "pass_rate_delta": sr.pass_rate - baseline_sr.pass_rate,
                        "score_delta": sr.average_score - baseline_sr.average_score,
                    }
            deltas[report.model_name]["by_suite"] = suite_deltas

        return deltas

    def generate_summary_table(self) -> str:
        """Generate a formatted summary table."""
        lines = []
        lines.append("=" * 80)
        lines.append("BENCHMARK COMPARISON SUMMARY")
        lines.append("=" * 80)
        lines.append("")

        # Header
        header = f"{'Model':<30} {'Pass Rate':>12} {'Avg Score':>12} {'Tasks':>8}"
        lines.append(header)
        lines.append("-" * 70)

        # Overall results
        for report in sorted(self.reports, key=lambda r: r.overall_average_score, reverse=True):
            line = f"{report.model_name:<30} {report.overall_pass_rate:>11.1%} {report.overall_average_score:>12.3f} {report.total_tasks:>8}"
            lines.append(line)

        lines.append("")
        lines.append("BY SUITE:")
        lines.append("-" * 70)

        # Per-suite results
        suite_names = set()
        for report in self.reports:
            suite_names.update(report.suite_results.keys())

        for suite_name in sorted(suite_names):
            lines.append(f"\n{suite_name}:")
            for report in sorted(self.reports, key=lambda r: r.suite_results.get(suite_name, SuiteResult(suite_name, "", [], datetime.now())).average_score, reverse=True):
                if suite_name in report.suite_results:
                    sr = report.suite_results[suite_name]
                    line = f"  {report.model_name:<28} {sr.pass_rate:>11.1%} {sr.average_score:>12.3f}"
                    lines.append(line)

        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Convert comparison report to dictionary."""
        return {
            "generated_at": self.generated_at.isoformat(),
            "model_names": self.model_names,
            "overall_comparison": self.overall_comparison(),
            "difficulty_comparison": self.difficulty_comparison(),
            "suite_winners": self.get_winner_by_suite(),
            "reports": [r.to_dict() for r in self.reports],
        }

    def save(self, path: str) -> None:
        """Save comparison report to JSON file."""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


def generate_characteristic_analysis(
    reports: List[BenchmarkReport],
) -> Dict[str, Dict[str, Any]]:
    """
    Analyze performance by task characteristics.

    Returns breakdown of how models perform on different capability requirements.
    """
    # This would require task metadata with characteristics flags
    # For now, return a placeholder structure
    analysis = {}

    characteristics = [
        "requires_error_recovery",
        "requires_disambiguation",
        "requires_state_tracking",
        "requires_multi_constraint",
        "requires_cross_reference",
        "requires_conditional_logic",
        "requires_long_reasoning_chain",
        "requires_plan_adaptation",
    ]

    for char in characteristics:
        analysis[char] = {
            report.model_name: {
                "with_characteristic": {"pass_rate": 0.0, "count": 0},
                "without_characteristic": {"pass_rate": 0.0, "count": 0},
            }
            for report in reports
        }

    return analysis


def format_results_markdown(report: BenchmarkReport) -> str:
    """Format benchmark report as markdown."""
    lines = []
    lines.append(f"# Benchmark Results: {report.model_name}")
    lines.append(f"\nGenerated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    lines.append("## Summary")
    lines.append(f"- **Overall Pass Rate**: {report.overall_pass_rate:.1%}")
    lines.append(f"- **Overall Average Score**: {report.overall_average_score:.3f}")
    lines.append(f"- **Total Tasks**: {report.total_tasks}")
    lines.append("")

    lines.append("## Results by Difficulty")
    lines.append("")
    lines.append("| Difficulty | Pass Rate | Avg Score | Tasks |")
    lines.append("|------------|-----------|-----------|-------|")
    for diff, data in sorted(report.by_difficulty().items()):
        lines.append(f"| {diff} | {data['pass_rate']:.1%} | {data['avg_score']:.3f} | {data['total']} |")
    lines.append("")

    lines.append("## Results by Suite")
    lines.append("")
    for suite_name, data in report.by_suite().items():
        lines.append(f"### {suite_name}")
        lines.append(f"- Pass Rate: {data['pass_rate']:.1%}")
        lines.append(f"- Average Score: {data['average_score']:.3f}")
        lines.append(f"- Average Tool Calls: {data['average_tool_calls']:.1f}")
        lines.append("")

    return "\n".join(lines)
