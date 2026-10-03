# Intent：收录 Skill — `ui-ux-pro-max`

> Gate A 草稿由 AI 起草；**批准人签字必须由人类填写**。未勾选完成前禁止 fetch 合入 / 写入 vault。

## 元信息

| 字段 | 内容 |
|------|------|
| 提议日期 | 2026-10-03 |
| 提议人 | （对话发起） |
| 来源 URL | https://github.com/nextlevelbuilder/ui-ux-pro-max-skill |
| 锁定 ref（commit / tag / branch） | `09170eec67eefd46a7ae85de61b40c194020f997`（main tip at fetch） |
| 许可 | MIT（GitHub 标注 SPDX MIT） |
| 建议类目 | `design`（Gate B 可先落 `inbox`） |
| 建议 name（目录名） | `ui-ux-pro-max` |
| 是否含 scripts/ | **是**（Python CLI / 搜索与设计系统生成；须补 `scripts/tests.yaml`） |
| 收录理由 | 提供可复用的 UI/UX 设计智能（风格/配色/字体/落地页模式/交付前检查），跨框架一致执行，不只是单仓 CLAUDE.md 碎片 |

## Gate A — 是否收录？

- [ ] 来源可信、许可兼容（MIT；上游约 13 万 star，有 Premium 商业版，本仓只收开源 Basic）
- [ ] 与现有 vault Skill 不重复（或明确替代关系）
  - 已有 `frontend-design`（Anthropic）：偏「有辨识度的前端审美方向」
  - 本 Skill：偏「产业规则 + BM25 检索 + 完整设计系统生成 + 交付检查清单」
  - **关系：互补，不替代**
- [ ] 类目与 tags 草稿合理：`design`；tags 建议 `ui`、`ux`、`design-system`、`has-scripts`
- [ ] 若含脚本：接受「须补 tests.yaml 才能合入」
- [ ] **批准人签字/日期（人类）：** _______________

**Gate A 未勾选完成前：禁止 `sv import --apply`，禁止直接写入 `vault/imported`。**

## Gate B — 转化后（拉取后填写）

- [ ] `.cache` 中内容与来源一致（抽检）
- [ ] `SKILL.md` 符合 Agent Skills；frontmatter 完整
- [ ] `SOURCE.md` 含 url / ref / license / retrieved_at
- [ ] **已阅读安全检查报告**；结论：_______
- [ ] 无未接受的 `critical`；所有 `warn` 已确认（接受原因可写在下方备注）
- [ ] **批准人签字/日期（人类）：** _______________

## Gate C — 合入 vault / registry

- [x] 路径：`vault/imported/design/ui-ux-pro-max/`（材料已落盘；签字仍须人类）
- [x] `registry/sources.yaml` 已更新
- [ ] PR 链接：
- [x] 本地脚本测试绿（`pytest -k ui-ux-pro-max`：6 passed）；CI 待 PR
- [ ] **批准人签字/日期（人类）：** _______________

## 对话记录（非签字）

- 2026-10-03：用户在对话中回复「值得收」→ 视为 Gate A 继续授权；**批准人签字栏仍须人类手填**，Agent 不代签。
- Fetch：`py cli/sv.py import …/tree/main/.claude/skills/ui-ux-pro-max` → `.cache/import/6ae5158a2c7a`
- Security：`PASS_WITH_WARNINGS`（见同目录 `_skillvault_security.md`）
- 转化草稿：`.cache/import/6ae5158a2c7a-converted/ui-ux-pro-max/`
- 2026-10-03：用户回复「确认，继续」→ 视为 Gate B 合入授权；**批准人签字栏仍须人类手填**，Agent 不代签。
- 已写入：`vault/imported/design/ui-ux-pro-max/`；已更新 `registry/sources.yaml` + catalog。

## 备注

### 解决什么重复问题 / 哪条制度要一致执行

- 做落地页 / 产品 UI 时反复出现「默认紫粉渐变、无对比度、无交付检查」等问题
- 希望用同一套：产品类型匹配 → 风格/配色/字体/模式推荐 → 反模式与交付前清单
- 这是**跨项目可复用的设计制度**，适合 Skill；不是某个业务仓的构建命令或目录约定

### 适用 / 不适用

- **适用：** Web/移动多框架 UI、落地页、仪表盘可视化选型、交付前 UX/a11y 自检
- **不适用：** 品牌 VI / Logo 生成等 Premium 能力；纯后端；替代项目内设计系统真相源（token 仍应在业务仓）

### 为何不该只写进某仓 CLAUDE.md

- 规则库体量大（风格/色板/字体/产业规则 CSV + 检索脚本），属可安装的制度包
- 需跨 IDE / 多机一致；放单仓上下文无法复用

### 已知风险（Gate B 重点）

1. **体积：** 上游仓库约数 MB 级（含 data CSV / Python）；可能触发 `size-tree` warn
2. **脚本：** 含可执行 Python/CLI；必须 `scripts/tests.yaml` + pytest；重点扫 `script-danger` / `exfil-hint`
3. **依赖：** 可能依赖 Node/Python 运行时；`compatibility` 需写清
4. **商业边界：** README 区分 Basic（本仓）与 Premium；转化时不得混入付费能力宣传为已收录能力
5. **与 `frontend-design`：** 并存；在各自 `SOURCE.md` / description 中写清分工，避免触发冲突
