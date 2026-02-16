"""
Seed-controlled API surface randomization.

Given a ToolArchetype + seed, produces a concrete Tool with randomized
name, parameter names, and description — while preserving behavior.
"""

import random
from typing import Any, Callable, Dict, List, Tuple

from agentbuilder.Tools.base import Tool

from agnibench.procedural.archetypes import ParameterArchetype, ToolArchetype


def _pick_variant(variants: List[str], rng: random.Random) -> str:
    """Pick a random variant from a list using the seeded RNG."""
    return rng.choice(variants)


def _build_param_schema(
    param: ParameterArchetype,
    surface_name: str,
    rng: random.Random,
) -> Dict[str, Any]:
    """Build a JSON schema entry for a parameter."""
    schema: Dict[str, Any] = {}

    type_map = {
        "string": "string",
        "integer": "integer",
        "boolean": "boolean",
        "array": "array",
    }
    schema["type"] = type_map.get(param.data_type, "string")

    if param.data_type == "array":
        schema["items"] = {"type": "string"}

    schema["description"] = _pick_variant(param.description_templates, rng)

    if param.default is not None:
        schema["default"] = param.default

    return schema


def mutate_tool_surface(
    archetype: ToolArchetype,
    impl_factory: Callable[[Dict[str, Any]], Callable],
    data_store: Dict[str, Any],
    rng: random.Random,
) -> Tuple[Tool, Dict[str, str]]:
    """
    Given a ToolArchetype and seed-controlled RNG, produce a concrete Tool
    with randomized API surface.

    Args:
        archetype: The tool archetype to mutate
        impl_factory: Factory that creates the implementation function (from workspace_impl)
        data_store: Shared data store dict for closure-based implementations
        rng: Seeded random.Random instance

    Returns:
        Tuple of (Tool, param_name_map) where param_name_map is
        {surface_param_name: semantic_role}
    """
    # Pick tool name
    tool_name = _pick_variant(archetype.name_variants, rng)

    # Pick tool description
    tool_description = _pick_variant(archetype.description_templates, rng)

    # Pick parameter surface names and build schema
    param_name_map: Dict[str, str] = {}  # surface_name -> semantic_role
    reverse_map: Dict[str, str] = {}  # semantic_role -> surface_name
    properties: Dict[str, Any] = {}
    required: List[str] = []

    for param in archetype.parameters:
        surface_name = _pick_variant(param.name_variants, rng)

        # Avoid collisions — if we already picked this name, try others
        attempts = 0
        while surface_name in param_name_map and attempts < len(param.name_variants):
            surface_name = _pick_variant(param.name_variants, rng)
            attempts += 1

        # If still colliding, append semantic role to disambiguate
        if surface_name in param_name_map:
            surface_name = f"{surface_name}_{param.semantic_role}"

        param_name_map[surface_name] = param.semantic_role
        reverse_map[param.semantic_role] = surface_name
        properties[surface_name] = _build_param_schema(param, surface_name, rng)

        if param.required:
            required.append(surface_name)

    parameters_schema = {
        "type": "object",
        "properties": properties,
        "required": required,
    }

    # Create the canonical implementation
    canonical_impl = impl_factory(data_store)

    # Create wrapper that translates surface param names → semantic (canonical) names
    def surface_wrapper(**kwargs):
        canonical_kwargs = {}
        for surface_name, value in kwargs.items():
            semantic_role = param_name_map.get(surface_name, surface_name)
            canonical_kwargs[semantic_role] = value
        return canonical_impl(**canonical_kwargs)

    tool = Tool(
        name=tool_name,
        description=tool_description,
        parameters=parameters_schema,
        function=surface_wrapper,
    )

    return tool, param_name_map


def mutate_all_tools(
    archetypes: List[ToolArchetype],
    impl_registry: Dict[str, Callable],
    data_store: Dict[str, Any],
    seed: int,
) -> Tuple[List[Tool], Dict[str, Dict[str, str]], Dict[str, str]]:
    """
    Mutate all tool archetypes with a single seed.

    Args:
        archetypes: List of tool archetypes to mutate
        impl_registry: Maps behavior_key -> impl factory function
        data_store: Shared data store
        seed: Random seed for deterministic mutation

    Returns:
        Tuple of:
        - List[Tool]: The mutated tools
        - Dict[str, Dict[str, str]]: Maps tool_name -> {surface_param: semantic_role}
        - Dict[str, str]: Maps archetype_id -> surface tool_name
    """
    rng = random.Random(seed)
    tools: List[Tool] = []
    all_param_maps: Dict[str, Dict[str, str]] = {}
    archetype_to_surface: Dict[str, str] = {}

    # Track used tool names to avoid collisions
    used_names = set()

    for archetype in archetypes:
        impl_factory = impl_registry.get(archetype.behavior_key)
        if impl_factory is None:
            raise ValueError(
                f"No implementation found for behavior_key '{archetype.behavior_key}'"
            )

        tool, param_map = mutate_tool_surface(archetype, impl_factory, data_store, rng)

        # Ensure unique tool names
        while tool.name in used_names:
            tool_name = _pick_variant(archetype.name_variants, rng)
            tool = Tool(
                name=tool_name,
                description=tool.description,
                parameters=tool.parameters,
                function=tool.function,
            )

        used_names.add(tool.name)
        tools.append(tool)
        all_param_maps[tool.name] = param_map
        archetype_to_surface[archetype.archetype_id] = tool.name

    return tools, all_param_maps, archetype_to_surface
