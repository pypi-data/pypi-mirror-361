"""Main entry point to launch the DuckQuest game."""

import platform
from duckquest.utils.helpers import is_raspberry_pi
from duckquest.utils.logger import setup_logger

logger = setup_logger(__name__)  # Initialize module-level logger


def main():
    """Initialize and start the DuckQuest game."""
    OS_NAME = platform.system()
    ON_RASPBERRY_PI = is_raspberry_pi()

    logger.info(f"Starting Duck Quest on OS: {OS_NAME}")

    if ON_RASPBERRY_PI:
        logger.info("Running on Raspberry Pi hardware.")
    else:
        logger.warning(
            "Hardware mode disabled: running in mock mode (not a Raspberry Pi system). GPIO and LED features will be simulated."
        )

    try:
        from duckquest.game_manager import GameManager

        logger.debug("Instantiating GameManager")
        game = GameManager(ON_RASPBERRY_PI)
        logger.info("GameManager instantiated, launching mainloop.")
        game.root.mainloop()
        logger.info("Main loop terminated cleanly.")

    except Exception as e:
        logger.critical(f"Unhandled exception in main: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
