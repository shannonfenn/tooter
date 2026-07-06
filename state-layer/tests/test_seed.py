from __future__ import annotations

from datetime import date

import pytest

from tooter_state import seed, store
from tooter_state.workspace import Pack

TODAY = date(2026, 7, 6)

PROGRESS = """\
# Chapter Progress

Status values: `not-started`, `reading`, `exercises`, `review`, `complete`, `refresh`.

| Ch | AATA topic | Study mode | Status | Pitt first | MIT backup | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Preliminaries | full | complete | yes | limited | Completed before kickoff. |
| 2 | The Integers | full | complete | yes | limited | Sage sketch exists. |
| 3 | Groups | full | complete | yes | yes | Core exercises done. |
| 4 | Cyclic Groups | full | not-started | yes | yes | Include programming exercises. |
"""

CODE_EXERCISES = """\
# Programming Exercise Tracking

| Chapter | Exercise/topic | Python status | Tests | Notes |
| --- | --- | --- | --- | --- |
| 2 | Euclidean algorithm and Bezout coefficients | started | Property tests | Sage sketch. |
| 3 | Finite group checker and subgroup test | complete | Unit tests | Runnable exercise. |
"""


@pytest.fixture
def seeded_pack(pack: Pack) -> Pack:
    pack.progress_file.write_text(PROGRESS, encoding="utf-8")
    (pack.state_dir / "code-exercises.md").write_text(CODE_EXERCISES, encoding="utf-8")
    return pack


def test_seed_migrates_both_tables(seeded_pack: Pack) -> None:
    messages = seed.seed(seeded_pack, TODAY)
    assert any("4 chapters" in m for m in messages)

    chapters = store.load_chapters(seeded_pack)["chapters"]
    assert [c["ch"] for c in chapters] == [1, 2, 3, 4]
    assert chapters[2]["status"] == "complete"
    assert chapters[3]["topic"] == "Cyclic Groups"
    assert chapters[0]["sources"] == {"pitt": "yes", "mit": "limited"}

    euclid = store.get_exercise(seeded_pack, 2, "code:euclidean-bezout")
    assert euclid["kind"] == "code"
    assert euclid["status"] == "attempted"
    assert euclid["patterns"] == ["euclidean-algorithm", "bezout-identity"]

    checker = store.get_exercise(seeded_pack, 3, "code:group-checker")
    assert checker["status"] == "retired"
    assert "python status 'complete'" in checker["note"]

    assert seeded_pack.attempts_file.exists()
    assert "Misconception Ledger" in seeded_pack.misconceptions_file.read_text()
    # progress.md untouched
    assert seeded_pack.progress_file.read_text() == PROGRESS


def test_seed_refuses_to_overwrite(seeded_pack: Pack) -> None:
    seed.seed(seeded_pack, TODAY)
    with pytest.raises(seed.SeedError, match="--force"):
        seed.seed(seeded_pack, TODAY)
    seed.seed(seeded_pack, TODAY, force=True)  # explicit reseed allowed


def test_parse_md_table_skips_separator() -> None:
    rows = seed.parse_md_table(PROGRESS)
    assert len(rows) == 4
    assert rows[0]["AATA topic"] == "Preliminaries"
