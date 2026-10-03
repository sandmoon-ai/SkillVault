"""Unit tests for skill install copy behavior (M1 / issue #4)."""

from __future__ import annotations

from pathlib import Path

import pytest

from cli.common import read_frontmatter
from cli.install_cmd import install_skills


def _write_skill(root: Path, name: str = "demo-skill") -> Path:
    skill = root / "vault" / "own" / "meta" / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                f"name: {name}",
                "description: Demo skill for install tests. Trigger when testing.",
                "license: MIT",
                "compatibility: linux, windows",
                "metadata:",
                "  category: meta",
                "  tags: [test]",
                "allowed-tools: Bash",
                "disable-model-invocation: true",
                "extra-vault-only: should-strip-on-codex",
                "---",
                "",
                "# Demo",
                "",
                "Body text.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (skill / "SOURCE.md").write_text("# Source\n", encoding="utf-8")
    (skill / "_skillvault_security.md").write_text("# scan\n", encoding="utf-8")
    (skill / "_skillvault_security.json").write_text("{}\n", encoding="utf-8")
    (skill / "_skillvault_summary.json").write_text("{}\n", encoding="utf-8")
    scripts = skill / "scripts"
    scripts.mkdir()
    (scripts / "tests.yaml").write_text("tests: []\n", encoding="utf-8")
    (scripts / "hello.sh").write_text("#!/bin/sh\necho ok\n", encoding="utf-8")
    (skill / ".gitkeep").write_text("", encoding="utf-8")
    return skill


@pytest.fixture()
def vault_skill(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point cli.common vault roots at a temp tree and seed one skill."""
    import cli.common as common
    import cli.install_cmd as install_cmd

    skill = _write_skill(tmp_path)
    monkeypatch.setattr(common, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(common, "VAULT_OWN", tmp_path / "vault" / "own")
    monkeypatch.setattr(common, "VAULT_IMPORTED", tmp_path / "vault" / "imported")
    # install_cmd imports resolve_skill from common at call time via resolve_skill
    # but resolve_skill uses common.VAULT_* — already patched.
    _ = install_cmd
    # Adapters still load from real repo (frontmatter + targets)
    return skill


def test_install_excludes_source_and_tests(
    vault_skill: Path, tmp_path: Path
) -> None:
    home = tmp_path / "home"
    home.mkdir()
    installed = install_skills(
        ["demo-skill"],
        ide="cursor",
        os_name="windows",
        home_override=home,
    )
    dest = installed[0]
    assert dest.name == "demo-skill"
    assert (dest / "SKILL.md").is_file()
    assert (dest / "scripts" / "hello.sh").is_file()
    assert not (dest / "SOURCE.md").exists()
    assert not (dest / "scripts" / "tests.yaml").exists()
    assert not (dest / ".gitkeep").exists()
    assert not (dest / "_skillvault_security.md").exists()
    assert not (dest / "_skillvault_security.json").exists()
    assert not (dest / "_skillvault_summary.json").exists()
    # Flat under IDE skills root (no category segment)
    assert dest.parent.name == "skills"


def test_install_default_no_overwrite(
    vault_skill: Path, tmp_path: Path
) -> None:
    home = tmp_path / "home"
    home.mkdir()
    install_skills(
        ["demo-skill"],
        ide="cursor",
        os_name="linux",
        home_override=home,
    )
    with pytest.raises(FileExistsError, match="--force"):
        install_skills(
            ["demo-skill"],
            ide="cursor",
            os_name="linux",
            home_override=home,
        )


def test_install_force_overwrites(vault_skill: Path, tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir()
    first = install_skills(
        ["demo-skill"],
        ide="cursor",
        os_name="linux",
        home_override=home,
    )[0]
    marker = first / "stale.txt"
    marker.write_text("old", encoding="utf-8")
    second = install_skills(
        ["demo-skill"],
        ide="cursor",
        os_name="linux",
        home_override=home,
        force=True,
    )[0]
    assert second == first
    assert not marker.exists()
    assert (second / "SKILL.md").is_file()


def test_install_frontmatter_filtered_for_codex(
    vault_skill: Path, tmp_path: Path
) -> None:
    home = tmp_path / "home"
    home.mkdir()
    dest = install_skills(
        ["demo-skill"],
        ide="codex",
        os_name="linux",
        home_override=home,
    )[0]
    meta, body = read_frontmatter(dest / "SKILL.md")
    assert meta["name"] == "demo-skill"
    assert "description" in meta
    assert "disable-model-invocation" not in meta
    assert "extra-vault-only" not in meta
    assert "Demo" in body or "Body" in body


def test_install_frontmatter_keeps_cursor_extension(
    vault_skill: Path, tmp_path: Path
) -> None:
    home = tmp_path / "home"
    home.mkdir()
    dest = install_skills(
        ["demo-skill"],
        ide="cursor",
        os_name="macos",
        home_override=home,
    )[0]
    meta, _ = read_frontmatter(dest / "SKILL.md")
    assert meta.get("disable-model-invocation") is True
    # Non-listed keys are stripped even for cursor
    assert "extra-vault-only" not in meta
