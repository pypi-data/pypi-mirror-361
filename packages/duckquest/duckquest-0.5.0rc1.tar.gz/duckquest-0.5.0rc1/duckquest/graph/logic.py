"""Implements the graph logic for user interaction and shortest path validation.

Handles node selection, path construction, and score calculation.
"""

import networkx as nx
from duckquest.utils.logger import setup_logger

logger = setup_logger(__name__)  # Initialize module-level logger


class GraphLogic:
    """Manage the logic and operations of the graph for the game."""

    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.graph = self.game_manager.graph

        self.selected_path = []
        self.user_path_edges = []
        self.selected_nodes = set()
        self.shortest_path_displayed = False

        # Initialize the graph
        self.start_node = "A1"
        self.end_node = "Q2"

        self.current_node = self.start_node
        self.available_nodes = self.get_available_nodes()
        self.selection_index = 0

        logger.info(
            f"Initializing GraphLogic from {self.start_node} to {self.end_node}"
        )
        self.graph.assign_weights_and_colors(self.game_manager.difficulty)
        logger.debug("Graph weights and colors assigned")
        self.change_current_node()

    def get_available_nodes(self):
        """Return a list of available neighboring nodes."""
        neighbors = [
            self.current_node,
            *reversed(self.graph.neighbors(self.current_node)),
        ]
        logger.debug(f"Available neighbors from {self.current_node}: {neighbors}")
        return neighbors

    def change_current_node(self):
        """Update the current node to the selected node."""
        self.current_node = self.available_nodes[self.selection_index]
        logger.info(f"Current node changed to {self.current_node}")
        self.available_nodes = self.get_available_nodes()
        self.handle_node_click(self.current_node)
        self.selection_index = 0

    def reset_selection(self):
        """Reset all selected nodes and edges"""
        logger.info("Resetting user selection")
        self.selected_path = []
        self.user_path_edges = []
        self.selected_nodes = set()

        self.current_node = self.start_node
        self.available_nodes = self.get_available_nodes()
        self.selection_index = 0

    def restart_game(self):
        """Restart the game by randomizing edge weights"""
        logger.info("Restarting game logic and reassigning weights")
        self.graph.assign_weights_and_colors(self.game_manager.difficulty)
        self.shortest_path_displayed = False
        self.reset_selection()

    def calculate_score(self):
        """Calculate the score based on the optimal path"""
        logger.debug("Calculating score for user's path")
        try:
            shortest_path = self.graph.shortest_path(self.start_node, self.end_node)
            W_optimal = sum(
                self.graph.graph[u][v]["weight"]
                for u, v in zip(shortest_path, shortest_path[1:])
            )
            logger.debug(f"Shortest path: {shortest_path}, optimal weight: {W_optimal}")
        except nx.NetworkXNoPath:
            logger.warning("No path exists between start and end node")
            return "No path between selected nodes.", 0

        if (
            not self.selected_path
            or self.selected_path[0] != self.start_node
            or self.selected_path[-1] != self.end_node
        ):
            logger.warning("Invalid path boundaries selected by user")
            return "Your path must start at the beginning and end at the goal.", 0

        # Calculate the weight of the path selected by the user
        W_user = sum(self.graph.graph[u][v]["weight"] for u, v in self.user_path_edges)
        logger.debug(f"User path weight: {W_user}")

        # Score calculation
        score = int(max(0, 100 * (W_optimal / W_user)))
        logger.info(f"Score calculated: {score}%")
        return f"Your score: {score} %", score

    def check_shortest_path(self):
        """Check if the user's selected path is the shortest path"""
        logger.info("Checking if user path is the shortest path")
        if len(self.selected_path) < 2:
            logger.warning("Path too short to evaluate")
            return "Please select a valid path with at least two nodes.", 0

        message, score = self.calculate_score()

        if score == 100:
            logger.info("User found the optimal path")
            return (
                f"Congratulations! You've found the shortest path! You're amazing! {message}",
                score,
            )
        else:
            logger.info("User path is suboptimal")
            return f"This is not the shortest route. {message} Try again!", score

    def handle_node_click(self, node: str):
        """Handles a single node click"""
        logger.debug(f"Handling click on node: {node}")
        if node in self.selected_nodes:
            logger.debug(f"Deselecting node: {node}")
            self.selected_nodes.remove(node)
            self.selected_path = [n for n in self.selected_path if n != node]
            self.user_path_edges = [
                edge for edge in self.user_path_edges if node not in edge
            ]
        else:
            logger.debug(f"Selecting node: {node}")
            self.selected_nodes.add(node)
            if self.selected_path and self.selected_path[-1] != node:
                edge = (self.selected_path[-1], node)
                if self.graph.graph.has_edge(*edge) or self.graph.graph.has_edge(
                    *edge[::-1]
                ):
                    self.user_path_edges.append(edge)
                    logger.debug(f"Edge added to path: {edge}")
            self.selected_path.append(node)
