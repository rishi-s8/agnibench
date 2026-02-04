"""
Tasks for the data analysis benchmark suite.

Contains 16 tasks distributed across difficulty levels and information flows.
"""

from typing import List
from agnibench.core.abstractions import (
    Task,
    TaskCharacteristics,
    DifficultyLevel,
    InformationFlow,
)


def get_data_analysis_tasks() -> List[Task]:
    """Get all data analysis tasks."""
    tasks = []

    # ============================================================================
    # SIMPLE TASKS (3 tasks, 2-3 tool calls)
    # ============================================================================

    tasks.append(Task(
        id="data_simple_01",
        name="List Available Datasets",
        prompt="What datasets are available for analysis?",
        difficulty=DifficultyLevel.SIMPLE,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["list_datasets"],
        expected_answer=["Sales", "Customer", "Product"],
        verifier_config={
            "answer": ["Sales", "Customer", "Product", "datasets"],
            "match_mode": "contains",
            "tools": {
                "required": ["list_datasets"],
                "min_calls": 1,
                "max_calls": 2
            }
        },
        description="Simple dataset listing",
        min_tool_calls=1,
        max_tool_calls=2,
        tags=["list", "datasets"],
    ))

    tasks.append(Task(
        id="data_simple_02",
        name="Describe Sales Dataset",
        prompt="Describe the sales dataset - what columns does it have?",
        difficulty=DifficultyLevel.SIMPLE,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["describe_dataset"],
        expected_answer=["amount", "region", "category"],
        verifier_config={
            "answer": ["amount", "region", "category", "transaction", "quantity"],
            "match_mode": "contains",
            "tools": {
                "required": ["describe_dataset"],
                "min_calls": 1,
                "max_calls": 2
            }
        },
        description="Dataset schema exploration",
        min_tool_calls=1,
        max_tool_calls=2,
        tags=["describe", "schema"],
    ))

    tasks.append(Task(
        id="data_simple_03",
        name="Basic Statistics Query",
        prompt="What is the average sale amount in the sales dataset?",
        difficulty=DifficultyLevel.SIMPLE,
        information_flow=InformationFlow.PROMPT_FULL,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["compute_statistics"],
        expected_answer=["352", "mean", "average"],
        verifier_config={
            "answer": ["352", "mean", "average"],
            "match_mode": "contains",
            "tools": {
                "required": ["compute_statistics"],
                "optional": ["describe_dataset", "list_datasets"],
                "min_calls": 1,
                "max_calls": 3
            }
        },
        description="Basic statistics computation",
        min_tool_calls=1,
        max_tool_calls=3,
        tags=["statistics", "mean"],
    ))

    # ============================================================================
    # MEDIUM TASKS (5 tasks, 4-6 tool calls)
    # ============================================================================

    tasks.append(Task(
        id="data_medium_01",
        name="Regional Sales Analysis",
        prompt="Analyze sales performance by region. Which region has the highest average sale amount?",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["describe_dataset", "compute_statistics", "query_data"],
        expected_answer=["East", "412", "region"],
        verifier_config={
            "answer": ["East", "412", "region", "highest"],
            "match_mode": "contains",
            "tools": {
                "required": ["compute_statistics"],
                "optional": ["describe_dataset", "query_data", "list_datasets"],
                "min_calls": 1,
                "max_calls": 5
            }
        },
        description="Grouped analysis by region",
        min_tool_calls=1,
        max_tool_calls=5,
        tags=["group_by", "region", "comparison"],
    ))

    tasks.append(Task(
        id="data_medium_02",
        name="Category Performance Visualization",
        prompt="Create a bar chart showing average sales amount by product category.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["describe_dataset", "compute_statistics", "create_visualization"],
        expected_answer=["bar", "chart", "created", "category"],
        verifier_config={
            "answer": ["bar", "visualization", "category", "created"],
            "match_mode": "contains",
            "tools": {
                "required": ["create_visualization"],
                "optional": ["describe_dataset", "compute_statistics", "query_data"],
                "min_calls": 1,
                "max_calls": 5
            },
            "state": {
                "visualizations": {"$length": {"$gte": 1}}
            }
        },
        description="Visualization creation",
        min_tool_calls=1,
        max_tool_calls=5,
        tags=["visualization", "bar_chart"],
    ))

    tasks.append(Task(
        id="data_medium_03",
        name="Customer Churn Analysis",
        prompt="What is the average churn risk by region? Which region has the highest churn risk?",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["list_datasets", "describe_dataset", "compute_statistics"],
        expected_answer=["West", "0.35", "churn"],
        verifier_config={
            "answer": ["West", "0.35", "churn", "risk"],
            "match_mode": "contains",
            "tools": {
                "required": ["compute_statistics"],
                "optional": ["list_datasets", "describe_dataset", "query_data"],
                "min_calls": 1,
                "max_calls": 5
            }
        },
        description="Customer churn analysis",
        min_tool_calls=1,
        max_tool_calls=5,
        tags=["churn", "customer", "risk"],
    ))

    tasks.append(Task(
        id="data_medium_04",
        name="Correlation Discovery",
        prompt="Find correlations in the customer dataset. What factors are most strongly correlated with lifetime value?",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_cross_reference=True,
        ),
        expected_tool_calls=["describe_dataset", "correlate_columns"],
        expected_answer=["purchase_count", "0.85", "correlation"],
        verifier_config={
            "answer": ["purchase_count", "0.85", "correlation", "strong"],
            "match_mode": "contains",
            "tools": {
                "required": ["correlate_columns"],
                "optional": ["describe_dataset", "list_datasets"],
                "min_calls": 1,
                "max_calls": 5
            }
        },
        description="Correlation analysis",
        min_tool_calls=1,
        max_tool_calls=5,
        tags=["correlation", "lifetime_value"],
    ))

    tasks.append(Task(
        id="data_medium_05",
        name="Anomaly Detection",
        prompt="Check the sales dataset for anomalies in the amount column. How many outliers are there?",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["describe_dataset", "detect_anomalies"],
        expected_answer=["3", "anomal", "outlier"],
        verifier_config={
            "answer": ["3", "anomal", "outlier", "zscore"],
            "match_mode": "contains",
            "tools": {
                "required": ["detect_anomalies"],
                "optional": ["describe_dataset", "list_datasets", "compute_statistics"],
                "min_calls": 1,
                "max_calls": 5
            }
        },
        description="Anomaly detection in sales",
        min_tool_calls=1,
        max_tool_calls=5,
        tags=["anomaly", "outlier", "detection"],
    ))

    # ============================================================================
    # HARD TASKS (5 tasks, 7-10 tool calls)
    # ============================================================================

    tasks.append(Task(
        id="data_hard_01",
        name="Multi-Dataset Analysis",
        prompt="Compare the Electronics category performance across both the sales and products datasets. What's the average sale amount for Electronics and how does the price-to-cost ratio look for Electronics products?",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["list_datasets", "describe_dataset", "describe_dataset", "compute_statistics", "query_data", "compute_statistics"],
        expected_answer=["Electronics", "549", "price", "cost"],
        verifier_config={
            "answer": ["Electronics", "549", "price", "cost"],
            "match_mode": "contains",
            "tools": {
                "required": ["describe_dataset", "compute_statistics"],
                "optional": ["list_datasets", "query_data"],
                "min_calls": 3,
                "max_calls": 10
            }
        },
        description="Cross-dataset analysis",
        min_tool_calls=3,
        max_tool_calls=10,
        tags=["multi-dataset", "comparison", "cross-reference"],
    ))

    tasks.append(Task(
        id="data_hard_02",
        name="Customer Segmentation Analysis",
        prompt="Analyze the customer dataset to understand customer segments. Look at the distribution of lifetime value, identify correlations with other metrics, find any anomalies, and save your key insights.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_long_reasoning_chain=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["describe_dataset", "compute_statistics", "correlate_columns", "detect_anomalies", "save_insight"],
        expected_answer=["lifetime_value", "purchase_count", "correlation", "insight"],
        verifier_config={
            "answer": ["lifetime_value", "correlation", "customer"],
            "match_mode": "contains",
            "tools": {
                "required": ["compute_statistics", "correlate_columns", "save_insight"],
                "optional": ["describe_dataset", "detect_anomalies", "create_visualization"],
                "min_calls": 4,
                "max_calls": 10
            },
            "state": {
                "insights": {"$length": {"$gte": 1}}
            }
        },
        description="Comprehensive customer analysis",
        min_tool_calls=4,
        max_tool_calls=10,
        tags=["segmentation", "customer", "comprehensive"],
    ))

    tasks.append(Task(
        id="data_hard_03",
        name="Sales Trend Investigation",
        prompt="Investigate sales patterns: What are the top categories by revenue? Are there regional differences? Create visualizations to show the patterns and document your findings.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,  # FIXED: Questions explicitly state what to analyze
            control_flow_from_tools=False,
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["describe_dataset", "compute_statistics", "compute_statistics", "query_data", "create_visualization", "save_insight"],
        expected_answer=["Electronics", "category", "region", "visualization"],
        verifier_config={
            "answer": ["Electronics", "category", "region", "visual"],
            "match_mode": "contains",
            "tools": {
                "required": ["compute_statistics", "create_visualization"],
                "optional": ["describe_dataset", "query_data", "save_insight"],
                "min_calls": 3,
                "max_calls": 10
            },
            "state": {
                "visualizations": {"$length": {"$gte": 1}}
            }
        },
        description="Sales pattern investigation",
        min_tool_calls=3,
        max_tool_calls=10,
        tags=["sales", "trends", "investigation"],
    ))

    tasks.append(Task(
        id="data_hard_04",
        name="Product Inventory Analysis",
        prompt="Analyze the product catalog. Find products with low stock (stock < 50), check their prices and ratings. Are there any high-value products at risk of stockout? Create a visualization and save your findings.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["describe_dataset", "query_data", "compute_statistics", "detect_anomalies", "create_visualization", "save_insight"],
        expected_answer=["stock", "low", "price", "risk"],
        verifier_config={
            "answer": ["stock", "low", "product", "price"],
            "match_mode": "contains",
            "tools": {
                "required": ["query_data", "save_insight"],
                "optional": ["describe_dataset", "compute_statistics", "detect_anomalies", "create_visualization"],
                "min_calls": 3,
                "max_calls": 10
            },
            "state": {
                "insights": {"$length": {"$gte": 1}}
            }
        },
        description="Inventory risk analysis",
        min_tool_calls=3,
        max_tool_calls=10,
        tags=["inventory", "risk", "product"],
    ))

    tasks.append(Task(
        id="data_hard_05",
        name="Churn Prediction Factors",
        prompt="Investigate factors that influence customer churn. Analyze correlations, compare statistics across regions, and identify which customer segments have the highest churn risk. Document all findings.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,  # FIXED: Analysis steps are explicitly stated in prompt
            control_flow_from_tools=False,
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["describe_dataset", "correlate_columns", "compute_statistics", "query_data", "save_insight"],
        expected_answer=["churn", "correlation", "lifetime_value", "region"],
        verifier_config={
            "answer": ["churn", "correlation", "lifetime", "West"],
            "match_mode": "contains",
            "tools": {
                "required": ["correlate_columns", "compute_statistics", "save_insight"],
                "optional": ["describe_dataset", "query_data", "create_visualization"],
                "min_calls": 3,
                "max_calls": 10
            },
            "state": {
                "insights": {"$length": {"$gte": 1}}
            }
        },
        description="Churn prediction factor analysis",
        min_tool_calls=3,
        max_tool_calls=10,
        tags=["churn", "prediction", "factors"],
    ))

    # ============================================================================
    # EXPERT TASKS (3 tasks, 11+ tool calls)
    # ============================================================================

    tasks.append(Task(
        id="data_expert_01",
        name="Comprehensive Business Analysis",
        prompt="""Conduct a comprehensive analysis of the business performance:
        1. Explore all available datasets
        2. Analyze sales by category and region
        3. Examine customer behavior and churn risk
        4. Check product inventory status
        5. Find correlations across metrics
        6. Identify anomalies that need attention
        7. Create at least 2 visualizations
        8. Document at least 3 key insights

        Provide a summary of the overall business health.""",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_long_reasoning_chain=True,
            requires_state_tracking=True,
            requires_multi_constraint=True,
        ),
        expected_tool_calls=["list_datasets"] + ["describe_dataset"] * 3 + ["compute_statistics"] * 4 + ["correlate_columns", "detect_anomalies"] + ["create_visualization"] * 2 + ["save_insight"] * 3,
        expected_answer=["sales", "customer", "product", "insight"],
        verifier_config={
            "answer": ["sales", "customer", "product", "analysis"],
            "match_mode": "contains",
            "tools": {
                "required": ["list_datasets", "compute_statistics", "create_visualization", "save_insight"],
                "optional": ["describe_dataset", "query_data", "correlate_columns", "detect_anomalies"],
                "min_calls": 8,
                "max_calls": 20
            },
            "state": {
                "visualizations": {"$length": {"$gte": 2}},
                "insights": {"$length": {"$gte": 3}}
            }
        },
        description="Full business analysis report",
        min_tool_calls=8,
        max_tool_calls=20,
        tags=["comprehensive", "business", "report"],
    ))

    tasks.append(Task(
        id="data_expert_02",
        name="Revenue Optimization Analysis",
        prompt="""Perform a revenue optimization analysis:
        1. Identify highest-revenue categories and regions
        2. Analyze price-to-performance relationships in products
        3. Find underperforming segments
        4. Correlate customer value with purchase patterns
        5. Detect pricing anomalies
        6. Identify high-value customers at risk of churn
        7. Create visualizations for key findings
        8. Document actionable recommendations

        The goal is to find opportunities to increase revenue.""",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,  # FIXED: Explicit numbered steps - this is a recipe
            control_flow_from_tools=False,
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_long_reasoning_chain=True,
            requires_state_tracking=True,
            requires_plan_adaptation=True,
        ),
        expected_tool_calls=["list_datasets"] + ["describe_dataset"] * 2 + ["compute_statistics"] * 5 + ["query_data"] * 2 + ["correlate_columns", "detect_anomalies"] + ["create_visualization"] * 2 + ["save_insight"] * 3,
        expected_answer=["revenue", "optimization", "recommendation", "opportunity"],
        verifier_config={
            "answer": ["revenue", "customer", "value", "optimization"],
            "match_mode": "contains",
            "tools": {
                "required": ["compute_statistics", "correlate_columns", "save_insight"],
                "optional": ["list_datasets", "describe_dataset", "query_data", "detect_anomalies", "create_visualization"],
                "min_calls": 8,
                "max_calls": 25
            },
            "state": {
                "insights": {"$length": {"$gte": 2}}
            }
        },
        description="Revenue optimization deep dive",
        min_tool_calls=8,
        max_tool_calls=25,
        tags=["revenue", "optimization", "strategy"],
    ))

    tasks.append(Task(
        id="data_expert_03",
        name="Hypothesis Testing Investigation",
        prompt="""Investigate the following hypotheses using the available data:

        H1: Electronics has the highest profit margin
        H2: Customer lifetime value is primarily driven by purchase frequency
        H3: The North region outperforms others in sales
        H4: High-priced products have better ratings

        For each hypothesis:
        - Query the relevant data
        - Compute supporting statistics
        - Check for anomalies that might skew results
        - Document whether the hypothesis is supported or refuted

        Create visualizations for at least 2 hypotheses and save all findings.""",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_long_reasoning_chain=True,
            requires_state_tracking=True,
            requires_multi_constraint=True,
        ),
        expected_tool_calls=["describe_dataset"] * 3 + ["query_data"] * 4 + ["compute_statistics"] * 4 + ["correlate_columns"] * 2 + ["create_visualization"] * 2 + ["save_insight"] * 4,
        expected_answer=["hypothesis", "supported", "refuted", "evidence"],
        verifier_config={
            "answer": ["hypothesis", "Electronics", "North", "correlation"],
            "match_mode": "contains",
            "tools": {
                "required": ["compute_statistics", "correlate_columns", "save_insight"],
                "optional": ["describe_dataset", "query_data", "detect_anomalies", "create_visualization"],
                "min_calls": 10,
                "max_calls": 25
            },
            "state": {
                "insights": {"$length": {"$gte": 4}},
                "visualizations": {"$length": {"$gte": 2}}
            }
        },
        description="Multi-hypothesis testing",
        min_tool_calls=10,
        max_tool_calls=25,
        tags=["hypothesis", "testing", "investigation"],
    ))

    # ============================================================================
    # TRUE TOOL-DRIVEN CONTROL FLOW TASKS
    # These tasks require discovering what to do from tool responses
    # ============================================================================

    tasks.append(Task(
        id="data_discovery_01",
        name="Find Data Quality Issues",
        prompt="Scan the available datasets for any data quality issues (anomalies, missing patterns, outliers). Report what you find and suggest fixes.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Must discover WHAT datasets exist, WHAT issues are present
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["list_datasets"],  # Dataset contents determine analysis path
        expected_answer=["quality", "issue", "found"],
        verifier_config={
            "answer": ["data", "quality", "anomal"],
            "match_mode": "contains",
            "tools": {
                "required": ["list_datasets"],
                "optional": ["describe_dataset", "compute_statistics", "detect_anomalies", "query_data", "save_insight"],
                "min_calls": 2,
                "max_calls": 12
            }
        },
        description="TRUE tool-driven: discovered issues determine reporting",
        min_tool_calls=2,
        max_tool_calls=12,
        tags=["discovery", "quality", "anomaly"],
    ))

    tasks.append(Task(
        id="data_discovery_02",
        name="Investigate Metric Drop",
        prompt="Something in our business metrics has declined. Investigate the data to find what dropped and why.",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Must discover WHICH metric dropped before investigating WHY
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_long_reasoning_chain=True,
            requires_cross_reference=True,
        ),
        expected_tool_calls=["list_datasets", "compute_statistics"],  # Initial stats reveal the problem area
        expected_answer=["found", "decline", "reason"],
        verifier_config={
            "answer": ["metric", "decline", "analysis"],
            "match_mode": "contains",
            "tools": {
                "required": ["compute_statistics"],
                "optional": ["list_datasets", "describe_dataset", "query_data", "correlate_columns", "detect_anomalies", "save_insight", "create_visualization"],
                "min_calls": 3,
                "max_calls": 15
            },
            "state": {
                "insights": {"$length": {"$gte": 1}}
            }
        },
        description="TRUE tool-driven: discovered decline determines investigation path",
        min_tool_calls=3,
        max_tool_calls=15,
        tags=["discovery", "investigation", "root-cause"],
    ))

    tasks.append(Task(
        id="data_discovery_03",
        name="Find Actionable Insights",
        prompt="Explore the available data and find any actionable business insights. Focus on patterns that could inform decisions.",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Open-ended exploration - discoveries drive next steps
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_cross_reference=True,
            requires_state_tracking=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["list_datasets"],  # Pure exploration
        expected_answer=["insight", "actionable", "pattern"],
        verifier_config={
            "answer": ["insight", "pattern", "data"],
            "match_mode": "contains",
            "tools": {
                "required": ["list_datasets", "save_insight"],
                "optional": ["describe_dataset", "compute_statistics", "query_data", "correlate_columns", "detect_anomalies", "create_visualization"],
                "min_calls": 4,
                "max_calls": 20
            },
            "state": {
                "insights": {"$length": {"$gte": 2}}
            }
        },
        description="TRUE tool-driven: open exploration where discoveries drive analysis",
        min_tool_calls=4,
        max_tool_calls=20,
        tags=["discovery", "exploration", "insights"],
    ))

    tasks.append(Task(
        id="data_discovery_04",
        name="Answer Business Question",
        prompt="The CEO asks: 'What should we focus on next quarter?' Use the available data to provide a data-driven recommendation.",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Must discover what data exists and what it reveals before recommending
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_cross_reference=True,
            requires_long_reasoning_chain=True,
            requires_multi_constraint=True,
        ),
        expected_tool_calls=["list_datasets"],  # Data landscape determines analysis
        expected_answer=["recommendation", "focus", "quarter"],
        verifier_config={
            "answer": ["recommend", "focus", "data"],
            "match_mode": "contains",
            "tools": {
                "required": ["list_datasets", "compute_statistics", "save_insight"],
                "optional": ["describe_dataset", "query_data", "correlate_columns", "detect_anomalies", "create_visualization"],
                "min_calls": 5,
                "max_calls": 20
            },
            "state": {
                "insights": {"$length": {"$gte": 1}}
            }
        },
        description="TRUE tool-driven: vague question requires data exploration to answer",
        min_tool_calls=5,
        max_tool_calls=20,
        tags=["discovery", "strategic", "recommendation"],
    ))

    tasks.append(Task(
        id="data_discovery_05",
        name="Anomaly Alert Investigation",
        prompt="An automated alert flagged something unusual in our data. Find what triggered the alert and assess if it needs immediate attention.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Must discover WHAT anomaly before assessing impact
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_plan_adaptation=True,
        ),
        expected_tool_calls=["list_datasets", "detect_anomalies"],  # Anomaly type determines response
        expected_answer=["anomaly", "found", "assessment"],
        verifier_config={
            "answer": ["anomaly", "alert", "found"],
            "match_mode": "contains",
            "tools": {
                "required": ["detect_anomalies"],
                "optional": ["list_datasets", "describe_dataset", "compute_statistics", "query_data", "save_insight"],
                "min_calls": 2,
                "max_calls": 10
            }
        },
        description="TRUE tool-driven: anomaly type determines investigation depth",
        min_tool_calls=2,
        max_tool_calls=10,
        tags=["discovery", "alert", "anomaly"],
    ))

    tasks.append(Task(
        id="data_discovery_06",
        name="Competitive Analysis Setup",
        prompt="We need to understand our market position. Analyze whatever relevant data we have and identify our strengths and weaknesses.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Must discover what data is available before analysis
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_cross_reference=True,
        ),
        expected_tool_calls=["list_datasets"],  # Available data determines analysis scope
        expected_answer=["strength", "weakness", "analysis"],
        verifier_config={
            "answer": ["strength", "weakness", "market", "analysis"],
            "match_mode": "contains",
            "tools": {
                "required": ["list_datasets", "compute_statistics"],
                "optional": ["describe_dataset", "query_data", "correlate_columns", "create_visualization", "save_insight"],
                "min_calls": 3,
                "max_calls": 12
            },
            "state": {
                "insights": {"$length": {"$gte": 1}}
            }
        },
        description="TRUE tool-driven: available data determines analysis scope",
        min_tool_calls=3,
        max_tool_calls=12,
        tags=["discovery", "competitive", "swot"],
    ))

    return tasks
