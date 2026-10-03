from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
VAULT_OWN = REPO_ROOT / "vault" / "own"
VAULT_IMPORTED = REPO_ROOT / "vault" / "imported"
ADAPTERS_DIR = REPO_ROOT / "adapters"
REGISTRY_PATH = REPO_ROOT / "registry" / "sources.yaml"
CACHE_DIR = REPO_ROOT / ".cache"
EXCLUDE_ON_INSTALL = {"SOURCE.md", ".gitkeep", "tests.yaml"}
SKIP_SKILL_DIRS = {"_template"}
# 与 docs/taxonomy.md 对齐；未知类目仍允许（便于演进），list 时原样显示
KNOWN_CATEGORIES = frozenset(
    {
        "foundation",
        "discover",
        "define",
        "deliver",
        "design",
        "engineering",
        "ops",
        "meta",
        "inbox",
    }
)

SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def dump_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, sort_keys=False, allow_unicode=True)


def iter_vault_skills() -> list[tuple[str, Path, str, str]]:
    """返回 (name, path, origin, category) 列表。

    支持：
    - vault/{own,imported}/<category>/<skill-name>/SKILL.md（推荐）
    - vault/{own,imported}/<skill-name>/SKILL.md（遗留扁平，category=inbox）
    """
    found: list[tuple[str, Path, str, str]] = []
    for origin, root in ("own", VAULT_OWN), ("imported", VAULT_IMPORTED):
        if not root.is_dir():
            continue
        for child in sorted(root.iterdir()):
            if not child.is_dir() or child.name in SKIP_SKILL_DIRS:
                continue
            # 遗留：直接是 skill 包
            if (child / "SKILL.md").is_file():
                found.append((child.name, child, origin, "inbox"))
                continue
            # 推荐：类目 / skill 包
            category = child.name
            for skill_dir in sorted(child.iterdir()):
                if not skill_dir.is_dir() or skill_dir.name in SKIP_SKILL_DIRS:
                    continue
                if (skill_dir / "SKILL.md").is_file():
                    found.append((skill_dir.name, skill_dir, origin, category))
    return found


def resolve_skill(name: str) -> tuple[str, Path, str, str]:
    matches = [item for item in iter_vault_skills() if item[0] == name]
    if not matches:
        available = ", ".join(n for n, _, _, _ in iter_vault_skills()) or "(none)"
        raise FileNotFoundError(f"Skill not found: {name}. Available: {available}")
    if len(matches) > 1:
        own = [m for m in matches if m[2] == "own"]
        return own[0] if own else matches[0]
    return matches[0]


def validate_skill_name(name: str) -> None:
    if not SKILL_NAME_RE.fullmatch(name):
        raise ValueError(
            f"Invalid skill name '{name}'. Use lowercase letters, digits, hyphens."
        )


def validate_category(category: str) -> None:
    if not SKILL_NAME_RE.fullmatch(category):
        raise ValueError(
            f"Invalid category '{category}'. Use lowercase letters, digits, hyphens."
        )


def read_frontmatter(skill_md: Path) -> tuple[dict[str, Any], str]:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta = yaml.safe_load(parts[1]) or {}
    body = parts[2].lstrip("\n")
    return meta, body


def write_skill_md(path: Path, meta: dict[str, Any], body: str) -> None:
    dumped = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).strip()
    content = f"---\n{dumped}\n---\n\n{body.lstrip()}"
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
