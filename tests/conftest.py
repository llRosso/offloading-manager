import pytest
from starlette.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from src.main import app
from src.core.model import Model
from src.core.decision_module import OnlyDeleteDecisionModule
from src.type import ModuleType, OffloadingType, Stats, RobotID
from tests.fixtures.fixtures import test_client, clean_model

@pytest.fixture
def test():
    with TestClient(app, raise_server_exceptions=True) as client:
        yield client


@pytest.fixture
def model():
    return Model(OnlyDeleteDecisionModule)


@pytest.fixture
def populated_model(model):
    """Model with two robots and one module already registered."""
    from src.routers.robot.robot import Robot
    from src.routers.module.module import Module

    robot1 = MagicMock(spec=Robot)
    robot1.robot_id = 1
    robot2 = MagicMock(spec=Robot)
    robot2.robot_id = 2

    model._robotRegistry.add_robot_connection(robot1, 1)
    model._robotRegistry.add_robot_connection(robot2, 2)

    module = MagicMock(spec=Module)
    module._connected = True
    model._moduleRegistry.add_module_connection(ModuleType.ARUCO, module)
    model._moduleRegistry.update_module_stats(ModuleType.ARUCO, Stats(cpu_usage=10.0, memory_usage=20.0))

    return model, robot1, robot2, module
