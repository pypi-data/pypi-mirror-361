"""Audio manager for background music and sound effects.

Uses pygame to load, play, pause, and stop music, and control volume for the DuckQuest game.
"""

import pygame
from duckquest.utils.logger import setup_logger

logger = setup_logger(__name__)


class AudioManager:
    """Manages background music and sound effects."""

    def __init__(self):
        try:
            pygame.mixer.init()
            self.music_paused = False  # Tracks if the music is paused
            logger.info("Audio mixer initialized successfully.")
        except Exception:
            logger.error("Failed to initialize audio mixer.", exc_info=True)
            self.music_paused = False

    def play_music(self, file_path: str, loop: int = -1):
        """Play background music."""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play(loop)
            self.music_paused = False
            logger.info(f"Playing music: {file_path}")
        except Exception:
            logger.error(f"Error playing music: {file_path}", exc_info=True)

    def pause_or_resume_music(self):
        """Pause or resume the currently playing music."""
        try:
            if self.music_paused:
                pygame.mixer.music.unpause()
                self.music_paused = False
                logger.info("Music resumed.")
            else:
                pygame.mixer.music.pause()
                self.music_paused = True
                logger.info("Music paused.")
        except Exception:
            logger.error("Error while pausing/resuming music.", exc_info=True)

    def stop_music(self):
        """Stop the background music."""
        try:
            pygame.mixer.music.stop()
            self.music_paused = False
            logger.info("Music stopped.")
        except Exception:
            logger.error("Error stopping music.", exc_info=True)

    def play_sound_effect(self, file_path: str):
        """Play a sound effect."""
        try:
            sound = pygame.mixer.Sound(file_path)
            sound.play()
            logger.info(f"Sound effect played: {file_path}")
        except Exception:
            logger.error(f"Error playing sound effect: {file_path}", exc_info=True)

    def set_volume(self, volume: float):
        """Set the volume for music."""
        if 0.0 <= volume <= 1.0:
            pygame.mixer.music.set_volume(volume)
            logger.info(f"Music volume set to {volume:.2f}")
        else:
            logger.warning(f"Invalid volume: {volume}. Must be between 0.0 and 1.0.")

    def increase_volume(self, increment: float = 0.1):
        """Increase the music volume by a specified increment."""
        current_volume = pygame.mixer.music.get_volume()
        new_volume = min(1.0, current_volume + increment)
        pygame.mixer.music.set_volume(new_volume)
        logger.info(f"Volume increased to {new_volume:.2f}")

    def decrease_volume(self, decrement: float = 0.1):
        """Decrease the music volume by a specified decrement."""
        current_volume = pygame.mixer.music.get_volume()
        new_volume = max(0.0, current_volume - decrement)
        pygame.mixer.music.set_volume(new_volume)
        logger.info(f"Volume decreased to {new_volume:.2f}")
