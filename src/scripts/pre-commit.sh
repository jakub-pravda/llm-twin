#!/usr/bin/env bash

PROJECT_SRC_DIR=./src

echo "Running pre-commit script"

echo "Python - formatting code"
ruff format $PROJECT_SRC_DIR

echo "Python - linting code (fixing automatically)"
ruff check --fix $PROJECT_SRC_DIR

echo "Python - running type checks"
poetry run mypy --strict $PROJECT_SRC_DIR

