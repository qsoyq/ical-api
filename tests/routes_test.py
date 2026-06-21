import os

import pytest
from bs4 import BeautifulSoup
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


def test_vlrgg(client: TestClient):
    events = [2765]
    params = {"events": events}
    response = client.get("/api/ics/vlrgg/event/matches.ics", params=params)
    assert response.status_code == 200, response.text
    assert "BEGIN:VCALENDAR" in response.text
    assert "Valorant Masters London 2026" in response.text
    assert "670471" in response.text


def test_vlrgg_event_parser_supports_current_event_header():
    from ical_api.applications.vlrgg.router import (
        parse_vlrgg_event_matches,
        parse_vlrgg_event_title,
    )

    document = BeautifulSoup(
        """
        <h1 class="event-header-main-title">Valorant Masters London 2026</h1>
        <div class="wf-card">
            <a href="/670471/paper-rex-vs-leviat-n-valorant-masters-london-2026-gf"
               class="wf-module-item match-item mod-color">
                <div class="match-item-vs-team-name"><div class="text-of">Paper Rex</div></div>
                <div class="match-item-vs-team-name"><div class="text-of">LEVIATÁN</div></div>
            </a>
        </div>
        """,
        "lxml",
    )

    title = parse_vlrgg_event_title(document)
    events = parse_vlrgg_event_matches(document, title)

    assert title == "Valorant Masters London 2026"
    assert len(events) == 1
    assert events[0].name == "Paper Rex vs LEVIATÁN"
    assert events[0].description == "Valorant Masters London 2026"
    assert events[0].url == "https://www.vlr.gg/670471/paper-rex-vs-leviat-n-valorant-masters-london-2026-gf"


def test_vlrgg_event_parser_keeps_legacy_title_selector():
    from ical_api.applications.vlrgg.router import parse_vlrgg_event_title

    document = BeautifulSoup(
        """
        <h1 class="wf-title">Legacy VLR Event</h1>
        """,
        "lxml",
    )

    assert parse_vlrgg_event_title(document) == "Legacy VLR Event"


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
