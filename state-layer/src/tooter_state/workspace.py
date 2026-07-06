"""Locate the study workspace root and its active study pack."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

ACTIVE_FILE = Path("studies") / "active.md"
_PACK_RE = re.compile(r"`(studies/[A-Za-z0-9._-]+)/?`")


class WorkspaceError(RuntimeError):
    """The study workspace or active pack could not be resolved."""


def find_root(start: Path | None = None) -> Path:
    """Resolve the workspace root: $TOOTER_STUDIES_ROOT, else walk up from cwd."""
    env = os.environ.get("TOOTER_STUDIES_ROOT")
    if env:
        root = Path(env).expanduser().resolve()
        if not (root / ACTIVE_FILE).is_file():
            raise WorkspaceError(f"TOOTER_STUDIES_ROOT={root} has no {ACTIVE_FILE}")
        return root
    cur = (start or Path.cwd()).resolve()
    for candidate in (cur, *cur.parents):
        if (candidate / ACTIVE_FILE).is_file():
            return candidate
    raise WorkspaceError(
        f"no {ACTIVE_FILE} found walking up from {cur}; "
        "run inside the study workspace or set TOOTER_STUDIES_ROOT"
    )


@dataclass(frozen=True)
class Pack:
    """Paths of one study pack inside a workspace."""

    root: Path
    path: Path

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def state_dir(self) -> Path:
        return self.path / "state"

    @property
    def exercises_dir(self) -> Path:
        return self.state_dir / "exercises"

    @property
    def chapters_file(self) -> Path:
        return self.state_dir / "chapters.yaml"

    @property
    def attempts_file(self) -> Path:
        return self.state_dir / "attempts.jsonl"

    @property
    def misconceptions_file(self) -> Path:
        return self.state_dir / "misconceptions.md"

    @property
    def queue_file(self) -> Path:
        return self.state_dir / "queue.md"

    @property
    def dashboard_file(self) -> Path:
        return self.state_dir / "dashboard.html"

    @property
    def progress_file(self) -> Path:
        return self.state_dir / "progress.md"


def active_pack(root: Path) -> Pack:
    """Parse studies/active.md for the default pack path."""
    text = (root / ACTIVE_FILE).read_text(encoding="utf-8")
    match = _PACK_RE.search(text)
    if not match:
        raise WorkspaceError(f"could not parse an active pack out of {root / ACTIVE_FILE}")
    pack_path = root / match.group(1)
    if not pack_path.is_dir():
        raise WorkspaceError(f"active pack directory {pack_path} does not exist")
    return Pack(root=root, path=pack_path)
