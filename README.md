# Learning Abstract Algebra with Judson AATA

Workspace for self-study of Thomas W. Judson's *Abstract Algebra: Theory and Applications* using the 2021 print edition as the primary reading copy, with current online references, Pitt Math 0430 problem sets, MIT OCW notes, Sage examples, Python exercises managed by `uv`, and parallel Rust implementations.

## Current Study Policy

- Primary text: 2021 print/PDF edition of Judson AATA.
- Update check: compare against the official 2025 online/PDF edition and upstream Git tags.
- Primary exercise filter: Pitt Math 0430, especially Fall 2017 first, then Spring 2016 as supplemental.
- Secondary reference: MIT OCW 18.703 lecture notes and assignments.
- Coverage: all AATA chapters, with Chapter 7 (Cryptography) and Chapter 20 (Vector Spaces) treated as refresh chapters because they were already studied independently.
- Code workflow: write runnable Python exercises first, then implement the same idea as runnable Rust examples. Add checks only when they clarify a mathematical invariant.
- Sage workflow: use Sage/Runestone examples for computation-heavy algebra exploration, keeping local `.sage` files under `sage/`.

## Layout

- `docs/`: study workflow, resource notes, and AATA version notes.
- `tracking/`: chapter progress, exercise completion, and coding exercise status.
- `references/`: downloaded PDFs, course pages, problem sets, solutions, and generated diffs.
- `notes/`: chapter notes and reading summaries.
- `sage/`: local Sage examples and experiments.
- `code/`: runnable Python/Rust coding exercises and optional checks.
- `scripts/`: resource fetch and AATA diff helpers.

## Common Commands

```sh
uv sync
uv run python code/python/exercises/ch02_integers.py
```

```sh
cargo run --example ch02_integers
```

Optional checks:

```sh
uv run pytest
uv run ruff check
cargo test
```

Refresh downloaded references:

```sh
uv run python scripts/fetch_references.py
scripts/update_aata_diff.sh
```

Start exercise selection from `tracking/pitt-math0430-index.md`, then apply any known old-edition corrections from `docs/pitt-exercise-verification.md`.
