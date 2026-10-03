# Skill 脚本测试规范

本仓库硬性要求：**凡 Skill 包内的可执行脚本，合入前必须有对应测试且本地/CI 通过。**

适用范围：

- `vault/own/**/scripts/**`
- `vault/imported/**/scripts/**`（转化时一并补齐；上游无测试则本仓补 smoke）
- 将来若 `meta-skills/**/scripts/**` 出现脚本，同样适用

不在此列：`cli/` 下的 Python（走单元测试 / Phase 4）；纯文档 Skill（无 `scripts/`）无需脚本测试。

## 最低标准

每个脚本至少具备：

1. **可发现**：放在该 Skill 的 `scripts/` 下  
2. **有清单**：同目录 `tests.yaml` 声明如何跑、期望什么  
3. **可自动执行**：`py -m pytest tests/test_skill_scripts.py`（或 `py cli/sv.py` 将来扩展）能跑到  
4. **退出码 0**（除非清单明确期望非零）  
5. **跨平台声明**：`platforms` 标明 `windows` / `linux` / `macos`；当前 OS 不匹配则跳过，不得假装通过后在目标平台从不跑

双平台脚本（`.sh` + `.ps1`）须**各自**有测试条目；不能只测一边。

## `scripts/tests.yaml` 格式

```yaml
tests:
  - script: hello.ps1
    platforms: [windows]
    expect_exit: 0
    expect_stdout_contains: "hello-skillvault: ok"
  - script: hello.sh
    platforms: [linux, macos]
    expect_exit: 0
    expect_stdout_contains: "hello-skillvault: ok"
    # 可选：Windows 上若有 bash（Git Bash）也可测
    # platforms: [linux, macos, windows]
    # runner: bash
```

字段：

| 字段 | 必需 | 说明 |
|------|------|------|
| `script` | 是 | 相对 `scripts/` 的文件名 |
| `platforms` | 是 | 在哪些 OS 上执行 |
| `expect_exit` | 否 | 默认 `0` |
| `expect_stdout_contains` | 否 | 子串断言 |
| `expect_stderr_contains` | 否 | 子串断言 |
| `args` | 否 | 传给脚本的参数列表 |
| `runner` | 否 | `powershell` / `bash` / `python`；默认按扩展名推断 |

## Gate 挂钩

| 时机 | 要求 |
|------|------|
| 自建 Skill 合入 | Gate：有脚本则 `tests.yaml` 齐全且测试绿 |
| 收录转化（Gate B） | 源带脚本 → 转化后补测试；测不过不进 `imported` |
| AI / CLI 安装 | 不替代本规范；安装前建议跑相关 skill 脚本测试 |

## 本地命令

```bash
# 安装测试依赖（一次性）
py -m pip install -e ".[dev]"

# 跑全部 Skill 脚本测试
py -m pytest tests/test_skill_scripts.py -v
```

当前 OS 不支持的脚本条目会以 `skipped` 显示，这是预期行为。
