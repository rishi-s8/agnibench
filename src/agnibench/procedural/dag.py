"""
DAG data structures for procedural task generation.

Defines the directed acyclic graph structures that represent task execution plans.
Three first-class DAGs:
  - ControlFlowDAG: What tool calls happen in what order, and where ordering knowledge comes from.
  - DataFlowDAG: Where each piece of data originates and where it flows to.
  - ExecutionDAG (formerly TaskDAG): The combined concrete execution plan.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Existing enums (unchanged)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# New enums for the three-DAG architecture
# ---------------------------------------------------------------------------

class ControlSource(Enum):
    """Where control flow ordering knowledge comes from."""

    PROMPT = "prompt"        # Step/ordering from user prompt
    DISCOVERY = "discovery"  # Agent must discover this


class DataSource(Enum):
    """Where a piece of data originates."""

    PROMPT = "prompt"            # Value provided in user prompt
    TOOL_OUTPUT = "tool_output"  # Value from tool call result
    DERIVED = "derived"          # Computed from other data


class DataFlowNodeType(Enum):
    """Types of nodes in the DataFlowDAG."""

    PROMPT_VALUE = "prompt_value"
    TOOL_OUTPUT = "tool_output"
    TOOL_INPUT = "tool_input"


# ---------------------------------------------------------------------------
# Existing data structures (unchanged)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# ControlFlowDAG
# ---------------------------------------------------------------------------

@dataclass
class ControlFlowNode:
    """A node in the ControlFlowDAG (represents a tool call action)."""

    node_id: str
    archetype_id: str
    control_source: ControlSource
    static_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ControlFlowEdge:
    """An edge in the ControlFlowDAG (ordering constraint)."""

    source_node_id: str
    target_node_id: str
    control_source: ControlSource
    reason: Optional[str] = None  # "data_dependency" or "ordering"


@dataclass
class ControlFlowDAG:
    """DAG representing the control flow of tool call actions."""

    dag_id: str
    nodes: Dict[str, ControlFlowNode]
    edges: List[ControlFlowEdge]
    entry_nodes: List[str]
    terminal_nodes: List[str]

    @property
    def depth(self) -> int:
        """Longest path through the DAG."""
        if not self.nodes:
            return 0
        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}
        for edge in self.edges:
            adj[edge.source_node_id].append(edge.target_node_id)
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
        in_degree = {nid: 0 for nid in self.nodes}
        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}
        for edge in self.edges:
            adj[edge.source_node_id].append(edge.target_node_id)
            in_degree[edge.target_node_id] += 1
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
        return len(self.nodes)

    def get_topological_order(self) -> List[ControlFlowNode]:
        """Get nodes in topological order."""
        in_degree = {nid: 0 for nid in self.nodes}
        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}
        for edge in self.edges:
            adj[edge.source_node_id].append(edge.target_node_id)
            in_degree[edge.target_node_id] += 1
        queue = sorted([nid for nid in self.nodes if in_degree[nid] == 0])
        ordered = []
        while queue:
            nid = queue.pop(0)
            ordered.append(self.nodes[nid])
            for child in sorted(adj[nid]):
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)
        return ordered

    def to_dot(self, archetype_to_surface: Optional[Dict[str, str]] = None) -> str:
        """Generate a Graphviz DOT representation of the ControlFlowDAG."""
        lines = [
            f'digraph "{self.dag_id}_control_flow" {{',
            '  rankdir=TB;',
            '  node [fontname="Helvetica" fontsize=10];',
            '  edge [fontname="Helvetica" fontsize=8];',
            '',
        ]
        for nid, node in self.nodes.items():
            name = node.archetype_id
            if archetype_to_surface and node.archetype_id:
                name = archetype_to_surface.get(node.archetype_id, name)
            tag = "P" if node.control_source == ControlSource.PROMPT else "D"
            label = f"{name} [{tag}]"
            style = 'shape=box style="filled,rounded" fillcolor="#E3F2FD"'
            lines.append(f'  "{nid}" [{style} label="{label}"];')
        lines.append('')
        for edge in self.edges:
            tag = "P" if edge.control_source == ControlSource.PROMPT else "D"
            reason_label = f" ({edge.reason})" if edge.reason else ""
            style = f'color="#757575" style=dashed label="[{tag}]{reason_label}"'
            lines.append(f'  "{edge.source_node_id}" -> "{edge.target_node_id}" [{style}];')
        lines.append('}')
        return '\n'.join(lines)

    def to_ascii(self, archetype_to_surface: Optional[Dict[str, str]] = None) -> str:
        """Generate a simple ASCII representation of the ControlFlowDAG."""
        if not self.nodes:
            return "(empty ControlFlowDAG)"
        in_degree = {nid: 0 for nid in self.nodes}
        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}
        for edge in self.edges:
            adj[edge.source_node_id].append(edge.target_node_id)
            in_degree[edge.target_node_id] += 1
        levels: List[List[str]] = []
        current = [nid for nid in self.nodes if in_degree[nid] == 0]
        while current:
            levels.append(sorted(current))
            next_level = []
            for nid in current:
                for child in adj[nid]:
                    in_degree[child] -= 1
                    if in_degree[child] == 0:
                        next_level.append(child)
            current = next_level

        def label(nid: str) -> str:
            node = self.nodes[nid]
            name = node.archetype_id
            if archetype_to_surface and node.archetype_id:
                name = archetype_to_surface.get(node.archetype_id, name)
            tag = "P" if node.control_source == ControlSource.PROMPT else "D"
            return f"({name}) [{tag}]"

        lines = []
        for i, level in enumerate(levels):
            node_strs = [label(nid) for nid in level]
            lines.append(f"  Level {i}: {' '.join(node_strs)}")
            if i < len(levels) - 1:
                lines.append(f"           |")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# DataFlowDAG
# ---------------------------------------------------------------------------

@dataclass
class DataFlowNode:
    """A node in the DataFlowDAG."""

    node_id: str
    node_type: DataFlowNodeType
    data_source: DataSource
    # For PROMPT_VALUE
    prompt_key: Optional[str] = None
    prompt_value: Optional[Any] = None
    # For TOOL_OUTPUT
    archetype_id: Optional[str] = None
    output_slot: Optional[str] = None
    tool_node_ref: Optional[str] = None  # -> ControlFlowNode.node_id
    # For TOOL_INPUT
    param_role: Optional[str] = None


@dataclass
class DataFlowEdge:
    """An edge in the DataFlowDAG."""

    source_node_id: str
    target_node_id: str
    data_slot: DataSlot
    data_source: DataSource
    target_param: Optional[str] = None


@dataclass
class DataFlowDAG:
    """DAG representing data origins and flow between actions."""

    dag_id: str
    nodes: Dict[str, DataFlowNode]
    edges: List[DataFlowEdge]
    entry_nodes: List[str]
    terminal_nodes: List[str]

    def get_prompt_value_nodes(self) -> List[DataFlowNode]:
        """Get all PROMPT_VALUE nodes."""
        return [n for n in self.nodes.values() if n.node_type == DataFlowNodeType.PROMPT_VALUE]

    def get_tool_output_nodes(self) -> List[DataFlowNode]:
        """Get all TOOL_OUTPUT nodes."""
        return [n for n in self.nodes.values() if n.node_type == DataFlowNodeType.TOOL_OUTPUT]

    def to_dot(self, archetype_to_surface: Optional[Dict[str, str]] = None) -> str:
        """Generate a Graphviz DOT representation of the DataFlowDAG."""
        lines = [
            f'digraph "{self.dag_id}_data_flow" {{',
            '  rankdir=TB;',
            '  node [fontname="Helvetica" fontsize=10];',
            '  edge [fontname="Helvetica" fontsize=8];',
            '',
        ]
        node_styles = {
            DataFlowNodeType.PROMPT_VALUE: 'shape=note style=filled fillcolor="#E8F5E9"',
            DataFlowNodeType.TOOL_OUTPUT: 'shape=box style="filled,rounded" fillcolor="#E3F2FD"',
            DataFlowNodeType.TOOL_INPUT: 'shape=box style=filled fillcolor="#FFF3E0"',
        }
        for nid, node in self.nodes.items():
            style = node_styles.get(node.node_type, 'shape=ellipse')
            label = self._dot_node_label(node, archetype_to_surface)
            safe_label = label.replace('"', '\\"')
            lines.append(f'  "{nid}" [{style} label="{safe_label}"];')
        lines.append('')
        for edge in self.edges:
            tag = edge.data_source.value.upper()
            slot_label = edge.data_slot.name
            if edge.target_param:
                slot_label = f"{edge.data_slot.name} -> {edge.target_param}"
            style = f'color="#1565C0" style=solid label="{slot_label} [{tag}]"'
            lines.append(f'  "{edge.source_node_id}" -> "{edge.target_node_id}" [{style}];')
        lines.append('}')
        return '\n'.join(lines)

    def _dot_node_label(
        self, node: DataFlowNode, archetype_to_surface: Optional[Dict[str, str]] = None
    ) -> str:
        if node.node_type == DataFlowNodeType.PROMPT_VALUE:
            key = node.prompt_key or "data"
            val = str(node.prompt_value or "")
            if len(val) > 30:
                val = val[:27] + "..."
            return f"PROMPT\\n{key}: {val}"
        if node.node_type == DataFlowNodeType.TOOL_OUTPUT:
            name = node.archetype_id or "?"
            if archetype_to_surface and node.archetype_id:
                name = archetype_to_surface.get(node.archetype_id, name)
            slot = node.output_slot or "out"
            return f"{name}.{slot} [TOOL]"
        if node.node_type == DataFlowNodeType.TOOL_INPUT:
            name = node.archetype_id or "?"
            if archetype_to_surface and node.archetype_id:
                name = archetype_to_surface.get(node.archetype_id, name)
            role = node.param_role or "input"
            return f"{name}.{role}"
        return node.node_id

    def to_ascii(self, archetype_to_surface: Optional[Dict[str, str]] = None) -> str:
        """Generate a simple ASCII representation of the DataFlowDAG."""
        if not self.nodes:
            return "(empty DataFlowDAG)"
        in_degree = {nid: 0 for nid in self.nodes}
        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}
        for edge in self.edges:
            adj[edge.source_node_id].append(edge.target_node_id)
            in_degree[edge.target_node_id] += 1
        levels: List[List[str]] = []
        current = [nid for nid in self.nodes if in_degree[nid] == 0]
        while current:
            levels.append(sorted(current))
            next_level = []
            for nid in current:
                for child in adj[nid]:
                    in_degree[child] -= 1
                    if in_degree[child] == 0:
                        next_level.append(child)
            current = next_level

        def label(nid: str) -> str:
            node = self.nodes[nid]
            if node.node_type == DataFlowNodeType.PROMPT_VALUE:
                tag = node.data_source.value.upper()
                return f"[{node.prompt_key or 'data'}: {tag}]"
            if node.node_type == DataFlowNodeType.TOOL_OUTPUT:
                name = node.archetype_id or "?"
                if archetype_to_surface and node.archetype_id:
                    name = archetype_to_surface.get(node.archetype_id, name)
                return f"{{{name}.out}} [TOOL]"
            if node.node_type == DataFlowNodeType.TOOL_INPUT:
                name = node.archetype_id or "?"
                if archetype_to_surface and node.archetype_id:
                    name = archetype_to_surface.get(node.archetype_id, name)
                role = node.param_role or "input"
                tag = node.data_source.value.upper()
                return f"({name}.{role}) [{tag}]"
            return f"[{nid}]"

        lines = []
        for i, level in enumerate(levels):
            node_strs = [label(nid) for nid in level]
            lines.append(f"  Level {i}: {'  '.join(node_strs)}")
            if i < len(levels) - 1:
                lines.append(f"           |")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# ExecutionDAG (renamed from TaskDAG)
# ---------------------------------------------------------------------------

@dataclass
class ExecutionDAG:
    """A complete task execution DAG (union of control flow and data flow)."""

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

    def to_dot(self, archetype_to_surface: Optional[Dict[str, str]] = None) -> str:
        """
        Generate a Graphviz DOT representation of this DAG.

        Args:
            archetype_to_surface: Optional mapping from archetype_id to surface tool name.
                If provided, tool call nodes show the surface name.

        Returns:
            DOT format string that can be rendered by Graphviz or online viewers.
        """
        lines = [
            f'digraph "{self.dag_id}" {{',
            '  rankdir=TB;',
            '  node [fontname="Helvetica" fontsize=10];',
            '  edge [fontname="Helvetica" fontsize=8];',
            '',
        ]

        # Style mapping for node types
        node_styles = {
            NodeType.PROMPT_DATA: 'shape=note style=filled fillcolor="#E8F5E9"',
            NodeType.TOOL_CALL: 'shape=box style="filled,rounded" fillcolor="#E3F2FD"',
            NodeType.COMPUTATION: 'shape=diamond style=filled fillcolor="#FFF3E0"',
            NodeType.CONDITIONAL: 'shape=diamond style=filled fillcolor="#FCE4EC"',
            NodeType.AGGREGATION: 'shape=trapezium style=filled fillcolor="#F3E5F5"',
        }

        edge_styles = {
            EdgeType.DATA_FLOW: 'color="#1565C0" style=solid',
            EdgeType.CONTROL_FLOW: 'color="#757575" style=dashed',
            EdgeType.CONDITIONAL_TRUE: 'color="#2E7D32" style=bold label="true"',
            EdgeType.CONDITIONAL_FALSE: 'color="#C62828" style=bold label="false"',
        }

        # Render nodes
        for nid, node in self.nodes.items():
            style = node_styles.get(node.node_type, 'shape=ellipse')
            label = self._dot_node_label(node, archetype_to_surface)
            safe_label = label.replace('"', '\\"')
            lines.append(f'  "{nid}" [{style} label="{safe_label}"];')

        lines.append('')

        # Render edges
        for edge in self.edges:
            style = edge_styles.get(edge.edge_type, '')
            extra = ''
            if edge.data_slot and edge.edge_type == EdgeType.DATA_FLOW:
                slot_label = edge.data_slot.name
                if edge.target_param:
                    slot_label = f"{edge.data_slot.name} -> {edge.target_param}"
                extra = f' label="{slot_label}"'
            lines.append(f'  "{edge.source_node_id}" -> "{edge.target_node_id}" [{style}{extra}];')

        lines.append('}')
        return '\n'.join(lines)

    def _dot_node_label(
        self, node: DAGNode, archetype_to_surface: Optional[Dict[str, str]] = None
    ) -> str:
        """Build a human-readable label for a DOT node."""
        if node.node_type == NodeType.PROMPT_DATA:
            key = node.prompt_key or "data"
            val = str(node.prompt_value or "")
            if len(val) > 30:
                val = val[:27] + "..."
            return f"PROMPT\\n{key}: {val}"

        if node.node_type == NodeType.TOOL_CALL:
            name = node.archetype_id or "?"
            if archetype_to_surface and node.archetype_id:
                name = archetype_to_surface.get(node.archetype_id, name)
            params = []
            for k, v in list(node.static_params.items())[:3]:
                sv = str(v)
                if len(sv) > 20:
                    sv = sv[:17] + "..."
                params.append(f"{k}={sv}")
            param_str = "\\n".join(params) if params else ""
            return f"{name}\\n{param_str}" if param_str else name

        if node.node_type == NodeType.COMPUTATION:
            return f"COMPUTE\\n{node.operation or '?'}"

        if node.node_type == NodeType.CONDITIONAL:
            return f"IF\\n{node.condition or '?'}"

        if node.node_type == NodeType.AGGREGATION:
            return "AGGREGATE"

        return node.node_id

    def to_ascii(self, archetype_to_surface: Optional[Dict[str, str]] = None) -> str:
        """
        Generate a simple ASCII representation of the DAG.

        Shows nodes grouped by topological level with arrows between levels.
        """
        if not self.nodes:
            return "(empty DAG)"

        # Compute topological levels
        in_degree = {nid: 0 for nid in self.nodes}
        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}
        for edge in self.edges:
            adj[edge.source_node_id].append(edge.target_node_id)
            in_degree[edge.target_node_id] += 1

        levels: List[List[str]] = []
        current = [nid for nid in self.nodes if in_degree[nid] == 0]

        while current:
            levels.append(sorted(current))
            next_level = []
            for nid in current:
                for child in adj[nid]:
                    in_degree[child] -= 1
                    if in_degree[child] == 0:
                        next_level.append(child)
            current = next_level

        # Build labels
        def label(nid: str) -> str:
            node = self.nodes[nid]
            if node.node_type == NodeType.PROMPT_DATA:
                return f"[{node.prompt_key or 'data'}]"
            if node.node_type == NodeType.TOOL_CALL:
                name = node.archetype_id or "?"
                if archetype_to_surface and node.archetype_id:
                    name = archetype_to_surface.get(node.archetype_id, name)
                return f"({name})"
            if node.node_type == NodeType.COMPUTATION:
                return f"<{node.operation or 'compute'}>"
            if node.node_type == NodeType.CONDITIONAL:
                return f"?{node.condition or 'cond'}?"
            return f"[{nid}]"

        lines = []
        for i, level in enumerate(levels):
            node_strs = [label(nid) for nid in level]
            row = "  ".join(node_strs)
            lines.append(f"  Level {i}: {row}")
            if i < len(levels) - 1:
                # Show arrows
                arrows = []
                for nid in level:
                    src_label = label(nid)
                    for child in adj.get(nid, []):
                        if child in levels[i + 1]:
                            arrows.append(f"{src_label} -> {label(child)}")
                if arrows:
                    for a in arrows:
                        lines.append(f"           {a}")
                else:
                    lines.append(f"           |")

        return "\n".join(lines)


# Backward compatibility alias
TaskDAG = ExecutionDAG


# ---------------------------------------------------------------------------
# TaskDAGBundle — bundles all three DAGs
# ---------------------------------------------------------------------------

@dataclass
class TaskDAGBundle:
    """Bundles the three DAGs: control flow, data flow, and execution."""

    control_flow: ControlFlowDAG
    data_flow: DataFlowDAG
    execution: ExecutionDAG

    @property
    def dag_id(self) -> str:
        return self.execution.dag_id

    @property
    def depth(self) -> int:
        return self.execution.depth

    @property
    def breadth(self) -> int:
        return self.execution.breadth

    @property
    def tool_call_count(self) -> int:
        return self.execution.tool_call_count
