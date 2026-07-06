"""YAML/JSONL state IO.

``state/attempts.jsonl`` is append-only by contract: this module exposes no
way to rewrite it. Exercise records live in ``state/exercises/chNN.yaml`` as a
mapping of exercise id to record; chapter-level state lives in
``state/chapters.yaml``.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from collections.abc import Iterator
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from .workspace import Pack

STATUSES = ("unseen", "attempted", "needs-review", "proved", "re-derived", "transfers-ok",
            "retired")
ATTEMPT_KINDS = ("attempt", "stuck-here")
VERDICTS = ("correct", "mostly-correct", "incomplete", "incorrect")
EXERCISE_KINDS = ("text", "code")

# Stable field order for dumped exercise records.
FIELD_ORDER = ("kind", "status", "patterns", "attempts", "last_attempt", "next_review",
               "review_index", "note")

_CHAPTER_ID_RE = re.compile(r"^(\d+)\.")

EXERCISES_HEADER = (
    "# Per-exercise records — written by `tooter-state`; hand-edits OK for patterns/notes.\n"
    "# Statuses: unseen attempted needs-review proved re-derived transfers-ok retired.\n"
    "# next_review/review_index are managed by the scheduling ladder; avoid editing them.\n"
)
CHAPTERS_HEADER = (
    "# Chapter-level study state — structured source behind state/progress.md.\n"
    "# Keep in step with progress.md; an exit check is the only path that advances\n"
    "# the covered-work boundary.\n"
)


class StateError(RuntimeError):
    """Invalid state operation or malformed state file."""


def new_record(kind: str = "text") -> dict[str, Any]:
    if kind not in EXERCISE_KINDS:
        raise StateError(f"unknown exercise kind {kind!r} (expected one of {EXERCISE_KINDS})")
    return {
        "kind": kind,
        "status": "unseen",
        "patterns": [],
        "attempts": 0,
        "last_attempt": None,
        "next_review": None,
        "review_index": 0,
        "note": None,
    }


def chapter_of(exercise_id: str) -> int | None:
    """Infer the chapter from a text-exercise id like ``4.5``; None if not inferable."""
    match = _CHAPTER_ID_RE.match(exercise_id)
    return int(match.group(1)) if match else None


def exercise_file(pack: Pack, chapter: int) -> Path:
    return pack.exercises_dir / f"ch{chapter:02d}.yaml"


def as_date(value: Any) -> date | None:
    if value is None or isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _normalise_record(record: dict[str, Any]) -> dict[str, Any]:
    base = new_record(record.get("kind", "text"))
    for key, default in base.items():
        record.setdefault(key, default)
    if record["status"] not in STATUSES:
        raise StateError(f"unknown status {record['status']!r} (expected one of {STATUSES})")
    record["patterns"] = list(record["patterns"] or [])
    record["attempts"] = int(record["attempts"])
    record["review_index"] = int(record["review_index"])
    record["last_attempt"] = as_date(record["last_attempt"])
    record["next_review"] = as_date(record["next_review"])
    return {key: record[key] for key in FIELD_ORDER}


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        umask = os.umask(0)
        os.umask(umask)
        os.chmod(tmp, 0o666 & ~umask)  # mkstemp defaults to 0600
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


def _dump_yaml(header: str, data: dict[str, Any]) -> str:
    body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100)
    return header + body


def load_chapter_exercises(pack: Pack, chapter: int) -> dict[str, Any]:
    path = exercise_file(pack, chapter)
    if not path.is_file():
        return {"chapter": chapter, "exercises": {}}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    exercises = data.get("exercises") or {}
    return {
        "chapter": int(data.get("chapter", chapter)),
        "exercises": {str(k): _normalise_record(dict(v)) for k, v in exercises.items()},
    }


def save_chapter_exercises(pack: Pack, chapter: int, data: dict[str, Any]) -> Path:
    path = exercise_file(pack, chapter)
    ordered = {
        "chapter": int(data.get("chapter", chapter)),
        "exercises": {
            key: _normalise_record(dict(value))
            for key, value in sorted(data.get("exercises", {}).items())
        },
    }
    _atomic_write(path, _dump_yaml(EXERCISES_HEADER, ordered))
    return path


def get_exercise(pack: Pack, chapter: int, exercise_id: str) -> dict[str, Any] | None:
    record = load_chapter_exercises(pack, chapter)["exercises"].get(exercise_id)
    return dict(record) if record else None


def upsert_exercise(pack: Pack, chapter: int, exercise_id: str,
                    record: dict[str, Any]) -> dict[str, Any]:
    data = load_chapter_exercises(pack, chapter)
    data["exercises"][exercise_id] = _normalise_record(dict(record))
    save_chapter_exercises(pack, chapter, data)
    return data["exercises"][exercise_id]


def iter_exercises(pack: Pack) -> Iterator[tuple[int, str, dict[str, Any]]]:
    if not pack.exercises_dir.is_dir():
        return
    for path in sorted(pack.exercises_dir.glob("ch*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        chapter = int(data.get("chapter", 0))
        for exercise_id, record in (data.get("exercises") or {}).items():
            yield chapter, str(exercise_id), _normalise_record(dict(record))


def append_attempt(pack: Pack, *, ts: str, exercise: str, kind: str,
                   verdict: str | None, hint_depth: int | None,
                   image_paths: list[str], tutor_summary: str | None) -> dict[str, Any]:
    """Append one record to attempts.jsonl. The only write path — append mode only."""
    if kind not in ATTEMPT_KINDS:
        raise StateError(f"unknown attempt kind {kind!r} (expected one of {ATTEMPT_KINDS})")
    if kind == "stuck-here" and verdict is not None:
        raise StateError("stuck-here attempts are not graded; drop the verdict")
    if verdict is not None and verdict not in VERDICTS:
        raise StateError(f"unknown verdict {verdict!r} (expected one of {VERDICTS})")
    record = {
        "ts": ts,
        "exercise": exercise,
        "kind": kind,
        "verdict": verdict,
        "hint_depth": hint_depth,
        "image_paths": list(image_paths),
        "tutor_summary": tutor_summary,
    }
    pack.attempts_file.parent.mkdir(parents=True, exist_ok=True)
    with pack.attempts_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def read_attempts(pack: Pack) -> list[dict[str, Any]]:
    if not pack.attempts_file.is_file():
        return []
    records = []
    for line in pack.attempts_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def load_chapters(pack: Pack) -> dict[str, Any]:
    if not pack.chapters_file.is_file():
        return {"chapters": []}
    data = yaml.safe_load(pack.chapters_file.read_text(encoding="utf-8")) or {}
    return {"chapters": list(data.get("chapters") or [])}


def save_chapters(pack: Pack, data: dict[str, Any]) -> Path:
    ordered = {"chapters": list(data.get("chapters") or [])}
    _atomic_write(pack.chapters_file, _dump_yaml(CHAPTERS_HEADER, ordered))
    return pack.chapters_file


def now_iso(today: date | None = None) -> str:
    """Timestamp for the attempt ledger; midnight when a --date override is used."""
    if today is not None:
        return datetime.combine(today, datetime.min.time()).isoformat(timespec="seconds")
    return datetime.now().isoformat(timespec="seconds")
