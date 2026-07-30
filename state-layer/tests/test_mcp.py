from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

from tooter_state import store
from tooter_state.mcp import TOOLS, handle_request
from tooter_state.workspace import Pack

TODAY = "2026-07-06"


def rpc(workspace: Path, method: str, params: dict | None = None, request_id: int = 1) -> dict:
    response = handle_request(workspace, {
        "jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {},
    })
    assert response is not None
    return response


def call(workspace: Path, name: str, arguments: dict) -> dict:
    response = rpc(workspace, "tools/call", {"name": name, "arguments": arguments})
    result = response["result"]
    assert not result.get("isError"), result
    return json.loads(result["content"][0]["text"])


def test_initialize_and_tools_list(workspace: Path) -> None:
    init = rpc(workspace, "initialize", {"protocolVersion": "2024-11-05"})
    assert init["result"]["protocolVersion"] == "2024-11-05"
    assert init["result"]["serverInfo"]["name"] == "tooter-state"
    listed = rpc(workspace, "tools/list")
    names = [tool["name"] for tool in listed["result"]["tools"]]
    assert names == ["get_progress", "get_due_reviews", "get_exercise",
                     "record_attempt", "update_status", "log_misconception"]
    assert names == [tool["name"] for tool in TOOLS]


def test_notifications_get_no_response(workspace: Path) -> None:
    assert handle_request(workspace, {"jsonrpc": "2.0",
                                      "method": "notifications/initialized"}) is None


def test_unknown_method_errors(workspace: Path) -> None:
    response = rpc(workspace, "resources/list")
    assert response["error"]["code"] == -32601


def test_record_attempt_and_get_exercise(workspace: Path, pack: Pack) -> None:
    result = call(workspace, "record_attempt", {
        "exercise": "4.5", "verdict": "mostly-correct", "hint_depth": 2,
        "images": ["attempts/2026/p1.png"], "summary": "well-definedness gap",
        "patterns": ["cyclic-subgroups"], "date": TODAY,
    })
    assert result["messages"] == ["recorded attempt #1 for 4.5 (verdict: mostly-correct)"]
    assert result["record"]["status"] == "attempted"

    entry = json.loads(pack.attempts_file.read_text().splitlines()[0])
    assert entry["image_paths"] == ["attempts/2026/p1.png"]
    assert entry["ts"].startswith(TODAY)

    fetched = call(workspace, "get_exercise", {"exercise": "4.5"})
    assert fetched["chapter"] == 4
    assert fetched["attempts"] == 1
    assert fetched["patterns"] == ["cyclic-subgroups"]


def test_record_stuck_here_defaults_hint_depth(workspace: Path, pack: Pack) -> None:
    call(workspace, "record_attempt",
         {"exercise": "4.7", "kind": "stuck-here", "date": TODAY})
    entry = json.loads(pack.attempts_file.read_text().splitlines()[0])
    assert entry["kind"] == "stuck-here"
    assert entry["hint_depth"] == 1
    assert entry["verdict"] is None


def test_stuck_here_with_verdict_is_error(workspace: Path) -> None:
    response = rpc(workspace, "tools/call", {"name": "record_attempt", "arguments": {
        "exercise": "4.7", "kind": "stuck-here", "verdict": "correct", "date": TODAY,
    }})
    assert response["result"]["isError"] is True
    assert "stuck-here" in response["result"]["content"][0]["text"]


def test_update_status_and_due_reviews(workspace: Path, pack: Pack) -> None:
    result = call(workspace, "update_status", {
        "exercise": "4.5", "status": "proved",
        "patterns": ["cyclic-subgroups"], "date": TODAY,
    })
    assert result["record"]["status"] == "proved"
    assert store.get_exercise(pack, 4, "4.5")["next_review"] == date(2026, 7, 7)

    due = call(workspace, "get_due_reviews", {"date": "2026-07-07"})
    assert due["patterns"] == {"cyclic-subgroups": ["4.5"]}
    assert due["exercises"][0]["exercise"] == "4.5"
    assert call(workspace, "get_due_reviews", {"date": TODAY})["exercises"] == []


def test_get_progress_includes_boundary_view(workspace: Path, pack: Pack) -> None:
    pack.progress_file.write_text("# Chapter Progress\n", encoding="utf-8")
    store.save_chapters(pack, {"chapters": [
        {"ch": 4, "topic": "Cyclic Groups", "mode": "full", "status": "exercises"},
    ]})
    call(workspace, "record_attempt", {"exercise": "4.5", "date": TODAY})
    progress = call(workspace, "get_progress", {})
    assert progress["pack"] == "test-pack"
    assert progress["chapters"][0]["topic"] == "Cyclic Groups"
    assert progress["exercise_status_counts"] == {"attempted": 1}
    assert progress["progress_md"].startswith("# Chapter Progress")


def test_log_misconception_replaces_placeholder(workspace: Path, pack: Pack) -> None:
    pack.misconceptions_file.parent.mkdir(parents=True, exist_ok=True)
    pack.misconceptions_file.write_text(
        "# Misconception Ledger\n\n(none yet)\n", encoding="utf-8",
    )
    result = call(workspace, "log_misconception", {
        "text": "conflates order of an element with order of the group",
        "topic": "order-arguments", "evidence": ["2026-07-06T00:00:00"],
    })
    text = pack.misconceptions_file.read_text()
    assert "(none yet)" not in text
    assert result["logged"] in text
    assert text.rstrip().endswith(
        "- [order-arguments] conflates order of an element with order of the group "
        "(evidence: 2026-07-06T00:00:00)"
    )
    progress = call(workspace, "get_progress", {})
    assert len(progress["misconceptions"]) == 1


def test_stdio_round_trip(workspace: Path) -> None:
    requests = "\n".join(json.dumps(r) for r in [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2025-06-18"}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": "record_attempt",
                    "arguments": {"exercise": "4.5", "date": TODAY}}},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "get_exercise", "arguments": {"exercise": "4.5"}}},
    ]) + "\n"
    proc = subprocess.run(
        [sys.executable, "-m", "tooter_state.mcp", "--root", str(workspace)],
        input=requests, capture_output=True, text=True, timeout=30, check=True,
    )
    responses = [json.loads(line) for line in proc.stdout.splitlines()]
    assert [r["id"] for r in responses] == [1, 2, 3]
    assert responses[0]["result"]["protocolVersion"] == "2025-06-18"
    fetched = json.loads(responses[2]["result"]["content"][0]["text"])
    assert fetched["attempts"] == 1
