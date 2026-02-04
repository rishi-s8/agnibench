"""
Custom verifiers for the research synthesis benchmark suite.
"""

from typing import Any, Dict, List
from agnibench.core.abstractions import TaskResult, VerificationResult
from agnibench.core.environment import SimulatedEnvironment
from agnibench.core.evaluation import (
    Verifier,
    CompositeVerifier,
    ExactMatchVerifier,
    ToolCallSequenceVerifier,
)


class FactExtractionVerifier(Verifier):
    """Verifies that key facts were extracted from documents."""

    def __init__(self, expected_facts: List[str] = None, min_facts: int = 1):
        self.expected_facts = expected_facts or []
        self.min_facts = min_facts

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify fact extraction."""
        extract_calls = [
            tc for tc in result.tool_calls
            if tc.tool_name == "extract_facts"
        ]

        if len(extract_calls) < self.min_facts:
            return VerificationResult(
                passed=False,
                score=len(extract_calls) / self.min_facts,
                details={"error": f"Expected at least {self.min_facts} fact extraction calls"},
            )

        # Check if expected facts appear in response
        response_lower = result.final_response.lower()
        found_facts = []
        for fact in self.expected_facts:
            if fact.lower() in response_lower:
                found_facts.append(fact)

        score = len(found_facts) / len(self.expected_facts) if self.expected_facts else 1.0

        return VerificationResult(
            passed=score >= 0.5,
            score=score,
            details={
                "extract_calls": len(extract_calls),
                "expected_facts": self.expected_facts,
                "found_facts": found_facts,
            },
        )


class CrossReferenceVerifier(Verifier):
    """Verifies that multiple sources were cross-referenced."""

    def __init__(self, min_sources: int = 2, require_comparison: bool = True):
        self.min_sources = min_sources
        self.require_comparison = require_comparison

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify cross-referencing was done."""
        # Count unique documents accessed
        read_calls = [
            tc for tc in result.tool_calls
            if tc.tool_name in ["read_document", "extract_facts"]
        ]

        unique_docs = set()
        for call in read_calls:
            doc_id = call.arguments.get("document_id")
            if doc_id:
                unique_docs.add(doc_id)

        # Check for comparison calls
        compare_calls = [
            tc for tc in result.tool_calls
            if tc.tool_name == "compare_sources"
        ]

        details = {
            "unique_documents_accessed": list(unique_docs),
            "document_count": len(unique_docs),
            "comparison_calls": len(compare_calls),
        }

        if len(unique_docs) < self.min_sources:
            return VerificationResult(
                passed=False,
                score=len(unique_docs) / self.min_sources,
                details={**details, "error": f"Expected at least {self.min_sources} sources"},
            )

        if self.require_comparison and len(compare_calls) == 0:
            return VerificationResult(
                passed=False,
                score=0.7,  # Partial credit for accessing multiple sources
                details={**details, "warning": "No explicit comparison made"},
            )

        return VerificationResult(
            passed=True,
            score=1.0,
            details=details,
        )


class SynthesisQualityVerifier(Verifier):
    """Verifies the quality of synthesis/summary generation."""

    def __init__(self, required_topics: List[str] = None):
        self.required_topics = required_topics or []

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify synthesis quality."""
        # Check if summary was generated
        summary_calls = [
            tc for tc in result.tool_calls
            if tc.tool_name == "generate_summary"
        ]

        response_lower = result.final_response.lower()

        # Check for required topics in response
        found_topics = []
        for topic in self.required_topics:
            if topic.lower() in response_lower:
                found_topics.append(topic)

        details = {
            "summary_generated": len(summary_calls) > 0,
            "required_topics": self.required_topics,
            "found_topics": found_topics,
        }

        if not summary_calls:
            return VerificationResult(
                passed=False,
                score=0.5,  # Partial credit if response is still good
                details={**details, "warning": "No summary tool used"},
            )

        topic_score = len(found_topics) / len(self.required_topics) if self.required_topics else 1.0

        return VerificationResult(
            passed=topic_score >= 0.6,
            score=topic_score,
            details=details,
        )


class NotesTakenVerifier(Verifier):
    """Verifies that research notes were taken appropriately."""

    def __init__(self, min_notes: int = 1, required_tags: List[str] = None):
        self.min_notes = min_notes
        self.required_tags = required_tags or []

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify notes were taken."""
        note_calls = [
            tc for tc in result.tool_calls
            if tc.tool_name == "take_notes"
        ]

        notes = environment.get_state("notes", [])

        details = {
            "note_calls": len(note_calls),
            "notes_stored": len(notes),
            "min_required": self.min_notes,
        }

        if len(note_calls) < self.min_notes:
            return VerificationResult(
                passed=False,
                score=len(note_calls) / self.min_notes,
                details={**details, "error": f"Expected at least {self.min_notes} notes"},
            )

        return VerificationResult(
            passed=True,
            score=1.0,
            details=details,
        )


class DocumentCoverageVerifier(Verifier):
    """Verifies that relevant documents were found and accessed."""

    def __init__(self, expected_doc_ids: List[str] = None, min_coverage: float = 0.5):
        self.expected_doc_ids = expected_doc_ids or []
        self.min_coverage = min_coverage

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify document coverage."""
        # Get all documents accessed
        accessed_docs = set()
        for tc in result.tool_calls:
            if tc.tool_name in ["read_document", "extract_facts"]:
                doc_id = tc.arguments.get("document_id")
                if doc_id:
                    accessed_docs.add(doc_id)

        # Check coverage of expected documents
        if self.expected_doc_ids:
            found = [d for d in self.expected_doc_ids if d in accessed_docs]
            coverage = len(found) / len(self.expected_doc_ids)
        else:
            coverage = 1.0 if accessed_docs else 0.0

        details = {
            "accessed_documents": list(accessed_docs),
            "expected_documents": self.expected_doc_ids,
            "coverage": coverage,
        }

        return VerificationResult(
            passed=coverage >= self.min_coverage,
            score=coverage,
            details=details,
        )


def create_research_verifier(task_config: Dict[str, Any]) -> CompositeVerifier:
    """
    Factory function to create appropriate verifier for a research task.

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

    # Cross-reference verification
    if task_config.get("verify_cross_reference"):
        cross_ref_verifier = CrossReferenceVerifier(
            min_sources=task_config.get("min_sources", 2),
            require_comparison=task_config.get("require_comparison", True),
        )
        verifiers.append((cross_ref_verifier, 0.2, None))

    # Fact extraction verification
    if task_config.get("expected_facts"):
        fact_verifier = FactExtractionVerifier(
            expected_facts=task_config["expected_facts"],
        )
        verifiers.append((fact_verifier, 0.2, None))

    # Synthesis verification
    if task_config.get("required_topics"):
        synthesis_verifier = SynthesisQualityVerifier(
            required_topics=task_config["required_topics"],
        )
        verifiers.append((synthesis_verifier, 0.2, None))

    # Notes verification
    if task_config.get("min_notes"):
        notes_verifier = NotesTakenVerifier(
            min_notes=task_config["min_notes"],
        )
        verifiers.append((notes_verifier, 0.1, None))

    if not verifiers:
        # Fallback to basic response match
        basic_verifier = ExactMatchVerifier(match_mode="contains")
        verifiers.append((basic_verifier, 1.0, task_config.get("answer", "")))

    return CompositeVerifier(verifiers, mode="weighted", pass_threshold=0.5)
