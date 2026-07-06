"""Derived views: due listing, state/queue.md, state/dashboard.html.

Both files are disposable — regenerated wholesale, never edited. Reviews are
freshly generated retrieval/transfer prompts against the due pattern, never a
re-read of prior work, so the queue leads with *patterns*, not artifacts.
"""

from __future__ import annotations

import html
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from . import store
from .workspace import Pack


@dataclass(frozen=True)
class DueItem:
    chapter: int
    exercise_id: str
    record: dict[str, Any]

    @property
    def next_review(self) -> date:
        return self.record["next_review"]


def scheduled_items(pack: Pack) -> list[DueItem]:
    items = [
        DueItem(chapter, exercise_id, record)
        for chapter, exercise_id, record in store.iter_exercises(pack)
        if record["next_review"] is not None
    ]
    return sorted(items, key=lambda item: (item.next_review, item.chapter, item.exercise_id))


def due_items(pack: Pack, today: date, horizon_days: int = 0) -> list[DueItem]:
    cutoff = today + timedelta(days=horizon_days)
    return [item for item in scheduled_items(pack) if item.next_review <= cutoff]


def due_patterns(items: list[DueItem]) -> dict[str, list[DueItem]]:
    patterns: dict[str, list[DueItem]] = {}
    for item in items:
        for pattern in item.record["patterns"] or ["(untagged)"]:
            patterns.setdefault(pattern, []).append(item)
    return dict(sorted(patterns.items()))


def working_set(pack: Pack) -> list[DueItem]:
    return [
        DueItem(chapter, exercise_id, record)
        for chapter, exercise_id, record in store.iter_exercises(pack)
        if record["status"] in ("attempted", "needs-review")
    ]


def misconception_bullets(pack: Pack) -> list[str]:
    if not pack.misconceptions_file.is_file():
        return []
    lines = pack.misconceptions_file.read_text(encoding="utf-8").splitlines()
    return [line[2:].strip() for line in lines if line.startswith("- ")]


def _item_line(item: DueItem, today: date) -> str:
    record = item.record
    when = item.next_review.isoformat()
    overdue = " (overdue)" if item.next_review < today else ""
    patterns = ", ".join(record["patterns"]) or "untagged"
    return (f"- `{item.exercise_id}` (ch {item.chapter}, {record['status']}, "
            f"due {when}{overdue}) — patterns: {patterns}")


def build_queue(pack: Pack, today: date) -> str:
    due_now = due_items(pack, today)
    upcoming = [i for i in due_items(pack, today, horizon_days=7) if i not in due_now]
    working = working_set(pack)
    tracked = sum(1 for _ in store.iter_exercises(pack))

    lines = [
        f"<!-- GENERATED {today.isoformat()} by `tooter-state build-queue`. "
        "Derived view - do not edit. -->",
        "",
        f"# Review Queue — {pack.name}",
        "",
        f"## Due now ({len(due_now)})",
        "",
    ]
    if due_now:
        lines.append("Patterns due — generate a fresh retrieval or transfer prompt per "
                     "pattern; never re-read prior work:")
        lines.append("")
        for pattern, items in due_patterns(due_now).items():
            via = ", ".join(f"`{i.exercise_id}`" for i in items)
            lines.append(f"- **{pattern}** — via {via}")
        lines.append("")
        lines.append("Exercises:")
        lines.append("")
        lines.extend(_item_line(item, today) for item in due_now)
    else:
        lines.append("Nothing due. Study forward.")
    lines += ["", f"## Due within 7 days ({len(upcoming)})", ""]
    if upcoming:
        lines.extend(_item_line(item, today) for item in upcoming)
    else:
        lines.append("None scheduled.")
    lines += ["", f"## Working set ({len(working)})", ""]
    if working:
        for item in sorted(working, key=lambda i: (i.chapter, i.exercise_id)):
            note = item.record["note"] or ""
            suffix = f" — {note}" if note else ""
            lines.append(f"- `{item.exercise_id}` (ch {item.chapter}, "
                         f"{item.record['status']}){suffix}")
    else:
        lines.append("Empty.")
    misconceptions = misconception_bullets(pack)
    lines += ["", f"_Tracked: {tracked} exercises · live misconceptions: "
                  f"{len(misconceptions)}._", ""]
    text = "\n".join(lines)
    pack.queue_file.parent.mkdir(parents=True, exist_ok=True)
    pack.queue_file.write_text(text, encoding="utf-8")
    return text


_DASH_CSS = """
body { font: 15px/1.5 -apple-system, sans-serif; margin: 2rem auto; max-width: 60rem;
       padding: 0 1rem; color: #1a1a1a; }
h1 { font-size: 1.4rem; } h2 { font-size: 1.1rem; margin-top: 2rem; }
table { border-collapse: collapse; width: 100%; }
th, td { text-align: left; padding: .3rem .6rem; border-bottom: 1px solid #ddd; }
th { border-bottom: 2px solid #999; }
.muted { color: #777; } .due { color: #b30000; font-weight: 600; }
code { background: #f4f4f4; padding: .05rem .3rem; border-radius: 3px; }
""".strip()


def render_dashboard(pack: Pack, today: date) -> str:
    chapters = store.load_chapters(pack)["chapters"]
    exercises = list(store.iter_exercises(pack))
    due_now = due_items(pack, today)
    attempts = store.read_attempts(pack)
    misconceptions = misconception_bullets(pack)

    status_counts: dict[str, int] = {}
    per_chapter: dict[int, list[dict[str, Any]]] = {}
    for chapter, _exercise_id, record in exercises:
        status_counts[record["status"]] = status_counts.get(record["status"], 0) + 1
        per_chapter.setdefault(chapter, []).append(record)

    def esc(value: Any) -> str:
        return html.escape(str(value))

    rows = []
    for chapter in chapters:
        ch = chapter.get("ch")
        recs = per_chapter.get(ch, [])
        due_ch = sum(1 for item in due_now if item.chapter == ch)
        due_cell = (f'<span class="due">{due_ch}</span>' if due_ch
                    else '<span class="muted">0</span>')
        rows.append(
            f"<tr><td>{esc(ch)}</td><td>{esc(chapter.get('topic', ''))}</td>"
            f"<td>{esc(chapter.get('mode', ''))}</td><td>{esc(chapter.get('status', ''))}</td>"
            f"<td>{len(recs)}</td><td>{due_cell}</td></tr>"
        )

    counts = " · ".join(f"{name}: {count}" for name, count in sorted(status_counts.items())) \
        or "none tracked yet"
    due_list = "".join(
        f"<li><code>{esc(item.exercise_id)}</code> ch {item.chapter} — "
        f"{esc(item.record['status'])}, due {item.next_review.isoformat()}, patterns: "
        f"{esc(', '.join(item.record['patterns']) or 'untagged')}</li>"
        for item in due_now
    ) or "<li class='muted'>nothing due</li>"
    recent = "".join(
        f"<li><code>{esc(a['exercise'])}</code> {esc(a['kind'])}"
        f"{' — ' + esc(a['verdict']) if a.get('verdict') else ''}"
        f" <span class='muted'>{esc(a['ts'])}</span></li>"
        for a in attempts[-10:][::-1]
    ) or "<li class='muted'>no attempts recorded</li>"
    misconception_list = "".join(f"<li>{esc(b)}</li>" for b in misconceptions) \
        or "<li class='muted'>none live</li>"

    text = f"""<!doctype html>
<!-- GENERATED {today.isoformat()} by `tooter-state render-dashboard`. Do not edit. -->
<meta charset="utf-8">
<title>{esc(pack.name)} — study dashboard</title>
<style>{_DASH_CSS}</style>
<h1>{esc(pack.name)} — {today.isoformat()}</h1>
<p>Exercise statuses: {esc(counts)}.</p>
<h2>Due now ({len(due_now)})</h2>
<ul>{due_list}</ul>
<h2>Chapters</h2>
<table>
<tr><th>Ch</th><th>Topic</th><th>Mode</th><th>Status</th><th>Tracked</th><th>Due</th></tr>
{''.join(rows)}
</table>
<h2>Live misconceptions ({len(misconceptions)})</h2>
<ul>{misconception_list}</ul>
<h2>Recent attempts</h2>
<ul>{recent}</ul>
"""
    pack.dashboard_file.parent.mkdir(parents=True, exist_ok=True)
    pack.dashboard_file.write_text(text, encoding="utf-8")
    return text
