# tooter v1 Redesign Plan

**Status:** adopted 2026-07-06 · branch `redesign/v1-plan`
**Provenance:** multi-agent design review (repo + harness audit, 3 landscape research tracks, 4 competing architecture proposals, 2 adversarial critiques). This plan supersedes the v0 posture in `docs/agent-harnesses.md`; that doc is rewritten in Phase 0/1 to point here.

## 1. Decision summary

The content architecture is sound and is kept: study packs as plain files, pedagogy prose, covered-work discipline, paper as the primary derivation medium. What changes is the deployment architecture.

**Own two contracts, rent every surface:**

1. **Tutor-core** — the ~300 lines of role/skill/command prose (the real portable asset), single-sourced in the dev repo and *compiled* to each surface: opencode agent + commands now; optionally claude.ai Project instructions later; an SDK system prompt only if a custom app is ever triggered.
2. **State layer** — per-exercise state machines, append-only attempt log, misconception ledger, derived review queue; exposed **both** as CLI scripts and as a small stdio MCP server, so every present and future surface consumes identical state.

Plus three structural moves:

- **Separation by geometry, enforced by permissions.** Tutoring runs only in a dedicated study repo (`~/dev/oth/github/tooter-studies`) that contains zero dev config — and whose ancestor directories hold no agent instruction files; the dev repo (workbench) regains a normal `AGENTS.md`. Harness permission globs and disabled built-in SWE agents replace prose guardrails.
- **`opencode web` is the daily tutor surface** (renders KaTeX as of v1.17); the TUI is the always-working floor. **`.pi/` is deleted** — one tutor config source, compiled outward.
- **At-desk paper capture is a requirement, not a feature** (§4). Away/mobile sessions are an optional nice-to-have, deprioritized.

Not now, and only behind explicit triggers (§9): custom app, notebook stack, remote MCP, FSRS.

## 2. What stays / what changes

**Stays:** pack layout and policy files; `docs/pedagogy-for-tutoring.md` and the Barton MCQ pattern; covered-work discipline; the `/command` grammar (named pedagogical moves); uv/just programming-exercise loop; references pipeline; paper-first derivations.

**Changes:** `.pi/` deleted; tutoring moves out of this repo; two hand-edited state tables → structured state layer with schema'd writes; terminal → rendered web surface; photo review becomes a first-class protocol with integrity gates; progress semantics reworked for proof skills (§5); Sage de-emphasized to a pack-declared computational sidecar (§7).

## 3. Target architecture

### 3.1 Geometry: two repos — `tooter` (workbench) and `tooter-studies` (study workspace)

```
~/dev/src/github/tooter/            # WORKBENCH — dev repo (keeps name + history)
  AGENTS.md                         # restored: dev-agent instructions (safe here)
  tutor/                            # tutor-core SOURCES (role, moves, protocols)
  compiler/  (or scripts/)          # compile/deploy tutor-core + state tooling
  state-layer/                      # python package: schemas, CLI, MCP server
  docs/                             # this plan, pedagogy, harness notes
  Justfile                          # deploy, deploy --check, lint, test

~/dev/oth/github/tooter-studies/    # STUDY WORKSPACE — private repo; tutor cwd, always
  .opencode/ + opencode.jsonc       # DEPLOYED tutor config (one-way, git-tracked)
  studies/active.md
  studies/judson-aata/              # pack: policy, exercises, editions, code/
    state/                          # see §3.3
    attempts/2026/                  # archived page scans, beside their ledger entries
  inbox/                            # capture drop (see §4)
  references/  notes/  pyproject.toml  uv.lock  Justfile (study targets)
```

Dev agents (Claude Code / Codex) work only in the workbench. `tooter-studies` contains no dev files, and — **the geometry invariant** — none of its ancestor directories (`~/dev`, `~/dev/oth`, `~/dev/oth/github`) may hold agent instruction/config files (`AGENTS.md`, `CLAUDE.md`, `.claude/`, `opencode.jsonc`, …), so upward config discovery finds nothing to leak in either direction. The old failure (SWE instructions leaking into tutoring) becomes geometrically impossible rather than textually forbidden; equally, dev agents stop being starved of instructions to protect the tutor.

Naming/location rationale: it is a git repo, so it lives in the `~/dev` tree rather than `$HOME` (which is for installed-software config/state) — but under `~/dev/oth/` ("other"), not `~/dev/src/` (source-code checkouts), since it is state/content rather than software source. The `tooter-` prefix keeps the pairing discoverable, and "studies" describes a state package rather than a product. The pack directories inside keep their existing names (`studies/judson-aata/` etc.).

### 3.2 Contract 1: tutor-core (single source, compiled)

`workbench/tutor/` holds the canonical prose: the tutor role, the moves (`/start`, `/hint`, `/assess-solution`, `/review-paper`, `/chapter-plan`, `/exit-check`, `/transfer-problem`, `/progress`), and the protocols (§4.4, §6). `just deploy` compiles these into `tooter-studies/.opencode/` (agent, commands, instructions). The compiler is dumb concatenation/templating — no cleverness. Drift check (`deploy --check`) runs on a weekly schedule, never at session start (a maintenance prompt at study time is a study-killer).

### 3.3 Contract 2: state layer (dual-faced)

Python package in the workbench; `tooter-studies` consumes it as an installed tool.

- `state/exercises/chNN.yaml` — per-exercise records: `status ∈ {unseen, attempted, needs-review, proved, re-derived, transfers-ok, retired}` (deliberately **no "mastered"** — see §5), topic/pattern tags, attempts count, last_attempt, next_review, short note.
- `state/attempts.jsonl` — append-only: `{ts, exercise, kind: attempt|stuck-here, verdict, hint_depth, image_paths, tutor_summary}`. Never edited.
- `state/misconceptions.md` — tutor-curated, one bullet per live misconception with evidence links into attempts.jsonl; entries deleted when disconfirmed.
- `state/queue.md`, `state/dashboard.html` — derived views, regenerated by scripts; disposable.
- `state/progress.md` — survives as the human-readable covered-work boundary (generated or hand-adjusted; open question §11).

Faces: a CLI (`tooter-state record-attempt|update-status|build-queue|render-dashboard|due`) bash-allowlisted to the tutor, and a stdio **MCP server** (~150 lines) exposing `get_progress`, `get_due_reviews`, `get_exercise`, `record_attempt`, `update_status`, `log_misconception`. Same functions, two transports — opencode calls scripts today; any future surface (claude.ai, custom app) mounts the MCP server unchanged.

Scheduling: expanding intervals 1/3/7/21/60d; on `proved`, push `next_review` outward on the exercise's prerequisite patterns (FIRe-lite). `py-fsrs` is a later drop-in only if interval feel proves wrong.

### 3.4 Surfaces (rented) and enforcement

- **Primary:** `opencode web`, localhost, launched by `just study` (also: regenerate queue, open dashboard tab). Adopt only after the Phase-1 hour-one check: KaTeX rendering + image attach verified on real transcripts.
- **Floor:** opencode TUI + files. Breakage degrades; it never halts studying.
- **Optional later (deprioritized):** claude.ai Project compiled from tutor-core, for away sessions. If ever added: mobile is **never state-authoritative** — capture + feedback only; the desk session re-records from the same scans.
- **Triggered only:** thin custom app (Agent SDK + assistant-ui) — see §9; if built, pedagogy widgets ship first (commit-gated MCQs, hint-ladder reveal, transcription gate), not a nicer chat.

`tooter-studies/opencode.jsonc` (enforcement, not prose): `edit` deny-by-default, allow `studies/*/state/**` and `studies/*/attempts/**`, ask for `studies/*/code/**`; `bash` deny-by-default with an allowlist (`tooter-state *`, `just *`, `ls inbox/*`); built-in `build`/`plan` agents `disable: true`. Pin the opencode version; upgrades happen on a scheduled quarterly evening against a smoke checklist (permission semantics, KaTeX, image attach) — opencode moves fast and its web assets are proxied from app.opencode.ai, so upgrades are a deliberate act, not an accident. Sessions launch via `just study`, which also disables opencode's external-skill discovery (`~/.claude/skills/` etc. would otherwise surface dev skills inside tutor context; no config key exists, env vars only — details in `agent-harnesses.md`). Bare `opencode` in the studies repo reopens that leak.

## 4. Capture (requirement)

### 4.1 Requirements

- At-desk loop: **"page done → reviewable in session" in ≤2 manual actions and ≤30 seconds.** Ease of use dominates; each manual step is a defect. This is the highest-frequency loop in the whole system — it must be boring.
- Devices: iPhone 16 Pro; MacBook Pro 14 (built-in camera); Insta360 Link 2 Pro on the monitor — usable only if it needn't be physically moved from its meeting position (software gimbal repositioning with reliable return is acceptable).
- Quality: sufficient for VLM transcription of handwritten math. Research baseline: document-scan-grade capture (deskew/contrast) attacks the dominant VLM failure modes (blur, rotation); Claude ingests up to 2576px long edge natively, so a sharp 4K frame may obviate scan processing.
- Files land in `tooter-studies/inbox/` timestamped; after review they are archived to the pack's `attempts/YYYY/` beside their ledger entries (provenance: scan lives next to its assessment record).
- No new always-on daemon unless it demonstrably beats the daemon-free option.

### 4.2 Researched flows (dossiers 2026-07-06)

Two research tracks (Apple-native/iPhone; webcam/Insta360), merged ranking:

| # | Flow | Manual actions | Latency to file-in-inbox | Quality for handwritten math | Setup | Fragility |
|---|------|----------------|--------------------------|------------------------------|-------|-----------|
| 1 | **iPhone Action Button → VisionKit document scan → iCloud Drive inbox** | **2** (press Action Button; tap Save — pages auto-capture in between) | scan 10–15s + iCloud sync (usually seconds; documented envelope "a couple of minutes") | **Best**: auto edge-detect, perspective/deskew correction, grayscale/B&W contrast modes | ~20 min once | iCloud sync variance; native Scan Document action has folder-targeting quirks (Actions-app variant if so) |
| 2 | **Finder right-click → Import from iPhone → Scan Documents** (Continuity Camera) | 3–4 (2 with a hotkey macro) | 15–25s, **deterministic** — lands locally, no cloud in the loop | Same VisionKit scanner | Zero | Hotkey macro is UI-scripting (fragile); needs a Finder target; phone nearby w/ BT+Wi-Fi |
| 3 | **Insta360 Link 2 Pro: hotkey → DeskView/desk-preset → 4K snap → auto-return** | **1** (touch nothing but a key; camera stays in meeting position — gimbal presets are stored in the camera) | 10–20s | ~200 dpi on page at 2–3× zoom with on-device perspective correction — **dense-handwriting legibility unverified** (no published samples) | Medium-high: one-time preset framing + Hammerspoon UI-script of Link Controller; official Stream Deck plugin is the robust trigger (needs the hardware); community UVC-protocol port is the headless endgame | UI-script breaks on app redesigns; DeskView exit/return behavior undocumented (mitigated by preset recall / re-enabling AI tracking, which re-frames automatically) |
| 4 | iPhone in a desk stand as persistent Continuity Camera; Mac hotkey CLI grab | 1 | 3–10s per grab | Weak: video pipeline caps at 1920×1440 (~170 dpi), no deskew | Low | Per-grab connect/warm-up; portrait/down-pointing orientation crops; feed pauses when phone unlocked |
| 5 | MacBook built-in camera, hold page up + hotkey | 2 | ~10s | ~130 dpi ceiling, handheld blur, glare — emergency only | Trivial | Low |

**Rejected:** Apple Desk View (single warped 1920×1440 format; fails for text) · AirDrop (5 taps, raw un-deskewed photo, `~/Downloads` only) · iCloud Photos + polling (minutes-scale variance, heavyweight) · third-party scanner apps (more taps + subscription; fixed export folders).

Already verified on the target Mac (macOS 26.4.1): ffmpeg/AVFoundation enumerates the iPhone and Desk View Continuity devices with no pairing step; `brctl download` still works (absent from `brctl` help, present in man page, functional); the `shortcuts` CLI is available.

### 4.3 Chosen flow + fallback

- **Primary: flow 1** — an Action Button shortcut "Scan to Inbox": VisionKit document scan (grayscale for math pages) → Save File into iCloud Drive `tooter-studies/inbox`. The repo's `inbox/` is a symlink into the iCloud container (`~/Library/Mobile Documents/com~apple~CloudDocs/tooter-studies/inbox`). (The archived capture dossiers predate this rename and show `~/studies/inbox` in example commands — substitute accordingly.) The consumer (`/review-paper`) reads **on-demand**: list the folder → `brctl download` anything dataless → short retry loop (≤60s) — no watchers, no daemons. One-time Mac config: Optimize Mac Storage **off** (eager replication), pin the inbox folder ("Keep Downloaded").
- **Interim + fallback: flow 2** — Finder → Import from iPhone → Scan Documents straight into `inbox/`. Zero setup, deterministic, local; usable from day one and whenever iCloud misbehaves.
- **Candidate upgrade: flow 3** — the Insta360 zero-touch loop (1 action beats 2, and the page never leaves the desk). Adopt for the per-page loop **only if the empirical gate passes**: a dense derivation page, captured via the desk preset, is legible at 100% and Claude's transcription matches the iPhone-scan baseline on subscripts/exponents/fraction bars. Trigger via Hammerspoon first; if adopted, harden with the Stream Deck plugin or the UVC-protocol port. The iPhone scan remains the quality-escalation path for any page the tutor flags illegible.
- **Empirical tests before locking (Phase 1 tasks):**
  - iCloud sync latency distribution: ~20 Action-Button scans, record p50/p90 phone-Save → Mac-readable. Gate: p90 ≤ 60s, else flow 2 becomes primary.
  - Scan output resolution (`pdfimages -list`): expect ~2000–3300px long edge against Claude's 2576px native ceiling.
  - Native "Scan Document" Shortcuts action: destination determinism from the Action Button with the phone locked (else switch to the Actions-app variant: Scan Documents → Wait to Return → Get Clipboard → Save File).
  - Insta360: 4K still negotiation via imagesnap/ffmpeg; desk-preset framing repeatability ×10; whether DeskView's perspective correction appears in the UVC stream (not just the client preview); the legibility gate above.
  - Whether an ImageMagick deskew/page-crop pass before sending measurably improves Claude's transcription; if yes, insert it into the capture script (zero added manual steps).

### 4.4 Photo protocols (tutor-core)

Two distinct protocols; the learner names which applies:

- **`attempt`** — transcribe-first with integrity gates: per-page LaTeX transcription with uncertain spans explicitly marked; the learner confirms/corrects **each page** (monolithic echoes invite rubber-stamping); only after confirmation does assessment run; verdict + hint_depth recorded via `record_attempt`; scan archived beside the record.
- **`stuck-here`** — the learner indicates the stuck point; the tutor reads **no further than that point** (a photographed page contains the learner's later scratch work — reading ahead spoils the struggle); responds with the smallest useful hint (ladder rung 1); no grading; logged with `kind: stuck-here`.
- **Crossed-out work** — excluded from grading, but with the learner's consent it is *mined*: the first faulty inference in a discarded attempt is prime misconception evidence for `misconceptions.md`.

## 5. Progress and review model

- **Reviews are freshly generated retrieval/transfer prompts against the due proof pattern or concept — never a re-read of prior work.** (Re-reading one's own solved proof is among the lowest-utility review activities; the testing effect demands generation.)
- **Proof patterns are the unit of mastery, exercises are the vehicle.** A per-chapter pattern registry (e.g., coset counting, well-definedness, order/divisibility arguments) tags exercises; the queue schedules patterns due for retrieval; the tutor generates a fresh transfer problem or retrieval prompt for the pattern at review time. Hence no per-exercise "mastered": statuses record what happened (`proved`, `re-derived`, `transfers-ok`), not a claim about the skill.
- **Session-open ritual is mechanized** (`/start`, also run by `just study`): inject today's due reviews and the top two active misconceptions **as retrieval prompts** ("Before we start: define normalizer and centralizer"), never as statements. Without mechanization, the misconception ledger is a file nobody reads.
- **Exit-check remains the only path that advances the covered-work boundary.**
- **No streaks. No in-session cost meters.** (Streak pressure selects short computational exercises over multi-evening proofs; a visible taxi-meter shortens exactly the long flailing sessions proof learning requires.)

## 6. Pedagogy hardening (tutor-core edits, same day rendering arrives)

Rendering removes the decode-cost that quietly capped the damage of over-answering in the terminal; discipline must tighten in step:

- **Hint ladder:** one rung per message; end each rung with a question; never volunteer rung n+1. Overshoot in beautiful typesetting is effortless to passively read — treat it as a regression, not a feature.
- **Retrieval before help:** for definitional confusion, request the learner's attempted definition before explaining.
- **Diagnostic MCQs** per the pedagogy doc: answer + confidence committed before any explanation (prose-enforced for now; making this commit-gated in software is the *only* standing justification for a future custom app).
- **Keep the `/command` grammar on every surface** — the named moves are themselves pedagogical ritual, forcing requests into categories (smallest hint, assessment, exit check) rather than "help?".
- **Honest limits:** commutative diagrams don't render acceptably anywhere — diagram chasing stays on paper, stated plainly. Structured math editors (MathLive et al.) are rejected for a LaTeX-fluent learner; the input story is prose + `$…$`, sloppy ASCII (`Z_12`, `<a>`) that the tutor echoes back as proper LaTeX, and photos for anything long.

## 7. Computational sidecar (generalized; Sage de-emphasized)

Sage was an artifact of the first text, not a commitment. Generalize:

- Each pack **declares its computational tooling** in `profile.md` (judson-aata: Sage where the text uses it, Python/SymPy otherwise — SymPy is already a dependency; future packs: whatever fits the text, defaulting to Python/SymPy).
- The sidecar stays in the **terminal** (`just`/uv), outside the tutor surface. The tutor may *propose* a verification snippet **only after a proof attempt exists** — computation is verification, never a substitute for proving (the always-available run button is a documented avoidance channel).
- No notebook stack. If a pack's computational work grows genuinely heavy (trigger, §9), add a bare kernel scratchpad — still no chat integration.

## 8. Phasing

### Phase 0 — no-regret foundation (first weekend)

Every later branch of the decision tree consumes these unchanged.

- [x] Create the `tooter-studies` private repo at `~/dev/oth/github/tooter-studies`; move `studies/`, `references/`, `notes/`, `pyproject.toml`/`uv.lock`, study Justfile targets.
- [x] Verify the geometry invariant: no agent instruction/config files (`AGENTS.md`, `CLAUDE.md`, `.claude/`, `opencode.jsonc`, …) in any ancestor (`~/dev`, `~/dev/oth`, `~/dev/oth/github`); note the invariant in the studies repo's README.
- [x] **Delete `.pi/`** (unanimous across the design review).
- [x] Relocate `.opencode/*` prose into workbench `tutor/` sources; write the compile/deploy step (`just deploy`, `deploy --check`).
- [x] `tooter-studies/opencode.jsonc` with permission enforcement (§3.4); disable built-in `build`/`plan` agents.
- [x] State layer v1: package, YAML/JSONL schemas, CLI face, `seed_state.py` migrating `state/progress.md` + `state/code-exercises.md` (then delete `code-exercises.md`; `progress.md` survives as the boundary view).
- [x] Restore workbench `AGENTS.md` (dev-agent instructions); rewrite `docs/agent-harnesses.md` to point at this plan.

_Phase 0 executed 2026-07-06. Also done, from §11: opencode pinned at 1.17.13 (`brew pin opencode`) with the quarterly upgrade smoke checklist written into `agent-harnesses.md`; `just study` closes the external-skills leak found during verification. Studies repo relocated from `~/dev/src/github` to `~/dev/oth/github` on 2026-07-30 (repo-taxonomy decision: `oth/` for state/content repos, `src/` for source checkouts); invariant re-verified, deploy default + setup paths updated._

### Phase 1 — surface + capture (second weekend)

- [ ] **Hour one:** verify `opencode web` KaTeX rendering + image attach on real transcripts. Failure → stay on TUI and bring the optional claude.ai surface forward.
- [ ] Implement the chosen capture flow (§4.3) end-to-end, including Mac-side hotkey/script glue; run the empirical quality tests from the capture research on real handwriting.
- [ ] `/review-paper` and `/start` moves wired to the state CLI; queue + dashboard generation in `just study`.
- [ ] Tutor-core hardening edits (§6) and photo protocols (§4.4) deployed.
- [ ] MCP face of the state layer (~150 lines; same functions as the CLI).
- [ ] **Shakedown:** finish chapter 4 end-to-end on the new system before any further investment.

### Phase 2 — optional, deprioritized (nice-to-have)

- [ ] claude.ai Project compiled from the same tutor-core, for away sessions. Mobile = capture + feedback only, never state-authoritative; the desk session re-records from the same scans.

### Phase 3 — triggered only (see §9)

- Thin app (pedagogy widgets first) · remote MCP connector · py-fsrs · bare kernel scratchpad.

## 9. Decision triggers (pre-committed; don't relitigate ad hoc)

| Signal | Action |
|---|---|
| Capture friction noted ≥2×/week (sync wait, upload fail, fiddly framing) | Swap transport/flow (§4.3 fallback); the capture loop must be boring |
| `opencode web` breaks twice in a quarter, or a needed fix ships only behind a breaking upgrade | Swap surface to a claude.ai Project (state layer + tutor-core unchanged); reassess after two calm months |
| API spend > $40/month, or noticeable hesitation to ask questions due to metered cost | Move tutoring turns to a subscription surface |
| ≥3 study days in a month lost to tooling (any cause) | Two-week hard freeze on tool work; study via TUI + files; the habit outranks the system |
| A real, logged need for commit-gated MCQs / hint-ladder reveal / transcription gating | The only justification for building the thin app — pedagogy widgets are v0 of it |
| A pack's computational tool wanted >2 sessions/week for a month | Add a bare kernel scratchpad (no chat integration) |
| Caught doing surface work not on the friction log, twice | Ban weekday tool work by calendar rule — that is the personal-tooling death signature |

## 10. Non-goals (v1)

No custom app. No jupyter-ai / notebook tutor. No remote MCP / tunnels. No away-session infrastructure. No FSRS. No multi-learner features. No new always-on daemons — the chosen capture flow needs none (iCloud on-demand reads; no Syncthing, no file-watchers).

## 11. Open questions

- Whether `state/progress.md` stays a hand-adjustable boundary view or becomes fully generated from the YAML.
- Default computational tooling policy for future packs (Python/SymPy default vs per-pack) — decide when the second pack lands.
- ~~opencode pinning: exact version + the quarterly upgrade smoke checklist to be written in Phase 0.~~ Done: pinned 1.17.13, checklist in `agent-harnesses.md`.
- Remaining capture empirical tests: see §4.3.
