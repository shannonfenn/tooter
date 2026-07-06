# Adversarial critique: solo-dev sustainability & total cost of ownership

> Provenance: produced 2026-07-06 by an adversarial critic subagent during the
> tooter redesign review, reviewing the four proposals in
> [proposals.md](proposals.md). Preserved verbatim. Its "strongest hybrid"
> (§8) and decision triggers (§9) fed directly into the adopted plan.

## 0. Ground truth established before critique

- **Repo facts:** Learner is at **chapter 4 of 23** (`studies/judson-aata/state/progress.md`). The entire prompt/skill/command investment is **~302 lines of markdown** (`wc -l` over `.opencode/` + `.pi/APPEND_SYSTEM.md`). `code-exercises.md` is 2 rows. `docs/agent-harnesses.md` §V1 Boundary says a v1 harness is warranted only if the CLI setup "**cannot** support … persistent learner state outside the repo, structured assessment records, cross-session scheduling, or more reliable automatic role selection." All four proposals' "what survives" arguments are inflated: the portable asset is ~300 lines of prose plus 2 small tables. **Exit cost is therefore dominated by NEW code each proposal builds, not by what it preserves.**
- **Cost budget (computed, not vibes).** Realistic 90-min session: ~12K-token cached prefix (tutor core + pack policy), history growing to ~25K, ~25 assistant turns, 2–6 scans (~1.5–3K tokens each at typical scan resolution; up to ~4.8K at full res on current models), thinking-heavy assessment turns (billed even when display is omitted), 5-min cache TTL expiring during 20–60-min paper-work gaps (3–4 cache re-writes/session or 2× writes on 1h TTL).
  - **Sonnet-tier ($3/$15, reads 0.1×, writes 1.25×):** ≈ $0.19 reads + $0.05 input/images + $0.30 writes + $0.80 output/thinking ≈ **$1.30–1.50/session → $35–40/month daily**.
  - **Opus-tier ($5/$25):** ≈ **$2.20–2.60/session → $55–70/month**, more at high effort.
  - **Adjudication of B's "$10–30/month":** achievable only on Sonnet with lean sessions. The task — grading handwritten abstract-algebra proofs — is exactly where you'd want Opus-tier. Realistic spend for the workload as described: **$35–70/month, $450–850/year**. B's estimate is ~2× low for the model the task wants. C inherits the same bill (same SDK). D's marginal inference cost is ~$0 on an existing claude.ai subscription; A's depends on provider auth already in place. Metered billing also adds a behavioral tax B ignores: per-token pricing quietly discourages asking the tutor questions — a direct hit on the pedagogy.
- **Shared hand-wave (A, B, C): Syncthing on iOS.** There is no first-party iOS Syncthing; third-party clients (Möbius Sync/Synctrain) cannot guarantee background sync under iOS background-execution limits. "Scan lands in `inbox/` within seconds" is true only if the sync app happens to be running. The real ritual is scan → open sync app → wait → return to desk. All three local proposals put a flaky, human-triggered sync step inside the highest-frequency loop of the whole system. D is the only proposal whose capture path has zero learner-maintained infrastructure.

## 1. Proposal A — "Consolidate on opencode web"

**Bitrot vector (primary):** opencode's velocity. Its 2026 changelog shows near-continuous releases including a v2 session UI, a V2 plugin API, and releases explicitly carrying "compatibility-facing behavior changes" that require reading the summary before upgrading. A's enforcement story sits on two version-sensitive surfaces at once: the **permission-glob semantics** in `opencode.jsonc` and the **web UI whose assets proxy from app.opencode.ai** (A's own concession). The proxy detail is worse than A treats it: pinning your local binary does *not* pin the web UI experience — an upstream asset change can alter or break your "pinned" surface with no local action, and offline study dies outright. The `@opencode-ai/plugin` dep pinned at 1.17.9 in `.opencode/package.json` is already on the pre-V2 plugin API. **Fire rate:** expect one forced-upgrade event (bugfix you need, or upstream asset shift) per quarter; each costs an evening of changelog reading + permission re-verification.

**Habit / moving parts.** Study: `just study` → Syncthing daemon + drift-check + opencode server + browser (2 tabs). Four parts, one always-on daemon, one network dependency on app.opencode.ai. Review loop: scan → iOS sync-app dance → `/review-paper`. Degraded mode is honest and real: TUI + files always works — A is the only local proposal whose floor is the *currently running system*.

**Hidden ops hand-waved:** (1) The two-repo split turns every prompt tweak into edit-in-workbench → `deploy.sh` → test-in-studio; hot-fixes made in the studio during a session get flagged (or clobbered) by the next deploy. This tax lands hardest in month 1, exactly when prompt tuning is heaviest. (2) `deploy --check` at study-launch time injects a maintenance prompt into the study ritual — a scheduled trigger for the "fix the tool tonight instead of studying" failure. Move drift checks to a weekly cron, not session start. (3) The Syncthing iOS gap above.

**Exit at month 8:** best in class. Stranded: ~300 lines of scripts + one jsonc. Everything else (state YAML, queue builder, prompts, scans) is harness-neutral. **Grade: A-.**

## 2. Proposal B — "Thin custom app (Agent SDK + assistant-ui)"

**Bitrot vector (primary):** the full modern-frontend stack, owned by one person whose actual goal is Sylow theorems. React + assistant-ui + Streamdown + MathLive + Express/WS + Agent SDK is hundreds of transitive npm deps. Pinning freezes them until the first forced unfreeze (Node/macOS upgrade, security fix, SDK resume-format change — the V2 removal precedent B itself cites). **Fire rate:** the pinned tree survives ~2 quarters untouched; the first forced rebuild costs a weekend, and it will land on a weekend that was budgeted for chapter 6.

**The claim that dies under scrutiny: "weekend v0 with streaming + resume + images + KaTeX + tools."** A streaming demo by Sunday night: credible (~60%) — the demos starter plus `LocalRuntime` genuinely shortcut this. A *daily-driver*: not a weekend. Mid-stream partial-math hardening, reconnect/resume UX, error states, the inbox picker, and the exercise binding are precisely the "streaming edge cases" B's own risk list names. B's own phasing concedes it: v0 weekend + "2–3 weekends" v1 = ~a month of all free time before the system reaches the state A reaches in one weekend. Every one of those hours is debited from the only success metric, chapters completed.

**Structural self-contradiction:** B's thesis is "prose discipline fails" (the AGENTS.md leak), but its survival plan is prose discipline applied to the developer: "feature freeze post-v1," "app work only against a logged friction list." A solo dev with a bespoke app and a nightly papercut list does not obey feature freezes — this is the best-documented death in personal tooling. B also misreads the V1 Boundary: the doc gates v1 on the CLI setup being *unable* to support state/records/scheduling — A's design demonstrates ability. Flaws 2 and 3 (rendering, capture) aren't in the boundary list at all. The planned graduation isn't due.

**Concrete hidden op nobody priced:** `sessions.json` maps exercises → SDK session ids while the transcripts themselves live under `~/.claude/projects` subject to Claude Code's transcript **cleanup period (default ~30 days)**. "Resume yesterday's 4.14 session" silently 404s for any exercise untouched for a month — i.e., exactly the spaced-review resurfacing at 21/60-day intervals. The resume feature and the review scheduler are in direct conflict as designed.

**Habit / moving parts:** server process + built frontend + Syncthing + browser + API billing; every failure in any of them is *yours to debug*, with no vendor and no community for the composite. Fallback exists only until B retires `.opencode/` after two chapters — after which a Tuesday-night WS hang means no tutoring that night.

**Exit at month 8:** ~1–1.5K LoC of dead UI + server; state files survive (good design there — pack tools over plain files is the best state architecture of the four). **Grade: C.** Assistant-ui itself: MIT core with a VC-backed company steering it; a pivot to cloud-first is survivable (fork/pin) but adds one more "quarterly changelog to read."

## 3. Proposal C — "JupyterLab + jupyter-ai persona"

**Bitrot vector (primary):** the deepest dependency stack of all four, with the youngest critical layer. jupyter-ai v3.0 was committed to ship by March 31, 2026 — it is ~3 months old, as C admits. Worse than C admits: the persona interface lives in a separate `jupyter-ai-persona-manager` package whose API is at the **"Persona API v0.1 discussion" stage**, with maintainers openly redesigning it to fix "gaps in the existing design." C's core plumbing is a ~300-line class against an interface its own authors call v0.1. Underneath: JupyterLab 4.x extension-compat matrix + Sage kernelspec (Sage on macOS breaks on OS/Python bumps as a hobby unto itself) + a *second* server (the "permissioned Jupyter MCP server" for cell writes) + Syncthing + `%load_attempt` magic + worksheet generator. **Fire rate:** two independent quarterly breakage sources (Lab extension matrix, Sage), plus persona-API churn on every jupyter-ai minor.

**Habit / moving parts:** the worst count: Jupyter server + 2 kernels + persona + cell-write MCP + Syncthing + generator. And C adds a *build step between the learner and the content*: `just worksheet ch04` must correctly render each chapter's quirks (Pitt filtering, renumbering) before studying that chapter can begin — a per-chapter opportunity for a blocking generator bug, 19 more times. A 30-minute day in C is: boot Lab, generate/open worksheet, `%load_attempt`, chat — the heaviest ceremony of the four for a learner whose derivations happen on paper anyway.

**Honesty credit:** C flags chat-math rendering as unverified and stages an hour-one test. But the fallback (persona writes feedback into cells, chat is coordination-only) quietly demotes the conversational medium — the thing flaw 2 is about — and moves the cell-write MCP server into the critical path of every review.

**Structural point:** C's day-one fallback is ACP mode, which C itself admits "inherits harness config — the same leak class flaw 1 already burned us on." So during the 2–3 weekends the persona is being built, flaw 1 is unfixed. The medium argument also inverts the repo's own workflow: `workflow.md`/pedagogy say derivations happen on paper; the executable-math dividend applies to the *minority* Sage loop (currently: one `.sage` file and one Python exercise in the whole repo).

**Exit at month 8:** worksheets survive as readable `.ipynb` artifacts (genuinely the nicest residue of any option); the persona, magics, generator, and MCP plumbing (~600–900 lines) are stranded; the Sage kernel remains useful standalone. **Grade: C+ on artifacts, D on plumbing.**

## 4. Proposal D — "claude.ai Projects + repo as MCP/state backend"

**Bitrot vector (primary):** platform churn you cannot pin. Three independent channels: (a) `claude_desktop_config.json` / desktop-extension packaging has already migrated formats once and sits inside an auto-updating app — plus the classic failure of the app resolving your uv/python environment differently after an update (stdio server silently absent); (b) Projects knowledge limits/RAG behavior change without notice; (c) **tool-calling reliability is a model-behavior property**, and model updates arrive on Anthropic's schedule — an update that calls `record_attempt` less eagerly degrades the ledger with no error anywhere. **Fire rate:** something in claude.ai's Projects/MCP/desktop surface changes materially roughly monthly; most changes are free improvements (D's real argument), but 2–3 per year will each cost an evening of reconfiguration.

**The paste-block ritual is the load-bearing hand-wave.** Be concrete about the human: after a café session, the learner must later open that mobile chat, find the fenced YAML block, and paste it into a desktop session (or run `just sync`). This is a chore with no immediate payoff, deferred to a different device at a different time — the exact shape of ritual humans drop. And it fails *silently*: nothing errors when the block is never pasted; the ledger just stops matching reality. Busy months increase mobile sessions and decrease desktop sessions simultaneously — the fork window widens precisely when the learner has the least attention for hygiene. Within ~6 weeks of a busy stretch the due-queue is prescribing already-done exercises, the learner stops trusting `get_due_reviews`, and flaw 4 has silently regressed. Also unpriced: **scans are never archived** — the paper record lives only inside chat threads; `attempts/2026/…` doesn't exist in D.

**What D genuinely gets right, stated adversarially against the others:** zero learner-maintained daemons in the capture path; the surface is maintained by a company with teams, not by the learner on Tuesday nights; "studying is never blocked by an MCP outage" is designed-in, so D *degrades toward continued studying* (a chatbot with a stale ledger) where B and C degrade toward *no session tonight*. For the actual success metric that asymmetry is worth more than any feature.

**Exit at month 8:** compiler + MCP (~350 lines) reusable; state plain files; Project instructions regenerate from `tutor/` sources; chat history and the un-synced mobile fragments are stranded. **Grade: B+**, docked for the missing scan archive.

## 5. Factual adjudications

1. **B's weekend v0** — *Partly credible*: streaming+KaTeX+images demo, yes; reliable daily driver incl. resume and tools, no. B's own v1 budget (2–3 more weekends) is the confession. Total ≈ 3–4 weekends to parity with A's weekend 1.
2. **A's permission globs** — *Trust at v1.17, flag version fragility*: verified against current docs per A, but the project's own changelog cadence (compatibility-facing changes, V2 plugin API) means every upgrade requires re-verifying deny-by-default semantics. Enforcement that must be re-audited quarterly is weaker than B's in-process tool allowlist (which cannot drift) — B wins the enforcement argument in principle and loses it on the cost of everything attached to it.
3. **C's chat-math rendering** — *Correctly flagged by C as unverified*; the fallback is workable but demotes chat and adds a server to the loop. Hour-one test is the right call; do it before any other C investment.
4. **D's "smooth in practice"** — *Mostly true on desktop today* (stdio MCP + Projects is a documented, working path), but subject to config-format migration, app auto-update PATH breakage, and model-behavior drift in tool-calling; mobile MCP remains nonexistent, so the degraded mode is permanent, not transitional.
5. **$10–30/month API estimate** — *Understated ~2× for the natural model tier*; see §0. Sonnet-lean $35–40, Opus-daily $55–70. If the learner already pays for claude.ai, D's marginal inference cost is ~$0 and B/C carry a $450–850/year line item that A and D do not.
6. **B's "V1 Boundary already crossed"** — *Misreads the doc*: the boundary is capability ("cannot support"), and A's config-only design demonstrates capability. Flaws 2–3 aren't boundary items. The repo's own governing text sides with A.

## 6. Verdicts — how each one dies

- **A** dies of a thousand small upstream cuts: month 3, an opencode upgrade (pulled in for a bugfix) changes permission or config semantics; the web UI hiccups because assets it proxies moved; the learner studies in the TUI "for now"; raw LaTeX is back; sessions thin out. *Prevention:* pin hard; upgrade only on a scheduled quarterly evening with a smoke-test checklist (permissions, KaTeX, image attach); move drift-check out of session start; accept the iOS sync-app step or swap Syncthing for an iCloud-Drive inbox folder (zero new daemon on all-Apple hardware).
- **B** dies in its own build phase or at first post-freeze breakage: weekends 1–4 consume a month of study time; month 5, a Node/macOS/dep event breaks the frozen tree on a weeknight; opencode fallback was already retired; "I'll fix it this weekend" becomes three weeks of zero chapters. *Prevention:* never retire the fallback; hard-cap app time (calendar, not intentions); adopt the state layer first so the app is optional at every point.
- **C** dies of ceremony plus stack fragility: the persona v0.1 API shifts under a jupyter-ai minor, or a Lab-extension/Sage conflict after an OS bump takes the whole surface down; separately, 30-minute days can't afford worksheet-generation ceremony, so the notebook is skipped, and a skipped medium is a dead medium. *Prevention:* don't build it; if built, pin the entire env in uv lock, upgrade on a branch quarterly, and keep the ACP fallback forever (accepting flaw 1 persists in fallback).
- **D** dies silently by state fork: café sessions accumulate; YAML blocks never get pasted; the ledger lies; the learner stops consulting the queue; by month 6 the Project is a very good stateless chatbot and flaws 1/3/4 have regressed without a single error message. *Prevention:* make mobile non-authoritative by design (capture + feedback only; desktop re-derives state from re-attached scans), or ship the remote connector early if mobile writes prove real.

## 7. Ranking — P(system still in daily use at month 12)

| Rank | Proposal | P(daily use @ m12) | Why |
|---|---|---|---|
| 1 | **A** | ~0.60 | Fewest new parts on an already-running habit; harness-neutral state; TUI floor means breakage degrades, not halts. Docked for opencode velocity + proxied web assets + iOS sync hand-wave. |
| 2 | **D** | ~0.50 (as-designed) / ~0.70 for "still tutoring most days" | Consumer surface someone else maintains; zero-infra capture; degrades toward continued studying. The designed system (ledger fidelity) is what's at risk, not the habit. |
| 3 | **B** | ~0.35 | Best separation architecture and best state-mutation design, buried under a month of build and a permanent solo frontend-maintenance tax; freeze-by-prose; fallback scheduled for retirement. |
| 4 | **C** | ~0.25 | Most daemons, youngest API (persona v0.1), per-chapter generator gate, heaviest daily ceremony, medium optimized for the minority loop. |

If the metric is strictly *chapters completed* rather than *system alive*, D closes to a near-tie with A, because D's failure mode still tutors.

## 8. The strongest hybrid (minimum-regret composite)

**Principle: build the one artifact every branch of the decision tree consumes, first; rent every surface; make mobile non-authoritative.**

**Build FIRST (weekend 1) — the harness-neutral state layer.** A small Python package + CLI in the repo: per-chapter YAML state machines, `attempts.jsonl`, `misconceptions.md`, `build_queue.py`, `render_progress.py` (markdown + `dashboard.html`), `seed_state.py` migrating the two tables, exposed **both** as bash-allowlisted scripts (A's consumption path) **and** as a ~150-line stdio MCP server wrapping the same functions (D's and any future B's consumption path). Delete `.pi/` (all four proposals agree; zero-regret). This layer is the contract: opencode calls scripts today, claude.ai calls MCP tomorrow, a future SDK app imports the module — no fork of the decision tree orphans it.
Also weekend 1: **A's geometry** — studio split, studio `opencode.jsonc` permissions, restore workbench `AGENTS.md`, verify web-UI KaTeX + image attach in one hour (A's own first-weekend task).

**Weekend 2 — capture loop, de-hand-waved.** Phone-as-scanner two ways: (a) at-desk: iOS Shortcut document-scan → **iCloud Drive inbox folder** (no new daemon; on-demand read, no watcher) → `/review-paper` in opencode web, archive to `attempts/`; (b) away: **claude.ai Project** (compiled from the same `tutor/` sources via D's ~150-line compiler) for photo → rendered feedback in one minute — but *mobile is never state-authoritative*: no YAML paste-back; the next desktop session re-attaches the same scans from the camera roll/inbox and runs `record_attempt` there. The scan is the sync medium; state cannot fork because only one writer exists. Syncthing enters only if iCloud latency measurably annoys.

**Standing sidecars:** Sage stays `just`/terminal (or a bare `sage-scratch.ipynb` with a registered kernel — C-lite, no jupyter-ai). Programming exercises stay in the existing terminal loop.

**Explicitly deferred:** B's app (only behind triggers below, and it would consume the weekend-1 state layer unchanged); C's persona/worksheet stack (only if Sage-session frequency demands it); remote MCP connector (only if mobile-write demand is proven).

**Total new surface owned: ~500–600 lines of Python + one jsonc + one compiler — and zero new always-on daemons.**

## 9. Decision triggers (observable, pre-committed)

| Signal | Action |
|---|---|
| opencode web breaks twice in one quarter, or a needed fix ships only behind a breaking upgrade | Swap desktop surface: claude.ai desktop Project + MCP (state layer unchanged); reassess B only after two calm months |
| Monthly Anthropic API spend > $40, or observed hesitation to ask questions because of metered cost | Move tutoring turns to subscription surface (claude.ai / Claude Code on Max); keep API only for batch jobs |
| >20% of away-session attempts absent from the ledger after 4 weeks | Either ship remote MCP connector (Tailscale Funnel) or formally declare mobile feedback-only and stop pretending |
| ≥3 study days in one month lost to tooling (any cause) | Two-week hard freeze on all tool work; study via TUI + files; habit outranks system |
| Scan-to-review friction (sync wait or upload fail) noted ≥2×/week | Replace transport (iCloud → Syncthing or vice versa); the capture loop must be boring |
| Sage used >2 sessions/week for a month | Add C-lite notebook sidecar (kernel + scratchpad only, still no jupyter-ai) |
| jupyter-ai personas reach a stable v1 API **and** a real notebook-medium need has been logged | Only then reconsider C |
| Caught adding a surface feature not on the friction log, twice | That is the B-death signature — ban weekday tool work by calendar rule, not intention |

Sources: [opencode changelog](https://opencode.ai/changelog), [opencode release notes (releasebot)](https://releasebot.io/updates/sst/opencode), [opencode releases (GitHub)](https://github.com/anomalyco/opencode/releases), [Jupyter AI v3.0 release issue #1531](https://github.com/jupyterlab/jupyter-ai/issues/1531), [Persona API v0.1 discussion #1571](https://github.com/jupyterlab/jupyter-ai/issues/1571), [jupyter-ai-persona-manager](https://github.com/jupyter-ai-contrib/jupyter-ai-persona-manager), [jupyter-ai user guide (v3)](https://jupyter-ai.readthedocs.io/en/v3/users/).
