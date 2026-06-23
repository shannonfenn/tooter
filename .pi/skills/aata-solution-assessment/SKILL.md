---
name: aata-solution-assessment
description: Assess typed or handwritten Judson AATA solution attempts line by line using only covered material. Use for pasted proofs, exercise attempts, photos of handwritten work, proof feedback, and requests to find the first faulty inference.
---

# AATA Solution Assessment

Use this skill when the user asks for feedback on a solution attempt, proof, computation, or handwritten image.

## Required Context

Before assessment, check:

- `tracking/progress.md` for covered chapters and current likely chapter.
- `docs/workflow.md` for the tutoring and exercise loops.
- `docs/aata-2021-to-current.md` if the statement may differ between the 2021 and current AATA editions.
- `docs/pitt-exercise-verification.md` if the exercise comes from Pitt numbering.

Use Judson hints and Pitt solutions for feedback after an attempt, not as the first step unless the user asks.

## Assessment Workflow

1. Identify the exact exercise, theorem, definition, or claim being attempted.
2. For handwritten solution images, first transcribe the relevant mathematical claims.
3. Check the argument line by line.
4. Identify the first faulty inference, not only the final wrong answer.
5. Separate mathematical correctness from clarity or presentation improvements.
6. State what is already correct before giving repairs.
7. Prefer the smallest repair that makes the user's proof work.
8. Offer one follow-up check or transfer prompt when useful.

## Covered-Work Standard

Judge the solution using only covered definitions, propositions, examples, and proof patterns. Covered work means chapters marked `complete` or `refresh` in `tracking/progress.md`, the current chapter the user is actively studying, and prior knowledge the user explicitly asks to include.

Do not criticize the absence of later terminology or later methods. If a proposed refinement uses later material, label it as a preview and do not treat it as required.

Examples:

- In Chapter 3, distinguish groups using tools available there, such as Cayley tables, commutativity, subgroup structure, and concrete element behavior. Do not require isomorphism language unless the user asks for a preview.
- In Chapter 3, do not use element order, cyclic subgroups, generated subgroups, or subgroup generation as completion criteria; those belong to Chapter 4 unless explicitly introduced as previews.

## Output Shape

Keep feedback concise unless the user asks for a full write-up. A useful default structure is:

- Verdict: correct, mostly correct, incomplete, or incorrect.
- First issue: the earliest step that fails or needs justification.
- Repair: the smallest correction or missing justification.
- Scope note: whether any suggested method is covered or a preview.
