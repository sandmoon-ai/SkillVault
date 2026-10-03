---
name: install
description: >-
  Install SkillVault skills into an IDE via the AI pathway (or by running the
  CLI). Use when the user asks to install, sync, or load vault skills into
  Cursor, Codex, Claude Code, Copilot, Pi, or OpenCode — including phrases like
  安装 skill、装到 Cursor、用户级安装.
---

# Install Skills from SkillVault（AI 一等通路）

安装是产物链末环。Skill 须**已在 vault**（`vault/own` 或经门禁的 `vault/imported`）。

本 play 是 **AI 安装** 的规程；与 `py cli/sv.py install` **同等有效**。优先直接由 AI 落盘；用户明确要求脚本/批量时再调 CLI。

## 默认

- Scope = **user**，除非用户明确要求项目级
- 必须弄清 **IDE + OS**（`windows` | `linux` | `macos`）；缺了就问
- 无项目级授权时绝不写项目目录
- 不安装 `SOURCE.md`、`_template`、`.gitkeep`

## AI 安装步骤（推荐）

```text
Install Progress:
- [ ] 1. 列出 vault 中可选 Skill（读 vault/own、vault/imported）
- [ ] 2. 确认 skill 名、IDE、OS；项目级则再要 project-root
- [ ] 3. 读 adapters/targets.yaml，解析目标目录
- [ ] 4. 向用户复述将写入的绝对路径，等人确认（Gate）
- [ ] 5. 复制 Skill 目录到目标/<skill-name>/（排除 SOURCE.md）
- [ ] 6. 按 adapters/frontmatter.yaml 裁剪目标侧 SKILL.md frontmatter（可选但推荐）
- [ ] 7. 回报结果；建议重载 Agent；可选触发抽检
```

### 解析路径

1. 打开 [`adapters/targets.yaml`](../../adapters/targets.yaml)
2. 取 `ides.<ide>.<scope>.<os>` 模板
3. 展开 `{home}` → 当前用户主目录；`{project_root}` → 用户给出的根
4. 最终目录 = `解析后的路径 / <skill-name>`

路径对照也可看 [`docs/ide-targets.md`](../../docs/ide-targets.md)。

`--ide` 取值：`cursor` | `claude-code` | `codex` | `copilot` | `pi` | `opencode`

### 复制规则

- 源：`vault/own/<name>/` 或 `vault/imported/<name>/`（own 优先）
- 排除：`SOURCE.md` 及仓库内部占位文件
- 目标已存在：先说明将覆盖，**等人确认**后再覆盖（对齐 CLI 的 `--force` 语义）
- 不要发明第二套路径约定

## CLI 安装（等价备选）

用户要脚本化或批量时：

```bash
py cli/sv.py list
py cli/sv.py install <skill-name> --ide <ide> --os <os>
py cli/sv.py install --all --ide <ide> --os <os>
py cli/sv.py install <skill-name> --ide <ide> --os <os> \
  --scope project --project-root <path>
```

AI 可代为执行上述命令，仍须先确认 IDE/OS/scope。

## 示例对话意图

- 「把 hello-skillvault 装到我这台 Windows 的 Cursor」→ AI 通路，user scope
- 「这个 skill 装进当前仓库给 Claude Code 用」→ 先确认 project-root，再 project scope
- 「所有 skill 装到 Codex」→ 可 AI 逐个复制，或 `sv install --all`

## 脚本健康（建议在安装前）

若目标 Skill 含 `scripts/`，安装前可跑：

```bash
py -m pytest tests/test_skill_scripts.py -v -k <skill-name>
```

测试失败时应告知用户；是否仍安装由用户决定，但不得隐瞒失败。规范见 [`docs/script-testing.md`](../../docs/script-testing.md)。

## 不要

- 跳过路径确认直接写盘（除非用户已在本轮明确授权路径）
- 把 `CLAUDE.md` / 业务仓杂项当成 Skill 安装
- 默认项目级
- 只甩 CLI 命令却拒绝在可写环境下代为安装（用户要的是结果）
- 合入带脚本却无测试的 Skill（应在 import/own 门禁挡住）
