import pytest
from duckquest.graph.logic import GraphLogic
from duckquest.graph.manager import GraphManager
from duckquest.utils.logger import setup_logger

logger = setup_logger(__name__)


class DummyGameManager:
    def __init__(self, difficulty=11):
        logger.debug(f"Initializing DummyGameManager with difficulty={difficulty}")
        self.difficulty = difficulty
        self.graph = GraphManager()
        self.graph.assign_weights_and_colors(self.difficulty)
        logger.debug("DummyGameManager initialized successfully")


@pytest.fixture
def graph_manager():
    """Provide a fresh instance of GraphManager for each test."""
    logger.info("Creating GraphManager fixture")
    manager = GraphManager()
    logger.debug("GraphManager fixture ready")
    return manager


@pytest.fixture
def logic():
    """Fixture for initializing GraphLogic with a dummy game manager."""
    logger.info("Creating GraphLogic fixture with DummyGameManager")
    game_manager = DummyGameManager()
    logic_instance = GraphLogic(game_manager)
    logger.debug("GraphLogic fixture ready")
    return logic_instance
