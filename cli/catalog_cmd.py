"""Generate and verify the vault skill index (catalog.yaml + skills-index*.md)."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cli import common
from cli.common import dump_yaml, iter_vault_skills, load_yaml, read_frontmatter

_DESC_MAX = 160
_LICENSE_RE = re.compile(r"(?im)^-\s*License:\s*(.+?)\s*$")

_CATEGORY_ZH = {
    "foundation": "立项 / 基础",
    "discover": "发现 / 调研",
    "define": "定义",
    "deliver": "交付",
    "design": "设计",
    "engineering": "工程",
    "ops": "运营 / 度量",
    "meta": "元工具",
    "inbox": "待归类",
}

_ORIGIN_ZH = {
    "own": "自建",
    "imported": "收录",
}


def _repo_root() -> Path:
    return common.REPO_ROOT


def catalog_yaml_path() -> Path:
    return _repo_root() / "registry" / "catalog.yaml"


def skills_index_md_path() -> Path:
    return _repo_root() / "docs" / "skills-index.md"


def skills_index_zh_md_path() -> Path:
    return _repo_root() / "docs" / "skills-index.zh-CN.md"


def descriptions_zh_path() -> Path:
    return _repo_root() / "registry" / "descriptions.zh-CN.yaml"


def registry_path() -> Path:
    return common.REGISTRY_PATH


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
    path = registry_path()
    data = load_yaml(path) if path.is_file() else {}
    out: dict[str, dict[str, Any]] = {}
    for item in data.get("skills") or []:
        if isinstance(item, dict) and item.get("name"):
            out[str(item["name"])] = item
    return out


def _descriptions_zh() -> dict[str, str]:
    path = descriptions_zh_path()
    if not path.is_file():
        return {}
    data = load_yaml(path)
    raw = data.get("descriptions") if isinstance(data, dict) else None
    if not isinstance(raw, dict):
        return {}
    return {str(k): str(v).strip() for k, v in raw.items() if str(v).strip()}


def build_catalog(*, generated_at: str | None = None) -> dict[str, Any]:
    """Scan vault tree and build a deterministic catalog payload."""
    root = _repo_root()
    registry = _registry_by_name()
    zh_map = _descriptions_zh()
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
            license_name = (
                reg.get("license") or _license_from_source_md(path) or "see LICENSE.txt"
            )
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:
            rel = path.as_posix()
        desc_en = _truncate(str(meta.get("description") or ""))
        desc_zh = zh_map.get(name) or ""
        if not desc_zh:
            meta_zh = None
            if isinstance(meta.get("metadata"), dict):
                meta_zh = meta["metadata"].get("description_zh")
            desc_zh = str(meta_zh or meta.get("description_zh") or "").strip()
        if desc_zh:
            desc_zh = _truncate(desc_zh)
        entry: dict[str, Any] = {
            "name": name,
            "category": category,
            "origin": origin,
            "path": rel,
            "description": desc_en,
            "description_zh": desc_zh,
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
    """English/bilingual chrome index (original)."""
    counts = catalog.get("counts") or {}
    total = counts.get("total", 0)
    own = counts.get("own", 0)
    imported = counts.get("imported", 0)
    lines: list[str] = [
        "# Skill Index",
        "",
        (
            "> Auto-generated by `py cli/sv.py catalog` — do not edit by hand. "
            "Source of truth: `vault/**/SKILL.md`. Machine-readable: "
            "[`registry/catalog.yaml`](../registry/catalog.yaml). "
            "Chinese: [`skills-index.zh-CN.md`](./skills-index.zh-CN.md)."
        ),
        "",
        f"- Generated (UTC): `{catalog.get('generated_at', '')}`",
        f"- Total: **{total}** (own {own} / imported {imported})",
        "",
        "## By category",
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


def render_skills_index_zh_md(catalog: dict[str, Any]) -> str:
    """Chinese human-readable index."""
    counts = catalog.get("counts") or {}
    total = counts.get("total", 0)
    own = counts.get("own", 0)
    imported = counts.get("imported", 0)
    lines: list[str] = [
        "# Skill 索引（中文）",
        "",
        (
            "> 由 `py cli/sv.py catalog` **自动生成**，请勿手改。"
            "真相源是 `vault/**/SKILL.md`；机器可读见 "
            "[`registry/catalog.yaml`](../registry/catalog.yaml)；"
            "中文简介词条维护于 "
            "[`registry/descriptions.zh-CN.yaml`](../registry/descriptions.zh-CN.yaml)。"
            "英文版：[skills-index.md](./skills-index.md)。"
        ),
        "",
        f"- 生成时间（UTC）：`{catalog.get('generated_at', '')}`",
        f"- 合计：**{total}**（自建 {own} / 收录 {imported}）",
        "",
        "## 按类目",
        "",
        "| 类目 | 说明 | 数量 |",
        "|------|------|-----:|",
    ]
    for cat, n in (counts.get("by_category") or {}).items():
        label = _CATEGORY_ZH.get(cat, cat)
        lines.append(f"| `{cat}` | {label} | {n} |")
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
            origin_label = _ORIGIN_ZH.get(origin, origin)
            lines.extend([f"## {origin_label}（`{origin}`）", ""])
        if category != current_category:
            current_category = category
            cat_label = _CATEGORY_ZH.get(category, category)
            lines.extend(
                [
                    f"### {cat_label}（`{category}`）",
                    "",
                    "| 名称 | 许可 | 用途（中文） |",
                    "|------|------|--------------|",
                ]
            )
        name = str(skill.get("name") or "")
        path = str(skill.get("path") or "")
        lic = str(skill.get("license") or "unknown").replace("|", "\\|")
        zh = str(skill.get("description_zh") or "").strip()
        en = str(skill.get("description") or "").strip()
        if zh:
            desc = zh
        elif en:
            desc = f"{en}（待译）"
        else:
            desc = "（无简介）"
        desc = desc.replace("|", "\\|")
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
    index_zh_path: Path | None = None,
) -> dict[str, Any]:
    catalog = build_catalog()
    yaml_path = catalog_path or catalog_yaml_path()
    md_path = index_path or skills_index_md_path()
    zh_path = index_zh_path or skills_index_zh_md_path()
    dump_yaml(yaml_path, catalog)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_skills_index_md(catalog), encoding="utf-8")
    zh_path.write_text(render_skills_index_zh_md(catalog), encoding="utf-8")
    return catalog


def catalog_is_fresh(
    *,
    catalog_path: Path | None = None,
    index_path: Path | None = None,
    index_zh_path: Path | None = None,
) -> tuple[bool, str]:
    """Return (ok, message) whether on-disk index matches the vault tree."""
    root = _repo_root()
    yaml_path = catalog_path or catalog_yaml_path()
    md_path = index_path or skills_index_md_path()
    zh_path = index_zh_path or skills_index_zh_md_path()
    expected = build_catalog(generated_at="CHECK")
    for path, label in (
        (yaml_path, "registry/catalog.yaml"),
        (md_path, "docs/skills-index.md"),
        (zh_path, "docs/skills-index.zh-CN.md"),
    ):
        if not path.is_file():
            try:
                rel = path.relative_to(root).as_posix()
            except ValueError:
                rel = str(path)
            return False, f"missing {rel}"
    on_disk = load_yaml(yaml_path)
    if _catalog_compare_payload(on_disk) != _catalog_compare_payload(expected):
        return False, "registry/catalog.yaml is stale; run: py cli/sv.py catalog"
    stamp = str(on_disk.get("generated_at") or "")
    expected_with_stamp = {**expected, "generated_at": stamp}
    if md_path.read_text(encoding="utf-8") != render_skills_index_md(expected_with_stamp):
        return False, "docs/skills-index.md is stale; run: py cli/sv.py catalog"
    if zh_path.read_text(encoding="utf-8") != render_skills_index_zh_md(
        expected_with_stamp
    ):
        return False, "docs/skills-index.zh-CN.md is stale; run: py cli/sv.py catalog"
    return True, "catalog up to date"


def _vault_roots_aligned() -> bool:
    """False when tests monkeypatch vault dirs outside REPO_ROOT."""
    root = _repo_root().resolve()
    for vault in (common.VAULT_OWN, common.VAULT_IMPORTED):
        try:
            vault.resolve().relative_to(root)
        except ValueError:
            return False
    return True


def refresh_catalog_after_mutation() -> None:
    """Best-effort regenerate after import/sync; never raises to callers."""
    try:
        if not _vault_roots_aligned():
            return
        write_catalog()
    except Exception:
        # Tests may omit a writable docs/ tree; real CLI paths should still work.
        pass
