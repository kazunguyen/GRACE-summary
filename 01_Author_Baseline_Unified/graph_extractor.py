"""
GRACE Graph Extraction & Formatting Module
Formats whole CPG (AST, CFG, PDG) nodes and edges according to the author's original format
with item caps; token budget is enforced by prompt_builder.
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
    Enforces referential integrity: edges whose endpoints were truncated are excluded.
    Returns: (graph_context_str, metadata_dict)
    """
    retained_nodes = nodes[:max_nodes]

    # Collect retained node identifiers
    retained_ids = set()
    has_node_ids = False
    for idx, n in enumerate(retained_nodes):
        if isinstance(n, dict) and "id" in n:
            retained_ids.add(str(n["id"]))
            has_node_ids = True
        else:
            retained_ids.add(str(idx))

    # Filter edges so that both src and dst exist in retained_nodes
    valid_edges = []
    for e in edges:
        if isinstance(e, dict):
            src = str(e.get("start", e.get("source", e.get("src", "?"))))
            dst = str(e.get("end", e.get("target", e.get("dst", "?"))))
            if has_node_ids:
                if src in retained_ids and dst in retained_ids:
                    valid_edges.append(e)
            else:
                valid_edges.append(e)
        else:
            valid_edges.append(e)

    retained_edges = valid_edges[:max_edges]

    node_str = format_node_information(retained_nodes, max_nodes=max_nodes)
    edge_str = format_edge_information(retained_edges, max_edges=max_edges)

    context = (
        f"The node information of the function is as follows:\n{node_str}\n\n"
        f"The edge information of the function is as follows:\n{edge_str}"
    )
    meta = {
        "nodes_original": len(nodes),
        "edges_original": len(edges),
        "nodes_used": len(retained_nodes),
        "edges_used": len(retained_edges),
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
