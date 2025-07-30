"""LED strip controller for WS2812 addressable LEDs.

Provides animation effects and scoring feedback for DuckQuest using PWM-controlled LEDs.
"""

import time
from rpi_ws281x import PixelStrip, Color
from duckquest.utils.logger import setup_logger

logger = setup_logger(__name__)

# LED strip configuration
LED_COUNT = 144  # Number of LED pixels
LED_PIN = 18  # GPIO pin connected to the pixels (18 = PWM)
LED_FREQ_HZ = 800000  # Frequency of the signal in hertz (usually 800kHz)
LED_DMA = 10  # DMA channel to use for generating signal
LED_BRIGHTNESS = 10  # Brightness (0 to 255)
LED_INVERT = False  # True to invert signal
LED_CHANNEL = 0  # 0 for GPIO 18; 1 for GPIOs 13/19/41/45/53


class LEDStripManager:
    """Control an LED strip connected via PWM."""

    def __init__(self):
        """Initialize the LED strip hardware."""
        logger.info("Initializing LED strip...")
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
        logger.debug(f"LED strip initialized with {LED_COUNT} LEDs")

    def set_pixel_color(self, pixel: int, color: tuple[int, int, int]):
        """Set a single pixel color and update the strip."""
        if not (0 <= pixel < self.strip.numPixels()):
            logger.warning(f"Ignored invalid pixel index: {pixel}")
            return
        self.strip.setPixelColor(pixel, Color(*color))
        self.strip.show()
        logger.debug(f"Set pixel {pixel} to color {color}")

    def set_all_pixels(self, color: tuple[int, int, int]):
        """Set all pixels to the specified color."""
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(*color))
        self.strip.show()
        logger.debug(f"Set all pixels to color {color}")

    def score_effect(self, percentage: float = 1) -> tuple[int, int, int]:
        """Display a progressive red-to-green effect based on percentage."""
        logger.info(f"Starting score effect for {percentage*100:.1f}%")
        pause = 60
        color = (0, 0, 0)
        steps = max(1, int(self.strip.numPixels() * percentage))
        progress = 0.0

        for i in range(steps):
            color = (
                int(255 * (1 - progress)),
                int(255 * progress),
                0,
            )
            self.strip.setPixelColor(i, Color(*color))
            self.strip.show()
            progress += percentage / steps
            pause = max(10, pause - (i * percentage / 200))
            time.sleep(pause / 1000.0)

        logger.debug(f"Score effect completed with final color: {color}")
        time.sleep(0.1)
        return color

    def blink(self, color: tuple[int, int, int], repetitions: int, wait_ms: float):
        """Blink the whole strip in a specified color."""
        logger.info(f"Blinking {repetitions}x with color {color}")
        for _ in range(repetitions):
            self.set_all_pixels(color)
            time.sleep(wait_ms / 1000.0)
            self.set_all_pixels((0, 0, 0))  # Turn off LEDs between blinks
            time.sleep(wait_ms / 1000.0)
        logger.debug("Blink sequence finished")

    def clear(self):
        """Turn off all LEDs."""
        logger.info("Clearing LED strip")
        self.set_all_pixels((0, 0, 0))
