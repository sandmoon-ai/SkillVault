---
name: import-from-url
description: >-
  Import a public skill by URL into SkillVault via the AI pathway (fetch,
  convert to Agent Skills format, human gates). Use when the user provides a
  GitHub/raw URL or local path, or asks to 收录 / 导入 / import a skill.
---

# Import Public Skill by URL（AI 一等通路）

对齐 [`docs/architecture.md`](../../docs/architecture.md)：拉取 ≠ 合入；人审门禁后再进 vault。

本 play 是 **AI 收录** 的规程；与 `py cli/sv.py import` **配合或独立使用均可**。语义转化必须以 AI 完成；CLI 只负责确定性下载（可选）。

## 产物链

```text
Import Progress:
- [ ] Gate A: intents/intent-import-<name>.md（为何收、边界）— 等人确认
- [ ] Fetch: 拉到 .cache（AI 下载 或 sv import）— 出示摘要
- [ ] Convert: 写成 Agent Skills 包 → vault/imported/<category>/<name>/ + SOURCE.md
      （默认 category=`inbox`，Gate B 再归入 docs/taxonomy.md 标准类目）
- [ ] Gate B: 展示 diff，确认类目/标签，等人确认
- [ ] Gate C: 更新 registry + catalog（可选）+ 建议 commit
- [ ] 需要落地时 → 走 meta-skills/install（AI 或 CLI）
```

## Gate A — 意图（AI 起草，人确认）

在 `intents/` 写明：

- 解决什么重复问题 / 哪条制度要一致执行
- 适用与不适用边界
- 为何不该写成某仓的 `CLAUDE.md` 碎片

**停下来等人说「继续 / 值得收」**，再 fetch。

## Fetch — 两种等价方式

### A. AI 拉取（一等）

在可访问网络时，AI 可直接：

1. 解析 GitHub tree/blob/raw（或用户给的本地路径）
2. 下载 Skill 相关文件到 `.cache/import/<短哈希或名称>/`
3. 列出文件树、读 frontmatter、标出脚本平台线索
4. 把摘要给用户看

### B. CLI 拉取（等价）

```bash
py cli/sv.py import <url> [--name <skill-name>] [--ref <ref>]
```

只写入 `.cache`。**不要默认 `--apply`。**

## 转化规则（AI 主责）

目标格式：[Agent Skills Specification](https://agentskills.io/specification)。

- 输出：`vault/imported/<category>/<name>/SKILL.md`（目录名 = `name`；分类见 [taxonomy.md](../../docs/taxonomy.md)）
- 任意源形态 → 规范目录包（`scripts/` / `references/` / `assets/` 按需）
- Frontmatter：必需 `name`、`description`；`metadata.category` + `metadata.tags`；可选 `license` / `compatibility` / `allowed-tools`
- `name`：小写+数字+连字符，1–64，与目录名一致
- `description`：1–1024，做什么 + **何时触发**
- 去掉写死 IDE 路径；改为经 SkillVault 安装
- 脚本：`.sh` + `.ps1` 或 Python；否则标明 `compatibility`
- **若有脚本：必须按 [docs/script-testing.md](../../docs/script-testing.md) 补齐 `scripts/tests.yaml`，并跑通测试；测不过不得合入**
- 上游许可/作者 → `SOURCE.md`（永不安装进 IDE）
- 无法映射为 Agent Skills、或不像制度知识 → **停止并说明**，不要硬收

## Gate B / C

1. 展示将合入的文件树与关键 diff、`SOURCE.md`
2. 若存在 `scripts/`：确认 `tests.yaml` 覆盖每个脚本，并执行 `py -m pytest tests/test_skill_scripts.py -v`（或至少跑该 skill 相关用例）
3. **等人确认**后写入 `vault/imported/` 与 `registry/sources.yaml`
4. 提示 commit；用户要求时可代为提交
5. 若用户接着要「装到某 IDE」→ 直接转入 `meta-skills/install`，勿只丢 CLI 文档

## 示例对话意图

- 「把 https://github.com/.../tree/.../some-skill 收进 SkillVault」→ 本 play 全流程
- 「先别进 vault，只帮我看看源长什么样」→ 只做到 Fetch + 摘要
- 「收完并装到我 Windows 的 Cursor」→ import 门禁通过后接 install play

## 不要

- 无 Gate 确认就写入 `vault/imported` 或改 registry
- 只回复「请运行 sv import」却拒绝在可写环境代为拉取/转化（用户要的是收录结果）
- 把 CLI `--apply` 当成跳过人工审查的捷径
