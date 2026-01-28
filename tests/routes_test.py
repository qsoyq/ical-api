import pytest
from fastapi.testclient import TestClient
from tests import TestSettings

from ical_api.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client


def test_redoc(client: TestClient):
    response = client.get("/redoc")
    assert response.status_code == 200


def test_vlrgg(client: TestClient):
    events = [2285]
    params = {"events": events}
    response = client.get("/api/ics/vlrgg/event/matches", params=params)
    assert response.status_code == 200, response.text


def test_gofans(client: TestClient):
    response = client.get("/api/ics/gofans/iOS.ics")
    assert response.status_code == 200, response.text

    response = client.get("/api/ics/gofans/macOS.ics")
    assert response.status_code == 200, response.text


def test_github_issues(client: TestClient):
    token = TestSettings().github.test_github_token
    owner = TestSettings().github.test_github_owner
    repo = TestSettings().github.test_github_repo
    assert token and owner and repo
    params = {
        "token": token,
        "owner": owner,
        "repo": repo,
    }
    response = client.get(f"/api/ics/github/issues/repos/{owner}/{repo}/issues.ics", params=params)
    assert response.status_code == 200, response.text
