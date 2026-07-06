from __future__ import annotations

from datetime import date, timedelta

from tooter_state import scheduling, store

TODAY = date(2026, 7, 6)


def test_interval_ladder() -> None:
    assert [scheduling.interval_for(i) for i in range(7)] == [1, 3, 7, 21, 60, 60, 60]


def test_proved_walks_the_ladder() -> None:
    record = store.new_record()
    for expected_days in (1, 3, 7, 21, 60, 60):
        scheduling.apply_status(record, "proved", TODAY)
        assert record["next_review"] == TODAY + timedelta(days=expected_days)


def test_needs_review_resets_ladder() -> None:
    record = store.new_record()
    record["review_index"] = 3
    scheduling.apply_status(record, "needs-review", TODAY)
    assert record["review_index"] == 0
    assert record["next_review"] == TODAY + timedelta(days=1)


def test_retired_clears_schedule() -> None:
    record = store.new_record()
    scheduling.apply_status(record, "proved", TODAY)
    scheduling.apply_status(record, "retired", TODAY)
    assert record["next_review"] is None


def test_propagation_pushes_outward_only(pack) -> None:
    sibling = store.new_record()
    sibling["status"] = "proved"
    sibling["patterns"] = ["subgroup-criterion"]
    sibling["next_review"] = TODAY + timedelta(days=2)
    sibling["review_index"] = 2  # next ladder step: 7 days
    store.upsert_exercise(pack, 3, "3.9", sibling)

    unrelated = store.new_record()
    unrelated["status"] = "proved"
    unrelated["patterns"] = ["other-pattern"]
    unrelated["next_review"] = TODAY + timedelta(days=2)
    store.upsert_exercise(pack, 3, "3.10", unrelated)

    messages = scheduling.propagate_proved(pack, "4.5", ["subgroup-criterion"], TODAY)
    assert len(messages) == 1 and "3.9" in messages[0]
    assert store.get_exercise(pack, 3, "3.9")["next_review"] == TODAY + timedelta(days=7)
    assert store.get_exercise(pack, 3, "3.10")["next_review"] == TODAY + timedelta(days=2)


def test_propagation_never_pulls_inward(pack) -> None:
    sibling = store.new_record()
    sibling["status"] = "proved"
    sibling["patterns"] = ["subgroup-criterion"]
    sibling["next_review"] = TODAY + timedelta(days=45)
    sibling["review_index"] = 1  # candidate would be today + 3
    store.upsert_exercise(pack, 3, "3.9", sibling)

    assert scheduling.propagate_proved(pack, "4.5", ["subgroup-criterion"], TODAY) == []
    assert store.get_exercise(pack, 3, "3.9")["next_review"] == TODAY + timedelta(days=45)


def test_set_status_creates_and_schedules(pack) -> None:
    record, messages = scheduling.set_status(
        pack, 6, "6.5", "proved", TODAY, patterns=["coset-counting"],
    )
    assert record["status"] == "proved"
    assert record["next_review"] == TODAY + timedelta(days=1)
    assert any("created new record" in m for m in messages)
    assert store.get_exercise(pack, 6, "6.5")["patterns"] == ["coset-counting"]
