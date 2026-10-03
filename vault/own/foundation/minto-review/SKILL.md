---
name: minto-review
description: 'Audit memos, decks, and reports with Barbara Minto''s Pyramid Principle:
  governing thought, vertical Q&A, horizontal logic, SCQA intro, MECE grouping, and
  non-blank summaries. Use when prose feels unstructured, "没有重点", logic is fuzzy,
  or the user mentions 金字塔原理 / Minto / pyramid review.'
license: MIT
compatibility: linux, macos, windows
metadata:
  category: foundation
  vault: own
  tags:
  - from-book
  - minto
---

# 金字塔原理 Review

审表达是否已成塔：有塔尖、上下问答成立、同层同类有序。不管文笔漂不漂亮——明托管的是落笔前的思想结构。

规则来源：Barbara Minto《金字塔原理》/ The Minto Pyramid Principle。

## 何时使用

- 邮件、备忘、报告、幻灯片「写很长但抓不住重点」
- 用户说逻辑乱、结论埋太深、分类重叠
- 需要决定：重搭塔 / 重写序言 / 只改分组

分流：搭塔 → `minto-pyramid`；序言 → `minto-scqa`；分类/解题树 → `minto-mece`。成文流程可叠 `kaku-*`。

## 工作流

```
Review Progress:
- [ ] 1. 定文类与读者决策任务
- [ ] 2. 找/还原塔尖（中心思想）
- [ ] 3. 查纵向：上层概括下层？下层答上层之问？
- [ ] 4. 查横向：同组演绎或归纳？顺序？近 MECE？
- [ ] 5. 查序言：是否 SCQA 引出 A？
- [ ] 6. 查概括句：有无空洞断言？
- [ ] 7. 分流并按严重度输出
```

## 核心检查

### 1. 塔尖（Governing thought）

- 能否用 **一句** 说出中心思想（读者应知/应决的答案）？
- 是否结论先行，还是「背景→分析→所以」直到文末才给答案？
- 商业沟通里悬念通常是成本，不是优点。

无塔尖 → Critical。先别改句子。

### 2. 纵向关系（Vertical）

- 每一上层思想是否 **概括** 其下各组？
- 下层是否回答上层自然引发的疑问（为何？如何？何以见得？）？
- 是否出现「上层问 A、下层答 B」的错位？

### 3. 横向关系（Horizontal）

同层一组思想必须是：

- **演绎**：前提→前提→因此；或  
- **归纳**：同类思想归为一组，再向上概括  

并检查：

- 是否同一类思想（能共用一个复数名词：原因们、步骤们、部分们）？
- 顺序是否匹配分析方式：时间 / 结构 / 重要性？
- 是否明显重叠或重大遗漏（MECE 体检）？

### 4. 序言

- 是否用情境→冲突→疑问自然接到答案？
- 还是一上来堆术语/数据，读者不知道「所以要回答什么」？

### 5. 概括质量

剔除「智力空白」断言，例如：

- 坏：「有三个原因」「做了若干改变」  
- 好：概括其 **共同效应/具体结论**（下层合起来说明了什么）

## 分流表

| 诊断 | 下一步 |
|------|--------|
| 无塔尖/上下错位/横无逻辑 | `minto-pyramid` |
| 塔有、开头劝不动人读 | `minto-scqa` |
| 分类重叠遗漏、议题树乱 | `minto-mece` |
| 结构可、句子拖 | `kaku-revise` / `krug-scan` |

## 输出格式

```markdown
# 金字塔 Review

**文类**: …
**读者决策**: …
**总判**: [无塔尖 / 纵向断 / 横向乱 / 序言弱 — 一句话]

## 结构速写（现状还原）
- 塔尖: …
- Key Line: 1.… 2.… 3.…
- 主要断裂: …

## 检查表
| 项 | 结果 | 备注 |
|----|------|------|
| 一句中心思想 | ✅/❌ | |
| 结论位置 | 先/中/末 | |
| 纵向问答 | | |
| 横向演绎或归纳 | | |
| 顺序逻辑 | | |
| 近 MECE | | |
| SCQA 序言 | | |
| 概括非空 | | |

## 问题清单

### 🔴 Critical
1. **[现象]** → 违反: …
   - 改法: …
   - 下一 skill: …

### 🟡 Should fix
…

## 建议路径
1. …
```

## 反模式

- 用「更有文采」代替结构调整  
- 把时间线叙述误当成已论证  
- 强制文学悬念式开场于决策文档  
- 一次列出所有品味问题，不标结构优先级  

## 边界

- 不裁决事实真伪；缺证据标「下层支撑不足」  
- 小说叙事不适用「必须结论先行」  
- 设计目的用 `nyumon-purpose`；本 skill 只管思想金字塔
