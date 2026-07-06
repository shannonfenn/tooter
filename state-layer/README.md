# state-layer — `tooter-state`

Structured learner state for tooter study workspaces (redesign-plan.md §3.3).
One set of functions, two faces: this CLI today, a ~150-line stdio MCP server
in Phase 1, so every present and future surface consumes identical state.

## State files (in the active pack's `state/`)

- `chapters.yaml` — chapter-level study state (structured source behind `progress.md`).
- `exercises/chNN.yaml` — per-exercise records: `status ∈ {unseen, attempted,
  needs-review, proved, re-derived, transfers-ok, retired}` (deliberately no
  "mastered"), pattern tags, attempts count, last_attempt, next_review, note.
- `attempts.jsonl` — append-only ledger: `{ts, exercise, kind: attempt|stuck-here,
  verdict, hint_depth, image_paths, tutor_summary}`. Never edited; this package
  exposes no rewrite path.
- `misconceptions.md` — tutor-curated prose; not owned by this package.
- `queue.md`, `dashboard.html` — derived views; regenerated, disposable.

## CLI

```sh
tooter-state record-attempt --exercise 4.5 --verdict mostly-correct \
    --hint-depth 2 --image attempts/2026/p1.png --summary "well-definedness gap"
tooter-state update-status --exercise 4.5 --status proved
tooter-state due [--days 7]
tooter-state build-queue
tooter-state render-dashboard
```

Workspace resolution: `--root`, else `$TOOTER_STUDIES_ROOT`, else walk up from
cwd to the nearest `studies/active.md`. The active pack comes from that file.

## Scheduling

Expanding ladder 1/3/7/21/60 days on `proved` / `re-derived` / `transfers-ok`;
`needs-review` resets the ladder and returns tomorrow. FIRe-lite: a `proved`
exercise pushes scheduled siblings sharing its patterns *outward* (never
inward). `py-fsrs` is a later drop-in only if interval feel proves wrong.

## Install into the studies workspace

```sh
uv tool install --editable ~/dev/src/github/tooter/state-layer   # or `just setup` there
```

## Dev

```sh
uv run --directory state-layer pytest
uv run --directory state-layer ruff check
```

`scripts/seed_state.py` is the one-shot Phase-0 migration from the v0
hand-edited tables; see its docstring.
