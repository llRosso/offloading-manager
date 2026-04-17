from starlette.testclient import TestClient


class TestState:
    def test_get_robots(self, test: TestClient):
        response = test.get("/state/robots")
        assert response.status_code == 200
        assert isinstance(response.json(), list)