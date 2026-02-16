"""
DAG data structures for procedural task generation.

Defines the directed acyclic graph structures that represent task execution plans.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class NodeType(Enum):
    """Types of nodes in a task DAG."""

    PROMPT_DATA = "prompt_data"  # Data from user prompt
    TOOL_CALL = "tool_call"  # Tool invocation
    COMPUTATION = "computation"  # Derived value (e.g., format string)
    CONDITIONAL = "conditional"  # Branch point
    AGGREGATION = "aggregation"  # Combine multiple sources


class EdgeType(Enum):
    """Types of edges in a task DAG."""

    DATA_FLOW = "data_flow"  # Output feeds into input
    CONTROL_FLOW = "control_flow"  # Must execute before
    CONDITIONAL_TRUE = "cond_true"
    CONDITIONAL_FALSE = "cond_false"


@dataclass
class DataSlot:
    """A named data slot — describes a piece of data flowing through the DAG."""

    name: str  # "alice_email", "meeting_time"
    data_type: str  # "string", "integer", "list"
    source_path: Optional[str] = None  # JSON path in source output: "results[0].email"


@dataclass
class DAGNode:
    """A node in the task DAG."""

    node_id: str
    node_type: NodeType
    archetype_id: Optional[str] = None  # For TOOL_CALL nodes
    static_params: Dict[str, Any] = field(default_factory=dict)  # Hardcoded param values
    outputs: List[DataSlot] = field(default_factory=list)

    # For PROMPT_DATA nodes
    prompt_key: Optional[str] = None  # e.g., "recipient_name"
    prompt_value: Optional[Any] = None  # e.g., "Alice Johnson"

    # For COMPUTATION nodes
    operation: Optional[str] = None  # "format_string", "extract", "concat"
    operation_config: Dict[str, Any] = field(default_factory=dict)

    # For CONDITIONAL nodes
    condition: Optional[str] = None  # "has_results", "is_available"
    condition_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DAGEdge:
    """An edge in the task DAG."""

    source_node_id: str
    target_node_id: str
    edge_type: EdgeType
    data_slot: Optional[DataSlot] = None  # What data flows
    target_param: Optional[str] = None  # Which param of target (semantic_role)


@dataclass
class TaskDAG:
    """A complete task execution DAG."""

    dag_id: str
    nodes: Dict[str, DAGNode]
    edges: List[DAGEdge]
    entry_nodes: List[str]  # Nodes with no incoming edges
    terminal_nodes: List[str]  # Nodes with no outgoing edges

    @property
    def depth(self) -> int:
        """Longest path through the DAG."""
        if not self.nodes:
            return 0

        # Build adjacency list
        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}
        for edge in self.edges:
            adj[edge.source_node_id].append(edge.target_node_id)

        # BFS/DFS for longest path
        memo: Dict[str, int] = {}

        def _longest(nid: str) -> int:
            if nid in memo:
                return memo[nid]
            if not adj[nid]:
                memo[nid] = 1
                return 1
            memo[nid] = 1 + max(_longest(c) for c in adj[nid])
            return memo[nid]

        return max(_longest(nid) for nid in self.entry_nodes) if self.entry_nodes else 0

    @property
    def breadth(self) -> int:
        """Maximum number of parallel independent nodes at any level."""
        if not self.nodes:
            return 0

        # Compute topological levels
        in_degree = {nid: 0 for nid in self.nodes}
        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}
        for edge in self.edges:
            adj[edge.source_node_id].append(edge.target_node_id)
            in_degree[edge.target_node_id] += 1

        # BFS by level
        current_level = [nid for nid in self.nodes if in_degree[nid] == 0]
        max_breadth = len(current_level)

        while current_level:
            next_level = []
            for nid in current_level:
                for child in adj[nid]:
                    in_degree[child] -= 1
                    if in_degree[child] == 0:
                        next_level.append(child)
            if next_level:
                max_breadth = max(max_breadth, len(next_level))
            current_level = next_level

        return max_breadth

    @property
    def tool_call_count(self) -> int:
        """Number of TOOL_CALL nodes in the DAG."""
        return sum(1 for n in self.nodes.values() if n.node_type == NodeType.TOOL_CALL)

    def get_tool_call_nodes(self) -> List[DAGNode]:
        """Get all TOOL_CALL nodes in topological order."""
        # Topological sort
        in_degree = {nid: 0 for nid in self.nodes}
        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}
        for edge in self.edges:
            adj[edge.source_node_id].append(edge.target_node_id)
            in_degree[edge.target_node_id] += 1

        queue = [nid for nid in self.nodes if in_degree[nid] == 0]
        ordered = []

        while queue:
            nid = queue.pop(0)
            node = self.nodes[nid]
            if node.node_type == NodeType.TOOL_CALL:
                ordered.append(node)
            for child in adj[nid]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        return ordered

    def get_node_inputs(self, node_id: str) -> List[DAGEdge]:
        """Get all incoming edges for a node."""
        return [e for e in self.edges if e.target_node_id == node_id]

    def get_node_outputs(self, node_id: str) -> List[DAGEdge]:
        """Get all outgoing edges from a node."""
        return [e for e in self.edges if e.source_node_id == node_id]

    def get_prompt_data_nodes(self) -> List[DAGNode]:
        """Get all PROMPT_DATA nodes."""
        return [n for n in self.nodes.values() if n.node_type == NodeType.PROMPT_DATA]

    def get_terminal_tool_nodes(self) -> List[DAGNode]:
        """Get terminal nodes that are tool calls."""
        return [
            self.nodes[nid]
            for nid in self.terminal_nodes
            if self.nodes[nid].node_type == NodeType.TOOL_CALL
        ]
