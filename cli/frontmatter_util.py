from __future__ import annotations

from typing import Any

from cli.common import ADAPTERS_DIR, load_yaml, read_frontmatter, write_skill_md
from pathlib import Path


def load_frontmatter_policy() -> dict:
    return load_yaml(ADAPTERS_DIR / "frontmatter.yaml")


def filter_meta_for_ide(meta: dict[str, Any], ide: str) -> dict[str, Any]:
    policy = load_frontmatter_policy()
    keep = ((policy.get("ides") or {}).get(ide) or {}).get("keep")
    if keep is None:
        return dict(meta)
    if keep == "*":
        return dict(meta)
    return {k: v for k, v in meta.items() if k in set(keep)}


def write_filtered_skill_md(src: Path, dest: Path, ide: str) -> None:
    meta, body = read_frontmatter(src)
    filtered = filter_meta_for_ide(meta, ide)
    # Ensure required keys survive even if missing from keep list.
    for key in ("name", "description"):
        if key in meta:
            filtered[key] = meta[key]
    write_skill_md(dest, filtered, body)
