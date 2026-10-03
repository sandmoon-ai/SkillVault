# 上游定时检知 + 自动 Issue

**状态：** 已实现（`sv watch upstream` + `.github/workflows/upstream-watch.yml`）  

**关联：** [`cli/sync_cmd.py`](../../cli/sync_cmd.py)、[m2-import.md](./m2-import.md)、[ci.md](../ci.md)、[architecture.md](../architecture.md)

> 与 [m3-sync-harden.md](./m3-sync-harden.md) 的「vault ↔ IDE 有无对照」不同：本文是 **上游 URL ↔ `vault/imported`** 的变更检知。

## 1. 目标

对 `registry/sources.yaml` 中已收录的 Skill，定期检查上游是否相对 vault 有变化；**有 diff 则开 Issue 给 owner 确认**，不停在人审之前的任一步写入 vault。

```text
schedule（每周）
  → 只读 registry 条目
  → 拉取进 .cache + 与 vault/imported 比 diff（等同 sv sync，无 --apply）
  → 无变化：安静成功退出
  → 有变化：创建（或复用）Issue，贴摘要，等人决定是否收纳
```

## 2. 成本与频率（定稿）

| 项 | 选择 | 理由 |
|----|------|------|
| Runner | 仅 `ubuntu-latest` | 公开仓标准分钟免费；禁 Windows/macOS |
| 周期 | **每周 1 次**（如 `cron: 0 3 * * 1` UTC） | 够用；避免高频拉上游 |
| 范围 | **仅 registry 已有条目** | 不扫全网、不发现新 Skill |
| Artifact | **不上传** | 摘要写在 Job log + Issue body |
| Cache | 默认不用；若以后加须受成本卫生检查约束 | |
| 合入 | **Job 内永不 `--apply`** | 人审后本地/PR 再收纳 |

手动触发：`workflow_dispatch` 可选，便于调试。

## 3. 行为规格

### 3.1 检知

对每条 registry skill：

1. 按 `url` + `ref` 拉取到 `.cache`（复用现有 `import_from_url` / `sync_skills` 逻辑）  
2. 与 `vault/imported/<category>/<name>/` 做文件级 diff（排除 `SOURCE.md`、sidecar）  
3. 汇总：`unchanged` | `changed` | `missing-local` | `fetch-failed`

### 3.2 Issue

- **无任一条 changed/missing-local：** 不创建 Issue，exit 0  
- **有变化：**  
  - 标题示例：`[upstream-drift] <name> …`（多条可合并为一个 Issue，或每 skill 一条；**首选合并一条周报 Issue**，降低噪音）  
  - 标签：`upstream-drift`  
  - Body：skill 名、url、ref、diff 条数与前 N 条路径、指向 Actions run 的链接、下一步操作提示  
- **去重：** 若已有 **open** 且带 `upstream-drift` 的 Issue，则 **追加评论** 更新，不重复开新 Issue  
- Assignees：仓库 owner（或 `CODEOWNERS` / 仓库变量 `UPSTREAM_WATCH_ASSIGNEES`）

### 3.3 人确认之后（Job 外）

Owner 在 Issue 上决定后，人工或开 PR：

```text
审 diff →（必要时 AI 再转化 / 补 tests.yaml）→ sv sync <name> --apply 或 PR
→ 各机 install --force
```

定时 Job **不**自动开 PR、不自动改 `main`。

## 4. Workflow 草案（实现时）

路径建议：`.github/workflows/upstream-watch.yml`

```yaml
# 要点（实现对照，非最终文件）
on:
  schedule:
    - cron: "0 3 * * 1"   # 每周一 03:00 UTC
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
      - run: py cli/sv.py sync --all    # 无 --apply；需 CLI 支持稳定非零/零与机器可读摘要
      - # 解析输出：有 drift 则 gh issue create / comment
        env:
          GH_TOKEN: ${{ github.token }}
```

实现前可先给 `sv sync` 增加稳定退出码或 `--json` 摘要（有 drift → exit 2；干净 → 0），便于脚本判断。

## 5. 完成标准

- [x] Workflow 合入；仅 Ubuntu；无 artifact  
- [x] 空 registry 或全无 drift 时不产生 Issue（`publish_watch_issue` 看 `has_drift`）  
- [x] 单测覆盖 change 检测；可用 `workflow_dispatch` 手工跑  
- [x] [ci.md](../ci.md) 与 [status.md](../status.md) 已链到本文  
- [x] 成本卫生检查仍绿（workflow 含 guard）

## 6. 非目标

- 定时自动 `--apply` / 自动合入 vault  
- 发现 registry 之外的新上游 Skill  
- 内容哈希驱动的 vault↔IDE 重装提醒（属 M3 另议）  
- 每小时检知、多 OS 矩阵  
