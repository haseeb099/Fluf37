from backend.config import NexusConfig
from backend.memory.demo_graph import seed_demo_graph
from backend.memory.graph import NexusGraph


def test_demo_graph_has_readable_labels(tmp_path):
    cfg = NexusConfig.model_construct(graph_db_path=str(tmp_path / "graph.json"))
    graph = NexusGraph(cfg)
    seed_demo_graph(graph)
    data = graph.serialize()
    titles = {n["id"]: n.get("title") for n in data["nodes"]}
    assert titles["fail_001"] == "Circular payment loop — Acme Corp"
    assert "loss_001" in titles
    assert "Realized loss" in titles["loss_001"]
    assert len(data["edges"]) == 3
