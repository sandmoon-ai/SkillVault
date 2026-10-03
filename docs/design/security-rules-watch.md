# 安全规则定期检知 + 自动 Issue

**状态：** 设计已定；实现待做（建议在 `cli/security_rules.yaml` 与首版 scanner 落地之后）  
**关联：** [import-security.md](./import-security.md)、[upstream-watch.md](./upstream-watch.md)、[ci.md](../ci.md)

## 1. 目标

安全规则会过时；用定时作业**收集上游规则/扫描器变更线索并开 Issue**，由人决定是否采纳进本仓 `cli/security_rules.yaml`（或可选集成配置）。

```text
schedule（每月，或与上游检知错开的每周）
  → 读取本仓「规则来源钉扎」清单
  → 拉取各来源的版本/日期/changelog 摘要（只读，不改规则文件）
  → 相对上次已知指纹无变化：安静退出
  → 有变化：开/更新 Issue（label: security-rules），等人决定采纳与否
```

**Job 绝不自动合并规则、不自动改 `security_rules.yaml`。**

## 2. 与「上游 Skill 检知」的分工

| | [upstream-watch](./upstream-watch.md) | 本文 |
|--|--------------------------------------|------|
| 对象 | 已收录 Skill 的内容 drift | 安全**规则来源**的版本 drift |
| Issue 标签 | `upstream-drift` | `security-rules` |
| 人确认后动作 | 收纳/更新 vault Skill | 改规则 YAML / 升依赖 / 写采纳说明 |

可共用同一 workflow 文件的两个 job，或分两个 workflow；成本策略一致。

## 3. 成本与频率（定稿）

| 项 | 选择 | 理由 |
|----|------|------|
| Runner | 仅 `ubuntu-latest` | 公开仓分钟免费 |
| 周期 | **每月 1 次**（如 `cron: 0 4 1 * *` UTC）；另加 `workflow_dispatch` | 规则变慢于 Skill 内容；降噪音 |
| 网络 | 只请求钉扎的少量 URL / GitHub API（releases、raw 规则页） | 不做全网爬取 |
| Artifact | 不上传 | 摘要进 Issue |
| 合入 | 永不自动改规则文件 | 人审后 PR |

## 4. 规则来源钉扎（本仓维护）

建议路径：`registry/security_sources.yaml`（或 `cli/security_sources.yaml`）。

每条至少：

| 字段 | 含义 |
|------|------|
| `id` | 如 `skillsafe-ruleset`、`skillspector`、`gitleaks`、`owasp-ast10-checklist` |
| `url` | 规则页 / release / raw 文件 |
| `kind` | `html` \| `github-release` \| `raw` \| `git-tag` |
| `track` | 关注什么：页面内版本号、latest tag、文件 hash |
| `last_seen` | 上次检知到的指纹（version / etag / sha256） |
| `notes` | 采纳策略备注（例如「只采凭证类」「仅作对照不直接拷贝」） |

**初始钉扎（与 [import-security §10](./import-security.md) 对齐）：**

1. SkillSafe 最新 ruleset 页（或版本化 URL）  
2. NVIDIA SkillSpector GitHub `latest` release  
3. Gitleaks 规则仓库 / release（若 v1 复用其思路）  
4. OWASP Agentic Skills Top 10 checklist 页面或仓库 commit  

来源可增删，但须经 PR 改钉扎文件（本身也走人审）。

## 5. 检知与 Issue 行为

### 5.1 检知

对每条 source：

1. 按 `kind` 取当前指纹（release tag、页面标题中的 `vYYYY.MM.DD`、raw 文件 sha256 等）  
2. 与 `last_seen` 比较  
3. 变化则记入本轮报告；可选抓 changelog 前几行（截断，防超大 body）

失败（404/限流）：该条标 `fetch-failed`，不阻断整 job；连续失败可写进同一 Issue 的「源不可达」节。

### 5.2 Issue

- **无任何变化：** 不创建 Issue，exit 0  
- **有变化：**  
  - 标签：`security-rules`  
  - 标题：`[security-rules] upstream rule sources updated (YYYY-MM)`  
  - Body：来源 id、旧指纹 → 新指纹、链接、简短 diff/changelog、**建议动作模板**（见下）  
  - **去重：** 若已有 open 的 `security-rules` Issue，则追加评论，不新开  
- Assignees：owner / 仓库变量  

### 5.3 人确认后的建议动作（写在 Issue 模板里）

```text
- [ ] 已阅读上游变更说明
- [ ] 决定：采纳 / 部分采纳 / 忽略（写原因）
- [ ] 若采纳：开 PR 更新 cli/security_rules.yaml（及单测夹具）
- [ ] 更新 registry/security_sources.yaml 的 last_seen
- [ ] （可选）对本仓 vault/imported 抽检重跑 sv security-scan
```

关闭 Issue 前应留下采纳结论，便于审计。

## 6. Workflow 草案

路径建议：`.github/workflows/security-rules-watch.yml`

```yaml
# 要点（实现对照）
on:
  schedule:
    - cron: "0 4 1 * *"   # 每月 1 日 04:00 UTC
  workflow_dispatch:

permissions:
  contents: read
  issues: write

jobs:
  watch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -e .
      - run: py cli/sv.py security-rules-watch   # 只读检知；打印 JSON 摘要
      - # 有 drift → gh issue create / comment
        env:
          GH_TOKEN: ${{ github.token }}
```

实现可先做独立小脚本，再挂到 `sv` 子命令。

## 7. 完成标准

- [ ] `security_sources.yaml` 钉扎 ≥3 个来源  
- [ ] 定时/手动 workflow：无变化安静；有变化开/更新 Issue  
- [ ] Issue 含「采纳勾选」模板；文档写明不自动改规则  
- [ ] 成本卫生检查仍绿  
- [ ] [import-security.md](./import-security.md) / [status.md](../status.md) 已链接  

## 8. 非目标

- 自动 PR 合并上游规则全文（许可与误报风险高）  
- 自动升高危规则级别而不经人审  
- 每日检知、多 OS runner  
- 替代漏洞情报订阅的完整 SOC 流程  
