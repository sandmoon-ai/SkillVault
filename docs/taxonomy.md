# Skill 分类约定

Skill 变多后用 **浅分类目录 + 标签** 组织，避免 `vault/own` 下一层堆平。

## 规则

1. **目录形态**（Agent Skills：`SKILL.md` 父目录名 = `name`）：

```text
vault/own/<category>/<skill-name>/SKILL.md
vault/imported/<category>/<skill-name>/SKILL.md
```

2. **类目按工作阶段**（粗粒度、尽量互斥），**不按 IDE** 分。  
3. **标签**写在 frontmatter `metadata.tags`，表达交叉维度（语言、场景、是否含脚本等）。  
4. **`metadata.category`** 应与目录 `<category>` 一致，便于校验与列表。  
5. 拿不准先放 `inbox`，定期归类。  
6. 特殊目录：`vault/own/_template/` 为模板，**不是**类目，不安装。  
7. 仓库根 `meta-skills/` 仍是「操作本库」的 play（含 `import-from-url`、`install`、`github-ops`），不必迁入 `vault/own`。

## 标准类目

| category | 含义 | 示例 |
|----------|------|------|
| `foundation` | 立项、假设、会议、干系人 | lean-canvas、会议纪要 |
| `discover` | 调研、竞品、旅程、访谈综合 | 竞品分析、journey-map |
| `define` | 问题定义、JTBD、优先级 | problem-statement、OKR |
| `deliver` | PRD、故事、验收、发布说明 | prd、user-stories、AC |
| `design` | 体验 / 视觉相关流程 | 前端品味、可用性走查 |
| `engineering` | 工程实现、码评、调试、测试约定 | 代码审查清单 |
| `ops` | 发布、值班、事故、运维 | 发布检查、复盘 |
| `meta` | 本库烟测、通用元流程（非根目录 meta-skills） | hello-skillvault |
| `inbox` | 暂存、待归类 | 新收录尚未归类 |

新增类目要改本表，并保持总数大约 **≤10**；过碎就合并。

## Frontmatter 示例

```yaml
---
name: my-skill
description: ...
license: MIT
compatibility: linux, windows
metadata:
  category: deliver
  tags: [prd, writing]
  vault: own
---
```

## 列表与安装

- CLI：`py cli/sv.py list` 会显示 `category`  
- 安装目标仍是 IDE 的 `skills/<skill-name>/`（**不**把 category 带进 IDE 路径，保持各工具扁平发现）  
- 收录转化：默认写入 `vault/imported/inbox/<name>/`，Gate B 再归入正式类目  

## 索引（可选）

[`registry/catalog.yaml`](../registry/catalog.yaml) 可手维或由脚本生成，便于浏览；真相源仍是目录树。
