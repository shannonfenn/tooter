# Four Architecture Proposals for tooter v1

> Provenance: the four competing architecture proposals, each argued by a dedicated proposer subagent on 2026-07-06 during the tooter redesign review. Preserved verbatim; adversarially reviewed in critique-sustainability.md and critique-pedagogy.md.

Context: tooter = personal agentic math-tutoring workspace. Solo adult learner (CS background) working through Judson's AATA (2021 print), Pitt Math 0430 problem sets as exercise filter, real derivations on PAPER, Python exercises via uv/just, Sage for computational checks. Study packs under studies/<pack>/ with policy files + state/progress.md + state/code-exercises.md (hand-edited markdown tables). Tutor agents currently run on TWO harnesses with duplicated config (opencode: math-pedagogy agent + 4 math-* skills + 5 commands; pi: APPEND_SYSTEM.md + identical skills/prompts). Dev work by Codex, no config; root AGENTS.md deliberately deleted after SWE instructions leaked into tutor sessions.

Four flaws to solve:
1. Tutor/dev agent separation is textual-only and fragile; both share the repo root as working directory.
2. Terminal medium: learner reads raw LaTeX and slowly types math questions/partial solutions.
3. No fast path from paper work to agentic review.
4. Progress through an exercise set is hard to see; state is two coarse markdown tables.

---

## PROPOSAL A — "Consolidate, Don't Rebuild" (stay on opencode; config + geometry + scripts only)

**Thesis:** All four flaws are configuration and geometry problems wearing an "app" costume. The repo's own `docs/agent-harnesses.md` already states the governing principle: no custom UI until the CLI setup hits a capability limit. It hasn't. As of opencode v1.17, every capability the flaws demand — rendered KaTeX, path-scoped permission *enforcement*, image ingestion, custom agents in a browser — ships in the harness Shannon already runs. The correct move is to drop pi, split the tree, and write ~300 lines of scripts. Nothing else.

### 1. Target layout: workbench and studio

Split one repo into two, along the actual trust boundary.

```
~/dev/src/github/tooter/            # WORKBENCH (dev repo, keeps name+history)
  AGENTS.md                         # RESTORED — safe now, no tutor ever runs here
  harness/opencode/                 #   source of truth for tutor config
    agents/math-pedagogy.md
    skills/math-*/SKILL.md
    commands/{hint,assess-solution,chapter-plan,exit-check,
              transfer-problem,review-paper,progress}.md
    instructions/math-study-context.md
    opencode.jsonc                  #   studio permission policy (below)
  scripts/{deploy.sh, seed_state.py, build_queue.py, render_progress.py,
           fetch_references.py, update_aata_diff.sh}
  docs/{agent-harnesses.md, pedagogy-for-tutoring.md}
  Justfile                          # deploy, deploy --check, lint

~/studies/                          # STUDIO (new private repo; tutor cwd, always)
  .opencode/ + opencode.jsonc       # DEPLOYED copy (rsync, one-way, git-tracked)
  studies/active.md
  studies/judson-aata/
    profile.md workflow.md source-priority.md pedagogy-overrides.md
    exercises/{index.md, verification.md}   editions/
    code/{python,sage}/             # learner-facing; uv env lives in studio
    state/
      progress.md                   # kept: covered-work boundary, human-readable
      exercises/ch01.yaml … ch23.yaml   # per-exercise state machine
      attempts.jsonl                # append-only audit log
      misconceptions.md             # tutor-curated, evidence-linked
      queue.md + dashboard.html     # DERIVED, regenerated
    attempts/2026/…                 # archived page scans
  inbox/                            # Syncthing-synced phone-scan drop
  references/  notes/  pyproject.toml  uv.lock  Justfile
```

### 2. The four flaws, with enforcement

**Flaw 1 — separation.** Geometry first: the tutor is launched only in `~/studies`, whose tree (and parents) contains zero dev files — no AGENTS.md, no CI, no SWE docs. Config discovery walks up from cwd, so there is nothing to leak; the AGENTS.md incident becomes structurally impossible rather than forbidden by prose. Codex works only in the workbench, which regains a real `AGENTS.md` — today's setup punishes the *dev* agent (no instructions at all) to protect the tutor; the split fixes both directions. Second, enforcement replaces prose (verified against opencode docs today): studio `opencode.jsonc` sets, for `math-pedagogy`:

```jsonc
"permission": {
  "edit": { "*": "deny",
            "studies/*/state/**": "allow",
            "studies/*/code/**": "ask",
            "studies/*/attempts/**": "allow" },
  "bash": { "*": "ask",
            "uv run python scripts/*": "allow",
            "just *": "allow", "ls inbox*": "allow",
            "git *": "deny", "rm *": "deny" }
},
"agent": { "build": { "disable": true }, "plan": { "disable": true } }
```

Built-in SWE agents are *disabled*, not admonished; the tutor *cannot* edit outside state/code paths. Permission globs are evaluated by the harness, not by the model's goodwill. (Conceded: app-level, not OS-level, enforcement.)

**Flaw 2 — medium.** `opencode web`, localhost, becomes the daily surface: KaTeX rendering (fixed Jan 2026), existing agents/commands/skills carry over unchanged. `math-study-context.md` gains one paragraph: emit `$…$`/`$$…$$` KaTeX-safe delimiters, prefer aligned display blocks for derivations. TUI remains the degraded-mode fallback. Later, `OPENCODE_SERVER_PASSWORD` + LAN bind gives iPad access at the desk where the paper work happens — for free.

**Flaw 3 — paper loop.** iOS Shortcut ("Scan to Studio"): document-scan mode (deskew/contrast — kills the dominant blur/rotation failure modes) → save to a Syncthing folder = `~/studies/inbox/` (explicitly not iCloud; no file-watchers needed — ingestion is on-demand). New `/review-paper` command: glob newest inbox files, attach images, run the transcribe-first protocol verbatim from the research (echo LaTeX transcription, flag illegible regions rather than hallucinate, ignore crossed-out work, learner confirms before any assessment), then hand off to `math-solution-assessment`, append `attempts.jsonl`, move scan to `attempts/2026/`. Latency: shutter-to-feedback under a minute; cost ~$0.04/two pages. First-weekend task: confirm whether web-UI attach or agent file-read is the more reliable image path — both exist; standardize on whichever wins.

**Flaw 4 — progress.** Per-chapter YAML state machine (`unseen/attempted/needs-review/mastered/retired`, `next_review` on 1/3/7/21/60d expanding intervals, FIRe-style outward push on prerequisites at mastery), `attempts.jsonl`, curated `misconceptions.md`. Two ~100-line scripts: `build_queue.py` (due reviews + frontier → `queue.md`) and `render_progress.py` (in-chat markdown table + self-contained `dashboard.html` kept open in the adjacent browser tab). The tutor updates state by *calling the scripts* (bash-allowlisted), not free-editing tables — schema'd writes end the corrupt-markdown-table problem. `progress.md` survives as the human-readable covered-work boundary. `py-fsrs` is a drop-in later if fixed intervals feel wrong.

### 3. Session lifecycle

1. `just study` (studio): starts Syncthing if needed, `deploy --check` warns on config drift, launches `opencode web` on localhost, opens chat + `dashboard.html` tabs. Only primary agent available: `math-pedagogy`.
2. `/progress` or `/chapter-plan` → pick from `queue.md` → derivation happens on paper (unchanged, by design).
3. Phone scan → lands in `inbox/` within seconds → `/review-paper` → transcribe-confirm-assess → tutor appends attempt, updates YAML via script, archives scan.
4. `/exit-check` → verdicts recorded, queue rebuilt, `progress.md` boundary advanced if warranted. State changes are ordinary git commits in the studio repo — full audit trail.

### 4. Migration and effort

**First weekend (~1 day):** `git init ~/studies`; move `studies/ references/ notes/ pyproject uv.lock` + study Justfile targets; **delete `.pi/` entirely**; move `.opencode/*` to workbench `harness/`, write `deploy.sh`; write studio `opencode.jsonc` (permissions above); verify web UI KaTeX + image path; build Shortcut + Syncthing folder; write `/review-paper`; `seed_state.py` converts `progress.md` + `code-exercises.md` into YAML (then delete `code-exercises.md`). **v1 (week two, evenings):** `build_queue.py`, `render_progress.py`, `/progress`, misconceptions workflow, restore workbench `AGENTS.md`, rewrite `agent-harnesses.md`. **Later, only if pulled:** LAN/iPad access, py-fsrs, a ~40-line opencode plugin as a second enforcement layer (the `@opencode-ai/plugin` dep already sits in `.opencode/package.json`), second study pack.

**Deleted:** the entire `.pi/` duplicate harness (10 files), `code-exercises.md`, the root-AGENTS.md prohibition (scoped now to studio only), and the standing anxiety of two-harness drift.

### 5. Honest risks

- **`opencode web` is young; assets proxy from app.opencode.ai.** Mitigation: pin the version; TUI fallback preserves everything but rendering; the investment is portable markdown — if the web UI regresses, every other stance's surface can still consume these same skills/state files. Consolidation is the low-regret branch.
- **Typed math input stays mediocre** (no MathLive without an app). Conceded — but the system's own pedagogy says real derivations happen on paper; flaw 3's loop removes the bulk of math typing, and the tutor echo-confirms ASCII-math for the remainder.
- **Two-copy config.** It's dotfile deployment, not duplication: one source, one-way rsync, `--check` drift detection, both ends git-tracked. Strictly better than today's pi/opencode hand-sync.
- **App-level, not OS-level, sandboxing.** True. But the realistic threat is a *confused* agent, not a malicious one, and confusion comes from visible context — which geometry removes; permissions are the backstop, the plugin a third layer if ever needed.
- **VLM transcription errors.** Residual grading errors are mostly transcription; transcribe-first with learner confirmation converts them from silent mis-grades into a five-second correction.

### 6. Why this beats the alternatives

An Agent SDK + assistant-ui app spends the first 3–5 days reaching feature parity with a chat pane opencode already ships, then bills forever: streaming edge cases, session resume, permission UI, dependency rot — all charged against study hours, the only scarce resource here. The Jupyter/marimo route inverts the medium: tutoring is conversation-first with occasional computation, not notebook-first with chat bolted on; the tutor already runs Sage scripts, and AATA's live-Sage HTML edition covers interactive reading without owning a lab stack. claude.ai mobile is genuinely zero-setup and genuinely disconnected: no `attempts.jsonl`, no covered-work enforcement, no exercise state — it solves flaw 2 by abandoning flaws 1, 3, and 4. Consolidation reuses ~100% of the prompt/skill/command investment, deletes a whole harness, ships in a weekend, and every piece — the split, the permissions, the inbox, the YAML — is independently reversible and independently valuable under any future architecture. Build the app when a capability wall appears. There isn't one today.

---

## PROPOSAL B — "Own a Thin App; the Harness Is the Product" (Claude Agent SDK + assistant-ui)

**Thesis:** Every rival proposal rents a generalist coding harness and disciplines it with prose. Flaw 1 is the documented proof that prose discipline fails — SWE instructions leaked into tutoring until `AGENTS.md` was deleted. The Claude Agent SDK makes the harness a *library*: a tutor built on `query()` with a fully custom system prompt has **zero coding-agent defaults to leak**. Separation stops being config hygiene and becomes ordinary software boundaries. And this is not scope creep: `docs/agent-harnesses.md` §"V1 Boundary" already commits to a custom harness once the CLI setup can't support "persistent learner state, structured assessment records, cross-session scheduling, or more reliable role selection." All four flaws are that boundary being crossed. This is the planned graduation — kept deliberately thin.

### Architecture

```
tooter/
  app/                      # NEW — dev agents (Codex/Claude Code) work here, normal SWE config;
    server/                 #   AGENTS.md may safely return *inside app/* — the tutor never loads it
    web/
  studies/                  # unchanged role: packs = content + state, the tutor's whole world
  references/               # unchanged (PDFs, Pitt sets)
```

- **Server** (~400 LoC TypeScript): Claude Agent SDK `query()` + resume; Express + WebSocket streaming (crib the official `claude-agent-sdk-demos` React/Express/WS starter). `settingSources: []` — no CLAUDE.md, no user settings, no skills directory scanned. System prompt assembled per session: tutor core (distilled from the four `math-*` skills) + active pack policy + covered-work boundary computed from state — prompt-cached.
- **Pack tools** via in-process MCP: `get_exercise`, `list_exercises`, `search_text` (over the existing `.cache/text` AATA extraction), `record_attempt`, `update_status`, `get_due_reviews`, `log_misconception`, `read_pack_file` (path-restricted to `studies/`). **The tutor has no Edit/Bash/filesystem tools at all.** State mutation happens only through schema-validated tools — flaw 1 and the fragile hand-edited tables die in one move.
- **Where state lives**: transcripts = SDK JSONL under `~/.claude/projects` (machine-local, disposable, resume/fork free); the *pedagogical ledger* = plain files in `studies/<pack>/state/` (git-tracked, durable): per-chapter YAML state machines, `attempts.jsonl` (append-only), `misconceptions.md`, queue derived at render time. A small gitignored `sessions.json` maps exercise → session ids so "resume yesterday's 4.14 session" is one click.
- **Frontend**: React + **assistant-ui** (over AI Elements). Reasons: `LocalRuntime` needs exactly one `ChatModelAdapter.run()` yielding chunks — a direct bridge to the SDK stream, no Vercel AI SDK transport layer and no community shim in the critical path; best-engineered math pipeline (Streamdown/KaTeX that hardens *partial* math blocks mid-stream, `normalizeMathDelimiters`, `escapeCurrencyDollars`); attachment adapters give image upload for free. AI Elements is the fallback if assistant-ui dies — the KaTeX plumbing is standard remark/rehype either way.

### Composer: fast math input

Three modes, one box:
1. **Default**: prose + `$…$` with live KaTeX preview under the textarea — proofs are mostly prose; this covers 80% of input.
2. **Ctrl+M / `$$` trigger**: inline **MathLive** `<math-field>` — type `/`, `^`, `sqrt`, get 2-D structured editing; on commit its `.value` LaTeX embeds into the message. Virtual keyboard on tablet.
3. **Attachments**: paste/drag images, plus an inbox picker.

Current commands survive verbatim: `/hint`, `/assess-solution`, `/chapter-plan`, `/exit-check`, `/transfer-problem` become composer slash commands **and** context-bound buttons — the "Assess" button on exercise 4.14's pane sends the same prompt body with the exercise pre-bound. Diagnostic-MCQ answer chips are deferred (AG-UI/generative-UI is the later upgrade path).

### Paper loop, end-to-end

1. Derivation on paper (unchanged — that's the pedagogy).
2. iOS Shortcut "tooter scan": document-scan capture → Syncthing → `studies/judson-aata/inbox/`.
3. App shows an inbox badge; click attaches scans to the current exercise as image content blocks (native SDK support).
4. **Transcribe-first protocol** in the system prompt: model echoes a KaTeX-rendered LaTeX transcription, flags illegible spots, ignores cross-outs; learner confirms *before* assessment. This converts "84% acceptable OCR" into a safe workflow.
5. Assessment runs; `record_attempt` writes outcome + misconception tags; scan archived beside the JSONL entry. Photo → confirmed transcription in ~90 seconds, ~$0.04/two pages.

### Progress UI (at a glance)

Rendered *from* the plain files — the app is a viewer, files stay canonical, opencode can still read them:
- **Chapter strip**: 23 chapters colored by existing statuses; current chapter expanded.
- **Exercise grid**: each Pitt-filtered exercise as a cell in the per-exercise state machine `unseen / attempted / needs-review / mastered / retired`; click → statement ref, attempt history, Start/Assess buttons.
- **Due queue**: expanding intervals 1/3/7/21/60d + FIRe-style prerequisite refresh. py-fsrs later drop-in.
- **Misconceptions panel**: `misconceptions.md` linked to spawning attempts.

### What survives

Skills prose → system-prompt sections (unchanged wording, one evening). Commands → slash commands/buttons (same bodies). `pedagogy-for-tutoring.md`, packs, edition notes, verification → loaded as-is. `code/python`+`sage`+Justfile → untouched; programming exercises stay in the terminal (a sandboxed run-tool is a *later* maybe). `.opencode`/`.pi` kept as fallback until the app survives two full chapters, then retired.

### Phases and honest burden

- **v0, one weekend**: demos starter + custom prompt + assistant-ui chat with KaTeX + image paste + resume + read-only pack tools + `record_attempt`. Already beats the terminal on day one. Hard rule: if v0 exceeds a weekend, stop and reassess.
- **v1, 2–3 weekends**: MathLive composer, inbox watcher, state-machine migration script, chapter/exercise/queue UI, misconceptions panel.
- **Later, only on logged study friction**: py-fsrs, MCQ chips, Sage tool.
- **Maintenance**: ~1–1.5k LoC total, localhost-only, no auth, no CI, pinned lockfile. Budget one evening/month. Feature-frozen after v1; success metric = chapters completed, not commits to `app/`.

### Auth/billing: API key

Recommended. Subscription login for third-party programs is a ToS gray zone riding a community provider — an outage mid-chapter is the worst failure mode for a study habit. n=1 tutoring with cached pack policy ≈ $10–30/month; show per-session cost from SDK usage fields. If the Max-login posture ever becomes officially supported, one-line swap.

### Risks

- **Scope creep** (the real one): feature freeze post-v1; app work only against a logged friction list; this is a tool to study *with*.
- **SDK churn** (V2 removal is precedent): build only on the stable `query()`+resume core; quarantine all SDK calls in one ~100-line adapter; pin, upgrade quarterly.
- **Frontend bitrot**: pinned deps, zero external services; runtime interface is one class to swap.
- **Lock-in**: none — state is plain files; worst case, fall back to opencode on the same packs tomorrow.

### Why not the alternatives

**opencode web** fixes half of flaw 2 (rendering) and nothing else — input is still typed LaTeX, separation is still prose, state is still two tables. **JupyterLab/ACP** is the wrong shape: proofs are conversations, not cells; ACP personas inherit harness config — the same leak class flaw 1 already burned us on; Sage cells are a sidecar we already have. **claude.ai** is a tutor with amnesia about the only thing that matters — the exercise ledger — and can't run pack tools or enforce covered-work. Only owning the thin harness makes the guardrails *be* the architecture, and the repo's own docs already scheduled this move.

---

## PROPOSAL C — "Notebook-Native: The Medium Should Be Executable Math" (JupyterLab + jupyter-ai persona)

**Thesis:** A tutoring session for AATA is not a conversation; it is a **document under construction**: the exercise statement, the learner's paper attempt, the transcription, the tutor's feedback, a Sage counterexample check, and the exit verdict. Every chat-shaped option makes that document ephemeral and makes Sage a side-channel. JupyterLab makes it the primary artifact. This matters doubly for *this* book: Judson's official edition is a PreTeXt/Runestone text with **live Sage cells** — executable math *is the author's pedagogy* — and Sage's standard UI **is** the Jupyter kernel. tooter already has `code/sage/` and `code/python/`; only this option makes them first-class.

### Stack decision

- **JupyterLab + jupyter-ai 3.0, not marimo.** Marimo's chat hook is elegant, but Sage-under-marimo is off the beaten path (memory-leak reports), no ACP plumbing, and its reactive model fights the "append feedback to a worksheet" workflow.
- **Custom persona wrapping the Claude Agent SDK (Python), not the ACP-client route, as primary.** ACP personas (Claude Code / opencode @-mentioned in chat) reuse existing config — but that config *is* flaw #1: an SWE harness wearing a tutor costume. jupyter-ai 3.0 personas are plain Python classes, so the tutor persona instantiates the SDK with a **fully custom system prompt (zero SWE defaults)**, streaming, session resume, image blocks, and in-process MCP tools for state. ACP mode is the day-one fallback while the persona is built.
- **Kernels:** project Python kernel from the uv venv; Sage kernelspec registered from the Sage install.

### Pack v2 layout

```
studies/judson-aata/
  profile.md workflow.md source-priority.md ...   (as today)
  state/
    chapters.yaml            # per-exercise machine: unseen/attempted/needs-review/mastered/retired
    attempts.jsonl           # append-only event log (persona-written)
    misconceptions.md        # tutor-curated
    queue.md                 # derived: due today (1/3/7/21/60d expanding intervals)
  worksheets/
    ch04-cyclic-groups/
      worksheet.ipynb        # generated from exercises/index.md
      attempts/              # scanned pages embedded + archived
      sage-scratch.ipynb     # Sage kernel scratchpad
  inbox/                     # Syncthing target for iOS Shortcut document-scans
  dashboard.ipynb            # renders chapters.yaml: heatmap, due queue, misconception digest
harness/jupyter/             # persona class, tooter_nb helpers, MCP state tools (dev-owned)
```

### Worksheet lifecycle

1. **Generate.** `just worksheet ch04` renders `worksheet.ipynb` from `exercises/index.md` + `verification.md`: one section per Pitt exercise (statement, renumbering note, attempt slot, feedback slot), plus Judson's Sage exercises for the chapter. Generator refuses exercises beyond the covered-work boundary in `chapters.yaml` — **covered-work discipline becomes code, not prose**.
2. **Work on paper.** Unchanged; paper stays primary for derivations.
3. **Ingest.** iOS Shortcut document-scan → `inbox/` via Syncthing; in the notebook, `%load_attempt 4.27` embeds the newest scan into the exercise's attempt cell (image stored as an ipynb attachment — durable) and files it under `attempts/`.
4. **Review.** @tutor in chat (or a cell comment): persona does **transcribe-first** review — echoes LaTeX transcription, flags illegibles, ignores cross-outs, learner confirms — then formative feedback per pedagogy doc, writing the assessment into the feedback cell via the permissioned Jupyter MCP server. Sage checks get inserted as *runnable cells the learner executes* ("verify your claimed subgroup is closed"), not as claims to trust.
5. **Exit check + archive.** `/exit-check` equivalent runs against the worksheet; persona updates `chapters.yaml`/`attempts.jsonl` via MCP state tools (schema-enforced). The finished notebook is the chapter's study record; spaced review **re-opens it** on the 1/3/7/21/60d schedule.

### The four flaws

1. **Separation** — solved structurally, twice over. JupyterLab launches with `root_dir=studies/judson-aata` (`just study`): `.opencode/`, `.pi/`, dev docs are *outside the served tree* — the learner and file browser cannot see them. The persona's SDK client gets `cwd`=pack, a Read/Write allowlist under the pack + `references/`, and a PreToolUse hook denying anything else. Enforcement, not prose. Codex keeps the repo root. Also kills the pi/opencode **config duplication**: one persona, one prompt.
2. **Medium** — MathJax renders all notebook markdown; jupyterlab-katex if speed grates. Worked examples, attempts, and feedback are rendered math in a scrollable document, not raw LaTeX in a terminal.
3. **Paper→review** — the inbox + `%load_attempt` + transcribe-first pipeline; the scan ends up *inside the artifact* next to its feedback, which neither claude.ai upload nor terminal paste achieves.
4. **Progress** — YAML/JSONL state written by MCP tools, and — the notebook dividend — `dashboard.ipynb` renders it as chapter heatmaps, per-exercise status, and today's queue with ~50 lines of pandas. No frontend built; a dashboard exists.

### Honest input story

Typing math in a notebook cell is still typing LaTeX. Mitigations, in priority order: **photo-first philosophy** (derivations belong on paper; typing is for short confirmations); markdown renders on run, so you see real math seconds later (vs never, in a terminal); a snippets palette for `\langle a \rangle`, `\mathbb{Z}_n`, quotient notation; and the tutor accepts sloppy ASCII (`Z_12`, `<a>`) and echoes proper LaTeX back. I will not claim notebook input beats MathLive in a custom app — it doesn't. I claim input is the *minor* channel for a paper-first learner, and the custom app wins input while losing execution, artifact, and dashboard.

### Migration & phasing

- **Weekend 1 (validation):** `uv add --group study-ui jupyterlab jupyter-ai`; register Sage kernel; **hour one: test math rendering in chat-panel messages** — this is the one unverified link. Run opencode as ACP persona against a hand-made Ch4 worksheet; test one photo ingest.
- **v1 (2–3 weekends):** SDK persona (prompt ported from math-pedagogy + skills); `tooter_nb` helpers; MCP state tools; state migration script (markdown tables → YAML/JSONL); worksheet generator; dashboard.
- **Later:** py-fsrs, FIRe-style prerequisite refresh, nbconvert HTML archives. Retire `.pi/` once the persona is trusted; keep opencode for a term as fallback.

### Risks — stated plainly

- **Chat math rendering unverified.** Inferred from shared rendermime; if it fails, the fallback is *on-thesis*: the persona writes feedback into notebook markdown cells (guaranteed MathJax) and chat carries only coordination. Testable in hour one; does not sink the design.
- **jupyter-ai 3.0 is three months old.** Persona API may churn. Mitigation: persona is a small class (~300 lines) over the SDK; pin everything via uv lock; ACP mode as fallback.
- **Extension-stack fragility (real).** Mitigation: minimal extension set, pinned env, quarterly upgrades on a branch. Worst-case exit: `.ipynb` + YAML/JSONL are harness-neutral — every artifact and all state survive a move to any future UI. The custom web app fails *its* worst case with a dead bespoke frontend.

### Closing

opencode web fixes rendering and nothing else — same SWE harness, ephemeral transcript, no photo pipeline, no state model. claude.ai has the best zero-setup capture and no hands on local state, Sage, or the covered-work boundary. The custom app is 3–5 days to a better input box and a permanent solo frontend-maintenance tax, with Sage as a remote procedure call. For a CS-background adult working a Sage-integrated textbook with paper derivations and a need for durable, reviewable records: the tutoring medium should be the thing mathematics already lives in — a rendered, executable, keepable document.

---

## PROPOSAL D — "Don't Build a Client Anthropic Already Built" (claude.ai Projects + repo as backend)

**Thesis:** tooter's four flaws are a separation problem, a rendering problem, a capture problem, and a state problem. Anthropic's clients already solve rendering and capture with polish a solo dev will never match; separation is solved by *not running the tutor in a repo at all*; state is ~200 lines of repo-owned MCP over git-versioned YAML. The learner's job is Sylow theorems, not software. Own the content and the state; rent everything else.

### 1. Architecture

- **Tutor surface:** a claude.ai Project ("AATA Tutor") on desktop + mobile. Custom instructions = compiled tutor role; knowledge = compiled pack policy; state via MCP.
- **Repo:** demoted from "place where tutoring happens" to content/state backend: pack sources, compiler, `tooter-state` MCP server, references, `code/`.
- **Companion surface:** Claude Code desktop *in the repo* for the programming-exercise loop (Sage/Python via uv/just) and dev work. Here the SWE system prompt is a *feature*, not a leak — `math-programming-exercises` is the one skill that is genuinely repo-native, and it stays.

**The Claude Code-as-tutor hybrid, weighed and declined:** a dedicated `~/study/aata` directory with a `.claude/agents/tutor.md` subagent (fully custom prompt, tool allowlist) is the fallback if claude.ai ever fails — but as primary surface it inherits the harness's SWE identity in the main loop (a "tutor skill" does not remove it; only subagents/SDK replace the prompt), has no phone, and its rendering story (artifacts) is worse than native chat LaTeX. Keep it as the documented Plan B; one afternoon to stand up.

### 2. Compile pipeline (`tooter compile`)

A ~150-line uv script; `just compile` emits `dist/claude-project/`:

- **Project instructions (small, stable):** tutor role distilled from math-pedagogy + math-study-context; covered-work policy; the five commands become instruction-defined **moves** — "hint:", "assess:", "plan ch N", "exit check", "transfer"; *transcribe-first* photo protocol; MCP tool usage rules; a compile version stamp the tutor announces at session start so staleness is visible.
- **Project knowledge (static-ish only):** `profile.md`, `workflow.md`, `source-priority.md`, `pedagogy-overrides.md`, `exercises/index.md` + `verification.md`, `editions/2021-to-current.md`, `docs/pedagogy-for-tutoring.md`.
- **Deliberately excluded from knowledge:** anything volatile. Progress, attempts, misconceptions flow through MCP. Knowledge changes only when pack *policy* changes (monthly at most) → recompile, drag-and-drop replace, two minutes.

### 3. State bridge — recommendation

**v1: local MCP server + claude.ai desktop app** (`claude_desktop_config.json`; supported and documented, with desktop-extension packaging for one-click install). `tooter-state` is a small stdio Python server exposing `get_progress`, `get_due_reviews`, `record_attempt`, `update_status`, `log_misconception`, `read_misconceptions`, `get_pack_file`.

Backing store per the n=1 findings, **in the repo, git-versioned**: per-chapter per-exercise state-machine YAML, append-only `attempts.jsonl`, tutor-curated `misconceptions.md`, derived `queue.md` with expanding intervals and FIRe-style prerequisite refresh. A one-shot script migrates today's two markdown tables. Plain text, no database, zero lock-in.

**Mobile: read-mostly degraded mode, explicitly designed.** No remote connector in v1 — tunnel ops and connector OAuth friction aren't worth it yet. Instructions direct the tutor, when state tools are unavailable, to end assessment turns with a fenced ```tooter-state``` YAML block; the next desktop session opens with "any mobile sessions to sync?" and applies pasted blocks (or `just sync` ingests them). Studying is never blocked by an MCP outage. **v1.5 (only if mobile writes prove wanted):** promote the same server to a remote connector via Tailscale Funnel or a $5 worker + bearer token.

### 4. Session lifecycle

**Desktop:** open the Project → tutor calls `get_due_reviews`/`get_progress` → "2 reviews due (3.17, 3.31); current: ch4 §4.1" → learner works **on paper** → drags in a photo (or macOS Continuity Camera) or types → tutor transcribes, confirms, assesses, `record_attempt`, offers a transfer problem. All math renders natively. **Chats are disposable by design:** one conversation per section or problem set; continuity lives in MCP state, not the thread — which is also the answer to context limits over a 23-chapter book.

**Phone (paper → review, zero setup):** finish a page at a café → open the same Project in the mobile app → document-scan photo (20 files/chat, 30MB each) → "assess: PS2 3.22" → rendered feedback in a minute → tutor emits the state block; sync lands next desktop session. The phone **is** the scanner; the pipeline maintained is *none*. Voice input covers "why does Lagrange need finiteness?" while walking.

### 5. The four flaws

1. **Separation → structural, not textual.** The tutor runs in a different *product* with only compiled context; it cannot see Justfile, pyproject, git, or any SWE instruction — there is nothing to leak, in either direction. Dev agents see tutor prompts only as inert data under `studies/`. No competing option achieves this; they all fence roles inside one working directory.
2. **Medium →** native LaTeX rendering, real chat UI, mobile, voice. Input honesty: still typed math for short answers — mitigated by photo-first culture, Claude rendering back what you typed, and a CS-background learner being fine with `Z_5`-style plaintext for fragments.
3. **Paper → review →** solved outright.
4. **Progress →** per-exercise state machine + attempts log + due-queue behind MCP; "show chapter 3" renders a live table in chat; `just dashboard` can emit a static HTML/artifact later. For n=1, a queried table *is* the dashboard.

### 6. Repo after; deletions

**Keep:** `studies/` (packs = single source of truth), new `state/` YAML+jsonl, `tutor/` (role + moves sources, relocated), compiler, `tooter-state` server, `references/`, `docs/`, `code/`, Justfile/uv. **Delete: `.pi/` and `.opencode/` entirely.** Their prose isn't lost — it becomes compiler input in `tutor/` — but the duplicated two-harness config, the very thing that rotted, goes. One source, one compile target.

### 7. Effort and the maintenance claim, scrutinized

- **First weekend:** compiler v0 (concat+trim), create Project + upload, MCP server with the four core tools, state migration script, delete `.pi/`/`.opencode/` after relocating sources. Studying on the new surface Monday.
- **v1 (+1–2 weekends):** due-review scheduling, misconception curation protocol, transcribe-first hardening, mobile sync ritual, desktop-extension packaging.
- **Later, only if earned:** remote connector; dashboard generator.

"Near-zero maintenance" is *not* zero: honest residuals are (a) manual knowledge re-upload on policy edits — bounded by keeping knowledge static; (b) ~200 lines of MCP that can rot — pinned deps, and the paste-block fallback means it's never load-bearing; (c) platform churn. What it *is*: zero UI code, zero auth code, zero hosting, zero mobile app, and every claude.ai improvement (rendering, memory, voice, capture) arrives for free.

### 8. Risks

| Risk | Mitigation |
|---|---|
| Anthropic product churn (Projects limits, connector policy) | Sources + state live in the repo; compiler retargets; documented Plan B = Claude Code subagent in a study dir, one afternoon |
| Context limits, 23 chapters | Disposable chats; state-not-thread continuity; per-section conversations |
| Connector auth friction (mobile writes) | Deferred; degraded mode is designed, not accidental |
| No Sage/Python execution in claude.ai | Tutor *writes* Sage (rendered), learner runs it in the repo Claude Code session or Runestone's live AATA cells |
| VLM misreads handwriting | Transcribe-first + learner confirmation gate + document-scan capture; every rival uses the same VLMs — capture ergonomics is the only differentiator, and phones win it |

### 9. Closing argument

**opencode-web** fixes rendering and nothing else: no capture path, same fragile textual separation, same duplicated config. **The custom SDK app**'s "3–5 days" is a down payment on auth, streaming edge cases, persistence, and a phone story that amounts to rebuilding claude.ai mobile, badly, for one user; n=1 apps die the month life gets busy. **Jupyter** optimizes the minority loop — this repo's own workflow says real derivations happen on paper — and proofs-in-notebooks with no mobile story is the wrong medium for a proof-based book. Anthropic employs teams shipping exactly the client this learner needs, continuously. The winning move for someone who wants to *study* is to own ~350 lines (compiler + MCP), own the plain-text state and pack sources forever, and ride everything else.
