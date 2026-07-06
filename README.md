# Tooter

Workbench for a personal AI math-tutoring system. This repo owns the two
portable contracts — the **tutor-core** prose and the **state layer** — and
compiles them outward; the tutoring itself happens in the sibling study
workspace, [`tooter-studies`](../tooter-studies) (private), which is the
tutor's working directory, always.

Architecture, phasing, and decision triggers: [docs/redesign-plan.md](docs/redesign-plan.md)
(adopted 2026-07-06). In short: own two contracts, rent every surface.

## Layout

- `tutor/` — tutor-core sources: the `math-pedagogy` agent, the `/command`
  moves, always-loaded instructions, skills, and the permission-enforced
  `opencode.jsonc`. Compiled one-way into `tooter-studies` by `just deploy`.
- `state-layer/` — the `tooter-state` Python package: chapter/exercise YAML
  schemas, append-only attempt ledger, review scheduling, CLI face (a stdio
  MCP face with the same functions arrives in Phase 1).
- `scripts/deploy.py` — the compiler (dumb manifest copy + drift check).
- `docs/` — the redesign plan, pedagogy reference (deployed to the tutor),
  harness notes, and archived design-review research.

## Commands

```sh
just deploy            # compile tutor-core + config into ../tooter-studies
just deploy --check    # drift check (run weekly, never at study-session start)
just test              # state-layer tests
just check             # tests + lint
just install-state     # install the tooter-state CLI as an editable uv tool
```

## The two-repo rule

Dev agents (Claude Code / Codex) work only here, guided by `AGENTS.md`. The
tutor works only in `tooter-studies`, guided by the deployed config. Neither
repo's instructions can reach the other, and no ancestor directory of either
may hold agent instruction/config files (the geometry invariant — see the
studies repo README).
