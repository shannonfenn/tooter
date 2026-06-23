---
name: aata-study-planning
description: Plan Judson AATA chapter study, choose exercises from Pitt/MIT resources, check 2021-to-current AATA updates, and update progress tracking. Use for chapter plans, exercise selection, exit checks, and progress-tracking work.
---

# AATA Study Planning

Use this skill when the user asks for chapter planning, exercise selection, study status, exit checks, source verification, or progress tracking.

## Required Context

Read the relevant files before planning:

- `README.md` for overall study policy and repository layout.
- `docs/workflow.md` for the per-chapter study loop.
- `tracking/progress.md` for status and chapter notes.
- `tracking/pitt-math0430-index.md` for the primary exercise subset.
- `docs/pitt-exercise-verification.md` for known Pitt-to-2021 exercise renumbering.
- `docs/aata-2021-to-current.md` for current-edition corrections.

Use local files under `references/` when a source document is needed.

## Source Priority

Use sources in this order unless the user says otherwise:

1. Judson AATA 2021 print/PDF for the user's chapter and exercise numbering.
2. Current official AATA HTML/PDF and upstream Git diffs for corrections.
3. Pitt Math 0430 problem sets and solutions as the main exercise filter.
4. MIT OCW 18.703 lecture notes and assignments as secondary reference.
5. Sage/Runestone for computational checks and examples.

## Chapter Study Loop

The default per-chapter sequence is:

1. Read the 2021 print chapter.
2. Check `docs/aata-2021-to-current.md` for known updates.
3. Answer Judson reading questions without notes.
4. Work Pitt Math 0430 assigned problems first.
5. Apply known Pitt-to-2021 renumbering from `docs/pitt-exercise-verification.md`.
6. Use Judson hints only after an honest attempt.
7. Use Pitt solutions for feedback, not as the starting point.
8. Add Sage checks when computation can clarify the structure.
9. Implement programming exercises as runnable Python files.
10. Implement matching Rust examples.
11. Update `tracking/progress.md` and `tracking/code-exercises.md`.

## Progress Updates

Update `tracking/progress.md` and `tracking/code-exercises.md` only when work is completed or meaningfully advanced. Keep updates factual and compact. Preserve the existing table/status conventions.

Status values in `tracking/progress.md` are `not-started`, `reading`, `exercises`, `review`, `complete`, and `refresh`.
