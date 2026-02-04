"""
Simulated environment for the data analysis benchmark suite.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List
from agnibench.core.environment import SimulatedEnvironment
from agnibench.suites.data_analysis.tools import set_data_state, get_data_state


class DataAnalysisEnvironment(SimulatedEnvironment):
    """
    Environment for data analysis tasks.

    Manages datasets, query results, and insights.
    """

    def _setup_default_state(self) -> None:
        """Set up default state with sample datasets."""
        now = datetime.now()

        # Sample datasets
        datasets = [
            {
                "id": "ds_sales",
                "name": "Sales Transactions",
                "category": "sales",
                "description": "Monthly sales transactions for 2023",
                "num_rows": 15000,
                "num_columns": 8,
                "created_at": (now - timedelta(days=30)).isoformat(),
                "updated_at": (now - timedelta(days=1)).isoformat(),
                "columns": [
                    {"name": "transaction_id", "type": "string", "nullable": False},
                    {"name": "date", "type": "date", "nullable": False},
                    {"name": "product_id", "type": "string", "nullable": False},
                    {"name": "category", "type": "string", "nullable": False},
                    {"name": "region", "type": "string", "nullable": False},
                    {"name": "amount", "type": "float", "nullable": False},
                    {"name": "quantity", "type": "integer", "nullable": False},
                    {"name": "customer_id", "type": "string", "nullable": True},
                ],
                "sample_data": [
                    {"transaction_id": "T001", "date": "2023-01-15", "product_id": "P100", "category": "Electronics", "region": "North", "amount": 299.99, "quantity": 1, "customer_id": "C001"},
                    {"transaction_id": "T002", "date": "2023-01-15", "product_id": "P200", "category": "Clothing", "region": "South", "amount": 59.99, "quantity": 2, "customer_id": "C002"},
                    {"transaction_id": "T003", "date": "2023-01-16", "product_id": "P150", "category": "Electronics", "region": "East", "amount": 799.99, "quantity": 1, "customer_id": "C003"},
                    {"transaction_id": "T004", "date": "2023-01-16", "product_id": "P300", "category": "Home", "region": "West", "amount": 149.99, "quantity": 3, "customer_id": "C001"},
                    {"transaction_id": "T005", "date": "2023-01-17", "product_id": "P100", "category": "Electronics", "region": "North", "amount": 299.99, "quantity": 2, "customer_id": "C004"},
                ],
                "data": [
                    {"transaction_id": "T001", "date": "2023-01-15", "product_id": "P100", "category": "Electronics", "region": "North", "amount": 299.99, "quantity": 1, "customer_id": "C001"},
                    {"transaction_id": "T002", "date": "2023-01-15", "product_id": "P200", "category": "Clothing", "region": "South", "amount": 59.99, "quantity": 2, "customer_id": "C002"},
                    {"transaction_id": "T003", "date": "2023-01-16", "product_id": "P150", "category": "Electronics", "region": "East", "amount": 799.99, "quantity": 1, "customer_id": "C003"},
                    {"transaction_id": "T004", "date": "2023-01-16", "product_id": "P300", "category": "Home", "region": "West", "amount": 149.99, "quantity": 3, "customer_id": "C001"},
                    {"transaction_id": "T005", "date": "2023-01-17", "product_id": "P100", "category": "Electronics", "region": "North", "amount": 299.99, "quantity": 2, "customer_id": "C004"},
                    {"transaction_id": "T006", "date": "2023-01-17", "product_id": "P400", "category": "Food", "region": "South", "amount": 24.99, "quantity": 5, "customer_id": "C005"},
                    {"transaction_id": "T007", "date": "2023-01-18", "product_id": "P200", "category": "Clothing", "region": "North", "amount": 89.99, "quantity": 1, "customer_id": "C006"},
                    {"transaction_id": "T008", "date": "2023-01-18", "product_id": "P500", "category": "Electronics", "region": "West", "amount": 1299.99, "quantity": 1, "customer_id": "C007"},
                    {"transaction_id": "T009", "date": "2023-01-19", "product_id": "P300", "category": "Home", "region": "East", "amount": 199.99, "quantity": 2, "customer_id": "C008"},
                    {"transaction_id": "T010", "date": "2023-01-19", "product_id": "P100", "category": "Electronics", "region": "South", "amount": 299.99, "quantity": 1, "customer_id": "C009"},
                ],
                "column_statistics": {
                    "amount": {
                        "mean": 352.49,
                        "median": 274.99,
                        "std": 312.15,
                        "min": 24.99,
                        "max": 1299.99,
                        "count": 15000,
                        "percentiles": {"25": 89.99, "50": 274.99, "75": 449.99},
                    },
                    "quantity": {
                        "mean": 1.8,
                        "median": 1,
                        "std": 1.2,
                        "min": 1,
                        "max": 10,
                        "count": 15000,
                    },
                },
                "grouped_statistics": {
                    "amount_by_region": {
                        "North": {"mean": 389.99, "count": 4200},
                        "South": {"mean": 298.99, "count": 3800},
                        "East": {"mean": 412.50, "count": 3500},
                        "West": {"mean": 324.99, "count": 3500},
                    },
                    "amount_by_category": {
                        "Electronics": {"mean": 549.99, "count": 5500},
                        "Clothing": {"mean": 74.99, "count": 3200},
                        "Home": {"mean": 174.99, "count": 3000},
                        "Food": {"mean": 34.99, "count": 3300},
                    },
                },
                "correlations": {
                    "amount": {"quantity": 0.65, "amount": 1.0},
                    "quantity": {"amount": 0.65, "quantity": 1.0},
                },
                "anomalies": {
                    "amount": [
                        {"row": 1523, "value": 4999.99, "zscore": 4.2},
                        {"row": 8721, "value": 5299.99, "zscore": 4.5},
                        {"row": 12045, "value": 4599.99, "zscore": 3.9},
                    ],
                },
            },
            {
                "id": "ds_customers",
                "name": "Customer Profiles",
                "category": "customers",
                "description": "Customer demographic and behavioral data",
                "num_rows": 5000,
                "num_columns": 10,
                "created_at": (now - timedelta(days=60)).isoformat(),
                "updated_at": (now - timedelta(days=7)).isoformat(),
                "columns": [
                    {"name": "customer_id", "type": "string", "nullable": False},
                    {"name": "name", "type": "string", "nullable": False},
                    {"name": "email", "type": "string", "nullable": False},
                    {"name": "age", "type": "integer", "nullable": True},
                    {"name": "gender", "type": "string", "nullable": True},
                    {"name": "region", "type": "string", "nullable": False},
                    {"name": "signup_date", "type": "date", "nullable": False},
                    {"name": "lifetime_value", "type": "float", "nullable": False},
                    {"name": "purchase_count", "type": "integer", "nullable": False},
                    {"name": "churn_risk", "type": "float", "nullable": True},
                ],
                "sample_data": [
                    {"customer_id": "C001", "name": "John Doe", "email": "john@example.com", "age": 35, "gender": "M", "region": "North", "signup_date": "2022-03-15", "lifetime_value": 1250.50, "purchase_count": 12, "churn_risk": 0.15},
                    {"customer_id": "C002", "name": "Jane Smith", "email": "jane@example.com", "age": 28, "gender": "F", "region": "South", "signup_date": "2022-06-20", "lifetime_value": 890.25, "purchase_count": 8, "churn_risk": 0.25},
                ],
                "data": [
                    {"customer_id": "C001", "name": "John Doe", "age": 35, "gender": "M", "region": "North", "lifetime_value": 1250.50, "purchase_count": 12, "churn_risk": 0.15},
                    {"customer_id": "C002", "name": "Jane Smith", "age": 28, "gender": "F", "region": "South", "lifetime_value": 890.25, "purchase_count": 8, "churn_risk": 0.25},
                    {"customer_id": "C003", "name": "Bob Wilson", "age": 45, "gender": "M", "region": "East", "lifetime_value": 2100.00, "purchase_count": 25, "churn_risk": 0.05},
                    {"customer_id": "C004", "name": "Alice Brown", "age": 32, "gender": "F", "region": "West", "lifetime_value": 650.75, "purchase_count": 5, "churn_risk": 0.45},
                    {"customer_id": "C005", "name": "Charlie Davis", "age": 55, "gender": "M", "region": "North", "lifetime_value": 3200.00, "purchase_count": 35, "churn_risk": 0.02},
                ],
                "column_statistics": {
                    "age": {
                        "mean": 38.5,
                        "median": 36,
                        "std": 12.3,
                        "min": 18,
                        "max": 75,
                        "count": 4850,
                    },
                    "lifetime_value": {
                        "mean": 1450.25,
                        "median": 980.50,
                        "std": 1250.75,
                        "min": 15.00,
                        "max": 12500.00,
                        "count": 5000,
                    },
                    "purchase_count": {
                        "mean": 8.5,
                        "median": 6,
                        "std": 7.2,
                        "min": 1,
                        "max": 85,
                        "count": 5000,
                    },
                    "churn_risk": {
                        "mean": 0.28,
                        "median": 0.22,
                        "std": 0.18,
                        "min": 0.01,
                        "max": 0.95,
                        "count": 5000,
                    },
                },
                "grouped_statistics": {
                    "lifetime_value_by_region": {
                        "North": {"mean": 1650.00, "count": 1400},
                        "South": {"mean": 1250.00, "count": 1300},
                        "East": {"mean": 1550.00, "count": 1200},
                        "West": {"mean": 1350.00, "count": 1100},
                    },
                    "churn_risk_by_region": {
                        "North": {"mean": 0.22, "count": 1400},
                        "South": {"mean": 0.32, "count": 1300},
                        "East": {"mean": 0.25, "count": 1200},
                        "West": {"mean": 0.35, "count": 1100},
                    },
                },
                "correlations": {
                    "age": {"lifetime_value": 0.42, "purchase_count": 0.55, "churn_risk": -0.38},
                    "lifetime_value": {"age": 0.42, "purchase_count": 0.85, "churn_risk": -0.72},
                    "purchase_count": {"age": 0.55, "lifetime_value": 0.85, "churn_risk": -0.68},
                    "churn_risk": {"age": -0.38, "lifetime_value": -0.72, "purchase_count": -0.68},
                },
                "anomalies": {
                    "lifetime_value": [
                        {"row": 234, "value": 12500.00, "zscore": 4.8},
                        {"row": 1892, "value": 11200.00, "zscore": 4.2},
                    ],
                    "churn_risk": [
                        {"row": 3421, "value": 0.95, "zscore": 3.7},
                    ],
                },
            },
            {
                "id": "ds_products",
                "name": "Product Catalog",
                "category": "products",
                "description": "Product information and performance metrics",
                "num_rows": 500,
                "num_columns": 7,
                "created_at": (now - timedelta(days=90)).isoformat(),
                "updated_at": (now - timedelta(days=3)).isoformat(),
                "columns": [
                    {"name": "product_id", "type": "string", "nullable": False},
                    {"name": "name", "type": "string", "nullable": False},
                    {"name": "category", "type": "string", "nullable": False},
                    {"name": "price", "type": "float", "nullable": False},
                    {"name": "cost", "type": "float", "nullable": False},
                    {"name": "stock", "type": "integer", "nullable": False},
                    {"name": "rating", "type": "float", "nullable": True},
                ],
                "sample_data": [
                    {"product_id": "P100", "name": "Wireless Headphones", "category": "Electronics", "price": 299.99, "cost": 150.00, "stock": 250, "rating": 4.5},
                    {"product_id": "P150", "name": "Smart TV 55in", "category": "Electronics", "price": 799.99, "cost": 450.00, "stock": 45, "rating": 4.7},
                    {"product_id": "P200", "name": "Cotton T-Shirt", "category": "Clothing", "price": 29.99, "cost": 8.00, "stock": 500, "rating": 4.2},
                ],
                "data": [
                    {"product_id": "P100", "name": "Wireless Headphones", "category": "Electronics", "price": 299.99, "cost": 150.00, "stock": 250, "rating": 4.5},
                    {"product_id": "P150", "name": "Smart TV 55in", "category": "Electronics", "price": 799.99, "cost": 450.00, "stock": 45, "rating": 4.7},
                    {"product_id": "P200", "name": "Cotton T-Shirt", "category": "Clothing", "price": 29.99, "cost": 8.00, "stock": 500, "rating": 4.2},
                    {"product_id": "P300", "name": "Kitchen Blender", "category": "Home", "price": 149.99, "cost": 65.00, "stock": 120, "rating": 4.3},
                    {"product_id": "P400", "name": "Organic Snacks", "category": "Food", "price": 24.99, "cost": 12.00, "stock": 800, "rating": 4.0},
                    {"product_id": "P500", "name": "Laptop Pro", "category": "Electronics", "price": 1299.99, "cost": 750.00, "stock": 30, "rating": 4.8},
                ],
                "column_statistics": {
                    "price": {
                        "mean": 189.99,
                        "median": 99.99,
                        "std": 245.50,
                        "min": 9.99,
                        "max": 1999.99,
                        "count": 500,
                    },
                    "rating": {
                        "mean": 4.1,
                        "median": 4.2,
                        "std": 0.6,
                        "min": 1.5,
                        "max": 5.0,
                        "count": 485,
                    },
                    "stock": {
                        "mean": 215,
                        "median": 150,
                        "std": 180,
                        "min": 0,
                        "max": 1000,
                        "count": 500,
                    },
                },
                "grouped_statistics": {
                    "price_by_category": {
                        "Electronics": {"mean": 549.99, "count": 120},
                        "Clothing": {"mean": 49.99, "count": 150},
                        "Home": {"mean": 129.99, "count": 100},
                        "Food": {"mean": 19.99, "count": 130},
                    },
                },
                "correlations": {
                    "price": {"cost": 0.92, "rating": 0.25, "stock": -0.35},
                    "cost": {"price": 0.92, "rating": 0.18, "stock": -0.30},
                    "rating": {"price": 0.25, "cost": 0.18, "stock": 0.05},
                    "stock": {"price": -0.35, "cost": -0.30, "rating": 0.05},
                },
                "anomalies": {
                    "price": [
                        {"row": 89, "value": 1999.99, "zscore": 3.8},
                    ],
                    "stock": [
                        {"row": 45, "value": 0, "zscore": -1.2},
                        {"row": 112, "value": 0, "zscore": -1.2},
                    ],
                },
            },
            # EDGE CASE: Empty dataset
            {
                "id": "ds_empty",
                "name": "Q4 2024 Returns",
                "category": "returns",
                "description": "Return transactions for Q4 2024 - no data yet",
                "num_rows": 0,
                "num_columns": 5,
                "created_at": (now - timedelta(days=1)).isoformat(),
                "updated_at": now.isoformat(),
                "columns": [
                    {"name": "return_id", "type": "string", "nullable": False},
                    {"name": "transaction_id", "type": "string", "nullable": False},
                    {"name": "reason", "type": "string", "nullable": True},
                    {"name": "amount", "type": "float", "nullable": False},
                    {"name": "date", "type": "date", "nullable": False},
                ],
                "sample_data": [],
                "data": [],
                "column_statistics": {},
                "grouped_statistics": {},
                "correlations": {},
                "anomalies": {},
            },
            # EDGE CASE: Dataset with many null values and quality issues
            {
                "id": "ds_incomplete",
                "name": "Survey Responses",
                "category": "feedback",
                "description": "Customer satisfaction survey - partial responses",
                "num_rows": 1200,
                "num_columns": 6,
                "created_at": (now - timedelta(days=45)).isoformat(),
                "updated_at": (now - timedelta(days=30)).isoformat(),
                "columns": [
                    {"name": "response_id", "type": "string", "nullable": False},
                    {"name": "customer_id", "type": "string", "nullable": True},  # 30% null
                    {"name": "satisfaction", "type": "integer", "nullable": True},  # 25% null
                    {"name": "nps_score", "type": "integer", "nullable": True},  # 40% null
                    {"name": "feedback_text", "type": "string", "nullable": True},  # 60% null
                    {"name": "date", "type": "date", "nullable": False},
                ],
                "sample_data": [
                    {"response_id": "R001", "customer_id": "C001", "satisfaction": 4, "nps_score": 8, "feedback_text": "Good service", "date": "2023-09-15"},
                    {"response_id": "R002", "customer_id": None, "satisfaction": 3, "nps_score": None, "feedback_text": None, "date": "2023-09-16"},
                    {"response_id": "R003", "customer_id": "C045", "satisfaction": None, "nps_score": 9, "feedback_text": "Love it!", "date": "2023-09-16"},
                ],
                "data": [
                    {"response_id": "R001", "customer_id": "C001", "satisfaction": 4, "nps_score": 8, "feedback_text": "Good service", "date": "2023-09-15"},
                    {"response_id": "R002", "customer_id": None, "satisfaction": 3, "nps_score": None, "feedback_text": None, "date": "2023-09-16"},
                    {"response_id": "R003", "customer_id": "C045", "satisfaction": None, "nps_score": 9, "feedback_text": "Love it!", "date": "2023-09-16"},
                    {"response_id": "R004", "customer_id": "C102", "satisfaction": 2, "nps_score": 4, "feedback_text": "Needs improvement", "date": "2023-09-17"},
                    {"response_id": "R005", "customer_id": None, "satisfaction": None, "nps_score": None, "feedback_text": None, "date": "2023-09-17"},
                ],
                "column_statistics": {
                    "satisfaction": {
                        "mean": 3.6,
                        "median": 4,
                        "std": 1.1,
                        "min": 1,
                        "max": 5,
                        "count": 900,  # 300 missing
                        "null_count": 300,
                        "null_percentage": 25.0,
                    },
                    "nps_score": {
                        "mean": 7.2,
                        "median": 8,
                        "std": 2.5,
                        "min": 0,
                        "max": 10,
                        "count": 720,
                        "null_count": 480,
                        "null_percentage": 40.0,
                    },
                },
                "data_quality_issues": [
                    {"type": "high_null_rate", "column": "feedback_text", "null_percentage": 60.0},
                    {"type": "high_null_rate", "column": "nps_score", "null_percentage": 40.0},
                    {"type": "missing_customer_link", "column": "customer_id", "null_percentage": 30.0},
                ],
                "grouped_statistics": {},
                "correlations": {
                    "satisfaction": {"nps_score": 0.78},
                    "nps_score": {"satisfaction": 0.78},
                },
                "anomalies": {},
            },
            # EDGE CASE: Deprecated/archived dataset
            {
                "id": "ds_archived",
                "name": "Legacy Sales (2021)",
                "category": "sales",
                "description": "ARCHIVED: Historical data from old system - DO NOT USE for current analysis",
                "num_rows": 8500,
                "num_columns": 6,
                "created_at": (now - timedelta(days=730)).isoformat(),
                "updated_at": (now - timedelta(days=400)).isoformat(),
                "columns": [
                    {"name": "id", "type": "string", "nullable": False},
                    {"name": "date", "type": "date", "nullable": False},
                    {"name": "amount", "type": "float", "nullable": False},
                    {"name": "region", "type": "string", "nullable": False},
                    {"name": "category", "type": "string", "nullable": False},
                    {"name": "deprecated_flag", "type": "boolean", "nullable": False},
                ],
                "status": "archived",
                "deprecation_notice": "This dataset uses old category codes. Use ds_sales for current analysis.",
                "sample_data": [],
                "data": [],
                "column_statistics": {},
                "grouped_statistics": {},
                "correlations": {},
                "anomalies": {},
            },
        ]

        data_state = {
            "datasets": datasets,
            "query_results": [],
            "visualizations": [],
            "insights": [],
        }

        set_data_state(data_state)

        # Store in environment state
        self._state["datasets"] = datasets
        self._state["query_results"] = []
        self._state["visualizations"] = []
        self._state["insights"] = []

    def reset(self) -> None:
        """Reset the environment."""
        super().reset()
        self._setup_default_state()

    def sync_state_from_data(self) -> None:
        """Sync environment state from data state."""
        data_state = get_data_state()
        self._state["query_results"] = data_state.get("query_results", [])
        self._state["visualizations"] = data_state.get("visualizations", [])
        self._state["insights"] = data_state.get("insights", [])

    @property
    def dataset_count(self) -> int:
        """Number of datasets available."""
        return len(self._state.get("datasets", []))

    @property
    def query_count(self) -> int:
        """Number of queries executed."""
        return len(self._state.get("query_results", []))

    @property
    def visualization_count(self) -> int:
        """Number of visualizations created."""
        return len(self._state.get("visualizations", []))

    @property
    def insight_count(self) -> int:
        """Number of insights saved."""
        return len(self._state.get("insights", []))
