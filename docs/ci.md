# 这个项目的 CI 是什么、怎么用

## 用一句话理解 CI

**CI（Continuous Integration，持续集成）** =  
别人（或你自己）把代码推到 GitHub 后，**自动在云端再跑一遍检查**；不过就标红，提醒「这段改动有问题」。

它不替代你本机开发，而是多一层「公共、可重复」的质检。要真正拦住合并，还要配合分支 Ruleset（本仓库已启用，见下文）。

整体进度见 [status.md](./status.md)。

## 和本机测试的关系

| | 本机 | CI（GitHub Actions） |
|--|------|----------------------|
| 谁跑 | 你自己执行 `pytest` | GitHub 的虚拟机自动跑 |
| 环境 | 你的 Windows/软件版本 | 干净的 Ubuntu + 指定 Python |
| 作用 | 改代码时快速反馈 | 对所有贡献者一视同仁的门禁 |
| 能否强制别人 | 不能 | **Ruleset 要求检查通过后可以** |

本仓库当前 CI 主要跑：

1. 成本卫生检查：`.github/scripts/check_actions_cost_hygiene.py`  
2. Skill 脚本冒烟：`python -m pytest tests/test_skill_scripts.py -v`

对应文件：[`.github/workflows/ci.yml`](../.github/workflows/ci.yml)。  
Actions 页面：https://github.com/sandmoon-ai/SkillVault/actions  

## 一次 CI 在干什么（流程）

```text
你 push / 开 PR
      ↓
GitHub 读到 .github/workflows/ci.yml
      ↓
租一台干净的 ubuntu 虚拟机
      ↓
checkout → 成本卫生检查 → 装 Python → pip install → pytest
      ↓
网页上显示 ✅ 通过 或 ❌ 失败（点进 Actions 看日志）
```

关键概念：

- **Workflow（工作流）**：`ci.yml` / `actions-storage-cleanup.yml`
- **Trigger（触发）**：push / PR 到 `main`；清理任务还有每月定时
- **Job**：如 `Skill script tests`
- **Status check**：检查名 **`Skill script tests`**（Ruleset 里勾的就是这个）

## 分支保护（已启用 — Ruleset）

本仓库已用 **方式 A：Ruleset** 保护 `main`（不是仅文档建议）：

| 项 | 值 |
|----|-----|
| 名称 | `protect-main` |
| 状态 | Active |
| 目标 | `refs/heads/main` |
| 必需检查 | `Skill script tests`（要求分支相对基线最新） |
| 其它 | 禁止删除分支、禁止 force push |
| Bypass | 无（当前用户也不可绕过） |
| 必须 PR | **未开启**（仍可直接 push `main`；他人 PR 合并会卡检查） |
| 链接 | https://github.com/sandmoon-ai/SkillVault/rules/24400124 |

查看/修改：仓库 **Settings → Rules → Rulesets**。

若以后要「禁止直接 push、必须走 PR」，在该 Ruleset 中增加 pull request 规则即可。

## 你日常怎么用

**开发时（推荐）：**

```bash
py -m pip install -e ".[dev]"
py -m pytest tests/test_skill_scripts.py -v
```

**推到 GitHub 后：**

1. 打开 **Actions**，看 `CI` 是否绿  
2. 或打开 PR，看检查 **`Skill script tests`**

失败了：点进日志，修脚本或 `scripts/tests.yaml` / workflow 违规写法，再 push。

## 成本与存储防护

计费说明：[GitHub Actions 计费](https://docs.github.com/zh/billing/concepts/product-billing/github-actions)。

| 类型 | 会不会“跑完还一直扣” | 本仓库对策 |
|------|----------------------|------------|
| 运行分钟 | 否，跑完即止 | 默认 `ubuntu-latest`；**公开仓**标准 runner 分钟免费 |
| Artifact 存储 | **会**，按存放小时累计 | 上传必须 `retention-days`≤7；月度清理；**仓库保留期已设为 1 天** |
| Cache 存储 | 超每仓额度才可能收费 | 默认不开 pip cache；用 cache 必须有 `key` |
| 日志 / summary | 不计 artifact 配额 | 无需手动删 |

### 已自动化

1. **每次 CI 卫生检查**：[`.github/scripts/check_actions_cost_hygiene.py`](../.github/scripts/check_actions_cost_hygiene.py)  
2. **每月清理 artifact**：[`.github/workflows/actions-storage-cleanup.yml`](../.github/workflows/actions-storage-cleanup.yml)（删 >7 天；也可手动 Run workflow）

### 仓库网页已配置

- **Settings → Actions → General →** Artifact and log retention = **1 day**（组织上限 90；我们收紧为 1）  
- 保存后对新产生的 artifact/日志生效  

### 以后加功能时

```yaml
# ✅
- uses: actions/upload-artifact@v4
  with:
    name: pytest-report
    path: report/
    retention-days: 1   # 与仓库 1 天策略对齐；且必须 ≤7（CI 硬限制）

# ❌ 禁止没有 retention-days
```

确需 Windows/macOS runner 时，在 workflow 顶部加 `# cost-allow: windows-latest` 并在 PR 说明理由。

### 可选：预算告警

有付款方式时：**Settings → Billing / Budgets** 为 Actions 设告警。

### 当前主 CI 现状

主流程**不上传 artifact、不启用 cache**，跑完无持续计费残留。guard + 月度清理 + 1 天保留，是为以后预留的闸门。

## 计费速记（公开仓）

- 标准 **Ubuntu** GitHub-hosted runner：**分钟免费**  
- 仍可能占额度/产生费用的：artifact、超限 cache、大型/macOS/Windows runner  
- 本仓对策已覆盖「忘记删 artifact」类风险  

## 以后可以加什么（功能向）

- CLI 单元测试  
- 多 OS 矩阵（需 `# cost-allow`）  
- 上游 sync 定时任务（同样遵守产物保留规则）  
