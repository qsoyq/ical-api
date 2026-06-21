# Contributing

## Development Flow

1. Create or pick up a GitHub issue before starting non-trivial work.
2. Create a branch from `main` using `<type>/<issue-id>-<short-description>`, for example `fix/12-calendar-timezone`.
3. Keep the branch focused on the issue scope.
4. Open a pull request using the repository PR template.

## Local Setup

```bash
uv sync
```

Run the application:

```bash
uv run ical-api-server
```

## Validation

Run these before committing:

```bash
uv run pre-commit run --all-files
uv run pytest -q
```

If a test needs external credentials, it must skip when credentials are not present. Do not commit local `.env` files or secrets.

## Commit Messages

Use Conventional Commit format:

```text
<type>: <short summary> (#<issue-id>)
```

Common types are `feat`, `fix`, `docs`, `ci`, `chore`, `refactor`, and `test`.
