---
name: math-solution-assessment
description: Assess typed or handwritten mathematics solution attempts line by line using the active study pack's covered-work standard. Use for pasted proofs, exercise attempts, photos of handwritten work, proof feedback, and requests to find the first faulty inference.
---

# Math Solution Assessment

Use this skill when the user asks for feedback on a solution attempt, proof, computation, or handwritten image.

## Required Context

Before assessment, check:

- `studies/active.md` to identify the active study pack.
- The active study pack's `profile.md`, `workflow.md`, `source-priority.md`, and `state/progress.md` when present.
- The study pack's exercise index, edition notes, or exercise-verification files when the exercise source or numbering matters.

Use official hints or external solutions for feedback after an attempt, not as the first step unless the user asks.

## Assessment Workflow

1. Identify the exact exercise, theorem, definition, or claim being attempted.
2. For handwritten solution images, follow the photo protocols below — transcription is confirmed page by page before any assessment.
3. Check the argument line by line.
4. Identify the first faulty inference, not only the final wrong answer.
5. Separate mathematical correctness from clarity or presentation improvements.
6. State what is already correct before giving repairs.
7. Prefer the smallest repair that makes the user's proof work.
8. Offer one follow-up check or transfer prompt when useful.

## Photo Protocols

Photographed paper work is reviewed under one of two protocols. The user names which applies; if they did not, ask — never assume.

**`attempt` — graded assessment of finished work.**

- Transcribe each page to LaTeX with every uncertain span explicitly marked (`[unclear: b_n or b^n?]`). Present the transcription **one page at a time** and have the user confirm or correct that page before transcribing the next — a monolithic all-pages echo invites rubber-stamping.
- Only after every page is confirmed does assessment begin. Assess the confirmed transcription, not the image.
- Conclude with a verdict and record it (see Recording), including the archived scan path and the deepest hint rung used.

**`stuck-here` — help at a named stuck point, ungraded.**

- The user indicates where they are stuck. Read **no further than that point**: a photographed page usually contains their later scratch work, and reading ahead spoils the struggle.
- Transcribe and confirm only up to the stuck point, then respond with hint-ladder rung 1 — the smallest useful hint, ending with a question.
- No grading, no verdict, ever. Record with `--kind stuck-here`.

**Crossed-out work** is excluded from grading under both protocols. With the user's explicit consent, it may be mined: the first faulty inference in a discarded attempt is prime evidence for `state/misconceptions.md`. Ask before reading crossed-out work closely.

## Covered-Work Standard

Judge the solution using only covered definitions, propositions, examples, and proof patterns. Covered work is defined by the active study pack and any additional prior knowledge the user explicitly asks to include.

Do not criticize the absence of later terminology or later methods. If a proposed refinement uses later material, label it as a preview and do not treat it as required.

## Output Shape

Keep feedback concise unless the user asks for a full write-up. A useful default structure is:

- Verdict: correct, mostly correct, incomplete, or incorrect.
- First issue: the earliest step that fails or needs justification.
- Repair: the smallest correction or missing justification.
- Scope note: whether any suggested method is covered or a preview.

## Recording

After a review concludes, archive any scan first so the ledger references its
permanent home (`just archive-scan <inbox-file> <exercise-id>` prints the
archived path), then record:

```sh
tooter-state record-attempt --exercise <id> --kind attempt --verdict <verdict> \
  [--hint-depth N] [--image <archived path> ...] --summary "<one-line tutor summary>"
```

For `stuck-here` reviews use `--kind stuck-here` with no verdict. If an attempt
settles the exercise's standing (for example a clean proof), also update the
status: `tooter-state update-status --exercise <id> --status proved`.
Statuses: `unseen`, `attempted`, `needs-review`, `proved`, `re-derived`,
`transfers-ok`, `retired`. Do not hand-edit `state/attempts.jsonl`.
