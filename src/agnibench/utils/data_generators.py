"""
Synthetic data generators for benchmark suites.

Generates realistic test data for various benchmark scenarios.
"""

import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


def random_id(prefix: str = "") -> str:
    """Generate a random ID with optional prefix."""
    return f"{prefix}{uuid.uuid4().hex[:8]}"


def random_name() -> str:
    """Generate a random name."""
    first_names = [
        "Alice",
        "Bob",
        "Carol",
        "David",
        "Eve",
        "Frank",
        "Grace",
        "Henry",
        "Ivy",
        "Jack",
    ]
    last_names = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Garcia",
        "Miller",
        "Davis",
        "Martinez",
        "Wilson",
    ]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def random_email_address(name: Optional[str] = None) -> str:
    """Generate a random email address."""
    if name:
        local = name.lower().replace(" ", ".")
    else:
        local = "".join(random.choices(string.ascii_lowercase, k=8))
    domains = ["example.com", "test.org", "company.io", "acme.corp"]
    return f"{local}@{random.choice(domains)}"


def random_date(start_days_ago: int = 30, end_days_ahead: int = 30) -> datetime:
    """Generate a random date within a range."""
    now = datetime.now()
    delta = random.randint(-start_days_ago, end_days_ahead)
    return now + timedelta(days=delta)


def generate_random_email(
    email_id: Optional[str] = None,
    sender: Optional[str] = None,
    recipient: Optional[str] = None,
    subject: Optional[str] = None,
    body: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a random email.

    Args:
        email_id: Optional ID (generated if not provided)
        sender: Optional sender name
        recipient: Optional recipient name
        subject: Optional subject line
        body: Optional email body

    Returns:
        Dict with email data
    """
    sender_name = sender or random_name()
    recipient_name = recipient or random_name()

    subjects = [
        "Meeting Request",
        "Project Update",
        "Quick Question",
        "Follow-up from our call",
        "Important: Action Required",
        "Weekly Report",
        "Invitation: Team Sync",
        "Re: Your Request",
    ]

    bodies = [
        "Hi,\n\nI wanted to follow up on our previous discussion. Let me know when you're available to chat.\n\nBest,\n{sender}",
        "Hello,\n\nPlease review the attached document and provide your feedback by end of week.\n\nThanks,\n{sender}",
        "Hi there,\n\nJust a quick note to confirm our meeting tomorrow at 2pm. See you then!\n\nRegards,\n{sender}",
        "Hello,\n\nI've completed the analysis you requested. Key findings:\n- Revenue increased 15%\n- Customer satisfaction at 92%\n- Three new opportunities identified\n\nLet's discuss next steps.\n\n{sender}",
    ]

    return {
        "id": email_id or random_id("email_"),
        "sender": sender_name,
        "sender_email": random_email_address(sender_name),
        "recipient": recipient_name,
        "recipient_email": random_email_address(recipient_name),
        "subject": subject or random.choice(subjects),
        "body": (body or random.choice(bodies)).format(sender=sender_name),
        "timestamp": random_date(start_days_ago=14, end_days_ahead=0).isoformat(),
        "read": random.choice([True, False]),
        "labels": random.sample(
            ["inbox", "important", "work", "personal"], k=random.randint(1, 2)
        ),
    }


def generate_random_calendar_event(
    event_id: Optional[str] = None,
    title: Optional[str] = None,
    start_time: Optional[datetime] = None,
    duration_minutes: Optional[int] = None,
    attendees: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Generate a random calendar event.

    Args:
        event_id: Optional ID
        title: Optional event title
        start_time: Optional start time
        duration_minutes: Optional duration
        attendees: Optional list of attendee names

    Returns:
        Dict with event data
    """
    titles = [
        "Team Standup",
        "1:1 Meeting",
        "Project Review",
        "Client Call",
        "Planning Session",
        "Training Workshop",
        "All Hands Meeting",
        "Design Review",
    ]

    start = start_time or random_date(start_days_ago=0, end_days_ahead=14)
    # Align to hour
    start = start.replace(minute=0, second=0, microsecond=0)
    start = start.replace(hour=random.randint(9, 17))

    duration = duration_minutes or random.choice([30, 60, 90, 120])
    end = start + timedelta(minutes=duration)

    if attendees is None:
        attendees = [random_name() for _ in range(random.randint(1, 5))]

    return {
        "id": event_id or random_id("event_"),
        "title": title or random.choice(titles),
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "duration_minutes": duration,
        "attendees": attendees,
        "location": random.choice(
            ["Conference Room A", "Conference Room B", "Virtual", "Office 301", ""]
        ),
        "description": f"Meeting with {', '.join(attendees[:2])}",
        "organizer": random_name(),
        "status": random.choice(["confirmed", "tentative", "cancelled"]),
    }


def generate_random_customer(
    customer_id: Optional[str] = None,
    name: Optional[str] = None,
    tier: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a random customer profile.

    Args:
        customer_id: Optional ID
        name: Optional customer name
        tier: Optional tier (basic, premium, enterprise)

    Returns:
        Dict with customer data
    """
    customer_name = name or random_name()
    tiers = ["basic", "premium", "enterprise"]

    products = ["Pro Plan", "Starter Plan", "Enterprise Suite", "Basic Package"]
    statuses = ["active", "churned", "trial", "suspended"]

    return {
        "id": customer_id or random_id("cust_"),
        "name": customer_name,
        "email": random_email_address(customer_name),
        "tier": tier or random.choice(tiers),
        "status": random.choice(statuses),
        "created_date": random_date(start_days_ago=365, end_days_ahead=0).isoformat(),
        "products": random.sample(products, k=random.randint(1, 3)),
        "lifetime_value": round(random.uniform(100, 10000), 2),
        "support_tickets_count": random.randint(0, 20),
        "last_contact": random_date(start_days_ago=30, end_days_ahead=0).isoformat(),
        "satisfaction_score": round(random.uniform(1, 5), 1),
        "company": (
            f"{customer_name.split()[1]} Corp" if random.random() > 0.5 else None
        ),
    }


def generate_random_ticket(
    ticket_id: Optional[str] = None,
    customer_id: Optional[str] = None,
    issue_type: Optional[str] = None,
    priority: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a random support ticket.

    Args:
        ticket_id: Optional ID
        customer_id: Optional customer ID
        issue_type: Optional issue type
        priority: Optional priority

    Returns:
        Dict with ticket data
    """
    issue_types = [
        "billing",
        "technical",
        "account",
        "feature_request",
        "bug_report",
        "general_inquiry",
    ]

    priorities = ["low", "medium", "high", "urgent"]
    statuses = ["open", "in_progress", "waiting_customer", "resolved", "closed"]

    descriptions = [
        "Unable to access my account after password reset",
        "Billing charge appears incorrect for last month",
        "Feature not working as expected",
        "Need help with API integration",
        "Request for account upgrade",
        "Performance issues with the dashboard",
        "Data export not completing",
    ]

    return {
        "id": ticket_id or random_id("ticket_"),
        "customer_id": customer_id or random_id("cust_"),
        "issue_type": issue_type or random.choice(issue_types),
        "priority": priority or random.choice(priorities),
        "status": random.choice(statuses),
        "subject": random.choice(descriptions)[:50],
        "description": random.choice(descriptions),
        "created_at": random_date(start_days_ago=7, end_days_ahead=0).isoformat(),
        "updated_at": random_date(start_days_ago=2, end_days_ahead=0).isoformat(),
        "assigned_to": random_name() if random.random() > 0.3 else None,
        "tags": random.sample(
            ["urgent", "vip", "escalated", "first_contact", "recurring"],
            k=random.randint(0, 2),
        ),
        "resolution": (
            None
            if random.random() > 0.3
            else "Issue resolved by updating configuration"
        ),
    }


def generate_random_dataset(
    dataset_id: Optional[str] = None,
    name: Optional[str] = None,
    num_rows: Optional[int] = None,
    columns: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """
    Generate a random dataset metadata.

    Args:
        dataset_id: Optional ID
        name: Optional dataset name
        num_rows: Optional number of rows
        columns: Optional column definitions

    Returns:
        Dict with dataset metadata
    """
    dataset_names = [
        "sales_data",
        "customer_transactions",
        "user_activity",
        "product_inventory",
        "marketing_campaigns",
        "employee_records",
    ]

    default_columns = [
        {"name": "id", "type": "integer", "nullable": False},
        {"name": "date", "type": "datetime", "nullable": False},
        {"name": "amount", "type": "float", "nullable": True},
        {"name": "category", "type": "string", "nullable": True},
        {"name": "region", "type": "string", "nullable": True},
        {"name": "customer_id", "type": "string", "nullable": True},
    ]

    rows = num_rows or random.randint(1000, 100000)

    return {
        "id": dataset_id or random_id("ds_"),
        "name": name or random.choice(dataset_names),
        "num_rows": rows,
        "num_columns": len(columns or default_columns),
        "columns": columns or default_columns,
        "created_at": random_date(start_days_ago=90, end_days_ahead=0).isoformat(),
        "updated_at": random_date(start_days_ago=7, end_days_ahead=0).isoformat(),
        "size_bytes": rows * random.randint(50, 200),
        "format": random.choice(["csv", "parquet", "json"]),
        "description": f"Dataset containing {rows} records",
    }


def generate_random_document(
    doc_id: Optional[str] = None,
    title: Optional[str] = None,
    content: Optional[str] = None,
    doc_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a random document.

    Args:
        doc_id: Optional ID
        title: Optional title
        content: Optional content
        doc_type: Optional document type

    Returns:
        Dict with document data
    """
    titles = [
        "Q4 Financial Report",
        "Product Roadmap 2024",
        "Customer Survey Results",
        "Technical Architecture Document",
        "Marketing Strategy Overview",
        "Employee Handbook",
        "API Documentation",
        "Security Best Practices",
    ]

    contents = [
        "This document outlines the key findings from our quarterly analysis. Revenue growth exceeded expectations at 15%, driven primarily by new customer acquisition in the enterprise segment. Cost optimization efforts resulted in a 5% reduction in operational expenses.",
        "Our product roadmap focuses on three key areas: user experience improvements, platform scalability, and new integration capabilities. We plan to launch the redesigned dashboard in Q2, followed by the API v2.0 release in Q3.",
        "Survey responses indicate high satisfaction (4.2/5) with our core product features. Areas for improvement include mobile experience and customer support response times. Key recommendations are outlined in section 3.",
        "The system architecture follows a microservices pattern with event-driven communication. Key components include the API Gateway, Authentication Service, and Data Processing Pipeline. See diagrams in appendix A.",
    ]

    doc_types = ["report", "documentation", "policy", "analysis", "guide"]

    return {
        "id": doc_id or random_id("doc_"),
        "title": title or random.choice(titles),
        "content": content or random.choice(contents),
        "type": doc_type or random.choice(doc_types),
        "author": random_name(),
        "created_at": random_date(start_days_ago=180, end_days_ahead=0).isoformat(),
        "updated_at": random_date(start_days_ago=30, end_days_ahead=0).isoformat(),
        "tags": random.sample(
            ["internal", "confidential", "public", "draft", "final"],
            k=random.randint(1, 3),
        ),
        "word_count": random.randint(500, 5000),
        "version": f"{random.randint(1, 5)}.{random.randint(0, 9)}",
    }


def generate_slack_message(
    message_id: Optional[str] = None,
    channel: Optional[str] = None,
    sender: Optional[str] = None,
    content: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a random Slack message."""
    channels = [
        "#general",
        "#engineering",
        "#sales",
        "#support",
        "#random",
        "#announcements",
    ]

    messages = [
        "Hey team, quick update on the project status",
        "Anyone available for a quick sync?",
        "Just pushed the latest changes, please review",
        "Meeting notes from today's standup attached",
        "FYI - the deployment is scheduled for 5pm",
        "Great work on the release everyone!",
    ]

    sender_name = sender or random_name()

    return {
        "id": message_id or random_id("msg_"),
        "channel": channel or random.choice(channels),
        "sender": sender_name,
        "content": content or random.choice(messages),
        "timestamp": random_date(start_days_ago=7, end_days_ahead=0).isoformat(),
        "reactions": random.sample(
            ["thumbsup", "heart", "eyes", "rocket", "tada"], k=random.randint(0, 3)
        ),
        "thread_count": random.randint(0, 10),
    }


def generate_contact(
    contact_id: Optional[str] = None,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a random contact."""
    contact_name = name or random_name()
    departments = [
        "Engineering",
        "Sales",
        "Marketing",
        "Support",
        "Product",
        "HR",
        "Finance",
    ]

    return {
        "id": contact_id or random_id("contact_"),
        "name": contact_name,
        "email": random_email_address(contact_name),
        "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
        "department": random.choice(departments),
        "title": random.choice(
            ["Manager", "Director", "Engineer", "Analyst", "Specialist", "Lead"]
        ),
        "location": random.choice(
            ["San Francisco", "New York", "London", "Remote", "Austin"]
        ),
        "timezone": random.choice(["PST", "EST", "GMT", "CET"]),
    }
