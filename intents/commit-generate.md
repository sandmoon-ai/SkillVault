# Intent：收录 Skill — `commit-generate`

## 元信息

| 字段 | 内容 |
|------|------|
| 提议日期 | 2026-10-03 |
| 提议人 | sandmoon-ai / SkillVault M2 |
| 来源 URL | https://github.com/agenvoy/skill-commit-generate/tree/master |
| 锁定 ref（commit / tag / branch） | master |
| 许可 | MIT |
| 建议类目 | `engineering` |
| 建议 name（目录名） | commit-generate |
| 是否含 scripts/ | 否 |
| 收录理由 | 小体积 MIT 公开 Skill，走通收录闭环样例（staged diff → 提交说明） |

## Gate A — 是否收录？

- [x] 来源可信、许可兼容  
- [x] 与现有 vault Skill 不重复（或明确替代关系）  
- [x] 类目与 tags 草稿合理  
- [x] 若含脚本：接受「须补 tests.yaml 才能合入」  
- [x] **批准人签字/日期：** moyueshuwx / agent（对话「继续」推进 M2）2026-10-03

## Gate B — 转化后（拉取后填写）

- [x] `.cache` 中内容与来源一致（抽检）  
- [x] `SKILL.md` 符合 Agent Skills；frontmatter 完整  
- [x] `SOURCE.md` 含 url / ref / license / retrieved_at  
- [x] **已阅读安全检查报告**；结论：`PASS`  
- [x] 无未接受的 `critical`；所有 `warn` 已确认  
- [x] **批准人签字/日期：** 2026-10-03（报告：cache `_skillvault_security.md`，verdict PASS）

## Gate C — 合入 vault / registry

- [x] 路径：`vault/imported/engineering/commit-generate/`  
- [x] `registry/sources.yaml` 已更新  
- [x] PR 链接：（合入本样例的 PR）  
- [x] CI 绿（含脚本测试若适用）  
- [x] **批准人签字/日期：** 2026-10-03

## 备注

安全扫描 v1：`PASS`（critical=0, warn=0）。未做语义大改，以 upstream 正文合入并保留 LICENSE / doc。
