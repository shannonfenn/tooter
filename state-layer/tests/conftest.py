from __future__ import annotations

from pathlib import Path

import pytest

from tooter_state.workspace import Pack


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    root = tmp_path / "studies-repo"
    (root / "studies" / "test-pack" / "state").mkdir(parents=True)
    (root / "studies" / "active.md").write_text(
        "# Active Study Pack\n\nDefault study pack: `studies/test-pack/`\n",
        encoding="utf-8",
    )
    return root


@pytest.fixture
def pack(workspace: Path) -> Pack:
    return Pack(root=workspace, path=workspace / "studies" / "test-pack")
