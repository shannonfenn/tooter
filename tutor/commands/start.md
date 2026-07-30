---
description: Open a study session with due-review and misconception retrieval prompts
agent: math-pedagogy
---

Use the `math-tutoring` and `math-study-planning` skills and the active study pack from `studies/active.md`.

Today's due reviews from the state layer (patterns first — the exercise ids are only the vehicle):

!`tooter-state due`

Live misconception ledger:

!`cat studies/*/state/misconceptions.md`

Open my study session from that injected state. The two blocks above are tutor context — do not paste them back at me.

1. If patterns are due, take the one or two highest-value ones and turn each into a **freshly generated retrieval or transfer prompt** — a definition to state, a theorem hypothesis to recall, or a small new problem exercising the pattern. Never re-show prior work, never summarize what I did before; the generation effort is the point.
2. Take up to two live misconceptions and turn each into a **retrieval prompt** ("Before we start: define the normalizer and the centralizer of a subgroup") — never state the misconception or its correction.
3. Then ask what I am working on today, suggesting the current chapter from the active pack's `state/progress.md` if I have nothing queued.

Keep the opening tight: greet in one line, pose the prompts, stop, and wait for my answers before any teaching. If nothing is due and no misconceptions are live, say so in one line and go straight to step 3.
