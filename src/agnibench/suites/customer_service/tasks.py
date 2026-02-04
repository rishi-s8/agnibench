"""
Tasks for the customer service benchmark suite.

Contains 17 tasks distributed across difficulty levels and information flows.
"""

from typing import List
from agnibench.core.abstractions import (
    Task,
    TaskCharacteristics,
    DifficultyLevel,
    InformationFlow,
)


def get_customer_service_tasks() -> List[Task]:
    """Get all customer service tasks."""
    tasks = []

    # ============================================================================
    # SIMPLE TASKS (4 tasks, 2-3 tool calls)
    # ============================================================================

    tasks.append(Task(
        id="cs_simple_01",
        name="Find Open Tickets",
        prompt="Show me all open support tickets.",
        difficulty=DifficultyLevel.SIMPLE,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["search_tickets"],
        expected_answer="open tickets",
        verifier_config={
            "answer": ["ticket_001", "ticket_002", "ticket_003", "open"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_tickets"],
                "min_calls": 1,
                "max_calls": 2
            }
        },
        description="Simple ticket search",
        min_tool_calls=1,
        max_tool_calls=2,
        tags=["search", "tickets"],
    ))

    tasks.append(Task(
        id="cs_simple_02",
        name="Lookup Customer",
        prompt="Get the details for customer cust_001.",
        difficulty=DifficultyLevel.SIMPLE,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["get_customer"],
        expected_answer=["John Smith", "enterprise"],
        verifier_config={
            "answer": ["John Smith", "enterprise", "john.smith@example.com"],
            "match_mode": "contains",
            "tools": {
                "required": ["get_customer"],
                "min_calls": 1,
                "max_calls": 2
            }
        },
        description="Simple customer lookup",
        min_tool_calls=1,
        max_tool_calls=2,
        tags=["customer", "lookup"],
    ))

    tasks.append(Task(
        id="cs_simple_03",
        name="Search Knowledge Base",
        prompt="Find knowledge base articles about password reset.",
        difficulty=DifficultyLevel.SIMPLE,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["search_kb"],
        expected_answer=["password", "reset"],
        verifier_config={
            "answer": ["password", "reset", "kb_001"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_kb"],
                "min_calls": 1,
                "max_calls": 2
            }
        },
        description="Simple KB search",
        min_tool_calls=1,
        max_tool_calls=2,
        tags=["knowledge_base", "search"],
    ))

    tasks.append(Task(
        id="cs_simple_04",
        name="Check Service Status",
        prompt="What's the current status of the API service?",
        difficulty=DifficultyLevel.SIMPLE,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["check_product"],
        expected_answer=["API", "degraded"],
        verifier_config={
            "answer": ["API", "degraded", "500"],
            "match_mode": "contains",
            "tools": {
                "required": ["check_product"],
                "min_calls": 1,
                "max_calls": 2
            }
        },
        description="Service status check",
        min_tool_calls=1,
        max_tool_calls=2,
        tags=["product", "status"],
    ))

    # ============================================================================
    # MEDIUM TASKS (6 tasks, 4-6 tool calls)
    # ============================================================================

    tasks.append(Task(
        id="cs_medium_01",
        name="Investigate Login Issue",
        prompt="Customer cust_001 reports they can't log in. Investigate the issue and find a solution from the knowledge base.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["get_customer", "search_tickets", "get_ticket", "search_kb"],
        expected_answer=["password", "reset", "cache"],
        verifier_config={
            "answer": ["password", "reset", "cache", "browser"],
            "match_mode": "contains",
            "tools": {
                "required": ["get_customer", "search_kb"],
                "optional": ["search_tickets", "get_ticket"],
                "min_calls": 2,
                "max_calls": 6
            }
        },
        description="Login issue investigation",
        min_tool_calls=2,
        max_tool_calls=6,
        tags=["troubleshooting", "login"],
    ))

    tasks.append(Task(
        id="cs_medium_02",
        name="Handle Billing Issue",
        prompt="Look into ticket_002 about a billing discrepancy and prepare a response for the customer.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["get_ticket", "get_customer", "search_kb", "send_response"],
        expected_answer=["refund", "duplicate", "billing"],
        verifier_config={
            "answer": ["refund", "duplicate", "billing", "response"],
            "match_mode": "contains",
            "tools": {
                "required": ["get_ticket", "send_response"],
                "optional": ["get_customer", "search_kb"],
                "min_calls": 2,
                "max_calls": 6
            },
            "state": {
                "responses_sent": {"$length": {"$gte": 1}}
            }
        },
        description="Billing issue handling",
        min_tool_calls=2,
        max_tool_calls=6,
        tags=["billing", "response"],
    ))

    tasks.append(Task(
        id="cs_medium_03",
        name="API Error Investigation",
        prompt="A customer is reporting API 500 errors. Check if this is a known issue and provide relevant information.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_cross_reference=True,
        ),
        expected_tool_calls=["check_product", "search_kb", "search_tickets"],
        expected_answer=["degraded", "known issue", "500"],
        verifier_config={
            "answer": ["degraded", "500", "API", "investigating"],
            "match_mode": "contains",
            "tools": {
                "required": ["check_product"],
                "optional": ["search_kb", "search_tickets"],
                "min_calls": 1,
                "max_calls": 5
            }
        },
        description="API error investigation",
        min_tool_calls=1,
        max_tool_calls=5,
        tags=["api", "technical", "investigation"],
    ))

    tasks.append(Task(
        id="cs_medium_04",
        name="Update Ticket Status",
        prompt="Ticket ticket_001 has been investigated. Update it to 'in_progress' and add a note that the issue appears to be related to browser cache.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_prompt=True,
        ),
        expected_tool_calls=["get_ticket", "update_ticket"],
        expected_answer=["updated", "in_progress"],
        verifier_config={
            "answer": ["updated", "in_progress", "cache"],
            "match_mode": "contains",
            "tools": {
                "required": ["update_ticket"],
                "optional": ["get_ticket"],
                "min_calls": 1,
                "max_calls": 4
            },
            "state": {
                "ticket_updates": {"$length": {"$gte": 1}}
            }
        },
        description="Ticket status update",
        min_tool_calls=1,
        max_tool_calls=4,
        tags=["ticket", "update"],
    ))

    tasks.append(Task(
        id="cs_medium_05",
        name="Customer History Review",
        prompt="Before responding to the feature request in ticket_004, review the customer's profile and ticket history to understand their needs better.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_cross_reference=True,
        ),
        expected_tool_calls=["get_ticket", "get_customer", "search_tickets"],
        expected_answer=["enterprise", "Emily Davis", "feature"],
        verifier_config={
            "answer": ["enterprise", "Emily", "feature", "report"],
            "match_mode": "contains",
            "tools": {
                "required": ["get_ticket", "get_customer"],
                "optional": ["search_tickets"],
                "min_calls": 2,
                "max_calls": 5
            }
        },
        description="Customer context gathering",
        min_tool_calls=2,
        max_tool_calls=5,
        tags=["customer", "history", "context"],
    ))

    tasks.append(Task(
        id="cs_medium_06",
        name="Security Documentation Request",
        prompt="Customer cust_004 needs security documentation for an audit. Find the relevant KB article and prepare to respond.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["get_customer", "search_tickets", "search_kb"],
        expected_answer=["SOC 2", "security", "compliance"],
        verifier_config={
            "answer": ["SOC 2", "security", "compliance", "ISO 27001"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_kb"],
                "optional": ["get_customer", "search_tickets", "get_ticket"],
                "min_calls": 1,
                "max_calls": 5
            }
        },
        description="Security documentation lookup",
        min_tool_calls=1,
        max_tool_calls=5,
        tags=["security", "compliance", "documentation"],
    ))

    # ============================================================================
    # HARD TASKS (5 tasks, 7-10 tool calls)
    # ============================================================================

    tasks.append(Task(
        id="cs_hard_01",
        name="Complete Issue Resolution",
        prompt="Fully resolve ticket_001 (login issue). Investigate the problem, find the solution in KB, update the ticket, and send a helpful response to the customer.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_state_tracking=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["get_ticket", "get_customer", "search_kb", "update_ticket", "send_response"],
        expected_answer=["resolved", "password", "cache"],
        verifier_config={
            "answer": ["password", "reset", "cache", "response"],
            "match_mode": "contains",
            "tools": {
                "required": ["get_ticket", "search_kb", "send_response"],
                "optional": ["get_customer", "update_ticket"],
                "min_calls": 3,
                "max_calls": 10
            },
            "state": {
                "responses_sent": {"$length": {"$gte": 1}}
            }
        },
        description="Full issue resolution workflow",
        min_tool_calls=3,
        max_tool_calls=10,
        tags=["resolution", "complete", "login"],
    ))

    tasks.append(Task(
        id="cs_hard_02",
        name="Complex Technical Issue",
        prompt="Handle ticket_003 (API errors). Check service status, find relevant KB info, look at the customer context, and send an appropriate response explaining the situation.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["get_ticket", "check_product", "search_kb", "get_customer", "send_response"],
        expected_answer=["degraded", "investigating", "API"],
        verifier_config={
            "answer": ["API", "degraded", "500", "investigating"],
            "match_mode": "contains",
            "tools": {
                "required": ["get_ticket", "check_product", "send_response"],
                "optional": ["search_kb", "get_customer", "update_ticket"],
                "min_calls": 3,
                "max_calls": 10
            },
            "state": {
                "responses_sent": {"$length": {"$gte": 1}}
            }
        },
        description="Technical issue with service correlation",
        min_tool_calls=3,
        max_tool_calls=10,
        tags=["technical", "api", "service_status"],
    ))

    tasks.append(Task(
        id="cs_hard_03",
        name="Escalation Decision",
        prompt="Review ticket_002 (billing duplicate charge). Investigate thoroughly, and if this requires special handling, escalate to the billing team. Send an appropriate response to the customer.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,  # FIXED: The prompt already tells you it's a billing duplicate charge
            control_flow_from_tools=False,  # The escalation condition is known upfront from the prompt
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["get_ticket", "get_customer", "search_kb", "escalate_ticket", "send_response"],
        expected_answer=["escalated", "billing", "refund"],
        verifier_config={
            "answer": ["billing", "escalate", "refund", "duplicate"],
            "match_mode": "contains",
            "tools": {
                "required": ["get_ticket", "send_response"],
                "optional": ["get_customer", "search_kb", "escalate_ticket", "update_ticket"],
                "min_calls": 3,
                "max_calls": 10
            },
            "state": {
                "responses_sent": {"$length": {"$gte": 1}}
            }
        },
        description="Issue requiring escalation decision",
        min_tool_calls=3,
        max_tool_calls=10,
        tags=["escalation", "billing", "decision"],
    ))

    tasks.append(Task(
        id="cs_hard_04",
        name="Multi-Issue Customer",
        prompt="Customer cust_001 has multiple open tickets. Review all their issues, understand the full context, and prioritize which should be addressed first. Update the highest priority ticket and send a consolidated response.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,  # FIXED: Sequence is known: get customer → search tickets → get each ticket → prioritize → update → respond
            control_flow_from_tools=False,  # Prioritization is a judgment call, not control flow discovery
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_multi_constraint=True,
        ),
        expected_tool_calls=["get_customer", "search_tickets", "get_ticket", "get_ticket", "get_ticket", "update_ticket", "send_response"],
        expected_answer=["prioritize", "login", "export"],
        verifier_config={
            "answer": ["John Smith", "login", "priority", "ticket"],
            "match_mode": "contains",
            "tools": {
                "required": ["get_customer", "search_tickets", "send_response"],
                "optional": ["get_ticket", "update_ticket"],
                "min_calls": 3,
                "max_calls": 12  # Increased to account for 3 tickets now
            }
        },
        description="Multi-issue prioritization",
        min_tool_calls=3,
        max_tool_calls=12,
        tags=["prioritization", "multi-issue", "customer"],
    ))

    tasks.append(Task(
        id="cs_hard_05",
        name="Data Export Troubleshooting",
        prompt="Ticket_005 is about data export failures. The issue is already in progress. Check the KB for the known limitation, verify the customer's tier, and send a detailed response with the solution for large exports.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["get_ticket", "search_kb", "get_customer", "send_response"],
        expected_answer=["scheduled export", "10,000", "limitation"],
        verifier_config={
            "answer": ["export", "10,000", "scheduled", "async"],
            "match_mode": "contains",
            "tools": {
                "required": ["get_ticket", "search_kb", "send_response"],
                "optional": ["get_customer", "update_ticket"],
                "min_calls": 3,
                "max_calls": 10
            },
            "state": {
                "responses_sent": {"$length": {"$gte": 1}}
            }
        },
        description="Known limitation troubleshooting",
        min_tool_calls=3,
        max_tool_calls=10,
        tags=["export", "troubleshooting", "limitation"],
    ))

    # ============================================================================
    # EXPERT TASKS (2 tasks, 11+ tool calls)
    # ============================================================================

    tasks.append(Task(
        id="cs_expert_01",
        name="Full Queue Triage",
        prompt="""Perform a full triage of open tickets:
        1. Find all open tickets
        2. Review each ticket's details and customer context
        3. Check for any service outages affecting tickets
        4. Prioritize based on urgency and customer tier
        5. Update priorities where needed
        6. For the most urgent ticket, investigate and send a response

        Provide a summary of your triage and actions taken.""",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_multi_constraint=True,
            requires_long_reasoning_chain=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["search_tickets"] + ["get_ticket"] * 4 + ["get_customer"] * 2 + ["check_product", "update_ticket", "send_response"],
        expected_answer=["triage", "priority", "urgent"],
        verifier_config={
            "answer": ["open", "priority", "urgent", "ticket"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_tickets", "get_ticket", "send_response"],
                "optional": ["get_customer", "check_product", "update_ticket", "search_kb"],
                "min_calls": 5,
                "max_calls": 20
            },
            "state": {
                "responses_sent": {"$length": {"$gte": 1}}
            }
        },
        description="Full ticket queue triage",
        min_tool_calls=5,
        max_tool_calls=20,
        tags=["triage", "queue", "prioritization", "comprehensive"],
    ))

    tasks.append(Task(
        id="cs_expert_02",
        name="Enterprise Account Crisis Management",
        prompt="""Customer cust_004 (enterprise tier) has raised a security documentation request and they're a high-value customer.

        Handle this comprehensively:
        1. Review their full customer profile and history
        2. Understand all their current tickets
        3. Find all relevant security documentation in the KB
        4. Check their product status
        5. Update the security ticket appropriately
        6. Prepare a detailed response with all requested documentation links
        7. Escalate to the security team for direct follow-up
        8. Add internal notes documenting the situation

        Ensure the response is befitting an enterprise customer.""",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_long_reasoning_chain=True,
            requires_multi_constraint=True,
            requires_plan_adaptation=True,
        ),
        expected_tool_calls=["get_customer", "search_tickets", "get_ticket", "get_ticket", "search_kb", "check_product", "update_ticket", "send_response", "escalate_ticket"],
        expected_answer=["enterprise", "SOC 2", "escalated", "security"],
        verifier_config={
            "answer": ["enterprise", "SOC 2", "security", "Emily Davis"],
            "match_mode": "contains",
            "tools": {
                "required": ["get_customer", "search_kb", "send_response"],
                "optional": ["search_tickets", "get_ticket", "check_product", "update_ticket", "escalate_ticket"],
                "min_calls": 5,
                "max_calls": 15
            },
            "state": {
                "responses_sent": {"$length": {"$gte": 1}}
            }
        },
        description="High-touch enterprise customer handling",
        min_tool_calls=5,
        max_tool_calls=15,
        tags=["enterprise", "security", "comprehensive", "high-value"],
    ))

    # ============================================================================
    # TRUE TOOL-DRIVEN CONTROL FLOW TASKS
    # These tasks require discovering what to do from tool responses
    # ============================================================================

    tasks.append(Task(
        id="cs_discovery_01",
        name="Resolve Customer Issue",
        prompt="Ticket ticket_001 was just assigned to you. Investigate what the issue is and resolve it appropriately.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Must discover issue TYPE before knowing which tools/KB articles to use
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_plan_adaptation=True,
        ),
        expected_tool_calls=["get_ticket"],  # Issue type determines: billing tools, technical tools, or account tools
        expected_answer=["resolved", "issue", "response"],
        verifier_config={
            "answer": ["ticket", "issue", "response"],
            "match_mode": "contains",
            "tools": {
                "required": ["get_ticket"],
                "optional": ["get_customer", "search_kb", "check_product", "update_ticket", "send_response", "escalate_ticket"],
                "min_calls": 2,
                "max_calls": 10
            },
            "state": {
                "responses_sent": {"$length": {"$gte": 1}}
            }
        },
        description="TRUE tool-driven: issue type determines resolution path",
        min_tool_calls=2,
        max_tool_calls=10,
        tags=["discovery", "resolution", "branching"],
    ))

    tasks.append(Task(
        id="cs_discovery_02",
        name="Handle Next Queue Item",
        prompt="Take the next open ticket from the queue and handle it completely - investigate, resolve, and respond to the customer.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Don't know WHICH ticket or WHAT issue until we search
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["search_tickets", "get_ticket"],  # Ticket content determines all subsequent actions
        expected_answer=["handled", "resolved", "response"],
        verifier_config={
            "answer": ["ticket", "handled", "response"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_tickets", "get_ticket", "send_response"],
                "optional": ["get_customer", "search_kb", "check_product", "update_ticket", "escalate_ticket"],
                "min_calls": 3,
                "max_calls": 10
            },
            "state": {
                "responses_sent": {"$length": {"$gte": 1}}
            }
        },
        description="TRUE tool-driven: unknown ticket determines entire workflow",
        min_tool_calls=3,
        max_tool_calls=10,
        tags=["discovery", "queue", "complete-resolution"],
    ))

    tasks.append(Task(
        id="cs_discovery_03",
        name="Diagnose Service Issue",
        prompt="A customer reports something is broken but hasn't specified what. Their customer ID is cust_001. Figure out what's wrong and help them.",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Must investigate customer history and service status to identify issue
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_cross_reference=True,
            requires_disambiguation=True,
        ),
        expected_tool_calls=["get_customer", "search_tickets", "check_product"],  # Investigation determines resolution
        expected_answer=["diagnosed", "issue", "resolved"],
        verifier_config={
            "answer": ["issue", "customer", "response"],
            "match_mode": "contains",
            "tools": {
                "required": ["get_customer"],
                "optional": ["search_tickets", "get_ticket", "search_kb", "check_product", "update_ticket", "send_response"],
                "min_calls": 2,
                "max_calls": 12
            }
        },
        description="TRUE tool-driven: vague complaint requires investigation-driven diagnosis",
        min_tool_calls=2,
        max_tool_calls=12,
        tags=["discovery", "diagnosis", "ambiguous"],
    ))

    tasks.append(Task(
        id="cs_discovery_04",
        name="Handle Service Outage Impact",
        prompt="We have an ongoing service issue. Check which customers are affected and proactively reach out to those with open tickets.",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Must discover WHAT service issue and WHICH customers affected
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_state_tracking=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["check_product", "search_tickets"],  # Service status determines affected customers
        expected_answer=["notified", "affected", "customers"],
        verifier_config={
            "answer": ["outage", "customer", "response", "ticket"],
            "match_mode": "contains",
            "tools": {
                "required": ["check_product", "search_tickets"],
                "optional": ["get_ticket", "get_customer", "send_response", "update_ticket"],
                "min_calls": 3,
                "max_calls": 15
            }
        },
        description="TRUE tool-driven: service status determines customer outreach",
        min_tool_calls=3,
        max_tool_calls=15,
        tags=["discovery", "outage", "proactive"],
    ))

    tasks.append(Task(
        id="cs_discovery_05",
        name="Prioritize and Escalate",
        prompt="Review all open tickets. If any require escalation based on severity or customer tier, escalate them appropriately.",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Must discover ticket contents to determine escalation needs
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_multi_constraint=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["search_tickets"],  # Ticket details determine escalation decisions
        expected_answer=["reviewed", "escalated", "priority"],
        verifier_config={
            "answer": ["ticket", "priority", "escalat"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_tickets"],
                "optional": ["get_ticket", "get_customer", "escalate_ticket", "update_ticket", "send_response"],
                "min_calls": 2,
                "max_calls": 15
            }
        },
        description="TRUE tool-driven: ticket details determine escalation decisions",
        min_tool_calls=2,
        max_tool_calls=15,
        tags=["discovery", "triage", "escalation"],
    ))

    tasks.append(Task(
        id="cs_discovery_06",
        name="Customer Health Check",
        prompt="Check on customer cust_004's overall experience. If they have any unresolved issues or complaints, address them proactively.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Must discover customer history to know what (if any) action to take
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_cross_reference=True,
        ),
        expected_tool_calls=["get_customer", "search_tickets"],  # Customer situation determines response
        expected_answer=["health", "customer", "addressed"],
        verifier_config={
            "answer": ["customer", "ticket", "addressed"],
            "match_mode": "contains",
            "tools": {
                "required": ["get_customer", "search_tickets"],
                "optional": ["get_ticket", "search_kb", "send_response", "update_ticket"],
                "min_calls": 2,
                "max_calls": 10
            }
        },
        description="TRUE tool-driven: customer history determines if action needed",
        min_tool_calls=2,
        max_tool_calls=10,
        tags=["discovery", "proactive", "health-check"],
    ))

    return tasks
