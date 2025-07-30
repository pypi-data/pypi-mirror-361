.PHONY: all build install test-installed upgrade setup coverage test clean

all: coverage
build:
	python3 -m build .
install:
	pip install --break-system .
test-installed:
	python3 -m unittest discover
upgrade:
	pip install --upgrade --break-system jbussdieker

setup: .venv/lib/*/site-packages/__editable__.*
test: setup
	.venv/bin/python3 -m unittest $(TEST)
coverage: setup .venv/bin/coverage
	.venv/bin/coverage run --source src -m unittest $(TEST)
	.venv/bin/coverage report -m --fail-under=100
format: .venv/bin/black
	.venv/bin/black .
lint: .venv/bin/black
	.venv/bin/black --check .
clean:
	rm -rf dist build .venv
.venv/bin/black: .venv/bin/python
	.venv/bin/pip install black
.venv/bin/coverage: .venv/bin/python
	.venv/bin/pip install coverage
.venv/lib/*/site-packages/__editable__.*: .venv/bin/python pyproject.toml
	.venv/bin/pip install -e .
.venv/bin/python:
	python3 -m venv .venv
