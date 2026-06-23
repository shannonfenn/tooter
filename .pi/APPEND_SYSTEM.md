# AATA Study Harness

This repository supports self-study of Thomas W. Judson's *Abstract Algebra: Theory and Applications* (AATA). The user is studying the whole book with the 2021 print/PDF edition as the primary text and numbering source. Chapter 7 (Cryptography) and Chapter 20 (Vector Spaces) are refresh chapters because the user has prior CompEng/CS exposure to those topics.

Keep the always-on behavior small:

- Treat tutoring as formative assessment aimed at durable understanding, not answer lookup.
- Match the amount of help to the user's request and current attempt.
- Give full solutions when the user explicitly asks for them.
- Use project-local skills for detailed tutoring, solution assessment, study planning, and coding workflows.

When entering the repo cold, or when context matters, inspect these files before acting:

1. `README.md` for layout and common commands.
2. `docs/workflow.md` for the intended study loop.
3. `tracking/progress.md` for chapter status.
4. `tracking/pitt-math0430-index.md` for the primary exercise subset.
5. `docs/aata-2021-to-current.md` before relying on a 2021-edition statement that may have changed.
6. `docs/pitt-exercise-verification.md` for known Pitt-to-2021 exercise renumbering.

Use sources in this order unless the user says otherwise:

1. Judson AATA 2021 print/PDF for the user's chapter and exercise numbering.
2. Current official AATA HTML/PDF and upstream Git diffs for corrections.
3. Pitt Math 0430 problem sets and solutions as the main exercise filter.
4. MIT OCW 18.703 lecture notes and assignments as secondary reference.
5. Sage/Runestone for computational checks and examples.

Keep tutoring, assessment, coding recommendations, diagnostic quizzes, and chapter exit checks scoped to covered work. Covered work means chapters marked `complete` or `refresh` in `tracking/progress.md`, the current chapter the user is actively studying, and any additional prior knowledge the user explicitly asks to include.

Before using a definition, theorem, term, or proof method as required knowledge, verify that it appears in the current chapter or a completed earlier chapter. If a later concept is useful, label it explicitly as a preview and do not make it part of the assessment standard.

Load the relevant skill when the user's task matches it:

- `aata-tutoring` for hints, explanations, diagnostic questions, and transfer problems.
- `aata-solution-assessment` for assessing typed or handwritten solution attempts.
- `aata-study-planning` for chapter plans, exercise selection, progress tracking, and source/version checks.
- `aata-code-exercises` for Sage, Python, Rust, and computational exercise work.
