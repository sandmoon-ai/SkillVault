# SkillVault

个人 / 小团队的 **Agent Skill 制度知识库**：用 Git 统一管理自建与收录的 Skills，在 Linux / Windows 与多 IDE 间一致安装；公开源可通过 URL 拉取，经转化与人审后合入。

工具中立，不绑定单一产品。当前目标适配：**Cursor、Codex、Claude Code、Copilot、Pi、OpenCode**。

**包格式标准：** [Agent Skills](https://agentskills.io)（[Specification](https://agentskills.io/specification)）。vault 内 Skill 必须是规范的目录 + `SKILL.md` 包。

流程与治理对齐 [AI-native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook)：

- **提交产物、人审门禁**（而不是无审自动合入）
- **Skill = 需一致执行的制度知识**（不是项目杂项提示）
- **Git 为真相源**；安装只是把真相源投影到各 IDE 路径

完整架构见 [`docs/architecture.md`](docs/architecture.md)。  
**截至目前的落地对照与进度**见 [`docs/status.md`](docs/status.md)。  
**下一阶段设计（M1–M3）**见 [`docs/design/`](docs/design/README.md)。  
**参与贡献**：[CONTRIBUTING.zh-CN.md](CONTRIBUTING.zh-CN.md) · [CONTRIBUTING.md](CONTRIBUTING.md)（English）。

## 质量与 GitHub 门禁（已启用）

| 项 | 状态 |
|----|------|
| Skill 脚本测试 | `py -m pytest tests/test_skill_scripts.py`；规范见 [docs/script-testing.md](docs/script-testing.md) |
| CI | push/PR 跑卫生检查 + 脚本测试 → [Actions](https://github.com/sandmoon-ai/SkillVault/actions) |
| 分支 Ruleset `protect-main` | `main` 要求检查 `Skill script tests`；禁 force push / 删分支 → [规则](https://github.com/sandmoon-ai/SkillVault/rules/24400124) |
| Artifact 保留 | 仓库设置为 **1 天**；CI 另限制 `retention-days`≤7 + 月度清理 |

说明见 [docs/ci.md](docs/ci.md)。

## Skill 放什么、不放什么

| 放进 SkillVault | 留在各业务仓库 |
|-----------------|----------------|
| 可跨项目复用的流程、规范、审查清单 | `CLAUDE.md` / `AGENTS.md`（命令、目录约定、易错点） |
| 触发条件清晰的专用工作流 | 与单一仓库强绑定的说明 |
| 公开 Skill 转化后的规范包 + 溯源 | 业务 `intent.md` / `spec.md` / `plan.md` |

经验法则：**要处处一致执行 → Skill；只要这个仓的新成员知道怎么干活 → 项目上下文文件。**  
Skill 是建议性控制；必须强制的规则用 hook / CI / 评审，不要只靠 Skill。

## 产物链（先理解这个，再谈命令）

```text
intent-import   →  Gate：值得收吗？
      ↓
fetch (.cache)  →  源长什么样？
      ↓
转化 + SOURCE   →  Gate：diff 能合入吗？
      ↓
vault + registry（git commit）
      ↓
install --ide --os   （默认用户级）
```

- **默认不自动合入**：拉取只进 `.cache`，人审通过后才进 `vault/imported`。
- **默认用户级安装**：只有明确指定项目级时才写入某仓库。

## 目录结构

```text
SkillVault/
├── docs/                         # 含 taxonomy（分类）
├── adapters/
├── registry/                     # sources + catalog
├── intents/
├── vault/
│   ├── own/<category>/<skill>/   # 自建（按工作阶段分类）
│   └── imported/<category>/...   # 收录（默认先 inbox）
├── meta-skills/                  # AI 一等通路
├── cli/
└── .cache/
```

单个 Skill 包（[agentskills.io](https://agentskills.io/specification)）：

```text
vault/own/<category>/<skill-name>/
├── SKILL.md           # 必需；metadata.category 与目录一致
├── scripts/           # 可选 + tests.yaml
├── references/
├── assets/
└── SOURCE.md          # 仅 imported；安装时不拷贝
```

分类约定：[docs/taxonomy.md](docs/taxonomy.md)。安装到 IDE 时仍是扁平的 `<skill-name>/`。

## 使用概览：AI 与 CLI 双通路

收录和安装都是 **AI 通路与 CLI 通路并列**（规则相同，见 [`docs/architecture.md`](docs/architecture.md) §6.1）。日常优先对话驱动；批量/CI 用脚本。

| 场景 | AI 通路（推荐日常） | CLI 通路 |
|------|---------------------|----------|
| 安装到本机 IDE | 打开本仓库，让 Agent 按 [`meta-skills/install`](meta-skills/install/SKILL.md) 执行 | `py cli/sv.py install ...` |
| 收录公开 Skill | 给出 URL，按 [`meta-skills/import-from-url`](meta-skills/import-from-url/SKILL.md) | `py cli/sv.py import <url>`（只进 cache）+ AI 转化 |
| 本库 GitHub 操作 | 按 [`meta-skills/github-ops`](meta-skills/github-ops/SKILL.md)（PR / Issue / Milestone） | `gh` CLI |
| 上游更新 | 让 Agent 跑 sync 流程并展示 diff | `py cli/sv.py sync ...` |

### 换机 / 日常安装

1. `git clone` 或 `git pull` 本仓库  
2. **AI：**「把 `<skill>` 以用户级装到 Windows 的 Cursor」→ Agent 读 adapter、确认路径、复制文件  
   **或 CLI：**

```bash
py cli/sv.py list
py cli/sv.py list --category meta
py cli/sv.py install <skill> --ide cursor --os windows
py cli/sv.py install <skill> --ide claude-code --os linux

# 项目级必须显式
py cli/sv.py install <skill> --ide cursor --os windows \
  --scope project --project-root /path/to/repo
```

3. 重载 Agent；必要时做触发抽检  

路径对照：[docs/ide-targets.md](docs/ide-targets.md)。

### 收录公开 Skill

1. **AI：**「把 `<url>` 收进 SkillVault」→ 写 intent → fetch → 转化 → 等人审 → 合入 registry  
2. **或：** `sv import <url>` 只拉到 `.cache`，再由 AI 完成转化与门禁  
3. 需要落地时继续 **AI 安装** 或 `sv install`  
4. 未人审不得进 `vault/imported`

### 上游更新

AI 或 `sv sync` 重新拉取并给出 diff；**默认不覆盖**已审内容，确认后再 apply / 开 PR。

## 支持的 IDE 与 OS

| 维度 | 支持 |
|------|------|
| OS | Windows、Linux、macOS |
| IDE | Cursor、Codex、Claude Code、Copilot、Pi、OpenCode |
| 范围 | 默认 `user`；`project` 需显式指定 |

## 约定

- 格式遵循 [Agent Skills Specification](https://agentskills.io/specification)：`name` / `description` 规则与目录名一致  
- `description` 写清触发场景（agent 靠它决定是否加载）  
- `vault/own` 可直接改；`vault/imported` 经门禁合入，定制请 fork 到 `own/`  
- 正文保持工具中立；安装路径只存在于 `adapters/`  
- 不提交密钥、大二进制；第三方许可写在 `SOURCE.md` 或 `license` 字段  
- 脚本尽量双平台，否则在 `compatibility` 中标明限制  
- **脚本必测**：`scripts/` 下每个脚本须在 `scripts/tests.yaml` 声明，并经 `py -m pytest tests/test_skill_scripts.py` 通过（见 [docs/script-testing.md](docs/script-testing.md)）  


## 文档

| 文档 | 内容 |
|------|------|
| [CONTRIBUTING.zh-CN.md](CONTRIBUTING.zh-CN.md) / [CONTRIBUTING.md](CONTRIBUTING.md) | **贡献指南**（收录 / 自建 / PR 门禁） |
| [docs/status.md](docs/status.md) | **现状整理**：原则、已落地项、进度 |
| [docs/taxonomy.md](docs/taxonomy.md) | Skill 类目（阶段）+ 标签 |
| [docs/architecture.md](docs/architecture.md) | 格式标准、边界、产物链、双通路、治理 |
| [docs/ide-targets.md](docs/ide-targets.md) | 各 IDE 用户级 / 项目级路径 |
| [docs/script-testing.md](docs/script-testing.md) | Skill 脚本测试硬性规范 |
| [docs/ci.md](docs/ci.md) | CI、Ruleset、成本/存储防护 |
| [agentskills.io](https://agentskills.io/specification) | 外部规范（本仓库格式真相源） |
| [meta-skills/](meta-skills/) | AI 收录 / 安装 / GitHub 操作一等通路 |

## 许可证

本仓库以 [MIT License](./LICENSE) 发布。`vault/imported/` 下各 Skill 遵循其上游许可证；收录时保留原作者与许可声明。
