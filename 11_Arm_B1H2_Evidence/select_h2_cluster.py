"""Select a bounded CDG-centred view of the same frozen Joern graph."""
from collections import defaultdict, deque


def select_cluster(spec, operation_score, limits, max_operations):
    nodes = {str(node["id"]): node for node in spec["nodes"]}
    edges = spec["edges"]
    scores = {
        uid: operation_score({
            "kind": node["type"],
            "properties": {"NAME": node.get("name", ""), "CODE": node.get("code", "")},
        })
        for uid, node in nodes.items()
    }
    incoming = defaultdict(list)
    cfg = defaultdict(list)
    for edge in edges:
        start, end = str(edge["start"]), str(edge["end"])
        if start == end or start not in nodes or end not in nodes:
            continue
        kind = edge["type"].upper()
        if kind == "CDG" and scores[end]:
            incoming[end].append(edge)
        elif kind == "CFG":
            cfg[start].append(end)
            cfg[end].append(start)
    seeds = sorted(incoming, key=lambda uid: -scores[uid])[:max_operations]
    if not seeds:
        return None
    selected = dict.fromkeys(seeds)
    controls = []
    for uid in seeds:
        for edge in incoming[uid]:
            start = str(edge["start"])
            if len(selected) >= limits["nodes"] and start not in selected:
                continue
            selected[start] = None
            controls.append(edge)
            if len(controls) >= min(limits["edges"], max_operations * 4):
                break
        if len(controls) >= min(limits["edges"], max_operations * 4):
            break
    queue = deque(selected)
    while queue and len(selected) < limits["nodes"]:
        for neighbor in cfg[queue.popleft()]:
            if neighbor in selected:
                continue
            selected[neighbor] = None
            queue.append(neighbor)
            if len(selected) >= limits["nodes"]:
                break
    kept = [
        edge for edge in edges
        if str(edge["start"]) in selected and str(edge["end"]) in selected
    ]
    required = {id(edge) for edge in controls}
    kept.sort(key=lambda edge: 0 if id(edge) in required else 1 if edge["type"].upper() == "CFG" else 2)
    return {"nodes": [nodes[uid] for uid in selected], "edges": kept[:limits["edges"]]}
