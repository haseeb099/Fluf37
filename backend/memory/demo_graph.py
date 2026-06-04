"""Build demo traceback graph with human-readable node labels."""
from backend.memory.graph import NexusGraph
from backend.utils.synthetic_data import get_demo_failures


def _loss_node_id(failure_id: str) -> str:
    return f"loss_{failure_id.removeprefix('fail_')}"


def seed_demo_graph(graph: NexusGraph) -> None:
    """Rebuild graph from demo failures (idempotent for demo restarts)."""
    graph.clear()
    for f in get_demo_failures():
        graph.add_node(
            f.id,
            "failure",
            {
                "title": f.title,
                "description": f.description,
                "severity": f.severity,
                "source_ids": f.source_ids,
                "affected_entities": f.affected_entities,
                "dollar_loss": f.dollar_loss,
                "occurred_at": f.timestamp.isoformat(),
            },
        )
        if f.dollar_loss:
            loss_id = _loss_node_id(f.id)
            entities = ", ".join(f.affected_entities[:3])
            if len(f.affected_entities) > 3:
                entities += "…"
            graph.add_node(
                loss_id,
                "loss_event",
                {
                    "title": f"Realized loss — {f.title}",
                    "description": f.description,
                    "dollar_loss": f.dollar_loss,
                    "severity": f.severity,
                    "source_ids": f.source_ids,
                    "affected_entities": f.affected_entities,
                    "impact_summary": f"Affected: {entities}" if entities else "",
                },
            )
            prob = 0.87 if f.id == "fail_001" else 0.78 if f.id == "fail_002" else 0.72
            graph.add_edge(f.id, loss_id, "leads_to", prob)
    graph.save()
