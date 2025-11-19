PYTHON ?= python

.PHONY: install format lint test check

install:
	$(PYTHON) -m pip install -e .[dev]

format:
	$(PYTHON) -m black .

lint:
	$(PYTHON) -m ruff check .

test:
	$(PYTHON) -m pytest

check: format lint test
