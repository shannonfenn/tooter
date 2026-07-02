# Mathematics Study Workspace

Workspace for self-study of mathematics texts using reusable Pi/OpenCode pedagogy roles and text-specific study packs. The active study pack is currently Thomas W. Judson's *Abstract Algebra: Theory and Applications* (AATA).

## Active Study Pack

- Active selector: `studies/active.md`.
- Current pack: `studies/judson-aata/`.
- Primary text: 2021 print/PDF edition of Judson AATA.
- Text-specific policy, source priority, workflow, progress, and exercise tracking live in the active study pack.
- Computational learning workflow: write runnable Python or Sage exercises. Add tests only when they clarify a mathematical invariant.
- Agent harnesses: Codex is used for repository development; Pi resources under `.pi/` and OpenCode resources under `.opencode/` provide teaching roles. This repo intentionally avoids `AGENTS.md` so general coding agents are not forced into tutor behavior.

## Layout

- `studies/`: text-specific study packs, helper scripts, and the active-study selector.
- `docs/`: cross-text pedagogy and harness documentation.
- `references/`: downloaded PDFs, course pages, problem sets, solutions, and generated diffs.
- `notes/`: chapter notes and reading summaries.
- `.pi/`: Pi harness resources for tutoring, assessment, planning, and programming exercises.
- `.opencode/`: OpenCode harness resources for the same pedagogical workflows.

## Agent Harnesses

See `docs/agent-harnesses.md` for the v0 Pi/OpenCode setup, role boundaries, and usage notes.

## Computational Learning Commands

With `just` installed:

```sh
just ch03-groups
just exercise ch03_groups
```

Without `just`:

```sh
uv sync
uv run python studies/judson-aata/code/python/exercises/ch03_groups.py
```

## Development Commands

Optional tests and lint:

```sh
just test
just check
uv run pytest
uv run ruff check
```

Refresh downloaded references:

```sh
uv run python studies/judson-aata/scripts/fetch_references.py
studies/judson-aata/scripts/update_aata_diff.sh
```

For the Judson AATA pack, start exercise selection from `studies/judson-aata/exercises/index.md`, then apply any known old-edition corrections from `studies/judson-aata/exercises/verification.md`.
