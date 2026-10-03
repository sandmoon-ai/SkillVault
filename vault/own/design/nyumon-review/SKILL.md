---
name: nyumon-review
description: 'Review flyers, slides, and documents with 坂本伸二『デザイン入門教室』classroom order:
  purpose first, then layout, photos, color, type, text design, and infographics.
  Use when the user wants a beginner-design audit, デザイン入門教室 check, or asks why a layout
  feels amateurish / 伝わらない.'
license: MIT
compatibility: linux, macos, windows
metadata:
  category: design
  vault: own
  tags:
  - from-book
  - nyumon
---

# デザイン入門教室 Review

按「课堂顺序」审纸面/资料：先目的，后手法。センス不足通常是假诊断；真问题多半是目的不清或基本规则没守。

规则来源：坂本伸二『デザイン入門教室［特別講義］』。

## 何时使用

- チラシ、ポスター、企画書、スライド、通知物「看起来业余」
- 用户说没センス、不知哪里怪
- 需要决定回目的 / 改布局 / 改要素

分流：目的 → `nyumon-purpose`；布局 → `nyumon-layout`；图文字表 → `nyumon-elements`。配色深挖 → `haishoku-*`；资料伝わる细则 → `tsutawaru-*`。

## 工作流

```
Review Progress:
- [ ] 1. 文类与阅读场景
- [ ] 2. 目的是否可写清（Ch1）
- [ ] 3. レイアウト：揃える・余白・グループ・強弱（Ch2）
- [ ] 4. 写真/画像是否服务目的（Ch3）
- [ ] 5. 配色是否有战略印象（Ch4）
- [ ] 6. 书体与文字设计是否可读（Ch5–6）
- [ ] 7. 图解/表/グラフ是否减轻负担（Ch7）
- [ ] 8. 按严重度输出 + 指定下一 skill
```

## 检查顺序（不要跳）

### 1. 目的（最优先）

- 向谁？传达什么？希望对方知/信/做/感什么？
- 若答不出 → **Critical**，停在装饰层批评无意义
- 目的与媒介是否匹配（远看チラシ vs 近读文書）

### 2. レイアウト

- **揃える**是否贯彻？
- マージン/版心是否窒息或漂？
- 相关是否成组、无关是否拉开？
- 強弱是否表达信息优先级？
- 余白是「留给功能」还是「忘了排」？
- あしらい是否抢信息？

### 3. 写真と画像

- 选图是否贴目的？
- 裁切/方向是否突出主体？
- 图文是否抢戏或脱节？

### 4. 配色

- 有无目标印象，还是随意填色？
- 色数是否失控？对比是否可读？
- 深改色转 `haishoku-review`

### 5. 文字・书体・文章

- 书体印象与目的一致？
- 层级（标题/本文/注）是否清楚？
- 长文是否为难读墙？

### 6. インフォグラフィック

- 该图式化的是否仍是长文？
- 表/グラフ是否多余装饰、难读数？

## 分流表

| 诊断 | 下一步 |
|------|--------|
| 目的不清 | `nyumon-purpose` |
| 目的清、对齐/余白/层级崩 | `nyumon-layout` |
| 图/字/表/图解问题 | `nyumon-elements` |
| 配色印象/色板 | `haishoku-*` |
| 仅商务文结构 | `kaku-*` |
| Web 交互摩擦 | `krug-*` |

## 输出格式

```markdown
# デザイン入門教室 Review

**文类**: …
**总判**: [目的问题 / 布局问题 / 要素问题 — 一句话]

## 课堂检查
| 章 | 结果 | 要点 |
|----|------|------|
| 目的 | ✅/❌ | … |
| レイアウト | | |
| 写真 | | |
| 配色 | | |
| 文字 | | |
| 図解 | | |

## 问题清单

### 🔴 Critical
1. **[现象]** → 违反: 目的/揃える/…
   - 改法: …
   - 下一 skill: …

### 🟡 Should fix
…

### 🟢 Nice to have
…

## 建议改稿顺序
1. …
```

## 反模式

- 一上来评「不够高级/潮」
- 忽略目的只改装饰
- 用另一套审美体系全盘否定基本对齐
- 一次抛 40 条品味意见，不标优先级

## 边界

- 品牌 VI 优先；冲突时标注
- 本书偏平面/资料基础；产品交互深审用 `krug-*`
