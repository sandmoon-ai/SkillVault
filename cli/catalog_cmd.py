"""Generate and verify the vault skill index (catalog.yaml + skills-index.md)."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cli.common import (
    REPO_ROOT,
    REGISTRY_PATH,
    dump_yaml,
    iter_vault_skills,
    load_yaml,
    read_frontmatter,
)

CATALOG_YAML = REPO_ROOT / "registry" / "catalog.yaml"
SKILLS_INDEX_MD = REPO_ROOT / "docs" / "skills-index.md"
_DESC_MAX = 160
_LICENSE_RE = re.compile(r"(?im)^-\s*License:\s*(.+?)\s*$")


def _truncate(text: str, limit: int = _DESC_MAX) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _license_from_source_md(skill_dir: Path) -> str | None:
    source = skill_dir / "SOURCE.md"
    if not source.is_file():
        return None
    match = _LICENSE_RE.search(source.read_text(encoding="utf-8"))
    if not match:
        return None
    return match.group(1).strip() or None


def _registry_by_name() -> dict[str, dict[str, Any]]:
    data = load_yaml(REGISTRY_PATH) if REGISTRY_PATH.is_file() else {}
    out: dict[str, dict[str, Any]] = {}
    for item in data.get("skills") or []:
        if isinstance(item, dict) and item.get("name"):
            out[str(item["name"])] = item
    return out


def build_catalog(*, generated_at: str | None = None) -> dict[str, Any]:
    """Scan vault tree and build a deterministic catalog payload."""
    registry = _registry_by_name()
    skills: list[dict[str, Any]] = []
    for name, path, origin, category in iter_vault_skills():
        meta, _body = read_frontmatter(path / "SKILL.md")
        reg = registry.get(name) or {}
        tags = meta.get("metadata", {}) if isinstance(meta.get("metadata"), dict) else {}
        tag_list = tags.get("tags") if isinstance(tags, dict) else None
        if not isinstance(tag_list, list):
            tag_list = meta.get("tags") if isinstance(meta.get("tags"), list) else []
        license_name = (
            reg.get("license")
            or _license_from_source_md(path)
            or meta.get("license")
            or "unknown"
        )
        if isinstance(license_name, str) and license_name.startswith("Complete terms"):
            # Prefer SPDX from registry/SOURCE when frontmatter only points at LICENSE.txt
            license_name = (
                reg.get("license") or _license_from_source_md(path) or "see LICENSE.txt"
            )
        entry: dict[str, Any] = {
            "name": name,
            "category": category,
            "origin": origin,
            "path": path.relative_to(REPO_ROOT).as_posix(),
            "description": _truncate(str(meta.get("description") or "")),
            "license": str(license_name),
            "tags": [str(t) for t in tag_list],
        }
        if reg.get("url"):
            entry["upstream"] = str(reg["url"])
        skills.append(entry)

    skills.sort(key=lambda s: (s["origin"], s["category"], s["name"]))
    own = sum(1 for s in skills if s["origin"] == "own")
    imported = sum(1 for s in skills if s["origin"] == "imported")
    by_category: dict[str, int] = {}
    for s in skills:
        by_category[s["category"]] = by_category.get(s["category"], 0) + 1

    return {
        "generated_by": "py cli/sv.py catalog",
        "generated_at": generated_at
        or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "counts": {
            "total": len(skills),
            "own": own,
            "imported": imported,
            "by_category": dict(sorted(by_category.items())),
        },
        "skills": skills,
    }


def render_skills_index_md(catalog: dict[str, Any]) -> str:
    """Human-readable Markdown index grouped by origin then category."""
    counts = catalog.get("counts") or {}
    total = counts.get("total", 0)
    own = counts.get("own", 0)
    imported = counts.get("imported", 0)
    lines: list[str] = [
        "# Skill 索引",
        "",
        (
            "> 由 `py cli/sv.py catalog` **自动生成**，请勿手改。"
            "真相源是 `vault/**/SKILL.md`；机器可读副本见 "
            "[`registry/catalog.yaml`](../registry/catalog.yaml)。"
        ),
        "",
        f"- 生成时间（UTC）：`{catalog.get('generated_at', '')}`",
        f"- 合计：**{total}**（own {own} / imported {imported}）",
        "",
        "## 按类目",
        "",
        "| category | count |",
        "|----------|------:|",
    ]
    for cat, n in (counts.get("by_category") or {}).items():
        lines.append(f"| `{cat}` | {n} |")
    lines.append("")

    skills: list[dict[str, Any]] = list(catalog.get("skills") or [])
    current_origin = ""
    current_category = ""
    for skill in skills:
        origin = str(skill.get("origin") or "")
        category = str(skill.get("category") or "")
        if origin != current_origin:
            current_origin = origin
            current_category = ""
            lines.extend([f"## {origin}", ""])
        if category != current_category:
            current_category = category
            lines.extend(
                [
                    f"### `{category}`",
                    "",
                    "| name | license | description |",
                    "|------|---------|-------------|",
                ]
            )
        desc = str(skill.get("description") or "").replace("|", "\\|")
        lic = str(skill.get("license") or "unknown").replace("|", "\\|")
        name = str(skill.get("name") or "")
        path = str(skill.get("path") or "")
        lines.append(f"| [`{name}`](../{path}/) | {lic} | {desc} |")
    lines.append("")
    return "\n".join(lines)


def _catalog_compare_payload(catalog: dict[str, Any]) -> dict[str, Any]:
    """Drop volatile timestamp for freshness checks."""
    return {
        "counts": catalog.get("counts"),
        "skills": catalog.get("skills"),
    }


def write_catalog(
    *,
    catalog_path: Path | None = None,
    index_path: Path | None = None,
) -> dict[str, Any]:
    catalog = build_catalog()
    yaml_path = catalog_path or CATALOG_YAML
    md_path = index_path or SKILLS_INDEX_MD
    dump_yaml(yaml_path, catalog)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_skills_index_md(catalog), encoding="utf-8")
    return catalog


def catalog_is_fresh(
    *,
    catalog_path: Path | None = None,
    index_path: Path | None = None,
) -> tuple[bool, str]:
    """Return (ok, message) whether on-disk index matches the vault tree."""
    yaml_path = catalog_path or CATALOG_YAML
    md_path = index_path or SKILLS_INDEX_MD
    expected = build_catalog(generated_at="CHECK")
    if not yaml_path.is_file():
        return False, f"missing {yaml_path.relative_to(REPO_ROOT).as_posix()}"
    if not md_path.is_file():
        return False, f"missing {md_path.relative_to(REPO_ROOT).as_posix()}"
    on_disk = load_yaml(yaml_path)
    if _catalog_compare_payload(on_disk) != _catalog_compare_payload(expected):
        return False, "registry/catalog.yaml is stale; run: py cli/sv.py catalog"
    expected_md = render_skills_index_md(
        {**expected, "generated_at": on_disk.get("generated_at") or "CHECK"}
    )
    # Compare MD using on-disk generated_at so timestamp alone doesn't fail
    actual_md = md_path.read_text(encoding="utf-8")
    if actual_md != expected_md:
        # Allow MD timestamp line to match yaml's generated_at
        expected_md = render_skills_index_md(
            {
                **expected,
                "generated_at": str(on_disk.get("generated_at") or ""),
            }
        )
        if actual_md != expected_md:
            return False, "docs/skills-index.md is stale; run: py cli/sv.py catalog"
    return True, "catalog up to date"


def refresh_catalog_after_mutation() -> None:
    """Best-effort regenerate after import/sync; never raises to callers."""
    try:
        write_catalog()
    except OSError:
        pass
