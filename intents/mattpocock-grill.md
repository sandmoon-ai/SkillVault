# Intent：收录 Skill 套件 — `mattpocock/skills` grill 系

> Gate A 草稿由 AI 起草；**批准人签字必须由人类填写**。未勾选完成前禁止 fetch 合入 / 写入 vault。  
> 对话「收纳 grill skill」默认指向 Matt 系（本仓 `docs/design/ai-native-sdlc-composition.md` 已引用）。若你指的是 `zhjai/grill-all` 等第三方变体，请改选下方「来源」。

## 元信息

| 字段 | 内容 |
|------|------|
| 提议日期 | 2026-10-10 |
| 提议人 | （对话发起） |
| 来源 URL | https://github.com/mattpocock/skills |
| 锁定 ref（commit / tag / branch） | `49dd158d1076134a641b33efb035946536778336`（main tip at fetch 2026-10-10） |
| 许可 | MIT |
| 建议类目 | `grilling` / `grill-me` → `meta` 或 `engineering`；`grill-with-docs` / `domain-modeling` → `engineering` |
| 建议 name（目录名） | **按上游拆包**（见下表）；不合并成单一 `grill` 目录 |
| 是否含 scripts/ | **否**（仅 Markdown + 少量 `agents/openai.yaml` 适配元数据） |
| 收录理由 | 动手前用「烧烤式」访谈把设计树问透，对齐事实/决策分离；是本仓 AI-native SDLC 设计里已点名、尚未收录的 Matt 核心件 |

## 套件清单（grill 相关）

| name | 上游路径 | 建议类目 | 依赖 | 备注 |
|------|----------|----------|------|------|
| `grilling` | `skills/productivity/grilling` | engineering | — | **原语**：一轮问完 frontier、给推荐答案、等人答完再下一轮 |
| `grill-me` | `skills/productivity/grill-me` | engineering | `grilling` | 用户触发入口；正文几乎只有「Call Skill grilling」 |
| `domain-modeling` | `skills/engineering/domain-modeling` | engineering | — | 术语/glossary/ADR 写法；含 format 参考文件 |
| `grill-with-docs` | `skills/engineering/grill-with-docs` | engineering | `grilling` + `domain-modeling` | 访谈同时写 `GLOSSARY.md` / `docs/adr/` |

**不在本 intent 范围（除非另开）：** `to-spec`、`to-tickets`、`implement`、`tdd` 等 Matt 其余工程 skill。

## 来源确认（人类勾一项）

- [x] **M.** Matt Pocock `mattpocock/skills` grill 系（默认推荐）
- [ ] **X.** 其他：_______________（如 `zhjai/grill-all` / `nicobailon/grill-for-unknowns`）
  - 对话确认：2026-10-10 用户「继续，选 A」

## Gate A — 是否收录？

- [x] 来源可信、许可兼容（MIT；作者 Matt Pocock）
- [x] 与现有 vault Skill 不重复（或明确替代关系）
  - vault **尚未**收录同名包
  - 与 `ponytail`（实现极简）互补：grill 在**动手前对齐**，ponytail 在**动手时压复杂度**
  - 与 `brainstorming`（superpowers）有「先谈再做」重叠，但机制不同（设计树 + 推荐答案 vs 创意对齐）→ **并存，不替代**
- [x] 类目与 tags 草稿合理：tags 建议 `matt-pocock`、`grilling`、`interview`、`adr`（domain-modeling）
- [x] 若含脚本：接受「须补 tests.yaml 才能合入」（本套件无 scripts）
- [x] **收录范围已选定（人类勾一项）：**
  - [x] A. 全套 4 个（`grilling` + `grill-me` + `domain-modeling` + `grill-with-docs`）— **推荐**：薄入口依赖原语，缺一不可用
  - [ ] B. 只要原语：`grilling` + `domain-modeling`（入口由自然语言触发，不收 `grill-me` / `grill-with-docs` 薄壳）
  - [ ] C. 只收指定：_______________
- [ ] **批准人签字/日期（人类）：** _______________

**Gate A 未勾选完成前：禁止 `sv import --apply`，禁止直接写入 `vault/imported`。**

## Gate B — 转化后（拉取后填写）

- [x] `.cache` 中内容与来源一致（抽检；草稿见 `.cache/import/mattpocock-grill/converted/`）
- [x] 每个拟收 skill 的 `SKILL.md` 符合 Agent Skills；frontmatter 完整（草稿态）
- [x] 每个包有 `SOURCE.md`（url / ref / license / retrieved_at）
- [x] **已阅读安全检查报告**；结论：4×`PASS_WITH_WARNINGS`（critical=0；warn=`license-unknown`×1/包）
- [x] 无未接受的 `critical`（当前 0）；warn：对话确认合入时接受 `license-unknown`（仓库根 MIT；来源确认 mattpocock/skills）
  - 对话确认：2026-10-10 用户「就 mattpocock/skills 就行，合并」
- [ ] **批准人签字/日期（人类）：** _______________

### Gate B 材料

| name | cache | 转化要点 |
|------|-------|----------|
| `grilling` | `.cache/import/ad4982503508/` | 正文原样 + SkillVault frontmatter |
| `grill-me` | `.cache/import/5860b5c78304/` | 薄壳改写：显式加载 `grilling`（保留 `disable-model-invocation`） |
| `domain-modeling` | `.cache/import/09f792f8578a/` | 含 `ADR-FORMAT.md` / `GLOSSARY-FORMAT.md` |
| `grill-with-docs` | `.cache/import/35ac02f0acc9/` | 薄壳改写：显式加载 `grilling` + `domain-modeling` |

草稿根：`.cache/import/mattpocock-grill/converted/`  
LICENSE 副本：`.cache/import/mattpocock-grill/LICENSE`  
`agents/openai.yaml` 保留在 vault 包内（上游适配元数据）

## Gate C — 合入 vault / registry

- [x] 路径：`vault/imported/engineering/{grilling,grill-me,domain-modeling,grill-with-docs}/`（材料已落盘）
- [x] `registry/sources.yaml` 已更新（ref `49dd158`）；`descriptions.zh-CN.yaml` 已补中文词条
- [x] PR 链接：https://github.com/sandmoon-ai/SkillVault/pull/51
- [x] 无脚本；合入后安全扫描 4×`PASS`；`sv catalog` + `test_vault_gates`（本地）
- [ ] **批准人签字/日期（人类）：** _______________

## 备注 / 风险

1. **薄壳依赖：** `grill-me` / `grill-with-docs` 依赖 host 的 Skill 工具链式调用；Cursor 上若不能 `Call Skill`，转化时需改成「读取并执行同套件内 `grilling` / `domain-modeling` 正文」的显式步骤，否则薄壳几乎无用。
2. **写库副作用：** `grill-with-docs` / `domain-modeling` 会写 `GLOSSARY.md`、`docs/adr/`（或 `CONTEXT.md` 变体，视上游版本）；安装说明里应标明「只在可写仓库会话使用」。
3. **与设计稿关系：** `docs/design/ai-native-sdlc-composition.md` 已把 `grill-with-docs` 放在 Build 入口；本收录是该设计的前置库存，不自动改设计结论。
4. **可选元数据：** 上游 `agents/openai.yaml` 可保留在 vault（不进 IDE 安装面）或丢弃；Gate B 再定。
