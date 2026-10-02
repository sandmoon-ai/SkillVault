# SkillVault

个人 Agent Skill 仓库：自建与收录的 Skills 统一版本管理，可在桌面、笔记本与云端环境间同步；对来自公开项目的 Skill，可跟踪上游并自动更新。

面向各类支持 Skill / 指令包的 Agent 工具（如 Cursor、Claude Code、Codex、Windsurf 等），本仓库是**中立的内容源**，不绑定某一产品。

## 为什么需要 SkillVault

- **多机一致**：各工具本地 Skill 目录容易漂移，用 Git 当唯一真相源。
- **自建 + 收录**：自己的 Skill 与公开项目 Skill 分目录存放，职责清晰。
- **上游可更新**：收录的公开 Skill 绑定来源仓库/路径，一键拉取最新版本。
- **可审计**：每次变更都有 commit，方便回滚与对比。
- **工具无关**：仓库只存 Skill 内容；安装时再映射到各工具的本地路径。

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
├── targets.yaml            # 各 Agent 工具的本地安装路径（本机/按环境）
├── scripts/
│   └── sync-vendor.sh      # 按 sources.yaml 拉取/更新 vendor
├── install.sh              # 将本仓库 Skill 同步到 targets 中声明的路径
└── README.md
```

| 目录 / 文件 | 用途 | 是否手改 |
|-------------|------|----------|
| `own/` | 个人/团队自建 Skill | 是，直接编辑并 commit |
| `vendor/` | 镜像公开上游的 Skill | 否，由 `sync-vendor` 生成 |
| `sources.yaml` | 声明上游仓库、路径、目标目录 | 是，增删收录来源时改 |
| `targets.yaml` | 声明各工具本机 Skill 目录 | 是，按本机工具配置（可 gitignore 本地覆盖） |

每个 Skill 为独立目录，且必须包含 `SKILL.md`（建议含 YAML frontmatter：`name`、`description` 等）。具体字段以目标工具的 Skill 规范为准；编写时尽量保持通用，避免写死某一产品的专有路径或内部 API。

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/sandmoon-ai/SkillVault.git
cd SkillVault
```

### 2. 配置本机安装目标

在 `targets.yaml` 中声明要用的 Agent 工具及其 Skill 目录，例如：

```yaml
# targets.yaml（示例，按本机实际路径修改）
targets:
  - name: tool-a
    path: ~/.config/tool-a/skills
  - name: tool-b
    path: ~/Library/Application Support/tool-b/skills
  # Windows 示例：
  # - name: tool-c
  #   path: "%USERPROFILE%\\.tool-c\\skills"
```

不同工具的路径各不相同，以各自文档为准。SkillVault 只负责把 `own/` + `vendor/` 同步到你声明的目录。

### 3. 安装到本机

```bash
# 按 targets.yaml 同步 own + vendor
./install.sh

# 或手动：将 SkillVault/own/* 与 SkillVault/vendor/*/*/
# 复制或符号链接到各工具的 Skill 目录
```

Windows 可用 PowerShell 版安装脚本（`install.ps1`），或自行 junction / symlink / 同步。

### 4. 新机器上线检查清单

1. Clone 本仓库（或 `git pull`）
2. 配置或复制本机 `targets.yaml`
3. 运行 sync 更新公开 Skill
4. 运行 install 同步到各工具目录
5. 重启或重新加载对应 Agent，确认 Skill 已出现

## 公开 Skill 自动更新

### 来源清单 `sources.yaml`

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
4. 本机执行 install，在目标 Agent 中验证能否正确加载

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
- **工具中立**：正文避免写死某一产品的内部路径；安装映射放在 `targets.yaml`。
- **密钥**：切勿把 API Key、token、私钥写进 Skill 或 commit。
- **体积**：大二进制、数据集不要放进仓库；用链接或外部存储。
- **许可**：收录第三方 Skill 时保留其 LICENSE / 版权声明。

## 多机同步模式（任选）

| 模式 | 做法 | 适合 |
|------|------|------|
| Git 中心 | 各机 clone，改完 push / pull | 默认推荐 |
| 符号链接 | 工具本地 Skill 目录 → 指向本仓库 checkout | 单机开发最省事 |
| CI 跟上游 | Actions 定时 sync 并开 PR | 想少操心公开 Skill 更新 |

## 路线图（可选后续）

- [ ] 完善 `install.sh` / `install.ps1`（读取 `targets.yaml`）
- [ ] 完善 `scripts/sync-vendor.sh`（浅克隆、ref 锁定、变更报告）
- [ ] GitHub Actions：定时检测上游更新并创建 PR
- [ ] Skill 索引页（名称、来源、上次同步时间、适用工具备注）

## 许可证

本仓库整体以 [MIT License](./LICENSE) 发布。`vendor/` 下各 Skill 遵循其**各自上游许可证**；收录时请保留原作者声明。
