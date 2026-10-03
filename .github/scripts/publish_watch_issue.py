#!/usr/bin/env python3
"""Create or comment on a watch Issue from a JSON report (stdlib + gh CLI)."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _gh(*args: str) -> str:
    cmd = ["gh", *args]
    return subprocess.check_output(cmd, text=True, encoding="utf-8").strip()


def _find_open_issue(label: str) -> str | None:
    out = _gh(
        "issue",
        "list",
        "--label",
        label,
        "--state",
        "open",
        "--json",
        "number,title",
        "--jq",
        ".[0].number // empty",
    )
    return out or None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument(
        "--drift-key",
        default="has_drift",
        help="JSON boolean key that means 'open an issue'",
    )
    args = parser.parse_args()

    data = json.loads(args.report.read_text(encoding="utf-8"))
    if not data.get(args.drift_key):
        print(f"No drift ({args.drift_key}=false); skipping issue.")
        return 0

    run_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    actions_link = f"{run_url}/{repo}/actions/runs/{run_id}" if repo and run_id else "(local)"

    body_lines = [
        f"Automated watch report ({datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')})",
        "",
        f"Actions run: {actions_link}",
        "",
        "```json",
        json.dumps(data, indent=2, ensure_ascii=False)[:15000],
        "```",
        "",
        "### Next",
        "- Review diffs / fingerprints",
        "- Decide adopt / ignore",
        "- Do **not** expect this job to apply changes automatically",
    ]
    if args.label == "security-rules":
        body_lines.extend(
            [
                "",
                "### Adoption checklist",
                "- [ ] Read upstream change notes",
                "- [ ] Decide: adopt / partial / ignore (note why)",
                "- [ ] If adopt: PR updating `cli/security_rules.yaml` (+ tests)",
                "- [ ] Update `registry/security_sources.yaml` `last_seen`",
                "- [ ] Optional: re-run `sv security-scan` on `vault/imported/**`",
            ]
        )
    body = "\n".join(body_lines)

    existing = _find_open_issue(args.label)
    if existing:
        _gh("issue", "comment", existing, "--body", body)
        print(f"Commented on existing issue #{existing}")
    else:
        url = _gh(
            "issue",
            "create",
            "--title",
            args.title,
            "--label",
            args.label,
            "--body",
            body,
        )
        print(f"Created issue: {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
