# ical-api

Calendar subscription api

## Tech Stack

- Python 3.10+
- FastAPI
- Typer
- Uvicorn / Hypercorn
- Pydantic Settings
- uv
- pytest, Ruff, mypy, pre-commit

## Local Setup

```bash
uv sync
```

Copy `.env.example` to `.env` only for local development. Never commit `.env` or real credentials.

## Run

```bash
uv run ical-api-server
```

## Install

```bash
pip install git+https://github.com/qsoyq/ical-api.git
```

## Test

```bash
uv run pytest -q
```

Run the full local validation suite:

```bash
uv run pre-commit run --all-files
uv run ruff check .
uv run ruff format --check .
uv run mypy ical_api tests
```

GitHub integration tests require the optional `test_github_token`, `test_github_owner`, and `test_github_repo` values in `.env`. They are skipped when those values are absent.

External network integration tests are disabled by default because they depend on third-party site availability and page structure. Run them explicitly with:

```bash
RUN_EXTERNAL_INTEGRATION_TESTS=1 uv run pytest -q
```

To run only the external site tests:

```bash
RUN_EXTERNAL_INTEGRATION_TESTS=1 uv run pytest -q tests/routes_test.py::test_vlrgg tests/routes_test.py::test_gofans
```

To run only the GitHub issues integration test after configuring the required `.env` values:

```bash
uv run pytest -q tests/routes_test.py::test_github_issues
```

## Build

```bash
uv build
```

## Release

1. Confirm `main` is green in CI.
2. Update `pyproject.toml` version.
3. Record validation evidence and rollback notes in `docs/release/`.
4. Tag the release from `main`.

Rollback is handled by reverting the release commit or deploying the previous known-good tag.

## Branch Strategy

This repository uses GitHub Flow:

- `main` is the protected integration branch.
- Work happens on issue-linked branches named `<type>/<issue-id>-<short-description>`.
- Pull requests require CI, review, and a complete PR template before merge.

## Documentation

- `CONTRIBUTING.md`: development workflow and validation.
- `SECURITY.md`: vulnerability reporting and secret handling.
- `docs/decisions/`: architecture and process decisions.
- `docs/release/`: release and rollback notes.
- `docs/postmortems/`: incident reviews.

## Maintainer

Maintained by `@qsoyq`.

## Configuration

Runtime settings are read from environment variables and local `.env` files through Pydantic Settings.

Common variables:

```text
basic_auth_username
basic_auth_password
vlrgg_fetch_match_time_semaphore
http_host
http_port
http_reload
log_level
```
