# Security Policy

## Reporting

Report security issues privately to the repository owner instead of opening a public issue. Include the affected endpoint, expected impact, reproduction steps, and any relevant logs with secrets removed.

## Supported Versions

The `main` branch is the only supported development line for this project.

## Secrets

Do not commit API tokens, passwords, private keys, `.env` files, service account files, or production configuration. Use local `.env` files for development and GitHub Actions secrets for CI or deployment.

If a secret is committed by mistake:

1. Revoke or rotate the credential immediately.
2. Remove it from the repository history.
3. Open a private security report with the affected path and remediation status.
