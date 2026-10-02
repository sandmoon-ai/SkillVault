# SkillVault

个人 Agent Skill 仓库：自建与收录的 Cursor / MCP Skills 统一版本管理，可在桌面、笔记本与云端环境间同步；对来自公开项目的 Skill，可跟踪上游并自动更新。

## 为什么需要 SkillVault

- **多机一致**：不同电脑上的 `~/.cursor/skills` 容易漂移，用 Git 当唯一真相源。
- **自建 + 收录**：自己的 Skill 与公开项目 Skill 分目录存放，职责清晰。
- **上游可更新**：收录的公开 Skill 绑定来源仓库/路径，一键拉取最新版本。
- **可审计**：每次变更都有 commit，方便回滚与对比。

## 目录结构

```text
SkillVault/
├── own/                    # 自己编写的 Skill（完整纳入版本控制）
│   └── example-skill/
│       └── SKILL.md
├── vendor/                 # 从公开项目收录的 Skill（由同步脚本维护）
│   └── upstream-name/
│       └── skill-name/
│           └── SKILL.md
├── sources.yaml            # 公开 Skill 的上游来源清单
├── scripts/
│   └── sync-vendor.sh      # 按 sources.yaml 拉取/更新 vendor
├── install.sh              # 将本仓库 Skill 链接/同步到本地 Cursor
└── README.md
```

| 目录 | 用途 | 是否手改 |
|------|------|----------|
| `own/` | 个人/团队自建 Skill | 是，直接编辑并 commit |
| `vendor/` | 镜像公开上游的 Skill | 否，由 `sync-vendor` 生成 |
| `sources.yaml` | 声明上游仓库、路径、目标目录 | 是，增删收录来源时改 |

每个 Skill 为独立目录，且必须包含 `SKILL.md`（含 YAML frontmatter：`name`、`description` 等）。规范参见 [Cursor Agent Skills](https://cursor.com/docs)。

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/sandmoon-ai/SkillVault.git
cd SkillVault
```

### 2. 安装到本机 Cursor

将仓库中的 Skill 同步到 Cursor 个人 Skill 目录（跨平台路径）：

| 系统 | 典型路径 |
|------|----------|
| macOS / Linux | `~/.cursor/skills` |
| Windows | `%USERPROFILE%\.cursor\skills` |

推荐用符号链接或同步脚本，避免在多处各改一份：

```bash
# macOS / Linux 示例：把 own + vendor 链到 ~/.cursor/skills
./install.sh

# 或手动：把 SkillVault/own/* 与 SkillVault/vendor/*/*/ 放到 ~/.cursor/skills/
```

Windows（PowerShell）可先 clone，再按需创建 junction/symlink，或定期 `robocopy` / 脚本同步到 `%USERPROFILE%\.cursor\skills`。

### 3. 新机器上线检查清单

1. Clone 本仓库（或 `git pull`）
2. 运行 `./scripts/sync-vendor.sh`（或对应平台脚本）更新公开 Skill
3. 运行 `./install.sh` 安装到本地 Cursor
4. 重启 Cursor 或重新打开 Agent，确认 Skill 已出现

## 公开 Skill 自动更新

### 来源清单 `sources.yaml`

用清单声明每个收录 Skill 的上游，例如：

```yaml
# sources.yaml
skills:
  - name: example-public-skill
    repo: https://github.com/org/awesome-skills.git
    ref: main                    # branch / tag / commit
    path: skills/example         # 上游仓库内路径
    target: vendor/org/example-public-skill
    license: MIT                 # 可选，便于合规核对
```

### 同步流程

```bash
./scripts/sync-vendor.sh
# 1. 按 sources.yaml 浅克隆或拉取上游
# 2. 将指定 path 同步到 target
# 3. 若有变更，可自动 git add + 提示 commit
```

建议工作流：

1. **定时或换机时**运行 sync，检查 `git status`
2. 上游有更新 → 审阅 diff → commit → push
3. 其他机器 `git pull` + `install` 即与上游对齐

也可在 CI（如 GitHub Actions）中定时跑 sync，发现更新时开 PR，实现「自动检测、人工合并」。

### 收录新公开 Skill

1. 在 `sources.yaml` 增加一条来源
2. 运行 sync 脚本生成 `vendor/...`
3. 确认许可证与用途合适后 commit
4. 本机执行 install，验证 Agent 能正确加载

**注意**：不要直接手改 `vendor/` 下的文件；需要定制时，在 `own/` 中 fork 一份并注明源自何处。

## 自建 Skill

在 `own/<skill-name>/` 下创建：

```text
own/my-workflow/
├── SKILL.md          # 必需
├── reference.md      # 可选：长文档
├── examples.md       # 可选：示例
└── scripts/          # 可选：辅助脚本
```

`SKILL.md` 最小模板：

```markdown
---
name: my-workflow
description: 一句话说明做什么、何时使用
---

# My Workflow

## 何时使用
...

## 步骤
...
```

写完后：

```bash
git add own/my-workflow
git commit -m "Add own skill: my-workflow"
git push
# 其他机器 pull 后重新 install
```

## 推荐约定

- **命名**：Skill 目录与 frontmatter `name` 使用小写 + 连字符（如 `folder-structure`）。
- **边界**：`own` 可自由迭代；`vendor` 只通过 sync 更新。
- **密钥**：切勿把 API Key、token、私钥写进 Skill 或 commit。
- **体积**：大二进制、数据集不要放进仓库；用链接或外部存储。
- **许可**：收录第三方 Skill 时保留其 LICENSE / 版权声明。

## 多机同步模式（任选）

| 模式 | 做法 | 适合 |
|------|------|------|
| Git 中心 | 各机 clone，改完 push / pull | 默认推荐 |
| 符号链接 | 本地 `~/.cursor/skills` → 指向本仓库 checkout | 单机开发最省事 |
| CI 跟上游 | Actions 定时 sync 并开 PR | 想少操心公开 Skill 更新 |

## 路线图（可选后续）

- [ ] 完善 `install.sh` / Windows `install.ps1`
- [ ] 完善 `scripts/sync-vendor.sh`（浅克隆、ref 锁定、变更报告）
- [ ] GitHub Actions：定时检测上游更新并创建 PR
- [ ] Skill 索引页（名称、来源、上次同步时间）

## 许可证

本仓库整体以 [MIT License](./LICENSE) 发布。`vendor/` 下各 Skill 遵循其**各自上游许可证**；收录时请保留原作者声明。
