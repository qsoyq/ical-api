import os

import pytest
from fastapi.testclient import TestClient
from tests import AppTestSettings

from ical_api.main import app

RUN_EXTERNAL_INTEGRATION_TESTS = os.getenv("RUN_EXTERNAL_INTEGRATION_TESTS") == "1"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client


def test_redoc(client: TestClient):
    response = client.get("/redoc")
    assert response.status_code == 200


@pytest.mark.skipif(
    not RUN_EXTERNAL_INTEGRATION_TESTS,
    reason="external integration tests are disabled",
)
def test_vlrgg(client: TestClient):
    events = [2285]
    params = {"events": events}
    response = client.get("/api/ics/vlrgg/event/matches", params=params)
    assert response.status_code == 200, response.text


@pytest.mark.skipif(
    not RUN_EXTERNAL_INTEGRATION_TESTS,
    reason="external integration tests are disabled",
)
def test_gofans(client: TestClient):
    response = client.get("/api/ics/gofans/iOS.ics")
    assert response.status_code == 200, response.text

    response = client.get("/api/ics/gofans/macOS.ics")
    assert response.status_code == 200, response.text


def test_github_issues(client: TestClient):
    settings = AppTestSettings().github
    token = settings.test_github_token
    owner = settings.test_github_owner
    repo = settings.test_github_repo
    if not token or not owner or not repo:
        pytest.skip("GitHub integration test credentials are not configured")

    params = {
        "token": token,
        "owner": owner,
        "repo": repo,
    }
    response = client.get(f"/api/ics/github/issues/repos/{owner}/{repo}/issues.ics", params=params)
    assert response.status_code == 200, response.text
