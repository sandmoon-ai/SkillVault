"""Tests for skill catalog generation and freshness gate."""

from __future__ import annotations

from pathlib import Path

import yaml

from cli import catalog_cmd
from cli.sv import main


def _seed(root: Path) -> None:
    skill = root / "vault" / "own" / "meta" / "hello-a"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: hello-a\ndescription: A short hello skill.\n"
        "metadata:\n  category: meta\n  tags: [smoke]\n---\n\n# hello-a\n",
        encoding="utf-8",
    )
    imported = root / "vault" / "imported" / "deliver" / "demo-skill"
    imported.mkdir(parents=True)
    (imported / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: Demo imported skill.\n---\n\n# demo\n",
        encoding="utf-8",
    )
    (imported / "SOURCE.md").write_text(
        "# Source\n\n- License: Apache-2.0\n",
        encoding="utf-8",
    )
    reg = root / "registry"
    reg.mkdir(parents=True)
    (reg / "sources.yaml").write_text(
        "skills:\n"
        "- name: demo-skill\n"
        "  url: https://example.com/demo\n"
        "  license: Apache-2.0\n"
        "  category: deliver\n"
        "  local: vault/imported/deliver/demo-skill\n",
        encoding="utf-8",
    )


def _patch_roots(monkeypatch, root: Path) -> None:
    import cli.common as common

    monkeypatch.setattr(common, "REPO_ROOT", root)
    monkeypatch.setattr(common, "VAULT_OWN", root / "vault" / "own")
    monkeypatch.setattr(common, "VAULT_IMPORTED", root / "vault" / "imported")
    monkeypatch.setattr(common, "REGISTRY_PATH", root / "registry" / "sources.yaml")


def test_write_and_check_catalog(tmp_path: Path, monkeypatch) -> None:
    _seed(tmp_path)
    _patch_roots(monkeypatch, tmp_path)

    ok, msg = catalog_cmd.catalog_is_fresh()
    assert not ok
    assert "missing" in msg

    catalog = catalog_cmd.write_catalog()
    assert catalog["counts"]["total"] == 2
    assert catalog["counts"]["own"] == 1
    assert catalog["counts"]["imported"] == 1
    names = {s["name"] for s in catalog["skills"]}
    assert names == {"hello-a", "demo-skill"}
    demo = next(s for s in catalog["skills"] if s["name"] == "demo-skill")
    assert demo["license"] == "Apache-2.0"
    assert demo["upstream"] == "https://example.com/demo"

    ok, msg = catalog_cmd.catalog_is_fresh()
    assert ok, msg

    extra = tmp_path / "vault" / "own" / "meta" / "hello-b"
    extra.mkdir(parents=True)
    (extra / "SKILL.md").write_text(
        "---\nname: hello-b\ndescription: Another.\n---\n\n# b\n",
        encoding="utf-8",
    )
    ok, msg = catalog_cmd.catalog_is_fresh()
    assert not ok
    assert "stale" in msg


def test_cli_catalog_check_exit_codes(tmp_path: Path, monkeypatch, capsys) -> None:
    _seed(tmp_path)
    _patch_roots(monkeypatch, tmp_path)

    assert main(["catalog", "--check"]) == 2
    # Optional Chinese blurb
    (tmp_path / "registry" / "descriptions.zh-CN.yaml").write_text(
        "descriptions:\n  hello-a: 简短中文简介。\n",
        encoding="utf-8",
    )

    assert main(["catalog"]) == 0
    out = capsys.readouterr().out
    assert "skills-index.zh-CN.md" in out
    assert main(["catalog", "--check"]) == 0
    data = yaml.safe_load(
        (tmp_path / "registry" / "catalog.yaml").read_text(encoding="utf-8")
    )
    assert data["counts"]["total"] == 2
    zh = (tmp_path / "docs" / "skills-index.zh-CN.md").read_text(encoding="utf-8")
    assert "Skill 索引（中文）" in zh
    assert "简短中文简介" in zh
    assert "demo-skill" in zh and "待译" in zh
