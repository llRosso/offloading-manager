import pytest
from starlette.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from src.main import app
from src.core.model import Model
from src.core.decision_module import OnlyDeleteDecisionModule
from src.type import ModuleType, OffloadingType, Stats, RobotID
from tests.fixtures.fixtures import test_client, clean_model, populated_model, model_fixture, test

