# Intent：收录 Skill 套件 — `obra/superpowers`

> Gate A 草稿由 AI 起草；**批准人签字必须由人类填写**。未勾选完成前禁止 fetch 合入 / 写入 vault。

## 元信息

| 字段 | 内容 |
|------|------|
| 提议日期 | 2026-10-03 |
| 提议人 | （对话发起） |
| 来源 URL | https://github.com/obra/superpowers |
| 锁定 ref（commit / tag / branch） | `8ca22dba9a94f28898bbce59f2537ff4d87c747d`（Release v6.4.2） |
| 许可 | MIT（Copyright 2025 Jesse Vincent） |
| 建议类目 | 多数 `engineering`；`using-superpowers` / `writing-skills` / `diagnosing-superpowers` → `meta`；可先落 `inbox` |
| 建议 name（目录名） | **按上游拆成 15 个独立包**（见下表）；不合并成单一 `superpowers` 目录 |
| 是否含 scripts/ | **部分有**（见下）；有脚本者须补 `scripts/tests.yaml` |
| 收录理由 | 一套可组合的工程流程制度（设计→计划→TDD→子代理执行→码评→收尾），跨 IDE 可治理安装；不只是单仓 CLAUDE.md 碎片 |

## 套件清单（上游 `skills/`，15 个）

| name | 建议类目 | scripts | 备注 |
|------|----------|---------|------|
| `using-superpowers` | meta | 否 | 会话引导；会强制「先读 skill」 |
| `brainstorming` | engineering | **是**（Node companion server 等） | 可选 telemetry |
| `writing-plans` | engineering | 否 | |
| `executing-plans` | engineering | **是**（task-start/done） | |
| `subagent-driven-development` | engineering | **是** | 依赖子代理能力 |
| `dispatching-parallel-agents` | engineering | 否 | 依赖并行子代理 |
| `test-driven-development` | engineering | 否 | + references |
| `systematic-debugging` | engineering | 否 | + references |
| `verification-before-completion` | engineering | 否 | |
| `requesting-code-review` | engineering | 否 | |
| `receiving-code-review` | engineering | 否 | |
| `using-git-worktrees` | engineering | 否 | |
| `finishing-a-development-branch` | engineering | 否 | |
| `writing-skills` | meta | 否 | 写 skill 的 meta；含 eval 方法论引用 |
| `diagnosing-superpowers` | meta | 否 | 强依赖会话 transcript / 上游排障 |

## Gate A — 是否收录？

- [ ] 来源可信、许可兼容（MIT；作者 Jesse Vincent / Prime Radiant；上游活跃）
- [ ] 与现有 vault Skill 不重复（或明确替代关系）
  - vault **尚未**收录同名包
  - 本机 Cursor 已可通过官方插件 `/add-plugin superpowers` 使用（plugin cache）；收进 SkillVault = **治理副本 / 跨 IDE 安装**，不是「否则用不了」
  - 与搁置中的 `docs/design/ai-native-sdlc-composition.md`、Matt pocock 流程有方法论重叠 → **若收，需声明：工程流程以本套件为准，或只收子集**
- [ ] 类目与 tags 草稿合理：tags 建议 `superpowers`、`sdlc`、`tdd`、`debugging`；有脚本者加 `has-scripts`
- [ ] 若含脚本：接受「须补 tests.yaml 才能合入」（至少 brainstorming / executing-plans / subagent-driven-development）
- [x] **收录范围已选定（人类勾一项）：**
  - [ ] A. 全套 15 个
  - [x] B. 核心工程子集（建议：`brainstorming`、`writing-plans`、`executing-plans`、`test-driven-development`、`systematic-debugging`、`verification-before-completion`、`requesting-code-review`、`receiving-code-review`、`using-git-worktrees`、`finishing-a-development-branch`；暂缓 harness 强耦合：`using-superpowers`、`subagent-driven-development`、`dispatching-parallel-agents`、`diagnosing-superpowers`、`writing-skills`）
  - [ ] C. 只收指定若干：_______________
  - 对话确认：2026-10-03 用户「值得收」（未另选 A/C，按推荐默认 **B**）
- [ ] **批准人签字/日期（人类）：** _______________

**Gate A 未勾选完成前：禁止 `sv import --apply`，禁止直接写入 `vault/imported`。**

## Gate B — 转化后（拉取后填写）

- [x] `.cache` 中内容与来源一致（抽检；草稿见 `.cache/import/obra-superpowers/converted/`）
- [x] 每个拟收 skill 的 `SKILL.md` 符合 Agent Skills；frontmatter 完整（草稿态）
- [x] 每个包有 `SOURCE.md`（url / ref / license / retrieved_at）
- [x] **已阅读安全检查报告**；结论：9×`PASS` + brainstorming `PASS_WITH_WARNINGS`（对话确认合入时接受）
- [x] 无未接受的 `critical`（当前 critical=0）；warn：对话接受 brainstorming `parent_escape`（读 `assets/helper.js`）
- [x] 有脚本的包：已补 `tests.yaml`；本机用 Git Bash 手跑 usage smoke 通过（系统 `bash` 指向坏 WSL stub 时 pytest 可能 skip/失败，CI Linux 预期绿）
- [ ] **批准人签字/日期（人类）：** _______________

## Gate C — 合入 vault / registry

- [x] 路径：`vault/imported/engineering/<name>/`（B 子集 10 个；材料已落盘）
- [x] `registry/sources.yaml` 已更新（每 skill 一条；ref `8ca22db`）
- [ ] PR 链接：
- [x] 本地脚本测试绿（`pytest -k "brainstorming or systematic-debugging"`：3 passed）；CI 待 PR
- [ ] **批准人签字/日期（人类）：** _______________

## 备注 / 风险

1. **形态**：上游是 Claude/Cursor **plugin 套件**（skills + hooks + agents），SkillVault 只能一等收录 **skills/**；hooks / marketplace 安装体验不会随 vault 复制。
2. **Harness 耦合**：若干正文引用 `Skill` 工具、会话启动注入、worktree/子代理假设；转化时需去 IDE 死路径，并在 `compatibility` / 备注标明「无子代理时部分步骤降级」。
3. **Telemetry**：`brainstorming` 视觉 companion 默认会打上游 logo 请求；合入时应在 SKILL 中保留/强调 `SUPERPOWERS_DISABLE_TELEMETRY` 说明。
4. **重复安装**：若 Cursor 已装官方 plugin，再 `sv install` 同名 skill 可能双份并存——安装前需约定「plugin 优先」或「vault 覆盖」。
5. **工作量**：全套 ≈ 15 次转化 + 安全扫 + 若干脚本测试；建议优先 B 子集。

## 对话记录（非签字）

- 2026-10-03：用户问「obra/superpowers 套件能收纳进来么」→ 结论：**能收，须拆包 + 过 Gate A–C**；已起草本 intent，停在 Gate A。
- 2026-10-03：用户「值得收」→ 按默认 **B** 拉取 `8ca22db`；转化草稿在 `.cache/import/obra-superpowers/converted/`；**停在 Gate B**（未写 vault / registry）。
- 2026-10-03：用户「确认合入」→ 已写入 `vault/imported/engineering/` ×10、`registry/sources.yaml`、catalog + 中文简介；脚本烟测 3 passed。待 commit/PR 与人类 Gate 签字。
