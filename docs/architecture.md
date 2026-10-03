# SkillVault 架构

本文说明 SkillVault 在 AI-native SDLC 中的位置、产物链、门禁与目录职责。  
概念对齐：[The AI-native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook)。  

**落地进度与 GitHub 已启用配置**见 [status.md](./status.md)；CI / Ruleset 细节见 [ci.md](./ci.md)。

## 1. 定位

SkillVault 是**工具中立的制度知识库（Skills）**：

- Git 为唯一真相源（repo-as-source-of-truth）
- 一份规范 Skill 包，安装时再映射到各 IDE / OS
- 默认安装为**用户级**；项目级必须显式指定

它解决的是「可复用的流程/规范如何跨机器、跨工具一致落地」，不是替代项目管理或项目内上下文文件。

## 2. 包格式标准：Agent Skills（agentskills.io）

**本仓库接受并以 [Agent Skills](https://agentskills.io) 开放规范为 vault 内 Skill 的唯一格式标准。**  
规范原文：[Specification](https://agentskills.io/specification)。

| 约定 | 要求 |
|------|------|
| 形态 | 目录包；至少包含 `SKILL.md` |
| Frontmatter | 必需 `name`、`description`；可选 `license`、`compatibility`、`metadata`、`allowed-tools` |
| `name` | 1–64 字符；小写字母/数字/连字符；不首尾连字符；与父目录名一致 |
| `description` | 1–1024 字符；写清做什么 + **何时用**（触发负担主要在此） |
| 可选资源 | `scripts/`、`references/`、`assets/`（按需加载） |
| 加载模型 | Progressive disclosure：先元数据，激活后再读正文与资源 |

**本仓库补充（规范之外、安装时剥离）：**

- `SOURCE.md`：仅 `vault/imported` 溯源用，**不安装**到 IDE
- 产品私有 frontmatter（如部分工具的 `disable-model-invocation`）可在转化时保留于 vault；安装时按 `adapters/frontmatter.yaml` 裁剪

**不在标准内、由 adapter 处理的：**

- 各 IDE 的 user/project 磁盘路径（见 [ide-targets.md](./ide-targets.md)）
- 某产品对额外字段的扩展识别

收录公开 Skill 时：尽量规范到 agentskills.io 形态；无法映射为目录 + `SKILL.md` 的源，首期不收录。

## 3. Skill 与 CLAUDE.md（及同类文件）的边界

Playbook 的经验法则：**需要被一致执行的制度知识写成 Skill；日常仓库约定放进项目上下文文件。**

| | Skill（本仓库） | 项目上下文（不进 vault） |
|--|----------------|--------------------------|
| 典型文件 | `SKILL.md` 目录包 | `CLAUDE.md` / `AGENTS.md` / 各 IDE 规则文件 |
| 内容 | 何时触发、做什么、步骤、可选脚本 | 构建命令、目录约定、易错点、架构速览 |
| 作用域 | 跨项目复用（用户级）或明确装入某项目 | 跟随单个代码仓库 |
| 控制强度 | **建议性**：提高合规概率 | 会话起步上下文，不是策略引擎 |
| 变更方式 | PR / 人审后合入 vault，再 install | 在业务仓库里直接改 |

**应写成 Skill 的例子**

- API 安全审查清单、发布检查流程、PR 描述规范
- 可跨仓库复用的调研/设计/验收 play
- 从公开源转化来的、描述清晰的专用工作流

**不应放进 SkillVault 的例子**

- 某服务的 `make test`、包结构说明（属于该仓 `CLAUDE.md`）
- 一次性任务提示、与单一仓库强绑定的路径假设
- 必须 100% 强制的门禁（应另用 hook / CI / 评审；Skill 只降低违规率）

Skill 是 advisory control：装进 IDE 不等于强制执行。硬约束留在 hook、CI 与人工门禁。

## 4. 产物链（Artifact chain）

对齐 playbook：**每一阶段结束时提交下一阶段可读的产物；人审门禁产物，而不是盯着每一步生成过程。**

SkillVault 自身的轻量链：

```text
intent-import.md          # 为何收录、适用边界、不做的事
        │
        ▼  Gate A：人确认「值得收」
fetch summary             # CLI 拉取到 .cache；文件树 / frontmatter 摘要
        │
        ▼  Gate B：人/AI 转化并审阅 diff
converted skill           # vault/imported/<name>/SKILL.md + SOURCE.md
+ registry 条目
        │
        ▼  Gate C：commit / merge 合入 vault
sv install                # --ide + --os；默认 user
        │
        ▼  Gate D（可选）：在目标 IDE 做触发抽检
in use                    # 使用中发现问题 → 回写 intent 或修正 Skill
```

| 产物 | 谁写 | 下一阶段读什么 |
|------|------|----------------|
| `intent-import.md` | 人（可与 AI 共写） | 是否收录、范围约束 |
| `.cache/...` + summary | CLI | 源长什么样、有无脚本/许可线索 |
| `vault/imported/...` + `SOURCE.md` | AI 转化 + 人改 | 规范 Skill 正文与溯源 |
| `registry/sources.yaml` | import/sync 更新 | 上游 URL、ref、上次同步 |
| IDE 目录中的 Skill 副本 | `sv install` | Agent 运行时加载 |

默认：**拉取只进 cache，不自动合入 vault。**  
`--apply` / 合入 registry 视为 Gate B/C 之后的动作，需人审。

## 5. 目录结构（目标态）

```text
SkillVault/
├── README.md
├── LICENSE
├── docs/
│   ├── architecture.md          # 本文
│   └── ide-targets.md           # IDE 路径对照
├── adapters/
│   ├── targets.yaml             # ide × os × scope → 路径模板
│   └── frontmatter.yaml         # 安装时 frontmatter 字段裁剪
├── registry/
│   └── sources.yaml             # 已收录上游索引
├── vault/
│   ├── own/                     # 自建（可直接编辑）
│   └── imported/                # 公开源转化结果（经门禁后合入）
├── meta-skills/                 # AI 一等通路（收录 / 安装 play）
│   ├── import-from-url/
│   └── install/
├── intents/                     # 收录意图（intent-import 产物，可选按日期/名称）
├── cli/                         # CLI 等价通路：fetch / install / sync
└── .cache/                      # 本地拉取缓存（不提交）
```

### 规范 Skill 包（agentskills.io）

```text
<skill-name>/                 # 目录名 = frontmatter name
├── SKILL.md                  # 必需（规范核心）
├── scripts/                  # 可选
├── references/               # 可选
├── assets/                   # 可选
└── SOURCE.md                 # 仅 SkillVault imported；非规范字段，安装排除
```

`description` 必须写清**何时触发**；转化公开 Skill 时这是 Gate B 审查重点。校验可参考上游 [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref)。

## 6. 逻辑分层

| 层 | 路径 | 职责 |
|----|------|------|
| 真相源 | `vault/own`, `vault/imported` | 唯一规范内容；走 git 审计 |
| 意图 | `intents/` | 收录/变更的 why；Gate A 证据 |
| 索引 | `registry/sources.yaml` | 上游地址与同步元数据 |
| 适配 | `adapters/*` | 「装到哪里」、frontmatter 兼容 |
| 确定性工具 | `cli/` | 可选通路：拉取、复制、diff |
| AI play | `meta-skills/*` | **一等通路**：AI 收录 / AI 安装的完整操作规程 |

## 6.1 双通路：CLI 与 AI（同等一等）

收录与安装都提供两种用法，**效果与门禁规则相同**，不是「脚本为主、AI 为辅」。

| 通路 | 怎么用 | 适合 |
|------|--------|------|
| **AI 通路** | 在任意支持 Skills 的 Agent 里打开本仓库，调用 `meta-skills/import-from-url` 或 `meta-skills/install`；AI 读 `adapters/`、读写文件、停在各 Gate 等人确认 | 日常对话驱动、转化理解、换机引导 |
| **CLI 通路** | `py cli/sv.py import\|install\|list\|sync ...` | 批量、CI、可脚本化重复 |

共同约束：

- 规则与路径只来自本仓库文档 + `adapters/*.yaml`，两通路不得各写一套
- 门禁（Gate A–C）对人可见：AI 必须展示 intent / diff / 目标路径并等待确认，不得静默合入或静默覆盖
- AI 可直接按 adapter 复制文件完成安装；也可代用户调用 CLI——二者等价
- 语义转化（非标准源 → Agent Skills 包）以 **AI 通路为主**；CLI 负责确定性 fetch/copy

```text
用户：「把这个 URL 收进来」     →  AI play: import-from-url
用户：「装到 Cursor / Windows」 →  AI play: install
用户 / CI：批量脚本             →  CLI: sv import|install
```

## 7. 安装与范围

- 默认 scope = **user** → 写入各 IDE 用户级 Skills 目录  
- 项目级必须同时明确 scope=project 与 project-root（AI 询问或 CLI 参数）  
- 未指定 project 时，不得写入任何项目树  
- 支持 OS：`windows` / `linux` / `macos`  
- 支持 IDE：Cursor、Codex、Claude Code、Copilot、Pi、OpenCode（见 [ide-targets.md](./ide-targets.md)）

路径差异由 adapter 消化；vault 内正文保持工具中立，不写死某一 IDE 的安装路径。  
AI 安装时必须先解析 `adapters/targets.yaml` 得到绝对路径，再复制（排除 `SOURCE.md`），并回报落盘位置。

## 8. 治理（Governance）

| 原则 | 在 SkillVault 中的落法 |
|------|------------------------|
| 提交即审计 | intent、转化 diff、registry、Skill 正文均进 git |
| 人在门禁 | 合入 vault、安装到生产日常环境前需人确认 |
| 策略有主 | 自建 Skill 应能指出维护者；imported 保留上游与转化说明 |
| Skill ≠ 硬门禁 | 必须成立的规则另配 hook/CI；Skill 只保证「更容易做对」 |
| 变更可回滚 | 坏 Skill 用 git revert；各机 `install --force` 对齐 |
| **脚本必测** | Skill 内凡有 `scripts/` 可执行文件，须有 `scripts/tests.yaml` 且测试通过后方可合入（见 [script-testing.md](./script-testing.md)） |

## 9. 与完整 AI-native SDLC 的关系

完整链路是 `intent.md` → `spec.md` → `plan.md` → 代码/PR → 线上反馈。  

SkillVault **不承载**业务功能的 spec/plan；它提供的是 SDLC 各阶段可挂载的 **制度 Skills**（以及操作本库的 meta-skills）。业务仓仍用自己的 `CLAUDE.md` / `AGENTS.md` 与项目级 Skills。

```text
业务仓库                          SkillVault
────────                          ──────────
CLAUDE.md / AGENTS.md     ←上下文─  （不存放）
.cursor|claude|agents/... ←install─ vault/own|imported
intent/spec/plan.md       ←业务产物─ （不存放）
```

## 10. 推进原则（文档层约定）

1. vault 内格式以 [agentskills.io](https://agentskills.io/specification) 为准；路径差异用 adapter。  
2. 先稳定产物链与门禁语义，再加深 CLI / CI 自动化。  
3. 先手跑 play（meta-skill + 人工 Gate），再把重复步骤收进 `sv` 子命令。  
4. 收录标准宁缺毋滥：无法规范为 Agent Skills 包、或说不清触发/复用边界的源，不进 `imported`。  
5. 上游更新（sync）默认出 diff / PR，不默认覆盖已审内容。  
6. Skill 脚本无测试或测试失败 → 不得合入 vault（自建与 imported 相同）。
