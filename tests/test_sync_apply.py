"""Tests for upstream sync --apply security gate (M6 / issue #23)."""

from __future__ import annotations

from pathlib import Path

import pytest

from cli.sync_cmd import sync_skills


def _seed_registry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    source: Path,
    name: str = "demo-skill",
    category: str = "engineering",
) -> Path:
    import cli.common as common
    import cli.import_cmd as import_cmd
    import cli.sync_cmd as sync_cmd

    cache = tmp_path / "cache"
    vault_imported = tmp_path / "vault" / "imported"
    registry = tmp_path / "registry" / "sources.yaml"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        "\n".join(
            [
                "skills:",
                f"- name: {name}",
                f"  url: {source.as_posix()}",
                "  ref: local",
                f"  category: {category}",
                f"  local: vault/imported/{category}/{name}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    for mod in (common, import_cmd, sync_cmd):
        monkeypatch.setattr(mod, "CACHE_DIR", cache, raising=False)
        monkeypatch.setattr(mod, "VAULT_IMPORTED", vault_imported, raising=False)
        monkeypatch.setattr(mod, "REGISTRY_PATH", registry, raising=False)

    return vault_imported / category / name


def _write_skill(root: Path, *, secret: bool = False) -> Path:
    root.mkdir(parents=True)
    if secret:
        body = (
            "---\nname: demo-skill\n"
            "description: Intentionally bad skill for sync FAIL fixture.\n---\n\n"
            "# Bad\n\napi_key = \"AKIAIOSFODNN7EXAMPLE12\"\n"
        )
    else:
        body = (
            "---\nname: demo-skill\n"
            "description: Clean skill for sync apply tests.\n"
            "license: MIT\n---\n\n# Clean\n\nSafe content.\n"
        )
    (root / "SKILL.md").write_text(body, encoding="utf-8")
    (root / "LICENSE").write_text("MIT License\n", encoding="utf-8")
    return root


def test_sync_apply_blocked_on_fail(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    src = _write_skill(tmp_path / "src" / "demo-skill", secret=True)
    local = _seed_registry(tmp_path, monkeypatch, source=src)
    local.mkdir(parents=True)
    (local / "SKILL.md").write_text("---\nname: demo-skill\n---\n\nold\n", encoding="utf-8")
    (local / "SOURCE.md").write_text("# Source\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Security verdict"):
        sync_skills(["demo-skill"], apply=True)

    # Vault must remain untouched when apply is blocked
    assert (local / "SKILL.md").read_text(encoding="utf-8").endswith("old\n")


def test_sync_apply_skips_security_sidecars(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    src = _write_skill(tmp_path / "src" / "demo-skill", secret=False)
    local = _seed_registry(tmp_path, monkeypatch, source=src)

    reports = sync_skills(["demo-skill"], apply=True)
    assert any("applied: yes" in r for r in reports)
    assert (local / "SKILL.md").is_file()
    assert (local / "SOURCE.md").is_file()
    assert not (local / "_skillvault_security.md").exists()
    assert not (local / "_skillvault_security.json").exists()
    assert not (local / "_skillvault_summary.json").exists()
