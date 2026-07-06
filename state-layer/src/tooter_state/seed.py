"""One-shot migration: seed structured state from the hand-edited v0 tables.

Parses the active pack's ``state/progress.md`` chapter table into
``state/chapters.yaml`` and ``state/code-exercises.md`` into per-exercise
records, then creates the empty attempt ledger and the misconception-ledger
skeleton. ``progress.md`` itself is left in place — it survives as the
human-readable covered-work boundary view. Deleting ``code-exercises.md``
afterwards is a git operation, deliberately not done here.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from . import store
from .workspace import Pack

# Enrichment for known v0 rows: topic text -> (exercise id, pattern tags).
KNOWN_CODE_EXERCISES = {
    "Euclidean algorithm and Bezout coefficients":
        ("code:euclidean-bezout", ["euclidean-algorithm", "bezout-identity"]),
    "Finite group checker and subgroup test":
        ("code:group-checker", ["group-axioms", "subgroup-criterion"]),
}

# v0 python-status column -> state-layer status. "complete" maps to retired:
# a finished one-off programming exercise leaves the review rotation (proof
# patterns, not code artifacts, are the unit of review).
CODE_STATUS_MAP = {
    "started": "attempted",
    "in progress": "attempted",
    "complete": "retired",
    "done": "retired",
}

MISCONCEPTIONS_SKELETON = """\
# Misconception Ledger

One bullet per **live** misconception, curated by the tutor. Each bullet cites
its evidence (attempt timestamps from `attempts.jsonl`). Delete a bullet when
the misconception is disconfirmed — this file lists live issues, not history.

<!-- format: - [pattern-or-topic] the misconception, stated plainly (evidence: ts, ts) -->

(none yet)
"""


class SeedError(RuntimeError):
    """Migration cannot proceed."""


def parse_md_table(text: str) -> list[dict[str, str]]:
    """Parse the first pipe table in ``text`` into row dicts keyed by header."""
    rows: list[list[str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not (line.startswith("|") and line.endswith("|")):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    if len(rows) < 2:
        return []
    header = rows[0]
    return [dict(zip(header, row, strict=False)) for row in rows[1:]]


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def seed_chapters(pack: Pack) -> int:
    text = pack.progress_file.read_text(encoding="utf-8")
    rows = parse_md_table(text)
    if not rows:
        raise SeedError(f"no chapter table found in {pack.progress_file}")
    chapters: list[dict[str, Any]] = []
    for row in rows:
        chapters.append({
            "ch": int(row["Ch"]),
            "topic": row["AATA topic"],
            "mode": row["Study mode"],
            "status": row["Status"],
            "sources": {"pitt": row["Pitt first"], "mit": row["MIT backup"]},
            "note": row["Notes"],
        })
    store.save_chapters(pack, {"chapters": chapters})
    return len(chapters)


def seed_code_exercises(pack: Pack) -> list[str]:
    path = pack.state_dir / "code-exercises.md"
    if not path.is_file():
        return []
    rows = parse_md_table(path.read_text(encoding="utf-8"))
    seeded: list[str] = []
    for row in rows:
        topic = row["Exercise/topic"]
        chapter = int(row["Chapter"])
        exercise_id, patterns = KNOWN_CODE_EXERCISES.get(
            topic, (f"code:{_slug(topic)[:40].rstrip('-')}", [])
        )
        raw_status = row.get("Python status", "").lower()
        status = CODE_STATUS_MAP.get(raw_status, "attempted")
        note = (f"{row.get('Notes', '')} [seeded from code-exercises.md: "
                f"python status '{row.get('Python status', '')}', "
                f"tests: {row.get('Tests', '')}]")
        record = store.new_record("code")
        record["status"] = status
        record["patterns"] = patterns
        record["note"] = note
        store.upsert_exercise(pack, chapter, exercise_id, record)
        seeded.append(f"{exercise_id} (ch {chapter}, {status})")
    return seeded


def seed(pack: Pack, today: date, *, force: bool = False) -> list[str]:
    if pack.chapters_file.exists() and not force:
        raise SeedError(f"{pack.chapters_file} already exists; re-run with --force to reseed")
    messages = [f"seeded chapters.yaml with {seed_chapters(pack)} chapters"]
    messages += [f"seeded {entry}" for entry in seed_code_exercises(pack)]
    if not pack.attempts_file.exists():
        pack.attempts_file.parent.mkdir(parents=True, exist_ok=True)
        pack.attempts_file.touch()
        messages.append("created empty attempts.jsonl")
    if not pack.misconceptions_file.exists():
        pack.misconceptions_file.write_text(MISCONCEPTIONS_SKELETON, encoding="utf-8")
        messages.append("created misconceptions.md skeleton")
    messages.append(f"progress.md left in place as the boundary view ({today.isoformat()})")
    return messages
