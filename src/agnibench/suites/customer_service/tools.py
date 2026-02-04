"""
Tools for the customer service benchmark suite.

Provides 8 tools for ticket management, customer lookup, and issue resolution.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from agentbuilder.Tools.base import Tool


# Storage for simulated data
_service_data: Dict[str, Any] = {
    "tickets": [],
    "customers": [],
    "knowledge_base": [],
    "products": [],
    "ticket_updates": [],
    "escalations": [],
    "responses_sent": [],
}


def set_service_data(data: Dict[str, Any]) -> None:
    """Set the service data (called by environment)."""
    global _service_data
    _service_data = data


def get_service_data() -> Dict[str, Any]:
    """Get current service data."""
    return _service_data


# Pydantic models

class SearchTicketsParams(BaseModel):
    """Parameters for searching tickets."""
    query: Optional[str] = Field(default=None, description="Text search in ticket content")
    customer_id: Optional[str] = Field(default=None, description="Filter by customer ID")
    status: Optional[str] = Field(default=None, description="Filter by status: open, in_progress, resolved, closed")
    priority: Optional[str] = Field(default=None, description="Filter by priority: low, medium, high, urgent")
    issue_type: Optional[str] = Field(default=None, description="Filter by issue type")
    limit: int = Field(default=10, description="Maximum results")


class GetTicketParams(BaseModel):
    """Parameters for getting ticket details."""
    ticket_id: str = Field(description="ID of the ticket to retrieve")


class UpdateTicketParams(BaseModel):
    """Parameters for updating a ticket."""
    ticket_id: str = Field(description="ID of the ticket to update")
    status: Optional[str] = Field(default=None, description="New status")
    priority: Optional[str] = Field(default=None, description="New priority")
    notes: Optional[str] = Field(default=None, description="Internal notes to add")
    assigned_to: Optional[str] = Field(default=None, description="Assign to agent")


class SearchKBParams(BaseModel):
    """Parameters for searching knowledge base."""
    query: str = Field(description="Search query")
    category: Optional[str] = Field(default=None, description="Filter by category")
    limit: int = Field(default=5, description="Maximum results")


class GetCustomerParams(BaseModel):
    """Parameters for getting customer information."""
    customer_id: str = Field(description="Customer ID to look up")


class CheckProductParams(BaseModel):
    """Parameters for checking product/service status."""
    product_id: Optional[str] = Field(default=None, description="Product ID to check")
    service_name: Optional[str] = Field(default=None, description="Service name to check status")


class EscalateTicketParams(BaseModel):
    """Parameters for escalating a ticket."""
    ticket_id: str = Field(description="ID of the ticket to escalate")
    reason: str = Field(description="Reason for escalation")
    specialist_team: Optional[str] = Field(default=None, description="Team to escalate to")


class SendResponseParams(BaseModel):
    """Parameters for sending customer response."""
    ticket_id: str = Field(description="ID of the ticket to respond to")
    message: str = Field(description="Response message to customer")
    resolution_type: Optional[str] = Field(default=None, description="Type: answer, solution, follow_up, escalation_notice")


# Pydantic result models

class TicketSummary(BaseModel):
    """Summary of a ticket in search results."""
    id: Optional[str] = None
    customer_id: Optional[str] = None
    subject: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    issue_type: Optional[str] = None
    created_at: Optional[str] = None
    preview: Optional[str] = None


class SearchTicketsResult(BaseModel):
    """Result of searching tickets."""
    results: List[TicketSummary]
    count: int


class GetTicketResult(BaseModel):
    """Result of getting a ticket."""
    found: bool
    ticket: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class UpdateTicketResult(BaseModel):
    """Result of updating a ticket."""
    success: bool
    message: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class KBArticleSummary(BaseModel):
    """Summary of a knowledge base article."""
    id: Optional[str] = None
    title: Optional[str] = None
    category: Optional[str] = None
    preview: Optional[str] = None
    relevance: Optional[str] = None


class SearchKBResult(BaseModel):
    """Result of searching the knowledge base."""
    query: str
    results: List[KBArticleSummary]
    count: int


class CustomerTicketSummary(BaseModel):
    """Summary of a customer's ticket."""
    id: str
    subject: str
    status: str


class GetCustomerResult(BaseModel):
    """Result of getting customer info."""
    found: bool
    customer: Optional[Dict[str, Any]] = None
    recent_tickets: Optional[List[CustomerTicketSummary]] = None
    total_tickets: Optional[int] = None
    error: Optional[str] = None


class GeneralServiceStatus(BaseModel):
    """General service status when no specific product is found."""
    all_services: str
    last_incident: str
    scheduled_maintenance: Optional[str] = None


class CheckProductResult(BaseModel):
    """Result of checking a product."""
    found: bool
    product: Optional[Dict[str, Any]] = None
    general_status: Optional[GeneralServiceStatus] = None


class EscalationDetails(BaseModel):
    """Details of an escalation."""
    ticket_id: str
    reason: str
    specialist_team: str
    escalated_at: str
    previous_status: Optional[str] = None


class EscalateTicketResult(BaseModel):
    """Result of escalating a ticket."""
    success: bool
    message: Optional[str] = None
    escalation: Optional[EscalationDetails] = None
    error: Optional[str] = None


class SendResponseResult(BaseModel):
    """Result of sending a response."""
    success: bool
    message: Optional[str] = None
    response_type: Optional[str] = None
    error: Optional[str] = None


# Tool implementations

def search_tickets(params: SearchTicketsParams) -> SearchTicketsResult:
    """Search support tickets."""
    tickets = _service_data.get("tickets", [])
    results = []

    for ticket in tickets:
        # Apply filters
        if params.query:
            query_lower = params.query.lower()
            if (query_lower not in ticket.get("subject", "").lower() and
                query_lower not in ticket.get("description", "").lower()):
                continue

        if params.customer_id:
            if ticket.get("customer_id") != params.customer_id:
                continue

        if params.status:
            if ticket.get("status", "").lower() != params.status.lower():
                continue

        if params.priority:
            if ticket.get("priority", "").lower() != params.priority.lower():
                continue

        if params.issue_type:
            if ticket.get("issue_type", "").lower() != params.issue_type.lower():
                continue

        results.append(TicketSummary(
            id=ticket.get("id"),
            customer_id=ticket.get("customer_id"),
            subject=ticket.get("subject"),
            status=ticket.get("status"),
            priority=ticket.get("priority"),
            issue_type=ticket.get("issue_type"),
            created_at=ticket.get("created_at"),
            preview=ticket.get("description", "")[:100],
        ))

        if len(results) >= params.limit:
            break

    return SearchTicketsResult(
        results=results,
        count=len(results),
    )


def get_ticket(params: GetTicketParams) -> GetTicketResult:
    """Get detailed ticket information."""
    tickets = _service_data.get("tickets", [])

    for ticket in tickets:
        if ticket.get("id") == params.ticket_id:
            return GetTicketResult(
                found=True,
                ticket=ticket,
            )

    return GetTicketResult(
        found=False,
        error=f"Ticket '{params.ticket_id}' not found",
    )


def update_ticket(params: UpdateTicketParams) -> UpdateTicketResult:
    """Update a ticket's status, priority, or add notes."""
    tickets = _service_data.get("tickets", [])

    for ticket in tickets:
        if ticket.get("id") == params.ticket_id:
            update = {
                "ticket_id": params.ticket_id,
                "timestamp": datetime.now().isoformat(),
                "changes": {},
            }

            if params.status:
                ticket["status"] = params.status
                update["changes"]["status"] = params.status

            if params.priority:
                ticket["priority"] = params.priority
                update["changes"]["priority"] = params.priority

            if params.notes:
                if "internal_notes" not in ticket:
                    ticket["internal_notes"] = []
                ticket["internal_notes"].append({
                    "note": params.notes,
                    "added_at": datetime.now().isoformat(),
                })
                update["changes"]["notes_added"] = True

            if params.assigned_to:
                ticket["assigned_to"] = params.assigned_to
                update["changes"]["assigned_to"] = params.assigned_to

            if "ticket_updates" not in _service_data:
                _service_data["ticket_updates"] = []
            _service_data["ticket_updates"].append(update)

            return UpdateTicketResult(
                success=True,
                message=f"Ticket {params.ticket_id} updated",
                changes=update["changes"],
            )

    return UpdateTicketResult(
        success=False,
        error=f"Ticket '{params.ticket_id}' not found",
    )


def search_kb(params: SearchKBParams) -> SearchKBResult:
    """Search knowledge base for solutions."""
    kb_articles = _service_data.get("knowledge_base", [])
    results = []

    query_lower = params.query.lower()

    for article in kb_articles:
        # Check title, content, and keywords
        title_match = query_lower in article.get("title", "").lower()
        content_match = query_lower in article.get("content", "").lower()
        keyword_match = any(query_lower in kw.lower() for kw in article.get("keywords", []))

        if title_match or content_match or keyword_match:
            if params.category:
                if article.get("category", "").lower() != params.category.lower():
                    continue

            results.append(KBArticleSummary(
                id=article.get("id"),
                title=article.get("title"),
                category=article.get("category"),
                preview=article.get("content", "")[:200],
                relevance="high" if title_match else "medium",
            ))

            if len(results) >= params.limit:
                break

    return SearchKBResult(
        query=params.query,
        results=results,
        count=len(results),
    )


def get_customer(params: GetCustomerParams) -> GetCustomerResult:
    """Get customer profile and history."""
    customers = _service_data.get("customers", [])

    for customer in customers:
        if customer.get("id") == params.customer_id:
            # Get customer's ticket history
            tickets = _service_data.get("tickets", [])
            customer_tickets = [
                CustomerTicketSummary(id=t["id"], subject=t["subject"], status=t["status"])
                for t in tickets
                if t.get("customer_id") == params.customer_id
            ]

            return GetCustomerResult(
                found=True,
                customer=customer,
                recent_tickets=customer_tickets[:5],
                total_tickets=len(customer_tickets),
            )

    return GetCustomerResult(
        found=False,
        error=f"Customer '{params.customer_id}' not found",
    )


def check_product(params: CheckProductParams) -> CheckProductResult:
    """Check product or service status."""
    products = _service_data.get("products", [])

    for product in products:
        if params.product_id and product.get("id") == params.product_id:
            return CheckProductResult(
                found=True,
                product=product,
            )
        if params.service_name and params.service_name.lower() in product.get("name", "").lower():
            return CheckProductResult(
                found=True,
                product=product,
            )

    # Return general service status if no specific product found
    return CheckProductResult(
        found=False,
        general_status=GeneralServiceStatus(
            all_services="operational",
            last_incident="2024-01-10",
            scheduled_maintenance=None,
        ),
    )


def escalate_ticket(params: EscalateTicketParams) -> EscalateTicketResult:
    """Escalate a ticket to a specialist team."""
    tickets = _service_data.get("tickets", [])

    for ticket in tickets:
        if ticket.get("id") == params.ticket_id:
            specialist_team = params.specialist_team or "tier2_support"
            escalation = EscalationDetails(
                ticket_id=params.ticket_id,
                reason=params.reason,
                specialist_team=specialist_team,
                escalated_at=datetime.now().isoformat(),
                previous_status=ticket.get("status"),
            )

            ticket["status"] = "escalated"
            ticket["escalated_to"] = specialist_team

            if "escalations" not in _service_data:
                _service_data["escalations"] = []
            _service_data["escalations"].append(escalation.model_dump())

            return EscalateTicketResult(
                success=True,
                message=f"Ticket {params.ticket_id} escalated to {specialist_team}",
                escalation=escalation,
            )

    return EscalateTicketResult(
        success=False,
        error=f"Ticket '{params.ticket_id}' not found",
    )


def send_response(params: SendResponseParams) -> SendResponseResult:
    """Send a response to the customer."""
    tickets = _service_data.get("tickets", [])

    for ticket in tickets:
        if ticket.get("id") == params.ticket_id:
            response = {
                "ticket_id": params.ticket_id,
                "message": params.message,
                "resolution_type": params.resolution_type or "follow_up",
                "sent_at": datetime.now().isoformat(),
            }

            if "responses_sent" not in _service_data:
                _service_data["responses_sent"] = []
            _service_data["responses_sent"].append(response)

            # Update ticket if resolution
            if params.resolution_type == "solution":
                ticket["status"] = "resolved"

            return SendResponseResult(
                success=True,
                message=f"Response sent to customer for ticket {params.ticket_id}",
                response_type=params.resolution_type,
            )

    return SendResponseResult(
        success=False,
        error=f"Ticket '{params.ticket_id}' not found",
    )


# Tool creation

def get_customer_service_tools() -> List[Tool]:
    """Get all customer service tools."""
    return [
        Tool(
            name="search_tickets",
            description="Search support tickets by query, customer, status, priority, or issue type.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Text search in ticket content"},
                    "customer_id": {"type": "string", "description": "Filter by customer ID"},
                    "status": {"type": "string", "enum": ["open", "in_progress", "resolved", "closed", "escalated"], "description": "Filter by status"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "description": "Filter by priority"},
                    "issue_type": {"type": "string", "description": "Filter by issue type"},
                    "limit": {"type": "integer", "description": "Maximum results", "default": 10}
                },
                "required": []
            },
            function=lambda **kwargs: search_tickets(SearchTicketsParams(**kwargs))
        ),
        Tool(
            name="get_ticket",
            description="Get detailed information about a specific support ticket.",
            parameters={
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string", "description": "ID of the ticket"}
                },
                "required": ["ticket_id"]
            },
            function=lambda **kwargs: get_ticket(GetTicketParams(**kwargs))
        ),
        Tool(
            name="update_ticket",
            description="Update a ticket's status, priority, assignment, or add internal notes.",
            parameters={
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string", "description": "ID of the ticket"},
                    "status": {"type": "string", "enum": ["open", "in_progress", "resolved", "closed"], "description": "New status"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "description": "New priority"},
                    "notes": {"type": "string", "description": "Internal notes to add"},
                    "assigned_to": {"type": "string", "description": "Assign to agent"}
                },
                "required": ["ticket_id"]
            },
            function=lambda **kwargs: update_ticket(UpdateTicketParams(**kwargs))
        ),
        Tool(
            name="search_kb",
            description="Search the knowledge base for articles and solutions.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "category": {"type": "string", "description": "Filter by category"},
                    "limit": {"type": "integer", "description": "Maximum results", "default": 5}
                },
                "required": ["query"]
            },
            function=lambda **kwargs: search_kb(SearchKBParams(**kwargs))
        ),
        Tool(
            name="get_customer",
            description="Get customer profile, history, and account information.",
            parameters={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "Customer ID"}
                },
                "required": ["customer_id"]
            },
            function=lambda **kwargs: get_customer(GetCustomerParams(**kwargs))
        ),
        Tool(
            name="check_product",
            description="Check product or service status, including any known issues or outages.",
            parameters={
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "Product ID to check"},
                    "service_name": {"type": "string", "description": "Service name to check"}
                },
                "required": []
            },
            function=lambda **kwargs: check_product(CheckProductParams(**kwargs))
        ),
        Tool(
            name="escalate_ticket",
            description="Escalate a ticket to a specialist team for complex issues.",
            parameters={
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string", "description": "ID of the ticket"},
                    "reason": {"type": "string", "description": "Reason for escalation"},
                    "specialist_team": {"type": "string", "description": "Team to escalate to: billing, technical, security, management"}
                },
                "required": ["ticket_id", "reason"]
            },
            function=lambda **kwargs: escalate_ticket(EscalateTicketParams(**kwargs))
        ),
        Tool(
            name="send_response",
            description="Send a response message to the customer for a ticket.",
            parameters={
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string", "description": "ID of the ticket"},
                    "message": {"type": "string", "description": "Response message"},
                    "resolution_type": {"type": "string", "enum": ["answer", "solution", "follow_up", "escalation_notice"], "description": "Type of response"}
                },
                "required": ["ticket_id", "message"]
            },
            function=lambda **kwargs: send_response(SendResponseParams(**kwargs))
        ),
    ]
