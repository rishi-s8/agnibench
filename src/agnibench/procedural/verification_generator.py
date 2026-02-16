"""
Verification generator that auto-derives verifier_config from a TaskDAG.

Produces verifier configs compatible with the existing BenchmarkRunner._get_verifier()
and create_workspace_verifier() factory.
"""

from typing import Any, Dict, List

from agnibench.procedural.archetypes import DomainArchetypeSet
from agnibench.procedural.dag import NodeType, TaskDAG, TaskDAGBundle


class VerificationGenerator:
    """
    Auto-derives verifier_config from a TaskDAG.

    Output format matches existing verifier_config schema exactly, so it's
    compatible with the BenchmarkRunner and workspace verifier factory.
    """

    def __init__(self, archetype_set: DomainArchetypeSet):
        self.archetype_set = archetype_set

    def generate(
        self,
        bundle: TaskDAGBundle,
        entity_bindings: Dict[str, Any],
        archetype_to_surface: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Generate verifier_config from a DAG bundle.

        Args:
            bundle: TaskDAGBundle containing the execution DAG
            entity_bindings: Entity bindings from data generator
            archetype_to_surface: Maps archetype_id -> surface tool name

        Returns:
            verifier_config dict compatible with existing verification system
        """
        dag = bundle.execution
        config: Dict[str, Any] = {}

        # 1. Tool verification
        tool_nodes = dag.get_tool_call_nodes()
        required_tools = []
        for node in tool_nodes:
            surface_name = archetype_to_surface.get(node.archetype_id)
            if surface_name and surface_name not in required_tools:
                required_tools.append(surface_name)

        config["tools"] = {
            "required": required_tools,
            "min_calls": len(tool_nodes),
            "max_calls": len(tool_nodes) * 2,  # Allow some extra calls
        }

        # 2. State verification — find mutating nodes
        state_conditions = {}
        expected_state = {}

        for node in tool_nodes:
            archetype = self.archetype_set.get_archetype(node.archetype_id)
            if archetype is None or not archetype.side_effects:
                continue

            for side_effect_key in archetype.side_effects:
                condition = self._build_state_condition(
                    archetype.archetype_id,
                    side_effect_key,
                    node.static_params,
                    entity_bindings,
                )
                if condition:
                    state_conditions[side_effect_key] = condition
                    expected_state[side_effect_key] = condition

        if state_conditions:
            config["state"] = state_conditions
            config["expected_state"] = expected_state

        # 3. Answer verification
        answer_keywords = self._extract_answer_keywords(dag, entity_bindings)
        if answer_keywords:
            config["answer"] = answer_keywords
            config["match_mode"] = "contains"

        return config

    def _build_state_condition(
        self,
        archetype_id: str,
        state_key: str,
        static_params: Dict[str, Any],
        entity_bindings: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build a state verification condition for a mutating tool call."""
        if archetype_id == "send_email" and state_key == "sent_emails":
            condition: Dict[str, Any] = {}
            if "recipient_email" in static_params:
                condition["to"] = {"$regex": _escape_regex(static_params["recipient_email"])}
            # Check for key content in body
            primary = entity_bindings.get("primary_person", {})
            if primary.get("email"):
                condition.setdefault("to", {"$regex": _escape_regex(primary["email"])})
            if condition:
                return {"$contains": condition}

        elif archetype_id == "create_event" and state_key == "created_events":
            condition = {}
            if "event_title" in static_params:
                condition["title"] = {"$regex": f"(?i){_escape_regex(static_params['event_title'])}"}
            if condition:
                return {"$contains": condition}

        elif archetype_id == "send_slack" and state_key == "sent_slack":
            condition = {}
            if "slack_channel_required" in static_params:
                condition["channel"] = static_params["slack_channel_required"]
            if condition:
                return {"$contains": condition}

        return {}

    def _extract_answer_keywords(
        self,
        dag: TaskDAG,
        entity_bindings: Dict[str, Any],
    ) -> List[str]:
        """Extract expected keywords from terminal nodes and entity bindings."""
        keywords = []

        # Add action-related keywords from terminal nodes
        terminal_tools = dag.get_terminal_tool_nodes()
        for node in terminal_tools:
            archetype = self.archetype_set.get_archetype(node.archetype_id)
            if archetype is None:
                continue

            if archetype.archetype_id == "send_email":
                keywords.extend(["sent", "email", "reply"])
            elif archetype.archetype_id == "create_event":
                keywords.extend(["created", "event", "scheduled", "meeting"])
            elif archetype.archetype_id == "send_slack":
                keywords.extend(["sent", "message", "posted"])
            elif archetype.archetype_id in ("search_emails", "search_calendar", "search_slack"):
                keywords.extend(["found", "results"])
            elif archetype.archetype_id in ("read_email", "lookup_contact"):
                keywords.extend(["found", "information"])

        # Add entity keywords
        primary = entity_bindings.get("primary_person", {})
        if primary.get("name"):
            keywords.append(primary["name"].split()[0])  # First name

        topic = entity_bindings.get("topic", "")
        if topic:
            keywords.append(topic.split()[0])

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for kw in keywords:
            if kw.lower() not in seen:
                seen.add(kw.lower())
                unique.append(kw)

        return unique[:6]  # Cap at 6 keywords


def _escape_regex(s: str) -> str:
    """Escape special regex characters in a string."""
    import re
    return re.escape(s)
