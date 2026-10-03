"""Vault ↔ IDE presence sync tests (M3 / issue #17)."""

from __future__ import annotations

from pathlib import Path

import pytest

from cli.ide_sync import compare_vault_to_ide
from cli.sv import main


def _seed_vault(root: Path, names: list[str]) -> None:
    for name in names:
        skill = root / "vault" / "own" / "meta" / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Test {name}.\n"
            f"metadata:\n  category: meta\n---\n\n# {name}\n",
            encoding="utf-8",
        )


@pytest.fixture()
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    import cli.common as common

    monkeypatch.setattr(common, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(common, "VAULT_OWN", tmp_path / "vault" / "own")
    monkeypatch.setattr(common, "VAULT_IMPORTED", tmp_path / "vault" / "imported")
    return tmp_path


def test_pending_and_orphan_and_sync(env: Path) -> None:
    _seed_vault(env, ["alpha", "beta"])
    home = env / "home"
    skills = home / ".cursor" / "skills"
    skills.mkdir(parents=True)
    (skills / "beta").mkdir()
    (skills / "orphan-x").mkdir()

    report = compare_vault_to_ide(
        ide="cursor", os_name="windows", home_override=home
    )
    assert report.pending_install == ["alpha"]
    assert report.orphan_in_ide == ["orphan-x"]
    assert report.in_sync == ["beta"]


def test_cli_doctor_ide_mode(env: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _seed_vault(env, ["only-vault"])
    home = env / "home"
    (home / ".claude" / "skills").mkdir(parents=True)
    assert (
        main(
            [
                "doctor",
                "--ide",
                "claude-code",
                "--os",
                "linux",
                "--home",
                str(home),
            ]
        )
        == 0
    )
    out = capsys.readouterr().out
    assert "pending_install" in out
    assert "only-vault" in out
    assert "install --force" in out


def test_cli_sync_ide_mode_deprecated(
    env: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _seed_vault(env, ["only-vault"])
    home = env / "home"
    (home / ".claude" / "skills").mkdir(parents=True)
    assert (
        main(
            [
                "sync",
                "--ide",
                "claude-code",
                "--os",
                "linux",
                "--home",
                str(home),
            ]
        )
        == 0
    )
    captured = capsys.readouterr()
    assert "pending_install" in captured.out
    assert "deprecated" in captured.err
    assert "sv doctor" in captured.err


def test_cli_rejects_mixed_modes() -> None:
    assert main(["sync", "--all", "--ide", "cursor", "--os", "windows"]) == 1
