---
name: aata-code-exercises
description: Build and verify Sage, Python, and Rust exercises for Judson AATA using uv-managed Python and Python-first-then-Rust implementations. Use for computational examples, coding exercises, tests, and code recommendations tied to covered algebra concepts.
---

# AATA Code Exercises

Use this skill when the user asks for Sage examples, Python exercises, Rust implementations, computational checks, tests, or code recommendations related to AATA study.

## Required Context

Before coding, check:

- `README.md` for repository layout and commands.
- `docs/workflow.md` for the coding loop.
- `tracking/progress.md` for covered chapters and current likely chapter.
- `tracking/code-exercises.md` for code exercise status.
- `pyproject.toml` for Python environment and tooling.

## Code Policy

- Python is managed by `uv`; run Python commands with `uv run`.
- Prefer runnable exercise files over package-style code.
- Put Python exercises in `code/python/exercises/` and run them directly with `uv run python`.
- Put reusable Rust routines in `code/rust/aata_judson/src/` and runnable examples in `code/rust/aata_judson/examples/`.
- Implement Python first, then Rust with matching behavior.
- Add tests only when they sharpen mathematical feedback, such as testing an invariant over many inputs.
- Keep chapter-specific code direct until repetition justifies abstraction.
- Recommend coding exercises only when they directly reinforce the current chapter's covered concepts.
- Defer programs that mainly exercise later definitions, and state which later chapter they belong to.

## Local Commands

Use whichever commands are available in the environment:

```sh
uv sync
just ch02
just exercise ch02
just test
just check
uv run python code/python/exercises/ch02.py
cargo run --example ch02
uv run pytest
uv run ruff check
cargo test
scripts/update_aata_diff.sh
```

If a tool is missing, report that explicitly and continue with the parts that can be verified.

## Covered-Work Discipline

Keep computational examples and recommendations scoped to the current chapter and completed earlier chapters unless the user asks for a preview. If an implementation naturally belongs to a later chapter, label it as deferred or preview material.
