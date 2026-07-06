"""Review scheduling: expanding-interval ladder plus FIRe-lite propagation.

Ladder (redesign-plan.md §3.3): 1/3/7/21/60 days, indexed by how many
successful reviews an exercise has had (``review_index``). ``needs-review``
resets the ladder and comes back tomorrow. FIRe-lite: when an exercise is
``proved``, other scheduled exercises sharing one of its patterns get their
``next_review`` pushed *outward* (never inward) — proving fresh work is
implicit retrieval of its prerequisite patterns. ``py-fsrs`` is a later
drop-in only if interval feel proves wrong.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from . import store
from .workspace import Pack

INTERVALS = (1, 3, 7, 21, 60)

# Statuses that sit in the review rotation.
SCHEDULED_STATUSES = ("proved", "re-derived", "transfers-ok")


def interval_for(review_index: int) -> int:
    return INTERVALS[min(max(review_index, 0), len(INTERVALS) - 1)]


def apply_status(record: dict[str, Any], status: str, today: date) -> dict[str, Any]:
    """Set ``status`` on ``record`` and update its schedule. Mutates and returns it."""
    if status not in store.STATUSES:
        raise store.StateError(
            f"unknown status {status!r} (expected one of {store.STATUSES})"
        )
    record["status"] = status
    if status in SCHEDULED_STATUSES:
        record["next_review"] = today + timedelta(days=interval_for(record["review_index"]))
        record["review_index"] = record["review_index"] + 1
    elif status == "needs-review":
        record["review_index"] = 0
        record["next_review"] = today + timedelta(days=1)
    elif status == "retired":
        record["next_review"] = None
    # unseen/attempted: not in the rotation yet; leave next_review untouched.
    return record


def propagate_proved(pack: Pack, exercise_id: str, patterns: list[str],
                     today: date) -> list[str]:
    """Push sibling reviews outward after a proof; returns human-readable messages."""
    if not patterns:
        return []
    shared = set(patterns)
    messages: list[str] = []
    for chapter, other_id, record in list(store.iter_exercises(pack)):
        if other_id == exercise_id:
            continue
        if record["status"] not in SCHEDULED_STATUSES or record["next_review"] is None:
            continue
        overlap = shared & set(record["patterns"])
        if not overlap:
            continue
        candidate = today + timedelta(days=interval_for(record["review_index"]))
        if candidate > record["next_review"]:
            old = record["next_review"]
            record["next_review"] = candidate
            store.upsert_exercise(pack, chapter, other_id, record)
            messages.append(
                f"pushed {other_id} outward {old.isoformat()} -> {candidate.isoformat()} "
                f"(shared: {', '.join(sorted(overlap))})"
            )
    return messages


def set_status(pack: Pack, chapter: int, exercise_id: str, status: str, today: date,
               *, note: str | None = None, patterns: list[str] | None = None,
               propagate: bool = True) -> tuple[dict[str, Any], list[str]]:
    """Upsert an exercise record with a new status; returns (record, messages)."""
    messages: list[str] = []
    record = store.get_exercise(pack, chapter, exercise_id)
    if record is None:
        kind = "code" if exercise_id.startswith("code:") else "text"
        record = store.new_record(kind)
        messages.append(f"created new record for {exercise_id} (ch {chapter})")
    old_status = record["status"]
    if patterns:
        record["patterns"] = record["patterns"] + [
            p for p in patterns if p not in record["patterns"]
        ]
    if note is not None:
        record["note"] = note
    apply_status(record, status, today)
    store.upsert_exercise(pack, chapter, exercise_id, record)
    summary = f"{exercise_id}: status {old_status} -> {status}"
    if record["next_review"] is not None:
        summary += f"; next review {record['next_review'].isoformat()}"
    messages.append(summary)
    if status == "proved" and propagate:
        messages.extend(propagate_proved(pack, exercise_id, record["patterns"], today))
    return record, messages
