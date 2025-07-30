"""Entry point to manually launch the DuckQuest UI."""

from duckquest.game_manager import GameManager
from duckquest.utils.logger import setup_logger

logger = setup_logger(__name__)


def launch_ui():
    """Launch the DuckQuest user interface."""
    logger.info("Launching DuckQuest UI in manual mode (non-Raspberry Pi).")

    try:
        game = GameManager(is_rpi=False)
        game.root.mainloop()
    except Exception as e:
        logger.exception("Failed to launch the DuckQuest UI.")
        raise


if __name__ == "__main__":
    launch_ui()
