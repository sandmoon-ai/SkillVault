from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from cli.common import (
    CACHE_DIR,
    REGISTRY_PATH,
    VAULT_IMPORTED,
    dump_yaml,
    is_skillvault_sidecar,
    load_yaml,
    read_frontmatter,
    validate_category,
    validate_skill_name,
)
from cli.security_scan import require_report_for_apply, scan_tree, write_reports

GITHUB_TREE_RE = re.compile(
    r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/tree/(?P<ref>[^/]+)(?:/(?P<path>.*))?$"
)
GITHUB_BLOB_RE = re.compile(
    r"^https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/blob/(?P<ref>[^/]+)/(?P<path>.+)$"
)
GITHUB_RAW_RE = re.compile(
    r"^https?://raw\.githubusercontent\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/(?P<ref>[^/]+)/(?P<path>.+)$"
)

# Hard stop at fetch time (scan also warns at the same thresholds).
MAX_FETCH_FILES = 200
MAX_FETCH_BYTES = 5 * 1024 * 1024  # 5 MiB


@dataclass
class FetchResult:
    cache_dir: Path
    source_url: str
    ref: str | None
    upstream_path: str | None
    skill_md: Path | None
    summary: dict


@dataclass
class _FetchBudget:
    """Track download/copy size; raise before a huge tree enters cache."""

    files: int = 0
    nbytes: int = 0
    max_files: int = MAX_FETCH_FILES
    max_bytes: int = MAX_FETCH_BYTES

    def add(self, *, n_files: int = 0, n_bytes: int = 0) -> None:
        self.files += n_files
        self.nbytes += n_bytes
        if self.files > self.max_files:
            raise ValueError(
                f"Fetch aborted: too many files ({self.files} > {self.max_files}). "
                "Narrow the GitHub tree path or raise limits only after review."
            )
        if self.nbytes > self.max_bytes:
            raise ValueError(
                f"Fetch aborted: tree too large ({self.nbytes} bytes > {self.max_bytes}). "
                "Narrow the GitHub tree path or raise limits only after review."
            )


def _github_headers(*, json_api: bool = False) -> dict[str, str]:
    headers = {"User-Agent": "skillvault"}
    if json_api:
        headers["Accept"] = "application/vnd.github+json"
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _http_get_json(url: str) -> dict | list:
    req = urllib.request.Request(url, headers=_github_headers(json_api=True))
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _http_download(url: str, dest: Path, budget: _FetchBudget) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers=_github_headers())
    with urllib.request.urlopen(req, timeout=60) as resp, dest.open("wb") as out:
        shutil.copyfileobj(resp, out)
    size = dest.stat().st_size
    budget.add(n_files=1, n_bytes=size)


def _parse_github(url: str) -> tuple[str, str, str, str | None] | None:
    for pattern in (GITHUB_TREE_RE, GITHUB_BLOB_RE, GITHUB_RAW_RE):
        m = pattern.match(url.rstrip("/"))
        if m:
            path = m.groupdict().get("path") or None
            return m.group("owner"), m.group("repo"), m.group("ref"), path
    return None


def _fetch_github_dir(
    owner: str,
    repo: str,
    ref: str,
    path: str | None,
    dest: Path,
    budget: _FetchBudget | None = None,
) -> None:
    budget = budget or _FetchBudget()
    api = (
        f"https://api.github.com/repos/{owner}/{repo}/contents/"
        f"{urllib.parse.quote(path or '')}?ref={urllib.parse.quote(ref)}"
    )
    data = _http_get_json(api)
    if isinstance(data, dict) and data.get("type") == "file":
        # Single file URL pointed at a file
        name = data["name"]
        announced = int(data.get("size") or 0)
        if announced and budget.nbytes + announced > budget.max_bytes:
            budget.add(n_bytes=announced)  # raises with consistent message
        _http_download(data["download_url"], dest / name, budget)
        return
    if not isinstance(data, list):
        raise RuntimeError(f"Unexpected GitHub API response for {api}")

    dest.mkdir(parents=True, exist_ok=True)
    for item in data:
        rel = item["name"]
        target = dest / rel
        if item["type"] == "file":
            announced = int(item.get("size") or 0)
            if announced and budget.nbytes + announced > budget.max_bytes:
                budget.add(n_bytes=announced)  # raises
            _http_download(item["download_url"], target, budget)
        elif item["type"] == "dir":
            child_path = "/".join(p for p in (path, rel) if p)
            _fetch_github_dir(owner, repo, ref, child_path, target, budget)


def _enforce_tree_budget(root: Path, budget: _FetchBudget | None = None) -> _FetchBudget:
    """Count files already on disk (local copy path)."""
    budget = budget or _FetchBudget()
    for path in root.rglob("*"):
        if not path.is_file() or is_skillvault_sidecar(path.name):
            continue
        budget.add(n_files=1, n_bytes=path.stat().st_size)
    return budget


def _copy_local(src: Path, dest: Path, budget: _FetchBudget | None = None) -> None:
    if src.is_file():
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest / src.name)
        _enforce_tree_budget(dest, budget)
        return
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    _enforce_tree_budget(dest, budget)


def _find_skill_md(root: Path) -> Path | None:
    direct = root / "SKILL.md"
    if direct.is_file():
        return direct
    matches = sorted(root.rglob("SKILL.md"))
    return matches[0] if matches else None


def _summarize(cache_dir: Path, skill_md: Path | None) -> dict:
    files = sorted(
        str(p.relative_to(cache_dir)).replace("\\", "/")
        for p in cache_dir.rglob("*")
        if p.is_file()
    )
    meta = {}
    if skill_md and skill_md.is_file():
        meta, _ = read_frontmatter(skill_md)
    scripts = [f for f in files if "/scripts/" in f or f.startswith("scripts/")]
    return {
        "files": files,
        "frontmatter": meta,
        "scripts": scripts,
        "has_skill_md": skill_md is not None,
    }


def import_from_url(
    url: str,
    *,
    name: str | None = None,
    ref: str | None = None,
    apply: bool = False,
    accept_security_risks: bool = False,
    category: str = "inbox",
) -> FetchResult:
    cache_id = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
    cache_dir = CACHE_DIR / "import" / cache_id
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    upstream_path: str | None = None
    used_ref = ref
    source_url = url

    budget = _FetchBudget()
    local = Path(url)
    if local.exists():
        _copy_local(local, cache_dir, budget)
        used_ref = used_ref or "local"
    else:
        gh = _parse_github(url)
        if not gh:
            raise ValueError(
                "Unsupported URL. Provide a GitHub tree/blob/raw URL or a local path."
            )
        owner, repo, url_ref, path = gh
        used_ref = ref or url_ref
        upstream_path = path
        try:
            _fetch_github_dir(owner, repo, used_ref, path, cache_dir, budget)
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Failed to fetch {url}: HTTP {exc.code}") from exc

    skill_md = _find_skill_md(cache_dir)
    # If only a single markdown file without SKILL.md, treat it as candidate body.
    if skill_md is None:
        md_files = sorted(cache_dir.glob("*.md"))
        if len(md_files) == 1:
            skill_md = md_files[0]

    summary = _summarize(cache_dir, skill_md if skill_md and skill_md.name == "SKILL.md" else None)
    summary_path = cache_dir / "_skillvault_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    scan_root = skill_md.parent if skill_md and skill_md.name == "SKILL.md" else cache_dir
    report = scan_tree(scan_root)
    write_reports(scan_root, report)
    summary["security_verdict"] = report.verdict
    summary["security_counts"] = report.counts
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    result = FetchResult(
        cache_dir=cache_dir,
        source_url=source_url,
        ref=used_ref,
        upstream_path=upstream_path,
        skill_md=skill_md,
        summary=summary,
    )

    if apply:
        require_report_for_apply(scan_root, accept_security_risks=accept_security_risks)
        if not name:
            if skill_md and skill_md.name == "SKILL.md":
                meta, _ = read_frontmatter(skill_md)
                name = str(meta.get("name") or skill_md.parent.name)
            elif skill_md:
                name = skill_md.stem.replace("_", "-").lower()
            else:
                raise ValueError("--apply requires --name when SKILL.md is missing")
        apply_import(result, name=name, category=category or "inbox")

    return result


def apply_import(result: FetchResult, *, name: str, category: str = "inbox") -> Path:
    validate_skill_name(name)
    validate_category(category)
    dest = VAULT_IMPORTED / category / name
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    # Copy fetched files except SkillVault sidecars
    for item in result.cache_dir.rglob("*"):
        if is_skillvault_sidecar(item.name):
            continue
        rel = item.relative_to(result.cache_dir)
        target = dest / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)

    # Normalize single markdown into SKILL.md if needed
    skill_md = dest / "SKILL.md"
    if not skill_md.is_file():
        md_files = sorted(dest.glob("*.md"))
        if len(md_files) == 1 and md_files[0].name != "SOURCE.md":
            content = md_files[0].read_text(encoding="utf-8")
            if not content.startswith("---"):
                content = (
                    f"---\nname: {name}\n"
                    f"description: Imported skill {name}. Review and improve this description.\n"
                    f"---\n\n{content}"
                )
            skill_md.write_text(content, encoding="utf-8")
            if md_files[0].name != "SKILL.md":
                md_files[0].unlink()

    source_md = dest / "SOURCE.md"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    source_md.write_text(
        "\n".join(
            [
                "# Source",
                "",
                f"- Upstream: {result.source_url}",
                f"- Ref: {result.ref or 'unknown'}",
                f"- Path: {result.upstream_path or '.'}",
                f"- Imported: {now}",
                "- License: unknown",
                "- Notes: Raw apply via `sv import --apply`. Review/normalize with meta-skills/import-from-url.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    _upsert_registry(
        name=name,
        url=result.source_url,
        ref=result.ref or "main",
        path=result.upstream_path,
        license_name="unknown",
        last_synced=now,
        category=category,
    )
    return dest


def _upsert_registry(
    *,
    name: str,
    url: str,
    ref: str,
    path: str | None,
    license_name: str,
    last_synced: str,
    category: str = "inbox",
) -> None:
    data = load_yaml(REGISTRY_PATH)
    skills = list(data.get("skills") or [])
    entry = {
        "name": name,
        "url": url,
        "ref": ref,
        "path": path,
        "category": category,
        "local": f"vault/imported/{category}/{name}",
        "license": license_name,
        "last_synced": last_synced,
    }
    replaced = False
    for idx, existing in enumerate(skills):
        if existing.get("name") == name:
            skills[idx] = entry
            replaced = True
            break
    if not replaced:
        skills.append(entry)
    dump_yaml(REGISTRY_PATH, {"skills": skills})


def print_import_summary(result: FetchResult) -> str:
    lines = [
        f"Cached at: {result.cache_dir}",
        f"Source: {result.source_url}",
        f"Ref: {result.ref}",
        f"Upstream path: {result.upstream_path or '.'}",
        f"Has SKILL.md: {result.summary.get('has_skill_md')}",
        "Files:",
    ]
    for f in result.summary.get("files", []):
        lines.append(f"  - {f}")
    meta = result.summary.get("frontmatter") or {}
    if meta:
        lines.append(f"Frontmatter name: {meta.get('name')}")
        lines.append(f"Frontmatter description: {meta.get('description')}")
    verdict = result.summary.get("security_verdict")
    if verdict:
        lines.append(f"Security verdict: {verdict}")
        lines.append(
            f"Security report: {result.cache_dir / '_skillvault_security.md'} "
            f"(or next to SKILL.md if nested)"
        )
    lines.append(
        "Next: review security report + convert with meta-skills/import-from-url, "
        "or re-run with --apply --name <name> after Gate B."
    )
    return "\n".join(lines)
