"""
Workspace-domain tool archetypes with name/parameter variant pools.

Defines all 10 workspace tool archetypes matching the existing workspace suite
capabilities, but with multiple surface variations for each.
"""

from agnibench.procedural.archetypes import (
    DomainArchetypeSet,
    ParameterArchetype,
    ToolArchetype,
)

# --- Parameter archetype definitions ---

_SEARCH_QUERY = ParameterArchetype(
    semantic_role="search_query",
    data_type="string",
    required=False,
    name_variants=["query", "search_term", "keywords", "q", "search_text", "filter_text"],
    description_templates=[
        "Text to search for",
        "Search query string",
        "Keywords to match",
        "Filter text to search in content",
    ],
)

_EMAIL_SENDER_FILTER = ParameterArchetype(
    semantic_role="email_sender_filter",
    data_type="string",
    required=False,
    name_variants=["sender", "from_address", "sent_by", "from_name", "author", "from_email"],
    description_templates=[
        "Filter by sender name or email",
        "Only show emails from this sender",
        "Sender to filter by",
    ],
)

_DATE_FROM = ParameterArchetype(
    semantic_role="date_from",
    data_type="string",
    required=False,
    name_variants=["date_from", "start_date", "from_date", "after_date", "since"],
    description_templates=[
        "Start date (ISO format)",
        "Only include results after this date",
        "Filter start date",
    ],
)

_DATE_TO = ParameterArchetype(
    semantic_role="date_to",
    data_type="string",
    required=False,
    name_variants=["date_to", "end_date", "to_date", "before_date", "until"],
    description_templates=[
        "End date (ISO format)",
        "Only include results before this date",
        "Filter end date",
    ],
)

_UNREAD_ONLY = ParameterArchetype(
    semantic_role="unread_only",
    data_type="boolean",
    required=False,
    default=False,
    name_variants=["unread_only", "unread", "only_unread", "filter_unread", "is_unread"],
    description_templates=[
        "Only return unread emails",
        "Filter to unread messages only",
        "If true, only show unread items",
    ],
)

_RESULT_LIMIT = ParameterArchetype(
    semantic_role="result_limit",
    data_type="integer",
    required=False,
    default=10,
    constraints={"min": 1, "max": 100},
    name_variants=["limit", "max_results", "count", "num_results", "top_n", "page_size"],
    description_templates=[
        "Maximum results to return",
        "Limit number of results",
        "How many results to fetch",
    ],
)

_EMAIL_ID = ParameterArchetype(
    semantic_role="email_id",
    data_type="string",
    required=True,
    name_variants=["email_id", "message_id", "mail_id", "id", "msg_id"],
    description_templates=[
        "ID of the email to read",
        "Unique identifier of the message",
        "Email message identifier",
    ],
)

_RECIPIENT_EMAIL = ParameterArchetype(
    semantic_role="recipient_email",
    data_type="string",
    required=True,
    name_variants=["to", "recipient", "to_address", "send_to", "dest_email", "to_email"],
    description_templates=[
        "Recipient email address",
        "Email address to send to",
        "Destination email address",
    ],
)

_EMAIL_SUBJECT = ParameterArchetype(
    semantic_role="email_subject",
    data_type="string",
    required=True,
    name_variants=["subject", "subject_line", "email_subject", "title", "topic"],
    description_templates=[
        "Email subject",
        "Subject line of the email",
        "Message subject",
    ],
)

_EMAIL_BODY = ParameterArchetype(
    semantic_role="email_body",
    data_type="string",
    required=True,
    name_variants=["body", "content", "message_body", "text", "email_content", "message_text"],
    description_templates=[
        "Email body content",
        "The message content",
        "Body text of the email",
    ],
)

_REPLY_TO_ID = ParameterArchetype(
    semantic_role="reply_to_id",
    data_type="string",
    required=False,
    name_variants=["reply_to", "in_reply_to", "parent_id", "original_email_id", "thread_id"],
    description_templates=[
        "Email ID if this is a reply",
        "ID of the original email being replied to",
        "Parent message ID for threading",
    ],
)

_CALENDAR_QUERY = ParameterArchetype(
    semantic_role="calendar_query",
    data_type="string",
    required=False,
    name_variants=["query", "search_term", "keywords", "title_search", "event_search"],
    description_templates=[
        "Text to search in event title/description",
        "Search query for calendar events",
        "Keywords to find in events",
    ],
)

_ATTENDEE_FILTER = ParameterArchetype(
    semantic_role="attendee_filter",
    data_type="string",
    required=False,
    name_variants=["attendee", "participant", "invitee", "person", "member"],
    description_templates=[
        "Filter by attendee name",
        "Only show events with this participant",
        "Attendee to filter by",
    ],
)

_INCLUDE_CANCELLED = ParameterArchetype(
    semantic_role="include_cancelled",
    data_type="boolean",
    required=False,
    default=False,
    name_variants=[
        "include_cancelled", "show_cancelled", "with_cancelled",
        "include_canceled", "show_all",
    ],
    description_templates=[
        "Include cancelled events",
        "Whether to show cancelled events (default: false)",
        "Set true to include cancelled events",
    ],
)

_EVENT_TITLE = ParameterArchetype(
    semantic_role="event_title",
    data_type="string",
    required=True,
    name_variants=["title", "event_name", "name", "subject", "meeting_title"],
    description_templates=[
        "Event title",
        "Name of the calendar event",
        "Meeting title",
    ],
)

_EVENT_START = ParameterArchetype(
    semantic_role="event_start",
    data_type="string",
    required=True,
    name_variants=["start_time", "start", "begins_at", "start_datetime", "from_time"],
    description_templates=[
        "Start time (ISO format)",
        "When the event begins",
        "Event start datetime",
    ],
)

_EVENT_END = ParameterArchetype(
    semantic_role="event_end",
    data_type="string",
    required=True,
    name_variants=["end_time", "end", "ends_at", "end_datetime", "to_time"],
    description_templates=[
        "End time (ISO format)",
        "When the event ends",
        "Event end datetime",
    ],
)

_EVENT_ATTENDEES = ParameterArchetype(
    semantic_role="event_attendees",
    data_type="array",
    required=False,
    default=[],
    name_variants=["attendees", "participants", "invitees", "guests", "members"],
    description_templates=[
        "List of attendee emails",
        "Participants to invite",
        "People to add to this event",
    ],
)

_EVENT_LOCATION = ParameterArchetype(
    semantic_role="event_location",
    data_type="string",
    required=False,
    name_variants=["location", "venue", "place", "room", "meeting_room"],
    description_templates=[
        "Event location",
        "Where the event takes place",
        "Meeting room or venue",
    ],
)

_EVENT_DESCRIPTION = ParameterArchetype(
    semantic_role="event_description",
    data_type="string",
    required=False,
    name_variants=["description", "notes", "details", "agenda", "event_notes"],
    description_templates=[
        "Event description",
        "Additional details about the event",
        "Meeting agenda or notes",
    ],
)

_AVAILABILITY_ATTENDEES = ParameterArchetype(
    semantic_role="availability_attendees",
    data_type="array",
    required=True,
    name_variants=["attendees", "people", "participants", "users", "check_for"],
    description_templates=[
        "List of attendee names or emails",
        "People to check availability for",
        "Who to check schedules for",
    ],
)

_AVAILABILITY_DATE = ParameterArchetype(
    semantic_role="availability_date",
    data_type="string",
    required=True,
    name_variants=["date", "check_date", "target_date", "day", "on_date"],
    description_templates=[
        "Date to check (ISO format, date only)",
        "Which date to check availability",
        "Target date for scheduling",
    ],
)

_DURATION_MINUTES = ParameterArchetype(
    semantic_role="duration_minutes",
    data_type="integer",
    required=False,
    default=60,
    constraints={"min": 15, "max": 480},
    name_variants=[
        "duration_minutes", "duration", "length_minutes",
        "meeting_length", "time_needed",
    ],
    description_templates=[
        "Desired meeting duration in minutes",
        "How long the meeting should be",
        "Required time slot duration",
    ],
)

_SLACK_CHANNEL = ParameterArchetype(
    semantic_role="slack_channel",
    data_type="string",
    required=False,
    name_variants=["channel", "slack_channel", "room", "chat_room", "channel_name"],
    description_templates=[
        "Channel name (e.g., #general)",
        "Slack channel to search/post in",
        "Chat channel name",
    ],
)

_SLACK_SENDER = ParameterArchetype(
    semantic_role="slack_sender",
    data_type="string",
    required=False,
    name_variants=["sender", "author", "from_user", "posted_by", "user"],
    description_templates=[
        "Message author",
        "Filter by who sent the message",
        "Sender username",
    ],
)

_SLACK_CHANNEL_REQUIRED = ParameterArchetype(
    semantic_role="slack_channel_required",
    data_type="string",
    required=True,
    name_variants=["channel", "to_channel", "target_channel", "room", "destination"],
    description_templates=[
        "Channel name (e.g., #general) or user for DM",
        "Where to send the message",
        "Target channel or user",
    ],
)

_SLACK_MESSAGE = ParameterArchetype(
    semantic_role="slack_message",
    data_type="string",
    required=True,
    name_variants=["message", "text", "content", "msg", "body", "message_text"],
    description_templates=[
        "Message content",
        "Text to send",
        "The message to post",
    ],
)

_SLACK_THREAD = ParameterArchetype(
    semantic_role="slack_thread_ts",
    data_type="string",
    required=False,
    name_variants=["thread_ts", "thread_id", "reply_to_thread", "parent_ts", "in_thread"],
    description_templates=[
        "Thread timestamp for replies",
        "Thread ID to reply in",
        "Parent message timestamp",
    ],
)

_WEB_QUERY = ParameterArchetype(
    semantic_role="web_query",
    data_type="string",
    required=True,
    name_variants=["query", "search_query", "q", "search_term", "keywords"],
    description_templates=[
        "Search query",
        "What to search for on the web",
        "Web search keywords",
    ],
)

_CONTACT_NAME = ParameterArchetype(
    semantic_role="contact_name",
    data_type="string",
    required=False,
    name_variants=["name", "person_name", "full_name", "contact_name", "who"],
    description_templates=[
        "Contact name to search",
        "Name of the person to look up",
        "Who to find",
    ],
)

_CONTACT_EMAIL = ParameterArchetype(
    semantic_role="contact_email",
    data_type="string",
    required=False,
    name_variants=["email", "email_address", "contact_email", "mail", "address"],
    description_templates=[
        "Contact email to search",
        "Email address to look up",
        "Search by email",
    ],
)

_CONTACT_DEPARTMENT = ParameterArchetype(
    semantic_role="contact_department",
    data_type="string",
    required=False,
    name_variants=["department", "dept", "team", "division", "group"],
    description_templates=[
        "Filter by department",
        "Department to search in",
        "Team or department name",
    ],
)


# --- Tool archetype definitions ---

SEARCH_EMAILS_ARCHETYPE = ToolArchetype(
    archetype_id="search_emails",
    category="query",
    semantic_description="Search emails by query, sender, date range, or read status",
    parameters=[_SEARCH_QUERY, _EMAIL_SENDER_FILTER, _DATE_FROM, _DATE_TO, _UNREAD_ONLY, _RESULT_LIMIT],
    returns={"results": "list[email_summary]", "count": "int", "total_matches": "int"},
    side_effects=[],
    name_variants=[
        "search_emails", "find_messages", "query_inbox", "search_mail",
        "filter_emails", "find_emails", "lookup_emails", "search_inbox",
    ],
    description_templates=[
        "Search emails by query, sender, date range, or read status. Returns email previews.",
        "Find messages in your inbox matching specified criteria.",
        "Query your email inbox with various filters. Returns matching email summaries.",
        "Search through emails using filters like sender, keywords, and date range.",
    ],
    behavior_key="search_emails",
)

READ_EMAIL_ARCHETYPE = ToolArchetype(
    archetype_id="read_email",
    category="lookup",
    semantic_description="Read the full content of a specific email by its ID",
    parameters=[_EMAIL_ID],
    returns={"found": "bool", "email": "dict|null", "error": "str|null"},
    side_effects=[],
    name_variants=[
        "read_email", "get_message", "fetch_email", "open_email",
        "view_message", "get_email", "read_message", "get_mail",
    ],
    description_templates=[
        "Read the full content of a specific email by its ID.",
        "Fetch a complete email message by identifier.",
        "Retrieve the full details of an email message.",
        "Open and read a specific email by its unique ID.",
    ],
    behavior_key="read_email",
)

SEND_EMAIL_ARCHETYPE = ToolArchetype(
    archetype_id="send_email",
    category="mutate",
    semantic_description="Send an email to a recipient",
    parameters=[_RECIPIENT_EMAIL, _EMAIL_SUBJECT, _EMAIL_BODY, _REPLY_TO_ID],
    returns={"success": "bool", "email_id": "str|null", "message": "str|null"},
    side_effects=["sent_emails"],
    name_variants=[
        "send_email", "compose_email", "send_mail", "dispatch_email",
        "send_message", "mail_to", "new_email", "deliver_email",
    ],
    description_templates=[
        "Send an email to a recipient. Can be a new email or a reply.",
        "Compose and send a new email message.",
        "Deliver an email to the specified recipient address.",
        "Send a new email or reply to an existing message.",
    ],
    behavior_key="send_email",
)

SEARCH_CALENDAR_ARCHETYPE = ToolArchetype(
    archetype_id="search_calendar",
    category="query",
    semantic_description="Search calendar events by query, date range, or attendee",
    parameters=[_CALENDAR_QUERY, _DATE_FROM, _DATE_TO, _ATTENDEE_FILTER, _INCLUDE_CANCELLED],
    returns={"results": "list[event]", "count": "int"},
    side_effects=[],
    name_variants=[
        "search_calendar", "find_events", "query_calendar", "list_events",
        "get_events", "search_events", "browse_calendar", "check_calendar",
    ],
    description_templates=[
        "Search calendar events by query, date range, or attendee.",
        "Find events on your calendar matching specified criteria.",
        "Query calendar entries filtered by various parameters.",
        "Browse calendar events. Cancelled events excluded by default.",
    ],
    behavior_key="search_calendar",
)

CREATE_EVENT_ARCHETYPE = ToolArchetype(
    archetype_id="create_event",
    category="mutate",
    semantic_description="Create a new calendar event",
    parameters=[
        _EVENT_TITLE, _EVENT_START, _EVENT_END,
        _EVENT_ATTENDEES, _EVENT_LOCATION, _EVENT_DESCRIPTION,
    ],
    returns={"success": "bool", "event_id": "str|null", "message": "str|null", "event": "dict|null"},
    side_effects=["created_events"],
    name_variants=[
        "create_event", "schedule_meeting", "add_event", "new_event",
        "book_meeting", "create_meeting", "schedule_event", "add_calendar_entry",
    ],
    description_templates=[
        "Create a new calendar event with attendees.",
        "Schedule a meeting on the calendar.",
        "Add a new event to the calendar with optional attendees and details.",
        "Book a new meeting or event on the calendar.",
    ],
    behavior_key="create_event",
)

CHECK_AVAILABILITY_ARCHETYPE = ToolArchetype(
    archetype_id="check_availability",
    category="query",
    semantic_description="Check calendar availability for one or more attendees on a date",
    parameters=[_AVAILABILITY_ATTENDEES, _AVAILABILITY_DATE, _DURATION_MINUTES],
    returns={
        "date": "str", "attendees": "list[str]",
        "availability": "dict", "common_free_slots": "list[slot]",
    },
    side_effects=[],
    name_variants=[
        "check_availability", "find_free_time", "get_availability",
        "check_schedule", "find_available_slots", "check_free_slots",
        "get_free_times", "query_availability",
    ],
    description_templates=[
        "Check calendar availability for one or more attendees on a specific date.",
        "Find free time slots for scheduling a meeting.",
        "Query availability for participants on a given date.",
        "Check when attendees are free for a meeting of specified duration.",
    ],
    behavior_key="check_availability",
)

SEARCH_SLACK_ARCHETYPE = ToolArchetype(
    archetype_id="search_slack",
    category="query",
    semantic_description="Search Slack messages",
    parameters=[_SEARCH_QUERY, _SLACK_CHANNEL, _SLACK_SENDER, _RESULT_LIMIT],
    returns={"results": "list[message]", "count": "int"},
    side_effects=[],
    name_variants=[
        "search_slack", "find_slack_messages", "query_slack", "search_chat",
        "find_messages_slack", "search_channels", "lookup_slack",
    ],
    description_templates=[
        "Search Slack messages by query, channel, or sender.",
        "Find messages in Slack matching search criteria.",
        "Query Slack channels for messages.",
        "Search through Slack message history.",
    ],
    behavior_key="search_slack",
)

SEND_SLACK_ARCHETYPE = ToolArchetype(
    archetype_id="send_slack",
    category="mutate",
    semantic_description="Send a Slack message to a channel or user",
    parameters=[_SLACK_CHANNEL_REQUIRED, _SLACK_MESSAGE, _SLACK_THREAD],
    returns={"success": "bool", "message_id": "str|null", "channel": "str|null"},
    side_effects=["sent_slack"],
    name_variants=[
        "send_slack", "post_message", "send_chat", "slack_message",
        "post_to_channel", "send_slack_message", "chat_send", "post_slack",
    ],
    description_templates=[
        "Send a Slack message to a channel or user.",
        "Post a message to a Slack channel.",
        "Send a chat message to a channel or direct message.",
        "Deliver a message to the specified Slack channel or user.",
    ],
    behavior_key="send_slack",
)

WEB_SEARCH_ARCHETYPE = ToolArchetype(
    archetype_id="web_search",
    category="query",
    semantic_description="Search the web for information",
    parameters=[_WEB_QUERY, _RESULT_LIMIT],
    returns={"query": "str", "results": "list[result]", "count": "int"},
    side_effects=[],
    name_variants=[
        "web_search", "search_web", "internet_search", "online_search",
        "google_search", "find_online", "web_query", "search_internet",
    ],
    description_templates=[
        "Search the web for information.",
        "Perform an internet search.",
        "Find information online using a search query.",
        "Search the web and return relevant results.",
    ],
    behavior_key="web_search",
)

LOOKUP_CONTACT_ARCHETYPE = ToolArchetype(
    archetype_id="lookup_contact",
    category="lookup",
    semantic_description="Look up contact information",
    parameters=[_CONTACT_NAME, _CONTACT_EMAIL, _CONTACT_DEPARTMENT],
    returns={"found": "bool", "contact": "dict|null", "contacts": "list[dict]|null"},
    side_effects=[],
    name_variants=[
        "lookup_contact", "find_contact", "search_contacts", "get_contact",
        "find_person", "contact_lookup", "directory_search", "people_search",
    ],
    description_templates=[
        "Look up contact information by name, email, or department.",
        "Find a person in the contacts directory.",
        "Search the company directory for contact details.",
        "Look up employee contact information.",
    ],
    behavior_key="lookup_contact",
)

# --- All workspace archetypes ---

ALL_WORKSPACE_ARCHETYPES = [
    SEARCH_EMAILS_ARCHETYPE,
    READ_EMAIL_ARCHETYPE,
    SEND_EMAIL_ARCHETYPE,
    SEARCH_CALENDAR_ARCHETYPE,
    CREATE_EVENT_ARCHETYPE,
    CHECK_AVAILABILITY_ARCHETYPE,
    SEARCH_SLACK_ARCHETYPE,
    SEND_SLACK_ARCHETYPE,
    WEB_SEARCH_ARCHETYPE,
    LOOKUP_CONTACT_ARCHETYPE,
]

WORKSPACE_DATA_SCHEMA = {
    "emails": "list[email]",
    "calendar_events": "list[event]",
    "slack_messages": "list[message]",
    "contacts": "list[contact]",
    "sent_emails": "list[email]",
    "created_events": "list[event]",
    "sent_slack": "list[message]",
}


def get_workspace_archetype_set() -> DomainArchetypeSet:
    """Create the workspace domain archetype set."""
    return DomainArchetypeSet(
        domain="workspace",
        archetypes=ALL_WORKSPACE_ARCHETYPES,
        data_schema=WORKSPACE_DATA_SCHEMA,
    )
