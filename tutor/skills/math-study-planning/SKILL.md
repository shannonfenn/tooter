---
name: math-study-planning
description: Plan mathematics study from the active study pack, choose exercises, check edition/source notes, and update progress tracking. Use for chapter or section plans, exercise selection, exit checks, and progress-tracking work.
---

# Math Study Planning

Use this skill when the user asks for chapter or section planning, exercise selection, study status, exit checks, source verification, or progress tracking.

## Required Context

Read the relevant files before planning:

- `studies/active.md` to identify the active study pack.
- The active study pack's `profile.md` for the text, learner context, and study goals.
- The active study pack's `workflow.md` for the study loop.
- The active study pack's `state/progress.md` for status and covered-work boundaries.
- The active study pack's `source-priority.md` for source order.
- The active study pack's exercise index, edition notes, or verification notes when available.
- `tooter-state due` for exercises and proof patterns due for review.

Use `README.md` for repository layout and commands.

## Planning Policy

- Treat the active study pack as the source of text-specific policy.
- Prefer the study pack's primary exercise filter when one exists.
- Check edition/update notes before relying on a statement that may differ across editions.
- Use external solutions for feedback after an attempt, not as the starting point unless the user asks.
- Include computational checks only when they clarify the current covered material.
- Fold due reviews into plans as freshly generated retrieval or transfer prompts against the due pattern — never as a re-read of prior work.

## Progress Updates

Learner state is structured and written through the `tooter-state` CLI:

- `tooter-state record-attempt` after an assessed attempt or stuck-point.
- `tooter-state update-status --exercise <id> --status <status>` when an exercise's standing changes (statuses: `unseen`, `attempted`, `needs-review`, `proved`, `re-derived`, `transfers-ok`, `retired` — there is deliberately no "mastered").
- `tooter-state due` and `tooter-state build-queue` for review scheduling.

`state/progress.md` remains the human-readable covered-work boundary view; update it only when the boundary genuinely moves (an exit check is the only path that advances it), preserving its existing table conventions, and mirror chapter-status changes in `state/chapters.yaml`. Never edit `state/attempts.jsonl` (append-only, CLI-written) or the derived views `state/queue.md` and `state/dashboard.html`.
