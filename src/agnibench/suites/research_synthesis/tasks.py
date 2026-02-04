"""
Tasks for the research synthesis benchmark suite.

Contains 16 tasks distributed across difficulty levels and information flows.
"""

from typing import List
from agnibench.core.abstractions import (
    Task,
    TaskCharacteristics,
    DifficultyLevel,
    InformationFlow,
)


def get_research_tasks() -> List[Task]:
    """Get all research synthesis tasks."""
    tasks = []

    # ============================================================================
    # SIMPLE TASKS (4 tasks, 2-3 tool calls)
    # ============================================================================

    tasks.append(Task(
        id="research_simple_01",
        name="Find Financial Report",
        prompt="Find the Q4 financial performance report and tell me what the revenue growth was.",
        difficulty=DifficultyLevel.SIMPLE,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["search_documents", "read_document"],
        expected_answer="15%",
        verifier_config={
            "answer": ["15%", "15 percent", "$45.2M"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_documents"],
                "optional": ["read_document"],
                "min_calls": 1,
                "max_calls": 3
            }
        },
        description="Simple document search and fact retrieval",
        min_tool_calls=1,
        max_tool_calls=3,
        tags=["search", "financial"],
    ))

    tasks.append(Task(
        id="research_simple_02",
        name="Extract Customer Satisfaction Score",
        prompt="What is the current NPS score according to the customer survey?",
        difficulty=DifficultyLevel.SIMPLE,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["search_documents", "read_document"],
        expected_answer="42",
        verifier_config={
            "answer": ["42", "NPS", "up from 38"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_documents"],
                "optional": ["read_document", "extract_facts"],
                "min_calls": 1,
                "max_calls": 3
            }
        },
        description="Find specific metric in document",
        min_tool_calls=1,
        max_tool_calls=3,
        tags=["search", "customer"],
    ))

    tasks.append(Task(
        id="research_simple_03",
        name="Check Security Certification",
        prompt="What security certifications does the company have?",
        difficulty=DifficultyLevel.SIMPLE,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["search_documents", "read_document"],
        expected_answer=["SOC 2", "ISO 27001"],
        verifier_config={
            "answer": ["SOC 2", "ISO 27001", "GDPR", "HIPAA"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_documents"],
                "optional": ["read_document", "extract_facts"],
                "min_calls": 1,
                "max_calls": 3
            }
        },
        description="Find security information",
        min_tool_calls=1,
        max_tool_calls=3,
        tags=["search", "security"],
    ))

    tasks.append(Task(
        id="research_simple_04",
        name="Find Market Share",
        prompt="What is our current market share and market position?",
        difficulty=DifficultyLevel.SIMPLE,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["search_documents", "read_document"],
        expected_answer=["12%", "#3"],
        verifier_config={
            "answer": ["12%", "#3", "third", "market share"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_documents"],
                "optional": ["read_document", "extract_facts"],
                "min_calls": 1,
                "max_calls": 3
            }
        },
        description="Find market position information",
        min_tool_calls=1,
        max_tool_calls=3,
        tags=["search", "market"],
    ))

    # ============================================================================
    # MEDIUM TASKS (5 tasks, 4-6 tool calls)
    # ============================================================================

    tasks.append(Task(
        id="research_medium_01",
        name="Extract Key Facts from Report",
        prompt="Extract the key financial metrics from the Q4 report and take notes on the most important findings.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["search_documents", "read_document", "extract_facts", "take_notes"],
        expected_answer=["revenue", "margin", "growth"],
        verifier_config={
            "answer": ["$45.2M", "15%", "22%", "operating margin"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_documents", "extract_facts"],
                "optional": ["read_document", "take_notes"],
                "min_calls": 2,
                "max_calls": 6
            }
        },
        description="Extract and record key facts",
        min_tool_calls=2,
        max_tool_calls=6,
        tags=["extract", "notes", "financial"],
    ))

    tasks.append(Task(
        id="research_medium_02",
        name="Research Product Priorities",
        prompt="What are the Q1 product priorities according to the roadmap? List the main features being developed.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["search_documents", "read_document", "extract_facts"],
        expected_answer=["AI Assistant", "dashboard", "mobile app"],
        verifier_config={
            "answer": ["AI Assistant", "dashboard", "mobile app", "performance"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_documents"],
                "optional": ["read_document", "extract_facts"],
                "min_calls": 1,
                "max_calls": 5
            }
        },
        description="Find and list product priorities",
        min_tool_calls=1,
        max_tool_calls=5,
        tags=["product", "roadmap"],
    ))

    tasks.append(Task(
        id="research_medium_03",
        name="Compare Two Documents",
        prompt="Compare the market analysis with the competitive intelligence report. What are the common themes?",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_cross_reference=True,
        ),
        expected_tool_calls=["search_documents", "compare_sources"],
        expected_answer=["AI", "competitive", "market share"],
        verifier_config={
            "answer": ["AI", "competitive", "TechCorp", "market"],
            "match_mode": "contains",
            "tools": {
                "required": ["compare_sources"],
                "optional": ["search_documents", "read_document"],
                "min_calls": 1,
                "max_calls": 5
            }
        },
        description="Compare two related documents",
        min_tool_calls=1,
        max_tool_calls=5,
        tags=["compare", "analysis"],
    ))

    tasks.append(Task(
        id="research_medium_04",
        name="Find Customer Pain Points",
        prompt="Based on the customer survey, what are the top 3 areas that need improvement?",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
        ),
        expected_tool_calls=["search_documents", "read_document", "extract_facts"],
        expected_answer=["mobile", "documentation", "onboarding"],
        verifier_config={
            "answer": ["mobile", "documentation", "onboarding", "3.2", "3.5", "3.6"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_documents"],
                "optional": ["read_document", "extract_facts"],
                "min_calls": 1,
                "max_calls": 5
            }
        },
        description="Identify customer concerns",
        min_tool_calls=1,
        max_tool_calls=5,
        tags=["customer", "improvement"],
    ))

    tasks.append(Task(
        id="research_medium_05",
        name="Research with Web Supplement",
        prompt="Find information about AI trends in our market analysis, and supplement with a web search for the latest AI developments.",
        difficulty=DifficultyLevel.MEDIUM,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_cross_reference=True,
        ),
        expected_tool_calls=["search_documents", "read_document", "search_web"],
        expected_answer=["AI", "78%", "enterprises"],
        verifier_config={
            "answer": ["AI", "78%", "enterprises", "spending"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_documents", "search_web"],
                "optional": ["read_document", "extract_facts"],
                "min_calls": 2,
                "max_calls": 6
            }
        },
        description="Combine internal and external research",
        min_tool_calls=2,
        max_tool_calls=6,
        tags=["search", "web", "AI"],
    ))

    # ============================================================================
    # HARD TASKS (4 tasks, 7-10 tool calls)
    # ============================================================================

    tasks.append(Task(
        id="research_hard_01",
        name="Cross-Reference Multiple Sources",
        prompt="Compare what the financial report says about enterprise performance with what the market analysis says about enterprise trends. Are they consistent? Take notes on your findings.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["search_documents", "read_document", "read_document", "compare_sources", "take_notes"],
        expected_answer=["enterprise", "consistent", "growth"],
        verifier_config={
            "answer": ["enterprise", "20%", "growth", "consistent"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_documents", "compare_sources"],
                "optional": ["read_document", "extract_facts", "take_notes"],
                "min_calls": 3,
                "max_calls": 10
            }
        },
        description="Cross-reference and verify information",
        min_tool_calls=3,
        max_tool_calls=10,
        tags=["cross-reference", "verification"],
    ))

    tasks.append(Task(
        id="research_hard_02",
        name="Synthesize Strategy Recommendations",
        prompt="Review the market analysis, competitive intelligence, and product roadmap. Identify if our product strategy aligns with market opportunities and competitive threats. Generate a summary of your findings.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["search_documents", "read_document", "read_document", "read_document", "extract_facts", "generate_summary"],
        expected_answer=["AI", "alignment", "strategy"],
        verifier_config={
            "answer": ["AI", "strategy", "market", "competitive", "roadmap"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_documents", "generate_summary"],
                "optional": ["read_document", "extract_facts", "compare_sources", "take_notes"],
                "min_calls": 4,
                "max_calls": 12
            }
        },
        description="Multi-document strategy synthesis",
        min_tool_calls=4,
        max_tool_calls=12,
        tags=["synthesis", "strategy"],
    ))

    tasks.append(Task(
        id="research_hard_03",
        name="Customer-Product Alignment Analysis",
        prompt="Analyze whether the product roadmap addresses the top customer concerns from the survey. Extract facts from both documents, compare them, and document any gaps.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["search_documents", "extract_facts", "extract_facts", "compare_sources", "take_notes"],
        expected_answer=["mobile", "analytics", "addressed"],
        verifier_config={
            "answer": ["mobile", "analytics", "roadmap", "customer", "survey"],
            "match_mode": "contains",
            "tools": {
                "required": ["extract_facts", "compare_sources"],
                "optional": ["search_documents", "read_document", "take_notes"],
                "min_calls": 4,
                "max_calls": 10
            }
        },
        description="Alignment analysis between customer needs and product plans",
        min_tool_calls=4,
        max_tool_calls=10,
        tags=["alignment", "customer", "product"],
    ))

    tasks.append(Task(
        id="research_hard_04",
        name="Competitive Threat Assessment",
        prompt="Using the competitive intelligence and market analysis reports, assess the threat level from TechCorp's recent AI acquisition. How should we respond based on our roadmap?",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,  # FIXED: Prompt specifies which documents to read
            control_flow_from_tools=False,
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_conditional_logic=True,
        ),
        expected_tool_calls=["search_documents", "read_document", "read_document", "extract_facts", "take_notes"],
        expected_answer=["TechCorp", "AI", "acquisition", "accelerate"],
        verifier_config={
            "answer": ["TechCorp", "AI", "$200M", "accelerate", "threat"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_documents"],
                "optional": ["read_document", "extract_facts", "compare_sources", "take_notes"],
                "min_calls": 3,
                "max_calls": 10
            }
        },
        description="Competitive threat analysis and response recommendation",
        min_tool_calls=3,
        max_tool_calls=10,
        tags=["competitive", "threat", "strategy"],
    ))

    # ============================================================================
    # EXPERT TASKS (3 tasks, 11+ tool calls)
    # ============================================================================

    tasks.append(Task(
        id="research_expert_01",
        name="Comprehensive Market Position Analysis",
        prompt="""Conduct a comprehensive analysis of our market position by:
        1. Reviewing financial performance data
        2. Analyzing market trends and our market share
        3. Understanding competitive landscape
        4. Checking customer satisfaction levels
        5. Reviewing our product roadmap alignment

        Generate a comprehensive summary with key insights and recommendations.""",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_long_reasoning_chain=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["search_documents"] + ["read_document"] * 4 + ["extract_facts"] * 3 + ["take_notes", "generate_summary"],
        expected_answer=["market position", "recommendations", "summary"],
        verifier_config={
            "answer": ["market", "competitive", "customer", "roadmap", "financial"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_documents", "generate_summary"],
                "optional": ["read_document", "extract_facts", "compare_sources", "take_notes"],
                "min_calls": 6,
                "max_calls": 15
            }
        },
        description="Comprehensive multi-source market analysis",
        min_tool_calls=6,
        max_tool_calls=15,
        tags=["comprehensive", "market", "analysis"],
    ))

    tasks.append(Task(
        id="research_expert_02",
        name="Strategic Gap Analysis",
        prompt="""Perform a strategic gap analysis by:
        1. Identifying what customers want (from survey)
        2. Understanding market trends (from market analysis)
        3. Assessing competitor capabilities (from competitive intel)
        4. Reviewing our planned capabilities (from roadmap)
        5. Finding gaps between market needs and our plans
        6. Documenting all findings with detailed notes
        7. Generating a prioritized summary of gaps to address""",
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
        expected_tool_calls=["search_documents"] + ["read_document"] * 4 + ["extract_facts"] * 4 + ["compare_sources"] * 2 + ["take_notes"] * 3 + ["generate_summary"],
        expected_answer=["gaps", "priorities", "recommendations"],
        verifier_config={
            "answer": ["gap", "customer", "market", "competitor", "roadmap"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_documents", "extract_facts", "generate_summary"],
                "optional": ["read_document", "compare_sources", "take_notes"],
                "min_calls": 8,
                "max_calls": 20
            }
        },
        description="Multi-dimensional strategic gap analysis",
        min_tool_calls=8,
        max_tool_calls=20,
        tags=["gap-analysis", "strategy", "comprehensive"],
    ))

    tasks.append(Task(
        id="research_expert_03",
        name="Executive Briefing Preparation",
        prompt="""Prepare an executive briefing by researching and synthesizing information from all available documents:
        1. Search and identify all relevant documents
        2. Extract key facts from each document
        3. Cross-reference information across sources for consistency
        4. Identify any contradictions or inconsistencies
        5. Take detailed notes on critical findings
        6. Search the web for any recent relevant news
        7. Generate a comprehensive executive summary

        The briefing should cover: financial health, market position, competitive threats, customer satisfaction, and strategic priorities.""",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=True,  # FIXED: Explicit 7-step recipe provided
            control_flow_from_tools=False,
            data_flow_from_tools=True,
            requires_cross_reference=True,
            requires_long_reasoning_chain=True,
            requires_state_tracking=True,
            requires_plan_adaptation=True,
        ),
        expected_tool_calls=["search_documents"] + ["read_document"] * 5 + ["extract_facts"] * 5 + ["compare_sources"] * 2 + ["take_notes"] * 3 + ["search_web", "generate_summary"],
        expected_answer=["executive", "summary", "briefing"],
        verifier_config={
            "answer": ["financial", "market", "competitive", "customer", "strategy"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_documents", "extract_facts", "generate_summary"],
                "optional": ["read_document", "compare_sources", "take_notes", "search_web"],
                "min_calls": 10,
                "max_calls": 25
            }
        },
        description="Comprehensive executive briefing preparation",
        min_tool_calls=10,
        max_tool_calls=25,
        tags=["executive", "briefing", "comprehensive"],
    ))

    # ============================================================================
    # TRUE TOOL-DRIVEN CONTROL FLOW TASKS
    # These tasks require discovering what to do from tool responses
    # ============================================================================

    tasks.append(Task(
        id="research_discovery_01",
        name="Answer Ad-Hoc Question",
        prompt="The board wants to know: 'Are we on track?' Find relevant information to answer this question.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Must discover WHAT documents exist before knowing how to answer
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_cross_reference=True,
            requires_disambiguation=True,
        ),
        expected_tool_calls=["search_documents"],  # Document availability determines answer approach
        expected_answer=["track", "progress", "assessment"],
        verifier_config={
            "answer": ["track", "progress", "status"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_documents"],
                "optional": ["read_document", "extract_facts", "compare_sources", "generate_summary", "take_notes"],
                "min_calls": 2,
                "max_calls": 12
            }
        },
        description="TRUE tool-driven: vague question requires document discovery",
        min_tool_calls=2,
        max_tool_calls=12,
        tags=["discovery", "ad-hoc", "ambiguous"],
    ))

    tasks.append(Task(
        id="research_discovery_02",
        name="Find Supporting Evidence",
        prompt="Someone claimed our AI strategy is weak. Find evidence to either support or refute this claim.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Must discover what documents say about AI before concluding
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_cross_reference=True,
        ),
        expected_tool_calls=["search_documents"],  # Document content determines conclusion
        expected_answer=["evidence", "AI", "strategy"],
        verifier_config={
            "answer": ["AI", "strategy", "evidence"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_documents"],
                "optional": ["read_document", "extract_facts", "compare_sources", "take_notes"],
                "min_calls": 2,
                "max_calls": 10
            }
        },
        description="TRUE tool-driven: evidence determines support/refute conclusion",
        min_tool_calls=2,
        max_tool_calls=10,
        tags=["discovery", "evidence", "verification"],
    ))

    tasks.append(Task(
        id="research_discovery_03",
        name="Prepare for Unknown Meeting",
        prompt="I have an important meeting in an hour but forgot what it's about. Search our documents to figure out what topics I should be prepared to discuss.",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Must discover meeting context before knowing what to prepare
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_state_tracking=True,
        ),
        expected_tool_calls=["search_documents"],  # Document search reveals meeting context
        expected_answer=["meeting", "prepared", "topics"],
        verifier_config={
            "answer": ["meeting", "topic", "prepared"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_documents"],
                "optional": ["read_document", "extract_facts", "take_notes", "generate_summary"],
                "min_calls": 2,
                "max_calls": 10
            }
        },
        description="TRUE tool-driven: discovered context determines preparation topics",
        min_tool_calls=2,
        max_tool_calls=10,
        tags=["discovery", "meeting", "preparation"],
    ))

    tasks.append(Task(
        id="research_discovery_04",
        name="Identify Knowledge Gaps",
        prompt="Review our documentation and identify any significant gaps in our knowledge or missing information that we should address.",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Must discover document landscape to identify gaps
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_cross_reference=True,
            requires_long_reasoning_chain=True,
        ),
        expected_tool_calls=["search_documents"],  # Document inventory reveals gaps
        expected_answer=["gap", "missing", "knowledge"],
        verifier_config={
            "answer": ["gap", "missing", "information"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_documents"],
                "optional": ["read_document", "extract_facts", "compare_sources", "take_notes"],
                "min_calls": 3,
                "max_calls": 15
            }
        },
        description="TRUE tool-driven: document inventory determines gap analysis",
        min_tool_calls=3,
        max_tool_calls=15,
        tags=["discovery", "gaps", "audit"],
    ))

    tasks.append(Task(
        id="research_discovery_05",
        name="Resolve Contradictory Information",
        prompt="I've heard conflicting information about our market position. Search our documents, identify any contradictions, and determine the most accurate picture.",
        difficulty=DifficultyLevel.EXPERT,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Must discover what different documents say to find contradictions
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_cross_reference=True,
            requires_disambiguation=True,
        ),
        expected_tool_calls=["search_documents"],  # Document comparison reveals contradictions
        expected_answer=["contradiction", "resolved", "market"],
        verifier_config={
            "answer": ["market", "position", "contradiction"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_documents", "compare_sources"],
                "optional": ["read_document", "extract_facts", "take_notes", "generate_summary"],
                "min_calls": 3,
                "max_calls": 12
            }
        },
        description="TRUE tool-driven: document content determines contradictions to resolve",
        min_tool_calls=3,
        max_tool_calls=12,
        tags=["discovery", "contradiction", "resolution"],
    ))

    tasks.append(Task(
        id="research_discovery_06",
        name="Quick Research for Decision",
        prompt="I need to make a decision about whether to expand internationally. What does our available documentation say that could inform this decision?",
        difficulty=DifficultyLevel.HARD,
        information_flow=InformationFlow.TOOL_DISCOVERY,
        characteristics=TaskCharacteristics(
            control_flow_from_prompt=False,
            control_flow_from_tools=True,  # TRUE: Must discover what relevant info exists before synthesizing
            data_flow_from_tools=True,
            requires_conditional_logic=True,
            requires_cross_reference=True,
        ),
        expected_tool_calls=["search_documents"],  # Available information determines recommendation depth
        expected_answer=["international", "decision", "expansion"],
        verifier_config={
            "answer": ["international", "decision", "expand"],
            "match_mode": "contains",
            "tools": {
                "required": ["search_documents"],
                "optional": ["read_document", "extract_facts", "generate_summary", "take_notes"],
                "min_calls": 2,
                "max_calls": 10
            }
        },
        description="TRUE tool-driven: available information determines recommendation",
        min_tool_calls=2,
        max_tool_calls=10,
        tags=["discovery", "decision-support", "strategic"],
    ))

    return tasks
