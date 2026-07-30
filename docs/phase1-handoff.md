# Phase 1 handoff — the human steps

Everything buildable in Phase 1 is built, deployed, and pre-verified headlessly
(2026-07-30). These are the steps that need a phone, GUI settings, physical
scans, or learner judgment. Work top to bottom; nothing here is long.

## 1. First real session — final hour-one judgment

- [ ] `just study` in `tooter-studies` → browser opens `opencode web` on
      `127.0.0.1:4096` plus the dashboard tab. Confirm the project header says
      `~/dev/oth/github/tooter-studies` and the agent picker offers only
      Math-Pedagogy. (Stale "recent projects" rows for `/` and the old
      `learning-abstract-algebra-judson` path may linger — ignore or remove
      them; opening those gives an *unconfigured* session.)
- [ ] Run `/start`, do a little real tutoring with real math: judge the KaTeX
      rendering quality on a real transcript.
- [ ] Attach a real page scan to a message: judge legibility of the tutor's
      transcription (`/review-paper` flow).
- [ ] Confirm permission prompts still bite: ask the tutor to edit a file
      outside `studies/*/state/**` — expect a deny, not a prompt-free write.
- Failure branch (per plan §3.4): stay on `just study-tui` and bring the
  claude.ai surface forward; the state layer and tutor-core are unchanged.

## 2. iCloud + iPhone capture setup (~20 min once)

`just setup-capture` has already run: the iCloud inbox folder exists, repo
`inbox/` is a symlink to it, and the pin xattr is set.

- [ ] System Settings → [your name] → iCloud → Drive: **Optimize Mac Storage
      OFF** (forces eager replication).
- [ ] Finder → iCloud Drive → tooter-studies → right-click `inbox` →
      **Keep Downloaded** (verify the xattr pin took; this is the authoritative
      toggle).
- [ ] Build the iPhone shortcut "Scan to Inbox" and assign it to the Action
      Button. Exact recipe: workbench `docs/research/capture-apple.md` §4
      (paths there predate the rename — the destination is
      `iCloud Drive/tooter-studies/inbox`). Try the native "Scan Document"
      action first; if its save destination misbehaves from the Action Button,
      switch to the Actions-app variant in the same recipe.
- Until the shortcut exists (and whenever iCloud misbehaves), flow 2 works
  today with zero setup: park a Finder window on `inbox/` → right-click →
  Import from iPhone → **Scan Documents**.

## 3. Capture empirical tests (plan §4.3; harnesses ready)

- [ ] `just capture-test-latency` — ~20 Action-Button scans at the desk.
      **Gate: p90 ≤ 60s**, else flow 2 becomes primary (the script prints the
      verdict). Vary: display asleep, phone on Wi-Fi vs 5G.
- [ ] `just capture-test-resolution` — checks scan long-edge px against
      Claude's 2576px ceiling; also compare Grayscale vs Color file sizes.
- [ ] Native "Scan Document" action: does it save deterministically into the
      inbox from the Action Button with the phone locked? (Else: Actions-app
      variant.)
- [ ] Optional A/B: `just preprocess-scan inbox/<scan>.pdf`, then attach
      original and `-proc` variants to one session and compare transcriptions
      (subscripts, exponents, fraction bars). If preprocessing wins, it gets
      inserted into the consumer script — zero added manual steps.
- [ ] Optional flow-3 gate (Insta360): `just insta360-probe`, then the
      legibility test — dense page at 100%, transcription parity vs an iPhone
      scan. Adopt flow 3 only if it passes (plan §4.3).

## 4. Shakedown

- [ ] Finish **chapter 4 end-to-end** on the new system — `/start`, paper
      derivations, `/review-paper` both protocols, `/exit-check` advancing the
      boundary — before any further tooling investment (plan Phase 1, last
      item).

## Notes from the build

- opencode's project registry (sqlite, `~/.local/share/opencode/opencode.db`)
  pins each project's worktree path; after the Phase-0 repo move it still said
  `~/dev/src/...`, so `opencode web` opened a phantom, *enforcement-free*
  instance. Fixed 2026-07-30 (`project.worktree` updated; backup at
  `opencode.db.bak-20260730` — delete it once the web surface has behaved for
  a while). If the studies repo ever moves again, re-check this
  (`agent-harnesses.md` has the details).
- `opencode web` binds 127.0.0.1 without a server password and warns about it;
  fine for single-user localhost. Set `OPENCODE_SERVER_PASSWORD` in `just
  study` if that ever changes.
- The web session used one throwaway smoke message on the free model to verify
  KaTeX; the session was deleted. No learner state was written anywhere.
