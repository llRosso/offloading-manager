import pytest
from starlette.testclient import TestClient

from src.main import app


@pytest.fixture
def test():
    with TestClient(app, raise_server_exceptions=True) as client:
        yield client