"""
Customer Service Benchmark Suite

Tests issue resolution with incomplete information and adaptive questioning.
Selected for testing inference and handling ambiguity.
"""

from agnibench.core.abstractions import BenchmarkSuite
from agnibench.suites.customer_service.tools import get_customer_service_tools
from agnibench.suites.customer_service.environment import CustomerServiceEnvironment
from agnibench.suites.customer_service.tasks import get_customer_service_tasks


def CustomerServiceSuite() -> BenchmarkSuite:
    """Create the customer service benchmark suite."""
    return BenchmarkSuite(
        name="customer_service",
        description="Issue resolution testing inference and adaptive questioning",
        tasks=get_customer_service_tasks(),
        tools=get_customer_service_tools(),
        environment_class=CustomerServiceEnvironment,
        version="1.0.0",
        tags=["customer_service", "troubleshooting", "support", "diagnosis"],
    )


__all__ = ["CustomerServiceSuite", "CustomerServiceEnvironment", "get_customer_service_tools", "get_customer_service_tasks"]
