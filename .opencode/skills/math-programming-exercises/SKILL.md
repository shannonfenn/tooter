---
name: math-programming-exercises
description: Design, run, and critique learner-facing mathematical programming exercises for the active study pack using Sage and uv-managed Python. Use for small practice programs, finite checks of definitions, focused invariant checks, and code recommendations tied to covered concepts.
---

# Math Programming Exercises

Use this skill when the user asks for Sage examples, Python exercises, programming tasks, finite mathematical checks, focused tests, or code recommendations related to the active mathematics study pack.

## Required Context

Before designing or running a programming exercise, check:

- `studies/active.md` to identify the active study pack.
- The active study pack's `profile.md`, `state/progress.md`, and `state/code-exercises.md` when present.
- `README.md` and the active study pack's `workflow.md` for repository layout and commands.
- `pyproject.toml` only when running uv-managed Python is needed.

## Code Policy

- Python is managed by `uv`; run Python commands with `uv run`.
- Prefer runnable exercise files over package-style code.
- Put practice code inside the active study pack's `code/` directory; for Python exercises, use `code/python/exercises/` within that pack and run files directly with `uv run python`.
- Add tests only when they sharpen mathematical feedback, such as testing an invariant over many inputs.
- Keep text- or chapter-specific code direct until repetition justifies abstraction.
- Recommend programming exercises only when they directly reinforce the active study pack's covered concepts.
- Defer programs that mainly exercise later definitions, and state where they belong in the active text.
- Do not perform general repository maintenance, project setup, full-project linting, reference refreshes, or product-style implementation work; this role is limited to pedagogy.

## Local Commands

Use whichever commands are available in the environment:

```sh
uv sync
just ch03-groups
just exercise ch03_groups
just test
just check
uv run python studies/judson-aata/code/python/exercises/ch03_groups.py
uv run pytest
uv run ruff check
studies/judson-aata/scripts/update_aata_diff.sh
```

If a tool is missing, report that explicitly and continue with the parts that can be verified.

## Covered-Work Discipline

Keep programming examples and recommendations scoped to the current section/chapter and completed earlier material unless the user asks for a preview. If an implementation naturally belongs later in the active text, label it as deferred or preview material.
