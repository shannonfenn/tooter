# tooter workbench — agent instructions

This repo is the **dev workbench** for a personal AI math-tutoring system. No
tutoring happens here. The tutor runs in `~/dev/oth/github/tooter-studies` (a
separate private repo that is the tutor's cwd, always) and everything it needs
is compiled and deployed from here. You are a software/docs agent working on
tutor-core prose, the state layer, the compiler, and documentation.

## Map

- `docs/redesign-plan.md` — the adopted v1 plan. Read §3 before structural
  changes; §9's decision triggers are pre-committed — don't relitigate them.
- `tutor/` — tutor-core **sources** (agent, commands, instructions, skills,
  enforced opencode config). Single source of truth for everything under
  `tooter-studies/.opencode/` and its `opencode.jsonc`.
- `scripts/deploy.py` — the compiler: dumb manifest copy, `just deploy`,
  drift check via `just deploy --check`.
- `state-layer/` — `tooter-state` Python package (schemas, CLI; MCP face lands
  in Phase 1). uv project; tests under `state-layer/tests/`.
- `docs/pedagogy-for-tutoring.md` — pedagogy reference; deployed to the tutor
  as an on-demand reference file.

## Rules

- Never edit `tooter-studies/.opencode/**` or `tooter-studies/opencode.jsonc`
  directly — edit `tutor/` here and run `just deploy`.
- Never write learner state from this repo. State files live in
  `tooter-studies/studies/*/state/`; `attempts.jsonl` is append-only by
  contract and nothing may rewrite it.
- Geometry invariant: never create agent instruction/config files
  (`AGENTS.md`, `CLAUDE.md`, `.claude/`, `opencode.jsonc`, …) in `~/dev`,
  `~/dev/oth`, or `~/dev/oth/github` — the tutor's ancestry.
- Keep tutor-core prose pedagogical: no software-development workflow language
  in `tutor/` files.
- After changing `tutor/` or `docs/pedagogy-for-tutoring.md`, run
  `just deploy`; after changing `state-layer/`, run `just check`.

## Commands

```sh
just deploy            # compile tutor-core into ~/dev/oth/github/tooter-studies
just deploy --check    # drift report only (weekly ritual, never at study time)
just test / lint / check
just install-state     # (re)install the tooter-state CLI as an editable uv tool
```
