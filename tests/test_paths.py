"""Unit tests for install path resolution (M1 / issue #4)."""

from __future__ import annotations

from pathlib import Path

import pytest

from cli.paths import list_ides, resolve_install_dir

IDES = list_ides()
OS_NAMES = ("linux", "macos", "windows")


@pytest.mark.parametrize("ide", IDES)
@pytest.mark.parametrize("os_name", OS_NAMES)
def test_resolve_user_install_dir(tmp_path: Path, ide: str, os_name: str) -> None:
    home = tmp_path / "home"
    home.mkdir()
    dest = resolve_install_dir(
        ide, os_name, scope="user", home_override=home
    )
    assert dest.is_absolute()
    assert str(dest).startswith(str(home.resolve()))
    # User templates end at the IDE skills root (skill name appended at install)
    assert dest.name == "skills"


def test_project_scope_requires_root(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="project-root"):
        resolve_install_dir("cursor", "linux", scope="project")


def test_project_root_only_with_project_scope(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="only valid with --scope project"):
        resolve_install_dir(
            "cursor",
            "linux",
            scope="user",
            project_root=tmp_path / "proj",
            home_override=tmp_path / "home",
        )


def test_project_scope_expands_root(tmp_path: Path) -> None:
    proj = tmp_path / "myproj"
    proj.mkdir()
    dest = resolve_install_dir(
        "cursor", "windows", scope="project", project_root=proj
    )
    assert dest == (proj / ".cursor" / "skills").resolve()


def test_home_override_used(tmp_path: Path) -> None:
    home = tmp_path / "alt-home"
    home.mkdir()
    dest = resolve_install_dir(
        "claude-code", "windows", scope="user", home_override=home
    )
    assert dest == (home / ".claude" / "skills").resolve()


def test_unknown_ide_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unknown IDE"):
        resolve_install_dir(
            "not-an-ide", "linux", home_override=tmp_path / "h"
        )


def test_unsupported_os_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unsupported OS"):
        resolve_install_dir("cursor", "dos", home_override=tmp_path / "h")
