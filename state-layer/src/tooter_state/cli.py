"""CLI face of the state layer.

Subcommands (redesign-plan.md §3.3):
``record-attempt | update-status | due | build-queue | render-dashboard``.
The Phase-1 MCP face exposes the same functions over stdio.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from . import scheduling, store, views
from .workspace import Pack, WorkspaceError, active_pack, find_root


def _resolve_pack(args: argparse.Namespace) -> Pack:
    root = find_root(Path(args.root).expanduser() if args.root else None)
    return active_pack(root)


def _today(args: argparse.Namespace) -> date:
    return date.fromisoformat(args.date) if args.date else date.today()


def _chapter_for(args: argparse.Namespace, exercise_id: str) -> int:
    if args.chapter:
        return args.chapter
    chapter = store.chapter_of(exercise_id)
    if chapter is None:
        raise store.StateError(
            f"cannot infer a chapter from {exercise_id!r}; pass --chapter N"
        )
    return chapter


def _split_patterns(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def cmd_record_attempt(args: argparse.Namespace) -> int:
    pack = _resolve_pack(args)
    today = _today(args)
    chapter = _chapter_for(args, args.exercise)
    hint_depth = args.hint_depth
    if args.kind == "stuck-here" and hint_depth is None:
        hint_depth = 1  # smallest useful hint is the stuck-here contract
    store.append_attempt(
        pack,
        ts=store.now_iso(today if args.date else None),
        exercise=args.exercise,
        kind=args.kind,
        verdict=args.verdict,
        hint_depth=hint_depth,
        image_paths=args.image or [],
        tutor_summary=args.summary,
    )
    record = store.get_exercise(pack, chapter, args.exercise)
    if record is None:
        record = store.new_record("code" if args.exercise.startswith("code:") else "text")
    record["attempts"] += 1
    record["last_attempt"] = today
    if record["status"] == "unseen":
        record["status"] = "attempted"
    if args.patterns:
        merged = _split_patterns(args.patterns)
        record["patterns"] += [p for p in merged if p not in record["patterns"]]
    store.upsert_exercise(pack, chapter, args.exercise, record)
    graded = f" (verdict: {args.verdict})" if args.verdict else ""
    print(f"recorded {args.kind} #{record['attempts']} for {args.exercise}{graded}")
    if args.status:
        _, messages = scheduling.set_status(
            pack, chapter, args.exercise, args.status, today,
            propagate=not args.no_propagate,
        )
        for message in messages:
            print(message)
    return 0


def cmd_update_status(args: argparse.Namespace) -> int:
    pack = _resolve_pack(args)
    chapter = _chapter_for(args, args.exercise)
    _, messages = scheduling.set_status(
        pack, chapter, args.exercise, args.status, _today(args),
        note=args.note, patterns=_split_patterns(args.patterns),
        propagate=not args.no_propagate,
    )
    for message in messages:
        print(message)
    return 0


def cmd_due(args: argparse.Namespace) -> int:
    pack = _resolve_pack(args)
    today = _today(args)
    items = views.due_items(pack, today, horizon_days=args.days)
    if not items:
        horizon = f" within {args.days} days" if args.days else ""
        print(f"nothing due{horizon}")
        return 0
    for pattern, pattern_items in views.due_patterns(items).items():
        via = ", ".join(i.exercise_id for i in pattern_items)
        print(f"pattern {pattern}  (via {via})")
    for item in items:
        record = item.record
        patterns = ",".join(record["patterns"]) or "untagged"
        print(f"due {item.next_review.isoformat()}  {item.exercise_id}  "
              f"ch{item.chapter:02d}  {record['status']}  {patterns}")
    return 0


def cmd_build_queue(args: argparse.Namespace) -> int:
    pack = _resolve_pack(args)
    views.build_queue(pack, _today(args))
    print(f"wrote {pack.queue_file.relative_to(pack.root)}")
    return 0


def cmd_render_dashboard(args: argparse.Namespace) -> int:
    pack = _resolve_pack(args)
    views.render_dashboard(pack, _today(args))
    print(f"wrote {pack.dashboard_file.relative_to(pack.root)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tooter-state",
        description="Structured learner state for tooter study workspaces.",
    )
    parser.add_argument("--root", help="study workspace root (default: walk up from cwd, "
                                       "or $TOOTER_STUDIES_ROOT)")
    parser.add_argument("--date", help="override today (YYYY-MM-DD); for backfills and tests")
    sub = parser.add_subparsers(dest="command", required=True)

    record = sub.add_parser("record-attempt",
                            help="append to the attempt ledger and bump the exercise record")
    record.add_argument("--exercise", required=True, help="exercise id, e.g. 4.5 or code:slug")
    record.add_argument("--chapter", type=int, help="chapter number when not inferable from id")
    record.add_argument("--kind", choices=store.ATTEMPT_KINDS, default="attempt")
    record.add_argument("--verdict", choices=store.VERDICTS,
                        help="assessment verdict (attempt only; stuck-here is ungraded)")
    record.add_argument("--hint-depth", type=int, help="deepest hint-ladder rung used")
    record.add_argument("--image", action="append",
                        help="path to an archived page scan; repeatable")
    record.add_argument("--summary", help="one-line tutor summary for the ledger")
    record.add_argument("--patterns", help="comma-separated proof-pattern tags to merge")
    record.add_argument("--status", choices=store.STATUSES,
                        help="also update the exercise status (as update-status)")
    record.add_argument("--no-propagate", action="store_true",
                        help="skip FIRe-lite pushback of sibling reviews")
    record.set_defaults(func=cmd_record_attempt)

    update = sub.add_parser("update-status", help="set an exercise status and reschedule")
    update.add_argument("--exercise", required=True)
    update.add_argument("--chapter", type=int)
    update.add_argument("--status", required=True, choices=store.STATUSES)
    update.add_argument("--note", help="replace the record's short note")
    update.add_argument("--patterns", help="comma-separated proof-pattern tags to merge")
    update.add_argument("--no-propagate", action="store_true",
                        help="skip FIRe-lite pushback of sibling reviews")
    update.set_defaults(func=cmd_update_status)

    due = sub.add_parser("due", help="list exercises and patterns due for review")
    due.add_argument("--days", type=int, default=0, help="horizon in days (default: today)")
    due.set_defaults(func=cmd_due)

    queue = sub.add_parser("build-queue", help="regenerate state/queue.md")
    queue.set_defaults(func=cmd_build_queue)

    dashboard = sub.add_parser("render-dashboard", help="regenerate state/dashboard.html")
    dashboard.set_defaults(func=cmd_render_dashboard)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (store.StateError, WorkspaceError, ValueError) as error:
        print(f"tooter-state: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
