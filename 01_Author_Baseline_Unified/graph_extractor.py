"""
GRACE Graph Extraction & Formatting Module
Formats whole CPG (AST, CFG, PDG) nodes and edges according to the author's original format
and enforces the contract cap (max 40 nodes, max 80 edges).
"""

from __future__ import annotations

from typing import List, Dict, Any, Tuple


def format_node_information(nodes: List[Any], max_nodes: int = 40) -> str:
    """Format nodes into 'Node {id}: ({type}) \'{code}\'' strings."""
    if not nodes:
        return "[No Node Information Available]"

    lines = []
    for idx, n in enumerate(nodes[:max_nodes]):
        if isinstance(n, dict):
            n_id = n.get("id", idx)
            n_type = n.get("type", n.get("label", "Node"))
            n_code = n.get("code", "").strip()
            if n_code:
                snippet = n_code[:40] + "..." if len(n_code) > 40 else n_code
                lines.append(f"Node {n_id}: ({n_type}) '{snippet}'")
            else:
                lines.append(f"Node {n_id}: ({n_type})")
        else:
            lines.append(f"Node {idx}: {str(n)}")

    return "\n".join(lines)


def format_edge_information(edges: List[Any], max_edges: int = 80) -> str:
    """Format edges into 'Edge: Node {src} -> {type} -> Node {dst}' strings."""
    if not edges:
        return "[No Edge Information Available]"

    lines = []
    for idx, e in enumerate(edges[:max_edges]):
        if isinstance(e, dict):
            src = e.get("start", e.get("source", e.get("src", "?")))
            dst = e.get("end", e.get("target", e.get("dst", "?")))
            e_type = e.get("type", e.get("label", "CONNECTED_TO"))
            lines.append(f"Edge: Node {src} -> {e_type} -> Node {dst}")
        else:
            lines.append(f"Edge {idx}: {str(e)}")

    return "\n".join(lines)


def format_graph_context(
    nodes: List[Any],
    edges: List[Any],
    max_nodes: int = 40,
    max_edges: int = 80,
) -> Tuple[str, Dict[str, int]]:
    """
    Format whole CPG context for prompt insertion.
    Returns: (graph_context_str, metadata_dict)
    """
    node_str = format_node_information(nodes, max_nodes=max_nodes)
    edge_str = format_edge_information(edges, max_edges=max_edges)

    context = (
        f"The node information of the function is as follows:\n{node_str}\n\n"
        f"The edge information of the function is as follows:\n{edge_str}"
    )
    meta = {
        "nodes_original": len(nodes),
        "edges_original": len(edges),
        "nodes_used": min(len(nodes), max_nodes),
        "edges_used": min(len(edges), max_edges),
    }
    return context, meta


def serialize_ast_representation(nodes: List[Any], edges: List[Any]) -> str:
    """
    Serializes AST node types for syntactic Levenshtein/SequenceMatcher comparison.
    Extracts AST-typed nodes or sequential node types.
    """
    if not nodes:
        return "SourceUnit"

    ast_tokens = []
    for n in nodes:
        if isinstance(n, dict):
            n_type = n.get("type", n.get("label", "Node"))
            ast_tokens.append(str(n_type))
        else:
            ast_tokens.append(str(n))
    return " ".join(ast_tokens)
