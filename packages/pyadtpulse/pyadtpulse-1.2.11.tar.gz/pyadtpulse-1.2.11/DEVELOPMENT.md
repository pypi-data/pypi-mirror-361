# PyADTPulse Development Guide

Welcome! This guide explains how to set up a local development environment for contributing to pyadtpulse.

---

## 📦 Requirements

Before you start, ensure you have installed:

- Any supported version of Python3
- The newest version of Git
- A code editor (e.g., VSCode)

---

## 🧪 Setting Up the Development Environment with `uv`

This project uses [`uv`](https://github.com/astral-sh/uv), a fast Python package manager, to manage dependencies.

### 🔧 Installation (one-time setup)

If you don't have `uv` installed yet see the uv [installation guide](https://docs.astral.sh/uv/getting-started/installation/)

---

### 📦 Setup Python Environment

**Note:** These steps will:

- Create the `.venv` virtual environment directory (even if it already exists)
- Install all dependencies from uv.lock into the `.venv`
- Update .git/hooks/pre-commit to use pre-commit installed in your .venv

From the root of the project, run:

- `uv sync`
- `uv run pre-commit install`

### Update vscode to use your .venv

- `ctrl + shift + p (Command Pallet)`
- `Python: Select Interpreter`
- Select the environment to use. should be: `./.venv/bin/python`

---

### Running Scripts

With uv, we don't need to activate the .venv to interact with it.

- new dependancies can be added using `uv add package_name`
- The .venv will be used automatically when running python scripts or packages using:
- `uv run ./script.py` or `uv run pytest tests` for example

### Updating python versions

.python-version is used by uv to install the correct version of python in the .venv
the requires-python field in pyproject.toml is used by uv to determine functioning versions of dependancies.

if the python version needs to be updated, the exact version to use should be updated in .python-version, and the pyproject.toml should be reviewed to ensure its criteria works with the .python-version

for example: if the pyproject.toml has requires-python == "3.13.3" and .python-version = 3.13.4, there will be issues.


### Distribute New Python Package to PyPi

uv build
uv publish --token {{pypi_secret}}
