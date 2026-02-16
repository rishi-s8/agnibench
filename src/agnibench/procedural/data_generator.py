"""
Data generator that works backward from the DAG to plant consistent
data in the environment.

Ensures the environment data supports the expected execution path.
"""

import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

from agnibench.procedural.archetypes import DomainArchetypeSet
from agnibench.procedural.dag import DAGNode, NodeType, TaskDAG

# Name pools for generating entity data
FIRST_NAMES = [
    "Alice", "Bob", "Carol", "David", "Eve", "Frank", "Grace", "Henry",
    "Iris", "Jack", "Karen", "Leo", "Maria", "Nathan", "Olivia", "Paul",
    "Quinn", "Rachel", "Sam", "Tina", "Uma", "Victor", "Wendy", "Xavier",
]

LAST_NAMES = [
    "Johnson", "Smith", "Williams", "Brown", "Davis", "Miller", "Wilson",
    "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris",
    "Martin", "Thompson", "Garcia", "Martinez", "Robinson", "Clark",
]

DEPARTMENTS = ["Engineering", "Product", "Design", "Sales", "Marketing", "HR", "Finance", "Operations"]

TITLES = [
    "Software Engineer", "Senior Engineer", "Product Manager", "Lead Designer",
    "Sales Director", "Marketing Manager", "Engineering Manager", "VP of Engineering",
    "Data Scientist", "Technical Lead", "UX Researcher", "Account Executive",
]

EMAIL_SUBJECTS = [
    "Project Update - {topic}",
    "Re: {topic} Discussion",
    "{topic} Meeting Notes",
    "Follow-up: {topic}",
    "Action Items from {topic}",
    "Invitation: {topic} Review",
    "{topic} - Urgent",
    "Feedback on {topic}",
]

TOPICS = [
    "Q4 Planning", "Product Launch", "Budget Review", "Team Sync",
    "Feature Request", "Design Review", "Sprint Retrospective",
    "Customer Feedback", "Roadmap Update", "Architecture Review",
    "Performance Review", "Data Migration", "API Redesign",
]

SLACK_CHANNELS = ["#general", "#engineering", "#design", "#product", "#random", "#announcements"]

EMAIL_BODIES = [
    "Hi,\n\nI wanted to discuss {topic}. Can we find time to meet?\n\nBest,\n{sender}",
    "Hello,\n\nPlease review the attached {topic} document. Let me know your thoughts.\n\nThanks,\n{sender}",
    "Team,\n\nHere are the updates on {topic}:\n1. Progress on key deliverables\n2. Blockers identified\n3. Next steps\n\nRegards,\n{sender}",
    "Hi there,\n\nFollowing up on our conversation about {topic}. I've updated the requirements.\n\n{sender}",
]


class DataGenerator:
    """
    Generates workspace environment data consistent with a TaskDAG.

    Works backward from the DAG to ensure all data the tools expect to find
    actually exists in the environment.
    """

    def __init__(self, archetype_set: DomainArchetypeSet, seed: int):
        self.archetype_set = archetype_set
        self.rng = random.Random(seed)

    def _generate_person(self) -> Dict[str, Any]:
        """Generate a random person entity."""
        first = self.rng.choice(FIRST_NAMES)
        last = self.rng.choice(LAST_NAMES)
        name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}@company.com"
        dept = self.rng.choice(DEPARTMENTS)
        title = self.rng.choice(TITLES)
        return {
            "name": name,
            "email": email,
            "department": dept,
            "title": title,
            "first_name": first,
            "last_name": last,
        }

    def _generate_email(
        self,
        sender_info: Dict[str, Any],
        topic: str,
        email_id: str,
        unread: bool = True,
        hours_ago: int = 3,
    ) -> Dict[str, Any]:
        """Generate an email record."""
        now = datetime.now()
        subject_template = self.rng.choice(EMAIL_SUBJECTS)
        body_template = self.rng.choice(EMAIL_BODIES)

        return {
            "id": email_id,
            "sender": sender_info["name"],
            "sender_email": sender_info["email"],
            "recipient": "You",
            "recipient_email": "me@company.com",
            "subject": subject_template.format(topic=topic),
            "body": body_template.format(topic=topic, sender=sender_info["first_name"]),
            "timestamp": (now - timedelta(hours=hours_ago)).isoformat(),
            "read": not unread,
            "labels": ["inbox"] + (["important"] if self.rng.random() < 0.3 else []),
        }

    def _generate_calendar_event(
        self,
        title: str,
        attendees: List[str],
        days_from_now: int = 1,
        hour: int = 10,
        duration_hours: int = 1,
    ) -> Dict[str, Any]:
        """Generate a calendar event record."""
        now = datetime.now()
        start = (now + timedelta(days=days_from_now)).replace(
            hour=hour, minute=0, second=0, microsecond=0
        )
        end = start + timedelta(hours=duration_hours)

        return {
            "id": f"event_existing_{self.rng.randint(100, 999)}",
            "title": title,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "attendees": attendees,
            "location": self.rng.choice(["Conference Room A", "Virtual", "Office 301"]),
            "description": f"{title} meeting",
            "organizer": attendees[0] if attendees else "Unknown",
            "status": "confirmed",
        }

    def _generate_slack_message(
        self,
        sender_name: str,
        channel: str,
        content: str,
        hours_ago: int = 2,
    ) -> Dict[str, Any]:
        """Generate a Slack message record."""
        now = datetime.now()
        return {
            "id": f"slack_{self.rng.randint(100, 999)}",
            "channel": channel,
            "sender": sender_name,
            "content": content,
            "timestamp": (now - timedelta(hours=hours_ago)).isoformat(),
            "reactions": [],
            "thread_count": self.rng.randint(0, 5),
        }

    def _generate_contact(self, person: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a contact record from person info."""
        return {
            "id": f"contact_{self.rng.randint(100, 999)}",
            "name": person["name"],
            "email": person["email"],
            "phone": f"+1-555-{self.rng.randint(100,999)}-{self.rng.randint(1000,9999)}",
            "department": person["department"],
            "title": person["title"],
            "timezone": self.rng.choice(["PST", "EST", "CST", "UTC"]),
        }

    def generate(
        self,
        dag: TaskDAG,
    ) -> tuple:
        """
        Generate environment data and entity bindings consistent with a DAG.

        Returns:
            Tuple of (initial_state, entity_bindings) where:
            - initial_state: Dict to pass to environment.initialize()
            - entity_bindings: Dict mapping abstract roles to concrete values
        """
        entity_bindings: Dict[str, Any] = {}

        # Generate people that will be referenced
        num_people = max(3, min(dag.tool_call_count, 6))
        people = [self._generate_person() for _ in range(num_people)]

        # Ensure uniqueness by name
        seen_names = set()
        unique_people = []
        for p in people:
            if p["name"] not in seen_names:
                seen_names.add(p["name"])
                unique_people.append(p)
        people = unique_people

        entity_bindings["people"] = people
        entity_bindings["primary_person"] = people[0] if people else {}

        # Pick a topic for the task
        topic = self.rng.choice(TOPICS)
        entity_bindings["topic"] = topic

        # Generate emails
        emails = []
        # Generate emails from each person
        for i, person in enumerate(people[:3]):
            email = self._generate_email(
                sender_info=person,
                topic=topic if i == 0 else self.rng.choice(TOPICS),
                email_id=f"email_{i + 1}",
                unread=(i == 0),  # First email is unread
                hours_ago=self.rng.randint(1, 48),
            )
            emails.append(email)

        # Generate some additional emails for noise
        for i in range(2):
            noise_person = self._generate_person()
            emails.append(self._generate_email(
                sender_info=noise_person,
                topic=self.rng.choice(TOPICS),
                email_id=f"email_noise_{i + 1}",
                unread=self.rng.random() < 0.3,
                hours_ago=self.rng.randint(24, 96),
            ))

        entity_bindings["primary_email"] = emails[0] if emails else {}

        # Generate calendar events
        now = datetime.now()
        tomorrow = (now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)

        calendar_events = []
        # A few events with known people
        calendar_events.append(self._generate_calendar_event(
            title="Team Standup",
            attendees=[p["name"] for p in people[:3]],
            days_from_now=1,
            hour=10,
        ))
        calendar_events.append(self._generate_calendar_event(
            title=f"{topic} Meeting",
            attendees=[people[0]["name"]] if people else [],
            days_from_now=1,
            hour=14,
        ))
        # Add some busy slots for availability checking
        calendar_events.append(self._generate_calendar_event(
            title="Existing Meeting",
            attendees=[people[0]["name"]] if people else [],
            days_from_now=1,
            hour=11,
        ))

        entity_bindings["tomorrow_date"] = (now + timedelta(days=1)).strftime("%Y-%m-%d")

        # Generate slack messages
        slack_messages = []
        for i, person in enumerate(people[:2]):
            channel = self.rng.choice(SLACK_CHANNELS)
            slack_messages.append(self._generate_slack_message(
                sender_name=person["name"],
                channel=channel,
                content=f"Update on {topic}: things are progressing well.",
                hours_ago=self.rng.randint(1, 24),
            ))

        # Generate contacts
        contacts = [self._generate_contact(person) for person in people]

        # Build initial state
        initial_state = {
            "emails": emails,
            "calendar_events": calendar_events,
            "slack_messages": slack_messages,
            "contacts": contacts,
            "sent_emails": [],
            "created_events": [],
            "sent_slack": [],
        }

        # Bind archetype-specific values based on DAG tool nodes
        tool_nodes = dag.get_tool_call_nodes()
        for node in tool_nodes:
            archetype = self.archetype_set.get_archetype(node.archetype_id)
            if archetype is None:
                continue

            # Populate static params based on archetype type
            if archetype.archetype_id == "search_emails":
                node.static_params["search_query"] = topic
                if people:
                    node.static_params["email_sender_filter"] = people[0]["name"]
                entity_bindings.setdefault("search_query", topic)

            elif archetype.archetype_id == "read_email":
                node.static_params["email_id"] = emails[0]["id"] if emails else "email_1"

            elif archetype.archetype_id == "send_email":
                if people:
                    node.static_params["recipient_email"] = people[0]["email"]
                    node.static_params["email_subject"] = f"Re: {emails[0]['subject']}" if emails else f"Re: {topic}"
                    entity_bindings["reply_subject"] = node.static_params["email_subject"]

            elif archetype.archetype_id == "search_calendar":
                node.static_params["calendar_query"] = topic

            elif archetype.archetype_id == "create_event":
                node.static_params["event_title"] = f"{topic} Follow-up"
                tomorrow_10am = (now + timedelta(days=1)).replace(hour=15, minute=0, second=0, microsecond=0)
                node.static_params["event_start"] = tomorrow_10am.isoformat()
                node.static_params["event_end"] = (tomorrow_10am + timedelta(hours=1)).isoformat()
                if people:
                    node.static_params["event_attendees"] = [people[0]["email"]]

            elif archetype.archetype_id == "check_availability":
                if people:
                    node.static_params["availability_attendees"] = [people[0]["name"]]
                node.static_params["availability_date"] = entity_bindings.get(
                    "tomorrow_date", (now + timedelta(days=1)).strftime("%Y-%m-%d")
                )

            elif archetype.archetype_id == "search_slack":
                node.static_params["search_query"] = topic

            elif archetype.archetype_id == "send_slack":
                node.static_params["slack_channel_required"] = self.rng.choice(SLACK_CHANNELS)
                entity_bindings["slack_channel"] = node.static_params["slack_channel_required"]

            elif archetype.archetype_id == "lookup_contact":
                if people:
                    node.static_params["contact_name"] = people[0]["name"]

        return initial_state, entity_bindings
