"""Main controller that manages the overall game state and interactions.

This module coordinates the graph logic, UI rendering, physical hardware (buttons and LEDs), and audio manager to provide a cohesive game experience.
"""

from tkinter import *
from tkinter import messagebox
from duckquest.graph.manager import GraphManager
from duckquest.graph.logic import GraphLogic
from duckquest.graph.renderer import GraphRenderer
from duckquest.graph.ui import GraphUI
from duckquest.utils.logger import setup_logger

logger = setup_logger(__name__)  # Initialize module-level logger


# from duckquest.audio.manager import AudioManager
class GameManager:
    """Manage the overall game state, including logic, UI, audio, and hardware interactions."""

    def __init__(self, is_rpi: bool):
        logger.info("Initializing GameManager")

        self.score = 0
        self.difficulty = 6

        logger.debug("Initializing graph structure and logic")
        self.graph = GraphManager()
        self.logic = GraphLogic(self)

        # Audio system placeholder
        # self.audio_manager = AudioManager()
        # self.audio_manager.play_music("duckquest/assets/sounds/music_1.wav")

        logger.debug("Initializing graph rendering and UI")
        self.graph_renderer = GraphRenderer(self)
        self.graph_ui = GraphUI(self)
        self.root = self.graph_ui.root

        logger.debug("Importing hardware interfaces")
        try:
            if is_rpi:
                from duckquest.hardware.button_manager import ButtonManager
                from duckquest.hardware.led_strip_manager import LEDStripManager

                logger.info("Using real hardware drivers (Raspberry Pi)")
            else:
                from duckquest.hardware.mock import ButtonManager, LEDStripManager

                logger.info("Using mock hardware drivers")

            self.led_strip_manager = LEDStripManager()
            self.running = True
            self.button_manager = ButtonManager([17, 22, 23, 27, 16])  # GPIO pin setup
            logger.debug("Hardware initialized successfully")
        except Exception as e:
            logger.critical(f"Failed to initialize hardware: {e}", exc_info=True)
            raise

        self.check_buttons()
        logger.info("GameManager initialized")

    def check_buttons(self):
        """Check whether a button is pressed and perform the corresponding action."""
        if self.running:
            try:
                pressed_button = self.button_manager.get_pressed_button()
                if pressed_button == 17:
                    logger.debug("Button 17 pressed: select_node()")
                    self.select_node()
                elif pressed_button == 22:
                    logger.debug("Button 22 pressed: next_node()")
                    self.next_node()
                elif pressed_button == 23:
                    logger.debug("Button 23 pressed: previous_node()")
                    self.previous_node()
                elif pressed_button == 27:
                    logger.debug("Button 27 pressed: reset_selection()")
                    self.reset_selection()
                elif pressed_button == 16:
                    logger.debug("Button 16 pressed: check_path()")
                    self.check_path()
            except Exception as e:
                logger.warning(f"Error while handling button press: {e}", exc_info=True)

            self.root.after(100, self.check_buttons)

    def next_node(self):
        """Move selection to the next available node in a cyclic manner."""
        logger.debug("Switching to next node")
        self.logic.selection_index = (self.logic.selection_index + 1) % len(
            self.logic.available_nodes
        )
        self.graph_renderer.display_user_path()

    def previous_node(self):
        """Move selection to the previous available node in a cyclic manner."""
        logger.debug("Switching to previous node")
        self.logic.selection_index = (self.logic.selection_index - 1) % len(
            self.logic.available_nodes
        )
        self.graph_renderer.display_user_path()

    def select_node(self):
        """Handle node selection."""
        logger.debug("Selecting current node")
        self.logic.change_current_node()
        self.graph_renderer.display_user_path()

    def reset_selection(self):
        """Reset all selected nodes and edges."""
        logger.info("Resetting selection")
        self.logic.reset_selection()
        self.graph_renderer.display_user_path()

    def restart_game(self):
        """Restart the game."""
        logger.info("Restarting game")
        self.logic.restart_game()
        self.graph_renderer.display_user_path()

    def quit_game(self):
        """Close the application."""
        logger.info("Quitting game")
        self.led_strip_manager.clear()
        self.running = False
        self.button_manager.cleanup()
        self.root.quit()

    def on_click(self, event):
        """Handle node clicks and builds the user's selected path"""
        if event.xdata and event.ydata:
            logger.debug(f"Click at ({event.xdata}, {event.ydata})")
            for node, position in self.graph.node_positions.items():
                if (
                    abs(event.xdata - position[0]) < 0.2
                    and abs(event.ydata - position[1]) < 0.2
                ):
                    logger.debug(f"Node {node} selected via click")
                    self.logic.handle_node_click(node)
                    self.graph_renderer.display_user_path()
                    break

    def check_path(self):
        """Check if the user's selected path is the shortest path"""
        logger.info("Checking user's path against shortest path")
        result, score = self.logic.check_shortest_path()

        if result.startswith("Congratulations"):
            logger.info("Correct path selected")
            messagebox.showinfo("Success", result)
            self.restart_game()
        else:
            logger.warning("Incorrect path selected")
            messagebox.showerror("Error", result)
            self.reset_selection()

        self.led_strip_manager.blink(
            self.led_strip_manager.score_effect(score / 100), 5, 200
        )
        self.led_strip_manager.clear()

        self.score += score * self.difficulty
        logger.debug(f"Updated score: {self.score}")
        self.graph_ui.update_score_display(self.score)

    def toggle_shortest_path(self):
        """Display or hide the shortest path directly on the graph"""
        logger.debug("Toggling shortest path display")
        if not self.logic.shortest_path_displayed:
            path = self.graph.shortest_path(self.logic.start_node, self.logic.end_node)
            if path:
                logger.info(f"Displaying shortest path: {path}")
                self.graph_renderer.highlight_shortest_path(path)
            else:
                logger.error("No path found between start and end nodes")
                messagebox.showerror("Error", "No path found.")
        else:
            logger.info("Hiding shortest path display")
            self.graph_renderer.display_user_path()

        self.logic.shortest_path_displayed = not self.logic.shortest_path_displayed
