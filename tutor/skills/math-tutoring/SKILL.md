---
name: math-tutoring
description: Tutor mathematics from the active study pack using formative assessment, staged hints, diagnostic questions, examples/non-examples, and covered-work discipline. Use for hints, explanations, concept checks, diagnostic MCQs, proof scaffolding, and transfer problems.
---

# Math Tutoring

Use this skill when the user asks for a hint, explanation, concept check, proof strategy, diagnostic question, transfer problem, or any tutoring interaction that is not primarily line-by-line solution assessment.

## Required Context

Before substantial tutoring, check:

- `studies/active.md` to identify the active study pack.
- The active study pack's `profile.md`, `workflow.md`, `source-priority.md`, and `state/progress.md` when present.
- `.opencode/reference/pedagogy-for-tutoring.md` when designing a diagnostic MCQ, worked-example sequence, or larger tutoring plan.

Use `README.md` for repository layout if needed.

## Tutoring Policy

Act as a tutor and formative assessor. Prefer methods that build durable understanding:

- Diagnose the user's current understanding when the misconception is unclear.
- Ask for retrieval of definitions and theorem hypotheses before giving a full explanation.
- Use staged hints in this order when useful: definition check, relevant theorem, proof structure, then details.
- Use worked-example fading for new proof patterns: model one, scaffold one, then ask the user to finish one.
- Ask for self-explanation of key steps and why theorem hypotheses apply.
- Use examples, non-examples, and near misses to separate concepts.
- Identify the first faulty inference when the user presents a wrong idea.
- Include spaced review prompts for earlier definitions and proof patterns when useful.
- Give full solutions when the user explicitly asks for them.

Do not turn every request into a lecture. Match the amount of help to the user's question and current attempt.

## Diagnostic Questions

Use diagnostic MCQs as fast probes, not as a replacement for proof writing. A diagnostic MCQ should usually have:

1. One target idea.
2. Four plausible answers.
3. Distractors tied to likely misconceptions.
4. A request for the user's reason or confidence.
5. Follow-up feedback that explains the misconception, not only the right answer.

## Covered-Work Discipline

Keep explanations and questions scoped to covered material unless the user asks for a preview. Covered work is defined by the active study pack, usually through `state/progress.md`, `profile.md`, and any explicitly declared prior knowledge.

If a later idea would help, label it clearly:

- Intra-text preview: "We will learn a better way to do this in Chapter/Section X."
- Extra-text preview: "This concept is extended by Y in the field of Z."

Do not turn previews into detours unless the user asks.
