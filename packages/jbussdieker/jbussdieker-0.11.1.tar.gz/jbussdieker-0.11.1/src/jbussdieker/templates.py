from string import Template

PYPROJECT_TEMPLATE = Template(
    """\
[project]
name = "$project_name"
version = "0.0.0"
description = "A helpful CLI and project generator."
readme = "README.md"
requires-python = ">=3.9"
authors = [
  { name = "Joshua B. Bussdieker", email = "jbussdieker@gmail.com" }
]
maintainers = [
  { name = "Joshua B. Bussdieker", email = "jbussdieker@gmail.com" }
]
classifiers = [
  "Topic :: Software Development :: Build Tools",
  "Development Status :: 3 - Alpha",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.9",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
  "Operating System :: OS Independent",
  "Environment :: Console",
  "Intended Audience :: Developers",
  "Natural Language :: English",
  "Typing :: Typed",
]
license = "MIT"
license-files = ["LICENSE.txt"]

[project.scripts]
$project_name = "$project_name.cli:main"

[project.urls]
Homepage = "https://github.com/jbussdieker/python-$project_name"
Documentation = "https://github.com/jbussdieker/python-$project_name/blob/main/README.md"
Repository = "https://github.com/jbussdieker/python-$project_name"
Issues = "https://github.com/jbussdieker/python-$project_name/issues"
Changelog = "https://github.com/jbussdieker/python-$project_name/blob/main/CHANGELOG.md"

[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"
"""
)

LICENSE_TEMPLATE = Template(
    """\
MIT License

Copyright (c) 2025 Joshua B. Bussdieker

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
)

WORKFLOW_TEMPLATE = """\
name: release-please
on:
  push:
permissions:
  contents: write
  pull-requests: write
  issues: write
  actions: write
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}
          restore-keys: ${{ runner.os }}-pip-
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install lint tools
        run: pip install black mypy
      - name: Run black --check
        run: black --check .
      - name: Run mypy
        run: mypy src/
  test:
    runs-on: ubuntu-latest
    needs: lint
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12", "3.13"]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}-${{ matrix.python-version }}
          restore-keys: ${{ runner.os }}-pip-
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: pip install .
        run: pip install .
      - name: python -m unittest
        run: python -m unittest
  coverage:
    runs-on: ubuntu-latest
    needs: lint
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12", "3.13"]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}-${{ matrix.python-version }}
          restore-keys: ${{ runner.os }}-pip-
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: pip install coverage
        run: pip install coverage
      - name: pip install .
        run: pip install .
      - name: coverage run
        run: coverage run --source %PROJECT_NAME% -m unittest
      - name: coverage report
        run: coverage report -m --fail-under 100
  release-please:
    runs-on: ubuntu-latest
    needs: [lint, test, coverage]
    steps:
      - name: release-please
        if: github.ref == 'refs/heads/main'
        id: release-please
        uses: googleapis/release-please-action@v4
        with:
          release-type: python
      - name: checkout
        if: steps.release-please.outputs.release_created
        uses: actions/checkout@v4
      - name: trigger-publish
        if: steps.release-please.outputs.release_created
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          TAG_NAME: ${{ steps.release-please.outputs.tag_name }}
        run: gh workflow run publish.yml -f tag_name=${TAG_NAME}
"""

WORKFLOW_PUBLISH_SCRIPT = """\
name: publish
on:
  workflow_dispatch:
    inputs:
      tag_name:
        description: 'Tag name'
        required: true
        type: string
permissions:
  id-token: write
  contents: write
  pull-requests: write
jobs:
  publish:
    runs-on: ubuntu-latest
    environment: release
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}
          restore-keys: ${{ runner.os }}-pip-
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install build tools
        run: pip install build twine
      - name: Build package
        run: python -m build
      - name: Twine check
        run: twine check --strict dist/*
      - name: Publish to GitHub Releases
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          TAG_NAME: ${{ inputs.tag_name }}
        run: gh release upload ${{ inputs.tag_name }} dist/*
      - name: Publish to PyPI
        run: twine upload dist/*
"""

GITIGNORE = """\
dist/
build/
*.egg-info/
__pycache__/
.venv/
.coverage
"""

MAKEFILE_TEMPLATE = """\
build:
	python3 -m build .
install:
	pip install --break-system .
test-installed:
	python3 -m unittest discover
upgrade:
	pip install --upgrade --break-system %PROJECT_NAME%

coverage: .venv/bin/coverage .venv/bin/%PROJECT_NAME%
	.venv/bin/coverage run --source src -m unittest $(TEST)
	.venv/bin/coverage report -m --fail-under=100
test: .venv/bin/%PROJECT_NAME%
	.venv/bin/python3 -m unittest $(TEST)
.venv/bin/%PROJECT_NAME%: .venv/bin/python
	.venv/bin/pip install -e .
.venv/bin/coverage: .venv/bin/python
	.venv/bin/pip install coverage
.venv/bin/python:
	python3 -m venv .venv

clean:
	rm -rf dist build .venv
"""

TEST_TEMPLATE = Template(
    """\
import unittest

import $project_name


class TestPackage(unittest.TestCase):
    def test_version(self):
        self.assertIn("__version__", dir($project_name))


if __name__ == "__main__":
    unittest.main()
"""
)
