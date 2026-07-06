from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from tooter_state import store
from tooter_state.cli import main
from tooter_state.workspace import Pack

TODAY = "2026-07-06"


def run(workspace: Path, *argv: str) -> int:
    return main(["--root", str(workspace), "--date", TODAY, *argv])


def test_record_attempt_end_to_end(workspace: Path, pack: Pack, capsys) -> None:
    assert run(
        workspace, "record-attempt", "--exercise", "4.5", "--verdict", "mostly-correct",
        "--hint-depth", "2", "--image", "attempts/2026/p1.png",
        "--summary", "well-definedness gap", "--patterns", "cyclic-subgroups",
    ) == 0
    lines = pack.attempts_file.read_text().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["exercise"] == "4.5"
    assert entry["verdict"] == "mostly-correct"
    assert entry["hint_depth"] == 2
    assert entry["image_paths"] == ["attempts/2026/p1.png"]
    assert entry["tutor_summary"] == "well-definedness gap"

    record = store.get_exercise(pack, 4, "4.5")
    assert record["status"] == "attempted"  # unseen -> attempted
    assert record["attempts"] == 1
    assert record["last_attempt"] == date(2026, 7, 6)
    assert record["patterns"] == ["cyclic-subgroups"]
    assert "recorded attempt #1 for 4.5" in capsys.readouterr().out


def test_record_attempt_appends(workspace: Path, pack: Pack) -> None:
    run(workspace, "record-attempt", "--exercise", "4.5", "--verdict", "incorrect")
    run(workspace, "record-attempt", "--exercise", "4.5", "--verdict", "correct")
    assert len(pack.attempts_file.read_text().splitlines()) == 2
    assert store.get_exercise(pack, 4, "4.5")["attempts"] == 2


def test_record_attempt_with_status(workspace: Path, pack: Pack) -> None:
    assert run(
        workspace, "record-attempt", "--exercise", "4.5",
        "--verdict", "correct", "--status", "proved",
    ) == 0
    record = store.get_exercise(pack, 4, "4.5")
    assert record["status"] == "proved"
    assert record["next_review"] == date(2026, 7, 7)


def test_stuck_here_rejects_verdict(workspace: Path, capsys) -> None:
    assert run(
        workspace, "record-attempt", "--exercise", "4.5",
        "--kind", "stuck-here", "--verdict", "correct",
    ) == 1
    assert "not graded" in capsys.readouterr().err


def test_code_exercise_requires_chapter(workspace: Path, capsys) -> None:
    assert run(workspace, "record-attempt", "--exercise", "code:thing") == 1
    assert "--chapter" in capsys.readouterr().err
    assert run(workspace, "record-attempt", "--exercise", "code:thing", "--chapter", "4") == 0


def test_update_status_and_due(workspace: Path, pack: Pack, capsys) -> None:
    run(workspace, "update-status", "--exercise", "6.5", "--status", "proved",
        "--patterns", "coset-counting", "--note", "clean")
    capsys.readouterr()
    assert main(["--root", str(workspace), "--date", "2026-07-07", "due"]) == 0
    out = capsys.readouterr().out
    assert "6.5" in out
    assert "pattern coset-counting" in out

    # not due yet today
    assert main(["--root", str(workspace), "--date", TODAY, "due"]) == 0
    assert "nothing due" in capsys.readouterr().out


def test_views_written(workspace: Path, pack: Pack) -> None:
    run(workspace, "record-attempt", "--exercise", "6.5", "--verdict", "correct",
        "--status", "proved", "--patterns", "coset-counting")
    # render on the day the review falls due so the views list it
    due_day = ["--root", str(workspace), "--date", "2026-07-07"]
    assert main([*due_day, "build-queue"]) == 0
    assert main([*due_day, "render-dashboard"]) == 0
    queue = pack.queue_file.read_text()
    assert "GENERATED" in queue and "test-pack" in queue
    assert "coset-counting" in queue and "6.5" in queue
    dashboard = pack.dashboard_file.read_text()
    assert "GENERATED" in dashboard and "6.5" in dashboard
    assert "Recent attempts" in dashboard
