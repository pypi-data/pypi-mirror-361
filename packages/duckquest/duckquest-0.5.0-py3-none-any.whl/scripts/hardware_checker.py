import time
import RPi.GPIO as GPIO
from rpi_ws281x import PixelStrip, Color
from duckquest.utils.logger import setup_logger

logger = setup_logger(__name__)

# GPIO pin for the button
BUTTON_GPIO = 17  # Adjust as needed

# LED strip configuration
LED_COUNT = 144  # Number of LEDs in the strip
LED_PIN = 18  # GPIO pin connected to the LED strip (18 uses PWM!)
LED_FREQ_HZ = 800000  # LED signal frequency (typically 800kHz)
LED_DMA = 10  # DMA channel for generating the signal
LED_BRIGHTNESS = 10  # Brightness level (0 = off, 255 = max brightness)
LED_INVERT = (
    False  # Invert signal (set True if using an NPN transistor for level shifting)
)
LED_CHANNEL = 0  # Use channel 1 for GPIOs 13, 19, 41, 45, or 53


class HardwareChecker:
    """Controls the LED strip and monitors a button press."""

    def __init__(self, button_gpio: int):
        self.button_gpio = button_gpio
        self._setup_gpio()

        # Initialize LED strip
        self.strip = PixelStrip(
            LED_COUNT,
            LED_PIN,
            LED_FREQ_HZ,
            LED_DMA,
            LED_INVERT,
            LED_BRIGHTNESS,
            LED_CHANNEL,
        )
        self.strip.begin()
        logger.info("LED strip initialized.")

    def _setup_gpio(self) -> None:
        """Configure the GPIO pin for input with internal pull-up."""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.button_gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        logger.info(f"GPIO pin {self.button_gpio} configured as input with pull-up.")

    def all_color(self, color: Color) -> None:
        """Set all LEDs to the specified color."""
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
        self.strip.show()

    def blink(self, color: Color, repetitions: int, wait_ms: int) -> None:
        """Blink the LEDs with a specific color."""
        logger.info(f"Blinking {repetitions} times with color: {color}.")
        for _ in range(repetitions):
            self.all_color(color)
            time.sleep(wait_ms / 1000.0)
            self.clear()
            time.sleep(wait_ms / 1000.0)

    def clear(self) -> None:
        """Turn off all LEDs."""
        self.all_color(Color(0, 0, 0))

    def cleanup(self) -> None:
        """Reset LEDs and GPIO state."""
        self.clear()
        GPIO.cleanup()
        logger.info("GPIO and LEDs cleaned up. Exiting program.")

    def run(self) -> None:
        """Monitor button and respond with LED changes."""
        logger.info("Running hardware checker. Press button to activate yellow LEDs.")
        try:
            while True:
                if GPIO.input(self.button_gpio) == GPIO.LOW:
                    logger.debug("Button pressed.")
                    self.all_color(Color(255, 255, 0))  # Yellow
                    time.sleep(0.2)
                else:
                    self.clear()
                time.sleep(0.01)  # Short delay to reduce CPU usage
        except KeyboardInterrupt:
            logger.warning("Hardware checker interrupted by user.")
        except Exception as e:
            logger.exception("Unexpected error in hardware checker.")
            raise
        finally:
            self.cleanup()


if __name__ == "__main__":
    logger.info(f"Using button GPIO: {BUTTON_GPIO}")
    logger.info(f"Using LED GPIO: {LED_PIN}")
    logger.info(f"LED count: {LED_COUNT}")

    checker = HardwareChecker(BUTTON_GPIO)
    checker.run()
