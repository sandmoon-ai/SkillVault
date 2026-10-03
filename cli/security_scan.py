from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cli.common import is_skillvault_sidecar, load_yaml, read_frontmatter

RULES_PATH = Path(__file__).resolve().parent / "security_rules.yaml"
REPORT_JSON = "_skillvault_security.json"
REPORT_MD = "_skillvault_security.md"


@dataclass
class Finding:
    rule_id: str
    severity: str  # critical | warn | info
    path: str
    message: str
    excerpt: str = ""


@dataclass
class ScanReport:
    verdict: str  # PASS | PASS_WITH_WARNINGS | FAIL
    root: str
    rules_version: str
    scanned_at: str
    counts: dict[str, int] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    content_fingerprint: str = ""

    @property
    def ok_to_apply(self) -> bool:
        return self.verdict != "FAIL"


def content_fingerprint(root: Path) -> str:
    """Stable hash of skill tree files (excludes SkillVault sidecars)."""
    root = root.resolve()
    digest = hashlib.sha256()
    files = sorted(
        p
        for p in root.rglob("*")
        if p.is_file() and not is_skillvault_sidecar(p.name)
    )
    for path in files:
        rel = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(rel)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def load_rules() -> dict[str, Any]:
    return load_yaml(RULES_PATH)


def _rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _is_text(path: Path, rules: dict[str, Any]) -> bool:
    ext = path.suffix.lower()
    return ext in set(rules.get("text_extensions") or []) or ext == ""


def _read_text(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in data[:8192]:
        return None
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return None


def _add(
    findings: list[Finding],
    *,
    rule_id: str,
    severity: str,
    path: str,
    message: str,
    excerpt: str = "",
) -> None:
    findings.append(
        Finding(
            rule_id=rule_id,
            severity=severity,
            path=path,
            message=message,
            excerpt=excerpt[:200],
        )
    )


def _match_patterns(
    findings: list[Finding],
    *,
    patterns: list[dict[str, Any]],
    text: str,
    rel: str,
) -> None:
    for pat in patterns:
        regex = pat.get("regex") or ""
        if not regex:
            continue
        m = re.search(regex, text)
        if m:
            _add(
                findings,
                rule_id=str(pat.get("id") or "pattern"),
                severity=str(pat.get("severity") or "warn"),
                path=rel,
                message=f"Matched pattern {pat.get('id')}",
                excerpt=m.group(0),
            )


def scan_tree(root: Path) -> ScanReport:
    root = root.resolve()
    rules = load_rules()
    findings: list[Finding] = []
    skip = set(rules.get("skip_names") or [])
    limits = rules.get("limits") or {}
    max_file = int(limits.get("max_file_bytes") or 524288)
    max_files = int(limits.get("max_files") or 200)
    max_tree = int(limits.get("max_tree_bytes") or 5242880)
    image_ext = set(rules.get("image_extensions") or [])
    archive_ext = set(rules.get("archive_exec_extensions") or [])
    zw = set(int(x) for x in ((rules.get("unicode") or {}).get("zero_width_codepoints") or []))

    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        # Allow nested SKILL.md (fetched subdir)
        nested = sorted(root.rglob("SKILL.md"))
        nested = [p for p in nested if p.name not in skip]
        if not nested:
            _add(
                findings,
                rule_id="skill-md-missing",
                severity="critical",
                path=".",
                message="No SKILL.md found in scan root",
            )
        else:
            skill_md = nested[0]

    license_hit = False
    files: list[Path] = []
    tree_bytes = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name in skip:
            continue
        files.append(path)
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        tree_bytes += size

    if len(files) > max_files:
        _add(
            findings,
            rule_id="size-tree",
            severity="warn",
            path=".",
            message=f"Too many files: {len(files)} > {max_files}",
        )
    if tree_bytes > max_tree:
        _add(
            findings,
            rule_id="size-tree",
            severity="warn",
            path=".",
            message=f"Tree too large: {tree_bytes} bytes > {max_tree}",
        )

    for path in files:
        rel = _rel(root, path)
        ext = path.suffix.lower()
        try:
            size = path.stat().st_size
        except OSError:
            continue

        if path.name.upper().startswith("LICENSE") or path.name.upper() == "LICENCE":
            license_hit = True

        if ext in archive_ext:
            _add(
                findings,
                rule_id="archive-exec",
                severity="warn",
                path=rel,
                message=f"Archive/executable extension: {ext or path.name}",
            )

        if size > max_file:
            sev = "info" if ext in image_ext else "warn"
            _add(
                findings,
                rule_id="binary-opaque",
                severity=sev,
                path=rel,
                message=f"Large file: {size} bytes",
            )
            continue

        if ext in image_ext:
            continue

        text = _read_text(path) if _is_text(path, rules) or size < max_file else None
        if text is None:
            if ext not in image_ext and ext not in archive_ext:
                # opaque binary without known image/archive type
                if b"\x00" in path.read_bytes()[:8192]:
                    _add(
                        findings,
                        rule_id="binary-opaque",
                        severity="warn",
                        path=rel,
                        message="Non-text / binary content",
                    )
            continue

        if path.name.upper().startswith("LICENSE") or "license" in text[:500].lower():
            license_hit = True

        for cp in zw:
            if chr(cp) in text:
                _add(
                    findings,
                    rule_id="unicode-obfuscation",
                    severity="critical",
                    path=rel,
                    message=f"Zero-width / invisible Unicode U+{cp:04X}",
                )
                break

        _match_patterns(
            findings,
            patterns=list(rules.get("secret_patterns") or []),
            text=text,
            rel=rel,
        )
        _match_patterns(
            findings,
            patterns=list(rules.get("script_danger_patterns") or []),
            text=text,
            rel=rel,
        )
        _match_patterns(
            findings,
            patterns=list(rules.get("exfil_patterns") or []),
            text=text,
            rel=rel,
        )
        _match_patterns(
            findings,
            patterns=list(rules.get("path_escape_patterns") or []),
            text=text,
            rel=rel,
        )
        _match_patterns(
            findings,
            patterns=list(rules.get("agent_config_patterns") or []),
            text=text,
            rel=rel,
        )
        _match_patterns(
            findings,
            patterns=list(rules.get("prompt_injection_patterns") or []),
            text=text,
            rel=rel,
        )

        if path.name == "SKILL.md":
            meta, _ = read_frontmatter(path)
            tools = meta.get("allowed-tools")
            if isinstance(tools, str) and ("*" in tools or tools.strip() in {"all", "ANY"}):
                _add(
                    findings,
                    rule_id="allowed-tools-broad",
                    severity="warn",
                    path=rel,
                    message=f"Broad allowed-tools: {tools}",
                    excerpt=tools,
                )

    if not license_hit:
        _add(
            findings,
            rule_id="license-unknown",
            severity="warn",
            path=".",
            message="No LICENSE file or license cue detected",
        )

    counts = {"critical": 0, "warn": 0, "info": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1

    if counts.get("critical", 0) > 0:
        verdict = "FAIL"
    elif counts.get("warn", 0) > 0:
        verdict = "PASS_WITH_WARNINGS"
    else:
        verdict = "PASS"

    fp = content_fingerprint(root)
    return ScanReport(
        verdict=verdict,
        root=str(root),
        rules_version=str(rules.get("version") or "unknown"),
        scanned_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        counts=counts,
        findings=findings,
        content_fingerprint=fp,
    )


def write_reports(root: Path, report: ScanReport) -> tuple[Path, Path]:
    root = root.resolve()
    json_path = root / REPORT_JSON
    md_path = root / REPORT_MD
    if not report.content_fingerprint:
        report.content_fingerprint = content_fingerprint(root)
    payload = {
        "verdict": report.verdict,
        "root": report.root,
        "rules_version": report.rules_version,
        "scanned_at": report.scanned_at,
        "content_fingerprint": report.content_fingerprint,
        "counts": report.counts,
        "findings": [asdict(f) for f in report.findings],
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# SkillVault security scan",
        "",
        f"- **Verdict:** `{report.verdict}`",
        f"- **Root:** `{report.root}`",
        f"- **Rules version:** `{report.rules_version}`",
        f"- **Scanned at:** `{report.scanned_at}`",
        f"- **Content fingerprint:** `{report.content_fingerprint}`",
        f"- **Counts:** critical={report.counts.get('critical', 0)}, "
        f"warn={report.counts.get('warn', 0)}, info={report.counts.get('info', 0)}",
        "",
        "## Findings",
        "",
    ]
    if not report.findings:
        lines.append("_No findings._")
    else:
        for f in report.findings:
            lines.append(f"### `{f.severity}` — {f.rule_id}")
            lines.append(f"- Path: `{f.path}`")
            lines.append(f"- {f.message}")
            if f.excerpt:
                lines.append(f"- Excerpt: `{f.excerpt}`")
            lines.append("")
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return json_path, md_path


def load_report(root: Path) -> ScanReport | None:
    path = root.resolve() / REPORT_JSON
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    findings = [Finding(**f) for f in data.get("findings") or []]
    return ScanReport(
        verdict=str(data.get("verdict") or "FAIL"),
        root=str(data.get("root") or root),
        rules_version=str(data.get("rules_version") or ""),
        scanned_at=str(data.get("scanned_at") or ""),
        counts=dict(data.get("counts") or {}),
        findings=findings,
        content_fingerprint=str(data.get("content_fingerprint") or ""),
    )


def require_report_for_apply(
    root: Path, *, accept_security_risks: bool = False
) -> ScanReport:
    root = root.resolve()
    report = load_report(root)
    if report is None:
        raise ValueError(
            f"Missing security report under {root}. Run: py cli/sv.py security-scan {root}"
        )
    if not report.content_fingerprint:
        raise ValueError(
            f"Security report under {root} is missing content_fingerprint. "
            f"Re-run: py cli/sv.py security-scan {root}"
        )
    current = content_fingerprint(root)
    if report.content_fingerprint != current:
        raise ValueError(
            f"Security report is stale (source tree changed under {root}). "
            f"Re-run: py cli/sv.py security-scan {root}"
        )
    if not report.ok_to_apply and not accept_security_risks:
        raise ValueError(
            f"Security verdict is {report.verdict}. Fix findings or pass "
            "--accept-security-risks (requires documented Gate B acceptance)."
        )
    return report
