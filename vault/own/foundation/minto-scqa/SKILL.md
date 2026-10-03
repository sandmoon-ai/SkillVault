---
name: minto-scqa
description: Write introductions with Minto SCQA (Situation, Complication, Question,
  Answer) to lead into a pyramid governing thought. Use when crafting memo/deck openings,
  email hooks, problem framing, or when the user mentions SCQA, 序言, 情境冲突, or minto-scqa.
license: MIT
compatibility: linux, macos, windows
metadata:
  category: foundation
  vault: own
  tags:
  - from-book
  - minto
---

# SCQA 序言

用故事弧把读者带到塔尖答案：情境 → 冲突 → 疑问 → 答案。答案即金字塔顶端那一句。

## 何时使用

- 报告/提案/邮件开头不知道怎么起  
- 直接甩结论太硬，或堆背景没人读  
- Review 判定「有塔尖但序言失败」

塔身结构 → `minto-pyramid`。SCQA 的 A 必须与塔尖同一句。

## 工作流

```
SCQA Progress:
- [ ] 1. 锁定塔尖 Answer（已有则引用；无则先 pyramid）
- [ ] 2. 写 S：读者已知的稳定情境（别教对方已知道的细节）
- [ ] 3. 写 C：打破稳定的变化/麻烦/机会
- [ ] 4. 析出 Q：冲突自然逼出的问题（常可省略明写）
- [ ] 5. 给 A：塔尖答案
- [ ] 6. 压缩：只留带入问题所需的最少 S/C
- [ ] 7. 接 Key Line 展开
```

## 四段定义

| 段 | 含义 | 写法要点 |
|----|------|----------|
| **S Situation** | 读者同意的出发语境 | 短；用已知；建立「我们在谈同一世界」 |
| **C Complication** | 变化、问题、张力 | 打破 S 的稳定；制造「需要想一想」 |
| **Q Question** | 由 C 逼出的问题 | 可显式可隐含；必须是全文要答的 |
| **A Answer** | 对 Q 的回答 | = 塔尖；清晰可决策 |

常见故事型式（按材料选择，勿生搬）：

- 我们处于 S → 但 C 发生 → 因此要问 Q → 答案是 A  
- 曾以为 S → 实际 C → 所以 Q → A  

## 与读者的契约

- S 里只放 **读者已接受或易接受** 的内容；争议放后面论证  
- C 必须足够真实，才撑得起 Q；假冲突（强行转折）会毁掉信任  
- A 出现后，正文 Key Line 只负责证明/展开 A，不另起炉灶  

## 篇幅控制

| 文类 | SCQA 体量 |
|------|-----------|
| 短邮件 | 2–5 句内完成；Q 常隐含 |
| 一页备忘 | 一短段或四句标签化 |
| 长报告 | 一节序言；仍要快到 A |
| 幻灯片 | 首页或页一：S/C 极简 → A 作标题级主张 |

商业默认：**尽快到 A**。文学式长铺陈不适合决策文。

## 输出格式

```markdown
# SCQA 令

**读者**: …
**Q（核心问题）**: …
**A（塔尖）**: …

## 序言草稿
- S: …
- C: …
- Q: …（显式/隐含）
- A: …

## 连贯成段
…

## 自检
- [ ] S 多为已知
- [ ] C 真实造成张力
- [ ] Q 与全文一致
- [ ] A = 金字塔塔尖
- [ ] 无假冲突、无背景泄洪
```

## 反模式

- 把整个行业教科书塞进 S  
- C 写成情绪抱怨而无事实变化  
- A 与后文结论不一致  
- 先写方法论文再进入问题（读者未同意「为何在乎」）  
- 邮件里 SCQA 四段标题党排版过度（短文应自然成段）  

## 边界

- 不替代塔身论证；序言只负责导入  
- 危机沟通等场景仍要诚实：S/C 不粉饰  
- 与 `kaku-design` 的「导入」一致时可合并产出，逻辑术语以 SCQA 为准
