"""Graph rendering logic using matplotlib.

Handles visual display of the graph, selected paths, shortest paths, and weight-color legends for educational feedback.
"""

import networkx as nx
import matplotlib.pyplot as plt
from duckquest.utils.logger import setup_logger

logger = setup_logger(__name__)

COLORS = {
    1: (0, 1, 0),  # Soft Green
    2: (0.78, 1, 0),  # Yellow-Green
    3: (1, 1, 0),  # Bright Yellow
    4: (1, 0.5, 0),  # Orange
    5: (1, 0, 0),  # Bright Red
}


class GraphRenderer:
    """Responsible for rendering the graph and highlighting user interaction."""

    def __init__(self, game_manager):
        logger.info("Initializing GraphRenderer")
        self.game_manager = game_manager
        self.graph = self.game_manager.graph
        self.logic = self.game_manager.logic
        self.ax = None
        self.canvas = None

    def init_ui(self, ax, canvas):
        """Initialize the Matplotlib axis and canvas for rendering."""
        self.ax = ax
        self.canvas = canvas
        logger.debug("UI initialized with axis and canvas")

    def display_graph(self, edge_colors: list = None, node_colors: dict = None):
        """Display the graph in the main window with a legend for edge weights and colors"""
        logger.debug("Rendering full graph")
        self.ax.clear()
        # Determine edge colors if not provided
        if edge_colors is None:
            edge_colors = [
                data["color"] for _, _, data in self.graph.graph.edges(data=True)
            ]
            logger.debug("Default edge colors applied")
        # Determine node colors if not provided
        if node_colors is None:
            node_colors = {node: "lightblue" for node in self.graph.graph.nodes()}
            logger.debug("Default node colors applied")

        # Create a list of colors for nodes
        node_colors_list = [
            node_colors.get(node, "lightblue") for node in self.graph.graph.nodes()
        ]
        # Draw the graph
        nx.draw(
            self.graph.graph,
            pos=self.graph.node_positions,
            ax=self.ax,
            with_labels=True,
            node_size=500,
            node_color=node_colors_list,
            font_size=8,
            font_color="black",
            edge_color=edge_colors,
            width=5,
        )

        self.display_legend(self.ax)
        self.canvas.draw()
        logger.info("Graph rendered on canvas")

    def display_legend(self, ax):
        """Add a legend for edge weights and colors"""
        legend_handles = [
            plt.Line2D([0], [0], color=color, lw=4, label=f"{weight}")
            for weight, color in COLORS.items()
        ]
        ax.legend(
            handles=legend_handles,
            title="Edge Weights",
            loc="lower left",
            ncol=1,
            fontsize=10,
            title_fontsize=12,
            frameon=True,
        )
        logger.debug("Legend displayed")

    def display_user_path(self):
        """Highlight the user's selected path and selected nodes"""
        logger.debug("Displaying user-selected path")
        edge_colors = []
        for edge in self.graph.graph.edges():
            if (
                edge in self.logic.user_path_edges
                or (edge[1], edge[0]) in self.logic.user_path_edges
            ):
                edge_colors.append("cyan")
            else:
                edge_colors.append(
                    self.graph.graph[edge[0]][edge[1]].get("color", "black")
                )

        node_colors = {
            node: (
                "yellow"
                if node == self.logic.available_nodes[self.logic.selection_index]
                and node in self.logic.selected_nodes
                else (
                    "green"
                    if node == self.logic.available_nodes[self.logic.selection_index]
                    else "cyan" if node in self.logic.selected_nodes else "lightblue"
                )
            )
            for node in self.graph.graph.nodes()
        }

        self.display_graph(edge_colors, node_colors)
        logger.info("User path rendered")

    def highlight_shortest_path(self, path: list):
        """Highlight the shortest path in purple"""
        logger.debug(f"Highlighting shortest path: {path}")
        edges_in_path = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
        edge_colors = []
        for edge in self.graph.graph.edges():
            if edge in edges_in_path or (edge[1], edge[0]) in edges_in_path:
                edge_colors.append("purple")
            else:
                edge_colors.append(
                    self.graph.graph[edge[0]][edge[1]].get("color", "black")
                )

        self.display_graph(edge_colors)
        logger.info("Shortest path highlighted")
