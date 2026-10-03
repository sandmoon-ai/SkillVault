"""Tests for import security scan (M2 / issue #12)."""

from __future__ import annotations

from pathlib import Path

import pytest

from cli.import_cmd import import_from_url
from cli.security_scan import require_report_for_apply, scan_tree, write_reports
from cli.sv import main


def _write_clean_skill(root: Path) -> Path:
    skill = root / "clean-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: clean-skill\n"
        "description: A clean demo skill for security tests.\n"
        "license: MIT\n---\n\n# Clean\n\nSafe content.\n",
        encoding="utf-8",
    )
    (skill / "LICENSE").write_text("MIT License\n", encoding="utf-8")
    return skill


def _write_secret_skill(root: Path) -> Path:
    skill = root / "secret-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: secret-skill\n"
        "description: Intentionally bad skill for scanner FAIL fixture.\n---\n\n"
        "# Bad\n\napi_key = \"AKIAIOSFODNN7EXAMPLE12\"\n",
        encoding="utf-8",
    )
    return skill


def test_scan_clean_pass(tmp_path: Path) -> None:
    skill = _write_clean_skill(tmp_path)
    report = scan_tree(skill)
    assert report.verdict in {"PASS", "PASS_WITH_WARNINGS"}
    assert report.counts.get("critical", 0) == 0
    write_reports(skill, report)
    assert (skill / "_skillvault_security.md").is_file()


def test_scan_secret_fail(tmp_path: Path) -> None:
    skill = _write_secret_skill(tmp_path)
    report = scan_tree(skill)
    assert report.verdict == "FAIL"
    assert report.counts.get("critical", 0) >= 1
    assert any(f.rule_id in {"aws_access_key", "generic_api_key"} for f in report.findings)


def test_cli_security_scan_exit_codes(tmp_path: Path) -> None:
    clean = _write_clean_skill(tmp_path)
    assert main(["security-scan", str(clean)]) == 0
    bad = _write_secret_skill(tmp_path)
    assert main(["security-scan", str(bad)]) == 2


def test_apply_blocked_on_fail(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import cli.common as common
    import cli.import_cmd as import_cmd

    monkeypatch.setattr(common, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(import_cmd, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(common, "VAULT_IMPORTED", tmp_path / "vault" / "imported")
    monkeypatch.setattr(import_cmd, "VAULT_IMPORTED", tmp_path / "vault" / "imported")
    monkeypatch.setattr(common, "REGISTRY_PATH", tmp_path / "registry" / "sources.yaml")
    monkeypatch.setattr(import_cmd, "REGISTRY_PATH", tmp_path / "registry" / "sources.yaml")
    (tmp_path / "registry").mkdir(parents=True)
    (tmp_path / "registry" / "sources.yaml").write_text("skills: []\n", encoding="utf-8")

    bad = _write_secret_skill(tmp_path / "src")
    with pytest.raises(ValueError, match="Security verdict"):
        import_from_url(str(bad), name="secret-skill", apply=True)


def test_require_report_missing(tmp_path: Path) -> None:
    skill = _write_clean_skill(tmp_path)
    with pytest.raises(ValueError, match="Missing security report"):
        require_report_for_apply(skill)
