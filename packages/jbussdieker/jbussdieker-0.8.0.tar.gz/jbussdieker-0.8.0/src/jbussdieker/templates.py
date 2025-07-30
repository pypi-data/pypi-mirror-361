from string import Template

PYPROJECT_TEMPLATE = Template(
    """\
[project]
name = "$project_name"
version = "0.1.0"
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
