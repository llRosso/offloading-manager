import pytest
from starlette.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock, patch
from src.main import app, model
from src.type import OffloadingType, ModuleType
from src.routers.robot.robot import Robot

@pytest.fixture
def test_client():
    with TestClient(app, raise_server_exceptions=True) as client:
        yield client


@pytest.fixture(autouse=True)
def clean_model():
    """Reset model state between tests."""
    model._robotRegistry._robots_state.clear()
    model._moduleRegistry._module_connections.clear()
    model._moduleRegistry._module_stats.clear()
    yield
    model._robotRegistry._robots_state.clear()
    model._moduleRegistry._module_connections.clear()
    model._moduleRegistry._module_stats.clear()


