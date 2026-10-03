"""CI gates for vault/imported structure, registry, and security (M6 / issue #25)."""

from __future__ import annotations

from pathlib import Path

import yaml

from cli.common import REGISTRY_PATH, VAULT_IMPORTED, iter_vault_skills, read_frontmatter
from cli.security_scan import scan_tree

REPO_ROOT = Path(__file__).resolve().parent.parent


def _imported_skills() -> list[tuple[str, Path, str]]:
    """Return (name, path, category) for vault/imported only."""
    return [
        (name, path, category)
        for name, path, origin, category in iter_vault_skills()
        if origin == "imported"
    ]


def test_imported_skills_have_source_and_skill_md() -> None:
    skills = _imported_skills()
    assert skills, "expected at least one imported skill in vault"
    for name, path, _category in skills:
        assert (path / "SKILL.md").is_file(), f"{name}: missing SKILL.md"
        assert (path / "SOURCE.md").is_file(), f"{name}: missing SOURCE.md"


def test_imported_skills_in_registry() -> None:
    data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8")) or {}
    registered = {s.get("name") for s in (data.get("skills") or [])}
    for name, path, category in _imported_skills():
        assert name in registered, f"{name} missing from registry/sources.yaml"
        entry = next(s for s in data["skills"] if s.get("name") == name)
        expected_local = f"vault/imported/{category}/{name}"
        if entry.get("local"):
            assert Path(entry["local"]).as_posix() == expected_local
        if entry.get("category"):
            assert entry["category"] == category


def test_imported_frontmatter_has_name_and_description() -> None:
    for name, path, category in _imported_skills():
        meta, _body = read_frontmatter(path / "SKILL.md")
        assert meta.get("name"), f"{name}: frontmatter missing name"
        assert meta.get("description"), f"{name}: frontmatter missing description"
        # Prefer taxonomy alignment when metadata.category is present
        md_cat = (meta.get("metadata") or {}).get("category")
        if md_cat:
            assert md_cat == category, (
                f"{name}: metadata.category={md_cat!r} != dir category={category!r}"
            )


def test_imported_skills_security_not_fail() -> None:
    for name, path, _category in _imported_skills():
        report = scan_tree(path)
        assert report.verdict != "FAIL", (
            f"{name}: security scan FAIL "
            f"(critical={report.counts.get('critical', 0)}). "
            "Fix findings or document Gate B acceptance outside CI gate."
        )


def test_no_skillvault_sidecars_in_imported_tree() -> None:
    if not VAULT_IMPORTED.is_dir():
        return
    leaked = [
        p.relative_to(REPO_ROOT).as_posix()
        for p in VAULT_IMPORTED.rglob("_skillvault_*")
        if p.is_file()
    ]
    assert not leaked, f"security/summary sidecars must not live in vault: {leaked}"
