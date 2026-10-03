# Skill 索引（中文）

> 由 `py cli/sv.py catalog` **自动生成**，请勿手改。真相源是 `vault/**/SKILL.md`；机器可读见 [`registry/catalog.yaml`](../registry/catalog.yaml)；中文简介词条维护于 [`registry/descriptions.zh-CN.yaml`](../registry/descriptions.zh-CN.yaml)。英文版：[skills-index.md](./skills-index.md)。

- 生成时间（UTC）：`2026-10-03T09:33:35Z`
- 合计：**77**（自建 1 / 收录 76）

## 按类目

| 类目 | 说明 | 数量 |
|------|------|-----:|
| `define` | 定义 | 5 |
| `deliver` | 交付 | 7 |
| `design` | 设计 | 5 |
| `discover` | 发现 / 调研 | 5 |
| `engineering` | 工程 | 6 |
| `foundation` | 立项 / 基础 | 11 |
| `meta` | 元工具 | 28 |
| `ops` | 运营 / 度量 | 10 |

## 收录（`imported`）

### 定义（`define`）

| 名称 | 许可 | 用途（中文） |
|------|------|--------------|
| [`define-hypothesis`](../vault/imported/define/define-hypothesis/) | Apache-2.0 | 定义可验证假设：写清成功指标与验证路径。用于形成待测假设，或对齐团队对「成功长什么样」的共识。 |
| [`define-jtbd-canvas`](../vault/imported/define/define-jtbd-canvas/) | Apache-2.0 | 产出 Jobs to be Done 画布，覆盖功能/情感/社交维度。用于深入理解顾客动机与要完成的「工作」。 |
| [`define-opportunity-tree`](../vault/imported/define/define-opportunity-tree/) | Apache-2.0 | 产出机会解决方案树，把期望结果连到顾客机会与候选方案，避免一上来就跳进具体解法。 |
| [`define-prioritization-framework`](../vault/imported/define/define-prioritization-framework/) | Apache-2.0 | 用 RICE/ICE/MoSCoW/加权评分/Kano 等框架给功能或举措打分，产出对比表以辅助取舍。 |
| [`define-problem-statement`](../vault/imported/define/define-problem-statement/) | Apache-2.0 | 写清问题陈述：用户影响、业务背景与成功标准。用于开题、纠偏或重新对齐方向。 |
### 交付（`deliver`）

| 名称 | 许可 | 用途（中文） |
|------|------|--------------|
| [`deliver-acceptance-criteria`](../vault/imported/deliver/deliver-acceptance-criteria/) | Apache-2.0 | 为用户故事/功能切片生成 Given/When/Then 验收标准，覆盖主路径、关键失败与非功能要求。 |
| [`deliver-edge-cases`](../vault/imported/deliver/deliver-edge-cases/) | Apache-2.0 | 系统梳理边界/异常/竞态与恢复路径，形成「什么会出错、如何兜住」的清单。 |
| [`deliver-launch-checklist`](../vault/imported/deliver/deliver-launch-checklist/) | Apache-2.0 | 跨职能上线前检查清单（工程、设计、市场、支持、法务、运营），含负责人、日期与 go/no-go。 |
| [`deliver-prd`](../vault/imported/deliver/deliver-prd/) | Apache-2.0 | 产出对齐干系人的 PRD：做什么、为什么、如何衡量成功。用于功能规格与立项沟通。 |
| [`deliver-release-notes`](../vault/imported/deliver/deliver-release-notes/) | Apache-2.0 | 写面向用户的发布说明，用收益导向语言说明新功能、改进与修复。 |
| [`deliver-user-stories`](../vault/imported/deliver/deliver-user-stories/) | Apache-2.0 | 从需求/功能描述拆出标准「角色-行动-收益」用户故事。 |
| [`internal-comms`](../vault/imported/deliver/internal-comms/) | Apache-2.0 | 按公司常用格式撰写内部沟通：3P 更新、周报、领导同步、项目进展、事故通报、FAQ、内刊等。 |
### 设计（`design`）

| 名称 | 许可 | 用途（中文） |
|------|------|--------------|
| [`canvas-design`](../vault/imported/design/canvas-design/) | Apache-2.0 | 按设计哲学创作海报/视觉作品（png/pdf）。用户要做海报、静态视觉或艺术表达时使用。 |
| [`frontend-design`](../vault/imported/design/frontend-design/) | Apache-2.0 | 指导有辨识度、有意图的 UI 视觉方向：审美、字体与差异化，避免千篇一律的默认风。 |
| [`theme-factory`](../vault/imported/design/theme-factory/) | Apache-2.0 | 为幻灯片/文档/报告/落地页等套用主题；内置约 10 套配色与字体主题。 |
| [`ui-ux-pro-max`](../vault/imported/design/ui-ux-pro-max/) | MIT | 可检索的 UI/UX 设计智能（风格/配色/字体/落地页模式/交付检查）；含本地设计系统生成脚本。与 frontend-design 互补，不做纯后端。 |
| [`web-artifacts-builder`](../vault/imported/design/web-artifacts-builder/) | Apache-2.0 | 用 React/Tailwind/shadcn 搭建复杂多组件 HTML artifact（偏 claude.ai 产物）。 |
### 发现 / 调研（`discover`）

| 名称 | 许可 | 用途（中文） |
|------|------|--------------|
| [`discover-competitive-analysis`](../vault/imported/discover/discover-competitive-analysis/) | Apache-2.0 | 结构化竞品分析：功能/定价/定位对比（3–5 家）、2x2 图与行动建议。 |
| [`discover-interview-synthesis`](../vault/imported/discover/discover-interview-synthesis/) | Apache-2.0 | 把访谈/可用性测试综合成洞察、模式与建议。访谈完成后使用。 |
| [`discover-journey-map`](../vault/imported/discover/discover-journey-map/) | Apache-2.0 | 绘制顾客旅程：阶段、触点、情绪曲线、痛点与关键时刻；可附 mermaid 时间线。 |
| [`discover-market-sizing`](../vault/imported/discover/discover-market-sizing/) | Apache-2.0 | 用自上而下/自下而上/可比公司等方法估算 TAM/SAM/SOM，交叉验证市场规模。 |
| [`discover-stakeholder-summary`](../vault/imported/discover/discover-stakeholder-summary/) | Apache-2.0 | 梳理干系人需求、关切、影响力与沟通策略。适合 kickoff 或交接。 |
### 工程（`engineering`）

| 名称 | 许可 | 用途（中文） |
|------|------|--------------|
| [`commit-generate`](../vault/imported/engineering/commit-generate/) | MIT | 根据已暂存改动生成中英双语 Conventional Commit 信息。 |
| [`develop-adr`](../vault/imported/engineering/develop-adr/) | Apache-2.0 | 按 Nygard 格式写架构决策记录（ADR）：上下文、决策与后果。 |
| [`develop-design-rationale`](../vault/imported/engineering/develop-design-rationale/) | Apache-2.0 | 记录设计决策理由：备选方案、权衡与原则。用于重大 UX/设计取舍。 |
| [`develop-solution-brief`](../vault/imported/engineering/develop-solution-brief/) | Apache-2.0 | 一页纸方案概述：路径、关键决策与权衡。用于向干系人推销方案。 |
| [`develop-spike-summary`](../vault/imported/engineering/develop-spike-summary/) | Apache-2.0 | 总结技术/设计 spike：问题、方法、证据与是否继续的结论。 |
| [`webapp-testing`](../vault/imported/engineering/webapp-testing/) | Apache-2.0 | 用 Playwright 测本地 Web 应用：功能验证、UI 调试与浏览器自动化。 |
### 立项 / 基础（`foundation`）

| 名称 | 许可 | 用途（中文） |
|------|------|--------------|
| [`foundation-build-risk-review`](../vault/imported/foundation/foundation-build-risk-review/) | Apache-2.0 | 开建前快速风险审视：点出最可能让想法失败的那条假设，并给出对策。 |
| [`foundation-lean-canvas`](../vault/imported/foundation/foundation-lean-canvas/) | Apache-2.0 | 产出九宫格精益画布（问题、顾客、UVP、方案、渠道、收入、成本、指标、壁垒）。 |
| [`foundation-meeting-agenda`](../vault/imported/foundation/foundation-meeting-agenda/) | Apache-2.0 | 面向与会者的议程：议题、负责人与时间分配；支持多种会议类型。 |
| [`foundation-meeting-brief`](../vault/imported/foundation/foundation-meeting-brief/) | Apache-2.0 | 会前私用战略简报：利害、各方立场、期望结果与话术准备。 |
| [`foundation-meeting-recap`](../vault/imported/foundation/foundation-meeting-recap/) | Apache-2.0 | 会后按议题分段纪要：决策高亮、行动项汇总。 |
| [`foundation-meeting-synthesize`](../vault/imported/foundation/foundation-meeting-synthesize/) | Apache-2.0 | 跨多场会议做「考古」：从多份纪要/笔记里抽出单场看不见的模式。 |
| [`foundation-okr-writer`](../vault/imported/foundation/foundation-okr-writer/) | Apache-2.0 | 起草/评审/改写结果导向 OKR；支持引导、审稿等多种入口模式。 |
| [`foundation-persona`](../vault/imported/foundation/foundation-persona/) | Apache-2.0 | 生成证据校准的产品/营销画像，用于定视角或压测定位。 |
| [`foundation-prioritized-action-plan`](../vault/imported/foundation/foundation-prioritized-action-plan/) | Apache-2.0 | 从笔记、纪要、Slack、领导要求等原材料产出有证据支撑的优先级行动计划。 |
| [`foundation-stakeholder-briefings`](../vault/imported/foundation/foundation-stakeholder-briefings/) | Apache-2.0 | 把规格/调研/GTM/实验等源材料转成主文档 + 分受众简报。 |
| [`foundation-stakeholder-update`](../vault/imported/foundation/foundation-stakeholder-update/) | Apache-2.0 | 异步同步干系人（尤其未与会者）：把会议结果翻译成对方关心的要点。 |
### 元工具（`meta`）

| 名称 | 许可 | 用途（中文） |
|------|------|--------------|
| [`tool-design-sprint-brief`](../vault/imported/meta/tool-design-sprint-brief/) | Apache-2.0 | Design Sprint 会前简报：挑战、问题、角色、招募、原型介质与后勤。 |
| [`tool-design-sprint-decide-and-storyboard`](../vault/imported/meta/tool-design-sprint-decide-and-storyboard/) | Apache-2.0 | Design Sprint Day3：艺廊布局、热图、快评、投票与故事板决策。 |
| [`tool-design-sprint-map-and-target`](../vault/imported/meta/tool-design-sprint-map-and-target/) | Apache-2.0 | Design Sprint Day1：长期目标、可测风险问题、顾客旅程与目标。 |
| [`tool-design-sprint-prototype-plan`](../vault/imported/meta/tool-design-sprint-prototype-plan/) | Apache-2.0 | Design Sprint Day4：原型日角色与制作计划（Maker/Stitcher 等）。 |
| [`tool-design-sprint-readiness`](../vault/imported/meta/tool-design-sprint-readiness/) | Apache-2.0 | Design Sprint 就绪诊断：现在开跑 / 推迟 / 先补前提条件。 |
| [`tool-design-sprint-sketch`](../vault/imported/meta/tool-design-sprint-sketch/) | Apache-2.0 | Design Sprint Day2：闪电演示与四步独立方案草图（含 Crazy 8s）。 |
| [`tool-design-sprint-test-and-score`](../vault/imported/meta/tool-design-sprint-test-and-score/) | Apache-2.0 | Design Sprint Day5：访谈观察、金句、打分与学习结论。 |
| [`tool-foundation-sprint-approach-options`](../vault/imported/meta/tool-foundation-sprint-approach-options/) | Apache-2.0 | Foundation Sprint Day2 上午：先产出 3–7 个候选打法再收敛。 |
| [`tool-foundation-sprint-basics`](../vault/imported/meta/tool-foundation-sprint-basics/) | Apache-2.0 | Foundation Sprint Day1 上午：目标顾客、关键问题、优势与竞对。 |
| [`tool-foundation-sprint-brief`](../vault/imported/meta/tool-foundation-sprint-brief/) | Apache-2.0 | Foundation Sprint 会前：范围、要解锁的决策、角色与成功标准。 |
| [`tool-foundation-sprint-differentiation`](../vault/imported/meta/tool-foundation-sprint-differentiation/) | Apache-2.0 | Foundation Sprint Day1 下午：差异化选项评分，落到可防守定位。 |
| [`tool-foundation-sprint-founding-hypothesis`](../vault/imported/meta/tool-foundation-sprint-founding-hypothesis/) | Apache-2.0 | Foundation Sprint 收官：压成一句创立假设 + 支撑要点。 |
| [`tool-foundation-sprint-magic-lenses`](../vault/imported/meta/tool-foundation-sprint-magic-lenses/) | Apache-2.0 | Foundation Sprint Day2 下午：多透镜评估候选打法与权衡。 |
| [`tool-foundation-sprint-readiness`](../vault/imported/meta/tool-foundation-sprint-readiness/) | Apache-2.0 | Foundation Sprint 就绪诊断：现在开跑 / 推迟 / 先补前提。 |
| [`tool-note-and-vote`](../vault/imported/meta/tool-note-and-vote/) | Apache-2.0 | 结构化「静默发散-投票-决策人签核」群决策，产出捆绑工件。 |
| [`utility-mermaid-diagrams`](../vault/imported/meta/utility-mermaid-diagrams/) | Apache-2.0 | 教 PM 选对 mermaid 图类型并写出语法正确、可渲染的图。 |
| [`utility-pm-changelog-curator`](../vault/imported/meta/utility-pm-changelog-curator/) | Apache-2.0 | 从 git log 起草 CHANGELOG（公开路径、描述变更、无署名噪音）。 |
| [`utility-pm-critic`](../vault/imported/meta/utility-pm-critic/) | Apache-2.0 | 对 PM 工件做对抗式评审，按 P0–P3 给出发现与改法。 |
| [`utility-pm-release-conductor`](../vault/imported/meta/utility-pm-release-conductor/) | Apache-2.0 | 引导 6 门禁发布流程（就绪→对抗审→版本/日志→提交→打标→发布后）。 |
| [`utility-pm-skill-auditor`](../vault/imported/meta/utility-pm-skill-auditor/) | Apache-2.0 | 仓库级治理审计：跑校验套件、汇总计数与缺口。 |
| [`utility-pm-skill-builder`](../vault/imported/meta/utility-pm-skill-builder/) | Apache-2.0 | 从想法走到完整 Skill 实现包（缺口分析、工作表、对齐 pm-skills 约定）。 |
| [`utility-pm-skill-iterate`](../vault/imported/meta/utility-pm-skill-iterate/) | Apache-2.0 | 按反馈/校验/约定变更对既有 skill 做定向改进。 |
| [`utility-pm-skill-validate`](../vault/imported/meta/utility-pm-skill-validate/) | Apache-2.0 | 按结构与质量约定审计 skill，输出通过/失败与严重度报告。 |
| [`utility-pm-workflow-builder`](../vault/imported/meta/utility-pm-workflow-builder/) | Apache-2.0 | 从工作流想法走到完整 Workflow 实现包与交叉更新清单。 |
| [`utility-pm-workflow-orchestrator`](../vault/imported/meta/utility-pm-workflow-orchestrator/) | Apache-2.0 | 按序跑一组 pm-skills，逐步 go/no-go，失败或空输出即停。 |
| [`utility-slideshow-creator`](../vault/imported/meta/utility-slideshow-creator/) | Apache-2.0 | 从 JSON 讲稿规格生成专业幻灯片（多版式、深/浅色、内容到布局逻辑）。 |
| [`utility-update-pm-skills`](../vault/imported/meta/utility-update-pm-skills/) | Apache-2.0 | 检查并预览 pm-skills 新版本，确认后更新本地文件。 |
### 运营 / 度量（`ops`）

| 名称 | 许可 | 用途（中文） |
|------|------|--------------|
| [`iterate-lessons-log`](../vault/imported/ops/iterate-lessons-log/) | Apache-2.0 | 结构化经验教训条目，沉淀事故/项目后的组织记忆。 |
| [`iterate-pivot-decision`](../vault/imported/ops/iterate-pivot-decision/) | Apache-2.0 | 记录 pivot/persevere 决策：证据、分析与理由。 |
| [`iterate-refinement-notes`](../vault/imported/ops/iterate-refinement-notes/) | Apache-2.0 | 记录待办梳理会结果：故事、估点、问题与决定。 |
| [`iterate-retrospective`](../vault/imported/ops/iterate-retrospective/) | Apache-2.0 | 主持并记录回顾：做得好的、待改进与行动项。 |
| [`measure-dashboard-requirements`](../vault/imported/ops/measure-dashboard-requirements/) | Apache-2.0 | 明确看板要回答的问题及指标、可视化、筛选与数据源需求。 |
| [`measure-experiment-design`](../vault/imported/ops/measure-experiment-design/) | Apache-2.0 | 设计 A/B 或实验：变体、成功指标、样本量与时长。 |
| [`measure-experiment-results`](../vault/imported/ops/measure-experiment-results/) | Apache-2.0 | 记录实验/A/B 结果：统计、学习与建议。 |
| [`measure-instrumentation-spec`](../vault/imported/ops/measure-instrumentation-spec/) | Apache-2.0 | 规定埋点事件、触发时机与属性，作为产研数据契约。 |
| [`measure-okr-grader`](../vault/imported/ops/measure-okr-grader/) | Apache-2.0 | 周期结束时按 OKR 类型枚举给 KR 打分并给出下一周期建议。 |
| [`measure-survey-analysis`](../vault/imported/ops/measure-survey-analysis/) | Apache-2.0 | 分析问卷：画像分段、假设验证、开放题主题聚类与可执行洞察。 |
## 自建（`own`）

### 元工具（`meta`）

| 名称 | 许可 | 用途（中文） |
|------|------|--------------|
| [`hello-skillvault`](../vault/own/meta/hello-skillvault/) | MIT | 烟测 SkillVault 安装是否成功。用于确认 Skill 已正确装到 IDE 的用户级或项目级 skills 目录。 |
