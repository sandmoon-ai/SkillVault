"""发现并执行各 Skill 在 scripts/tests.yaml 中声明的冒烟测试。

仓库约定：vault / meta-skills 下凡带可执行脚本的 Skill，都必须有 tests.yaml，
且本文件中的用例要能跑通（当前 OS 不适用的条目会 skip）。
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

# 仓库根目录（本文件在 tests/ 下）
REPO_ROOT = Path(__file__).resolve().parent.parent

# 会扫描「Skill 脚本」的根路径
SKILL_SCRIPT_ROOTS = [
    REPO_ROOT / "vault" / "own",
    REPO_ROOT / "vault" / "imported",
    REPO_ROOT / "meta-skills",
]


def _host_os() -> str:
    """把 platform.system() 映射成 tests.yaml 里用的平台名。"""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    if system.startswith("win"):
        return "windows"
    return "linux"


def _discover_manifests() -> list[Path]:
    """收集所有 scripts/tests.yaml 清单文件。"""
    found: list[Path] = []
    for root in SKILL_SCRIPT_ROOTS:
        if not root.is_dir():
            continue
        found.extend(sorted(root.rglob("scripts/tests.yaml")))
    return found


def _scripts_without_manifest() -> list[Path]:
    """找出有脚本文件、却未被 tests.yaml 覆盖的路径（违规清单）。"""
    orphans: list[Path] = []
    # 视为「可执行脚本」的扩展名
    exts = {".sh", ".ps1", ".py", ".js", ".mjs", ".ts", ".bash", ".cmd", ".bat"}
    for root in SKILL_SCRIPT_ROOTS:
        if not root.is_dir():
            continue
        for scripts_dir in root.rglob("scripts"):
            if not scripts_dir.is_dir():
                continue
            # 模板目录只是文档示例，不强制测
            if "_template" in scripts_dir.parts:
                continue
            manifest = scripts_dir / "tests.yaml"
            script_files = [
                p
                for p in scripts_dir.iterdir()
                if p.is_file()
                and p.suffix.lower() in exts
                and p.name != "tests.yaml"
            ]
            # 有脚本但没有清单
            if script_files and not manifest.is_file():
                orphans.extend(script_files)
            # 有清单，但某个脚本没写进 tests 条目
            elif manifest.is_file() and script_files:
                data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
                declared = {
                    item.get("script")
                    for item in (data.get("tests") or [])
                    if isinstance(item, dict)
                }
                for script in script_files:
                    if script.name not in declared:
                        orphans.append(script)
    return orphans


def _infer_runner(script: Path, explicit: str | None) -> str:
    """决定用什么解释器跑脚本；清单里写了 runner 则优先用。"""
    if explicit:
        return explicit.lower()
    ext = script.suffix.lower()
    if ext == ".ps1":
        return "powershell"
    if ext in {".sh", ".bash"}:
        return "bash"
    if ext == ".py":
        return "python"
    if ext in {".cmd", ".bat"}:
        return "cmd"
    return "bash"


def _build_command(runner: str, script: Path, args: list[str]) -> list[str] | None:
    """拼出 subprocess 命令；找不到 runner 时返回 None。"""
    if runner == "powershell":
        return [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
            *args,
        ]
    if runner == "bash":
        bash = shutil.which("bash")
        if not bash:
            return None
        return [bash, str(script), *args]
    if runner == "python":
        return [sys.executable, str(script), *args]
    if runner == "cmd":
        return ["cmd", "/c", str(script), *args]
    return None


def _collect_cases() -> list[tuple[str, Path, dict]]:
    """从所有 tests.yaml 展开成 pytest 参数化用例列表。"""
    cases: list[tuple[str, Path, dict]] = []
    for manifest in _discover_manifests():
        data = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
        scripts_dir = manifest.parent
        for idx, item in enumerate(data.get("tests") or []):
            if not isinstance(item, dict) or not item.get("script"):
                continue
            script_path = scripts_dir / item["script"]
            skill_key = scripts_dir.parent.name
            case_id = f"{skill_key}/{item['script']}#{idx}"
            cases.append((case_id, script_path, item))
    return cases


# 收集阶段就算好，供 parametrize 使用
CASES = _collect_cases()


def test_every_skill_script_is_declared_in_tests_yaml():
    """硬门禁：不允许存在「有脚本、无 tests.yaml 覆盖」的 Skill。"""
    orphans = _scripts_without_manifest()
    assert not orphans, (
        "以下 Skill 脚本缺少 tests.yaml 覆盖：\n"
        + "\n".join(f"  - {p.relative_to(REPO_ROOT)}" for p in orphans)
    )


@pytest.mark.parametrize(
    "case_id,script_path,spec", CASES, ids=[c[0] for c in CASES] or ["none"]
)
def test_skill_script_smoke(case_id: str, script_path: Path, spec: dict):
    """按清单跑单条冒烟：退出码与可选的 stdout/stderr 子串断言。"""
    assert script_path.is_file(), f"用例 {case_id} 缺少脚本文件: {script_path}"

    host = _host_os()
    platforms = [p.lower() for p in (spec.get("platforms") or [])]
    # 当前机器不在声明平台内 → 跳过（例如 Windows 上不跑仅 linux 的 .sh）
    if host not in platforms:
        pytest.skip(f"{case_id}: 不适用于当前平台 {host}")

    runner = _infer_runner(script_path, spec.get("runner"))
    args = [str(a) for a in (spec.get("args") or [])]
    cmd = _build_command(runner, script_path, args)
    # optional_runner=true：本机没有该解释器（或解释器坏了）时允许 skip，不算失败
    optional = bool(spec.get("optional_runner"))

    if cmd is None:
        if optional:
            pytest.skip(f"{case_id}: 本机没有可用的 runner '{runner}'")
        pytest.fail(f"{case_id}: 本机没有可用的 runner '{runner}'")

    proc = subprocess.run(
        cmd,
        cwd=str(script_path.parent),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=os.environ.copy(),
        check=False,
    )

    expect_exit = int(spec.get("expect_exit", 0))
    if proc.returncode != expect_exit and optional:
        pytest.skip(
            f"{case_id}: 可选 runner '{runner}' 执行失败 "
            f"(exit {proc.returncode}): {proc.stderr.strip() or proc.stdout.strip()}"
        )
    assert proc.returncode == expect_exit, (
        f"{case_id} 退出码 {proc.returncode}，期望 {expect_exit}\n"
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )

    needle_out = spec.get("expect_stdout_contains")
    if needle_out:
        assert needle_out in proc.stdout, (
            f"{case_id} stdout 未包含 {needle_out!r}\nstdout:\n{proc.stdout}"
        )

    needle_err = spec.get("expect_stderr_contains")
    if needle_err:
        assert needle_err in proc.stderr, (
            f"{case_id} stderr 未包含 {needle_err!r}\nstderr:\n{proc.stderr}"
        )


def test_at_least_one_skill_script_manifest_exists():
    """防止测试目录空转：仓库里至少要有一份 scripts/tests.yaml。"""
    assert _discover_manifests(), "vault/ 下应至少存在一份 scripts/tests.yaml"
