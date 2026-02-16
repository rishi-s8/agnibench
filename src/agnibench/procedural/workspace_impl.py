"""
Canonical implementations for workspace tools.

These are closure-based (not module-level globals) — each receives a data_store
dict that is shared across all tools in a single procedural environment instance.
"""

from datetime import datetime
from typing import Any, Callable, Dict, List


def _make_search_emails(data_store: Dict[str, Any]) -> Callable:
    """Create search_emails implementation bound to data_store."""

    def impl(
        search_query: str = None,
        email_sender_filter: str = None,
        date_from: str = None,
        date_to: str = None,
        unread_only: bool = False,
        result_limit: int = 10,
    ) -> Dict[str, Any]:
        emails = data_store.get("emails", [])
        results = []

        for email in emails:
            if search_query:
                q = search_query.lower()
                if (
                    q not in email.get("subject", "").lower()
                    and q not in email.get("body", "").lower()
                ):
                    continue

            if email_sender_filter:
                s = email_sender_filter.lower()
                if (
                    s not in email.get("sender", "").lower()
                    and s not in email.get("sender_email", "").lower()
                ):
                    continue

            if unread_only and email.get("read", True):
                continue

            if date_from:
                try:
                    email_date = datetime.fromisoformat(email.get("timestamp", ""))
                    from_date = datetime.fromisoformat(date_from)
                    if email_date < from_date:
                        continue
                except ValueError:
                    pass

            if date_to:
                try:
                    email_date = datetime.fromisoformat(email.get("timestamp", ""))
                    to_date = datetime.fromisoformat(date_to)
                    if email_date > to_date:
                        continue
                except ValueError:
                    pass

            body = email.get("body", "")
            results.append({
                "id": email.get("id"),
                "sender": email.get("sender"),
                "subject": email.get("subject"),
                "timestamp": email.get("timestamp"),
                "read": email.get("read"),
                "preview": body[:100] + "..." if len(body) > 100 else body,
            })

            if len(results) >= result_limit:
                break

        return {"results": results, "count": len(results), "total_matches": len(results)}

    return impl


def _make_read_email(data_store: Dict[str, Any]) -> Callable:
    """Create read_email implementation bound to data_store."""

    def impl(email_id: str) -> Dict[str, Any]:
        emails = data_store.get("emails", [])
        for email in emails:
            if email.get("id") == email_id:
                return {"found": True, "email": email}
        return {"found": False, "error": f"Email with ID '{email_id}' not found"}

    return impl


def _make_send_email(data_store: Dict[str, Any]) -> Callable:
    """Create send_email implementation bound to data_store."""

    def impl(
        recipient_email: str,
        email_subject: str,
        email_body: str,
        reply_to_id: str = None,
    ) -> Dict[str, Any]:
        if "sent_emails" not in data_store:
            data_store["sent_emails"] = []

        email = {
            "id": f"sent_{len(data_store['sent_emails']) + 1}",
            "to": recipient_email,
            "subject": email_subject,
            "body": email_body,
            "reply_to": reply_to_id,
            "sent_at": datetime.now().isoformat(),
            "status": "sent",
        }
        data_store["sent_emails"].append(email)
        return {"success": True, "email_id": email["id"], "message": f"Email sent to {recipient_email}"}

    return impl


def _make_search_calendar(data_store: Dict[str, Any]) -> Callable:
    """Create search_calendar implementation bound to data_store."""

    def impl(
        calendar_query: str = None,
        date_from: str = None,
        date_to: str = None,
        attendee_filter: str = None,
        include_cancelled: bool = False,
    ) -> Dict[str, Any]:
        events = data_store.get("calendar_events", [])
        results = []

        for event in events:
            if not include_cancelled and event.get("status") == "cancelled":
                continue

            if calendar_query:
                q = calendar_query.lower()
                if (
                    q not in event.get("title", "").lower()
                    and q not in event.get("description", "").lower()
                ):
                    continue

            if attendee_filter:
                af = attendee_filter.lower()
                attendees = [a.lower() for a in event.get("attendees", [])]
                if not any(af in a for a in attendees):
                    continue

            if date_from:
                try:
                    event_date = datetime.fromisoformat(event.get("start_time", ""))
                    from_date = datetime.fromisoformat(date_from)
                    if event_date.date() < from_date.date():
                        continue
                except ValueError:
                    pass

            if date_to:
                try:
                    event_date = datetime.fromisoformat(event.get("start_time", ""))
                    to_date = datetime.fromisoformat(date_to)
                    if event_date.date() > to_date.date():
                        continue
                except ValueError:
                    pass

            results.append(event)

        return {"results": results, "count": len(results)}

    return impl


def _make_create_event(data_store: Dict[str, Any]) -> Callable:
    """Create create_event implementation bound to data_store."""

    def impl(
        event_title: str,
        event_start: str,
        event_end: str,
        event_attendees: List[str] = None,
        event_location: str = None,
        event_description: str = None,
    ) -> Dict[str, Any]:
        if "created_events" not in data_store:
            data_store["created_events"] = []

        event = {
            "id": f"event_{len(data_store['created_events']) + 1}",
            "title": event_title,
            "start_time": event_start,
            "end_time": event_end,
            "attendees": event_attendees or [],
            "location": event_location,
            "description": event_description,
            "created_at": datetime.now().isoformat(),
            "status": "confirmed",
        }
        data_store["created_events"].append(event)
        return {
            "success": True,
            "event_id": event["id"],
            "message": f"Event '{event_title}' created",
            "event": event,
        }

    return impl


def _make_check_availability(data_store: Dict[str, Any]) -> Callable:
    """Create check_availability implementation bound to data_store."""

    def impl(
        availability_attendees: List[str],
        availability_date: str,
        duration_minutes: int = 60,
    ) -> Dict[str, Any]:
        events = data_store.get("calendar_events", [])

        try:
            check_date = datetime.fromisoformat(availability_date).date()
        except ValueError:
            return {"error": f"Invalid date format: {availability_date}"}

        availability = {}
        for attendee in availability_attendees:
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
                                "title": event.get("title"),
                            })
                    except ValueError:
                        continue

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
                        "end": f"{slot_start:02d}:00",
                    })
                slot_end = int(slot["end"].split(":")[0])
                current_time = max(current_time, slot_end)

            if current_time < work_end:
                free_slots.append({
                    "start": f"{current_time:02d}:00",
                    "end": f"{work_end:02d}:00",
                })

            availability[attendee] = {
                "busy_slots": busy_slots,
                "free_slots": free_slots,
            }

        # Find common free times
        common_free = None
        if len(availability_attendees) > 1:
            common_free = []
            first = availability_attendees[0]
            for slot in availability.get(first, {}).get("free_slots", []):
                is_common = True
                for other in availability_attendees[1:]:
                    other_free = availability.get(other, {}).get("free_slots", [])
                    overlap = False
                    for other_slot in other_free:
                        if slot["start"] < other_slot["end"] and slot["end"] > other_slot["start"]:
                            overlap = True
                            break
                    if not overlap:
                        is_common = False
                        break
                if is_common:
                    common_free.append(slot)

        result = {
            "date": availability_date,
            "attendees": availability_attendees,
            "duration_requested": duration_minutes,
        }
        if common_free is not None:
            result["individual_availability"] = availability
            result["common_free_slots"] = common_free
        else:
            result["availability"] = availability
        return result

    return impl


def _make_search_slack(data_store: Dict[str, Any]) -> Callable:
    """Create search_slack implementation bound to data_store."""

    def impl(
        search_query: str = None,
        slack_channel: str = None,
        slack_sender: str = None,
        result_limit: int = 10,
    ) -> Dict[str, Any]:
        messages = data_store.get("slack_messages", [])
        results = []

        for msg in messages:
            if search_query:
                if search_query.lower() not in msg.get("content", "").lower():
                    continue
            if slack_channel:
                if slack_channel.lower() not in msg.get("channel", "").lower():
                    continue
            if slack_sender:
                if slack_sender.lower() not in msg.get("sender", "").lower():
                    continue

            results.append(msg)
            if len(results) >= result_limit:
                break

        return {"results": results, "count": len(results)}

    return impl


def _make_send_slack(data_store: Dict[str, Any]) -> Callable:
    """Create send_slack implementation bound to data_store."""

    def impl(
        slack_channel_required: str,
        slack_message: str,
        slack_thread_ts: str = None,
    ) -> Dict[str, Any]:
        if "sent_slack" not in data_store:
            data_store["sent_slack"] = []

        message = {
            "id": f"slack_{len(data_store['sent_slack']) + 1}",
            "channel": slack_channel_required,
            "message": slack_message,
            "thread_ts": slack_thread_ts,
            "sent_at": datetime.now().isoformat(),
        }
        data_store["sent_slack"].append(message)
        return {"success": True, "message_id": message["id"], "channel": slack_channel_required}

    return impl


def _make_web_search(data_store: Dict[str, Any]) -> Callable:
    """Create web_search implementation bound to data_store."""

    def impl(web_query: str, result_limit: int = 5) -> Dict[str, Any]:
        results = [{
            "title": f"Result for: {web_query}",
            "url": f"https://example.com/search?q={web_query.replace(' ', '+')}",
            "snippet": f"Information about {web_query}...",
        }]
        return {"query": web_query, "results": results[:result_limit], "count": len(results)}

    return impl


def _make_lookup_contact(data_store: Dict[str, Any]) -> Callable:
    """Create lookup_contact implementation bound to data_store."""

    def impl(
        contact_name: str = None,
        contact_email: str = None,
        contact_department: str = None,
    ) -> Dict[str, Any]:
        contacts = data_store.get("contacts", [])
        results = []

        for contact in contacts:
            if contact_name:
                if contact_name.lower() not in contact.get("name", "").lower():
                    continue
            if contact_email:
                if contact_email.lower() not in contact.get("email", "").lower():
                    continue
            if contact_department:
                if contact_department.lower() not in contact.get("department", "").lower():
                    continue
            results.append(contact)

        if len(results) == 1:
            return {"found": True, "contact": results[0]}
        elif len(results) > 1:
            return {"found": True, "multiple_matches": True, "contacts": results}
        else:
            return {"found": False, "message": "No matching contacts found"}

    return impl


# Registry mapping behavior_key -> factory function
WORKSPACE_IMPL_REGISTRY: Dict[str, Callable[[Dict[str, Any]], Callable]] = {
    "search_emails": _make_search_emails,
    "read_email": _make_read_email,
    "send_email": _make_send_email,
    "search_calendar": _make_search_calendar,
    "create_event": _make_create_event,
    "check_availability": _make_check_availability,
    "search_slack": _make_search_slack,
    "send_slack": _make_send_slack,
    "web_search": _make_web_search,
    "lookup_contact": _make_lookup_contact,
}
