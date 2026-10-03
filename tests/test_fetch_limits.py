"""Fetch size limits and GitHub auth headers (M6 / issue #29)."""

from __future__ import annotations

from pathlib import Path

import pytest

from cli.import_cmd import (
    MAX_FETCH_FILES,
    _FetchBudget,
    _copy_local,
    _github_headers,
    import_from_url,
)


def test_github_headers_include_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    assert "Authorization" not in _github_headers(json_api=True)

    monkeypatch.setenv("GH_TOKEN", "secret-token")
    headers = _github_headers(json_api=True)
    assert headers["Authorization"] == "Bearer secret-token"
    assert headers["Accept"] == "application/vnd.github+json"


def test_fetch_budget_rejects_too_many_files(tmp_path: Path) -> None:
    src = tmp_path / "big"
    src.mkdir()
    for i in range(MAX_FETCH_FILES + 1):
        (src / f"f{i}.txt").write_text("x", encoding="utf-8")
    dest = tmp_path / "dest"
    with pytest.raises(ValueError, match="too many files"):
        _copy_local(src, dest, _FetchBudget())


def test_fetch_budget_rejects_too_large_bytes(tmp_path: Path) -> None:
    src = tmp_path / "fat"
    src.mkdir()
    # One file just over 5 MiB
    (src / "blob.bin").write_bytes(b"a" * (5 * 1024 * 1024 + 1))
    dest = tmp_path / "dest"
    with pytest.raises(ValueError, match="tree too large"):
        _copy_local(src, dest, _FetchBudget())


def test_import_local_respects_fetch_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import cli.common as common
    import cli.import_cmd as import_cmd

    monkeypatch.setattr(common, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(import_cmd, "CACHE_DIR", tmp_path / "cache")

    src = tmp_path / "src"
    src.mkdir()
    for i in range(MAX_FETCH_FILES + 5):
        (src / f"n{i}.md").write_text("# x\n", encoding="utf-8")
    with pytest.raises(ValueError, match="too many files"):
        import_from_url(str(src))
