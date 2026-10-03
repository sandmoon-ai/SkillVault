# Intent：收录 Skill — `ocr`

> Gate A 草稿由 AI 起草；**批准人签字必须由人类填写**。未勾选完成前禁止 fetch 合入 / 写入 vault。

## 元信息

| 字段 | 内容 |
|------|------|
| 提议日期 | 2026-10-03 |
| 提议人 | （对话发起） |
| 来源 URL | https://github.com/ledin-pro/ocr |
| Skill 路径 | `skills/ocr/`（`SKILL.md` + `references/`） |
| 锁定 ref（commit / tag / branch） | `396fae9b284e5f111c8cec8d66719c26753e6e62`（release 0.7.0 / main tip） |
| 许可 | MIT（Copyright 2026 mxl；GitHub SPDX MIT） |
| 建议类目 | `ops`（Gate B 可先落 `inbox`） |
| 建议 name（目录名） | `ocr`（与上游 frontmatter `name` 一致） |
| 是否含 scripts/ | **否**（skill 包内无 `scripts/`；运行时依赖 PyPI `pro-ledin-ocr` CLI） |
| 收录理由 | 统一处理文本 PDF / 扫描件 / 纯图片 PDF 的抽取与 OCR 递进策略，含 searchable-PDF；跨 IDE 可安装的文档制度，不是单仓碎片 |

## Gate A — 是否收录？

- [ ] 来源可信、许可兼容（MIT；上游为独立 PyPI 包 `pro-ledin-ocr` + Agent Skill）
- [ ] 与现有 vault Skill 不重复（或明确替代关系）
  - vault **尚未**收录 `ocr` / PDF-OCR 类包
  - 本机可能另有个人级 `office-pdf` 等（文档创建/处理）；本 Skill 聚焦 **扫描/纯图 PDF → 文本/Markdown/可检索 PDF**
  - **关系：互补**；不替代 PaddleOCR / MinerU 等可选后端（本 skill 可调用 paddleocr 作引擎之一）
- [ ] 类目与 tags 草稿合理：`ops`；tags 建议 `pdf`、`ocr`、`documents`、`scanned`
- [ ] 若含脚本：接受「须补 tests.yaml 才能合入」→ **本包无 scripts/**；须在 `compatibility` / `SOURCE.md` 写清运行时依赖
- [ ] **批准人签字/日期（人类）：** _______________

**Gate A 未勾选完成前：禁止 `sv import --apply`，禁止直接写入 `vault/imported`。**

## Gate B — 转化后（拉取后填写）

- [x] `.cache` 中内容与来源一致（抽检：6 文件 = SKILL + 5 references；与上游 tree 一致）
- [x] `SKILL.md` 符合 Agent Skills；frontmatter 完整（草稿态：已加 license/compatibility/metadata + SkillVault 运行时说明）
- [x] `SOURCE.md` 含 url / ref / license / retrieved_at
- [ ] **已阅读安全检查报告**；结论：`PASS_WITH_WARNINGS`（见下；须人类勾选）
- [ ] 无未接受的 `critical`（当前 critical=0）；warn：接受 `license-unknown`（原因：仅 skill 子树无 LICENSE，仓库根 LICENSE=MIT）
- [ ] **批准人签字/日期（人类）：** _______________

## Gate C — 合入 vault / registry

- [x] 路径：`vault/imported/ops/ocr/`（材料已落盘；签字仍须人类）
- [x] `registry/sources.yaml` 已更新
- [ ] PR 链接：
- [ ] CI 绿（待 PR）
- [ ] **批准人签字/日期（人类）：** _______________

## 对话记录（非签字）

- 2026-10-03：调研 PDF/OCR skill 后用户指定「收纳 ledin-pro/ocr」→ 起草本 intent，停在 Gate A。
- 2026-10-03：用户问是否依赖 PaddleOCR → 答复：否，可选引擎；默认 tesseract。
- 2026-10-03：用户「值得收」→ 视为 Gate A 继续授权；**批准人签字栏仍须人类手填**，Agent 不代签。
- Fetch：`py cli/sv.py import …/tree/main/skills/ocr --ref 396fae9…` → `.cache/import/7e9a837f5def`
- Security：`PASS_WITH_WARNINGS`（`license-unknown` warn：cache 内无 LICENSE 文件；上游仓库 LICENSE 为 MIT，已在 Gate A / SOURCE 记录）
- 转化草稿：`.cache/import/7e9a837f5def-converted/ocr/`
- 2026-10-03：用户「确认」→ 视为 Gate B 合入授权；**批准人签字栏仍须人类手填**，Agent 不代签。
- 已写入：`vault/imported/ops/ocr/`；已更新 `registry/sources.yaml` + catalog + 中文简介；warn `license-unknown` 按「仓库根 MIT」接受说明写入 SOURCE/intent。

## 备注

### 解决什么重复问题 / 哪条制度要一致执行

- 遇到「PDF 全是图片 / 不可选中文字」时，各项目各自拼 pytesseract、pdf2image、Marker，行为不一致
- 希望固定流程：探测文本层 → 原生抽取/表格 → 失败则 OCR 引擎递进 → 可选 searchable PDF / Markdown
- 这是**跨项目可复用的文档抽取制度**，适合 Skill

### 适用 / 不适用

- **适用：** 扫描 PDF、纯图 PDF、截图/收据/证件图、多语言（含西里尔等）、文本 PDF 表格（Camelot）、产出 md/txt/json/searchable-pdf
- **不适用：** 纯排版「生成精美 PDF」设计工具；不替代商业合规 PDF/A 流水线（可用 Nutrient 等另议）；不捆绑安装全部 OCR 引擎权重

### 为何不该只写进某仓 CLAUDE.md

- 上游同时发布 PyPI CLI + skill 规程 + engines 参考；属可安装制度包
- 需跨 IDE / 多机一致；依赖与引擎选择需在 skill 内写清

### 上游包形态（转化时注意）

```text
skills/ocr/
  SKILL.md
  references/
    benchmark.md
    engine-setup.md
    engines.md
    peepshow-sinks.md
    troubleshooting.md
```

- **运行时：** `pip install pro-ledin-ocr`（可选 extras：`pdf` / `pytesseract` / `easyocr` / `paddle` / `all`）
- skill 正文假定本机已有 `ocr` CLI；转化时保留该约定，并在 `compatibility` / Notes 标明依赖与 Windows Poppler/Tesseract 等外部二进制
- `peepshow-sinks` 为可选周边；若不需要可保留 references（文档）但不强制安装 peepshow

### 已知风险（Gate B 重点）

1. **外部依赖重：** OCR 引擎（尤其 Paddle/EasyOCR）体积大；默认应文档化「最小安装」路径（如 tesseract + pymupdf），勿暗示必须 `all`
2. **网络/vision：** `--engine vision` / API key 路径 → 安全扫描关注 `exfil-hint`；转化时强调「须用户明确授权才调用云 API」
3. **name 过短：** `ocr` 合法但泛；若日后冲突可考虑别名，当前 vault 无冲突
4. **上游活跃度：** star 少、最近 release 0.7.0（2026-08）；许可清晰，但需接受「小众维护」风险
5. **无 skill 内 scripts：** 不触发 `scripts/tests.yaml`；勿把整个 `src/pro` 拷进 vault（只收 skill 目录；引擎走 PyPI）
