# Agent Harnesses

**This doc records operational harness facts for the v1 architecture.** The v0
single-repo Pi/OpenCode posture this file used to describe was superseded on
2026-07-06 by [redesign-plan.md](redesign-plan.md); Phase 0 of that plan
executed the split. Pi is gone (`.pi/` deleted, unanimous across the design
review). Read the plan first; this doc only pins the details the plan leaves
operational.

## Current shape

- **Two repos.** This workbench (dev agents: Claude Code / Codex, guided by
  `AGENTS.md`) and `~/dev/oth/github/tooter-studies` (the tutor's cwd, always).
  The geometry invariant — no agent instruction/config files in `~/dev`,
  `~/dev/oth`, `~/dev/oth/github` (the tutor's ancestry) — makes instruction
  leakage between the two roles impossible by construction. Verified
  2026-07-06; re-verified 2026-07-30 after the move to `~/dev/oth/github`;
  re-verify whenever something new lands in those directories.
- **Tutor.** opencode primary agent `math-pedagogy`, compiled from `tutor/`
  sources by `just deploy` into `tooter-studies/.opencode/` +
  `opencode.jsonc`. The deployed config is enforcement, not prose: `edit` and
  `bash` deny-by-default with narrow allowlists (state/attempts writable,
  `tooter-state *`/`just *` runnable), built-in `build`/`plan` agents
  disabled, sharing disabled.
- **Moves.** `/hint`, `/assess-solution`, `/chapter-plan`, `/exit-check`,
  `/transfer-problem` (Phase 1 adds `/start`, `/review-paper`, `/progress`).
  The `/command` grammar is itself pedagogical ritual — keep it on every
  surface.
- **State.** `state-layer/` package; CLI `tooter-state` installed as an
  editable uv tool (`just install-state` here, `just setup` in the studies
  repo). MCP face with identical functions lands in Phase 1.
- **Surfaces.** TUI is the always-working floor; `opencode web` becomes the
  daily surface after the Phase-1 hour-one check (KaTeX + image attach on real
  transcripts). `just study` in the studies repo launches the tutor with
  external-skill discovery disabled (see leak note below).
- **Drift.** `just deploy --check` — run on a weekly schedule, never at
  study-session start (a maintenance prompt at study time is a study-killer).

## opencode pin + upgrade ritual (plan §3.4, §11)

- **Pinned: opencode 1.17.13**, Homebrew formula, `brew pin opencode` applied
  2026-07-06. Upgrade with `brew unpin opencode && brew upgrade opencode`,
  then re-pin.
- Upgrades happen on a **scheduled quarterly evening**, never mid-study-week.
  opencode moves fast and its web assets are proxied from app.opencode.ai, so
  an upgrade is a deliberate act against this smoke checklist:
  1. **Permission semantics** — in `tooter-studies`: an edit outside
     `studies/*/state/**` / `studies/*/attempts/**` is denied; `tooter-state due`
     and `just --list` run without prompts; any other bash command is denied;
     `opencode agent list` shows `math-pedagogy` and does **not** show
     `build`/`plan`/`general`/`explore` (internal `compaction`/`summary`/`title`
     remaining listed is normal).
  2. **KaTeX rendering** — a real transcript with inline and display math
     renders in `opencode web` (Phase 1 onward).
  3. **Image attach** — a real page scan attaches and is readable in the
     session (Phase 1 onward).
  4. **Discovery** — `/hint` et al. appear in the command palette;
     `opencode debug skill` (with the `just study` env vars) lists exactly the
     four `math-*` skills plus opencode's built-in `customize-opencode` (which
     cannot be unlisted — registered in code — but is permission-denied in the
     deployed config).
  5. **Deploy integrity** — `just deploy --check` still reports clean.
- Rollback: `brew` keeps the previous keg; `brew switch`-style rollback is
  gone, so reinstall the pinned version from the formula history if a smoke
  step fails, and re-pin.

## Known leak, closed operationally

opencode auto-loads "external skills" from `~/.claude/skills/` and
`~/.agents/skills/` — dev/tooling skills would surface inside tutoring
sessions. There is no config key for this; only env vars. `just study` sets
`OPENCODE_DISABLE_EXTERNAL_SKILLS=1 OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1`.
Launching bare `opencode` in the studies repo works but reopens that leak —
use `just study`. (Skill *use* still requires an ask either way; the leak is
their descriptions entering tutor context.)

Residual, accepted: the built-in `customize-opencode` skill is registered in
opencode's code (a default plugin), survives both env vars, and cannot be
unlisted. Its description remains in tutor context; its use is hard-denied via
`permission.skill` in the deployed config. Re-check this on every version bump
in case more built-ins appear.

## Where things that used to be here went

| v0 (this repo, deleted)            | v1 home                                          |
| ---------------------------------- | ------------------------------------------------ |
| `.pi/` prompts/skills/append       | deleted; opencode is the single tutor harness    |
| `.opencode/` agent/commands/skills | sources in `tutor/`, deployed to `tooter-studies` |
| root `opencode.jsonc`              | source `tutor/opencode.jsonc`, deployed          |
| `studies/`, `references/`, `notes/` | `tooter-studies` (private repo)                  |
| `state/progress.md` + `code-exercises.md` tables | state layer (`chapters.yaml`, `exercises/*.yaml`); `progress.md` survives as the boundary view |
