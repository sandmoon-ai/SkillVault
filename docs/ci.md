# 这个项目的 CI 是什么、怎么用

## 用一句话理解 CI

**CI（Continuous Integration，持续集成）** =  
别人（或你自己）把代码推到 GitHub 后，**自动在云端再跑一遍检查**；不过就标红，提醒「这段改动有问题」。

它不替代你本机开发，而是多一层「公共、可重复、谁都绕不过（若开启保护）」的质检。

## 和本机测试的关系

| | 本机 | CI（GitHub Actions） |
|--|------|----------------------|
| 谁跑 | 你自己执行 `pytest` | GitHub 的虚拟机自动跑 |
| 环境 | 你的 Windows/软件版本 | 干净的 Ubuntu + 指定 Python |
| 作用 | 改代码时快速反馈 | 对所有贡献者一视同仁的门禁 |
| 能否强制别人 | 不能 | 开启「必需检查」后可以 |

本仓库当前 CI 主要跑：

```bash
python -m pytest tests/test_skill_scripts.py -v
```

对应文件：[`.github/workflows/ci.yml`](../.github/workflows/ci.yml)。

## 一次 CI 在干什么（流程）

```text
你 push / 开 PR
      ↓
GitHub 读到 .github/workflows/ci.yml
      ↓
租一台干净的 ubuntu 虚拟机
      ↓
checkout 代码 → 装 Python → pip install → pytest
      ↓
网页上显示 ✅ 通过 或 ❌ 失败（点进 Actions 看日志）
```

关键概念：

- **Workflow（工作流）**：一个 `ci.yml`，定义「何时跑、跑什么」
- **Trigger（触发）**：例如 push 到 `main`、或针对 `main` 的 pull_request
- **Job（任务）**：一台机器上的一组步骤（我们现在只有 `skill-script-tests`）
- **Step（步骤）**：checkout、setup-python、install、pytest
- **Status check（状态检查）**：这次运行的结果名字，可供分支保护勾选

## 怎样算「强制」其他提交者

只加 workflow **还不够**：失败时只会显示红叉，有权限的人仍可能强行合并。

要强制：

1. 仓库 Settings → **Rules** / **Branches** → 保护 `main`
2. 勾选 **Require status checks to pass**
3. 选中检查名（一般是 job 名，如 `Skill script tests`）
4. （建议）关掉 “Allow administrators to bypass”

这样：PR 里 CI 不过 → **不能点 Merge**。

> 私有仓库的 Actions 分钟数有额度限制；公开仓库的 Linux 托管 runner 通常更宽松。以 GitHub 当前计费说明为准。

## 你日常怎么用

**开发时（可选但推荐）：**

```bash
py -m pip install -e ".[dev]"
py -m pytest tests/test_skill_scripts.py -v
```

**推到 GitHub 后：**

1. 打开仓库 → **Actions** 标签，看本次运行是否绿  
2. 或打开 PR，看检查列表里的 `Skill script tests`

失败了：点进日志，修脚本或 `scripts/tests.yaml`，再 push，CI 会再跑一轮。

## 以后可以加什么（不必现在做）

- CLI 单元测试（`cli/` 路径解析、frontmatter 裁剪）
- 多 OS 矩阵（`windows-latest` + `ubuntu-latest`）——脚本跨平台更严
- sync 上游的定时任务（那是 CD/自动化的另一种用法，和「每次 PR 质检」不同）

先把「PR 必跑 skill 脚本测试」稳住，就够用。
