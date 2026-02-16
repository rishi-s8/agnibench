"""
DAG generator that builds task DAGs by composing micro-patterns.

Micro-patterns are small subgraph templates that represent real task structures.
The generator selects and composes patterns based on difficulty profiles.
"""

import random
from typing import Any, Dict, List, Optional, Tuple

from agnibench.core.abstractions import DifficultyLevel, InformationFlow
from agnibench.procedural.archetypes import DomainArchetypeSet, ToolArchetype
from agnibench.procedural.dag import (
    ControlFlowDAG,
    ControlFlowEdge,
    ControlFlowNode,
    ControlSource,
    DAGEdge,
    DAGNode,
    DataFlowDAG,
    DataFlowEdge,
    DataFlowNode,
    DataFlowNodeType,
    DataSlot,
    DataSource,
    EdgeType,
    ExecutionDAG,
    NodeType,
    TaskDAGBundle,
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
    Generates TaskDAGBundles from difficulty profiles and domain archetypes.

    Composes micro-patterns into DAGs, assigns tool archetypes to pattern slots,
    and wires data edges between them. Then splits the execution DAG into
    separate control flow and data flow DAGs.
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

    def _build_execution_dag(self, difficulty: DifficultyLevel, dag_id: str) -> Tuple[ExecutionDAG, DifficultyProfile]:
        """Build an ExecutionDAG (the core generation logic, unchanged from original)."""
        profile = get_profile(difficulty)

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

        exec_dag = ExecutionDAG(
            dag_id=dag_id,
            nodes=all_nodes,
            edges=all_edges,
            entry_nodes=final_entry,
            terminal_nodes=final_terminal,
        )
        return exec_dag, profile

    def _split_into_bundle(self, execution_dag: ExecutionDAG, profile: DifficultyProfile) -> TaskDAGBundle:
        """
        Split an ExecutionDAG into a TaskDAGBundle with separate
        ControlFlowDAG, DataFlowDAG, and the original ExecutionDAG.
        """
        info_flow = profile.information_flow

        # Determine control source based on information_flow
        if info_flow == InformationFlow.TOOL_DISCOVERY:
            control_source = ControlSource.DISCOVERY
        else:
            control_source = ControlSource.PROMPT

        # Determine data source for prompt-provided data
        if info_flow == InformationFlow.PROMPT_FULL:
            prompt_data_source = DataSource.PROMPT
        else:
            prompt_data_source = DataSource.TOOL_OUTPUT

        # --- Build ControlFlowDAG ---
        # Extract all TOOL_CALL nodes
        tool_node_ids = set()
        cf_nodes: Dict[str, ControlFlowNode] = {}
        for nid, node in execution_dag.nodes.items():
            if node.node_type == NodeType.TOOL_CALL:
                tool_node_ids.add(nid)
                cf_nodes[nid] = ControlFlowNode(
                    node_id=nid,
                    archetype_id=node.archetype_id or "",
                    control_source=control_source,
                    static_params=dict(node.static_params),
                )

        # Find edges between TOOL_CALL nodes (direct + transitive through PROMPT_DATA)
        # Build adjacency from execution DAG
        exec_adj: Dict[str, List[str]] = {nid: [] for nid in execution_dag.nodes}
        for edge in execution_dag.edges:
            exec_adj[edge.source_node_id].append(edge.target_node_id)

        cf_edges: List[ControlFlowEdge] = []
        seen_cf_edges = set()
        for edge in execution_dag.edges:
            src = edge.source_node_id
            tgt = edge.target_node_id
            if src in tool_node_ids and tgt in tool_node_ids:
                key = (src, tgt)
                if key not in seen_cf_edges:
                    seen_cf_edges.add(key)
                    reason = "data_dependency" if edge.edge_type == EdgeType.DATA_FLOW else "ordering"
                    cf_edges.append(ControlFlowEdge(
                        source_node_id=src,
                        target_node_id=tgt,
                        control_source=control_source,
                        reason=reason,
                    ))
            elif src in tool_node_ids and tgt not in tool_node_ids:
                # Transitive: tool -> non-tool -> ... -> tool
                # BFS to find tool successors
                visited = set()
                queue = [tgt]
                while queue:
                    cur = queue.pop(0)
                    if cur in visited:
                        continue
                    visited.add(cur)
                    if cur in tool_node_ids and cur != src:
                        key = (src, cur)
                        if key not in seen_cf_edges:
                            seen_cf_edges.add(key)
                            cf_edges.append(ControlFlowEdge(
                                source_node_id=src,
                                target_node_id=cur,
                                control_source=control_source,
                                reason="data_dependency",
                            ))
                    elif cur not in tool_node_ids:
                        for child in exec_adj.get(cur, []):
                            queue.append(child)
            elif src not in tool_node_ids and tgt in tool_node_ids:
                # Transitive: non-tool sources -> tool target
                # Find tool predecessors by looking at who feeds into this non-tool node
                # (handled by the src-in-tool_node_ids case above via BFS)
                pass

        # Compute entry/terminal for control flow
        cf_target_set = {e.target_node_id for e in cf_edges}
        cf_source_set = {e.source_node_id for e in cf_edges}
        cf_entry = [nid for nid in cf_nodes if nid not in cf_target_set]
        cf_terminal = [nid for nid in cf_nodes if nid not in cf_source_set]

        control_flow_dag = ControlFlowDAG(
            dag_id=execution_dag.dag_id,
            nodes=cf_nodes,
            edges=cf_edges,
            entry_nodes=cf_entry,
            terminal_nodes=cf_terminal,
        )

        # --- Build DataFlowDAG ---
        df_nodes: Dict[str, DataFlowNode] = {}
        df_edges: List[DataFlowEdge] = []
        df_counter = 0

        def _df_id(prefix: str) -> str:
            nonlocal df_counter
            df_counter += 1
            return f"df_{prefix}_{df_counter}"

        # Track tool output nodes we create (keyed by execution_dag node_id)
        tool_output_df_ids: Dict[str, str] = {}
        # Track tool input nodes (keyed by (target_node_id, target_param))
        tool_input_df_ids: Dict[str, str] = {}

        # Create TOOL_OUTPUT nodes for each TOOL_CALL node's outputs
        for nid, node in execution_dag.nodes.items():
            if node.node_type == NodeType.TOOL_CALL:
                for output_slot in node.outputs:
                    df_nid = _df_id("tout")
                    df_nodes[df_nid] = DataFlowNode(
                        node_id=df_nid,
                        node_type=DataFlowNodeType.TOOL_OUTPUT,
                        data_source=DataSource.TOOL_OUTPUT,
                        archetype_id=node.archetype_id,
                        output_slot=output_slot.name,
                        tool_node_ref=nid,
                    )
                    tool_output_df_ids[nid] = df_nid

        # Create PROMPT_VALUE nodes for PROMPT_DATA nodes
        prompt_value_df_ids: Dict[str, str] = {}
        for nid, node in execution_dag.nodes.items():
            if node.node_type == NodeType.PROMPT_DATA:
                df_nid = _df_id("pval")
                df_nodes[df_nid] = DataFlowNode(
                    node_id=df_nid,
                    node_type=DataFlowNodeType.PROMPT_VALUE,
                    data_source=prompt_data_source,
                    prompt_key=node.prompt_key,
                    prompt_value=node.prompt_value,
                )
                prompt_value_df_ids[nid] = df_nid

        # Process DATA_FLOW edges to create TOOL_INPUT nodes and data flow edges
        for edge in execution_dag.edges:
            if edge.edge_type != EdgeType.DATA_FLOW:
                continue

            src = edge.source_node_id
            tgt = edge.target_node_id
            src_node = execution_dag.nodes[src]
            tgt_node = execution_dag.nodes[tgt]

            if tgt_node.node_type != NodeType.TOOL_CALL:
                continue

            # Create a TOOL_INPUT node for the target
            df_input_nid = _df_id("tin")
            tgt_archetype_id = tgt_node.archetype_id or ""
            # Determine data source for this input
            if src_node.node_type == NodeType.PROMPT_DATA:
                input_data_source = prompt_data_source
            else:
                input_data_source = DataSource.TOOL_OUTPUT

            df_nodes[df_input_nid] = DataFlowNode(
                node_id=df_input_nid,
                node_type=DataFlowNodeType.TOOL_INPUT,
                data_source=input_data_source,
                archetype_id=tgt_archetype_id,
                param_role=edge.target_param,
                tool_node_ref=tgt,
            )
            tool_input_df_ids[f"{tgt}_{edge.target_param}"] = df_input_nid

            # Create edge from source to input
            if src_node.node_type == NodeType.PROMPT_DATA and src in prompt_value_df_ids:
                source_df_nid = prompt_value_df_ids[src]
                df_edges.append(DataFlowEdge(
                    source_node_id=source_df_nid,
                    target_node_id=df_input_nid,
                    data_slot=edge.data_slot or DataSlot(name="data", data_type="string"),
                    data_source=prompt_data_source,
                    target_param=edge.target_param,
                ))
            elif src_node.node_type == NodeType.TOOL_CALL and src in tool_output_df_ids:
                source_df_nid = tool_output_df_ids[src]
                df_edges.append(DataFlowEdge(
                    source_node_id=source_df_nid,
                    target_node_id=df_input_nid,
                    data_slot=edge.data_slot or DataSlot(name="data", data_type="string"),
                    data_source=DataSource.TOOL_OUTPUT,
                    target_param=edge.target_param,
                ))

        # Compute entry/terminal for data flow
        df_target_set = {e.target_node_id for e in df_edges}
        df_source_set = {e.source_node_id for e in df_edges}
        df_entry = [nid for nid in df_nodes if nid not in df_target_set]
        df_terminal = [nid for nid in df_nodes if nid not in df_source_set]

        data_flow_dag = DataFlowDAG(
            dag_id=execution_dag.dag_id,
            nodes=df_nodes,
            edges=df_edges,
            entry_nodes=df_entry,
            terminal_nodes=df_terminal,
        )

        return TaskDAGBundle(
            control_flow=control_flow_dag,
            data_flow=data_flow_dag,
            execution=execution_dag,
        )

    def generate(self, difficulty: DifficultyLevel, dag_id: str = None) -> TaskDAGBundle:
        """
        Generate a TaskDAGBundle for the given difficulty level.

        Args:
            difficulty: Target difficulty level
            dag_id: Optional ID for the DAG (auto-generated if None)

        Returns:
            A TaskDAGBundle containing control flow, data flow, and execution DAGs
        """
        if dag_id is None:
            dag_id = f"dag_{self.seed}_{difficulty.value}_{self.rng.randint(0, 99999)}"

        exec_dag, profile = self._build_execution_dag(difficulty, dag_id)
        return self._split_into_bundle(exec_dag, profile)

    def generate_batch(
        self,
        difficulty: DifficultyLevel,
        count: int,
    ) -> List[TaskDAGBundle]:
        """Generate multiple TaskDAGBundles for a difficulty level."""
        return [
            self.generate(difficulty, dag_id=f"dag_{self.seed}_{difficulty.value}_{i}")
            for i in range(count)
        ]
