from __future__ import annotations

from pathlib import Path

import pytest

from tooter_state.workspace import WorkspaceError, active_pack, find_root


def test_find_root_walks_up(workspace: Path) -> None:
    nested = workspace / "studies" / "test-pack" / "state"
    assert find_root(nested) == workspace


def test_find_root_env_override(workspace: Path, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("TOOTER_STUDIES_ROOT", str(workspace))
    assert find_root(tmp_path) == workspace


def test_find_root_missing(tmp_path: Path) -> None:
    with pytest.raises(WorkspaceError):
        find_root(tmp_path)


def test_active_pack(workspace: Path) -> None:
    pack = active_pack(workspace)
    assert pack.name == "test-pack"
    assert pack.state_dir == workspace / "studies" / "test-pack" / "state"


def test_active_pack_unparseable(workspace: Path) -> None:
    (workspace / "studies" / "active.md").write_text("nothing here", encoding="utf-8")
    with pytest.raises(WorkspaceError):
        active_pack(workspace)
