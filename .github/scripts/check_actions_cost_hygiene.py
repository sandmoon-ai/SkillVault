#!/usr/bin/env python3
"""CI 成本卫生检查（仅用标准库，可在 setup 之前跑）。

规则（预防「测完残留一直占存储」）：
1. 使用 upload-artifact 的步骤必须声明 retention-days，且 <= MAX_RETENTION_DAYS
2. 禁止在本仓库 workflow 里直接使用大型/昂贵 runner 标签（可按需改白名单）
3. 使用 actions/cache 时必须带 key（避免无效或失控缓存）
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
MAX_RETENTION_DAYS = 7

# 标准免费路径之外的 runner（公开仓用这些也会单独计费）
EXPENSIVE_RUNNER_PATTERNS = [
    re.compile(r"runs-on:\s*windows-latest", re.I),
    re.compile(r"runs-on:\s*macos-", re.I),
    re.compile(r"runs-on:\s*.*larger", re.I),
    re.compile(r"runs-on:\s*.*\d+-core", re.I),
]

# 允许的例外：在文件顶部加 "# cost-allow: windows-latest" 等（整行注释）
ALLOW_COMMENT = re.compile(r"#\s*cost-allow:\s*(\S+)", re.I)


def _iter_workflow_files() -> list[Path]:
    if not WORKFLOWS.is_dir():
        return []
    return sorted(
        list(WORKFLOWS.glob("*.yml")) + list(WORKFLOWS.glob("*.yaml"))
    )


def _allowed_tokens(text: str) -> set[str]:
    return {m.group(1).lower() for m in ALLOW_COMMENT.finditer(text)}


def check_upload_artifact(path: Path, text: str) -> list[str]:
    """粗粒度扫描：出现 upload-artifact 的 with 块里要有 retention-days。"""
    errors: list[str] = []
    # 按 uses: 行切开，检查含 upload-artifact 的片段
    parts = re.split(r"(?m)^(?=\s*-\s*uses:)", text)
    for part in parts:
        if "upload-artifact" not in part:
            continue
        if re.search(r"retention-days\s*:", part) is None:
            errors.append(
                f"{path.name}: 使用 upload-artifact 必须设置 retention-days"
                f"（建议 <= {MAX_RETENTION_DAYS}）"
            )
            continue
        m = re.search(r"retention-days\s*:\s*(\d+)", part)
        if m and int(m.group(1)) > MAX_RETENTION_DAYS:
            errors.append(
                f"{path.name}: retention-days={m.group(1)} 超过上限"
                f" {MAX_RETENTION_DAYS}；请缩短保留期或说明例外"
            )
    return errors


def check_cache(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    parts = re.split(r"(?m)^(?=\s*-\s*uses:)", text)
    for part in parts:
        if "actions/cache@" not in part and "actions/cache/restore@" not in part:
            continue
        if re.search(r"(?m)^\s*key\s*:", part) is None:
            errors.append(f"{path.name}: 使用 actions/cache 时必须设置 key")
    return errors


def check_expensive_runners(path: Path, text: str) -> list[str]:
    allowed = _allowed_tokens(text)
    errors: list[str] = []
    for pat in EXPENSIVE_RUNNER_PATTERNS:
        for m in pat.finditer(text):
            line = m.group(0).strip()
            # 从 runs-on 值判断是否已 allow
            token = line.split(":", 1)[-1].strip().strip("'\"")
            if token.lower() in allowed or "windows-latest" in allowed and "windows" in token.lower():
                continue
            if "macos" in token.lower() and any(a.startswith("macos") for a in allowed):
                continue
            errors.append(
                f"{path.name}: 检测到可能产生额外费用的 runner `{token}`。"
                f" 本仓库默认只用 ubuntu-latest。"
                f" 若确实需要，在文件顶部加注释"
                f" `# cost-allow: {token}` 并在 PR 说明理由。"
            )
    return errors


def main() -> int:
    files = _iter_workflow_files()
    if not files:
        print("No workflows found; skip.")
        return 0

    errors: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        errors.extend(check_upload_artifact(path, text))
        errors.extend(check_cache(path, text))
        errors.extend(check_expensive_runners(path, text))

    if errors:
        print("Actions 成本卫生检查失败：")
        for e in errors:
            print(f"  - {e}")
        print(
            "\n说明见 docs/ci.md「成本与存储防护」。"
            " 公开仓标准 Ubuntu 分钟免费，但 artifact/cache 仍可能占存储。"
        )
        return 1

    print(f"Actions 成本卫生检查通过（扫描 {len(files)} 个 workflow）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
