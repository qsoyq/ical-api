import pytest
from fastapi.testclient import TestClient

from python_fastapi_template.main import app


@pytest.fixture(scope='module')
def client():
    with TestClient(app) as client:
        yield client


def test_redoc(client: TestClient):
    response = client.get('/redoc')
    assert response.status_code == 200
