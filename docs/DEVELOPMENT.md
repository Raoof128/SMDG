# Development Guide

## Environment
- Python 3.11+ recommended
- Install dependencies: `python -m venv .venv && source .venv/bin/activate && pip install -e .[dev]`

## Quality Gates
- Format: `black .`
- Lint: `ruff check .`
- Tests: `pytest`
- All commands are wired into the `Makefile` (`make format`, `make lint`, `make test`, `make check`).

## Contributing Workflow
1. Create a feature branch.
2. Run `make check` locally to ensure formatting, linting, and tests pass.
3. Update documentation for new behavior.
4. Submit a pull request with a concise summary and testing notes.

## Release Checklist
- Bump the `version` field in `pyproject.toml`.
- Regenerate or validate example outputs if formats changed.
- Tag the release and publish the built package if distributing via PyPI.
