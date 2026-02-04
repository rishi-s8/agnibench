"""
Simulated environment for the workspace benchmark suite.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from agnibench.core.environment import SimulatedEnvironment
from agnibench.suites.workspace.tools import (get_workspace_data,
                                              set_workspace_data)
from agnibench.utils.data_generators import (generate_contact,
                                             generate_random_calendar_event,
                                             generate_random_email,
                                             generate_slack_message)


class WorkspaceEnvironment(SimulatedEnvironment):
    """
    Environment for workspace tasks.

    Manages emails, calendar events, Slack messages, and contacts.
    """

    def _setup_default_state(self) -> None:
        """Set up default state with sample workspace data."""
        # Generate sample data
        now = datetime.now()

        # Sample contacts
        contacts = [
            {
                "id": "contact_1",
                "name": "Alice Johnson",
                "email": "alice.johnson@company.com",
                "phone": "+1-555-123-4567",
                "department": "Engineering",
                "title": "Senior Engineer",
                "timezone": "PST",
            },
            {
                "id": "contact_2",
                "name": "Bob Smith",
                "email": "bob.smith@company.com",
                "phone": "+1-555-234-5678",
                "department": "Product",
                "title": "Product Manager",
                "timezone": "EST",
            },
            {
                "id": "contact_3",
                "name": "Carol Williams",
                "email": "carol.williams@company.com",
                "phone": "+1-555-345-6789",
                "department": "Design",
                "title": "Lead Designer",
                "timezone": "PST",
            },
            {
                "id": "contact_4",
                "name": "David Brown",
                "email": "david.brown@company.com",
                "phone": "+1-555-456-7890",
                "department": "Engineering",
                "title": "Engineering Manager",
                "timezone": "EST",
            },
            {
                "id": "contact_5",
                "name": "Eve Davis",
                "email": "eve.davis@company.com",
                "phone": "+1-555-567-8901",
                "department": "Sales",
                "title": "Sales Director",
                "timezone": "CST",
            },
        ]

        # Sample emails
        emails = [
            {
                "id": "email_1",
                "sender": "Alice Johnson",
                "sender_email": "alice.johnson@company.com",
                "recipient": "You",
                "recipient_email": "me@company.com",
                "subject": "Project Update - Q4 Planning",
                "body": "Hi,\n\nI wanted to share the latest updates on the Q4 planning. We need to schedule a meeting to discuss the roadmap. Can we find time this week?\n\nKey items to discuss:\n1. Feature priorities\n2. Resource allocation\n3. Timeline adjustments\n\nLet me know your availability.\n\nBest,\nAlice",
                "timestamp": (now - timedelta(hours=3)).isoformat(),
                "read": False,
                "labels": ["inbox", "important"],
            },
            {
                "id": "email_2",
                "sender": "Bob Smith",
                "sender_email": "bob.smith@company.com",
                "recipient": "You",
                "recipient_email": "me@company.com",
                "subject": "Re: Feature Request",
                "body": "Thanks for the feedback on the feature request. I've updated the requirements doc based on your suggestions.\n\nThe main changes are:\n- Added user authentication flow\n- Clarified the data model\n- Included edge cases\n\nPlease review when you have a chance.\n\nBob",
                "timestamp": (now - timedelta(days=1)).isoformat(),
                "read": True,
                "labels": ["inbox"],
            },
            {
                "id": "email_3",
                "sender": "Carol Williams",
                "sender_email": "carol.williams@company.com",
                "recipient": "You",
                "recipient_email": "me@company.com",
                "subject": "Design Review Meeting",
                "body": "Hi team,\n\nI'd like to schedule a design review for the new dashboard. We have several mockups ready for feedback.\n\nProposed agenda:\n- Overview of design changes\n- User feedback incorporation\n- Next steps\n\nPlease let me know if Tuesday or Wednesday works better.\n\nCarol",
                "timestamp": (now - timedelta(hours=6)).isoformat(),
                "read": False,
                "labels": ["inbox", "work"],
            },
            {
                "id": "email_4",
                "sender": "David Brown",
                "sender_email": "david.brown@company.com",
                "recipient": "You",
                "recipient_email": "me@company.com",
                "subject": "Team Sync - Action Items",
                "body": "Following up from our team sync:\n\nAction items:\n1. Review the API documentation by Friday\n2. Submit Q3 retrospective notes\n3. Update project timeline\n\nLet me know if you have questions.\n\nDavid",
                "timestamp": (now - timedelta(days=2)).isoformat(),
                "read": True,
                "labels": ["inbox"],
            },
            {
                "id": "email_5",
                "sender": "Eve Davis",
                "sender_email": "eve.davis@company.com",
                "recipient": "You",
                "recipient_email": "me@company.com",
                "subject": "Customer Meeting Prep",
                "body": "Hi,\n\nWe have an important customer meeting next week. Can you prepare a demo of the new features?\n\nCustomer: Acme Corp\nDate: Next Tuesday, 2 PM\nTopics: Product roadmap, integration options\n\nLet me know if you need any materials.\n\nEve",
                "timestamp": (now - timedelta(hours=1)).isoformat(),
                "read": False,
                "labels": ["inbox", "important"],
            },
        ]

        # Sample calendar events
        tomorrow = (now + timedelta(days=1)).replace(
            hour=10, minute=0, second=0, microsecond=0
        )
        next_week = (now + timedelta(days=7)).replace(
            hour=14, minute=0, second=0, microsecond=0
        )

        calendar_events = [
            {
                "id": "event_existing_1",
                "title": "Team Standup",
                "start_time": tomorrow.isoformat(),
                "end_time": (tomorrow + timedelta(minutes=30)).isoformat(),
                "attendees": ["Alice Johnson", "Bob Smith", "Carol Williams"],
                "location": "Conference Room A",
                "description": "Daily team standup",
                "organizer": "David Brown",
                "status": "confirmed",
            },
            {
                "id": "event_existing_2",
                "title": "Product Review",
                "start_time": (tomorrow + timedelta(hours=3)).isoformat(),
                "end_time": (tomorrow + timedelta(hours=4)).isoformat(),
                "attendees": ["Bob Smith", "Eve Davis"],
                "location": "Virtual",
                "description": "Weekly product review",
                "organizer": "Bob Smith",
                "status": "confirmed",
            },
            {
                "id": "event_existing_3",
                "title": "1:1 with Manager",
                "start_time": (tomorrow + timedelta(hours=5)).isoformat(),
                "end_time": (tomorrow + timedelta(hours=6)).isoformat(),
                "attendees": ["David Brown"],
                "location": "Office 301",
                "description": "Weekly 1:1",
                "organizer": "David Brown",
                "status": "confirmed",
            },
            {
                "id": "event_existing_4",
                "title": "Customer Demo",
                "start_time": next_week.isoformat(),
                "end_time": (next_week + timedelta(hours=1)).isoformat(),
                "attendees": ["Eve Davis", "Alice Johnson"],
                "location": "Virtual",
                "description": "Demo for Acme Corp",
                "organizer": "Eve Davis",
                "status": "confirmed",
            },
            # EDGE CASE: Scheduling conflict - overlaps with Product Review
            {
                "id": "event_conflict_1",
                "title": "Budget Planning",
                "start_time": (tomorrow + timedelta(hours=3, minutes=30)).isoformat(),
                "end_time": (tomorrow + timedelta(hours=4, minutes=30)).isoformat(),
                "attendees": ["Eve Davis", "David Brown"],
                "location": "Conference Room B",
                "description": "Q1 budget review - CONFLICTS with Product Review",
                "organizer": "Eve Davis",
                "status": "tentative",
            },
            # EDGE CASE: Cancelled event that should be ignored
            {
                "id": "event_cancelled_1",
                "title": "Old Planning Meeting",
                "start_time": (tomorrow + timedelta(hours=2)).isoformat(),
                "end_time": (tomorrow + timedelta(hours=3)).isoformat(),
                "attendees": ["Alice Johnson"],
                "location": "Virtual",
                "description": "This meeting was cancelled",
                "organizer": "Bob Smith",
                "status": "cancelled",
            },
            # EDGE CASE: All-day event
            {
                "id": "event_allday_1",
                "title": "Company Holiday",
                "start_time": (now + timedelta(days=5))
                .replace(hour=0, minute=0)
                .isoformat(),
                "end_time": (now + timedelta(days=5))
                .replace(hour=23, minute=59)
                .isoformat(),
                "attendees": [],
                "location": "",
                "description": "Office closed - company holiday",
                "organizer": "HR",
                "status": "confirmed",
                "all_day": True,
            },
        ]

        # Sample Slack messages
        slack_messages = [
            {
                "id": "slack_1",
                "channel": "#general",
                "sender": "Alice Johnson",
                "content": "Good morning everyone! Reminder about the team sync at 10am.",
                "timestamp": (now - timedelta(hours=2)).isoformat(),
                "reactions": ["thumbsup"],
                "thread_count": 3,
            },
            {
                "id": "slack_2",
                "channel": "#engineering",
                "sender": "Bob Smith",
                "content": "The deployment is scheduled for 5pm today. Please hold off on merging new PRs.",
                "timestamp": (now - timedelta(hours=1)).isoformat(),
                "reactions": ["eyes", "thumbsup"],
                "thread_count": 5,
            },
            {
                "id": "slack_3",
                "channel": "#design",
                "sender": "Carol Williams",
                "content": "New mockups are ready for review! Check the Figma link in the thread.",
                "timestamp": (now - timedelta(hours=4)).isoformat(),
                "reactions": ["heart"],
                "thread_count": 2,
            },
            {
                "id": "slack_4",
                "channel": "#general",
                "sender": "David Brown",
                "content": "Great work on the Q3 release everyone! Let's celebrate our wins.",
                "timestamp": (now - timedelta(days=1)).isoformat(),
                "reactions": ["tada", "rocket"],
                "thread_count": 10,
            },
        ]

        # Set up workspace data
        workspace_data = {
            "emails": emails,
            "calendar_events": calendar_events,
            "slack_messages": slack_messages,
            "contacts": contacts,
            "sent_emails": [],
            "created_events": [],
            "sent_slack": [],
        }

        set_workspace_data(workspace_data)

        # Also store in environment state for verification
        self._state["emails"] = emails
        self._state["calendar_events"] = calendar_events
        self._state["slack_messages"] = slack_messages
        self._state["contacts"] = contacts
        self._state["sent_emails"] = []
        self._state["created_events"] = []
        self._state["sent_slack"] = []

    def reset(self) -> None:
        """Reset the environment."""
        super().reset()
        self._setup_default_state()

    def add_email(self, email: Dict[str, Any]) -> None:
        """Add an email to the environment."""
        emails = self._state.get("emails", [])
        emails.append(email)
        self.set_state("emails", emails, source_tool="test_setup")

        # Also update workspace data
        workspace_data = get_workspace_data()
        workspace_data["emails"] = emails
        set_workspace_data(workspace_data)

    def add_calendar_event(self, event: Dict[str, Any]) -> None:
        """Add a calendar event to the environment."""
        events = self._state.get("calendar_events", [])
        events.append(event)
        self.set_state("calendar_events", events, source_tool="test_setup")

        workspace_data = get_workspace_data()
        workspace_data["calendar_events"] = events
        set_workspace_data(workspace_data)

    def add_contact(self, contact: Dict[str, Any]) -> None:
        """Add a contact to the environment."""
        contacts = self._state.get("contacts", [])
        contacts.append(contact)
        self.set_state("contacts", contacts, source_tool="test_setup")

        workspace_data = get_workspace_data()
        workspace_data["contacts"] = contacts
        set_workspace_data(workspace_data)

    def sync_state_from_workspace(self) -> None:
        """Sync environment state from workspace data (after tool executions)."""
        workspace_data = get_workspace_data()
        self._state["sent_emails"] = workspace_data.get("sent_emails", [])
        self._state["created_events"] = workspace_data.get("created_events", [])
        self._state["sent_slack"] = workspace_data.get("sent_slack", [])

    @property
    def email_count(self) -> int:
        """Number of emails in inbox."""
        return len(self._state.get("emails", []))

    @property
    def unread_count(self) -> int:
        """Number of unread emails."""
        return sum(1 for e in self._state.get("emails", []) if not e.get("read", True))

    @property
    def event_count(self) -> int:
        """Number of calendar events."""
        return len(self._state.get("calendar_events", []))

    @property
    def sent_email_count(self) -> int:
        """Number of emails sent during task."""
        return len(self._state.get("sent_emails", []))

    @property
    def created_event_count(self) -> int:
        """Number of events created during task."""
        return len(self._state.get("created_events", []))
