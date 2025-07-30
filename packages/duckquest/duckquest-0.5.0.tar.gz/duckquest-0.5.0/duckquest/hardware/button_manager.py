"""GPIO-based button manager for Raspberry Pi.

Handles initialization and polling of multiple physical buttons using BCM pin numbers.
"""

import RPi.GPIO as GPIO
from duckquest.utils.logger import setup_logger

logger = setup_logger(__name__)


class ButtonManager:
    """Manage GPIO buttons on Raspberry Pi."""

    def __init__(self, pins: list[int]):
        """Initialize GPIO pins for button input."""
        self.pins = pins
        logger.info(f"Initializing ButtonManager with pins: {self.pins}")
        GPIO.setmode(GPIO.BCM)
        self.setup_buttons()

    def setup_buttons(self):
        """Configure pins as pull-up inputs."""
        for pin in self.pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            logger.debug(f"Pin {pin} set as input with pull-up")

    def get_pressed_button(self) -> int | None:
        """Return the GPIO pin of the pressed button, or None."""
        for pin in self.pins:
            state = GPIO.input(pin)
            logger.debug(
                f"Reading pin {pin}: {'LOW (pressed)' if state == GPIO.LOW else 'HIGH'}"
            )
            if state == GPIO.LOW:
                logger.info(f"Button pressed on pin {pin}")
                return pin
        return None  # No button pressed

    def cleanup(self):
        """Clean up GPIO state."""
        GPIO.cleanup()
        logger.info("GPIO cleaned up")
