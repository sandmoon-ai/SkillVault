from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from cli.common import REGISTRY_PATH, VAULT_IMPORTED, dump_yaml, load_yaml
from cli.import_cmd import import_from_url


def _dir_diff(left: Path, right: Path) -> list[str]:
    """Return relative paths that differ or exist on only one side."""
    diffs: list[str] = []
    if not left.exists() or not right.exists():
        return ["<missing-side>"]

    skip = {
        "SOURCE.md",
        "_skillvault_summary.json",
        "_skillvault_security.json",
        "_skillvault_security.md",
    }
    left_files = {
        p.relative_to(left).as_posix()
        for p in left.rglob("*")
        if p.is_file() and p.name not in skip
    }
    right_files = {
        p.relative_to(right).as_posix()
        for p in right.rglob("*")
        if p.is_file() and p.name not in skip
    }

    for rel in sorted(left_files | right_files):
        lp = left / rel
        rp = right / rel
        if not lp.exists():
            diffs.append(f"only-in-cache: {rel}")
        elif not rp.exists():
            diffs.append(f"only-in-vault: {rel}")
        elif not _files_equal(lp, rp):
            diffs.append(f"changed: {rel}")
    return diffs


def _files_equal(left: Path, right: Path) -> bool:
    """Byte-compare; for text, ignore CRLF vs LF to avoid Windows false drift."""
    try:
        lb = left.read_bytes()
        rb = right.read_bytes()
    except OSError:
        return False
    if lb == rb:
        return True
    # Heuristic: treat as text if no NUL in either
    if b"\x00" in lb[:8192] or b"\x00" in rb[:8192]:
        return False
    return lb.replace(b"\r\n", b"\n").replace(b"\r", b"\n") == rb.replace(
        b"\r\n", b"\n"
    ).replace(b"\r", b"\n")


def sync_skills(names: list[str] | None, *, all_skills: bool = False, apply: bool = False) -> list[str]:
    data = load_yaml(REGISTRY_PATH)
    skills = list(data.get("skills") or [])
    if not skills:
        return ["Registry is empty. Import a skill first."]

    if all_skills:
        selected = skills
    else:
        if not names:
            raise ValueError("Provide skill name(s) or --all")
        wanted = set(names)
        selected = [s for s in skills if s.get("name") in wanted]
        missing = wanted - {s.get("name") for s in selected}
        if missing:
            raise FileNotFoundError(f"Not in registry: {', '.join(sorted(missing))}")

    reports: list[str] = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for entry in selected:
        name = entry["name"]
        url = entry["url"]
        ref = entry.get("ref") or "main"
        result = import_from_url(url, name=name, ref=ref, apply=False)
        category = entry.get("category") or "inbox"
        local = VAULT_IMPORTED / category / name
        diffs = _dir_diff(result.cache_dir, local) if local.exists() else ["new-skill"]
        report = [f"## {name}", f"cache: {result.cache_dir}", f"diff count: {len(diffs)}"]
        report.extend(f"  - {d}" for d in diffs[:50])
        if apply:
            # Preserve SOURCE.md notes if present, then refresh files from cache.
            old_source = None
            source_path = local / "SOURCE.md"
            if source_path.is_file():
                old_source = source_path.read_text(encoding="utf-8")
            if local.exists():
                shutil.rmtree(local)
            local.mkdir(parents=True)
            for item in result.cache_dir.rglob("*"):
                if item.name == "_skillvault_summary.json":
                    continue
                rel = item.relative_to(result.cache_dir)
                target = local / rel
                if item.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target)
            if old_source:
                # Refresh timestamp line if present
                lines = old_source.splitlines()
                refreshed = []
                for line in lines:
                    if line.startswith("- Imported:") or line.startswith("- Last synced:"):
                        refreshed.append(f"- Last synced: {now}")
                    else:
                        refreshed.append(line)
                if not any(l.startswith("- Last synced:") for l in refreshed):
                    refreshed.append(f"- Last synced: {now}")
                source_path.write_text("\n".join(refreshed) + "\n", encoding="utf-8")
            else:
                source_path.write_text(
                    f"# Source\n\n- Upstream: {url}\n- Ref: {ref}\n- Last synced: {now}\n",
                    encoding="utf-8",
                )
            entry["last_synced"] = now
            report.append("applied: yes")
        else:
            report.append("applied: no (pass --apply to update vault/imported)")
        reports.append("\n".join(report))

    if apply:
        dump_yaml(REGISTRY_PATH, {"skills": skills})
    return reports
