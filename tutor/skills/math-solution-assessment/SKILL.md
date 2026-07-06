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
2. For handwritten solution images, first transcribe the relevant mathematical claims and have the user confirm the transcription before assessing.
3. Check the argument line by line.
4. Identify the first faulty inference, not only the final wrong answer.
5. Separate mathematical correctness from clarity or presentation improvements.
6. State what is already correct before giving repairs.
7. Prefer the smallest repair that makes the user's proof work.
8. Offer one follow-up check or transfer prompt when useful.

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

After an assessment concludes, record it in the state layer:

```sh
tooter-state record-attempt --exercise <id> --kind attempt --verdict <verdict> \
  [--hint-depth N] [--image <path> ...] --summary "<one-line tutor summary>"
```

If the attempt settles the exercise's standing (for example a clean proof), also
update the status: `tooter-state update-status --exercise <id> --status proved`.
Statuses: `unseen`, `attempted`, `needs-review`, `proved`, `re-derived`,
`transfers-ok`, `retired`. Do not hand-edit `state/attempts.jsonl`.
