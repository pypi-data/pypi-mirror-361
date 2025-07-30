import pytest
from duckquest.utils.logger import setup_logger

logger = setup_logger(__name__)


def test_initial_state(logic):
    """Check initial state of GraphLogic"""
    logger.info("Testing initial state of GraphLogic")
    assert logic.current_node == "A1"
    assert logic.start_node == "A1"
    assert logic.end_node == "Q2"
    assert logic.selected_path == ["A1"]
    assert logic.user_path_edges == []
    assert not logic.shortest_path_displayed


def test_get_available_nodes(logic):
    """Check available neighbors are correctly fetched"""
    current = logic.current_node
    neighbors = list(logic.graph.graph.neighbors(current))
    expected = [current] + list(reversed(neighbors))
    assert logic.get_available_nodes() == expected


def test_change_current_node(logic):
    """Change the current node and check updates"""
    previous = logic.current_node
    logic.selection_index = 1
    logic.change_current_node()
    assert logic.current_node != previous
    assert logic.current_node in logic.graph.graph.nodes


def test_handle_node_click_add_remove(logic):
    """Test that node click adds and removes from selection correctly"""
    logic.handle_node_click("C1")
    assert "C1" in logic.selected_nodes
    assert logic.selected_path == ["A1", "C1"]
    logic.handle_node_click("C1")
    assert "C1" not in logic.selected_nodes
    assert logic.selected_path == ["A1"]


def test_reset_selection(logic):
    """Test reset_selection resets paths and index"""
    logic.selected_path = ["A1", "B1"]
    logic.user_path_edges = [("A1", "B1")]
    logic.selected_nodes = {"A1", "B1"}
    logic.selection_index = 2
    logic.reset_selection()
    assert logic.selected_path == []
    assert logic.user_path_edges == []
    assert logic.selected_nodes == set()
    assert logic.selection_index == 0
    assert logic.current_node == "A1"


def test_calculate_score_optimal(logic):
    """Test score is 100% when user path matches optimal path"""
    optimal_path = logic.graph.shortest_path("A1", "Q2")
    if not optimal_path or len(optimal_path) < 2:
        logger.warning("No valid path between A1 and Q2 — skipping")
        pytest.skip("No valid path between A1 and Q2")
    logic.selected_path = optimal_path
    logic.user_path_edges = list(zip(optimal_path, optimal_path[1:]))
    msg, score = logic.calculate_score()
    assert score == 100
    assert "100" in msg


def test_calculate_score_invalid_start_end(logic):
    """Test score is 0% when path does not start at A1 or end at Q2"""
    logic.selected_path = ["B1", "C1"]
    logic.user_path_edges = [("B1", "C1")]
    msg, score = logic.calculate_score()
    assert score == 0
    assert "must start at the beginning" in msg


def test_check_shortest_path_success(logic):
    """Test feedback when shortest path is found"""
    path = logic.graph.shortest_path("A1", "Q2")
    if not path or len(path) < 2:
        logger.warning("No valid path between A1 and Q2 — skipping")
        pytest.skip("No valid path between A1 and Q2")
    logic.selected_path = path
    logic.user_path_edges = list(zip(path, path[1:]))
    msg, score = logic.check_shortest_path()
    assert score == 100
    assert "Congratulations" in msg


def test_check_shortest_path_failure(logic):
    """Ensure non-optimal paths yield lower scores and correct feedback."""
    path = logic.graph.shortest_path("A1", "Q2")
    if not path or len(path) < 4:
        logger.warning("Path too short to test detour behavior — skipping")
        pytest.skip("Path too short to test detour behavior")

    debug_info = {}
    used_reverse = False

    def try_detour(path_to_modify):
        for i in range(len(path_to_modify) - 1):
            n1, n2 = path_to_modify[i], path_to_modify[i + 1]
            shared_neighbors = set(logic.graph.neighbors(n1)) & set(
                logic.graph.neighbors(n2)
            )
            candidate_nodes = shared_neighbors - set(path_to_modify)

            for detour_node in candidate_nodes:
                detour = (
                    path_to_modify[: i + 1] + [detour_node] + path_to_modify[i + 1 :]
                )
                W_opt = sum(
                    logic.graph.graph[u][v]["weight"]
                    for u, v in zip(path_to_modify, path_to_modify[1:])
                )
                W_test = sum(
                    logic.graph.graph[u][v]["weight"]
                    for u, v in zip(detour, detour[1:])
                )

                if W_test <= W_opt:
                    continue

                logic.selected_path = detour
                logic.user_path_edges = list(zip(detour, detour[1:]))
                _, score = logic.calculate_score()

                if score < 100:
                    return detour, detour_node, i, W_test, W_opt, score
        return None, None, None, None, None, None

    try:
        # Try original path
        bad_path, detour_node, index, W_user, W_opt, score = try_detour(path)

        # Try reversed path if needed
        if not bad_path:
            used_reverse = True
            reversed_path = list(reversed(path))
            reversed_bad_path, detour_node, rev_index, W_user, W_opt, score = (
                try_detour(reversed_path)
            )
            if reversed_bad_path:
                bad_path = list(reversed(reversed_bad_path))
                index = len(path) - rev_index - 2

        if not bad_path:
            logger.warning("No valid suboptimal detour found — skipping")
            pytest.skip("No valid suboptimal detour found")

        logic.selected_path = bad_path
        logic.user_path_edges = list(zip(bad_path, bad_path[1:]))
        msg, final_score = logic.check_shortest_path()

        # Save debug info in case of fail
        debug_info = {
            "used_reverse": used_reverse,
            "detour_node": detour_node,
            "index": index,
            "optimal_path": path,
            "user_path": bad_path,
            "W_opt": W_opt,
            "W_user": W_user,
            "score": final_score,
            "msg": msg,
        }

        assert final_score < 100, "Score should be less than 100 for a suboptimal path."
        assert "not the shortest route" in msg

    except AssertionError as e:
        logger.error("Test failed — debug info follows:")
        for k, v in debug_info.items():
            logger.error(f"{k}: {v}")
        raise
