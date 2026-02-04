"""
Custom verifiers for the customer service benchmark suite.
"""

from typing import Any, Dict, List
from agnibench.core.abstractions import TaskResult, VerificationResult
from agnibench.core.environment import SimulatedEnvironment
from agnibench.core.evaluation import (
    Verifier,
    CompositeVerifier,
    ExactMatchVerifier,
    ToolCallSequenceVerifier,
    EnvironmentStateVerifier,
)


class TicketResolutionVerifier(Verifier):
    """Verifies that a ticket was properly resolved."""

    def __init__(self, ticket_id: str = None, require_response: bool = True):
        self.ticket_id = ticket_id
        self.require_response = require_response

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify ticket resolution."""
        responses = environment.get_state("responses_sent", [])
        updates = environment.get_state("ticket_updates", [])

        details = {
            "responses_sent": len(responses),
            "updates_made": len(updates),
        }

        # Check if response was sent
        if self.require_response and len(responses) == 0:
            return VerificationResult(
                passed=False,
                score=0.5,
                details={**details, "error": "No response sent to customer"},
            )

        # Check if specific ticket was addressed
        if self.ticket_id:
            ticket_responded = any(
                r.get("ticket_id") == self.ticket_id for r in responses
            )
            if not ticket_responded:
                return VerificationResult(
                    passed=False,
                    score=0.6,
                    details={**details, "error": f"Ticket {self.ticket_id} not responded to"},
                )

        return VerificationResult(
            passed=True,
            score=1.0,
            details=details,
        )


class CustomerContextVerifier(Verifier):
    """Verifies that customer context was gathered before responding."""

    def __init__(self, require_customer_lookup: bool = True):
        self.require_customer_lookup = require_customer_lookup

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify customer context was gathered."""
        customer_calls = [
            tc for tc in result.tool_calls
            if tc.tool_name == "get_customer"
        ]

        response_calls = [
            tc for tc in result.tool_calls
            if tc.tool_name == "send_response"
        ]

        details = {
            "customer_lookups": len(customer_calls),
            "responses_sent": len(response_calls),
        }

        if self.require_customer_lookup and len(customer_calls) == 0:
            return VerificationResult(
                passed=False,
                score=0.7,
                details={**details, "warning": "Customer context not checked"},
            )

        # Check if customer lookup happened before response
        if customer_calls and response_calls:
            first_customer_call = min(
                i for i, tc in enumerate(result.tool_calls)
                if tc.tool_name == "get_customer"
            )
            first_response = min(
                i for i, tc in enumerate(result.tool_calls)
                if tc.tool_name == "send_response"
            )
            if first_customer_call > first_response:
                details["warning"] = "Customer looked up after response sent"

        return VerificationResult(
            passed=True,
            score=1.0,
            details=details,
        )


class EscalationVerifier(Verifier):
    """Verifies proper escalation handling."""

    def __init__(self, should_escalate: bool = None, expected_team: str = None):
        self.should_escalate = should_escalate
        self.expected_team = expected_team

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify escalation handling."""
        escalations = environment.get_state("escalations", [])
        escalation_calls = [
            tc for tc in result.tool_calls
            if tc.tool_name == "escalate_ticket"
        ]

        details = {
            "escalations": len(escalations),
            "escalation_calls": len(escalation_calls),
        }

        if self.should_escalate is True:
            if len(escalation_calls) == 0:
                return VerificationResult(
                    passed=False,
                    score=0.5,
                    details={**details, "error": "Should have escalated but didn't"},
                )

            if self.expected_team:
                escalated_to = [
                    e.get("specialist_team") for e in escalations
                ]
                if self.expected_team not in escalated_to:
                    return VerificationResult(
                        passed=False,
                        score=0.7,
                        details={**details, "error": f"Not escalated to {self.expected_team}"},
                    )

        elif self.should_escalate is False:
            if len(escalation_calls) > 0:
                return VerificationResult(
                    passed=False,
                    score=0.7,
                    details={**details, "warning": "Unnecessary escalation"},
                )

        return VerificationResult(
            passed=True,
            score=1.0,
            details=details,
        )


class KnowledgeBaseUsageVerifier(Verifier):
    """Verifies that knowledge base was consulted appropriately."""

    def __init__(self, min_searches: int = 1):
        self.min_searches = min_searches

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify KB usage."""
        kb_calls = [
            tc for tc in result.tool_calls
            if tc.tool_name == "search_kb"
        ]

        details = {
            "kb_searches": len(kb_calls),
            "min_required": self.min_searches,
        }

        if len(kb_calls) < self.min_searches:
            return VerificationResult(
                passed=False,
                score=len(kb_calls) / self.min_searches,
                details={**details, "warning": "Insufficient KB searches"},
            )

        return VerificationResult(
            passed=True,
            score=1.0,
            details=details,
        )


class DiagnosticWorkflowVerifier(Verifier):
    """Verifies proper diagnostic workflow was followed."""

    def __init__(
        self,
        require_ticket_read: bool = True,
        require_kb_search: bool = True,
        require_response: bool = True,
    ):
        self.require_ticket_read = require_ticket_read
        self.require_kb_search = require_kb_search
        self.require_response = require_response

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify diagnostic workflow."""
        tool_names = [tc.tool_name for tc in result.tool_calls]

        steps_completed = []
        steps_missing = []

        if self.require_ticket_read:
            if "get_ticket" in tool_names:
                steps_completed.append("ticket_read")
            else:
                steps_missing.append("ticket_read")

        if self.require_kb_search:
            if "search_kb" in tool_names:
                steps_completed.append("kb_search")
            else:
                steps_missing.append("kb_search")

        if self.require_response:
            if "send_response" in tool_names:
                steps_completed.append("response_sent")
            else:
                steps_missing.append("response_sent")

        total_steps = len(steps_completed) + len(steps_missing)
        score = len(steps_completed) / total_steps if total_steps > 0 else 0

        details = {
            "steps_completed": steps_completed,
            "steps_missing": steps_missing,
        }

        return VerificationResult(
            passed=len(steps_missing) == 0,
            score=score,
            details=details,
        )


class TriageQualityVerifier(Verifier):
    """Verifies quality of ticket triage."""

    def __init__(self, min_tickets_reviewed: int = 2):
        self.min_tickets_reviewed = min_tickets_reviewed

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify triage quality."""
        # Count unique tickets accessed
        tickets_accessed = set()
        for tc in result.tool_calls:
            if tc.tool_name == "get_ticket":
                ticket_id = tc.arguments.get("ticket_id")
                if ticket_id:
                    tickets_accessed.add(ticket_id)

        details = {
            "tickets_reviewed": len(tickets_accessed),
            "min_required": self.min_tickets_reviewed,
            "ticket_ids": list(tickets_accessed),
        }

        if len(tickets_accessed) < self.min_tickets_reviewed:
            return VerificationResult(
                passed=False,
                score=len(tickets_accessed) / self.min_tickets_reviewed,
                details={**details, "error": "Insufficient tickets reviewed"},
            )

        return VerificationResult(
            passed=True,
            score=1.0,
            details=details,
        )


def create_customer_service_verifier(task_config: Dict[str, Any]) -> CompositeVerifier:
    """
    Factory function to create appropriate verifier for a customer service task.

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

    # Ticket resolution verification
    if task_config.get("verify_resolution"):
        resolution_verifier = TicketResolutionVerifier(
            ticket_id=task_config.get("ticket_id"),
            require_response=task_config.get("require_response", True),
        )
        verifiers.append((resolution_verifier, 0.2, None))

    # Diagnostic workflow verification
    if task_config.get("verify_diagnostic"):
        diagnostic_verifier = DiagnosticWorkflowVerifier(
            require_ticket_read=task_config.get("require_ticket_read", True),
            require_kb_search=task_config.get("require_kb_search", True),
            require_response=task_config.get("require_response", True),
        )
        verifiers.append((diagnostic_verifier, 0.2, None))

    # Escalation verification
    if "should_escalate" in task_config:
        escalation_verifier = EscalationVerifier(
            should_escalate=task_config["should_escalate"],
            expected_team=task_config.get("expected_team"),
        )
        verifiers.append((escalation_verifier, 0.15, None))

    if not verifiers:
        # Fallback to basic response match
        basic_verifier = ExactMatchVerifier(match_mode="contains")
        verifiers.append((basic_verifier, 1.0, task_config.get("answer", "")))

    return CompositeVerifier(verifiers, mode="weighted", pass_threshold=0.5)
