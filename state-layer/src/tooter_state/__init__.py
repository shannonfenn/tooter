"""State layer for tooter study workspaces.

Two faces over identical state (redesign-plan.md §3.3): a CLI (`tooter-state`,
bash-allowlisted to the tutor) and a stdio MCP server (`tooter-state-mcp`)
exposing the same functions via shared ``ops``. State lives in the active
study pack:

- ``state/chapters.yaml``       chapter-level study state (structured source)
- ``state/exercises/chNN.yaml`` per-exercise records
- ``state/attempts.jsonl``      append-only attempt ledger; never edited
- ``state/misconceptions.md``   tutor-curated prose; not owned by this package
- ``state/queue.md``, ``state/dashboard.html``  derived views; disposable
- ``state/progress.md``         human-readable covered-work boundary view
"""

__version__ = "0.1.0"
