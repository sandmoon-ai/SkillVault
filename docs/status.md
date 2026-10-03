# 项目现状（整理稿）

最后更新：2026-10-03  

本文汇总「已经定下来的事」和「代码/配置落到哪了」，避免只存在于对话里。设计细节仍以 [architecture.md](./architecture.md) 为准。

## 1. 已确定的产品原则

| 原则 | 说明 |
|------|------|
| 包格式 | 以 [Agent Skills](https://agentskills.io/specification) 为 vault 唯一格式标准 |
| 流程治理 | 对齐 [AI-native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook)：产物链 + 人审门禁 |
| Skill 边界 | 制度/可复用流程进 vault；`CLAUDE.md` / `AGENTS.md` 留在业务仓 |
| 双通路 | **AI 收录/安装**（meta-skills）与 **CLI**（`cli/sv.py`）同等一等，规则相同 |
| 安装默认 | 用户级；项目级必须显式指定 |
| 脚本 | Skill 内脚本必须有 `scripts/tests.yaml` 且测试通过才能合入 |
| 硬门禁 | Skill 是建议性控制；仓库级强制靠 **CI + 分支 Ruleset** |

## 2. 产物链与门禁（摘要）

```text
intent-import → Gate A
fetch (.cache) → 摘要
转化 + SOURCE.md → Gate B
vault + registry commit → Gate C
install --ide/--os（默认 user）→ Gate D（可选抽检）
```

- 拉取默认**只进 `.cache`**，不自动合入 vault  
- `--apply` / 合入 registry 须人审  

详见 [architecture.md](./architecture.md)。

## 3. 仓库落地对照

### 已在 GitHub `main` 上

| 内容 | 路径 / 说明 |
|------|-------------|
| README / LICENSE | 仓库根 |
| 架构与 IDE / 脚本测试 / CI 文档 | `docs/*`（本文亦属文档层） |
| CI | `.github/workflows/ci.yml`（pytest + 成本卫生检查） |
| Artifact 月度清理 | `.github/workflows/actions-storage-cleanup.yml` |
| 成本卫生脚本 | `.github/scripts/check_actions_cost_hygiene.py` |
| 示例 Skill + 脚本测试 | `vault/own/hello-skillvault/`、`tests/test_skill_scripts.py` |
| 包装与依赖 | `pyproject.toml` |
| Frontmatter 适配表 | `adapters/frontmatter.yaml` |

### GitHub 网页上已配置（不在 git 内）

| 配置 | 状态 |
|------|------|
| Actions Artifact/日志保留期 | **1 天**（Settings → Actions → General） |
| 分支 Ruleset `protect-main` | **Active**；目标 `main`；必需检查 `Skill script tests`；禁删分支 / 禁 force push；无 bypass；**未**强制「必须走 PR」 |
| Ruleset 链接 | https://github.com/sandmoon-ai/SkillVault/rules/24400124 |

### 本机可选（不进仓库、项目控制不了）

| 项 | 说明 |
|----|------|
| Cursor 用户级 hook | `~/.cursor/hooks.json` + `hooks/skillvault-script-tests.ps1`：在 SkillVault 工作区 Agent `stop` 时跑脚本测试；失败则 followup。纯个人习惯，不替代 CI |

### 设计已有、需随文档一并进库的骨架

下列内容在本地工作区已存在，并应提交进 git，使远程与文档描述一致：

- `adapters/targets.yaml`
- `meta-skills/import-from-url`、`meta-skills/install`
- `registry/sources.yaml`
- `intents/`
- `vault/own/_template/`、`vault/imported/`
- `cli/`（Python CLI 草稿：list/install/import/sync）

> CLI 已能支撑双通路中的脚本侧，但验收与 IDE 实测仍属推进中项（见下节）。

## 4. 推进进度（相对计划）

| 阶段 | 状态 | 备注 |
|------|------|------|
| Phase 0 文档与产物链 / agentskills 规范 | **基本完成** | architecture / README / meta-skills / 脚本测试规范 |
| Phase 1 安装闭环 | **进行中** | CLI 与 meta-skill 已有；需收敛验证 + 多 IDE 实测 |
| Phase 2 收录闭环（门禁） | **进行中** | import meta-skill + CLI 草稿有；待真实公开 Skill 样例 |
| Phase 3 sync + 换机文档 | **部分** | sync 草稿有；换机流程在 README |
| Phase 4 硬化 | **部分完成** | Skill 脚本 pytest + CI + 成本卫生 + Ruleset；CLI 单测仍缺 |

## 5. 质量门禁一览

| 门禁 | 作用 |
|------|------|
| `tests/test_skill_scripts.py` | 清单驱动；未声明脚本或冒烟失败则红 |
| GitHub Actions `CI` | 每次 push/PR 跑卫生检查 + 脚本测试 |
| Ruleset `protect-main` | 合入/更新 `main` 相关流程要求 `Skill script tests` 通过；禁 force push / 删分支 |
| Gate A–C（人工 + AI play） | 收录语义与合入 vault |

## 6. 文档索引

| 文档 | 内容 |
|------|------|
| [architecture.md](./architecture.md) | 格式标准、边界、产物链、双通路、治理 |
| [ide-targets.md](./ide-targets.md) | 六 IDE 用户/项目路径 |
| [script-testing.md](./script-testing.md) | Skill 脚本测试规范 |
| [ci.md](./ci.md) | CI 概念、用法、成本防护、**已启用的 Ruleset** |
| [status.md](./status.md) | 本文：现状与落地对照 |

外部规范：[agentskills.io/specification](https://agentskills.io/specification)
