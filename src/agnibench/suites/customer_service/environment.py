"""
Simulated environment for the customer service benchmark suite.
"""

from datetime import datetime, timedelta

from agnibench.core.environment import SimulatedEnvironment
from agnibench.suites.customer_service.tools import (get_service_data,
                                                     set_service_data)


class CustomerServiceEnvironment(SimulatedEnvironment):
    """
    Environment for customer service tasks.

    Manages tickets, customers, knowledge base, and service status.
    """

    def _setup_default_state(self) -> None:
        """Set up default state with sample customer service data."""
        now = datetime.now()

        # Sample customers
        customers = [
            {
                "id": "cust_001",
                "name": "John Smith",
                "email": "john.smith@example.com",
                "tier": "enterprise",
                "status": "active",
                "created_date": (now - timedelta(days=365)).isoformat(),
                "products": ["Pro Plan", "API Access"],
                "lifetime_value": 15000,
                "support_tickets_count": 8,
                "satisfaction_score": 4.2,
            },
            {
                "id": "cust_002",
                "name": "Sarah Johnson",
                "email": "sarah.j@startup.io",
                "tier": "premium",
                "status": "active",
                "created_date": (now - timedelta(days=180)).isoformat(),
                "products": ["Pro Plan"],
                "lifetime_value": 3600,
                "support_tickets_count": 3,
                "satisfaction_score": 4.8,
            },
            {
                "id": "cust_003",
                "name": "Mike Chen",
                "email": "mchen@techcorp.com",
                "tier": "basic",
                "status": "trial",
                "created_date": (now - timedelta(days=14)).isoformat(),
                "products": ["Starter Plan"],
                "lifetime_value": 0,
                "support_tickets_count": 2,
                "satisfaction_score": None,
            },
            {
                "id": "cust_004",
                "name": "Emily Davis",
                "email": "emily.davis@bigco.com",
                "tier": "enterprise",
                "status": "active",
                "created_date": (now - timedelta(days=500)).isoformat(),
                "products": ["Enterprise Suite", "API Access", "Premium Support"],
                "lifetime_value": 50000,
                "support_tickets_count": 15,
                "satisfaction_score": 3.9,
            },
        ]

        # Sample tickets
        tickets = [
            {
                "id": "ticket_001",
                "customer_id": "cust_001",
                "subject": "Unable to access dashboard after password reset",
                "description": "I reset my password yesterday and now I can't log in. The system says my credentials are invalid even though I just changed them. I've tried multiple browsers. This is urgent as I need to access reports for a meeting.",
                "issue_type": "account",
                "priority": "high",
                "status": "open",
                "created_at": (now - timedelta(hours=4)).isoformat(),
                "updated_at": (now - timedelta(hours=4)).isoformat(),
                "assigned_to": None,
                "tags": ["login", "password", "urgent"],
            },
            {
                "id": "ticket_002",
                "customer_id": "cust_002",
                "subject": "Billing discrepancy - charged twice",
                "description": "I noticed I was charged twice for this month's subscription. Amount: $99 each time. Please refund the duplicate charge. Transaction IDs: TXN123 and TXN124.",
                "issue_type": "billing",
                "priority": "high",
                "status": "open",
                "created_at": (now - timedelta(hours=2)).isoformat(),
                "updated_at": (now - timedelta(hours=2)).isoformat(),
                "assigned_to": None,
                "tags": ["billing", "refund", "duplicate"],
            },
            {
                "id": "ticket_003",
                "customer_id": "cust_003",
                "subject": "API returning 500 errors",
                "description": "Getting intermittent 500 errors from the /api/v2/users endpoint. Started about an hour ago. Here's the error response: {'error': 'Internal server error', 'request_id': 'abc123'}",
                "issue_type": "technical",
                "priority": "urgent",
                "status": "open",
                "created_at": (now - timedelta(hours=1)).isoformat(),
                "updated_at": (now - timedelta(hours=1)).isoformat(),
                "assigned_to": None,
                "tags": ["api", "error", "technical"],
            },
            {
                "id": "ticket_004",
                "customer_id": "cust_004",
                "subject": "Feature request: Custom report builder",
                "description": "We'd like to request a custom report builder feature. Currently we export data and build reports manually. A drag-and-drop report builder would save us significant time.",
                "issue_type": "feature_request",
                "priority": "low",
                "status": "open",
                "created_at": (now - timedelta(days=3)).isoformat(),
                "updated_at": (now - timedelta(days=3)).isoformat(),
                "assigned_to": None,
                "tags": ["feature", "reports"],
            },
            {
                "id": "ticket_005",
                "customer_id": "cust_001",
                "subject": "Data export failing for large datasets",
                "description": "When I try to export more than 10,000 records, the export fails silently. No error message, just nothing happens. I've waited up to 30 minutes.",
                "issue_type": "technical",
                "priority": "medium",
                "status": "in_progress",
                "created_at": (now - timedelta(days=1)).isoformat(),
                "updated_at": (now - timedelta(hours=6)).isoformat(),
                "assigned_to": "Agent_Sarah",
                "tags": ["export", "data", "bug"],
                "internal_notes": [
                    {
                        "note": "Investigating export queue system",
                        "added_at": (now - timedelta(hours=6)).isoformat(),
                    }
                ],
            },
            {
                "id": "ticket_006",
                "customer_id": "cust_004",
                "subject": "Security audit documentation needed",
                "description": "Our compliance team needs documentation about your security practices for our annual audit. Specifically need: SOC 2 report, data encryption details, and incident response procedures.",
                "issue_type": "general_inquiry",
                "priority": "medium",
                "status": "open",
                "created_at": (now - timedelta(days=2)).isoformat(),
                "updated_at": (now - timedelta(days=2)).isoformat(),
                "assigned_to": None,
                "tags": ["security", "compliance", "documentation"],
            },
            # EDGE CASE: Closed ticket - should not be in active queue
            {
                "id": "ticket_007",
                "customer_id": "cust_002",
                "subject": "Previous billing inquiry - RESOLVED",
                "description": "This was resolved last week.",
                "issue_type": "billing",
                "priority": "low",
                "status": "closed",
                "created_at": (now - timedelta(days=10)).isoformat(),
                "updated_at": (now - timedelta(days=7)).isoformat(),
                "assigned_to": "Agent_Mike",
                "resolution": "Refund processed successfully",
                "tags": ["billing", "resolved"],
            },
            # EDGE CASE: Duplicate ticket - same customer, similar issue
            {
                "id": "ticket_008",
                "customer_id": "cust_001",
                "subject": "Still can't log in - follow up",
                "description": "Same issue as before, the password reset didn't work. This is getting frustrating.",
                "issue_type": "account",
                "priority": "high",
                "status": "open",
                "created_at": (now - timedelta(hours=1)).isoformat(),
                "updated_at": (now - timedelta(hours=1)).isoformat(),
                "assigned_to": None,
                "tags": ["login", "password", "follow-up", "frustrated"],
                "related_ticket": "ticket_001",  # Linked to original ticket
            },
            # EDGE CASE: VIP customer with urgent issue
            {
                "id": "ticket_009",
                "customer_id": "cust_004",
                "subject": "URGENT: Production system down",
                "description": "Our entire production environment is showing errors. This is impacting our business operations. Need immediate assistance!",
                "issue_type": "technical",
                "priority": "urgent",
                "status": "open",
                "created_at": (now - timedelta(minutes=30)).isoformat(),
                "updated_at": (now - timedelta(minutes=30)).isoformat(),
                "assigned_to": None,
                "tags": ["production", "urgent", "enterprise", "critical"],
                "sla_deadline": (now + timedelta(hours=1)).isoformat(),  # SLA pressure
            },
            # EDGE CASE: Ticket with missing/null customer reference
            {
                "id": "ticket_010",
                "customer_id": None,  # Edge case: orphaned ticket
                "subject": "Anonymous feedback",
                "description": "Submitted via public form - no account attached.",
                "issue_type": "feedback",
                "priority": "low",
                "status": "open",
                "created_at": (now - timedelta(days=1)).isoformat(),
                "updated_at": (now - timedelta(days=1)).isoformat(),
                "assigned_to": None,
                "tags": ["feedback", "anonymous"],
            },
        ]

        # Knowledge base articles
        knowledge_base = [
            {
                "id": "kb_001",
                "title": "How to Reset Your Password",
                "category": "account",
                "keywords": ["password", "reset", "login", "access"],
                "content": """To reset your password:
1. Go to the login page
2. Click "Forgot Password"
3. Enter your email address
4. Check your email for the reset link
5. Create a new password (minimum 8 characters)

Note: After resetting, you may need to clear your browser cache if you experience issues logging in.

If you're still having trouble, ensure:
- You're using the correct email address
- Check spam folder for reset email
- Try a different browser
- Clear cookies and cache""",
            },
            {
                "id": "kb_002",
                "title": "Understanding Your Bill",
                "category": "billing",
                "keywords": ["billing", "invoice", "charge", "payment", "refund"],
                "content": """Your bill includes:
- Monthly subscription fee
- Any usage overages
- Add-on services

Common billing questions:
- Duplicate charges: Contact support for investigation and refund
- Proration: Upgrades are prorated, downgrades take effect next cycle
- Refunds: Processed within 5-7 business days

To view your billing history, go to Settings > Billing > History.""",
            },
            {
                "id": "kb_003",
                "title": "API Error Codes and Solutions",
                "category": "technical",
                "keywords": ["api", "error", "500", "401", "403", "technical"],
                "content": """Common API errors:

500 Internal Server Error:
- Usually temporary, retry after a few seconds
- If persistent, check status.example.com for outages
- Include request_id when contacting support

401 Unauthorized:
- API key invalid or expired
- Regenerate key in Settings > API

403 Forbidden:
- Endpoint not available on your plan
- Check your plan's API access level

429 Too Many Requests:
- Rate limit exceeded
- Implement exponential backoff""",
            },
            {
                "id": "kb_004",
                "title": "Data Export Guide",
                "category": "technical",
                "keywords": ["export", "data", "csv", "download"],
                "content": """Exporting your data:

Small exports (< 10,000 records):
- Use the Export button in the UI
- Immediate download as CSV/Excel

Large exports (> 10,000 records):
- Use async export: Settings > Data > Schedule Export
- You'll receive an email when ready
- Files available for 7 days

Known limitation: UI exports timeout after 10,000 records. Use scheduled exports for larger datasets.""",
            },
            {
                "id": "kb_005",
                "title": "Security and Compliance Documentation",
                "category": "security",
                "keywords": ["security", "compliance", "soc2", "gdpr", "audit"],
                "content": """Available security documentation:

SOC 2 Type II Report:
- Available upon request for enterprise customers
- Contact support or your account manager

Security Whitepaper:
- Download from trust.example.com

Compliance certifications:
- SOC 2 Type II
- ISO 27001
- GDPR compliant
- HIPAA compliant (enterprise only)

For audit requests, we typically provide:
- SOC 2 report
- Penetration test summary
- Security questionnaire responses""",
            },
        ]

        # Products/Services status
        products = [
            {
                "id": "prod_dashboard",
                "name": "Dashboard",
                "status": "operational",
                "last_incident": None,
            },
            {
                "id": "prod_api",
                "name": "API",
                "status": "degraded",
                "last_incident": (now - timedelta(hours=2)).isoformat(),
                "incident_details": "Intermittent 500 errors on /api/v2/users endpoint. Engineering team investigating.",
            },
            {
                "id": "prod_export",
                "name": "Data Export",
                "status": "operational",
                "last_incident": (now - timedelta(days=5)).isoformat(),
            },
            {
                "id": "prod_auth",
                "name": "Authentication",
                "status": "operational",
                "last_incident": None,
            },
        ]

        service_data = {
            "tickets": tickets,
            "customers": customers,
            "knowledge_base": knowledge_base,
            "products": products,
            "ticket_updates": [],
            "escalations": [],
            "responses_sent": [],
        }

        set_service_data(service_data)

        # Store in environment state
        self._state["tickets"] = tickets
        self._state["customers"] = customers
        self._state["knowledge_base"] = knowledge_base
        self._state["products"] = products
        self._state["ticket_updates"] = []
        self._state["escalations"] = []
        self._state["responses_sent"] = []

    def reset(self) -> None:
        """Reset the environment."""
        super().reset()
        self._setup_default_state()

    def sync_state_from_service(self) -> None:
        """Sync environment state from service data."""
        service_data = get_service_data()
        self._state["ticket_updates"] = service_data.get("ticket_updates", [])
        self._state["escalations"] = service_data.get("escalations", [])
        self._state["responses_sent"] = service_data.get("responses_sent", [])

    @property
    def open_ticket_count(self) -> int:
        """Number of open tickets."""
        return sum(
            1 for t in self._state.get("tickets", []) if t.get("status") == "open"
        )

    @property
    def response_count(self) -> int:
        """Number of responses sent."""
        return len(self._state.get("responses_sent", []))

    @property
    def escalation_count(self) -> int:
        """Number of escalations made."""
        return len(self._state.get("escalations", []))
