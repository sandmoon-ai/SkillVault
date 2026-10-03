"""Tests for M4/M5 watch helpers."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from cli.watch_security_sources import watch_security_sources
from cli.watch_upstream import watch_upstream


def test_watch_upstream_empty_registry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import cli.common as common
    import cli.watch_upstream as wu

    reg = tmp_path / "sources.yaml"
    reg.write_text("skills: []\n", encoding="utf-8")
    monkeypatch.setattr(common, "REGISTRY_PATH", reg)
    monkeypatch.setattr(wu, "REGISTRY_PATH", reg)
    report = watch_upstream()
    assert report.has_drift is False
    assert report.items == []


def test_watch_upstream_detects_change(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import cli.common as common
    import cli.watch_upstream as wu

    # Local vault copy
    local = tmp_path / "vault" / "imported" / "inbox" / "demo"
    local.mkdir(parents=True)
    (local / "SKILL.md").write_text(
        "---\nname: demo\ndescription: old\n---\n\nold\n", encoding="utf-8"
    )

    # Upstream-like source dir
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    (upstream / "SKILL.md").write_text(
        "---\nname: demo\ndescription: new\n---\n\nnew\n", encoding="utf-8"
    )

    reg = tmp_path / "sources.yaml"
    reg.write_text(
        yaml.safe_dump(
            {
                "skills": [
                    {
                        "name": "demo",
                        "url": str(upstream),
                        "ref": "local",
                        "category": "inbox",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(common, "REGISTRY_PATH", reg)
    monkeypatch.setattr(wu, "REGISTRY_PATH", reg)
    monkeypatch.setattr(common, "VAULT_IMPORTED", tmp_path / "vault" / "imported")
    monkeypatch.setattr(wu, "VAULT_IMPORTED", tmp_path / "vault" / "imported")
    monkeypatch.setattr(common, "CACHE_DIR", tmp_path / "cache")
    import cli.import_cmd as import_cmd

    monkeypatch.setattr(import_cmd, "CACHE_DIR", tmp_path / "cache")

    report = watch_upstream()
    assert report.has_drift is True
    assert report.items[0].status == "changed"


def test_watch_security_local_and_pin(tmp_path: Path) -> None:
    pinned = tmp_path / "rules.txt"
    pinned.write_text("v1\n", encoding="utf-8")
    digest = __import__("hashlib").sha256(pinned.read_bytes()).hexdigest()
    sources = tmp_path / "security_sources.yaml"
    sources.write_text(
        yaml.safe_dump(
            {
                "sources": [
                    {
                        "id": "local",
                        "url": str(pinned),
                        "kind": "local-file",
                        "last_seen": digest,
                    },
                    {
                        "id": "pin-a",
                        "url": "https://example.com/x",
                        "kind": "pin",
                        "track": "v1",
                        "last_seen": "v1",
                    },
                    {
                        "id": "pin-b",
                        "url": "https://example.com/y",
                        "kind": "pin",
                        "track": "v2",
                        "last_seen": "v1",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    report = watch_security_sources(sources)
    by_id = {i.id: i for i in report.items}
    assert by_id["local"].status == "unchanged"
    assert by_id["pin-a"].status == "unchanged"
    assert by_id["pin-b"].status == "changed"
    assert report.has_changes is True
