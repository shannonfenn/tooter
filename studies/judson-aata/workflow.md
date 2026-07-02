# Study Workflow

## Per Chapter

1. Read the 2021 print chapter.
2. Check `editions/2021-to-current.md` for known updates.
3. Answer Judson reading questions without notes.
4. Work Pitt Math 0430 assigned problems first.
5. Apply known Pitt-to-2021 renumbering from `exercises/verification.md`.
6. Use Judson hints only after an honest attempt.
7. Use Pitt solutions for feedback, not as the starting point.
8. Add one or more Sage checks when computation can clarify the structure.
9. Implement any programming exercise as a runnable Python or Sage file.
10. Update `state/progress.md` and `state/code-exercises.md`.

## Tutoring Loop

Use this sequence when asking an agent for help:

1. State the exact theorem, definition, or exercise.
2. Paste your attempt directly into chat, or attach a photo of handwritten work.
3. Ask for the smallest useful hint first unless you want a full solution.
4. Ask the agent to identify which concept failed if an answer is wrong.
5. After correction, ask for one transfer problem that tests the same idea.

## Computational Learning Loop

With `just` installed:

```sh
just ch03-groups
just exercise ch03_groups
```

For Python:

```sh
uv run python studies/judson-aata/code/python/exercises/ch03_groups.py
```

Ask Codex or another development agent for repository maintenance commands such as full test/lint runs or reference refreshes:

```sh
just test
just check
uv run pytest
uv run ruff check
uv run python studies/judson-aata/scripts/fetch_references.py
studies/judson-aata/scripts/update_aata_diff.sh
```
