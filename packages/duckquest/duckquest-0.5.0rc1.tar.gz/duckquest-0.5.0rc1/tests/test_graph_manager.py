import pytest
from duckquest.graph.manager import COLORS
from duckquest.utils.logger import setup_logger

logger = setup_logger(__name__)


def test_graph_node_count(graph_manager):
    """Test that the graph contains the correct set of nodes."""
    expected_nodes = [
        f"{letter}{num}"
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for num in (1, 2)
        if not (letter > "R" and num == 2)
    ]
    logger.info(f"Expected node count: {len(expected_nodes)}")
    assert set(graph_manager.graph.nodes) == set(expected_nodes)


def test_graph_edge_existence(graph_manager):
    """Test that all expected edges exist in the graph."""
    for u, v in graph_manager.edges:
        assert graph_manager.graph.has_edge(u, v), f"Missing edge: {u}-{v}"


def test_graph_position_mapping(graph_manager):
    """Test that every node has a defined 2D position."""
    assert len(graph_manager.node_positions) == len(graph_manager.nodes)
    for node in graph_manager.nodes:
        assert node in graph_manager.node_positions
        pos = graph_manager.node_positions[node]
        assert isinstance(pos, tuple) and len(pos) == 2


def test_assign_weights_and_colors(graph_manager):
    """Test that edge weights and colors are correctly assigned."""
    graph_manager.assign_weights_and_colors(difficulty=6)
    for u, v in graph_manager.graph.edges:
        data = graph_manager.graph[u][v]
        assert "weight" in data
        assert "color" in data
        assert data["weight"] in [1, 3, 5]
        assert data["color"] == COLORS[data["weight"]]


def test_shortest_path_existing(graph_manager):
    """Test the shortest path between two connected nodes."""
    graph_manager.assign_weights_and_colors(difficulty=6)
    path = graph_manager.shortest_path("A1", "F1")
    logger.info(f"Shortest path from A1 to F1: {path}")
    assert path is not None
    assert path[0] == "A1"
    assert path[-1] == "F1"


def test_shortest_path_nonexistent(graph_manager):
    """Test the shortest path between disconnected nodes returns None."""
    graph_manager.graph.add_node("ZZZ")
    path = graph_manager.shortest_path("A1", "ZZZ")
    logger.warning("Testing path to non-existent node ZZZ — should return None")
    assert path is None


def test_edge_weight_existing(graph_manager):
    """Test that the weight of an existing edge is correct."""
    graph_manager.assign_weights_and_colors(difficulty=6)
    edge = graph_manager.edges[0]
    weight = graph_manager.edge_weight(*edge)
    assert weight in [1, 5, 3]


def test_edge_weight_missing(graph_manager):
    """Test that the weight of a non-existent edge returns None."""
    weight = graph_manager.edge_weight("A1", "ZZZ")
    logger.info("Testing edge_weight with non-existent edge A1-ZZZ")
    assert weight is None


def test_neighbors_valid_node(graph_manager):
    """Test that neighbors of a valid node are returned correctly."""
    neighbors = graph_manager.neighbors("A1")
    logger.info(f"Neighbors of A1: {neighbors}")
    assert isinstance(neighbors, list)
    assert all(isinstance(n, str) for n in neighbors)


def test_neighbors_invalid_node(graph_manager):
    """Test that querying neighbors of an invalid node raises ValueError."""
    with pytest.raises(ValueError):
        graph_manager.neighbors("ZZZ")
