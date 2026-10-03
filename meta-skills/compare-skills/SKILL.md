---
name: compare-skills
description: >-
  Compare SkillVault remote vs local clone, then vault skills vs user-level IDE
  skills (treating IDE/plugin-managed skills as installed without version
  maintenance). Use when the user asks to check skill updates, compare vault to
  installed skills, sync skill versions, doctor with content diff, or
  对比 skill / 检查更新 / 有没有新 skill 可装.
---

# Compare Skills（Vault ↔ 本机）

对照两层差异，并在确认后按 [`meta-skills/install`](../install/SKILL.md) 安装或更新。

| 层 | 比什么 | 默认策略 |
|----|--------|----------|
| A. 仓库 | 本地 clone vs 远端默认分支 | **直接对齐最新**：`fetch` 后若落后则建议 `pull`，再比 skill |
| B. Skill | vault 包 vs 用户级 IDE 安装 | 有更新 / 未装 → 询问是否安装或更新 |

与 `sv doctor` 的区别：doctor **只比目录名**；本 skill **比内容**（可装文件集），并识别 **plugin / 内置** 来源。

## 默认

- Scope = **user**（用户级）；未明确要求不做 project
- 须弄清 **IDE + OS**；缺了就问
- **不**自动 `pull`、**不**自动安装/覆盖——只报告，等人确认
- Plugin / IDE 内置 skill：**算已安装**，**不做版本维护**，默认不提议用 vault 覆盖

## 进度条

```text
Compare Skills:
- [ ] 1. 确认 IDE / OS / scope（默认 user）
- [ ] 2. 层 A：远端 vs 本地仓库（对齐最新）
- [ ] 3. 层 B：扫描 vault / 用户级 / plugin·内置
- [ ] 4. 内容比对 → 分类报告
- [ ] 5. 询问安装或更新；确认后走 install 规程
```

---

## 层 A — 远端仓库 vs 本地

**推荐：不要维护 SkillVault「整库 semver」对比；直接拿远端最新再比 skill。**

本库以 git 为真相源，vault 内容随 commit 变。整库版本号既不可靠也不必要。

### 步骤

1. 确认当前目录是 SkillVault 仓库根（含 `vault/`、`meta-skills/`、`cli/`）。
2. 解析远端默认分支（常见 `origin/main`；以 `git rev-parse --abbrev-ref origin/HEAD` 为准）。
3. 执行：

```bash
git fetch origin
git rev-parse HEAD
git rev-parse origin/<default-branch>
git status -sb
```

4. 判定：

| 状态 | 含义 | 动作 |
|------|------|------|
| HEAD == origin/<branch> 且工作区干净 | 已是最新 | 进入层 B |
| HEAD 落后于 origin | 本地旧 | **建议 pull**；确认后 `git pull --ff-only`，再进层 B |
| HEAD 超前 / 分叉 / 脏工作区 | 勿瞎 pull | 说明状况；征得同意后再决定 rebase/merge/stash；skill 对比可基于**当前工作区**继续，并注明「非远端 tip」 |

网络失败：跳过层 A，标明「未校验远端」，用当前本地 vault 做层 B。

---

## 层 B — Vault Skill vs 本机用户级

### B1. 收集三侧名单

**Vault（真相源）**  
扫描 `vault/own/**/SKILL.md` 与 `vault/imported/**/SKILL.md`（跳过 `_template`）。  
Skill 名 = 含 `SKILL.md` 的目录名（扁平名，不含 category）。

**用户级 IDE（可维护）**  
按 [`adapters/targets.yaml`](../../adapters/targets.yaml) 解析 `ides.<ide>.user.<os>`，列出一级子目录名。  
Cursor 例：`{home}/.cursor/skills/<name>/`。

**Plugin / 内置（只认领有，不维护版本）** — 按 IDE 探测，能扫到即可：

| IDE | 典型路径（存在则扫） |
|-----|----------------------|
| cursor | `{home}/.cursor/skills-cursor/<name>/`（内置） |
| cursor | `{home}/.cursor/plugins/cache/**/skills/<name>/` 或 cache 下含 `SKILL.md` 的包目录 |
| claude-code | 插件/marketplace 安装根（若可定位） |
| 其他 | 未知则跳过，在报告注明「未探测 plugin 路径」 |

同名出现在多处 plugin 路径：合并为一条 `plugin_or_builtin`，路径都列上。

### B2. 内容指纹（仅用户级 ↔ vault）

对「可安装载荷」做指纹，**排除**安装时不会进 IDE 的文件：

- 排除：`SOURCE.md`、`tests.yaml`、`.gitkeep`、`HISTORY.md`、`_skillvault_*`
- 纳入：`SKILL.md`、`references/`、`scripts/`（除 `tests.yaml`）、其他将被 `install` 复制的文件
- 算法：对纳入文件按相对路径排序，逐文件规范化换行（CRLF→LF）后算哈希，再合成包指纹  
  （PowerShell / Python 均可；一致即可，同一轮内同一算法）

可选辅助信号（不替代指纹）：

- 两侧 `metadata.version` / `version` frontmatter → 写入报告作提示
- 仅当**双方都有**可解析 semver 且 vault > local 时，可标注 `version_hint: newer`；指纹相同则仍算一致

**Plugin / 内置：不算指纹、不比版本。**

### B3. 分类

对每个 vault skill 名：

| 状态 | 条件 | 是否提示动作 |
|------|------|----------------|
| `current` | 用户级有且指纹与 vault 相同 | 否 |
| `update_available` | 用户级有且指纹不同 | **是** → 是否 `install --force` 更新 |
| `pending_install` | 用户级无，且 **不在** plugin/内置 | **是** → 是否安装 |
| `covered_by_plugin` | 用户级无，但 plugin/内置有同名 | 否（默认）。报告为「已由 plugin/内置提供，不做版本维护」；仅当用户明确要 vault 治理副本时才提议安装 |
| `orphan_user` | 用户级有、vault 无 | 告知；不自动删 |
| `plugin_only` | 仅 plugin/内置有、vault 无 | 列出即可；不维护 |

同名同时在用户级与 plugin：以**用户级**为准做指纹对比；报告中附注「plugin 亦存在」。

---

## 报告格式

```markdown
# Skill 对比报告

## 仓库
- 本地: <short-sha> | 远端: <short-sha> (<branch>) | 状态: up_to_date | behind | diverged | dirty | fetch_failed
- 说明: …

## 环境
- IDE / OS / scope / 用户级根路径
- Plugin/内置根: <paths or "未探测">

## 摘要
- current: N
- update_available: N
- pending_install: N
- covered_by_plugin: N
- orphan_user: N

## 待处理
### 可更新
| name | vault 指纹 | 本地指纹 | version hint | 建议 |
|------|------------|----------|--------------|------|
| … | … | … | … | install --force |

### 未安装（vault 有）
| name | category | 建议 |
|------|----------|------|
| … | … | install |

### 已由 plugin/内置覆盖（不维护版本）
| name | plugin 路径 |
|------|-------------|
| … | … |

## 仅供参考
- orphan_user / plugin_only / current（可折叠或只给计数）
```

---

## 确认与执行

1. 展示报告后，列出可操作项（`update_available` + `pending_install`）。
2. 询问用户：全部 / 指定名单 / 跳过。  
   - `covered_by_plugin` **默认不列入**可操作项；用户点名要 vault 副本时再装。
3. 用户确认后，严格按 [`meta-skills/install`](../install/SKILL.md)：
   - 复述目标绝对路径 → Gate → 复制（更新等价 `--force`）
   - 或：`py cli/sv.py install <name> --ide <ide> --os <os> [--force]`
4. 装完可再跑一轮层 B（跳过层 A）核对。

## CLI 捷径（可选）

有无对照可先看名字：

```bash
py cli/sv.py doctor --ide <ide> --os <os>
```

doctor **不含**内容指纹与 plugin 识别；本 skill 的结论以层 B 为准。

## 不要

- 把 plugin/内置 skill 当「过期」并默认用 vault 覆盖
- 在脏/分叉工作区强行 `pull`
- 跳过确认批量写用户级目录
- 与 `sv sync`（上游 registry 再拉取）混淆——那是另一条链
- 发明整库版本号协议替代 git tip 对比
```
