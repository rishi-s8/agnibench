"""
Tools for the workspace benchmark suite.

Provides 10 tools for email, calendar, Slack, and contact management.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from agentbuilder.Tools.base import Tool, Response


# Storage for simulated data (populated by environment)
_workspace_data: Dict[str, Any] = {
    "emails": [],
    "calendar_events": [],
    "slack_messages": [],
    "contacts": [],
    "sent_emails": [],
    "created_events": [],
    "sent_slack": [],
}


def set_workspace_data(data: Dict[str, Any]) -> None:
    """Set the workspace data (called by environment)."""
    global _workspace_data
    _workspace_data = data


def get_workspace_data() -> Dict[str, Any]:
    """Get current workspace data."""
    return _workspace_data


# Pydantic models for tool parameters

class SearchEmailsParams(BaseModel):
    """Parameters for searching emails."""
    query: Optional[str] = Field(default=None, description="Text to search in subject/body")
    sender: Optional[str] = Field(default=None, description="Filter by sender name or email")
    date_from: Optional[str] = Field(default=None, description="Start date (ISO format)")
    date_to: Optional[str] = Field(default=None, description="End date (ISO format)")
    unread_only: bool = Field(default=False, description="Only return unread emails")
    limit: int = Field(default=10, description="Maximum results to return")


class ReadEmailParams(BaseModel):
    """Parameters for reading a specific email."""
    email_id: str = Field(description="ID of the email to read")


class SendEmailParams(BaseModel):
    """Parameters for sending an email."""
    to: str = Field(description="Recipient email address")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body content")
    reply_to: Optional[str] = Field(default=None, description="Email ID if this is a reply")


class SearchCalendarParams(BaseModel):
    """Parameters for searching calendar events."""
    query: Optional[str] = Field(default=None, description="Text to search in title/description")
    date_from: Optional[str] = Field(default=None, description="Start date (ISO format)")
    date_to: Optional[str] = Field(default=None, description="End date (ISO format)")
    attendee: Optional[str] = Field(default=None, description="Filter by attendee name")
    include_cancelled: bool = Field(default=False, description="Include cancelled events (default: False)")


class CreateEventParams(BaseModel):
    """Parameters for creating a calendar event."""
    title: str = Field(description="Event title")
    start_time: str = Field(description="Start time (ISO format)")
    end_time: str = Field(description="End time (ISO format)")
    attendees: List[str] = Field(default_factory=list, description="List of attendee emails")
    location: Optional[str] = Field(default=None, description="Event location")
    description: Optional[str] = Field(default=None, description="Event description")


class CheckAvailabilityParams(BaseModel):
    """Parameters for checking attendee availability."""
    attendees: List[str] = Field(description="List of attendee names or emails")
    date: str = Field(description="Date to check (ISO format, date only)")
    duration_minutes: int = Field(default=60, description="Desired meeting duration")


class SearchSlackParams(BaseModel):
    """Parameters for searching Slack messages."""
    query: Optional[str] = Field(default=None, description="Text to search")
    channel: Optional[str] = Field(default=None, description="Channel name (e.g., #general)")
    sender: Optional[str] = Field(default=None, description="Message author")
    limit: int = Field(default=10, description="Maximum results")


class SendSlackParams(BaseModel):
    """Parameters for sending a Slack message."""
    channel: str = Field(description="Channel name (e.g., #general) or user for DM")
    message: str = Field(description="Message content")
    thread_ts: Optional[str] = Field(default=None, description="Thread timestamp for replies")


class WebSearchParams(BaseModel):
    """Parameters for web search."""
    query: str = Field(description="Search query")
    limit: int = Field(default=5, description="Maximum results")


class LookupContactParams(BaseModel):
    """Parameters for looking up a contact."""
    name: Optional[str] = Field(default=None, description="Contact name to search")
    email: Optional[str] = Field(default=None, description="Contact email to search")
    department: Optional[str] = Field(default=None, description="Filter by department")


# Tool implementation functions

def search_emails(params: SearchEmailsParams) -> Dict[str, Any]:
    """Search emails with various filters."""
    emails = _workspace_data.get("emails", [])
    results = []

    for email in emails:
        # Apply filters
        if params.query:
            query_lower = params.query.lower()
            if (query_lower not in email.get("subject", "").lower() and
                query_lower not in email.get("body", "").lower()):
                continue

        if params.sender:
            sender_lower = params.sender.lower()
            if (sender_lower not in email.get("sender", "").lower() and
                sender_lower not in email.get("sender_email", "").lower()):
                continue

        if params.unread_only and email.get("read", True):
            continue

        if params.date_from:
            try:
                email_date = datetime.fromisoformat(email.get("timestamp", ""))
                from_date = datetime.fromisoformat(params.date_from)
                if email_date < from_date:
                    continue
            except ValueError:
                pass

        if params.date_to:
            try:
                email_date = datetime.fromisoformat(email.get("timestamp", ""))
                to_date = datetime.fromisoformat(params.date_to)
                if email_date > to_date:
                    continue
            except ValueError:
                pass

        results.append({
            "id": email.get("id"),
            "sender": email.get("sender"),
            "subject": email.get("subject"),
            "timestamp": email.get("timestamp"),
            "read": email.get("read"),
            "preview": email.get("body", "")[:100] + "..." if len(email.get("body", "")) > 100 else email.get("body", "")
        })

        if len(results) >= params.limit:
            break

    return {
        "results": results,
        "count": len(results),
        "total_matches": len(results),
    }


def read_email(params: ReadEmailParams) -> Dict[str, Any]:
    """Read a specific email by ID."""
    emails = _workspace_data.get("emails", [])

    for email in emails:
        if email.get("id") == params.email_id:
            return {
                "found": True,
                "email": email
            }

    return {
        "found": False,
        "error": f"Email with ID '{params.email_id}' not found"
    }


def send_email(params: SendEmailParams) -> Dict[str, Any]:
    """Send an email."""
    email = {
        "id": f"sent_{len(_workspace_data.get('sent_emails', []))+1}",
        "to": params.to,
        "subject": params.subject,
        "body": params.body,
        "reply_to": params.reply_to,
        "sent_at": datetime.now().isoformat(),
        "status": "sent"
    }

    if "sent_emails" not in _workspace_data:
        _workspace_data["sent_emails"] = []
    _workspace_data["sent_emails"].append(email)

    return {
        "success": True,
        "email_id": email["id"],
        "message": f"Email sent to {params.to}"
    }


def search_calendar(params: SearchCalendarParams) -> Dict[str, Any]:
    """Search calendar events."""
    events = _workspace_data.get("calendar_events", [])
    results = []

    for event in events:
        # Filter out cancelled events by default
        if not params.include_cancelled and event.get("status") == "cancelled":
            continue

        if params.query:
            query_lower = params.query.lower()
            if (query_lower not in event.get("title", "").lower() and
                query_lower not in event.get("description", "").lower()):
                continue

        if params.attendee:
            attendee_lower = params.attendee.lower()
            attendees = [a.lower() for a in event.get("attendees", [])]
            if not any(attendee_lower in a for a in attendees):
                continue

        if params.date_from:
            try:
                event_date = datetime.fromisoformat(event.get("start_time", ""))
                from_date = datetime.fromisoformat(params.date_from)
                if event_date.date() < from_date.date():
                    continue
            except ValueError:
                pass

        if params.date_to:
            try:
                event_date = datetime.fromisoformat(event.get("start_time", ""))
                to_date = datetime.fromisoformat(params.date_to)
                if event_date.date() > to_date.date():
                    continue
            except ValueError:
                pass

        results.append(event)

    return {
        "results": results,
        "count": len(results)
    }


def create_event(params: CreateEventParams) -> Dict[str, Any]:
    """Create a calendar event."""
    event = {
        "id": f"event_{len(_workspace_data.get('created_events', []))+1}",
        "title": params.title,
        "start_time": params.start_time,
        "end_time": params.end_time,
        "attendees": params.attendees,
        "location": params.location,
        "description": params.description,
        "created_at": datetime.now().isoformat(),
        "status": "confirmed"
    }

    if "created_events" not in _workspace_data:
        _workspace_data["created_events"] = []
    _workspace_data["created_events"].append(event)

    return {
        "success": True,
        "event_id": event["id"],
        "message": f"Event '{params.title}' created",
        "event": event
    }


def check_availability(params: CheckAvailabilityParams) -> Dict[str, Any]:
    """Check availability for attendees on a given date."""
    events = _workspace_data.get("calendar_events", [])
    availability = {}

    try:
        check_date = datetime.fromisoformat(params.date).date()
    except ValueError:
        return {"error": f"Invalid date format: {params.date}"}

    for attendee in params.attendees:
        attendee_lower = attendee.lower()
        busy_slots = []

        for event in events:
            event_attendees = [a.lower() for a in event.get("attendees", [])]
            if any(attendee_lower in a for a in event_attendees):
                try:
                    start = datetime.fromisoformat(event.get("start_time", ""))
                    end = datetime.fromisoformat(event.get("end_time", ""))
                    if start.date() == check_date:
                        busy_slots.append({
                            "start": start.strftime("%H:%M"),
                            "end": end.strftime("%H:%M"),
                            "title": event.get("title")
                        })
                except ValueError:
                    continue

        # Find free slots (simplified: 9am-5pm working hours)
        free_slots = []
        work_start = 9
        work_end = 17
        busy_sorted = sorted(busy_slots, key=lambda x: x["start"])

        current_time = work_start
        for slot in busy_sorted:
            slot_start = int(slot["start"].split(":")[0])
            if current_time < slot_start:
                free_slots.append({
                    "start": f"{current_time:02d}:00",
                    "end": f"{slot_start:02d}:00"
                })
            slot_end = int(slot["end"].split(":")[0])
            current_time = max(current_time, slot_end)

        if current_time < work_end:
            free_slots.append({
                "start": f"{current_time:02d}:00",
                "end": f"{work_end:02d}:00"
            })

        availability[attendee] = {
            "busy_slots": busy_slots,
            "free_slots": free_slots
        }

    # Find common free times
    if len(params.attendees) > 1:
        # Simplified: find overlapping free slots
        common_free = []
        first_attendee = params.attendees[0]
        for slot in availability.get(first_attendee, {}).get("free_slots", []):
            is_common = True
            for other in params.attendees[1:]:
                other_free = availability.get(other, {}).get("free_slots", [])
                # Check if this slot overlaps with any free slot of other attendee
                overlap = False
                for other_slot in other_free:
                    if (slot["start"] < other_slot["end"] and
                        slot["end"] > other_slot["start"]):
                        overlap = True
                        break
                if not overlap:
                    is_common = False
                    break
            if is_common:
                common_free.append(slot)

        return {
            "date": params.date,
            "attendees": params.attendees,
            "individual_availability": availability,
            "common_free_slots": common_free,
            "duration_requested": params.duration_minutes
        }

    return {
        "date": params.date,
        "attendees": params.attendees,
        "availability": availability,
        "duration_requested": params.duration_minutes
    }


def search_slack(params: SearchSlackParams) -> Dict[str, Any]:
    """Search Slack messages."""
    messages = _workspace_data.get("slack_messages", [])
    results = []

    for msg in messages:
        if params.query:
            if params.query.lower() not in msg.get("content", "").lower():
                continue

        if params.channel:
            if params.channel.lower() not in msg.get("channel", "").lower():
                continue

        if params.sender:
            if params.sender.lower() not in msg.get("sender", "").lower():
                continue

        results.append(msg)

        if len(results) >= params.limit:
            break

    return {
        "results": results,
        "count": len(results)
    }


def send_slack(params: SendSlackParams) -> Dict[str, Any]:
    """Send a Slack message."""
    message = {
        "id": f"slack_{len(_workspace_data.get('sent_slack', []))+1}",
        "channel": params.channel,
        "message": params.message,
        "thread_ts": params.thread_ts,
        "sent_at": datetime.now().isoformat(),
    }

    if "sent_slack" not in _workspace_data:
        _workspace_data["sent_slack"] = []
    _workspace_data["sent_slack"].append(message)

    return {
        "success": True,
        "message_id": message["id"],
        "channel": params.channel
    }


def web_search(params: WebSearchParams) -> Dict[str, Any]:
    """Perform a web search (simulated)."""
    # Return simulated search results based on query
    results = [
        {
            "title": f"Result for: {params.query}",
            "url": f"https://example.com/search?q={params.query.replace(' ', '+')}",
            "snippet": f"Information about {params.query}..."
        }
    ]

    return {
        "query": params.query,
        "results": results[:params.limit],
        "count": len(results)
    }


def lookup_contact(params: LookupContactParams) -> Dict[str, Any]:
    """Look up contact information."""
    contacts = _workspace_data.get("contacts", [])
    results = []

    for contact in contacts:
        if params.name:
            if params.name.lower() not in contact.get("name", "").lower():
                continue

        if params.email:
            if params.email.lower() not in contact.get("email", "").lower():
                continue

        if params.department:
            if params.department.lower() not in contact.get("department", "").lower():
                continue

        results.append(contact)

    if len(results) == 1:
        return {
            "found": True,
            "contact": results[0]
        }
    elif len(results) > 1:
        return {
            "found": True,
            "multiple_matches": True,
            "contacts": results
        }
    else:
        return {
            "found": False,
            "message": "No matching contacts found"
        }


# Tool creation

def get_workspace_tools() -> List[Tool]:
    """Get all workspace tools."""
    return [
        Tool(
            name="search_emails",
            description="Search emails by query, sender, date range, or read status. Returns email previews.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Text to search in subject/body"},
                    "sender": {"type": "string", "description": "Filter by sender name or email"},
                    "date_from": {"type": "string", "description": "Start date (ISO format)"},
                    "date_to": {"type": "string", "description": "End date (ISO format)"},
                    "unread_only": {"type": "boolean", "description": "Only return unread emails", "default": False},
                    "limit": {"type": "integer", "description": "Maximum results", "default": 10}
                },
                "required": []
            },
            function=lambda **kwargs: search_emails(SearchEmailsParams(**kwargs))
        ),
        Tool(
            name="read_email",
            description="Read the full content of a specific email by its ID.",
            parameters={
                "type": "object",
                "properties": {
                    "email_id": {"type": "string", "description": "ID of the email to read"}
                },
                "required": ["email_id"]
            },
            function=lambda **kwargs: read_email(ReadEmailParams(**kwargs))
        ),
        Tool(
            name="send_email",
            description="Send an email to a recipient. Can be a new email or a reply.",
            parameters={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body content"},
                    "reply_to": {"type": "string", "description": "Email ID if this is a reply"}
                },
                "required": ["to", "subject", "body"]
            },
            function=lambda **kwargs: send_email(SendEmailParams(**kwargs))
        ),
        Tool(
            name="search_calendar",
            description="Search calendar events by query, date range, or attendee. Cancelled events are excluded by default.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Text to search in title/description"},
                    "date_from": {"type": "string", "description": "Start date (ISO format)"},
                    "date_to": {"type": "string", "description": "End date (ISO format)"},
                    "attendee": {"type": "string", "description": "Filter by attendee name"},
                    "include_cancelled": {"type": "boolean", "description": "Include cancelled events", "default": False}
                },
                "required": []
            },
            function=lambda **kwargs: search_calendar(SearchCalendarParams(**kwargs))
        ),
        Tool(
            name="create_event",
            description="Create a new calendar event with attendees.",
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Event title"},
                    "start_time": {"type": "string", "description": "Start time (ISO format)"},
                    "end_time": {"type": "string", "description": "End time (ISO format)"},
                    "attendees": {"type": "array", "items": {"type": "string"}, "description": "List of attendee emails"},
                    "location": {"type": "string", "description": "Event location"},
                    "description": {"type": "string", "description": "Event description"}
                },
                "required": ["title", "start_time", "end_time"]
            },
            function=lambda **kwargs: create_event(CreateEventParams(**kwargs))
        ),
        Tool(
            name="check_availability",
            description="Check calendar availability for one or more attendees on a specific date. Returns busy and free time slots.",
            parameters={
                "type": "object",
                "properties": {
                    "attendees": {"type": "array", "items": {"type": "string"}, "description": "List of attendee names or emails"},
                    "date": {"type": "string", "description": "Date to check (ISO format, date only)"},
                    "duration_minutes": {"type": "integer", "description": "Desired meeting duration", "default": 60}
                },
                "required": ["attendees", "date"]
            },
            function=lambda **kwargs: check_availability(CheckAvailabilityParams(**kwargs))
        ),
        Tool(
            name="search_slack",
            description="Search Slack messages by query, channel, or sender.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Text to search"},
                    "channel": {"type": "string", "description": "Channel name (e.g., #general)"},
                    "sender": {"type": "string", "description": "Message author"},
                    "limit": {"type": "integer", "description": "Maximum results", "default": 10}
                },
                "required": []
            },
            function=lambda **kwargs: search_slack(SearchSlackParams(**kwargs))
        ),
        Tool(
            name="send_slack",
            description="Send a Slack message to a channel or user.",
            parameters={
                "type": "object",
                "properties": {
                    "channel": {"type": "string", "description": "Channel name (e.g., #general) or username for DM"},
                    "message": {"type": "string", "description": "Message content"},
                    "thread_ts": {"type": "string", "description": "Thread timestamp for replies"}
                },
                "required": ["channel", "message"]
            },
            function=lambda **kwargs: send_slack(SendSlackParams(**kwargs))
        ),
        Tool(
            name="web_search",
            description="Search the web for information.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Maximum results", "default": 5}
                },
                "required": ["query"]
            },
            function=lambda **kwargs: web_search(WebSearchParams(**kwargs))
        ),
        Tool(
            name="lookup_contact",
            description="Look up contact information by name, email, or department.",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Contact name to search"},
                    "email": {"type": "string", "description": "Contact email to search"},
                    "department": {"type": "string", "description": "Filter by department"}
                },
                "required": []
            },
            function=lambda **kwargs: lookup_contact(LookupContactParams(**kwargs))
        ),
    ]
