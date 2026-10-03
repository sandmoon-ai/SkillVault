"""Upstream registry drift watch (M4). Never applies into vault."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from cli.common import REGISTRY_PATH, VAULT_IMPORTED, load_yaml
from cli.import_cmd import import_from_url
from cli.sync_cmd import _dir_diff


@dataclass
class UpstreamItem:
    name: str
    status: str  # unchanged | changed | missing-local | fetch-failed
    url: str = ""
    ref: str = ""
    category: str = ""
    diff_count: int = 0
    diffs: list[str] = field(default_factory=list)
    error: str = ""


@dataclass
class UpstreamWatchReport:
    items: list[UpstreamItem]
    has_drift: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "has_drift": self.has_drift,
            "items": [asdict(i) for i in self.items],
        }


def watch_upstream(names: list[str] | None = None, *, all_skills: bool = True) -> UpstreamWatchReport:
    data = load_yaml(REGISTRY_PATH)
    skills = list(data.get("skills") or [])
    if not skills:
        return UpstreamWatchReport(items=[], has_drift=False)

    if all_skills or not names:
        selected = skills
    else:
        wanted = set(names)
        selected = [s for s in skills if s.get("name") in wanted]

    items: list[UpstreamItem] = []
    for entry in selected:
        name = str(entry.get("name") or "")
        url = str(entry.get("url") or "")
        ref = str(entry.get("ref") or "main")
        category = str(entry.get("category") or "inbox")
        local = VAULT_IMPORTED / category / name
        try:
            result = import_from_url(url, name=name, ref=ref, apply=False)
            if not local.exists():
                items.append(
                    UpstreamItem(
                        name=name,
                        status="missing-local",
                        url=url,
                        ref=ref,
                        category=category,
                        diff_count=1,
                        diffs=["new-skill / missing local"],
                    )
                )
                continue
            diffs = _dir_diff(result.cache_dir, local)
            # Ignore SkillVault sidecars that only exist in cache
            diffs = [
                d
                for d in diffs
                if "_skillvault_" not in d and "SOURCE.md" not in d
            ]
            status = "changed" if diffs else "unchanged"
            items.append(
                UpstreamItem(
                    name=name,
                    status=status,
                    url=url,
                    ref=ref,
                    category=category,
                    diff_count=len(diffs),
                    diffs=diffs[:40],
                )
            )
        except Exception as exc:  # noqa: BLE001 — watch must continue
            items.append(
                UpstreamItem(
                    name=name,
                    status="fetch-failed",
                    url=url,
                    ref=ref,
                    category=category,
                    error=str(exc),
                )
            )

    drift = any(i.status in {"changed", "missing-local"} for i in items)
    return UpstreamWatchReport(items=items, has_drift=drift)


def format_upstream_watch(report: UpstreamWatchReport) -> str:
    lines = [f"has_drift: {report.has_drift}", f"items: {len(report.items)}"]
    for item in report.items:
        lines.append(f"- {item.name}: {item.status} (diffs={item.diff_count})")
        if item.error:
            lines.append(f"  error: {item.error}")
        for d in item.diffs[:10]:
            lines.append(f"  · {d}")
    return "\n".join(lines)


def write_upstream_json(path: Path, report: UpstreamWatchReport) -> None:
    path.write_text(
        json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
