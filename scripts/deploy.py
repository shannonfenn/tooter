#!/usr/bin/env python3
"""Compile tutor-core sources into the study workspace (one-way deploy).

Usage:
    python3 scripts/deploy.py             deploy: copy manifest, prune strays
    python3 scripts/deploy.py --check     report drift only; exit 1 if any
    python3 scripts/deploy.py --target P  deploy to a non-default studies repo

The compiler is deliberately dumb: byte-for-byte copies driven by a manifest.
No templating, no generation — the drift check is plain file equality.
Run --check on a weekly schedule, never at study-session start.

opencode's own runtime scaffolding inside .opencode/ (node_modules,
package.json, package-lock.json, bun.lock, .gitignore) is never touched.
"""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import sys
from pathlib import Path

WORKBENCH = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = Path.home() / "dev/oth/github/tooter-studies"

# Directory trees copied recursively: (workbench-relative, target-relative).
TREES = [
    ("tutor/agents", ".opencode/agents"),
    ("tutor/commands", ".opencode/commands"),
    ("tutor/instructions", ".opencode/instructions"),
    ("tutor/skills", ".opencode/skills"),
]

# Single files: (workbench-relative, target-relative).
FILES = [
    ("tutor/opencode.jsonc", "opencode.jsonc"),
    ("tutor/deployed-readme.md", ".opencode/README.md"),
    ("docs/pedagogy-for-tutoring.md", ".opencode/reference/pedagogy-for-tutoring.md"),
]

# Target-relative directories fully owned by the deploy: stray files inside
# them are pruned (deploy) or reported (--check).
MANAGED_DIRS = [dst for _, dst in TREES] + [".opencode/reference"]


def build_manifest(target: Path) -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    for src_rel, dst_rel in TREES:
        src_root = WORKBENCH / src_rel
        if not src_root.is_dir():
            sys.exit(f"deploy: missing source directory {src_root}")
        for path in sorted(src_root.rglob("*")):
            if path.is_file():
                pairs.append((path, target / dst_rel / path.relative_to(src_root)))
    for src_rel, dst_rel in FILES:
        src = WORKBENCH / src_rel
        if not src.is_file():
            sys.exit(f"deploy: missing source file {src}")
        pairs.append((src, target / dst_rel))
    return pairs


def find_strays(target: Path, dests: set[Path]) -> list[Path]:
    strays: list[Path] = []
    for dir_rel in MANAGED_DIRS:
        root = target / dir_rel
        if not root.is_dir():
            continue
        strays.extend(
            p for p in sorted(root.rglob("*")) if p.is_file() and p not in dests
        )
    return strays


def prune_empty_dirs(target: Path) -> None:
    for dir_rel in MANAGED_DIRS:
        root = target / dir_rel
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*"), reverse=True):
            if path.is_dir() and not any(path.iterdir()):
                path.rmdir()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="report drift, change nothing")
    parser.add_argument(
        "--target",
        type=Path,
        default=Path(os.environ.get("TOOTER_STUDIES", DEFAULT_TARGET)),
        help=f"studies repo to deploy into (default: {DEFAULT_TARGET})",
    )
    args = parser.parse_args()

    target = args.target.expanduser().resolve()
    if not (target / ".git").exists():
        sys.exit(f"deploy: {target} is not a git repo — is the studies workspace checked out?")

    pairs = build_manifest(target)
    dests = {dst for _, dst in pairs}

    missing = [dst for src, dst in pairs if not dst.exists()]
    changed = [
        dst for src, dst in pairs if dst.exists() and not filecmp.cmp(src, dst, shallow=False)
    ]
    strays = find_strays(target, dests)

    if args.check:
        for dst in missing:
            print(f"missing  {dst.relative_to(target)}")
        for dst in changed:
            print(f"drifted  {dst.relative_to(target)}")
        for dst in strays:
            print(f"stray    {dst.relative_to(target)}")
        if missing or changed or strays:
            print(f"deploy --check: DRIFT ({len(missing)} missing, "
                  f"{len(changed)} drifted, {len(strays)} stray) — run `just deploy`")
            return 1
        print(f"deploy --check: clean ({len(pairs)} files match {target})")
        return 0

    for src, dst in pairs:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    for stray in strays:
        stray.unlink()
        print(f"pruned   {stray.relative_to(target)}")
    prune_empty_dirs(target)
    print(f"deployed {len(pairs)} files to {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
