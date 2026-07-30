---
description: Review photographed paper work (attempt or stuck-here protocol)
agent: math-pedagogy
---

Use the `math-solution-assessment` skill and the active study pack from `studies/active.md`.

Capture inbox, freshly pulled from iCloud (`READY` files are downloaded and attachable):

!`just inbox`

Review my photographed paper work: `$ARGUMENTS`.

Follow the photo protocols in the `math-solution-assessment` skill exactly. In short:

1. Establish three things before reading any mathematics, asking one brief question if any is missing: which scan(s), which exercise, and which protocol — **`attempt`** (graded assessment of finished work) or **`stuck-here`** (smallest hint at a named stuck point, ungraded). Never assume the protocol. If the scan I name is not in the listing above, re-run `just inbox` — iCloud may still be syncing; if it stays missing, tell me instead of guessing.
2. Read the scan from the session attachment if I attached it; otherwise ask me to attach it or read the listed inbox file.
3. **attempt**: transcribe and confirm **one page at a time** with uncertain spans marked, and only after I confirm every page, assess (first faulty inference, smallest repair, verdict). **stuck-here**: I name the stuck point; read no further than it; give hint-ladder rung 1 only, ending with a question.
4. Archive the scan with `just archive-scan <inbox-file> <exercise-id>` and record the outcome with `tooter-state record-attempt`, passing the archived path via `--image`. For `attempt`, include the verdict and the deepest hint rung used; for `stuck-here`, no verdict ever.

Crossed-out work is excluded from grading. If a discarded attempt looks diagnostically interesting, ask whether I want it mined for the misconception ledger before reading it closely.
