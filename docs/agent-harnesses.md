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
- **Moves.** `/start`, `/hint`, `/assess-solution`, `/review-paper`,
  `/chapter-plan`, `/exit-check`, `/transfer-problem`, `/progress` (complete
  as of Phase 1). The `/command` grammar is itself pedagogical ritual — keep
  it on every surface. `/start` and `/progress` inject live state through
  opencode command-template shell interpolation (`` !`tooter-state due` ``),
  which runs the command at invocation and pastes its output into the prompt —
  the session-open ritual is mechanized, not remembered.
- **State.** `state-layer/` package; CLI `tooter-state` installed as an
  editable uv tool (`just install-state` here, `just setup` in the studies
  repo). The MCP face (`tooter-state-mcp`, stdio, Phase 1) exposes the same
  functions over shared `ops.py`; it is deliberately **not** mounted in
  opencode — the tutor keeps the bash-allowlisted CLI; the MCP face is for
  future surfaces (claude.ai Project, custom app).
- **Surfaces.** `opencode web` is the daily surface (Phase-1 hour-one check
  passed headlessly 2026-07-30; final judgment on a real transcript is in
  `phase1-handoff.md`). `just study` regenerates queue + dashboard, opens the
  dashboard, and launches `opencode web` on the **fixed port 4096** (stable
  browser origin = stable client-side state; the server binds 127.0.0.1,
  unsecured — fine for localhost single-user). TUI via `just study-tui` is the
  always-working floor. Both set the external-skill env vars (leak note
  below).
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
     renders in `opencode web`.
  3. **Image attach** — a real page scan attaches and is readable in the
     session.
  4. **Discovery** — `/hint` et al. appear in the command palette;
     `opencode debug skill` (with the `just study` env vars) lists exactly the
     four `math-*` skills plus opencode's built-in `customize-opencode` (which
     cannot be unlisted — registered in code — but is permission-denied in the
     deployed config).
  5. **Deploy integrity** — `just deploy --check` still reports clean.
  6. **Command-template shell injection** — `/start` still expands
     `` !`tooter-state due` `` (export a session and look for the injected
     block); an upgrade that breaks interpolation silently un-mechanizes the
     session-open ritual.
  7. **Web project registry** — the tooter-studies project in `opencode web`
     opens at `~/dev/oth/github/tooter-studies` with only Math-Pedagogy in the
     agent picker (see registry note below).

## opencode web project registry (repo moves)

opencode keys each project by its git root commit and **pins the worktree
path** in `~/.local/share/opencode/opencode.db` (`project.worktree`). Moving a
repo does not update it: after the Phase-0 relocation, the web UI resolved the
project to the old `~/dev/src/...` path and booted a phantom instance there —
**no repo `opencode.jsonc`, so no permission enforcement, default SWE agents,
zero tutor config**. The TUI never hits this (it uses the launch cwd).

Fixed 2026-07-30: server stopped, DB backed up
(`opencode.db.bak-20260730`), `project.worktree` updated to the oth path,
client localStorage cleared. If the studies repo ever moves again: expect the
same symptom (web project header shows the old path; agent picker shows
Build/Plan), and apply the same one-column fix — or delete the project row and
let opencode re-register it, accepting the loss of session history bound to
that project id.
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
