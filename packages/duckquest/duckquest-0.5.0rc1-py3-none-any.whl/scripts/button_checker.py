"""Script to manually verify button functionality on a Raspberry Pi GPIO pin."""

import time
import RPi.GPIO as GPIO
from duckquest.utils.logger import setup_logger

logger = setup_logger(__name__)


def setup_gpio(pin: int) -> None:
    """Configure the GPIO pin for input with internal pull-up."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    logger.info(f"GPIO pin {pin} configured for button input (pull-up enabled).")


def wait_for_button(pin: int) -> None:
    """
    Continuously monitor the button pin.
    Log press/release events and duration.
    """
    press_count = 0
    is_pressed = False
    press_start_time = None

    logger.info(f"Monitoring GPIO pin {pin} for button input (Ctrl+C to stop)...")

    try:
        while True:
            if GPIO.input(pin) == GPIO.LOW:
                if not is_pressed:
                    is_pressed = True
                    press_start_time = time.time()
                    logger.info("Button pressed.")
            else:
                if is_pressed:
                    is_pressed = False
                    press_duration = time.time() - press_start_time
                    press_count += 1
                    logger.info(f"Button released. Duration: {press_duration:.3f}s")
                    logger.info(f"Total presses: {press_count}")
            time.sleep(0.01)

    except KeyboardInterrupt:
        logger.warning("Test interrupted by user (KeyboardInterrupt).")
    except Exception as e:
        logger.exception("Unexpected error during button monitoring.")
        raise
    finally:
        GPIO.cleanup()
        logger.info("GPIO cleanup complete.")
        logger.info(f"Total button presses recorded: {press_count}")


def run_checker(gpio_pin: int = 17) -> None:
    """Main entry point to start button checking."""
    setup_gpio(gpio_pin)
    wait_for_button(gpio_pin)


if __name__ == "__main__":
    run_checker()
