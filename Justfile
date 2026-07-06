default:
    @just --list

# Compile tutor-core + config into the studies repo; `just deploy --check` reports drift only.
deploy *ARGS:
    python3 scripts/deploy.py {{ARGS}}

# Run state-layer tests.
test:
    uv run --directory state-layer pytest

# Run state-layer linting.
lint:
    uv run --directory state-layer ruff check

# Run tests and linting.
check: test lint

# Install the tooter-state CLI as an editable uv tool (what tooter-studies' `just setup` calls).
install-state:
    uv tool install --editable state-layer --force
