#!/usr/bin/env python3
"""Seed the structured state layer from the v0 hand-edited tables.

One-shot migration (redesign-plan.md Phase 0). Run from the workbench:

    uv run --directory state-layer python scripts/seed_state.py \
        --root ~/dev/src/github/tooter-studies
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from tooter_state import seed as seed_mod
from tooter_state.workspace import WorkspaceError, active_pack, find_root


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", help="study workspace root")
    parser.add_argument("--date", help="override today (YYYY-MM-DD)")
    parser.add_argument("--force", action="store_true", help="reseed over existing chapters.yaml")
    args = parser.parse_args(argv)
    today = date.fromisoformat(args.date) if args.date else date.today()
    try:
        pack = active_pack(find_root(Path(args.root).expanduser() if args.root else None))
        for message in seed_mod.seed(pack, today, force=args.force):
            print(message)
    except (seed_mod.SeedError, WorkspaceError) as error:
        print(f"seed_state: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
