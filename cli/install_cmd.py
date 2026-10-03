from __future__ import annotations

import shutil
from pathlib import Path

from cli.common import EXCLUDE_ON_INSTALL, iter_vault_skills, resolve_skill
from cli.frontmatter_util import write_filtered_skill_md
from cli.paths import resolve_install_dir


def _copy_skill(
    src: Path,
    dest: Path,
    *,
    ide: str,
    force: bool,
    link: bool,
) -> Path:
    if dest.exists():
        if not force:
            raise FileExistsError(
                f"Destination exists: {dest}. Use --force to overwrite."
            )
        if dest.is_dir() and not dest.is_symlink():
            shutil.rmtree(dest)
        else:
            dest.unlink()

    dest.parent.mkdir(parents=True, exist_ok=True)

    if link:
        dest.symlink_to(src, target_is_directory=True)
        return dest

    dest.mkdir(parents=True, exist_ok=True)
    for item in src.rglob("*"):
        rel = item.relative_to(src)
        if any(part in EXCLUDE_ON_INSTALL for part in rel.parts):
            continue
        if item.name in EXCLUDE_ON_INSTALL:
            continue
        target = dest / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if item.name == "SKILL.md":
            write_filtered_skill_md(item, target, ide)
        else:
            shutil.copy2(item, target)
    return dest


def install_skills(
    names: list[str] | None,
    *,
    ide: str,
    os_name: str,
    scope: str = "user",
    project_root: Path | None = None,
    force: bool = False,
    link: bool = False,
    home_override: Path | None = None,
    all_skills: bool = False,
) -> list[Path]:
    if scope == "project" and project_root is None:
        raise ValueError("project scope requires --project-root")
    if scope != "project" and project_root is not None:
        raise ValueError("--project-root requires --scope project")

    base = resolve_install_dir(
        ide,
        os_name,
        scope=scope,
        project_root=project_root,
        home_override=home_override,
    )

    if all_skills:
        selected = iter_vault_skills()
    else:
        if not names:
            raise ValueError("Provide skill name(s) or --all")
        selected = [resolve_skill(n) for n in names]

    installed: list[Path] = []
    for name, src, _origin, _category in selected:
        dest = base / name
        installed.append(
            _copy_skill(src, dest, ide=ide, force=force, link=link)
        )
    return installed
