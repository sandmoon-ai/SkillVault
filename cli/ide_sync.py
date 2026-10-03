"""Vault ↔ IDE skill presence report (M3). Not upstream registry sync."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cli.common import iter_vault_skills
from cli.paths import resolve_install_dir


@dataclass
class IdeSyncReport:
    ide: str
    os_name: str
    scope: str
    ide_root: Path
    pending_install: list[str]
    orphan_in_ide: list[str]
    in_sync: list[str]


def list_ide_skill_names(ide_root: Path) -> set[str]:
    if not ide_root.is_dir():
        return set()
    names: set[str] = set()
    for child in ide_root.iterdir():
        if child.is_dir() and not child.name.startswith("."):
            names.add(child.name)
    return names


def compare_vault_to_ide(
    *,
    ide: str,
    os_name: str,
    scope: str = "user",
    project_root: Path | None = None,
    home_override: Path | None = None,
) -> IdeSyncReport:
    ide_root = resolve_install_dir(
        ide,
        os_name,
        scope=scope,
        project_root=project_root,
        home_override=home_override,
    )
    vault_names = {name for name, _path, _origin, _cat in iter_vault_skills()}
    ide_names = list_ide_skill_names(ide_root)

    pending = sorted(vault_names - ide_names)
    orphan = sorted(ide_names - vault_names)
    synced = sorted(vault_names & ide_names)

    return IdeSyncReport(
        ide=ide,
        os_name=os_name,
        scope=scope,
        ide_root=ide_root,
        pending_install=pending,
        orphan_in_ide=orphan,
        in_sync=synced,
    )


def format_ide_sync_report(report: IdeSyncReport) -> str:
    lines = [
        f"IDE sync: ide={report.ide} os={report.os_name} scope={report.scope}",
        f"IDE skills root: {report.ide_root}",
        "",
        f"in_sync ({len(report.in_sync)}):",
    ]
    if report.in_sync:
        lines.extend(f"  - {n}" for n in report.in_sync)
    else:
        lines.append("  (none)")
    lines.append("")
    lines.append(f"pending_install ({len(report.pending_install)}):")
    if report.pending_install:
        lines.extend(f"  - {n}" for n in report.pending_install)
        lines.append(
            "  hint: py cli/sv.py install <name> "
            f"--ide {report.ide} --os {report.os_name}"
        )
    else:
        lines.append("  (none)")
    lines.append("")
    lines.append(f"orphan_in_ide ({len(report.orphan_in_ide)}):")
    if report.orphan_in_ide:
        lines.extend(f"  - {n}" for n in report.orphan_in_ide)
        lines.append("  hint: move into vault or remove from IDE after review")
    else:
        lines.append("  (none)")
    return "\n".join(lines)
