"""
Tasks for the workspace benchmark suite.

Contains 18 tasks distributed across difficulty levels and information flows.
"""

from typing import List
from agnibench.core.abstractions import (
    Task,
    TaskCharacteristics,
    DifficultyLevel,
    InformationFlow,
)


def get_workspace_tasks() -> List[Task]:
    """Get all workspace tasks."""
    tasks = []

    # ============================================================================
    # SIMPLE TASKS (4 tasks, 2-3 tool calls)
    # ============================================================================

    tasks.append(Task(
        id="workspace_simple_01",
        name="Find Unread Emails",
        prompt="Show me all my unread emails.",
        difficulty=DifficultyLevel.SIMPLE,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["search_emails"],
        expected_answer="unread emails",
        verifier_config={
            "answer": ["email", "unread", "Alice", "Carol", "Eve"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_emails"],
                "min_calls": 1,
                "max_calls": 2
            }
        },
        description="Simple email search",
        min_tool_calls=1,
        max_tool_calls=2,
        tags=["email", "search"],
    ))

    tasks.append(Task(
        id="workspace_simple_02",
        name="Lookup Contact",
        prompt="Find Alice Johnson's email address and phone number.",
        difficulty=DifficultyLevel.SIMPLE,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["lookup_contact"],
        expected_answer="alice.johnson@company.com",
        verifier_config={
            "answer": ["alice.johnson@company.com", "555-123-4567"],
            "match_mode": "contains",
            "tools": {
                "required": ["lookup_contact"],
                "min_calls": 1,
                "max_calls": 2
            }
        },
        description="Simple contact lookup",
        min_tool_calls=1,
        max_tool_calls=2,
        tags=["contact", "lookup"],
    ))

    tasks.append(Task(
        id="workspace_simple_03",
        name="Check Tomorrow's Schedule",
        prompt="What meetings do I have scheduled for tomorrow?",
        difficulty=DifficultyLevel.SIMPLE,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["search_calendar"],
        expected_answer="meetings",
        verifier_config={
            "answer": ["Team Standup", "Product Review", "1:1"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_calendar"],
                "min_calls": 1,
                "max_calls": 2
            }
        },
        description="Simple calendar check",
        min_tool_calls=1,
        max_tool_calls=2,
        tags=["calendar", "schedule"],
    ))

    tasks.append(Task(
        id="workspace_simple_04",
        name="Send Quick Slack Message",
        prompt="Send a message to the #general Slack channel saying 'Thanks for the update!'",
        difficulty=DifficultyLevel.SIMPLE,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
        ),
        expected_tool_calls=["send_slack"],
        expected_answer="sent",
        verifier_config={
            "answer": ["sent", "message", "success"],
            "match_mode": "contains",
            "tools": {
                "required": ["send_slack"],
                "min_calls": 1,
                "max_calls": 2
            },
            "state": {
                "sent_slack": {"$length": {"$gte": 1}}
            }
        },
        description="Simple Slack message",
        min_tool_calls=1,
        max_tool_calls=2,
        tags=["slack", "message"],
    ))

    # ============================================================================
    # MEDIUM TASKS (6 tasks, 4-6 tool calls)
    # ============================================================================

    tasks.append(Task(
        id="workspace_medium_01",
        name="Reply to Email",
        prompt="Find the email from Alice about Q4 Planning and send a reply saying I'm available tomorrow afternoon for the meeting.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["search_emails", "read_email", "send_email"],
        expected_answer="sent",
        verifier_config={
            "answer": ["sent", "reply", "Alice"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_emails", "send_email"],
                "optional": ["read_email"],
                "min_calls": 2,
                "max_calls": 5
            },
            "state": {
                "sent_emails": {"$length": {"$gte": 1}}
            }
        },
        description="Find and reply to specific email",
        min_tool_calls=2,
        max_tool_calls=5,
        tags=["email", "reply", "search"],
    ))

    tasks.append(Task(
        id="workspace_medium_02",
        name="Schedule Meeting with Contact",
        prompt="Schedule a 1-hour meeting with Bob Smith for tomorrow at 2 PM called 'Project Sync'. Include a note that we'll discuss the feature request.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["lookup_contact", "create_event"],
        expected_answer="created",
        verifier_config={
            "answer": ["created", "Project Sync", "Bob", "2 PM"],
            "match_mode": "contains",
            "tools": {
                "required": ["create_event"],
                "optional": ["lookup_contact", "search_calendar"],
                "min_calls": 1,
                "max_calls": 5
            },
            "state": {
                "created_events": {"$length": {"$gte": 1}}
            }
        },
        description="Create meeting with contact lookup",
        min_tool_calls=1,
        max_tool_calls=5,
        tags=["calendar", "contact", "meeting"],
    ))

    tasks.append(Task(
        id="workspace_medium_03",
        name="Check Engineering Team Slack",
        prompt="Check what's been discussed in the #engineering Slack channel and summarize the key points.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["search_slack"],
        expected_answer="deployment",
        verifier_config={
            "answer": ["deployment", "5pm", "PR", "engineering"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_slack"],
                "min_calls": 1,
                "max_calls": 4
            }
        },
        description="Search and summarize Slack",
        min_tool_calls=1,
        max_tool_calls=4,
        tags=["slack", "search", "summarize"],
    ))

    tasks.append(Task(
        id="workspace_medium_04",
        name="Find and Forward Information",
        prompt="Find the email about the customer meeting prep from Eve and forward the key details to Bob Smith.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_cross_reference=True,
        ),
        expected_tool_calls=["search_emails", "read_email", "lookup_contact", "send_email"],
        expected_answer="sent",
        verifier_config={
            "answer": ["sent", "Bob", "customer", "Acme"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_emails", "send_email"],
                "optional": ["read_email", "lookup_contact"],
                "min_calls": 2,
                "max_calls": 6
            },
            "state": {
                "sent_emails": {"$length": {"$gte": 1}}
            }
        },
        description="Find, read, and forward email",
        min_tool_calls=2,
        max_tool_calls=6,
        tags=["email", "forward", "search"],
    ))

    tasks.append(Task(
        id="workspace_medium_05",
        name="Check Availability and Notify",
        prompt="Check if Carol Williams is available tomorrow at 11 AM and send her a Slack message asking if she can join a quick design review.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_conditional_logic=True,
        ),
        expected_tool_calls=["check_availability", "send_slack"],
        expected_answer=["availability", "slack", "sent"],
        verifier_config={
            "answer": ["Carol", "available", "sent", "design"],
            "match_mode": "contains",
            "tools": {
                "required": ["check_availability", "send_slack"],
                "optional": ["lookup_contact"],
                "min_calls": 2,
                "max_calls": 5
            }
        },
        description="Check availability and send notification",
        min_tool_calls=2,
        max_tool_calls=5,
        tags=["calendar", "slack", "availability"],
    ))

    tasks.append(Task(
        id="workspace_medium_06",
        name="Compile Meeting Attendee List",
        prompt="List all the people I'm meeting with tomorrow along with their email addresses and departments.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_cross_reference=True,
        ),
        expected_tool_calls=["search_calendar", "lookup_contact", "lookup_contact", "lookup_contact"],
        expected_answer=["Alice", "Bob", "David"],
        verifier_config={
            "answer": ["Alice", "Bob", "David", "Engineering", "Product"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_calendar", "lookup_contact"],
                "min_calls": 2,
                "max_calls": 8
            }
        },
        description="Cross-reference calendar and contacts",
        min_tool_calls=2,
        max_tool_calls=8,
        tags=["calendar", "contact", "cross-reference"],
    ))

    # ============================================================================
    # HARD TASKS (5 tasks, 7-10 tool calls)
    # ============================================================================

    tasks.append(Task(
        id="workspace_hard_01",
        name="Schedule Multi-Person Meeting",
        prompt="Schedule a team meeting for tomorrow with Alice Johnson, Bob Smith, and Carol Williams. Find a time when everyone is available (at least 1 hour). Create the event and notify everyone via Slack.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_multi_constraint=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["check_availability", "create_event", "send_slack"],
        expected_answer=["created", "scheduled", "meeting"],
        verifier_config={
            "answer": ["created", "meeting", "Alice", "Bob", "Carol"],
            "match_mode": "contains",
            "tools": {
                "required": ["check_availability", "create_event"],
                "optional": ["lookup_contact", "send_slack", "search_calendar"],
                "min_calls": 3,
                "max_calls": 10
            },
            "state": {
                "created_events": {"$length": {"$gte": 1}}
            }
        },
        description="Multi-constraint scheduling",
        min_tool_calls=3,
        max_tool_calls=10,
        tags=["calendar", "scheduling", "multi-person"],
    ))

    tasks.append(Task(
        id="workspace_hard_02",
        name="Email Summary and Response",
        prompt="Read all my unread emails, summarize them, and send a single email to David Brown with a summary of the key action items from all unread emails.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["search_emails", "read_email", "read_email", "read_email", "lookup_contact", "send_email"],
        expected_answer=["sent", "summary", "action items"],
        verifier_config={
            "answer": ["sent", "David", "summary", "action"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_emails", "send_email"],
                "optional": ["read_email", "lookup_contact"],
                "min_calls": 3,
                "max_calls": 10
            },
            "state": {
                "sent_emails": {"$length": {"$gte": 1}}
            }
        },
        description="Aggregate and summarize multiple emails",
        min_tool_calls=3,
        max_tool_calls=10,
        tags=["email", "summary", "aggregation"],
    ))

    tasks.append(Task(
        id="workspace_hard_03",
        name="Coordinate Response to Request",
        prompt="Eve Davis sent an email about a customer meeting next week. Find the meeting on my calendar, check who else is invited, get their contact info, and send them all an email asking them to prepare demo materials.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,  # FIXED: The prompt explicitly specifies the sequence of actions
            control_flow_from_tools=False,
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["search_emails", "read_email", "search_calendar", "lookup_contact", "send_email"],
        expected_answer=["sent", "demo", "prepare"],
        verifier_config={
            "answer": ["sent", "demo", "Customer Demo", "Alice"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_emails", "search_calendar", "send_email"],
                "optional": ["read_email", "lookup_contact"],
                "min_calls": 4,
                "max_calls": 10
            },
            "state": {
                "sent_emails": {"$length": {"$gte": 1}}
            }
        },
        description="Complex coordination task",
        min_tool_calls=4,
        max_tool_calls=10,
        tags=["email", "calendar", "coordination"],
    ))

    tasks.append(Task(
        id="workspace_hard_04",
        name="Cross-Channel Communication Sync",
        prompt="Check what Alice Johnson has communicated about recently (emails and Slack), summarize her key points, and send an update to the #general Slack channel summarizing what Alice is working on.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,  # FIXED: Prompt specifies exact channels to check and action to take
            control_flow_from_tools=False,
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["search_emails", "search_slack", "send_slack"],
        expected_answer=["sent", "Alice", "#general"],
        verifier_config={
            "answer": ["sent", "Alice", "Q4", "planning"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_emails", "search_slack", "send_slack"],
                "optional": ["read_email"],
                "min_calls": 3,
                "max_calls": 10
            },
            "state": {
                "sent_slack": {"$length": {"$gte": 1}}
            }
        },
        description="Cross-channel information synthesis",
        min_tool_calls=3,
        max_tool_calls=10,
        tags=["email", "slack", "synthesis"],
    ))

    tasks.append(Task(
        id="workspace_hard_05",
        name="Meeting Preparation Package",
        prompt="For my 1:1 with David Brown tomorrow, prepare by: 1) Finding any recent emails from him, 2) Checking what he's mentioned in Slack, 3) Looking at our shared calendar events, then send him an email with a proposed agenda based on these findings.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["search_emails", "search_slack", "search_calendar", "send_email"],
        expected_answer=["sent", "agenda", "David"],
        verifier_config={
            "answer": ["sent", "agenda", "David", "1:1"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_emails", "search_calendar", "send_email"],
                "optional": ["search_slack", "read_email", "lookup_contact"],
                "min_calls": 4,
                "max_calls": 10
            },
            "state": {
                "sent_emails": {"$length": {"$gte": 1}}
            }
        },
        description="Comprehensive meeting preparation",
        min_tool_calls=4,
        max_tool_calls=10,
        tags=["email", "calendar", "slack", "preparation"],
    ))

    # ============================================================================
    # EXPERT TASKS (3 tasks, 11+ tool calls)
    # ============================================================================

    tasks.append(Task(
        id="workspace_expert_01",
        name="Conflict Resolution Scheduling",
        prompt="""I need to schedule a critical 2-hour planning meeting with all department heads (Alice from Engineering, Bob from Product, Carol from Design, David from Engineering Management, and Eve from Sales) sometime this week.

        Find a time that works for everyone, considering:
        1. Check everyone's availability
        2. If no common time exists, identify who has conflicts
        3. Create the meeting for the best available slot
        4. Send calendar invites and a Slack notification about the meeting
        5. Email anyone who might have conflicts asking them to reschedule their conflicting meetings""",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_multi_constraint=True,
            requires_plan_adaptation=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["check_availability"] * 5 + ["create_event", "send_slack", "send_email"],
        expected_answer=["meeting", "created", "scheduled"],
        verifier_config={
            "answer": ["created", "meeting", "planning"],
            "match_mode": "contains",
            "tools": {
                "required": ["check_availability", "create_event"],
                "optional": ["lookup_contact", "send_slack", "send_email", "search_calendar"],
                "min_calls": 5,
                "max_calls": 20
            },
            "state": {
                "created_events": {"$length": {"$gte": 1}}
            }
        },
        description="Complex multi-person scheduling with conflict resolution",
        min_tool_calls=5,
        max_tool_calls=20,
        tags=["calendar", "scheduling", "conflict-resolution", "multi-person"],
    ))

    tasks.append(Task(
        id="workspace_expert_02",
        name="Comprehensive Status Report",
        prompt="""Prepare a comprehensive weekly status report by:

        1. Gathering all unread emails and summarizing key requests/action items
        2. Checking all Slack channels for important discussions
        3. Reviewing this week's calendar for completed meetings
        4. Compiling everything into a status email to David Brown (my manager)
        5. Also post a summary to #general Slack

        The report should include: completed items, pending items, upcoming meetings, and any blockers.""",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,  # FIXED: Prompt provides explicit numbered steps - this is a recipe
            control_flow_from_tools=False,
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_long_reasoning_chain=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["search_emails", "read_email", "search_slack", "search_calendar", "send_email", "send_slack"],
        expected_answer=["sent", "status", "report"],
        verifier_config={
            "answer": ["sent", "status", "David"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_emails", "search_calendar", "send_email"],
                "optional": ["read_email", "search_slack", "send_slack", "lookup_contact"],
                "min_calls": 5,
                "max_calls": 20
            },
            "state": {
                "sent_emails": {"$length": {"$gte": 1}}
            }
        },
        description="Multi-source status report compilation",
        min_tool_calls=5,
        max_tool_calls=20,
        tags=["email", "slack", "calendar", "report", "synthesis"],
    ))

    tasks.append(Task(
        id="workspace_expert_03",
        name="Project Kickoff Coordination",
        prompt="""Coordinate a new project kickoff:

        1. Search emails for any project-related discussions
        2. Find all team members in Engineering and Product departments
        3. Check everyone's availability for a 90-minute kickoff meeting this week
        4. Create the meeting with all team members
        5. Send a detailed email to all attendees with the agenda
        6. Post an announcement in #engineering and #general Slack channels
        7. Send a separate email to Eve in Sales informing her about the new project

        Make sure to include relevant context from previous communications.""",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_multi_constraint=True,
            requires_long_reasoning_chain=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["search_emails", "lookup_contact", "check_availability", "create_event", "send_email", "send_slack"],
        expected_answer=["created", "kickoff", "meeting", "sent"],
        verifier_config={
            "answer": ["created", "meeting", "kickoff"],
            "match_mode": "contains",
            "tools": {
                "required": ["lookup_contact", "check_availability", "create_event", "send_email", "send_slack"],
                "optional": ["search_emails", "read_email", "search_calendar"],
                "min_calls": 8,
                "max_calls": 25
            },
            "state": {
                "created_events": {"$length": {"$gte": 1}},
                "sent_emails": {"$length": {"$gte": 1}},
                "sent_slack": {"$length": {"$gte": 1}}
            }
        },
        description="Full project kickoff coordination",
        min_tool_calls=8,
        max_tool_calls=25,
        tags=["email", "calendar", "slack", "coordination", "project"],
    ))

    # ============================================================================
    # TRUE TOOL-DRIVEN CONTROL FLOW TASKS
    # These tasks require discovering what to do from tool responses
    # ============================================================================

    tasks.append(Task(
        id="workspace_discovery_01",
        name="Handle Urgent Inbox Matter",
        prompt="Handle the most urgent matter in my inbox right now. Take whatever action is appropriate based on what you find.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Agent must read inbox first, then decide based on content
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_plan_adaptation=True,
        ),
        expected_tool_calls=["search_emails", "read_email"],  # Minimum - actual calls depend on email content
        expected_answer=["handled", "urgent", "action"],
        verifier_config={
            "answer": ["email", "action", "response"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_emails"],
                "optional": ["read_email", "send_email", "create_event", "send_slack", "lookup_contact", "check_availability"],
                "min_calls": 2,
                "max_calls": 10
            }
        },
        description="TRUE tool-driven: email content determines next actions",
        min_tool_calls=2,
        max_tool_calls=10,
        tags=["discovery", "urgent", "branching"],
    ))

    tasks.append(Task(
        id="workspace_discovery_02",
        name="Respond to Latest Message",
        prompt="Check all my communication channels (email, Slack) and respond to whoever messaged me most recently with an appropriate reply.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Must check both channels, compare timestamps, then decide which to reply to
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_cross_reference=True,
        ),
        expected_tool_calls=["search_emails", "search_slack"],  # Then either send_email or send_slack based on which is most recent
        expected_answer=["replied", "response", "sent"],
        verifier_config={
            "answer": ["sent", "reply", "response"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_emails", "search_slack"],
                "optional": ["read_email", "send_email", "send_slack", "lookup_contact"],
                "min_calls": 3,
                "max_calls": 8
            }
        },
        description="TRUE tool-driven: recency comparison determines response channel",
        min_tool_calls=3,
        max_tool_calls=8,
        tags=["discovery", "comparison", "branching"],
    ))

    tasks.append(Task(
        id="workspace_discovery_03",
        name="Fix Schedule Conflict",
        prompt="I have a scheduling conflict tomorrow. Find it and resolve it by rescheduling or declining one of the meetings.",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Must discover WHAT the conflict is before knowing how to resolve it
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_plan_adaptation=True,
            requires_error_recovery=True,
        ),
        expected_tool_calls=["search_calendar"],  # Then decide based on conflict type
        expected_answer=["resolved", "rescheduled", "conflict"],
        verifier_config={
            "answer": ["conflict", "resolve", "calendar"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_calendar"],
                "optional": ["check_availability", "create_event", "send_email", "send_slack", "lookup_contact"],
                "min_calls": 2,
                "max_calls": 12
            }
        },
        description="TRUE tool-driven: conflict details determine resolution strategy",
        min_tool_calls=2,
        max_tool_calls=12,
        tags=["discovery", "conflict", "resolution"],
    ))

    tasks.append(Task(
        id="workspace_discovery_04",
        name="Follow Up on Pending Items",
        prompt="Check if there are any emails or Slack messages I haven't responded to in the past week. If so, send appropriate follow-ups.",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Number and type of follow-ups depends entirely on what's found
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_state_tracking=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["search_emails", "search_slack"],  # Then 0 to many follow-ups based on what's found
        expected_answer=["follow", "sent", "response"],
        verifier_config={
            "answer": ["follow", "sent", "email", "slack"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_emails", "search_slack"],
                "optional": ["read_email", "send_email", "send_slack", "lookup_contact"],
                "min_calls": 2,
                "max_calls": 15
            }
        },
        description="TRUE tool-driven: discovered pending items determine actions",
        min_tool_calls=2,
        max_tool_calls=15,
        tags=["discovery", "follow-up", "iterative"],
    ))

    tasks.append(Task(
        id="workspace_discovery_05",
        name="Prepare for Next Meeting",
        prompt="Look at my next upcoming meeting and prepare for it by gathering all relevant context from emails and Slack discussions about the topic.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Must discover WHAT meeting is next, THEN search for relevant context
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["search_calendar"],  # Meeting topic determines what to search for
        expected_answer=["meeting", "context", "prepared"],
        verifier_config={
            "answer": ["meeting", "context", "email", "slack"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_calendar"],
                "optional": ["search_emails", "read_email", "search_slack", "lookup_contact"],
                "min_calls": 2,
                "max_calls": 10
            }
        },
        description="TRUE tool-driven: meeting topic determines search queries",
        min_tool_calls=2,
        max_tool_calls=10,
        tags=["discovery", "preparation", "context"],
    ))

    tasks.append(Task(
        id="workspace_discovery_06",
        name="Handle Communication Backlog",
        prompt="I've been away for a few days. Go through my unread communications and handle anything that needs immediate attention. Deprioritize anything that can wait.",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Complete discovery - what's unread, what's urgent, what actions to take
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_multi_constraint=True,
            requires_long_reasoning_chain=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["search_emails", "search_slack"],  # Then branching based on urgency
        expected_answer=["handled", "urgent", "backlog"],
        verifier_config={
            "answer": ["email", "slack", "urgent", "handled"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_emails", "search_slack"],
                "optional": ["read_email", "send_email", "send_slack", "create_event", "lookup_contact", "check_availability"],
                "min_calls": 2,
                "max_calls": 20
            }
        },
        description="TRUE tool-driven: discovered backlog determines all subsequent actions",
        min_tool_calls=2,
        max_tool_calls=20,
        tags=["discovery", "triage", "backlog", "branching"],
    ))

    return tasks
