default:
    @just --list

# Run a Python exercise, e.g. `just py ch02`
py name:
    uv run python code/python/exercises/{{name}}.py

# Run the matching Rust example, e.g. `just rs ch02`
rs name:
    cargo run --example {{name}}

# Run both Python and Rust versions of an exercise.
exercise name:
    uv run python code/python/exercises/{{name}}.py
    cargo run --example {{name}}

# Run optional tests.
test:
    uv run pytest
    cargo test

# Run Python linting.
lint:
    uv run ruff check

# Run tests and linting.
check: test lint
