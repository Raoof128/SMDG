# Security Policy

## Reporting
- Report vulnerabilities to `security@example.com` with a short description, reproduction steps, and potential impact.
- We aim to acknowledge reports within three business days and provide remediation guidance within ten business days.

## Scope and Data Handling
- The generator only produces synthetic data; no real patient data should be ingested or emitted.
- Avoid introducing real identifiers in tests, examples, or configuration files.

## Dependency Hygiene
- Dependencies are declared in `pyproject.toml` and `requirements.txt`; use `pip install -e .[dev]` for reproducible installs.
- Run `make check` (ruff, black, pytest) before publishing changes. Consider `pip-audit` for dependency scanning in CI when available.

## Supported Versions
Security fixes apply to the `main` branch and the latest tagged release. When in doubt, update to the most recent tag.
