# M2 — 收录闭环设计

**状态：** 设计已定；样例收录待做  
**关联：** [meta-skills/import-from-url](../../meta-skills/import-from-url/SKILL.md)、[`cli/import_cmd.py`](../../cli/import_cmd.py)、[architecture.md](../architecture.md) 门禁 A–C

## 1. 目标

走通一条完整收录链路：

```text
intent（Gate A）→ 拉取进 .cache → 安全检查报告
  → 转化 + SOURCE.md（Gate B：同时审 diff + 安全报告）
  → vault/imported/<category>/<name>/ + registry（Gate C）
```

产出至少 **1 个真实公开 Skill** 样例（许可兼容），并固定 intent 模板与操作剧本。  
安全检查规格见 [import-security.md](./import-security.md)。

## 2. 门禁与产物

| 门禁 | 人审点 | 产物 |
|------|--------|------|
| A | 是否收录、类目草稿、许可风险 | `intents/<slug>.md` |
| B | 转化是否忠实、**安全报告**、是否越权进 vault | `.cache/...` + 转化草稿 + `SOURCE.md` + `_skillvault_security.md` |
| C | 是否合入 vault / registry | `vault/imported/...` + `registry/sources.yaml` |

默认：拉取**只进 `.cache`**。合入须显式 `--apply`（CLI）或人确认（AI）。

## 3. Intent 模板

路径：[`intents/_template-import.md`](../../intents/_template-import.md)

每条收录复制为 `intents/<skill-or-slug>.md`，至少填：

- 来源 URL / commit 或 tag  
- 许可  
- 目标类目（`taxonomy` 之一）  
- 为何收录、是否含脚本  
- Gate A 勾选  

Gate A 通过前：**不跑** `sv import` 合入动作。

## 4. CLI / AI 行为规格

### 4.1 CLI

```bash
# 仅拉取到 .cache（默认）
py cli/sv.py import <url> [--ref <ref>] [--name <name>]

# Gate B/C 后人审通过后合入
py cli/sv.py import <url> --apply --category <cat> [--name <name>] [--ref <ref>]
```

合入时：

1. 写入 `vault/imported/<category>/<name>/`（整树复制，保留 `SKILL.md`）  
2. 生成或保留 `SOURCE.md`（url、ref、retrieved_at、license 摘要）  
3. 更新 `registry/sources.yaml` 一条记录  

### 4.2 AI（meta-skill）

按 `import-from-url`：先写 intent → 用户 Gate A → fetch 摘要 → **安全检查** → 转化 → Gate B（**须展示安全报告**）→ 合入提案 → Gate C。  
禁止跳过门禁或跳过安全报告直接写 vault。

## 5. 样例收录要求

| 项 | 要求 |
|----|------|
| 来源 | 真实公开仓库中的 Agent Skills 兼容包（含 `SKILL.md`） |
| 许可 | MIT / Apache-2.0 / 兼容的宽松许可；在 SOURCE.md 注明 |
| 类目 | 优先 `inbox`，确认后迁入正式类目；或直接选正确类目 |
| 脚本 | 若含 `scripts/`，必须补 `scripts/tests.yaml` 且 CI 通过，否则不合入 |
| Registry | `id`、`source`、`ref`、`license`、`category`、`imported_at` |

**选型原则（本周期）：** 优先小体积、无密钥、结构清晰的示例 Skill；避免整仓镜像。

## 6. 实现任务拆解

1. 落地 `intents/_template-import.md`（与本设计同步）  
2. 实现安全检查（见 [import-security.md](./import-security.md)）并挂到 import  
3. 选定公开 Skill → 填 intent → Gate A  
4. `sv import` 或 AI 通路进 `.cache` → scan → 转化 → Gate B（含报告）  
5. `--apply` 合入 + registry → PR → Gate C  
6. 回填下方验收记录与 [status.md](../status.md)  

## 7. 完成标准

- [ ] intent 模板已存在并可复制使用  
- [ ] 收录前安全检查可用，Gate B 展示报告  
- [ ] 至少 1 个 `vault/imported/<category>/<name>/` 含 `SKILL.md` + `SOURCE.md`  
- [ ] `registry/sources.yaml` 有对应条目  
- [ ] 若含脚本：`scripts/tests.yaml` + CI 绿  
- [ ] 验收记录已填  

## 8. 验收记录（实现后填写）

| 日期 | Skill name | 来源 URL | category | 许可 | PR |
|------|------------|----------|----------|------|-----|
| _待填_ | | | | | |

## 9. 上游再更新（衔接）

收录进 registry 之后的**定时检知**不在本里程碑实现，规格见 [upstream-watch.md](./upstream-watch.md)：每周 Ubuntu 跑 sync（无 `--apply`），有 diff 开/更新 Issue，人确认后再收纳。

## 10. 非目标（M2）

- 批量自动收录多源  
- 非 Skill 文档的全量魔法转换  
- 跳过人审的「一键进 vault」  
- 定时自动合入上游（仅检知 + Issue，见上游设计）  
- 无安全报告的 Gate B「口头确认合入」  
