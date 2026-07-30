"""Shared state operations behind both faces (CLI and MCP).

One set of functions, two transports (redesign-plan.md §3.3): the CLI
subcommands and the MCP tools both land here, so every surface mutates
state through identical code paths.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from . import scheduling, store, views
from .workspace import Pack


def chapter_for(exercise_id: str, chapter: int | None) -> int:
    if chapter:
        return chapter
    inferred = store.chapter_of(exercise_id)
    if inferred is None:
        raise store.StateError(
            f"cannot infer a chapter from {exercise_id!r}; pass the chapter number "
            "(--chapter N on the CLI)"
        )
    return inferred


def record_attempt(pack: Pack, *, exercise: str, chapter: int | None = None,
                   kind: str = "attempt", verdict: str | None = None,
                   hint_depth: int | None = None, images: list[str] | None = None,
                   summary: str | None = None, patterns: list[str] | None = None,
                   status: str | None = None, propagate: bool = True,
                   today: date, explicit_date: bool = False) -> tuple[dict[str, Any], list[str]]:
    """Append to the ledger, bump the exercise record, optionally set status.

    Returns (record, messages). ``explicit_date`` stamps the ledger at midnight
    of ``today`` (backfills); otherwise the wall clock is used.
    """
    resolved_chapter = chapter_for(exercise, chapter)
    if kind == "stuck-here" and hint_depth is None:
        hint_depth = 1  # smallest useful hint is the stuck-here contract
    store.append_attempt(
        pack,
        ts=store.now_iso(today if explicit_date else None),
        exercise=exercise,
        kind=kind,
        verdict=verdict,
        hint_depth=hint_depth,
        image_paths=list(images or []),
        tutor_summary=summary,
    )
    record = store.get_exercise(pack, resolved_chapter, exercise)
    if record is None:
        record = store.new_record("code" if exercise.startswith("code:") else "text")
    record["attempts"] += 1
    record["last_attempt"] = today
    if record["status"] == "unseen":
        record["status"] = "attempted"
    if patterns:
        record["patterns"] += [p for p in patterns if p not in record["patterns"]]
    store.upsert_exercise(pack, resolved_chapter, exercise, record)
    graded = f" (verdict: {verdict})" if verdict else ""
    messages = [f"recorded {kind} #{record['attempts']} for {exercise}{graded}"]
    if status:
        record, status_messages = scheduling.set_status(
            pack, resolved_chapter, exercise, status, today, propagate=propagate,
        )
        messages.extend(status_messages)
    return record, messages


def update_status(pack: Pack, *, exercise: str, status: str, chapter: int | None = None,
                  note: str | None = None, patterns: list[str] | None = None,
                  propagate: bool = True, today: date) -> tuple[dict[str, Any], list[str]]:
    return scheduling.set_status(
        pack, chapter_for(exercise, chapter), exercise, status, today,
        note=note, patterns=list(patterns or []), propagate=propagate,
    )


def due_reviews(pack: Pack, today: date, horizon_days: int = 0) -> dict[str, Any]:
    items = views.due_items(pack, today, horizon_days=horizon_days)
    return {
        "date": today.isoformat(),
        "horizon_days": horizon_days,
        "patterns": {
            pattern: [item.exercise_id for item in pattern_items]
            for pattern, pattern_items in views.due_patterns(items).items()
        },
        "exercises": [
            {"exercise": item.exercise_id, "chapter": item.chapter, **item.record}
            for item in items
        ],
    }


def get_exercise(pack: Pack, exercise: str, chapter: int | None = None) -> dict[str, Any] | None:
    record = store.get_exercise(pack, chapter_for(exercise, chapter), exercise)
    if record is None:
        return None
    return {"exercise": exercise, "chapter": chapter_for(exercise, chapter), **record}


def get_progress(pack: Pack) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    for _chapter, _exercise_id, record in store.iter_exercises(pack):
        status_counts[record["status"]] = status_counts.get(record["status"], 0) + 1
    progress_md = (
        pack.progress_file.read_text(encoding="utf-8")
        if pack.progress_file.is_file() else None
    )
    return {
        "pack": pack.name,
        "chapters": store.load_chapters(pack)["chapters"],
        "exercise_status_counts": status_counts,
        "misconceptions": views.misconception_bullets(pack),
        "progress_md": progress_md,
    }


def log_misconception(pack: Pack, *, text: str, topic: str | None = None,
                      evidence: list[str] | None = None) -> str:
    """Append one live-misconception bullet to state/misconceptions.md.

    Curation (rewording, deleting disconfirmed entries) stays tutor prose work;
    this only ever adds a bullet in the ledger's documented format.
    """
    if not text.strip():
        raise store.StateError("misconception text is empty")
    bullet = "- "
    if topic:
        bullet += f"[{topic}] "
    bullet += text.strip()
    if evidence:
        bullet += f" (evidence: {', '.join(evidence)})"
    path = pack.misconceptions_file
    if path.is_file():
        lines = path.read_text(encoding="utf-8").splitlines()
    else:
        lines = ["# Misconception Ledger", ""]
    lines = [line for line in lines if line.strip() != "(none yet)"]
    while lines and not lines[-1].strip():
        lines.pop()
    lines.append(bullet)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return bullet
