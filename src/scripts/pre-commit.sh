#!/bin/sh

PROJECT_SRC_DIR=./src

echo "Running pre-commit script"

echo "Python - sorting imports"
poetry run isort $PROJECT_SRC_DIR

echo "Python - formatting code"
poetry run ruff format $PROJECT_SRC_DIR

echo "Python - linting code"
poetry run ruff check $PROJECT_SRC_DIR

echo "Python - running type checks"
poetry run mypy --strict $PROJECT_SRC_DIR

