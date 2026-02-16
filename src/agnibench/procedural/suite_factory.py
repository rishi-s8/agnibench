"""
Suite factory — orchestrator that composes all procedural components
to produce a standard BenchmarkSuite from a seed + config.

Same seed -> identical benchmark. Different seed -> same capabilities, different surface.
"""

from typing import Any, Dict, List, Optional, Tuple

from agnibench.core.abstractions import (
    BenchmarkSuite,
    DifficultyLevel,
    InformationFlow,
    Task,
    TaskCharacteristics,
)
from agnibench.procedural.archetypes import DomainArchetypeSet
from agnibench.procedural.dag import TaskDAGBundle
from agnibench.procedural.dag_generator import DAGGenerator
from agnibench.procedural.data_generator import DataGenerator
from agnibench.procedural.difficulty import get_profile
from agnibench.procedural.environment import ProceduralEnvironment
from agnibench.procedural.prompt_generator import PromptGenerator
from agnibench.procedural.surface_mutator import mutate_all_tools
from agnibench.procedural.verification_generator import VerificationGenerator
from agnibench.procedural.workspace_archetypes import get_workspace_archetype_set
from agnibench.procedural.workspace_impl import WORKSPACE_IMPL_REGISTRY


def _make_verifier_factory(archetype_set: DomainArchetypeSet):
    """Create a verifier factory compatible with the existing workspace verifier."""
    from agnibench.suites.workspace.verifiers import create_workspace_verifier

    def factory(task: Task):
        return create_workspace_verifier(task.verifier_config)

    return factory


def _make_environment_class(data_store: Dict[str, Any]):
    """
    Create a ProceduralEnvironment subclass bound to a specific data_store.

    The BenchmarkRunner instantiates environment_class(), so we need a class
    that captures the data_store in its constructor.
    """

    class BoundProceduralEnvironment(ProceduralEnvironment):
        def __init__(self):
            super().__init__(data_store=data_store)

    return BoundProceduralEnvironment


class ProceduralSuiteFactory:
    """
    Orchestrator that produces a BenchmarkSuite from seed + config.

    Pipeline:
        SurfaceMutator -> List[Tool] + surface_maps
        DAGGenerator -> List[TaskDAGBundle]
        DataGenerator -> entity_bindings + initial_state (per task)
        PromptGenerator -> prompt (per task)
        VerificationGenerator -> verifier_config (per task)
        -> BenchmarkSuite
    """

    def __init__(
        self,
        domain: str = "workspace",
        seed: int = 42,
        llm_polish: bool = False,
        cache_dir: Optional[str] = None,
    ):
        self.domain = domain
        self.seed = seed
        self.llm_polish = llm_polish
        self.cache_dir = cache_dir

        # Currently only workspace domain
        if domain == "workspace":
            self.archetype_set = get_workspace_archetype_set()
            self.impl_registry = WORKSPACE_IMPL_REGISTRY
        else:
            raise ValueError(f"Unknown domain: {domain}. Available: ['workspace']")

    def create_suite(
        self,
        difficulty_distribution: Optional[Dict[DifficultyLevel, int]] = None,
    ) -> BenchmarkSuite:
        """
        Create a complete BenchmarkSuite.

        Args:
            difficulty_distribution: Maps DifficultyLevel -> number of tasks.
                Defaults to {SIMPLE: 2, MEDIUM: 2, HARD: 1, EXPERT: 1}.

        Returns:
            A standard BenchmarkSuite ready for BenchmarkRunner
        """
        if difficulty_distribution is None:
            difficulty_distribution = {
                DifficultyLevel.SIMPLE: 2,
                DifficultyLevel.MEDIUM: 2,
                DifficultyLevel.HARD: 1,
                DifficultyLevel.EXPERT: 1,
            }

        # Step 1: Create shared data store and mutate tool surfaces
        data_store: Dict[str, Any] = {}

        tools, param_maps, archetype_to_surface = mutate_all_tools(
            archetypes=self.archetype_set.archetypes,
            impl_registry=self.impl_registry,
            data_store=data_store,
            seed=self.seed,
        )

        # Step 2: Initialize generators
        dag_generator = DAGGenerator(self.archetype_set, seed=self.seed)
        data_gen = DataGenerator(self.archetype_set, seed=self.seed)
        prompt_gen = PromptGenerator(
            self.archetype_set,
            seed=self.seed,
            llm_polish=self.llm_polish,
            cache_dir=self.cache_dir,
        )
        verif_gen = VerificationGenerator(self.archetype_set)

        # Step 3: Generate tasks for each difficulty level
        tasks: List[Task] = []
        task_initial_states: List[Dict[str, Any]] = []
        task_counter = 0

        for difficulty, count in difficulty_distribution.items():
            bundles = dag_generator.generate_batch(difficulty, count)
            profile = get_profile(difficulty)

            for bundle in bundles:
                task_counter += 1

                # Generate data consistent with DAG
                initial_state, entity_bindings = data_gen.generate(bundle)
                task_initial_states.append(initial_state)

                # Generate prompt (information_flow controls how much the prompt reveals)
                prompt = prompt_gen.generate(bundle, entity_bindings, profile.information_flow)

                # Generate verifier config
                verifier_config = verif_gen.generate(
                    bundle, entity_bindings, archetype_to_surface
                )

                # Build expected tool call list (surface names)
                expected_tool_calls = []
                for node in bundle.execution.get_tool_call_nodes():
                    surface_name = archetype_to_surface.get(node.archetype_id, node.archetype_id)
                    expected_tool_calls.append(surface_name)

                # Build characteristics
                characteristics = TaskCharacteristics.from_information_flow(
                    profile.information_flow
                )
                characteristics.requires_cross_reference = profile.p_cross_reference > 0.3
                characteristics.requires_conditional_logic = profile.p_conditional > 0.3
                characteristics.requires_error_recovery = profile.p_error_recovery > 0.3
                characteristics.requires_plan_adaptation = profile.p_plan_adaptation > 0.3
                characteristics.requires_state_tracking = bundle.tool_call_count > 4
                characteristics.requires_long_reasoning_chain = bundle.depth > 4

                task = Task(
                    id=f"proc_{self.domain}_{self.seed}_{task_counter:03d}",
                    name=f"Procedural {difficulty.value.title()} Task {task_counter}",
                    prompt=prompt,
                    difficulty=difficulty,
                    information_flow=profile.information_flow,
                    characteristics=characteristics,
                    expected_tool_calls=expected_tool_calls,
                    expected_answer=verifier_config.get("answer", []),
                    verifier_config=verifier_config,
                    description=f"Procedurally generated {difficulty.value} task (seed={self.seed})",
                    min_tool_calls=bundle.tool_call_count,
                    max_tool_calls=bundle.tool_call_count * 2,
                    tags=["procedural", self.domain, difficulty.value],
                    metadata={
                        "seed": self.seed,
                        "dag_id": bundle.dag_id,
                        "dag_depth": bundle.depth,
                        "dag_breadth": bundle.breadth,
                        "tool_call_count": bundle.tool_call_count,
                    },
                )
                tasks.append(task)

        # Step 4: Merge all initial states into the data store
        # Use the first task's initial state as the base, then merge others
        if task_initial_states:
            merged_state = task_initial_states[0].copy()

            for state in task_initial_states[1:]:
                # Merge list fields by extending
                for key in ["emails", "calendar_events", "slack_messages", "contacts"]:
                    existing_ids = {
                        item.get("id") for item in merged_state.get(key, [])
                    }
                    for item in state.get(key, []):
                        if item.get("id") not in existing_ids:
                            merged_state.setdefault(key, []).append(item)
                            existing_ids.add(item.get("id"))

            # Initialize data store
            data_store.update(merged_state)

        # Step 5: Create bound environment class
        environment_class = _make_environment_class(data_store)

        # Step 6: Assemble BenchmarkSuite
        suite = BenchmarkSuite(
            name=f"procedural_{self.domain}",
            description=(
                f"Procedurally generated {self.domain} benchmark suite "
                f"(seed={self.seed}, {len(tasks)} tasks)"
            ),
            tasks=tasks,
            tools=tools,
            environment_class=environment_class,
            version="1.0.0",
            tags=["procedural", self.domain],
            verifier_factory=_make_verifier_factory(self.archetype_set),
        )

        return suite


def create_procedural_suite(
    domain: str = "workspace",
    seed: int = 42,
    difficulty_distribution: Optional[Dict[DifficultyLevel, int]] = None,
    llm_polish: bool = False,
    cache_dir: Optional[str] = None,
) -> BenchmarkSuite:
    """
    Convenience function to create a procedural benchmark suite.

    Args:
        domain: Domain name (currently only "workspace")
        seed: Random seed for deterministic generation
        difficulty_distribution: Optional map of difficulty -> task count
        llm_polish: Whether to use LLM to polish prompts
        cache_dir: Directory for caching polished prompts

    Returns:
        A standard BenchmarkSuite
    """
    factory = ProceduralSuiteFactory(
        domain=domain,
        seed=seed,
        llm_polish=llm_polish,
        cache_dir=cache_dir,
    )
    return factory.create_suite(difficulty_distribution)
