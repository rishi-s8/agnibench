"""
Tasks for the software development benchmark suite.

Contains tasks for debugging, code navigation, and software engineering.
Tests code understanding, diagnostic reasoning, and multi-file analysis.
"""

from typing import List

from agnibench.core.abstractions import (DifficultyLevel, InformationFlow,
                                         Task, TaskCharacteristics)


def get_software_dev_tasks() -> List[Task]:
    """Get all software development tasks."""
    tasks = []

    # ============================================================================
    # SIMPLE TASKS (4 tasks, 2-3 tool calls)
    # ============================================================================

    tasks.append(
        Task(
            id="dev_simple_01",
            name="Find Source File",
            prompt="Find the file that contains the UserService class.",
            difficulty=DifficultyLevel.SIMPLE,
            information_flow=InformationFlow.PROMPT_FULL,
            characteristics=TaskCharacteristics(
                control_flow_from_prompt=True,
                data_flow_from_tools=True,
            ),
            expected_tool_calls=["search_codebase"],
            expected_answer="src/auth/user_service.py",
            verifier_config={
                "answer": ["user_service.py", "UserService", "src/auth"],
                "match_mode": "contains",
                "tools": {
                    "required": ["search_codebase"],
                    "min_calls": 1,
                    "max_calls": 2,
                },
            },
            description="Simple file/class search",
            min_tool_calls=1,
            max_tool_calls=2,
            tags=["search", "navigation"],
        )
    )

    tasks.append(
        Task(
            id="dev_simple_02",
            name="Read Error Logs",
            prompt="Show me the most recent error logs from the authentication system.",
            difficulty=DifficultyLevel.SIMPLE,
            information_flow=InformationFlow.PROMPT_FULL,
            characteristics=TaskCharacteristics(
                control_flow_from_prompt=True,
                data_flow_from_tools=True,
            ),
            expected_tool_calls=["search_logs"],
            expected_answer=["ERROR", "authentication", "user_service"],
            verifier_config={
                "answer": ["ERROR", "auth", "log"],
                "match_mode": "contains",
                "tools": {"required": ["search_logs"], "min_calls": 1, "max_calls": 2},
            },
            description="Simple log search",
            min_tool_calls=1,
            max_tool_calls=2,
            tags=["logs", "search"],
        )
    )

    tasks.append(
        Task(
            id="dev_simple_03",
            name="Check Test Results",
            prompt="Run the tests and tell me how many passed and failed.",
            difficulty=DifficultyLevel.SIMPLE,
            information_flow=InformationFlow.PROMPT_FULL,
            characteristics=TaskCharacteristics(
                control_flow_from_prompt=True,
                data_flow_from_tools=True,
            ),
            expected_tool_calls=["run_tests"],
            expected_answer=["passed", "failed", "3", "2"],
            verifier_config={
                "answer": ["passed", "failed"],
                "match_mode": "contains",
                "tools": {"required": ["run_tests"], "min_calls": 1, "max_calls": 2},
            },
            description="Run tests and report results",
            min_tool_calls=1,
            max_tool_calls=2,
            tags=["testing", "status"],
        )
    )

    tasks.append(
        Task(
            id="dev_simple_04",
            name="Find Function Definition",
            prompt="Find where the authenticate function is defined.",
            difficulty=DifficultyLevel.SIMPLE,
            information_flow=InformationFlow.PROMPT_FULL,
            characteristics=TaskCharacteristics(
                control_flow_from_prompt=True,
                data_flow_from_tools=True,
            ),
            expected_tool_calls=["find_references"],
            expected_answer=["authenticate", "user_service.py", "definition"],
            verifier_config={
                "answer": ["authenticate", "user_service", "def"],
                "match_mode": "contains",
                "tools": {
                    "required": ["find_references"],
                    "optional": ["search_codebase"],
                    "min_calls": 1,
                    "max_calls": 3,
                },
            },
            description="Find function definition",
            min_tool_calls=1,
            max_tool_calls=3,
            tags=["navigation", "function"],
        )
    )

    # ============================================================================
    # MEDIUM TASKS (5 tasks, 4-6 tool calls)
    # ============================================================================

    tasks.append(
        Task(
            id="dev_medium_01",
            name="Investigate Failed Test",
            prompt="A test is failing. Find out which test failed and what the error message says.",
            difficulty=DifficultyLevel.MEDIUM,
            information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
            characteristics=TaskCharacteristics(
                control_flow_from_prompt=True,
                data_flow_from_tools=True,
            ),
            expected_tool_calls=["run_tests", "read_file"],
            expected_answer=[
                "failed",
                "test_authenticate_invalid_password",
                "case-insensitive",
            ],
            verifier_config={
                "answer": ["failed", "test", "error", "password"],
                "match_mode": "contains",
                "tools": {
                    "required": ["run_tests"],
                    "optional": ["read_file", "search_codebase"],
                    "min_calls": 1,
                    "max_calls": 5,
                },
            },
            description="Identify failing test and error",
            min_tool_calls=1,
            max_tool_calls=5,
            tags=["testing", "investigation"],
        )
    )

    tasks.append(
        Task(
            id="dev_medium_02",
            name="Trace Error to Source",
            prompt="There's an error in the logs about 'Session persistence failed'. Find the source code that's causing this error.",
            difficulty=DifficultyLevel.MEDIUM,
            information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
            characteristics=TaskCharacteristics(
                control_flow_from_prompt=True,
                data_flow_from_tools=True,
                requires_cross_reference=True,
            ),
            expected_tool_calls=["search_logs", "get_stack_trace", "read_file"],
            expected_answer=["_create_session", "line 73", "memory", "not persisted"],
            verifier_config={
                "answer": ["session", "user_service.py", "persist", "line"],
                "match_mode": "contains",
                "tools": {
                    "required": ["search_logs", "read_file"],
                    "optional": ["get_stack_trace", "search_codebase"],
                    "min_calls": 2,
                    "max_calls": 6,
                },
            },
            description="Trace error log to source code",
            min_tool_calls=2,
            max_tool_calls=6,
            tags=["debugging", "trace"],
        )
    )

    tasks.append(
        Task(
            id="dev_medium_03",
            name="Check File Dependencies",
            prompt="What files does user_service.py depend on? List its imports and what other files import it.",
            difficulty=DifficultyLevel.MEDIUM,
            information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
            characteristics=TaskCharacteristics(
                control_flow_from_prompt=True,
                data_flow_from_tools=True,
            ),
            expected_tool_calls=["search_codebase", "get_file_dependencies"],
            expected_answer=["models", "database", "cache", "endpoints.py"],
            verifier_config={
                "answer": ["imports", "models", "database", "endpoints"],
                "match_mode": "contains",
                "tools": {
                    "required": ["get_file_dependencies"],
                    "optional": ["search_codebase", "read_file"],
                    "min_calls": 1,
                    "max_calls": 5,
                },
            },
            description="Map file dependencies",
            min_tool_calls=1,
            max_tool_calls=5,
            tags=["dependencies", "architecture"],
        )
    )

    tasks.append(
        Task(
            id="dev_medium_04",
            name="Review Recent Changes",
            prompt="What changes were made to the authentication system in the last week? Check the git history.",
            difficulty=DifficultyLevel.MEDIUM,
            information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
            characteristics=TaskCharacteristics(
                control_flow_from_prompt=True,
                data_flow_from_tools=True,
            ),
            expected_tool_calls=["get_git_history", "read_file"],
            expected_answer=["alice", "bob", "password hashing", "lowercase"],
            verifier_config={
                "answer": ["commit", "auth", "changed", "password"],
                "match_mode": "contains",
                "tools": {
                    "required": ["get_git_history"],
                    "optional": ["read_file", "search_codebase"],
                    "min_calls": 1,
                    "max_calls": 5,
                },
            },
            description="Review git history for changes",
            min_tool_calls=1,
            max_tool_calls=5,
            tags=["git", "history", "review"],
        )
    )

    tasks.append(
        Task(
            id="dev_medium_05",
            name="Find Documentation",
            prompt="Find documentation about the authentication system and summarize its key components.",
            difficulty=DifficultyLevel.MEDIUM,
            information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
            characteristics=TaskCharacteristics(
                control_flow_from_prompt=True,
                data_flow_from_tools=True,
            ),
            expected_tool_calls=["search_documentation", "search_codebase"],
            expected_answer=["UserService", "Session", "rate limit", "security"],
            verifier_config={
                "answer": ["authentication", "session", "component"],
                "match_mode": "contains",
                "tools": {
                    "required": ["search_documentation"],
                    "optional": ["search_codebase", "read_file"],
                    "min_calls": 1,
                    "max_calls": 5,
                },
            },
            description="Find and summarize documentation",
            min_tool_calls=1,
            max_tool_calls=5,
            tags=["documentation", "overview"],
        )
    )

    # ============================================================================
    # HARD TASKS (5 tasks, 7-10 tool calls)
    # ============================================================================

    tasks.append(
        Task(
            id="dev_hard_01",
            name="Debug Password Hash Bug",
            prompt="""There's a bug where users can sometimes log in with incorrect passwords.
Investigate the authentication code, find the bug, and explain what's wrong.""",
            difficulty=DifficultyLevel.HARD,
            information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
            characteristics=TaskCharacteristics(
                control_flow_from_prompt=True,
                data_flow_from_tools=True,
                requires_cross_reference=True,
                requires_long_reasoning_chain=True,
            ),
            expected_tool_calls=[
                "search_codebase",
                "read_file",
                "search_logs",
                "run_tests",
                "add_note",
            ],
            expected_answer=["case-insensitive", "lower()", "line 42", "password_hash"],
            verifier_config={
                "answer": ["case", "lower", "password", "bug", "hash"],
                "match_mode": "contains",
                "tools": {
                    "required": ["search_codebase", "read_file"],
                    "optional": [
                        "search_logs",
                        "run_tests",
                        "get_stack_trace",
                        "add_note",
                    ],
                    "min_calls": 3,
                    "max_calls": 10,
                },
            },
            description="Debug password comparison bug",
            min_tool_calls=3,
            max_tool_calls=10,
            tags=["debugging", "security", "authentication"],
        )
    )

    tasks.append(
        Task(
            id="dev_hard_02",
            name="Investigate Admin Access Bug",
            prompt="""Admin users are being denied access to the /api/users endpoint even though they should have permission.
Find the bug in the authorization logic.""",
            difficulty=DifficultyLevel.HARD,
            information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
            characteristics=TaskCharacteristics(
                control_flow_from_prompt=True,
                data_flow_from_tools=True,
                requires_cross_reference=True,
                requires_long_reasoning_chain=True,
            ),
            expected_tool_calls=[
                "search_logs",
                "get_stack_trace",
                "search_codebase",
                "read_file",
                "run_tests",
            ],
            expected_answer=[
                "!= user",
                "should be == admin",
                "inverted",
                "line 72",
                "authorization",
            ],
            verifier_config={
                "answer": ["authorization", "admin", "role", "endpoint", "bug"],
                "match_mode": "contains",
                "tools": {
                    "required": ["search_logs", "read_file"],
                    "optional": [
                        "get_stack_trace",
                        "search_codebase",
                        "run_tests",
                        "find_references",
                    ],
                    "min_calls": 3,
                    "max_calls": 10,
                },
            },
            description="Debug authorization logic bug",
            min_tool_calls=3,
            max_tool_calls=10,
            tags=["debugging", "authorization", "api"],
        )
    )

    tasks.append(
        Task(
            id="dev_hard_03",
            name="Find Session Persistence Bug",
            prompt="""Users are losing their sessions when the server restarts.
Find where sessions are managed and identify why they're not being persisted.""",
            difficulty=DifficultyLevel.HARD,
            information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
            characteristics=TaskCharacteristics(
                control_flow_from_prompt=True,
                data_flow_from_tools=True,
                requires_cross_reference=True,
                requires_long_reasoning_chain=True,
            ),
            expected_tool_calls=[
                "search_codebase",
                "read_file",
                "search_logs",
                "search_documentation",
            ],
            expected_answer=[
                "_session_store",
                "memory",
                "not persisted",
                "database",
                "_create_session",
            ],
            verifier_config={
                "answer": ["session", "memory", "persist", "database"],
                "match_mode": "contains",
                "tools": {
                    "required": ["search_codebase", "read_file"],
                    "optional": [
                        "search_logs",
                        "search_documentation",
                        "get_stack_trace",
                        "find_references",
                    ],
                    "min_calls": 3,
                    "max_calls": 10,
                },
            },
            description="Debug session persistence issue",
            min_tool_calls=3,
            max_tool_calls=10,
            tags=["debugging", "sessions", "persistence"],
        )
    )

    tasks.append(
        Task(
            id="dev_hard_04",
            name="Trace Bug to Commit",
            prompt="""A bug was introduced recently that made password comparison case-insensitive.
Find when this was introduced by checking the git history and identify the problematic commit.""",
            difficulty=DifficultyLevel.HARD,
            information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
            characteristics=TaskCharacteristics(
                control_flow_from_prompt=True,
                data_flow_from_tools=True,
                requires_cross_reference=True,
                requires_state_tracking=True,
            ),
            expected_tool_calls=["get_git_history", "read_file", "search_codebase"],
            expected_answer=[
                "bob@company.com",
                "q7r8s9t0",
                "lowercase",
                "optimize password",
            ],
            verifier_config={
                "answer": ["commit", "bob", "password", "lowercase"],
                "match_mode": "contains",
                "tools": {
                    "required": ["get_git_history"],
                    "optional": ["read_file", "search_codebase", "find_references"],
                    "min_calls": 2,
                    "max_calls": 8,
                },
            },
            description="Git bisect to find bug introduction",
            min_tool_calls=2,
            max_tool_calls=8,
            tags=["git", "debugging", "history"],
        )
    )

    tasks.append(
        Task(
            id="dev_hard_05",
            name="Cache Invalidation Bug",
            prompt="""There's a bug where user data changes aren't reflected immediately after updates.
Investigate the repository layer and find the cache invalidation issue.""",
            difficulty=DifficultyLevel.HARD,
            information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
            characteristics=TaskCharacteristics(
                control_flow_from_prompt=True,
                data_flow_from_tools=True,
                requires_cross_reference=True,
            ),
            expected_tool_calls=[
                "search_logs",
                "search_codebase",
                "read_file",
                "find_references",
            ],
            expected_answer=["cache", "invalidate", "update", "repository.py", "stale"],
            verifier_config={
                "answer": ["cache", "invalidate", "update", "repository"],
                "match_mode": "contains",
                "tools": {
                    "required": ["search_codebase", "read_file"],
                    "optional": [
                        "search_logs",
                        "find_references",
                        "get_file_dependencies",
                    ],
                    "min_calls": 3,
                    "max_calls": 10,
                },
            },
            description="Debug cache invalidation bug",
            min_tool_calls=3,
            max_tool_calls=10,
            tags=["debugging", "cache", "repository"],
        )
    )

    # ============================================================================
    # EXPERT TASKS (3 tasks, 11+ tool calls)
    # ============================================================================

    tasks.append(
        Task(
            id="dev_expert_01",
            name="Full Security Audit",
            prompt="""Perform a security audit of the authentication system:

1. Find all files related to authentication
2. Check for any files marked as having bugs
3. Read the suspicious files and identify security issues
4. Check the error logs for any security-related errors
5. Review the documentation for known issues
6. Document all security vulnerabilities found

Provide a comprehensive security report.""",
            difficulty=DifficultyLevel.EXPERT,
            information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
            characteristics=TaskCharacteristics(
                control_flow_from_prompt=True,
                data_flow_from_tools=True,
                requires_cross_reference=True,
                requires_long_reasoning_chain=True,
                requires_state_tracking=True,
            ),
            expected_tool_calls=["search_codebase"]
            + ["read_file"] * 3
            + ["search_logs", "search_documentation", "add_note"],
            expected_answer=[
                "security",
                "vulnerabilities",
                "password",
                "session",
                "authorization",
            ],
            verifier_config={
                "answer": ["security", "vulnerability", "password", "authentication"],
                "match_mode": "contains",
                "tools": {
                    "required": ["search_codebase", "read_file", "add_note"],
                    "optional": [
                        "search_logs",
                        "search_documentation",
                        "find_references",
                        "run_tests",
                    ],
                    "min_calls": 6,
                    "max_calls": 20,
                },
                "state": {
                    "notes_added": {
                        "$contains": {
                            "content": {
                                "$regex": "(?is)(?=.*case[- ]?insensitive)(?=.*password)(?=.*session)"
                            }
                        }
                    }
                },
                "expected_state": {
                    "notes_added": {
                        "$contains": {
                            "content": {
                                "$regex": "(?is)(?=.*case[- ]?insensitive)(?=.*password)(?=.*session)"
                            }
                        }
                    }
                },
            },
            description="Comprehensive security audit",
            min_tool_calls=6,
            max_tool_calls=20,
            tags=["security", "audit", "comprehensive"],
        )
    )

    tasks.append(
        Task(
            id="dev_expert_02",
            name="Root Cause Analysis",
            prompt="""Multiple test failures have been reported. Perform a root cause analysis:

1. Run all tests to see the current state
2. For each failing test, trace the error to its source
3. Check the git history to see if the failures correlate with recent changes
4. Identify if there's a common root cause
5. Document the root cause and propose fixes

Provide a detailed root cause analysis report.""",
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
            expected_tool_calls=[
                "run_tests",
                "read_file",
                "read_file",
                "get_git_history",
                "search_logs",
                "add_note",
            ],
            expected_answer=[
                "root cause",
                "password",
                "authorization",
                "commit",
                "fix",
            ],
            verifier_config={
                "answer": ["root cause", "failed", "test", "fix"],
                "match_mode": "contains",
                "tools": {
                    "required": ["run_tests", "read_file", "add_note"],
                    "optional": [
                        "get_git_history",
                        "search_logs",
                        "get_stack_trace",
                        "search_codebase",
                    ],
                    "min_calls": 6,
                    "max_calls": 20,
                },
                "state": {
                    "notes_added": {
                        "$contains": {
                            "content": {"$regex": "(?i)root\\s+cause"}
                        }
                    },
                    "tests_run": {
                        "$contains": {"results_count": {"$range": [1, 1000]}}
                    },
                },
                "expected_state": {
                    "notes_added": {
                        "$contains": {
                            "content": {"$regex": "(?i)root\\s+cause"}
                        }
                    },
                    "tests_run": {
                        "$contains": {"results_count": {"$range": [1, 1000]}}
                    },
                },
            },
            description="Multi-failure root cause analysis",
            min_tool_calls=6,
            max_tool_calls=20,
            tags=["rca", "debugging", "comprehensive"],
        )
    )

    tasks.append(
        Task(
            id="dev_expert_03",
            name="Codebase Architecture Review",
            prompt="""Perform a comprehensive architecture review of the authentication system:

1. Map all components (files, classes, functions)
2. Trace the dependency graph
3. Identify the data flow for a login request
4. Check for architectural issues (circular dependencies, tight coupling)
5. Review the test coverage
6. Document the architecture with notes

Provide an architecture overview with improvement recommendations.""",
            difficulty=DifficultyLevel.EXPERT,
            information_flow=InformationFlow.PROMPT_CONTROL_TOOL_DATA,
            characteristics=TaskCharacteristics(
                control_flow_from_prompt=True,
                data_flow_from_tools=True,
                requires_cross_reference=True,
                requires_long_reasoning_chain=True,
                requires_state_tracking=True,
            ),
            expected_tool_calls=["search_codebase"]
            + ["get_file_dependencies"] * 3
            + ["read_file"] * 3
            + ["run_tests", "add_note"],
            expected_answer=[
                "architecture",
                "dependencies",
                "components",
                "flow",
                "recommendations",
            ],
            verifier_config={
                "answer": ["architecture", "component", "dependency", "flow"],
                "match_mode": "contains",
                "tools": {
                    "required": [
                        "search_codebase",
                        "get_file_dependencies",
                        "add_note",
                    ],
                    "optional": [
                        "read_file",
                        "run_tests",
                        "find_references",
                        "search_documentation",
                    ],
                    "min_calls": 6,
                    "max_calls": 20,
                },
                "state": {
                    "notes_added": {
                        "$contains": {
                            "content": {
                                "$regex": "(?is)(?=.*dependency)(?=.*data\\s+flow)"
                            }
                        }
                    }
                },
                "expected_state": {
                    "notes_added": {
                        "$contains": {
                            "content": {
                                "$regex": "(?is)(?=.*dependency)(?=.*data\\s+flow)"
                            }
                        }
                    }
                },
            },
            description="Full architecture review",
            min_tool_calls=6,
            max_tool_calls=20,
            tags=["architecture", "review", "comprehensive"],
        )
    )

    # ============================================================================
    # TRUE TOOL-DRIVEN CONTROL FLOW TASKS
    # These tasks require discovering what to do from tool responses
    # ============================================================================

    tasks.append(
        Task(
            id="dev_discovery_01",
            name="Debug Unknown Error",
            prompt="There's a bug reported in production but we don't know what it is. Check the logs and investigate.",
            difficulty=DifficultyLevel.HARD,
            information_flow=InformationFlow.TOOL_DISCOVERY,
            characteristics=TaskCharacteristics(
                control_flow_from_prompt=False,
                control_flow_from_tools=True,  # TRUE: Must discover WHAT error before knowing HOW to debug
                data_flow_from_tools=True,
                requires_conditional_logic=True,
                requires_plan_adaptation=True,
            ),
            expected_tool_calls=[
                "search_logs"
            ],  # Error type determines investigation path
            expected_answer=["bug", "found", "error", "investigation"],
            verifier_config={
                "answer": ["error", "bug", "found", "log"],
                "match_mode": "contains",
                "tools": {
                    "required": ["search_logs"],
                    "optional": [
                        "get_stack_trace",
                        "read_file",
                        "search_codebase",
                        "find_references",
                        "add_note",
                    ],
                    "min_calls": 2,
                    "max_calls": 12,
                },
            },
            description="TRUE tool-driven: discovered error type determines investigation path",
            min_tool_calls=2,
            max_tool_calls=12,
            tags=["discovery", "debugging", "unknown"],
        )
    )

    tasks.append(
        Task(
            id="dev_discovery_02",
            name="Fix Failing Tests",
            prompt="Some tests are failing. Find out which ones and fix the underlying issues.",
            difficulty=DifficultyLevel.EXPERT,
            information_flow=InformationFlow.TOOL_DISCOVERY,
            characteristics=TaskCharacteristics(
                control_flow_from_prompt=False,
                control_flow_from_tools=True,  # TRUE: Must run tests to discover WHICH failed and WHY
                data_flow_from_tools=True,
                requires_conditional_logic=True,
                requires_long_reasoning_chain=True,
                requires_state_tracking=True,
            ),
            expected_tool_calls=[
                "run_tests"
            ],  # Test results determine which files to investigate
            expected_answer=["fixed", "test", "passing"],
            verifier_config={
                "answer": ["test", "fix", "failed"],
                "match_mode": "contains",
                "tools": {
                    "required": ["run_tests"],
                    "optional": [
                        "read_file",
                        "search_codebase",
                        "apply_fix",
                        "add_note",
                        "find_references",
                    ],
                    "min_calls": 3,
                    "max_calls": 15,
                },
            },
            description="TRUE tool-driven: test failures determine fix approach",
            min_tool_calls=3,
            max_tool_calls=15,
            tags=["discovery", "testing", "fixing"],
        )
    )

    tasks.append(
        Task(
            id="dev_discovery_03",
            name="Understand Unfamiliar Code",
            prompt="I need to understand how the login flow works. Explore the codebase and document what you find.",
            difficulty=DifficultyLevel.HARD,
            information_flow=InformationFlow.TOOL_DISCOVERY,
            characteristics=TaskCharacteristics(
                control_flow_from_prompt=False,
                control_flow_from_tools=True,  # TRUE: Code structure determines exploration path
                data_flow_from_tools=True,
                requires_cross_reference=True,
                requires_state_tracking=True,
            ),
            expected_tool_calls=[
                "search_codebase"
            ],  # Found files determine what to read next
            expected_answer=["login", "flow", "understand", "documented"],
            verifier_config={
                "answer": ["login", "flow", "authentication"],
                "match_mode": "contains",
                "tools": {
                    "required": ["search_codebase"],
                    "optional": [
                        "read_file",
                        "get_file_dependencies",
                        "find_references",
                        "search_documentation",
                        "add_note",
                    ],
                    "min_calls": 3,
                    "max_calls": 12,
                },
            },
            description="TRUE tool-driven: code structure determines exploration",
            min_tool_calls=3,
            max_tool_calls=12,
            tags=["discovery", "exploration", "understanding"],
        )
    )

    tasks.append(
        Task(
            id="dev_discovery_04",
            name="Find Code Smells",
            prompt="Review the codebase for any code quality issues or bugs. Report what you find.",
            difficulty=DifficultyLevel.EXPERT,
            information_flow=InformationFlow.TOOL_DISCOVERY,
            characteristics=TaskCharacteristics(
                control_flow_from_prompt=False,
                control_flow_from_tools=True,  # TRUE: Must discover files and analyze to find issues
                data_flow_from_tools=True,
                requires_conditional_logic=True,
                requires_cross_reference=True,
                requires_long_reasoning_chain=True,
            ),
            expected_tool_calls=["search_codebase"],  # Files found determine analysis
            expected_answer=["issues", "bugs", "quality", "found"],
            verifier_config={
                "answer": ["issue", "bug", "quality", "code"],
                "match_mode": "contains",
                "tools": {
                    "required": ["search_codebase", "read_file"],
                    "optional": [
                        "find_references",
                        "get_file_dependencies",
                        "search_logs",
                        "add_note",
                    ],
                    "min_calls": 4,
                    "max_calls": 15,
                },
            },
            description="TRUE tool-driven: discovered files determine analysis scope",
            min_tool_calls=4,
            max_tool_calls=15,
            tags=["discovery", "quality", "review"],
        )
    )

    # ============================================================================
    # COMPOUND TASKS
    # Tasks that combine multiple independent problems
    # ============================================================================

    tasks.append(
        Task(
            id="dev_compound_01",
            name="Multi-Bug Investigation",
            prompt="""Investigate and document the following three reported issues:

ISSUE 1: Users can log in with incorrect password case (e.g., "PASSWORD" works when "password" is correct)
ISSUE 2: Admin users get "Unauthorized" error when accessing /api/users endpoint
ISSUE 3: Sessions are lost when server restarts

For each issue:
1. Find the relevant code
2. Identify the root cause
3. Document the bug location and fix

Provide a summary of all three bugs.""",
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
            expected_tool_calls=["search_codebase"]
            + ["read_file"] * 3
            + ["search_logs"]
            + ["add_note"] * 3,
            expected_answer=[
                "password case",
                "authorization",
                "session persistence",
                "bugs",
                "fixes",
            ],
            verifier_config={
                "answer": ["password", "admin", "session", "bug", "fix"],
                "match_mode": "contains",
                "tools": {
                    "required": ["search_codebase", "read_file", "add_note"],
                    "optional": [
                        "search_logs",
                        "get_stack_trace",
                        "find_references",
                        "run_tests",
                    ],
                    "min_calls": 8,
                    "max_calls": 25,
                },
                "state": {
                    "notes_added": {
                        "$contains": [
                            {
                                "content": {
                                    "$regex": "(?is)(?=.*password)(?=.*case[- ]?insensitive)"
                                }
                            },
                            {
                                "content": {
                                    "$regex": "(?is)(?=.*unauthorized)(?=.*admin)(?=.*api\\s*/?users)"
                                }
                            },
                            {
                                "content": {
                                    "$regex": "(?is)(?=.*session)(?=.*restart)"
                                }
                            },
                        ]
                    }
                },
                "expected_state": {
                    "notes_added": {
                        "$contains": [
                            {
                                "content": {
                                    "$regex": "(?is)(?=.*password)(?=.*case[- ]?insensitive)"
                                }
                            },
                            {
                                "content": {
                                    "$regex": "(?is)(?=.*unauthorized)(?=.*admin)(?=.*api\\s*/?users)"
                                }
                            },
                            {
                                "content": {
                                    "$regex": "(?is)(?=.*session)(?=.*restart)"
                                }
                            },
                        ]
                    }
                },
            },
            description="Compound: Investigate three independent bugs",
            min_tool_calls=8,
            max_tool_calls=25,
            tags=["compound", "multi-bug", "investigation"],
        )
    )

    tasks.append(
        Task(
            id="dev_compound_02",
            name="Code Review and Testing",
            prompt="""Perform a code review and testing session:

PART 1 - CODE REVIEW:
- Find all files related to authentication
- Review for bugs or security issues
- Document any issues found

PART 2 - TESTING:
- Run all tests
- For failing tests, identify the cause
- Correlate test failures with code issues

PART 3 - HISTORY ANALYSIS:
- Check recent commits to auth-related files
- Identify if any recent change introduced bugs

Provide a combined report covering all three parts.""",
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
            expected_tool_calls=[
                "search_codebase",
                "read_file",
                "read_file",
                "run_tests",
                "get_git_history",
                "add_note",
            ],
            expected_answer=["review", "tests", "history", "report", "issues"],
            verifier_config={
                "answer": ["review", "test", "commit", "issue"],
                "match_mode": "contains",
                "tools": {
                    "required": ["search_codebase", "run_tests", "get_git_history"],
                    "optional": [
                        "read_file",
                        "find_references",
                        "search_logs",
                        "add_note",
                    ],
                    "min_calls": 6,
                    "max_calls": 25,
                },
                "state": {
                    "tests_run": {
                        "$contains": {"results_count": {"$range": [1, 1000]}}
                    }
                },
                "expected_state": {
                    "tests_run": {
                        "$contains": {"results_count": {"$range": [1, 1000]}}
                    }
                },
            },
            description="Compound: Code review, testing, and history analysis",
            min_tool_calls=6,
            max_tool_calls=25,
            tags=["compound", "review", "testing", "history"],
        )
    )

    return tasks
