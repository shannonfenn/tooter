default:
    @just --list

# Run a Python exercise, e.g. `just py ch02_integers`
py name:
    uv run python code/python/exercises/{{name}}.py

# Run the matching Rust example, e.g. `just rs ch02_integers`
rs name:
    cargo run --example {{name}}

# Run both Python and Rust versions of an exercise.
exercise name:
    uv run python code/python/exercises/{{name}}.py
    cargo run --example {{name}}

# Run optional checks.
check:
    uv run pytest
    uv run ruff check
    cargo test

