from __future__ import annotations

from datetime import date

import pytest

from tooter_state import store


def test_chapter_of() -> None:
    assert store.chapter_of("4.5") == 4
    assert store.chapter_of("13.2a") == 13
    assert store.chapter_of("code:group-checker") is None


def test_round_trip_preserves_record(pack) -> None:
    record = store.new_record()
    record["status"] = "proved"
    record["patterns"] = ["coset-counting"]
    record["last_attempt"] = date(2026, 7, 1)
    record["next_review"] = date(2026, 7, 8)
    record["review_index"] = 2
    record["note"] = "clean second pass"
    store.upsert_exercise(pack, 6, "6.5", record)

    loaded = store.get_exercise(pack, 6, "6.5")
    assert loaded == {
        "kind": "text",
        "status": "proved",
        "patterns": ["coset-counting"],
        "attempts": 0,
        "last_attempt": date(2026, 7, 1),
        "next_review": date(2026, 7, 8),
        "review_index": 2,
        "note": "clean second pass",
    }


def test_iter_exercises_spans_chapters(pack) -> None:
    store.upsert_exercise(pack, 2, "2.1", store.new_record())
    store.upsert_exercise(pack, 11, "11.3", store.new_record())
    found = {(ch, ex) for ch, ex, _ in store.iter_exercises(pack)}
    assert found == {(2, "2.1"), (11, "11.3")}


def test_append_attempt_is_append_only(pack) -> None:
    first = store.append_attempt(
        pack, ts="2026-07-06T10:00:00", exercise="4.1", kind="attempt",
        verdict="correct", hint_depth=None, image_paths=[], tutor_summary="ok",
    )
    store.append_attempt(
        pack, ts="2026-07-06T11:00:00", exercise="4.2", kind="stuck-here",
        verdict=None, hint_depth=1, image_paths=["attempts/2026/p1.png"],
        tutor_summary=None,
    )
    attempts = store.read_attempts(pack)
    assert len(attempts) == 2
    assert attempts[0] == first
    assert list(attempts[1].keys()) == [
        "ts", "exercise", "kind", "verdict", "hint_depth", "image_paths", "tutor_summary",
    ]


def test_stuck_here_rejects_verdict(pack) -> None:
    with pytest.raises(store.StateError, match="not graded"):
        store.append_attempt(
            pack, ts="2026-07-06T10:00:00", exercise="4.1", kind="stuck-here",
            verdict="correct", hint_depth=1, image_paths=[], tutor_summary=None,
        )


def test_unknown_status_rejected(pack) -> None:
    record = store.new_record()
    record["status"] = "mastered"  # deliberately not a status (§5)
    with pytest.raises(store.StateError, match="unknown status"):
        store.upsert_exercise(pack, 3, "3.1", record)
