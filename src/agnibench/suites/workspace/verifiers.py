"""
Custom verifiers for the workspace benchmark suite.
"""

from typing import Any, Dict, List

from agnibench.core.abstractions import TaskResult, VerificationResult
from agnibench.core.environment import SimulatedEnvironment
from agnibench.core.evaluation import (CompositeVerifier,
                                       EnvironmentStateVerifier,
                                       ExactMatchVerifier,
                                       ToolCallSequenceVerifier, Verifier)


class EmailSentVerifier(Verifier):
    """Verifies that an email was sent with expected properties."""

    def __init__(
        self,
        required_recipient: str = None,
        subject_contains: str = None,
        body_contains: str = None,
    ):
        self.required_recipient = required_recipient
        self.subject_contains = subject_contains
        self.body_contains = body_contains

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify email was sent correctly."""
        sent_emails = environment.get_state("sent_emails", [])

        if not sent_emails:
            return VerificationResult(
                passed=False,
                score=0.0,
                details={"error": "No emails were sent"},
            )

        # Check each sent email
        for email in sent_emails:
            matches = True
            details = {"email": email}

            if self.required_recipient:
                if self.required_recipient.lower() not in email.get("to", "").lower():
                    matches = False
                    details["recipient_mismatch"] = True

            if self.subject_contains:
                if (
                    self.subject_contains.lower()
                    not in email.get("subject", "").lower()
                ):
                    matches = False
                    details["subject_mismatch"] = True

            if self.body_contains:
                if self.body_contains.lower() not in email.get("body", "").lower():
                    matches = False
                    details["body_mismatch"] = True

            if matches:
                return VerificationResult(
                    passed=True,
                    score=1.0,
                    details=details,
                )

        return VerificationResult(
            passed=False,
            score=0.5,  # Partial credit for sending something
            details={"emails_sent": len(sent_emails), "criteria_not_met": True},
        )


class EventCreatedVerifier(Verifier):
    """Verifies that a calendar event was created with expected properties."""

    def __init__(
        self,
        title_contains: str = None,
        required_attendees: List[str] = None,
        min_duration_minutes: int = None,
    ):
        self.title_contains = title_contains
        self.required_attendees = required_attendees or []
        self.min_duration_minutes = min_duration_minutes

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify event was created correctly."""
        created_events = environment.get_state("created_events", [])

        if not created_events:
            return VerificationResult(
                passed=False,
                score=0.0,
                details={"error": "No events were created"},
            )

        for event in created_events:
            matches = True
            details = {"event": event}

            if self.title_contains:
                if self.title_contains.lower() not in event.get("title", "").lower():
                    matches = False
                    details["title_mismatch"] = True

            if self.required_attendees:
                event_attendees = [a.lower() for a in event.get("attendees", [])]
                missing = []
                for req in self.required_attendees:
                    found = any(req.lower() in a for a in event_attendees)
                    if not found:
                        missing.append(req)
                if missing:
                    matches = False
                    details["missing_attendees"] = missing

            if self.min_duration_minutes:
                # Would need to parse times to verify duration
                pass

            if matches:
                return VerificationResult(
                    passed=True,
                    score=1.0,
                    details=details,
                )

        return VerificationResult(
            passed=False,
            score=0.5,
            details={"events_created": len(created_events), "criteria_not_met": True},
        )


class SlackSentVerifier(Verifier):
    """Verifies that a Slack message was sent with expected properties."""

    def __init__(
        self,
        required_channel: str = None,
        message_contains: str = None,
    ):
        self.required_channel = required_channel
        self.message_contains = message_contains

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify Slack message was sent correctly."""
        sent_slack = environment.get_state("sent_slack", [])

        if not sent_slack:
            return VerificationResult(
                passed=False,
                score=0.0,
                details={"error": "No Slack messages were sent"},
            )

        for msg in sent_slack:
            matches = True
            details = {"message": msg}

            if self.required_channel:
                if self.required_channel.lower() not in msg.get("channel", "").lower():
                    matches = False
                    details["channel_mismatch"] = True

            if self.message_contains:
                if self.message_contains.lower() not in msg.get("message", "").lower():
                    matches = False
                    details["content_mismatch"] = True

            if matches:
                return VerificationResult(
                    passed=True,
                    score=1.0,
                    details=details,
                )

        return VerificationResult(
            passed=False,
            score=0.5,
            details={"messages_sent": len(sent_slack), "criteria_not_met": True},
        )


class CoordinationVerifier(Verifier):
    """Verifies multi-tool coordination tasks."""

    def __init__(
        self,
        required_actions: List[
            str
        ] = None,  # e.g., ["email_sent", "event_created", "slack_sent"]
    ):
        self.required_actions = required_actions or []

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify all required actions were completed."""
        completed = []
        missing = []

        action_checks = {
            "email_sent": lambda: len(environment.get_state("sent_emails", [])) > 0,
            "event_created": lambda: len(environment.get_state("created_events", []))
            > 0,
            "slack_sent": lambda: len(environment.get_state("sent_slack", [])) > 0,
            "contacts_looked_up": lambda: any(
                tc.tool_name == "lookup_contact" for tc in result.tool_calls
            ),
            "availability_checked": lambda: any(
                tc.tool_name == "check_availability" for tc in result.tool_calls
            ),
        }

        for action in self.required_actions:
            if action in action_checks:
                if action_checks[action]():
                    completed.append(action)
                else:
                    missing.append(action)
            else:
                missing.append(action)

        score = (
            len(completed) / len(self.required_actions)
            if self.required_actions
            else 1.0
        )

        return VerificationResult(
            passed=len(missing) == 0,
            score=score,
            details={
                "completed_actions": completed,
                "missing_actions": missing,
                "required_actions": self.required_actions,
            },
        )


class AvailabilityCheckVerifier(Verifier):
    """Verifies that availability was properly checked before scheduling."""

    def __init__(self, required_attendees: List[str] = None):
        self.required_attendees = required_attendees or []

    def verify(
        self,
        result: TaskResult,
        environment: SimulatedEnvironment,
        expected: Any,
    ) -> VerificationResult:
        """Verify availability was checked for required attendees."""
        availability_calls = [
            tc for tc in result.tool_calls if tc.tool_name == "check_availability"
        ]

        if not availability_calls:
            return VerificationResult(
                passed=False,
                score=0.0,
                details={"error": "Availability was not checked"},
            )

        # Check which attendees were checked
        checked_attendees = set()
        for call in availability_calls:
            attendees = call.arguments.get("attendees", [])
            for att in attendees:
                checked_attendees.add(att.lower())

        # Verify required attendees were checked
        if self.required_attendees:
            missing = []
            for req in self.required_attendees:
                found = any(req.lower() in checked for checked in checked_attendees)
                if not found:
                    missing.append(req)

            if missing:
                return VerificationResult(
                    passed=False,
                    score=len(self.required_attendees - len(missing))
                    / len(self.required_attendees),
                    details={
                        "checked_attendees": list(checked_attendees),
                        "missing": missing,
                    },
                )

        return VerificationResult(
            passed=True,
            score=1.0,
            details={"checked_attendees": list(checked_attendees)},
        )


def create_workspace_verifier(task_config: Dict[str, Any]) -> CompositeVerifier:
    """
    Factory function to create appropriate verifier for a workspace task.

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
            strict_order=task_config.get("strict_order", False),
            allow_extra_calls=True,
        )
        verifiers.append((tool_verifier, 0.2, task_config["tools"]))

    # State verification
    if "state" in task_config:
        state_verifier = EnvironmentStateVerifier()
        verifiers.append((state_verifier, 0.3, task_config["state"]))

    # Email sent verification
    if task_config.get("verify_email_sent"):
        email_verifier = EmailSentVerifier(
            required_recipient=task_config.get("email_recipient"),
            subject_contains=task_config.get("email_subject_contains"),
            body_contains=task_config.get("email_body_contains"),
        )
        verifiers.append((email_verifier, 0.2, None))

    # Event created verification
    if task_config.get("verify_event_created"):
        event_verifier = EventCreatedVerifier(
            title_contains=task_config.get("event_title_contains"),
            required_attendees=task_config.get("event_attendees"),
        )
        verifiers.append((event_verifier, 0.2, None))

    # Coordination verification
    if task_config.get("required_actions"):
        coord_verifier = CoordinationVerifier(
            required_actions=task_config["required_actions"],
        )
        verifiers.append((coord_verifier, 0.3, None))

    if not verifiers:
        # Fallback to basic response match
        basic_verifier = ExactMatchVerifier(match_mode="contains")
        verifiers.append((basic_verifier, 1.0, task_config.get("answer", "")))

    return CompositeVerifier(verifiers, mode="weighted", pass_threshold=0.5)
