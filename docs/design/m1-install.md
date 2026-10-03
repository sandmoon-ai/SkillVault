# M1 — 安装闭环设计

**状态：** 已完成（2026-10-03）  

**关联：** [meta-skills/install](../../meta-skills/install/SKILL.md)、[`cli/install_cmd.py`](../../cli/install_cmd.py)、[`adapters/targets.yaml`](../../adapters/targets.yaml)

## 1. 目标

用户或 AI 指定 `--ide` + `--os` 后，能把 vault 内 Skill **稳定安装**到目标 IDE 的 skills 目录：

- 默认 **user**（用户级）  
- **project** 必须显式 `--scope project --project-root`  
- 行为由单测锁定，并由 Windows 上至少两个 IDE 实机确认  

## 2. 行为规格

| 项 | 规格 |
|----|------|
| 源路径 | `vault/{own,imported}/<category>/<name>/` |
| IDE 目标 | `{install_root}/<name>/`（**扁平**，不带 category） |
| 排除文件 | `SOURCE.md`、`.gitkeep`、`tests.yaml` |
| Frontmatter | 按 `adapters/frontmatter.yaml` 对目标 IDE 裁剪；vault 源文件不变 |
| 已存在目标 | 默认 `FileExistsError`；`--force` 覆盖 |
| `--link` | 符号链接（高级）；验收以 copy 为准 |
| 双通路 | CLI `sv install` 与 AI 按 meta-skill 落盘 **等价** |

### 2.1 命令面

```bash
py cli/sv.py list [--category <cat>]
py cli/sv.py install <skill> --ide <ide> --os <windows|linux|macos>
py cli/sv.py install <skill> --ide <ide> --os <os> --scope project --project-root <path>
py cli/sv.py install --all --ide <ide> --os <os>
```

`--ide`：`cursor` | `claude-code` | `codex` | `copilot` | `pi` | `opencode`

### 2.2 期望路径（Windows user 示例）

以用户主目录为 `{home}`：

| IDE | 期望目录 |
|-----|----------|
| cursor | `{home}\.cursor\skills\hello-skillvault\` |
| claude-code | `{home}\.claude\skills\hello-skillvault\` |

完整表见 [ide-targets.md](../ide-targets.md)。

## 3. 实现任务（设计拆解）

### 3.1 CLI 单测（锁行为）

| 文件 | 覆盖 |
|------|------|
| `tests/test_paths.py` | `resolve_install_dir`：六 IDE × 三 OS user 模板；project 需 root；缺 root / 误传 root 报错；`home_override` |
| `tests/test_install.py` | 装到临时 home；无 `SOURCE.md`/`tests.yaml`；默认不覆盖 / `--force`；frontmatter 键按 IDE 裁剪 |

测试用临时目录，不污染真实用户 skills。CI 跑全量 `tests/`。

### 3.2 CLI 小改

- `sv list --category <cat>`：按类目过滤（便于安装前挑选）

### 3.3 实机验收（本机 Windows）

验收 skill：`hello-skillvault`（`vault/own/meta/hello-skillvault`）。

**CLI 通路**

```bash
py cli/sv.py install hello-skillvault --ide cursor --os windows --force
py cli/sv.py install hello-skillvault --ide claude-code --os windows --force
```

检查：

1. 上述两路径存在 `SKILL.md`  
2. 目录名为 `hello-skillvault`（无 `meta` 前缀）  
3. 无 `SOURCE.md`、无 `tests.yaml`  
4. `scripts/hello.ps1` 仍在（若源有 scripts）  

**AI 通路**

打开本仓库，按 `meta-skills/install`：请 Agent 将 `hello-skillvault` 以用户级装到 Windows Cursor（可先装到临时目录或确认路径后执行）。规则与 CLI 相同。

### 3.4 文档

- 本文件验收记录节回填  
- 刷新 [status.md](../status.md) M1 进度  

## 4. 完成标准

- [x] `test_paths.py` / `test_install.py` 合入 `main`，CI 绿（PR #9）  
- [x] `list --category` 可用（PR #10）  
- [x] Windows：cursor + claude-code 用户级安装实测通过  
- [x] 下方「验收记录」已填写日期与结果  

## 5. 验收记录（实现后填写）

| 日期 | 操作者 | cursor | claude-code | AI 通路 | 备注 |
|------|--------|--------|-------------|---------|------|
| 2026-10-03 | moyueshuwx / agent | pass | pass | pass | 路径 `~\.cursor\skills\hello-skillvault`、`~\.claude\skills\hello-skillvault`；无 SOURCE.md/tests.yaml；有 scripts；AI 通路在用户「继续」授权后覆盖装入 Cursor |

## 6. 非目标（M1）

- 一次命令装多个 IDE  
- 修改 Ruleset 为强制 PR  
- 上 CI Windows runner  
