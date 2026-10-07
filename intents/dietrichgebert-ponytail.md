# Intent：收录 Skill 套件 — `DietrichGebert/ponytail`

> Gate A 草稿由 AI 起草；**批准人签字必须由人类填写**。未勾选完成前禁止 fetch 合入 / 写入 vault。

## 元信息

| 字段 | 内容 |
|------|------|
| 提议日期 | 2026-10-07 |
| 提议人 | （对话发起） |
| 来源 URL | https://github.com/DietrichGebert/ponytail |
| 锁定 ref（commit / tag / branch） | `552acd5efd0aeae2583a12efe39373d2f076f25e`（main tip at fetch 2026-10-07） |
| 许可 | MIT（Copyright 2026 DietrichGebert） |
| 建议类目 | 多数 `engineering`；`ponytail-help` / `ponytail-gain` → `meta`；可先落 `inbox` |
| 建议 name（目录名） | **按上游拆成 6 个独立包**（见下表）；不合并成单一 `ponytail` 目录 |
| 是否含 scripts/ | **否**（上游 `skills/*/SKILL.md` 仅文档；无 `scripts/`） |
| 收录理由 | YAGNI / 最小实现制度：编码时强制「能不写就不写、stdlib/原生优先」；另有删减向码评与全仓审计 |

## 套件清单（上游 `skills/`，6 个）

| name | 建议类目 | scripts | 备注 |
|------|----------|---------|------|
| `ponytail` | engineering | 否 | 核心：lite/full/ultra 强度；编码任务 always-on 风格 |
| `ponytail-review` | engineering | 否 | 针对 diff 的「过度工程」审查，输出删除清单 |
| `ponytail-audit` | engineering | 否 | 全仓过度工程审计（非只看 diff） |
| `ponytail-debt` | engineering | 否 | 收集代码里 `ponytail:` 延期标记 → 债务台账 |
| `ponytail-gain` | meta | 否 | 展示上游 benchmark 计分板（非本仓实测） |
| `ponytail-help` | meta | 否 | 命令/模式速查 |

**不收进 vault 的上游形态（仅说明）：** 根 `AGENTS.md`、各 IDE plugin/hooks/marketplace 适配器——SkillVault 只一等收录 `skills/` 包。

## Gate A — 是否收录？

- [x] 来源可信、许可兼容（MIT；作者 DietrichGebert；公开 GitHub）
- [x] 与现有 vault Skill 不重复（或明确替代关系）
  - vault **尚未**收录同名包
  - 与「写少/少依赖」类口头约定互补，不是 superpowers 工程流程的替代品
- [x] 类目与 tags 草稿合理：tags 建议 `ponytail`、`yagni`、`minimal`、`over-engineering`
- [x] 若含脚本：接受「须补 tests.yaml 才能合入」（本套件当前无 scripts）
- [x] **收录范围已选定（人类勾一项）：**
  - [x] A. 全套 6 个
  - [ ] B. 核心子集（建议：`ponytail`、`ponytail-review`、`ponytail-audit`；暂缓展示向：`ponytail-gain`、`ponytail-help`；可选：`ponytail-debt`）
  - [ ] C. 只收指定若干：_______________
  - 对话确认：2026-10-07 用户「A」
- [ ] **批准人签字/日期（人类）：** _______________

**Gate A 未勾选完成前：禁止 `sv import --apply`，禁止直接写入 `vault/imported`。**

## Gate B — 转化后（拉取后填写）

- [x] `.cache` 中内容与来源一致（抽检；草稿见 `.cache/import/dietrichgebert-ponytail/converted/`）
- [x] 每个拟收 skill 的 `SKILL.md` 符合 Agent Skills；frontmatter 完整（草稿态；已去 `argument-hint`）
- [x] 每个包有 `SOURCE.md`（url / ref / license / retrieved_at）
- [x] **已阅读安全检查报告**；结论：6×`PASS_WITH_WARNINGS`（critical=0；warn=`license-unknown`×1/包）
- [x] 无未接受的 `critical`（当前 critical=0）；warn：对话确认合入时接受 `license-unknown`（仓库根 MIT）
  - 对话确认：2026-10-07 用户「合入」
- [ ] **批准人签字/日期（人类）：** _______________

### Gate B 材料位置

| name | category | cache | security |
|------|----------|-------|----------|
| `ponytail` | engineering | `.cache/import/98a58b420845/` | `_skillvault_security.md` → also `.../security/ponytail.md` |
| `ponytail-review` | engineering | `.cache/import/64c88b8f7dd7/` | ditto |
| `ponytail-audit` | engineering | `.cache/import/3899edcf4814/` | ditto |
| `ponytail-debt` | engineering | `.cache/import/d5a39dcf8594/` | ditto |
| `ponytail-gain` | meta | `.cache/import/9c0b4244350b/` | ditto |
| `ponytail-help` | meta | `.cache/import/ab047f81648b/` | ditto |

转化草稿根：`.cache/import/dietrichgebert-ponytail/converted/`  
仓库根 LICENSE 副本：`.cache/import/dietrichgebert-ponytail/LICENSE`

## Gate C — 合入 vault / registry

- [x] 路径：4×`vault/imported/engineering/ponytail*` + 2×`vault/imported/meta/ponytail*`（材料已落盘）
- [x] `registry/sources.yaml` 已更新（ref `552acd5`）；`descriptions.zh-CN.yaml` 已补中文词条
- [x] PR 链接：https://github.com/sandmoon-ai/SkillVault/pull/50
- [x] 无脚本；`sv catalog` 刷新索引（本地）
- [ ] **批准人签字/日期（人类）：** _______________

## 备注 / 风险

1. **形态**：上游是多 IDE plugin + skills 套件；SkillVault 只收 `skills/` 六包，hooks / marketplace 体验不会随 vault 复制。
2. **会话状态**：上游 `/ponytail lite|full|ultra|off` 依赖 host 命令或会话级模式；Cursor 用户级 skill 安装后，强度切换需靠自然语言触发（与官方 plugin 体验可能不同）。
3. **`ponytail-gain`**：数字来自上游公开 benchmark，不是本仓指标；若收，应在转化备注中标明「展示用、非本地测量」。
4. **与码评 skill 分工**：`ponytail-review` 只打过度工程；正确性/安全码评仍用既有 review 类 skill。
5. **合入修复**：PowerShell 写入的 `SOURCE.md` 带 UTF-8 BOM，触发 vault gate `critical`；已去 BOM。合入后六包再扫均为 `PASS`；`tests/test_vault_gates.py` 5 passed。
