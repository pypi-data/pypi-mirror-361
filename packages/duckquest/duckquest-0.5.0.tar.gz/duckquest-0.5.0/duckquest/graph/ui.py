"""Tkinter-based user interface for interacting with the graph.

This module defines the GUI layout, buttons, difficulty selector, and integrates with the renderer for dynamic graph updates.
"""

import json
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from duckquest.utils.logger import setup_logger

logger = setup_logger(__name__)

BUTTON_STYLE = {
    "bg": "#61AFEF",
    "fg": "white",
    "font": ("Arial", 12, "bold"),
    "relief": tk.RAISED,
    "borderwidth": 2,
    "activebackground": "#528AAE",
}

LABEL_STYLE = {
    "bg": "#282C34",
    "fg": "white",
    "font": ("Arial", 15, "bold"),
}


class GraphUI:
    """Handle the graphical interface for displaying and interacting with the graph."""

    def __init__(self, game_manager):
        logger.info("Initializing GraphUI")
        self.game_manager = game_manager
        self.graph = self.game_manager.graph
        self.logic = self.game_manager.logic
        # self.audio_manager = self.game_manager.audio_manager

        # Initialize the main Tkinter window
        self.root = tk.Tk()
        self.root.title("DuckQuest - Game Modelling")
        self.root.configure(bg="#282C34")

        # Define button actions and their associated functions
        self.button_commands = [
            ("Help", self.help_screen),
            ("Start a graph", self.game_manager.restart_game),
            ("Reset selection", self.game_manager.reset_selection),
            ("Check your path", self.game_manager.check_path),
            ("Solution", self.game_manager.toggle_shortest_path),
            ("Select node", self.game_manager.select_node),
            ("Next node", self.game_manager.next_node),
            ("Previous node", self.game_manager.previous_node),
            # ("Music pause", self.audio_manager.pause_or_resume_music),
            ("Quit", self.game_manager.quit_game),
        ]

        # Create a frame to hold the buttons
        self.button_frame = tk.Frame(self.root, bg="#282C34")
        self.button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Generate buttons dynamically from the list of commands
        for text, command in self.button_commands:
            button = tk.Button(
                self.button_frame, text=text, command=command, **BUTTON_STYLE
            )
            button.pack(fill=tk.X, pady=10)
        logger.debug("Buttons initialized")

        self.top_frame = tk.Frame(self.root, bg="#282C34")
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.difficulty_label = tk.Label(
            self.top_frame,
            text="DIFFICULTY : ",
            **LABEL_STYLE,
        )
        self.difficulty_label.pack(side=tk.LEFT, padx=10)

        self.difficulty_scale = tk.Scale(
            self.top_frame,
            from_=1,
            to=11,
            orient=tk.HORIZONTAL,
            length=200,
            bg="#61AFEF",
            fg="#282C34",
            highlightbackground="#282C34",
            troughcolor="#282C34",
            sliderrelief=tk.RAISED,
            showvalue=False,
            command=self.update_difficulty,
        )
        self.difficulty_scale.set(self.game_manager.difficulty)
        self.difficulty_scale.pack(side=tk.LEFT)
        logger.debug("Difficulty scale configured")

        # Score banner
        self.score_label = tk.Label(
            self.top_frame,
            text=f"SCORE : {self.game_manager.score} PTS",
            **LABEL_STYLE,
        )
        self.score_label.pack(side=tk.LEFT, padx=10)
        logger.debug("Score label initialized")

        # Initialize the graph display area using Matplotlib
        self.figure, self.ax = plt.subplots(figsize=(12, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack(
            side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10
        )
        logger.debug("Matplotlib canvas initialized")

        # Link the renderer to the UI for visualization
        self.game_manager.graph_renderer.init_ui(self.ax, self.canvas)
        self.game_manager.graph_renderer.display_graph()

        logger.info("UI setup complete - displaying help screen")
        # Display help screen on startup
        self.help_screen()

        # Connect mouse click events to the graph interaction logic
        self.canvas.mpl_connect("button_press_event", self.game_manager.on_click)
        logger.debug("Canvas click binding established")

    def update_difficulty(self, value):
        """Update the difficulty."""
        new_difficulty = int(value)
        logger.info(f"Difficulty changed to {new_difficulty}")
        self.game_manager.difficulty = new_difficulty
        self.game_manager.restart_game()

    def update_score_display(self, score: int):
        """Update the score display bar."""
        logger.info(f"Score updated: {score} pts")
        self.score_label.config(text=f"SCORE : {score} PTS")

    def help_screen(self):
        """Display the game rules in an organized and visually appealing way."""
        logger.debug("Displaying help screen")
        y_position = 1.1  # Start near the top
        line_spacing = 0.04  # Space between lines
        # Clear the current axis

        self.ax.clear()
        self.ax.set_facecolor("#282C34")  # Dark background for better visibility
        self.ax.axis("off")  # Hide axes

        try:
            # Load rules from JSON
            with open("duckquest/data/rules.json", "r") as file:
                rules_data = json.load(file)
            rules = rules_data["rules"]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load rules: {e}")
            self.ax.text(0.5, 0.5, "Error loading rules.", ha="center", va="center")
            self.canvas.draw()
            return

        for section in rules:
            header = section["header"]
            content = section["content"]
            # Add section header
            self.ax.text(
                0.05,
                y_position,
                header,
                fontsize=12,
                fontweight="bold",
                ha="left",
                va="top",
                transform=self.ax.transAxes,
                color="black",
            )
            y_position -= line_spacing * 1.5  # Add extra space after the header
            for line in content:  # Add section content
                self.ax.text(
                    0.07,
                    y_position,
                    line,
                    fontsize=10,
                    ha="left",
                    va="top",
                    transform=self.ax.transAxes,
                    wrap=True,
                    color="black",
                )
                y_position -= line_spacing
            y_position -= line_spacing * 0.5  # Extra spacing after each section

        # Ensure the canvas updates
        self.canvas.draw()
        logger.info("Help screen rendered")
