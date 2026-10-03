# Issue 与 Milestone 标准

**状态：** 设计已定；用于制造工程推进  
**关联：** [design/README.md](./README.md)、[CONTRIBUTING.zh-CN.md](../../CONTRIBUTING.zh-CN.md)、[ci.md](../ci.md)

制造阶段用 **GitHub Milestone + Issue + PR** 跟踪进度。设计真相源仍是 `docs/design/*`；Issue 只承载可执行切片，不另起叙事。

---

## 1. Milestone 标准

### 1.1 何时建

每个**可对外交付的制造阶段**对应 **一个 Milestone**，并与一篇（或一组）设计文档对齐。  
当前建议集合（可按仓库实际增删，标题保持稳定）：

| Milestone 标题 | 对齐设计 | 目标一句话 |
|----------------|----------|------------|
| `M1 — Install loop` | [m1-install.md](./m1-install.md) | 安装行为可测 + Windows 双 IDE 验收 |
| `M2 — Import loop` | [m2-import.md](./m2-import.md)、[import-security.md](./import-security.md) | 门禁收录样例 + 安全扫描进 Gate B |
| `M3 — Sync & harden` | [m3-sync-harden.md](./m3-sync-harden.md) | vault↔IDE 对照可测 + 换机清单 |
| `M4 — Upstream watch` | [upstream-watch.md](./upstream-watch.md) | 定时检知 Skill 上游 → Issue |
| `M5 — Security rules watch` | [security-rules-watch.md](./security-rules-watch.md) | 定时检知规则源 → Issue |

不必一次建齐；**即将开工的下一个**必须先有 Milestone。

### 1.2 命名

```text
M<序号> - <English short name>
```

- 序号与设计执行顺序一致（M1→M2→…）。  
- 短名用英文（GitHub 列表清晰）；Description 可用中文。  
- 标题用 **ASCII 连字符 `-`**（避免 em-dash `—` 在 API/部分环境下乱码）。  
- 用 `gh api` 写 Description 时须 **UTF-8 JSON 文件**（`ensure_ascii=False`）；勿用会丢编码的 PowerShell 管道字符串，否则中文会变成 `?`。  
- **禁止**同一阶段多个 Milestone（如「M1a / M1 补充」）；追加工作进原 Milestone 的新 Issue。

仓库中对应标题示例：`M1 - Install loop` … `M5 - Security rules watch`。

### 1.3 Description 必填结构

```markdown
## 目标
<一句话>

## 设计文档
- docs/design/<file>.md

## 完成定义（DoD）
- [ ] 设计文档「完成标准」全部勾选（或明示砍掉的项）
- [ ] 相关 Issue 全部 closed
- [ ] 验收记录已回填日期/结果
- [ ] 需要的文档（status / README）已刷新

## 非目标
- <从设计文档「非目标」抄 1–3 条>

## 依赖
- 前序 Milestone：<若无写 None>
```

### 1.4 Due date

- 有对外承诺时再填；内部探索可留空。  
- 逾期不自动砍范围：先改 Due 或把 Issue 移出并注明原因。

### 1.5 关闭条件

仅当 Description 中 DoD 勾完，且无 open Issue 挂在该 Milestone（或剩余 Issue 已移出并说明）时关闭。  
关闭后在 [status.md](../status.md) 把对应阶段标为完成。

---

## 2. Issue 标准

### 2.1 类型与标签

| 类型 | 标签（建议） | 用途 |
|------|----------------|------|
| 制造任务 | `type:task` | 实现、单测、workflow、文档落地 |
| 验收 | `type:acceptance` | 实机/换机/样例收录勾选 |
| 缺陷 | `type:bug` | 已合入行为不符合设计 |
| 设计变更 | `type:design` | 要先改 `docs/design/*` 再施工 |
| 收录提案 | `type:import` | 外部/内部提议收某个公开 Skill（走门禁） |
| 杂务 | `type:chore` | 依赖升级、仓库维护（repo hygiene）、无用户可见行为变更 |

可选维度标签（按需）：

- `area:cli` / `area:docs` / `area:ci` / `area:vault` / `area:meta-skill` / `area:security`  
- `good first issue`（对外友好的小切片）

### 2.2 标题

```text
<动词短语>：<对象>
```

示例：

- `添加：paths/install CLI 单测`  
- `验收：Windows 上 cursor + claude-code 安装 hello-skillvault`  
- `实现：sv security-scan 与 import 挂钩`  
- `文档：回填 m1-install 验收记录`

避免：`M1`、`修一下`、`WIP` 当唯一标题。

### 2.3 正文模板（制造 / 验收）

开 Issue 时使用仓库模板，或粘贴：

```markdown
## 背景
<!-- 为什么现在做；链到设计章节 -->

## 设计依据
- 文档：`docs/design/<file>.md` §<节>
- Milestone：M<n>

## 范围
- [ ] …
- [ ] …

## 非范围
- …

## 完成标准
- [ ] …
- [ ] CI 绿（若涉及代码）
- [ ] 设计文档对应勾选已更新（若适用）

## 测试计划
- [ ] 单测 / 手工步骤：…

## 关联
- 阻塞：#…
- 设计讨论：#…（若有）
```

### 2.4 粒度

| 合适 | 不合适 |
|------|--------|
| 一个 PR 能讲完的切片（约 0.5–2 人日） | 「做完整个 M2」一条 Issue |
| 可独立验收（单测绿或验收表可勾） | 纯讨论无产出（用 Discussion / 标 `type:design`） |
| 标题能让外人看懂要交什么 | 依赖未写明的隐式「顺便做」 |

过大则拆子 Issue，用一个 tracking Issue 正文列清单并勾选（父 Issue 可挂同一 Milestone）。

### 2.5 与 PR / 门禁

- 制造 Issue：**一个 PR 关闭一个主 Issue**（`Fixes #n`）；若必须多 PR，在 Issue 中列出子勾选，全部完成后手动 close。  
- 收录类 Issue：PR 须满足 [CONTRIBUTING](../../CONTRIBUTING.zh-CN.md) 与 Gate A–C；维护者在 PR 上确认门禁后再 merge。  
- 禁止用 Issue 代替设计文档的长期规格；规格变了先 `type:design` 改文档，再开/改 task。

### 2.6 状态约定

| 状态 | 含义 |
|------|------|
| Open + 无 assignee | 待认领 |
| Open + assignee | 进行中 |
| Open + label `blocked` | 阻塞（正文写清等谁/等什么） |
| Closed | 完成标准已满足（或 `wontfix` + 原因） |

不使用 Project 看板时，以上即可；若启用 Projects，列名与上表同义映射。

---

## 3. 编号与执行秩序

1. 建（或确认）Milestone → 按设计「实现任务拆解」批量开 Issue 并挂上 Milestone。  
2. 同一 Milestone 内用 Issue 依赖或正文「阻塞」表达顺序（例如：安全扫描落地 → 再开「真实 imported 样例」）。  
3. 开工顺序默认遵循 [design/README.md](./README.md) 的执行顺序；并行仅限无依赖的文档/单测类。

---

## 4. 中英文

- Milestone **标题**英文短名；Description 可用中文。  
- Issue **标题**可用中文（本仓主要协作者）；对外 `good first issue` 可用英文标题 + 正文双语或链到中文设计。  
- 本标准正文以中文为准；英文贡献者见 [CONTRIBUTING.md](../../CONTRIBUTING.md) 与设计文档英文链接。

---

## 5. 建仓检查清单（首次启用）

- [ ] 建立即将开工的 Milestone（含 §1.3 Description）  
- [ ] 启用 Issue 模板（`.github/ISSUE_TEMPLATE/`）  
- [ ] 创建常用 labels（§2.1）  
- [ ] 从当前设计拆第一批 Issue 并挂 Milestone  
- [ ] 在 [status.md](../status.md) 链到本文  

---

## 6. 非目标

- 用 Milestone 替代设计文档  
- 强制 GitHub Projects / 复杂工作流自动化  
- 为每个文档错字开 Milestone  
