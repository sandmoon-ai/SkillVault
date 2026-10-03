# AI-native SDLC 组合设计：playbook 管全局，Matt 管 Build

**状态：** 草案（2026-10-03），待评审  
**关联：** [architecture.md](../architecture.md)（§3 Skill 边界、§4 产物链、§9 与 SDLC 的关系）、[taxonomy.md](../taxonomy.md)  
**来源：**

- [The AI-native SDLC playbook](https://claude.com/blog/the-ai-native-sdlc-playbook)（Anthropic，2026-08-21）→ 下文简称 **playbook**
- [mattpocock/skills](https://github.com/mattpocock/skills)（含 README、`ask-matt`、`grilling` 等 skill 原文与 aihero.dev 文档）→ 下文简称 **Matt**

**标注约定：** 文中【playbook】【Matt】表示该说法来自原文；【本设计】表示本文自己的取舍或推论，原文没有这样说。

---

## 1. 结论

### 1.1 可行性

**可行。** 两者在同一前提下工作：写代码不再是瓶颈，瓶颈在对齐、评审和治理。两者也共享同一批机制：工件提交进 git、Skill 固化知识、人把关判断、先计划后动手。

分工能成立，是因为边界天然落在工件上：

- Build 的**入口**是 playbook Stage 2 产出的已批准 `spec.md`
- Build 的**出口**是 playbook Stage 5 要审的 PR（附证据）

只要把这两个工件定义成契约，Build 内部就可以整体替换为 Matt 的做法。

### 1.2 不能直接拼的地方

直接拼会遇到 3 处冲突和 4 处缺口，本文给出了处理（详见 §6、§9）。

**3 处冲突：**

| # | 冲突 | 处理（摘要） |
|---|------|--------------|
| C1 | playbook 的 Design 阶段允许无人值守生成 spec；Matt 明确说追问**没有异步模式**，没人回答就只是 agent 的意见 | 引入「决策权规则」：允许自动起草，但取舍型决策必须留作**待决问题**，由人关闭 |
| C2 | playbook 的 Build 以 plan mode 起步；Matt 说追问时**关掉** plan mode | 用「ticket 集合 + 人批准」承担「未批准的计划不得实现」，plan mode 只作可选只读保护 |
| C3 | playbook 的 Design 由产品负责人主导、不需工程技能；Matt 的 `to-spec` 要求写实现决策与测试 seam，需要工程师参与 | spec **两段式**：需求段归产品，实现/测试段在 Build 入口由工程师补 |

**4 处缺口（任何一边都没覆盖）：**

1. Matt 没有 `intent.md` 的模板与采集方式
2. Matt 的 `code-review` 没有安全/合规这一轴
3. Matt 的 skill 是建议性的，没有强制层（hook / CI / 权限）
4. 没有任何一边规定「如何回归测试 skill 本身」（playbook 有 evals 思路，但针对 Claude Code 配置）

### 1.3 与你的分工设想的一个偏差

你的设想是「大方面用 playbook，Build 用 Matt」。Matt 的主流程**不止 Build**：`grill-with-docs`、`to-spec` 在 playbook 的 Plan/Design 阶段（Build 之前）。

本设计的默认做法是：**不把 Matt 前移**。Build 入口先做一轮工程师侧的 `grill-with-docs`，让 Matt 的对齐能力仍然落在 Build 内（见 §5.3）。是否把 Matt 的追问技法前移到 Stage 1–2，作为决策 D4 留给你。

---

## 2. 设计思想

八条原则。每条标明来源。

| # | 原则 | 来源 |
|---|------|------|
| P1 | **工件即接口。** 每阶段以提交一个下一阶段可读的工件结束；下一阶段从读它开始。链上的提交即审计链 | 【playbook】 |
| P2 | **决策权规则。** agent 可以查事实、起草、评审；取舍型决策只能由人做。工件里凡未关闭的取舍问题，必须以「待决问题」显式存在，带着待决问题的工件**不得过门** | 【Matt】grilling 的事实/决策分离，【本设计】把它推广到全链 |
| P3 | **对齐先于动手。** 共识需要人明确确认，之前不实现 | 【Matt】、【playbook】plan mode 的目的 |
| P4 | **反馈环先于产量。** 让 agent 能自己验证工作，再谈并行与自治 | 【playbook】、【Matt】tdd / diagnosing-bugs |
| P5 | **建议与强制分层。** Skill 只提高做对的概率；必须成立的规则交给 hook、CI、权限 | 【playbook】（明确说 skill 是 advisory control） |
| P6 | **知识外置到仓库，分四类：** 词汇（`GLOSSARY.md`）、决策（ADR）、操作约定（`AGENTS.md` / `CLAUDE.md`）、制度（Skills） | 【Matt】前两类，【playbook】后两类，【本设计】合并 |
| P7 | **自治分档。** 自治度按阶段和风险分级，而不是全局一档 | 【playbook】（auto mode、闭环）与【Matt】（人编排）的折中，【本设计】 |
| P8 | **每阶段有先行与滞后指标，且能从 git / PR 历史读出** | 【playbook】 |

### 自治分档（P7 展开）

| 档 | 含义 | 适用 |
|----|------|------|
| L0 | 人做，agent 不介入 | 取舍型决策、过门、生产授权 |
| L1 | agent 起草 / 查证，人审定 | intent、spec 草稿，追问，ticket 拆分 |
| L2 | agent 在门内自主执行，到门前停 | 按 ticket 实现、测试、PR 评审、CI 内判断步骤 |
| L3 | 无人触发的闭环，仅限确定性检测触发 + 门内动作 | Maintain 的 control band 监控 |

---

## 3. 分工边界

### 3.1 阶段 × 来源

| 阶段 | 主导 | 采用什么 | 说明 |
|------|------|----------|------|
| 1 Plan | playbook | `intent.md` 采集；可选 Matt `grill-me` 做访谈 | Matt 没有 intent 模板，需新写（缺口 1） |
| 2 Design | playbook | 组织政策 Skills 约束下生成 `spec.md`；标出关注点 | spec 只含需求段（C3） |
| **3 Build** | **Matt** | `grill-with-docs` → 补实现段 → `to-tickets` → `implement` / `implement-spec` → `tdd` → `code-review` → `pr` → `retro` | 本设计的核心，见 §5.3 |
| 4 Test | 两者叠加 | Matt 的 tdd / diagnosing-bugs + playbook 的反馈环、测试保护、配置 evals | |
| 5 Deploy | playbook 为骨架 | `REVIEW.md` 评审轮次、hook 审批门、CI/CD；Matt `code-review` 的两轴并入评审 | 补安全/合规轴（缺口 2） |
| 6 Maintain | playbook | control band → `intent.md`；Matt `triage` / `diagnosing-bugs` / `retro` 作入口与收尾 | |

### 3.2 Build 的接口契约

**入口门（Build Entry Gate）**——全部满足才能开始 Build：

1. `spec.md` 需求段已由产品负责人批准，且**没有未关闭的待决问题**
2. 仓库已有 `AGENTS.md`（或 `CLAUDE.md`）、`GLOSSARY.md`；issue tracker 已配置（Matt 的 `setup-matt-pocock-skills` 一次性完成）
3. 本次变更涉及的组织政策 Skill（安全、品牌、合规、UX）在 Stage 2 已应用，关注点已有处置

**出口门（Build Exit Gate）**——全部满足才能进入 Stage 5：

1. 所有 ticket 的验收标准满足；全量测试通过（输出已附）
2. 作者侧 `code-review` 已跑，两轴 finding 已处理或显式接受
3. 实现与 spec / tickets 一致；偏离处已在**同一提交**里更新工件
4. PR 已按 `pr` 的形态产出：摘要、前后证据、门类型判断
5. PR 通过分支保护进入 Stage 5；agent 无直接推送主干的路径

---

## 4. 工件链

```text
Stage 1  intent.md            原始意图；originator 的话
           │  Gate 1：产品负责人接受
Stage 2  spec.md（需求段）     问题 / 方案 / 用户故事 / 范围外 / 关注点
           │  Gate 2：产品负责人批准；无待决问题
─────────── Build Entry Gate ───────────
Stage 3  spec.md（实现段）     实现决策 / 测试决策（seam）  ← 工程师补
         GLOSSARY.md / ADR     追问中沉淀
         tickets（= plan）     tracer-bullet 垂直切片 + 阻塞边
           │  Gate 3：工程师批准 ticket 拆分（承担「无批准计划不实现」）
         diff + tests          按 ticket 实现
─────────── Build Exit Gate ────────────
Stage 4  测试证据              命令输出 / 构建日志 / 截图差异
Stage 5  PR + 评审 findings    REVIEW.md 各轮次；人审批
           │  Gate 4：code owner 批准；生产授权走 hook
Stage 6  事故 / 偏离记录       control band 触发 → 新的 intent.md
```

### 4.1 工件归属与真相源

【playbook】要求：每个工件只指定**一个**系统作为真相源，其余只持链接。

| 工件 | 作者 | 默认真相源 | 备注 |
|------|------|------------|------|
| `intent.md` | originator + agent | 仓库 `intent/` 目录 | playbook 默认做法 |
| `spec.md` | 需求段：agent 起草、产品审；实现段：工程师 + agent | 仓库，与 `intent.md` 相邻 | 见 D1 |
| tickets | agent 拆、工程师批 | 仓库本地 markdown（Matt 的 local tracker 形态） | 对外部 tracker 保持链接 |
| `GLOSSARY.md` / ADR | 追问中沉淀 | 仓库 | 【Matt】 |
| 测试证据 | 工具链 | PR 的 check run / 会话 transcript | 【playbook】 |
| PR + findings | 评审 agent + 人 | 代码托管平台 | |

【本设计】选「仓库为真相源」是因为 playbook 把提交历史当审计链；Matt 默认把 spec 与 tickets 发布到 tracker，这一点需要通过配置 local tracker 或链接最低线来对齐，见 D1。

---

## 5. 逐阶段设计

### 5.1 Plan

【playbook】originator 与 agent 头脑风暴，按组织模板写成 `intent.md`，由 originator 纠错后提交；包含问题、期望结果、受影响用户与系统、约束、待决问题。

【本设计】补充：

- `intent.md` 的模板编码成一个 Skill（缺口 1）。这是新写的，Matt 没有对应物。
- 访谈技法可选用 Matt 的 `grill-me`：它无状态、不写文件、不依赖仓库，适合非工程师。【Matt】文档同时警告「被动应答」是主要失败模式，所以产品负责人评审 `intent.md` 时，检查项里应包含「originator 是否在访谈中反驳或修正过至少一次」。
- `intent.md` 的「待决问题」一节是 P2 的载体：它们不被编造答案，而是带入下一阶段。

### 5.2 Design

【playbook】产品负责人把已接受的 `intent.md` 交给 agent，在组织的品牌/安全/合规/UX Skills 约束下产出 requirements + design spec，并标出无法满足的矛盾政策等关注点。成熟后可以由「intent 合并」触发非交互任务，把 `spec.md` 作为 PR 提交。

【本设计】调整（对应冲突 C1、C3）：

- **允许自动起草，不允许自动拍板。** 无人值守任务可以生成 spec 草稿，但草稿里凡是价值取舍，都写成「待决问题」，不得写成结论。产品负责人的评审动作，就是关闭这些问题。
- **spec 只含需求段**：问题陈述、方案（用户视角）、用户故事、范围外、关注点、待决问题。结构沿用【Matt】`to-spec` 模板的这些部分。
- 实现决策与测试决策**不在此阶段写**，因为那需要工程判断（见 §5.3 B3）。
- 术语一律使用 `GLOSSARY.md` 的词汇；与现有词汇冲突时当场暴露，不静默改写。【Matt】`domain-modeling`

### 5.3 Build（核心）

整体流程：

```text
入口门
  │
B1  grill-with-docs   工程师 ↔ agent，对 spec 追问实现层决策
  │                    · 事实 agent 查，决策人做
  │                    · 术语写进 GLOSSARY，够格的取舍写 ADR
  │   ┌─ 有「谈不清」的问题（手感 / 状态 / 逻辑）→ prototype（必要时 handoff）→ 带结论回来
  ▼
B2  确认 seam         先写下并确认要测的 seam，再谈实现
  │
B3  补 spec 实现段    实现决策 + 测试决策（不写文件路径与代码片段）
  │
B4  to-tickets        垂直切片 + 阻塞边；逐条与工程师确认粒度与依赖
  │                    ── Gate 3：批准 = 计划生效 ──
  ▼
B5  实现              ┌ 小 / 线性：implement，逐 ticket、每张换新上下文
  │                   └ 大 / 可并行：implement-spec，按「前沿」并行，集成分支
  │                    · 每个切片 tdd：红 → 绿，一次一个 seam
  │                    · 类型检查常跑，单文件测试常跑，全量只在最后一次
  ▼
B6  验证              verifier 子代理（全新上下文，只报告不修改）
  │
B7  code-review       Standards 轴 + Spec 轴（并行子代理，不合并重排）
  │
B8  pr                摘要 / 前后证据 / 单向门或双向门判断
  ▼
出口门 ──→ Stage 5
B9  retro（会话后）   把重复的错误沉淀为检查或标准
```

逐步说明：

**B1 `grill-with-docs`（Matt）。** 目的是对齐**实现层**，不是重开需求。输入是已批准的 `spec.md`，追问聚焦实现边界、模块、数据与失败路径；需求层的新疑问，退回产品负责人，而不是在 Build 里自行决定。  
【Matt】文档要求追问最好在新对话里、不要叠在 agent 已写好的计划之上；这里输入恰好是 agent 起草过的 spec。风险和缓解：工程师必须主动反驳，且追问只允许新增实现决策，不得悄悄改动需求段。

**B2 确认 seam（Matt `tdd`）。** 【Matt】「未确认的 seam 上不写测试」。seam 优先复用已有的，且越高越好，理想只有一个。

**B3 补 spec 实现段。** 沿用【Matt】`to-spec` 的「实现决策 / 测试决策」两节，并遵守其规则：不写具体文件路径和代码片段（容易过期），原型里编码决策更精确的片段是唯一例外。

**B4 `to-tickets`（Matt）。** 每张 ticket 是一个 tracer-bullet：穿过各层的窄而完整的竖切，能独立演示或验证，大小能放进一个新的上下文窗口，并声明被哪些 ticket 阻塞。批准拆分的这一步，在本设计里**等价于 playbook 的「接受计划」**（见 §6 的 C2）。

**B5 实现。** 选哪条路，由规模决定：

- `implement`：逐 ticket；【Matt】建议 `to-tickets` 之前保持同一个未清理的上下文，之后每张 ticket 换新上下文。
- `implement-spec`：把 ticket 看成任务图，对就绪「前沿」并行派实现子代理，各自在独立 worktree，合并子代理汇入集成分支，最后统一 `code-review`。

**并行度上限。**【本设计】综合两边：【playbook】指出实际上限是「一个人能认真评审的流数」，建议从 2–3 路开始；【Matt】的 `implement-spec` 以图的宽度决定并发。本设计取两者的小值：**并发数 = min(前沿宽度, 评审带宽)**。

**B6 verifier。**【playbook】在全新上下文里运行应用、检查行为是否符合计划，只报告不修复，避免判断被产出代码的假设污染。这是对【Matt】`code-review`（读 diff）的行为侧补充。

**B7 `code-review`（Matt）。** 两轴并行，互不污染：

- Standards：仓库文档化的标准 + 一套 Fowler 坏味道基线（仓库标准优先，基线只作判断参考）
- Spec：实现是否忠实于源 spec / ticket

这是**作者侧自审**。Stage 5 的独立评审由不同的评审通道执行（写代码的 agent 不能批准自己的代码，【playbook】）。

**B8 `pr`（Matt）。** 摘要（最小可视化）、前后证据、合并危险度判断。其中「单向门 / 双向门 + 爆炸半径」被【本设计】用作 Stage 5 的升级依据（见 §5.5）。

**B9 `retro`（Matt）。** 会话结束后建议改进 agent 环境。与【playbook】的规则合并：同一个错误第二次出现时，修正必须进入 `AGENTS.md`、Skill 或 hook；机械错误做成确定性检查，判断类问题做成编码标准。

**Build 内的偏离处理。**

- 实现与 ticket / spec 不一致：**在同一提交里更新工件**【playbook，可用 hook 强制】
- 实现中发现一个**取舍型决策还没定**：停下，回到 B1 重开该分支，不得自行决定（P2）
- 难以复现的 bug：走【Matt】`diagnosing-bugs`，先造出针对该 bug 必红的反馈环再假设

### 5.4 Test

两边叠加，分三层：

| 层 | 内容 | 来源 |
|----|------|------|
| 工作内的反馈环 | 在 `AGENTS.md` 的 Commands 里写明构建/测试/lint 命令及健康输出示例；给出可量化目标；「完成」必须附命令输出 | 【playbook】 |
| 测试方法 | 红 → 绿，一次一个切片，只在已确认的 seam 上测外部行为；修 bug 先写失败测试并提交，再让其变绿 | 【Matt】tdd，【playbook】 |
| 测试保护 | 修 bug 任务期间，阻止 agent 编辑测试文件的 hook | 【playbook】 |
| 对 agent 配置的回归 | 20–50 个真实任务做成 evals，每次改动 `AGENTS.md` / Skills / hooks 时在 CI 运行；每个事故沉淀一个 eval | 【playbook】 |

【本设计】两点说明：

- 【Matt】的 tdd 规则（先红后绿、不改测试）本身只是建议；把「不改测试」做成 hook 就是 P5 的落实。
- 【Matt】的 Skills 没有回归机制。本设计把「Build 用到的 Skills 与规则文件」纳入 evals 的覆盖范围（缺口 4）。

### 5.5 Deploy

**评审轮次（`REVIEW.md`，【playbook】）。** 技术负责人在仓库根写 `REVIEW.md`，按轮次拆分：

| 轮次 | 内容 | 来源 |
|------|------|------|
| Bugs | 逻辑错误、边界、回归 | 【playbook】 |
| Standards | 编码标准 + 坏味道基线 | 【Matt】`code-review` Standards 轴 |
| Spec | 实现对 `spec.md` / tickets 的符合度 | 【Matt】Spec 轴，【playbook】Compliance 轮次 |
| Security / Compliance | 注入、认证缺口、PII 入日志、政策符合度 | 【playbook】（补缺口 2） |

- findings 本身不批准或阻断 PR，批准仍由 code owner 经分支保护给出。【playbook】
- 评审者对 findings 评级；每月调优并限制 nit 数量。【playbook】

**升级依据（【本设计】推论）。** PR 里的「单向门 / 双向门 + 爆炸半径」判断，用作人审的分流：双向门、小半径 → code owner；单向门或大半径 → 技术负责人 / 架构师。原文没有这条规则，需要在试行中确认它是否好用。

**审批门（hook，【playbook】）。** 把必须保留的人工批准（变更单、发布授权、受保护路径）写成 hook：放行 / 询问 / 阻断。生产发布 hook 要求具名授权才放行。团队级 hook 进 `.claude/settings.json`（或对应工具配置），不可让工程师关闭的放在受管设置里。

**CI/CD。**【playbook】先只读的判断步骤，再带写权限的步骤（产出走 PR），沙箱运行，无常驻生产凭据；部署通过 MCP 暴露，按环境分档；回滚是被演练最多的路径。

### 5.6 Maintain

**闭环（【playbook】）。** 确定性脚本监控一个有稳定滚动基线的指标；按带分档响应：1σ 记录，2σ 只读诊断，3σ 可通过 PR 或预批准 runbook 行动。诊断结果写成 `intent.md`，回到 Stage 1。

**入口并联（【本设计】）：**

| 来源 | 走法 |
|------|------|
| 监控触发 | 自动诊断 → `intent.md` → Stage 1 |
| 人提的 bug / 请求 | 【Matt】`triage` 分流为可由 agent 接手的 issue |
| 难复现缺陷 | 【Matt】`diagnosing-bugs` |
| 小而边界清晰的修复 | 经 `triage` 后可直接进 Build 的 `implement`，跳过 Stage 1–2 |
| 较大的发现 | 写成 `intent.md`，走完整链 |

【Matt】`triage` 只处理你**没有创建**的 issue；`to-tickets` 产出的 ticket 已可交给 agent，不要再 triage。

**收尾。** 每个事故沉淀一个 eval（§5.4）；会话后用 `retro` 改环境。

---

## 6. 冲突与取舍

| # | 议题 | playbook | Matt | 本设计的取舍 | 理由 |
|---|------|----------|------|--------------|------|
| C1 | 自动化生成 spec | 可由合并触发的非交互任务起草，人评审 | 追问无异步模式；没人答的会话只是 agent 的意见 | 允许**起草**，但取舍型决策必须留作待决问题，由人关闭（P2） | 评审动作本身就是「回答 frontier」，agent 的起草不替人做决定 |
| C2 | plan mode | 工程师从 plan mode 起步，接受计划后才可改文件 | 追问时关掉 plan mode，它促使过早产出计划 | 对齐阶段不开 plan mode；「无批准计划不实现」由 **ticket 拆分的批准门（Gate 3）** 承担；只读保护作为可选项 | 保住 playbook 的不变量，又不损害 Matt 的追问质量 |
| C3 | 谁写 spec | 产品负责人主导，无需工程技能 | `to-spec` 含实现与测试决策，要确认 seam | spec 两段式：需求段归产品，实现段在 Build 入口由工程师补 | 两类决策需要不同判断力，放在同一份工件里但不同时批准 |
| C4 | 计划里写不写文件路径 | `plan.md` 列出会变更的文件 | spec 和 ticket 里**不写**文件路径，易过期 | 计划实体 = ticket 集合；文件级细节在实现时产生，不预先提交 | 过期的计划比没有更坏；保留 playbook 的「顺序 + 风险 + 证明」三要素 |
| C5 | 真相源 | repo 或旧系统，二选一并链接 | 默认发布到 issue tracker | 默认 repo + local tracker；外部系统保持链接最低线 | 审计链最简单，提交时间戳单一 |
| C6 | 控制强度 | skill 建议性 + hook 强制 | 以 skill 与纪律为主 | 建议留在 skill，必须成立的转 hook / CI | P5 |
| C7 | 并行度 | 2–3 路起步，上限为评审带宽 | 以任务图前沿决定并发 | 并发数 = min(前沿宽度, 评审带宽) | 评审是瓶颈 |
| C8 | 工具耦合 | 基于 Claude Code 及相关产品 | 声称适配任何模型与 agent | 设计保持工具中立，产品相关项放在 §10 附录并标注待验证 | 与 SkillVault 的工具中立定位一致（architecture.md §1、§2） |

---

## 7. 控制层：建议与强制的对应

| 纪律 | 默认形态（建议） | 要保证成立时的强制手段 |
|------|------------------|------------------------|
| 追问后才动手 | `grill-with-docs` / `grilling` 的确认门 | 在 `AGENTS.md` 写明「未获确认不得实现」；弱模型尤其需要 |
| 无批准计划不实现 | Gate 3（ticket 批准） | 没有已批准 ticket 的分支，CI 拒绝合并（可选） |
| 先红后绿，不改测试 | `tdd` 规则 | 修 bug 任务期间阻止编辑测试文件的 hook |
| 工件与实现同步 | 偏离时同提交更新 | 检查 spec / ticket 与 diff 同步的 hook |
| 写代码的不批准代码 | Stage 5 独立评审通道 | 分支保护 + code owner |
| 不得直接推送主干 | `implement` 在特性分支工作 | 分支保护 |
| 生产授权 | 评审与 `pr` 的门类型判断 | 生产发布 hook |
| 偏离环境标准 | `retro` 的建议 | 把重复错误做成确定性检查 |

---

## 8. 度量

先行 / 滞后指标沿用【playbook】，从 git 与 PR 历史读取。以下标【本设计】的是针对 Matt 技法新增、需试行确认的指标。

| 阶段 | 先行指标 | 滞后指标 |
|------|----------|----------|
| Plan | 首次对话到 `intent.md` 提交的时间 | 被接受进 Design 的比例 |
| Design | `intent.md` 到 `spec.md` 的时间 | 第一份 plan 之后仍修改 spec 的提交数 |
| Build | 首轮实现即合并的变更占比；计划批准到合并的时间 | 每个变更的返工轮数；合并 diff 与批准计划的一致程度 |
| Build（新增，【本设计】） | 追问的**轮数**与问题数之比；Build 入口门之后新增的待决问题数 | ticket 一次通过率；`code-review` 两轴 finding 数 |
| Test | agent 变更首轮 CI 通过率；evals 通过率 | 单 PR 评审时间；变更失败率 |
| Deploy | 首次评审耗时；无人工改动即解决的评审意见占比 | 合并前发现的缺陷 vs 逃逸到生产的缺陷 |
| Maintain | 带越界到 `intent.md` 入队的时间 | 发现变成合并修复的比例；同类事故复发 |

---

## 9. 与 SkillVault 的关系

【architecture.md §9】SkillVault 不承载业务功能的 spec / plan，只提供可挂载到 SDLC 各阶段的**制度 Skills**。本设计遵循这条边界：本文定义的是一套**参考工作流**，以及它需要哪些 Skills；它不改变 SkillVault 的范围。

### 9.1 所需 Skills 清单

| 类别 | 内容 | 状态 |
|------|------|------|
| 沿用 Matt 原样 | `grilling`、`grill-me`、`grill-with-docs`、`domain-modeling`、`to-tickets`、`implement`、`implement-spec`、`tdd`、`code-review`、`pr`、`retro`、`triage`、`diagnosing-bugs`、`prototype`、`setup-matt-pocock-skills` | 未收录；收录须经现有 import 门禁（Gate A–C）与安全扫描 |
| 沿用 Matt，需改造 | `to-spec`：拆为「需求段」与「实现段」两个模式（C3） | 待设计 |
| 需新写 | `intent-capture`（intent 模板）；`review-policy`（`REVIEW.md` 骨架含安全/合规轮次）；`decision-rights`（待决问题的写法与过门检查） | 待设计 |
| 组织政策 Skills | 安全、品牌、合规、UX | 属各组织自建，不属本库公共内容 |
| 不进 SkillVault | `AGENTS.md`、`GLOSSARY.md`、ADR、`REVIEW.md`、hooks | 属业务仓库（architecture.md §3） |

### 9.2 Matt 的 skill 之间的依赖（收录时要保持完整）

- `grill-me` 只有一行，调用 `grilling`；没有 `grilling` 就不会工作
- `grill-with-docs` 调用 `grilling` 与 `domain-modeling`
- 【Matt】文档记录了已知问题：一个 skill 点名另一个 skill 并不能保证后者被加载

因此收录必须成套，且验收时要检查依赖是否真的被加载。

---

## 10. 工具映射（附录，待验证）

本设计的主体保持工具中立。以下是产品相关的映射，**均未在本仓库内实测**。

| 概念 | Claude Code | Cursor |
|------|-------------|--------|
| 用户才能触发的 skill | `disable-model-invocation: true` | Cursor 文档的 skill frontmatter 表中列有同名字段，待实测行为 |
| 子代理 / worktree 并行 | 子代理、`--worktree` | 有子代理与 worktree 能力，与 `implement-spec` 的契合度待实测 |
| 阻断式 hook（审批门、保护测试文件） | `PreToolUse` 等 | Cursor 有 hooks；事件与阻断语义是否等价待核对 |
| 受管设置、沙箱、Claude Security、Claude Tag | playbook 原样 | 不适用或需另找等价物；本设计的主体不依赖它们 |

---

## 11. 未决问题（需你拍板）

| # | 问题 | 默认建议 | 备选 |
|---|------|----------|------|
| D1 | 真相源 | 仓库 markdown + local tracker；外部系统保持链接最低线 | Matt 默认的外部 tracker（GitHub / Linear）为 tickets 与 spec 真相源 |
| D2 | spec 是否两段式 | 是（C3） | 单段，Stage 2 就有工程师参与 |
| D3 | `plan.md` 的实体 | = ticket 集合，不写文件路径（C4） | 保留 playbook 的 `plan.md`，在 ticket 之上另写一份含文件列表的计划 |
| D4 | Matt 的追问是否前移到 Stage 1–2 | 仅在 Stage 1 把 `grill-me` 作为可选访谈技法；Stage 2 不用 | 全面前移，`grill-with-docs` 用于 Stage 2 的 spec 对齐 |
| D5 | 本设计的用途 | 通用参考工作流，放在 SkillVault 的 docs 里；是否 dogfood 另议 | 直接作为 SkillVault 自身开发流程的规范 |
| D6 | 首个验证环境 | Cursor 先行，Claude Code 作为对照 | 以 Claude Code 为准，因为 playbook 针对它 |

---

## 12. 依据与未核验项

**已读原文：**

- playbook 全文（含各 play 的 Traditional / AI-native、步骤、示例、治理、指标）
- Matt：README、`GLOSSARY.md`、ADR 0002、`skills/engineering/README.md`、`ask-matt`、`grilling`、`grill-me`、`grill-with-docs`、`domain-modeling`、`to-spec`、`to-tickets`、`implement`、`implement-spec`、`tdd`、`code-review`；aihero.dev 上 `grilling` 与 `grill-me` 的说明页

**只读到 README 级描述、未读 SKILL.md 正文：** `triage`、`wayfinder`、`pr`、`diagnosing-bugs`、`retro`、`improve-codebase-architecture`、`prototype`、`codebase-design`、`setup-matt-pocock-skills`。涉及它们的段落（B8、B9、§5.6、§9.1）是依据说明做的设计，细节需要在收录前对照正文复核。

**其它未核验：**

- Matt 仓库的许可证文本未读，收录前需确认
- §5.5 的「按门类型分流评审」是本设计的推论，两边原文均无此规则
- §8 中标【本设计】的指标未经试行
- §10 的 Cursor 一列全部待实测

---

## 13. 建议的落地顺序

1. **评审本文**，先定 D1–D6。
2. **选一条真实的小需求**，手工走一遍 Stage 1 → Build → Stage 5，只用现有的 Matt skill 与手写 `intent.md` / `REVIEW.md`。目的是检验工件契约（§3.2）是否顺手，而不是自动化。
3. 根据试行结果决定 `to-spec` 是否拆两段、`decision-rights` 是否值得写成 Skill。
4. 再按 SkillVault 现有流程收录 Matt 的 skill（逐个过安全扫描与人审），并把新写的 Skills 放入 `vault/own`。
5. 最后才考虑 hook、CI、evals 的自动化。与 architecture.md 的推进原则一致：先手跑 play，再收进 `sv` 子命令。
