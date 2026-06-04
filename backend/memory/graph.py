"""NetworkX graph memory."""
import json
from pathlib import Path
from typing import Any, Dict, List, Set

import networkx as nx

from backend.config import NexusConfig


class NexusGraph:
    def __init__(self, config: NexusConfig):
        self.config = config
        self.graph = nx.DiGraph()
        self._load()

    def _load(self) -> None:
        path = Path(self.config.graph_db_path)
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            self.deserialize(data)

    def add_node(self, node_id: str, node_type: str, data: Dict[str, Any]) -> None:
        self.graph.add_node(node_id, type=node_type, **data)

    def add_edge(self, source: str, target: str, edge_type: str, probability: float = 1.0) -> None:
        self.graph.add_edge(source, target, type=edge_type, probability=probability)

    def find_paths(self, source_id: str, target_type: str = "loss_event", max_hops: int = 7) -> List[List[str]]:
        paths = []
        targets = [n for n, d in self.graph.nodes(data=True) if d.get("type") == target_type]
        for target in targets:
            try:
                for path in nx.all_simple_paths(self.graph, source_id, target, cutoff=max_hops):
                    paths.append(path)
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                continue
        return paths[:10]

    def get_blast_radius(self, node_id: str, max_depth: int = 3) -> Set[str]:
        if node_id not in self.graph:
            return set()
        visited = {node_id}
        frontier = [node_id]
        for _ in range(max_depth):
            next_frontier = []
            for n in frontier:
                for neighbor in self.graph.successors(n):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        next_frontier.append(neighbor)
            frontier = next_frontier
        return visited

    def get_subgraph(self, node_ids: List[str]) -> Dict[str, Any]:
        nodes = []
        edges = []
        for nid in node_ids:
            if nid in self.graph:
                d = dict(self.graph.nodes[nid])
                nodes.append({"id": nid, "type": d.get("type", "failure"), "data": d})
        seen_edges = set()
        for nid in node_ids:
            if nid not in self.graph:
                continue
            for u, v, ed in self.graph.edges(nid, data=True):
                if (u, v) not in seen_edges:
                    seen_edges.add((u, v))
                    edges.append({"source": u, "target": v, **ed})
        return {"nodes": nodes, "edges": edges}

    @staticmethod
    def _node_label(node_id: str, data: Dict[str, Any]) -> str:
        if data.get("title"):
            return str(data["title"])
        if data.get("description"):
            desc = str(data["description"])
            return desc if len(desc) <= 72 else desc[:69] + "…"
        return node_id

    def serialize(self) -> Dict[str, Any]:
        nodes = []
        for n, d in self.graph.nodes(data=True):
            payload = dict(d)
            payload["label"] = self._node_label(n, payload)
            nodes.append({"id": n, **payload})
        return {
            "nodes": nodes,
            "edges": [{"source": u, "target": v, **d} for u, v, d in self.graph.edges(data=True)],
        }

    def clear(self) -> None:
        self.graph.clear()

    def deserialize(self, data: Dict[str, Any]) -> None:
        self.graph.clear()
        for n in data.get("nodes", []):
            nid = n.pop("id")
            self.graph.add_node(nid, **n)
        for e in data.get("edges", []):
            u, v = e.pop("source"), e.pop("target")
            self.graph.add_edge(u, v, **e)

    def save(self) -> None:
        path = Path(self.config.graph_db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.serialize(), indent=2), encoding="utf-8")
