"""
Tool archetype definitions for procedural benchmark generation.

Separates what a tool does (archetype) from how its API looks (surface).
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ParameterArchetype:
    """Defines the semantic role of a tool parameter, independent of surface naming."""

    semantic_role: str  # "search_query", "entity_id", "filter_field"
    data_type: str  # "string", "integer", "boolean", "array"
    required: bool
    default: Any = None
    constraints: Dict[str, Any] = field(default_factory=dict)  # enums, ranges, etc.
    name_variants: List[str] = field(default_factory=list)
    description_templates: List[str] = field(default_factory=list)


@dataclass
class ToolArchetype:
    """Defines what a tool does, independent of its API surface."""

    archetype_id: str  # "search_emails", "create_event"
    category: str  # "query", "mutate", "compute", "lookup"
    semantic_description: str
    parameters: List[ParameterArchetype]
    returns: Dict[str, Any]  # Abstract return schema
    side_effects: List[str]  # State keys this tool modifies (e.g., ["sent_emails"])
    name_variants: List[str]  # ["search_emails", "find_messages", "query_inbox"]
    description_templates: List[str]
    behavior_key: str  # Maps to implementation function

    def get_required_params(self) -> List[ParameterArchetype]:
        """Return only required parameters."""
        return [p for p in self.parameters if p.required]

    def get_param_by_role(self, role: str) -> Optional[ParameterArchetype]:
        """Find a parameter by its semantic role."""
        for p in self.parameters:
            if p.semantic_role == role:
                return p
        return None


@dataclass
class DomainArchetypeSet:
    """A collection of tool archetypes for a specific domain."""

    domain: str  # "workspace"
    archetypes: List[ToolArchetype]
    data_schema: Dict[str, Any]  # Schema for environment data
    entity_generators: Dict[str, Callable] = field(default_factory=dict)

    def get_archetype(self, archetype_id: str) -> Optional[ToolArchetype]:
        """Find an archetype by ID."""
        for a in self.archetypes:
            if a.archetype_id == archetype_id:
                return a
        return None

    def get_archetypes_by_category(self, category: str) -> List[ToolArchetype]:
        """Get all archetypes in a category."""
        return [a for a in self.archetypes if a.category == category]

    def get_mutating_archetypes(self) -> List[ToolArchetype]:
        """Get archetypes that modify environment state."""
        return [a for a in self.archetypes if a.side_effects]
