# Intent：收录 Skill — `<skill-name>`

> 复制本文件为 `intents/<skill-name>.md`，填完并完成 Gate A 后再执行拉取/转化。

## 元信息

| 字段 | 内容 |
|------|------|
| 提议日期 | YYYY-MM-DD |
| 提议人 | |
| 来源 URL | |
| 锁定 ref（commit / tag / branch） | |
| 许可 | |
| 建议类目 | `inbox` / `foundation` / …（见 docs/taxonomy.md） |
| 建议 name（目录名） | 须符合 Agent Skills `name` 规则 |
| 是否含 scripts/ | 是 / 否 |
| 收录理由 | 一句话 |

## Gate A — 是否收录？

- [ ] 来源可信、许可兼容  
- [ ] 与现有 vault Skill 不重复（或明确替代关系）  
- [ ] 类目与 tags 草稿合理  
- [ ] 若含脚本：接受「须补 tests.yaml 才能合入」  
- [ ] **批准人签字/日期：** _______________

**Gate A 未勾选完成前：禁止 `sv import --apply`，禁止直接写入 `vault/imported`。**

## Gate B — 转化后（拉取后填写）

- [ ] `.cache` 中内容与来源一致（抽检）  
- [ ] `SKILL.md` 符合 Agent Skills；frontmatter 完整  
- [ ] `SOURCE.md` 含 url / ref / license / retrieved_at  
- [ ] **已阅读安全检查报告**（`_skillvault_security.md` 或等价输出）；结论：`PASS` / `PASS_WITH_WARNINGS` / `FAIL`：_______  
- [ ] 无未接受的 `critical`；所有 `warn` 已确认（接受原因可写在下方备注）  
- [ ] **批准人签字/日期：** _______________

## Gate C — 合入 vault / registry

- [ ] 路径：`vault/imported/<category>/<name>/`  
- [ ] `registry/sources.yaml` 已更新  
- [ ] PR 链接：  
- [ ] CI 绿（含脚本测试若适用）  
- [ ] **批准人签字/日期：** _______________

## 备注

（风险、后续迁移类目、依赖工具等）
