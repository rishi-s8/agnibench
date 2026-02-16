"""
DAG generator that builds task DAGs by composing micro-patterns.

Micro-patterns are small subgraph templates that represent real task structures.
The generator selects and composes patterns based on difficulty profiles.
"""

import random
from typing import Any, Dict, List, Optional, Tuple

from agnibench.core.abstractions import DifficultyLevel
from agnibench.procedural.archetypes import DomainArchetypeSet, ToolArchetype
from agnibench.procedural.dag import (
    DAGEdge,
    DAGNode,
    DataSlot,
    EdgeType,
    NodeType,
    TaskDAG,
)
from agnibench.procedural.difficulty import DifficultyProfile, get_profile


class MicroPattern:
    """A micro-pattern — a small subgraph template representing a task structure."""

    def __init__(self, name: str, min_tools: int, requires_categories: List[str]):
        self.name = name
        self.min_tools = min_tools
        self.requires_categories = requires_categories


# Micro-pattern definitions
LINEAR_CHAIN = MicroPattern("linear_chain", min_tools=2, requires_categories=["query", "lookup"])
LOOKUP_THEN_ACT = MicroPattern("lookup_then_act", min_tools=3, requires_categories=["query", "lookup", "mutate"])
FAN_OUT = MicroPattern("fan_out", min_tools=3, requires_categories=["query"])
FAN_IN = MicroPattern("fan_in", min_tools=3, requires_categories=["query", "mutate"])
CROSS_REFERENCE = MicroPattern("cross_reference", min_tools=3, requires_categories=["query", "mutate"])
CONDITIONAL_BRANCH = MicroPattern("conditional_branch", min_tools=3, requires_categories=["query", "mutate"])
READ_MODIFY_WRITE = MicroPattern("read_modify_write", min_tools=3, requires_categories=["query", "mutate"])


class DAGGenerator:
    """
    Generates TaskDAGs from difficulty profiles and domain archetypes.

    Composes micro-patterns into DAGs, assigns tool archetypes to pattern slots,
    and wires data edges between them.
    """

    def __init__(self, archetype_set: DomainArchetypeSet, seed: int):
        self.archetype_set = archetype_set
        self.seed = seed
        self.rng = random.Random(seed)
        self._node_counter = 0

    def _next_node_id(self, prefix: str = "n") -> str:
        """Generate unique node IDs."""
        self._node_counter += 1
        return f"{prefix}_{self._node_counter}"

    def _pick_archetype(self, category: str, exclude: Optional[List[str]] = None) -> ToolArchetype:
        """Pick a random archetype from a category."""
        candidates = self.archetype_set.get_archetypes_by_category(category)
        if exclude:
            candidates = [a for a in candidates if a.archetype_id not in exclude]
        if not candidates:
            # Fallback: pick any archetype
            candidates = self.archetype_set.archetypes
        return self.rng.choice(candidates)

    def _pick_mutating_archetype(self, exclude: Optional[List[str]] = None) -> ToolArchetype:
        """Pick a random mutating archetype (one with side effects)."""
        candidates = self.archetype_set.get_mutating_archetypes()
        if exclude:
            candidates = [a for a in candidates if a.archetype_id not in exclude]
        if not candidates:
            candidates = self.archetype_set.get_mutating_archetypes()
        return self.rng.choice(candidates)

    def _build_linear_chain(self, num_tools: int) -> Tuple[List[DAGNode], List[DAGEdge], List[str], List[str]]:
        """Build a LINEAR_CHAIN pattern: A -> B -> C ..."""
        nodes: List[DAGNode] = []
        edges: List[DAGEdge] = []
        used_archetypes: List[str] = []

        # Start with a query/lookup tool
        first_archetype = self._pick_archetype("query")
        used_archetypes.append(first_archetype.archetype_id)

        first_node = DAGNode(
            node_id=self._next_node_id("tool"),
            node_type=NodeType.TOOL_CALL,
            archetype_id=first_archetype.archetype_id,
            outputs=[DataSlot(name="result", data_type="dict", source_path="results[0]")],
        )
        nodes.append(first_node)

        prev_node = first_node
        for i in range(1, num_tools):
            if i == num_tools - 1:
                # Last in chain — mutating action or lookup
                archetype = self._pick_archetype(
                    self.rng.choice(["lookup", "mutate"]),
                    exclude=used_archetypes,
                )
            else:
                archetype = self._pick_archetype("lookup", exclude=used_archetypes)
            used_archetypes.append(archetype.archetype_id)

            node = DAGNode(
                node_id=self._next_node_id("tool"),
                node_type=NodeType.TOOL_CALL,
                archetype_id=archetype.archetype_id,
                outputs=[DataSlot(name="result", data_type="dict")],
            )
            nodes.append(node)

            # Data flow edge from previous node
            required_params = archetype.get_required_params()
            target_param = required_params[0].semantic_role if required_params else None
            edges.append(DAGEdge(
                source_node_id=prev_node.node_id,
                target_node_id=node.node_id,
                edge_type=EdgeType.DATA_FLOW,
                data_slot=DataSlot(name="chain_data", data_type="string"),
                target_param=target_param,
            ))
            prev_node = node

        entry_nodes = [nodes[0].node_id]
        terminal_nodes = [nodes[-1].node_id]
        return nodes, edges, entry_nodes, terminal_nodes

    def _build_lookup_then_act(self) -> Tuple[List[DAGNode], List[DAGEdge], List[str], List[str]]:
        """Build LOOKUP_THEN_ACT pattern: search -> read_detail -> mutate."""
        nodes: List[DAGNode] = []
        edges: List[DAGEdge] = []

        # Step 1: Search
        search_arch = self._pick_archetype("query")
        search_node = DAGNode(
            node_id=self._next_node_id("tool"),
            node_type=NodeType.TOOL_CALL,
            archetype_id=search_arch.archetype_id,
            outputs=[DataSlot(name="search_results", data_type="list", source_path="results[0].id")],
        )
        nodes.append(search_node)

        # Step 2: Read detail
        lookup_arch = self._pick_archetype("lookup")
        lookup_node = DAGNode(
            node_id=self._next_node_id("tool"),
            node_type=NodeType.TOOL_CALL,
            archetype_id=lookup_arch.archetype_id,
            outputs=[DataSlot(name="detail", data_type="dict")],
        )
        nodes.append(lookup_node)

        required_params = lookup_arch.get_required_params()
        edges.append(DAGEdge(
            source_node_id=search_node.node_id,
            target_node_id=lookup_node.node_id,
            edge_type=EdgeType.DATA_FLOW,
            data_slot=DataSlot(name="entity_id", data_type="string", source_path="results[0].id"),
            target_param=required_params[0].semantic_role if required_params else None,
        ))

        # Step 3: Act
        act_arch = self._pick_mutating_archetype()
        act_node = DAGNode(
            node_id=self._next_node_id("tool"),
            node_type=NodeType.TOOL_CALL,
            archetype_id=act_arch.archetype_id,
            outputs=[DataSlot(name="action_result", data_type="dict")],
        )
        nodes.append(act_node)

        edges.append(DAGEdge(
            source_node_id=lookup_node.node_id,
            target_node_id=act_node.node_id,
            edge_type=EdgeType.DATA_FLOW,
            data_slot=DataSlot(name="detail_data", data_type="dict"),
            target_param=None,  # Will be resolved during data generation
        ))

        return nodes, edges, [search_node.node_id], [act_node.node_id]

    def _build_fan_out(self, num_parallel: int = 2) -> Tuple[List[DAGNode], List[DAGEdge], List[str], List[str]]:
        """Build FAN_OUT pattern: A -> [B, C, D] (parallel queries)."""
        nodes: List[DAGNode] = []
        edges: List[DAGEdge] = []
        used = []

        terminal_ids = []
        for _ in range(num_parallel):
            arch = self._pick_archetype("query", exclude=used)
            used.append(arch.archetype_id)
            node = DAGNode(
                node_id=self._next_node_id("tool"),
                node_type=NodeType.TOOL_CALL,
                archetype_id=arch.archetype_id,
                outputs=[DataSlot(name="result", data_type="dict")],
            )
            nodes.append(node)
            terminal_ids.append(node.node_id)

        entry_ids = [n.node_id for n in nodes]
        return nodes, edges, entry_ids, terminal_ids

    def _build_fan_in(self, num_sources: int = 2) -> Tuple[List[DAGNode], List[DAGEdge], List[str], List[str]]:
        """Build FAN_IN pattern: [A, B] -> C (aggregate then act)."""
        nodes: List[DAGNode] = []
        edges: List[DAGEdge] = []
        entry_ids = []
        used = []

        # Source nodes
        for _ in range(num_sources):
            arch = self._pick_archetype("query", exclude=used)
            used.append(arch.archetype_id)
            node = DAGNode(
                node_id=self._next_node_id("tool"),
                node_type=NodeType.TOOL_CALL,
                archetype_id=arch.archetype_id,
                outputs=[DataSlot(name="result", data_type="dict")],
            )
            nodes.append(node)
            entry_ids.append(node.node_id)

        # Aggregation/action node
        act_arch = self._pick_mutating_archetype()
        act_node = DAGNode(
            node_id=self._next_node_id("tool"),
            node_type=NodeType.TOOL_CALL,
            archetype_id=act_arch.archetype_id,
            outputs=[DataSlot(name="action_result", data_type="dict")],
        )
        nodes.append(act_node)

        for source_node in nodes[:-1]:
            edges.append(DAGEdge(
                source_node_id=source_node.node_id,
                target_node_id=act_node.node_id,
                edge_type=EdgeType.DATA_FLOW,
                data_slot=DataSlot(name="source_data", data_type="dict"),
            ))

        return nodes, edges, entry_ids, [act_node.node_id]

    def _build_cross_reference(self) -> Tuple[List[DAGNode], List[DAGEdge], List[str], List[str]]:
        """Build CROSS_REFERENCE: [source_A, source_B] -> compare -> act."""
        nodes: List[DAGNode] = []
        edges: List[DAGEdge] = []

        # Two query sources
        arch_a = self._pick_archetype("query")
        node_a = DAGNode(
            node_id=self._next_node_id("tool"),
            node_type=NodeType.TOOL_CALL,
            archetype_id=arch_a.archetype_id,
            outputs=[DataSlot(name="source_a", data_type="dict")],
        )
        nodes.append(node_a)

        arch_b = self._pick_archetype("query", exclude=[arch_a.archetype_id])
        node_b = DAGNode(
            node_id=self._next_node_id("tool"),
            node_type=NodeType.TOOL_CALL,
            archetype_id=arch_b.archetype_id,
            outputs=[DataSlot(name="source_b", data_type="dict")],
        )
        nodes.append(node_b)

        # Lookup/detail step that uses info from both
        lookup_arch = self._pick_archetype("lookup")
        lookup_node = DAGNode(
            node_id=self._next_node_id("tool"),
            node_type=NodeType.TOOL_CALL,
            archetype_id=lookup_arch.archetype_id,
            outputs=[DataSlot(name="cross_ref_result", data_type="dict")],
        )
        nodes.append(lookup_node)

        edges.append(DAGEdge(
            source_node_id=node_a.node_id,
            target_node_id=lookup_node.node_id,
            edge_type=EdgeType.DATA_FLOW,
            data_slot=DataSlot(name="ref_a", data_type="dict"),
        ))
        edges.append(DAGEdge(
            source_node_id=node_b.node_id,
            target_node_id=lookup_node.node_id,
            edge_type=EdgeType.DATA_FLOW,
            data_slot=DataSlot(name="ref_b", data_type="dict"),
        ))

        # Action node
        act_arch = self._pick_mutating_archetype()
        act_node = DAGNode(
            node_id=self._next_node_id("tool"),
            node_type=NodeType.TOOL_CALL,
            archetype_id=act_arch.archetype_id,
            outputs=[DataSlot(name="action_result", data_type="dict")],
        )
        nodes.append(act_node)

        edges.append(DAGEdge(
            source_node_id=lookup_node.node_id,
            target_node_id=act_node.node_id,
            edge_type=EdgeType.DATA_FLOW,
            data_slot=DataSlot(name="cross_ref_data", data_type="dict"),
        ))

        return nodes, edges, [node_a.node_id, node_b.node_id], [act_node.node_id]

    def _build_read_modify_write(self) -> Tuple[List[DAGNode], List[DAGEdge], List[str], List[str]]:
        """Build READ_MODIFY_WRITE: read -> compute -> write."""
        nodes: List[DAGNode] = []
        edges: List[DAGEdge] = []

        # Read step (query or lookup)
        read_arch = self._pick_archetype(self.rng.choice(["query", "lookup"]))
        read_node = DAGNode(
            node_id=self._next_node_id("tool"),
            node_type=NodeType.TOOL_CALL,
            archetype_id=read_arch.archetype_id,
            outputs=[DataSlot(name="read_data", data_type="dict")],
        )
        nodes.append(read_node)

        # Write step (mutate)
        write_arch = self._pick_mutating_archetype()
        write_node = DAGNode(
            node_id=self._next_node_id("tool"),
            node_type=NodeType.TOOL_CALL,
            archetype_id=write_arch.archetype_id,
            outputs=[DataSlot(name="write_result", data_type="dict")],
        )
        nodes.append(write_node)

        edges.append(DAGEdge(
            source_node_id=read_node.node_id,
            target_node_id=write_node.node_id,
            edge_type=EdgeType.DATA_FLOW,
            data_slot=DataSlot(name="modify_data", data_type="dict"),
        ))

        return nodes, edges, [read_node.node_id], [write_node.node_id]

    def _select_patterns(self, profile: DifficultyProfile) -> List[str]:
        """Select micro-patterns based on difficulty profile."""
        target_tools = self.rng.randint(profile.min_tool_calls, profile.max_tool_calls)

        patterns = []
        current_tools = 0

        # Always start with a base pattern
        if target_tools <= 3:
            if target_tools == 2:
                patterns.append("read_modify_write")
                current_tools += 2
            else:
                patterns.append("lookup_then_act")
                current_tools += 3
        else:
            # Pick a primary pattern
            primary_options = ["lookup_then_act"]
            if self.rng.random() < profile.p_cross_reference:
                primary_options.append("cross_reference")
            patterns.append(self.rng.choice(primary_options))
            current_tools += 4 if patterns[0] == "cross_reference" else 3

        # Add more patterns until we reach target tool count
        while current_tools < target_tools:
            remaining = target_tools - current_tools
            if remaining >= 4 and self.rng.random() < profile.p_cross_reference:
                patterns.append("cross_reference")
                current_tools += 4
            elif remaining >= 3:
                choice = self.rng.choice(["lookup_then_act", "fan_in"])
                patterns.append(choice)
                current_tools += 3
            elif remaining >= 2:
                patterns.append("read_modify_write")
                current_tools += 2
            elif remaining == 1:
                # Upgrade the last read_modify_write to lookup_then_act to absorb the extra tool
                if patterns and patterns[-1] == "read_modify_write":
                    patterns[-1] = "lookup_then_act"
                    current_tools += 1
                else:
                    # Add a read_modify_write (overshoots by 1, acceptable)
                    patterns.append("read_modify_write")
                    current_tools += 2
                break
            else:
                break

        # Ensure we meet the minimum tool call count
        while current_tools < profile.min_tool_calls:
            shortfall = profile.min_tool_calls - current_tools
            if shortfall >= 3:
                patterns.append("lookup_then_act")
                current_tools += 3
            else:
                patterns.append("read_modify_write")
                current_tools += 2

        return patterns

    def _add_prompt_data_nodes(
        self,
        dag_nodes: Dict[str, DAGNode],
        dag_edges: List[DAGEdge],
        entry_nodes: List[str],
        profile: DifficultyProfile,
    ) -> None:
        """Add PROMPT_DATA nodes for entry points based on information flow."""
        for entry_id in entry_nodes:
            node = dag_nodes[entry_id]
            if node.node_type == NodeType.TOOL_CALL:
                archetype = self.archetype_set.get_archetype(node.archetype_id)
                if archetype is None:
                    continue

                # Add prompt data for required params based on information_flow
                for param in archetype.parameters:
                    if not param.required:
                        continue

                    # For PROMPT_FULL, provide data directly in prompt
                    # For others, some data comes from tools (no prompt node)
                    if profile.information_flow.value == "prompt_full" or param.required:
                        prompt_node = DAGNode(
                            node_id=self._next_node_id("prompt"),
                            node_type=NodeType.PROMPT_DATA,
                            prompt_key=param.semantic_role,
                            outputs=[DataSlot(name=param.semantic_role, data_type=param.data_type)],
                        )
                        dag_nodes[prompt_node.node_id] = prompt_node
                        dag_edges.append(DAGEdge(
                            source_node_id=prompt_node.node_id,
                            target_node_id=entry_id,
                            edge_type=EdgeType.DATA_FLOW,
                            data_slot=DataSlot(name=param.semantic_role, data_type=param.data_type),
                            target_param=param.semantic_role,
                        ))

    def generate(self, difficulty: DifficultyLevel, dag_id: str = None) -> TaskDAG:
        """
        Generate a TaskDAG for the given difficulty level.

        Args:
            difficulty: Target difficulty level
            dag_id: Optional ID for the DAG (auto-generated if None)

        Returns:
            A TaskDAG ready for data generation and prompt generation
        """
        profile = get_profile(difficulty)
        if dag_id is None:
            dag_id = f"dag_{self.seed}_{difficulty.value}_{self.rng.randint(0, 99999)}"

        patterns = self._select_patterns(profile)

        # Build all pattern subgraphs
        all_nodes: Dict[str, DAGNode] = {}
        all_edges: List[DAGEdge] = []
        all_entry: List[str] = []
        all_terminal: List[str] = []

        prev_terminal: Optional[List[str]] = None

        for pattern_name in patterns:
            if pattern_name == "linear_chain":
                num = self.rng.randint(2, min(3, profile.max_tool_calls))
                nodes, edges, entry, terminal = self._build_linear_chain(num)
            elif pattern_name == "lookup_then_act":
                nodes, edges, entry, terminal = self._build_lookup_then_act()
            elif pattern_name == "fan_out":
                breadth = self.rng.randint(*profile.breadth_range)
                nodes, edges, entry, terminal = self._build_fan_out(max(2, breadth))
            elif pattern_name == "fan_in":
                breadth = self.rng.randint(*profile.breadth_range)
                nodes, edges, entry, terminal = self._build_fan_in(max(2, breadth))
            elif pattern_name == "cross_reference":
                nodes, edges, entry, terminal = self._build_cross_reference()
            elif pattern_name == "read_modify_write":
                nodes, edges, entry, terminal = self._build_read_modify_write()
            else:
                continue

            # Register nodes
            for node in nodes:
                all_nodes[node.node_id] = node
            all_edges.extend(edges)

            # Wire patterns together: previous terminal -> current entry
            if prev_terminal is not None:
                for prev_id in prev_terminal:
                    for entry_id in entry:
                        all_edges.append(DAGEdge(
                            source_node_id=prev_id,
                            target_node_id=entry_id,
                            edge_type=EdgeType.CONTROL_FLOW,
                        ))
            else:
                all_entry.extend(entry)

            prev_terminal = terminal

        if prev_terminal:
            all_terminal = prev_terminal

        # Add prompt data nodes
        self._add_prompt_data_nodes(all_nodes, all_edges, all_entry, profile)

        # Recompute entry nodes (nodes with no incoming edges)
        target_nodes = {e.target_node_id for e in all_edges}
        final_entry = [nid for nid in all_nodes if nid not in target_nodes]

        # Recompute terminal nodes (nodes with no outgoing edges)
        source_nodes = {e.source_node_id for e in all_edges}
        final_terminal = [nid for nid in all_nodes if nid not in source_nodes]

        return TaskDAG(
            dag_id=dag_id,
            nodes=all_nodes,
            edges=all_edges,
            entry_nodes=final_entry,
            terminal_nodes=final_terminal,
        )

    def generate_batch(
        self,
        difficulty: DifficultyLevel,
        count: int,
    ) -> List[TaskDAG]:
        """Generate multiple DAGs for a difficulty level."""
        return [
            self.generate(difficulty, dag_id=f"dag_{self.seed}_{difficulty.value}_{i}")
            for i in range(count)
        ]
