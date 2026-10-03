"""Tests for `sv list --category` (M1 / issue #5)."""

from __future__ import annotations

from pathlib import Path

import pytest

from cli.sv import main


def _seed_skills(root: Path) -> None:
    for category, name in (
        ("meta", "hello-a"),
        ("inbox", "pending-b"),
        ("deliver", "prd-c"),
    ):
        skill = root / "vault" / "own" / category / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Test skill {name}.\n"
            f"metadata:\n  category: {category}\n---\n\n# {name}\n",
            encoding="utf-8",
        )


@pytest.fixture()
def vault_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    import cli.common as common

    _seed_skills(tmp_path)
    monkeypatch.setattr(common, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(common, "VAULT_OWN", tmp_path / "vault" / "own")
    monkeypatch.setattr(common, "VAULT_IMPORTED", tmp_path / "vault" / "imported")
    return tmp_path


def test_list_all(vault_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["list"]) == 0
    out = capsys.readouterr().out
    assert "hello-a" in out
    assert "pending-b" in out
    assert "prd-c" in out


def test_list_category_meta(
    vault_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["list", "--category", "meta"]) == 0
    out = capsys.readouterr().out
    assert "hello-a" in out
    assert "pending-b" not in out
    assert "prd-c" not in out


def test_list_category_empty(
    vault_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["list", "--category", "ops"]) == 0
    out = capsys.readouterr().out
    assert "No skills matching category 'ops'" in out


def test_list_invalid_category(vault_root: Path) -> None:
    assert main(["list", "--category", "Bad Category"]) == 1
