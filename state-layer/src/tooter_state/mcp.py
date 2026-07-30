"""MCP face of the state layer: a stdio server over the same ops as the CLI.

Speaks Model Context Protocol JSON-RPC (newline-delimited) on stdin/stdout,
exposing exactly the redesign-plan.md §3.3 tool set: ``get_progress``,
``get_due_reviews``, ``get_exercise``, ``record_attempt``, ``update_status``,
``log_misconception``. No SDK dependency — the needed protocol subset
(initialize / tools/list / tools/call / ping) is tiny and stable.

The workspace is resolved per call (``--root``, else $TOOTER_STUDIES_ROOT,
else walk up from cwd), so an active-pack switch takes effect live.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

from . import __version__, ops, store
from .workspace import WorkspaceError, active_pack, find_root

PROTOCOL_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")

_EXERCISE = {"type": "string", "description": "Exercise id, e.g. 4.5 or code:slug"}
_CHAPTER = {"type": "integer", "description": "Chapter number when not inferable from the id"}
_DATE = {"type": "string", "description": "Override today (YYYY-MM-DD); backfills only"}
_PATTERNS = {"type": "array", "items": {"type": "string"},
             "description": "Proof-pattern tags to merge"}

TOOLS: list[dict[str, Any]] = [
    {
        "name": "get_progress",
        "description": "Chapter-level study state, exercise status counts, live "
                       "misconceptions, and the covered-work boundary view (progress.md).",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_due_reviews",
        "description": "Exercises and proof patterns due for review. Reviews are freshly "
                       "generated retrieval/transfer prompts against the due pattern — "
                       "never a re-read of prior work.",
        "inputSchema": {"type": "object", "properties": {
            "days": {"type": "integer", "description": "Horizon in days (default: due today)"},
            "date": _DATE,
        }},
    },
    {
        "name": "get_exercise",
        "description": "One exercise record (status, patterns, attempts, next review).",
        "inputSchema": {"type": "object", "properties": {
            "exercise": _EXERCISE, "chapter": _CHAPTER,
        }, "required": ["exercise"]},
    },
    {
        "name": "record_attempt",
        "description": "Append to the attempt ledger and bump the exercise record. "
                       "kind 'stuck-here' is ungraded (no verdict).",
        "inputSchema": {"type": "object", "properties": {
            "exercise": _EXERCISE, "chapter": _CHAPTER,
            "kind": {"type": "string", "enum": list(store.ATTEMPT_KINDS)},
            "verdict": {"type": "string", "enum": list(store.VERDICTS)},
            "hint_depth": {"type": "integer",
                           "description": "Deepest hint-ladder rung used"},
            "images": {"type": "array", "items": {"type": "string"},
                       "description": "Archived page-scan paths"},
            "summary": {"type": "string", "description": "One-line tutor summary"},
            "patterns": _PATTERNS,
            "status": {"type": "string", "enum": list(store.STATUSES),
                       "description": "Also update the exercise status"},
            "no_propagate": {"type": "boolean",
                             "description": "Skip FIRe-lite pushback of sibling reviews"},
            "date": _DATE,
        }, "required": ["exercise"]},
    },
    {
        "name": "update_status",
        "description": "Set an exercise status and reschedule its review. Statuses record "
                       "what happened (proved, re-derived, transfers-ok) — there is "
                       "deliberately no 'mastered'.",
        "inputSchema": {"type": "object", "properties": {
            "exercise": _EXERCISE, "chapter": _CHAPTER,
            "status": {"type": "string", "enum": list(store.STATUSES)},
            "note": {"type": "string", "description": "Replace the record's short note"},
            "patterns": _PATTERNS,
            "no_propagate": {"type": "boolean"},
            "date": _DATE,
        }, "required": ["exercise", "status"]},
    },
    {
        "name": "log_misconception",
        "description": "Append one live-misconception bullet to state/misconceptions.md, "
                       "with evidence timestamps from the attempt ledger.",
        "inputSchema": {"type": "object", "properties": {
            "text": {"type": "string", "description": "The misconception, stated plainly"},
            "topic": {"type": "string", "description": "Pattern or topic tag"},
            "evidence": {"type": "array", "items": {"type": "string"},
                         "description": "attempts.jsonl timestamps"},
        }, "required": ["text"]},
    },
]


def _today(arguments: dict[str, Any]) -> date:
    raw = arguments.get("date")
    return date.fromisoformat(raw) if raw else date.today()


def call_tool(root: Path | None, name: str, arguments: dict[str, Any]) -> Any:
    pack = active_pack(find_root(root))
    if name == "get_progress":
        return ops.get_progress(pack)
    if name == "get_due_reviews":
        return ops.due_reviews(pack, _today(arguments),
                               horizon_days=int(arguments.get("days") or 0))
    if name == "get_exercise":
        return ops.get_exercise(pack, arguments["exercise"], arguments.get("chapter"))
    if name == "record_attempt":
        record, messages = ops.record_attempt(
            pack,
            exercise=arguments["exercise"],
            chapter=arguments.get("chapter"),
            kind=arguments.get("kind", "attempt"),
            verdict=arguments.get("verdict"),
            hint_depth=arguments.get("hint_depth"),
            images=arguments.get("images"),
            summary=arguments.get("summary"),
            patterns=arguments.get("patterns"),
            status=arguments.get("status"),
            propagate=not arguments.get("no_propagate", False),
            today=_today(arguments),
            explicit_date="date" in arguments,
        )
        return {"record": record, "messages": messages}
    if name == "update_status":
        record, messages = ops.update_status(
            pack,
            exercise=arguments["exercise"],
            status=arguments["status"],
            chapter=arguments.get("chapter"),
            note=arguments.get("note"),
            patterns=arguments.get("patterns"),
            propagate=not arguments.get("no_propagate", False),
            today=_today(arguments),
        )
        return {"record": record, "messages": messages}
    if name == "log_misconception":
        return {"logged": ops.log_misconception(
            pack, text=arguments["text"], topic=arguments.get("topic"),
            evidence=arguments.get("evidence"),
        )}
    raise store.StateError(f"unknown tool {name!r}")


def handle_request(root: Path | None, request: dict[str, Any]) -> dict[str, Any] | None:
    """Return a JSON-RPC response, or None for notifications."""
    request_id, method = request.get("id"), request.get("method", "")
    params = request.get("params") or {}

    def respond(result: Any) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    if method == "initialize":
        requested = params.get("protocolVersion")
        return respond({
            "protocolVersion": requested if requested in PROTOCOL_VERSIONS
            else PROTOCOL_VERSIONS[0],
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "tooter-state", "version": __version__},
        })
    if method.startswith("notifications/"):
        return None
    if method == "ping":
        return respond({})
    if method == "tools/list":
        return respond({"tools": TOOLS})
    if method == "tools/call":
        try:
            result = call_tool(root, params.get("name", ""), params.get("arguments") or {})
        except (store.StateError, WorkspaceError, KeyError, ValueError) as error:
            return respond({"content": [{"type": "text", "text": f"{error}"}],
                            "isError": True})
        return respond({"content": [{"type": "text",
                                     "text": json.dumps(result, default=str,
                                                        ensure_ascii=False)}]})
    if request_id is None:
        return None
    return {"jsonrpc": "2.0", "id": request_id,
            "error": {"code": -32601, "message": f"method not found: {method}"}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tooter-state-mcp", description=__doc__)
    parser.add_argument("--root", help="study workspace root (default: walk up from cwd, "
                                       "or $TOOTER_STUDIES_ROOT)")
    args = parser.parse_args(argv)
    root = Path(args.root).expanduser() if args.root else None
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            response: dict[str, Any] | None = {
                "jsonrpc": "2.0", "id": None,
                "error": {"code": -32700, "message": "parse error"},
            }
        else:
            response = handle_request(root, request)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
