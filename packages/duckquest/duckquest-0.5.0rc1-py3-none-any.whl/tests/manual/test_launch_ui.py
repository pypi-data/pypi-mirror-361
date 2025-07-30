import pytest
from duckquest.utils.logger import setup_logger

logger = setup_logger(__name__)


@pytest.mark.manual
def test_manual_ui_launch():
    """Manual UI launch test for visual inspection."""
    logger.info("Launching manual UI test. Please verify the interface visually.")
    import tests.launch_ui as launch_ui

    launch_ui.launch_ui()
