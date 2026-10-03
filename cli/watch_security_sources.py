"""Security rule source fingerprint watch (M5). Never edits security_rules.yaml."""

from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from cli.common import REPO_ROOT, load_yaml

SOURCES_PATH = REPO_ROOT / "registry" / "security_sources.yaml"


@dataclass
class SourceItem:
    id: str
    status: str  # unchanged | changed | baseline | fetch-failed
    url: str = ""
    kind: str = ""
    last_seen: str = ""
    current: str = ""
    error: str = ""
    notes: str = ""


@dataclass
class SecuritySourcesReport:
    items: list[SourceItem]
    has_changes: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "has_changes": self.has_changes,
            "items": [asdict(i) for i in self.items],
        }


def _http_get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "skillvault-watch"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _fingerprint(entry: dict[str, Any]) -> str:
    kind = str(entry.get("kind") or "")
    url = str(entry.get("url") or "")
    track = str(entry.get("track") or "")

    if kind == "github-release":
        # url like https://api.github.com/repos/OWNER/REPO/releases/latest
        data = json.loads(_http_get(url).decode("utf-8"))
        key = track or "tag_name"
        return str(data.get(key) or "")

    if kind == "raw":
        body = _http_get(url)
        return hashlib.sha256(body).hexdigest()

    if kind == "html":
        text = _http_get(url).decode("utf-8", errors="replace")
        pattern = track or r"v?\d{4}\.\d{2}\.\d{2}"
        m = re.search(pattern, text)
        if not m:
            raise RuntimeError(f"No match for track pattern on {url}")
        return m.group(0) if m.lastindex is None else m.group(1) or m.group(0)

    if kind == "local-file":
        path = Path(url)
        if not path.is_file():
            path = REPO_ROOT / url
        data = path.read_bytes()
        return hashlib.sha256(data).hexdigest()

    if kind == "pin":
        # Manual pin: human bumps track/pin when adopting a new upstream URL/version.
        return str(entry.get("track") or entry.get("pin") or url)

    raise ValueError(f"Unsupported kind: {kind}")


def watch_security_sources(sources_path: Path | None = None) -> SecuritySourcesReport:
    path = sources_path or SOURCES_PATH
    data = load_yaml(path)
    sources = list(data.get("sources") or [])
    items: list[SourceItem] = []
    for entry in sources:
        sid = str(entry.get("id") or "")
        url = str(entry.get("url") or "")
        kind = str(entry.get("kind") or "")
        last = str(entry.get("last_seen") or "")
        notes = str(entry.get("notes") or "")
        try:
            current = _fingerprint(entry)
            if not last:
                status = "baseline"
            elif current != last:
                status = "changed"
            else:
                status = "unchanged"
            items.append(
                SourceItem(
                    id=sid,
                    status=status,
                    url=url,
                    kind=kind,
                    last_seen=last,
                    current=current,
                    notes=notes,
                )
            )
        except Exception as exc:  # noqa: BLE001
            items.append(
                SourceItem(
                    id=sid,
                    status="fetch-failed",
                    url=url,
                    kind=kind,
                    last_seen=last,
                    error=str(exc),
                    notes=notes,
                )
            )

    has_changes = any(i.status == "changed" for i in items)
    return SecuritySourcesReport(items=items, has_changes=has_changes)


def format_security_sources(report: SecuritySourcesReport) -> str:
    lines = [f"has_changes: {report.has_changes}", f"items: {len(report.items)}"]
    for item in report.items:
        lines.append(
            f"- {item.id}: {item.status} last_seen={item.last_seen!r} current={item.current!r}"
        )
        if item.error:
            lines.append(f"  error: {item.error}")
    return "\n".join(lines)


def write_security_json(path: Path, report: SecuritySourcesReport) -> None:
    path.write_text(
        json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
