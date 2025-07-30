"""Mock hardware interfaces for non-Raspberry Pi systems.

Provides dummy implementations of ButtonManager and LEDStripManager for development and testing.
"""

from duckquest.utils.logger import setup_logger

logger = setup_logger(__name__)


class ButtonManager:
    """Mock ButtonManager for non-Raspberry Pi systems."""

    def __init__(self, pins):
        logger.info(f"[MOCK] ButtonManager initialized with pins: {pins}")

    def get_pressed_button(self):
        logger.debug("[MOCK] get_pressed_button() called")
        return None

    def cleanup(self):
        logger.info("[MOCK] ButtonManager cleanup called")


class LEDStripManager:
    """Mock LEDStripManager for non-Raspberry Pi systems."""

    def clear(self):
        logger.info("[MOCK] LED Strip cleared")

    def blink(self, color, times, delay):
        logger.info(
            f"[MOCK] Blinking LED {times} times with color {color}, delay {delay}"
        )

    def score_effect(self, score):
        logger.info(f"[MOCK] score_effect called with score: {score}")
        return "[MOCK] Score effect color"
