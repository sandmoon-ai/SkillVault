# 下一阶段设计文档

本目录把「Phase 1–2 设计计划」落成可执行的设计说明，供实现与验收对照。  
总原则仍以 [architecture.md](../architecture.md)、[taxonomy.md](../taxonomy.md) 为准。

## 里程碑

| 文档 | 里程碑 | 目标 |
|------|--------|------|
| [m1-install.md](./m1-install.md) | M1 安装闭环 | CLI/AI 安装行为锁定 + Windows 双 IDE 验收 |
| [m2-import.md](./m2-import.md) | M2 收录闭环 | URL→门禁→imported 样例 |
| [m3-sync-harden.md](./m3-sync-harden.md) | M3 Sync 与硬化 | vault↔IDE 有无对照、换机清单 |
| [upstream-watch.md](./upstream-watch.md) | 上游检知 | 每周定时 diff + 自动 Issue（不自动合入） |
| [import-security.md](./import-security.md) | 收录安全 | 收纳前扫描；Gate B 与人审一并出示 |
| [security-rules-watch.md](./security-rules-watch.md) | 规则维护 | 定期检知主流规则源 → Issue；人决定是否采纳 |
| [issue-milestone-standard.md](./issue-milestone-standard.md) | 推进方式 | Issue / Milestone 命名、模板、DoD |

制造阶段用 GitHub **Milestone + Issue** 推进；标准见上表末行。Issue 表单在 `.github/ISSUE_TEMPLATE/`。

## 执行顺序

```text
M1 单测与安装验收
  → M2 intent + 真实公开 Skill 样例
  → M3 vault↔IDE sync 单测 + 文档收束
  → 上游定时检知（registry 有样例后）
```

全程走分支 + PR（Ruleset `protect-main` 要求 `Skill script tests`）。

## 本周期明确不做

- GUI / 同一 Skill 多路径同时安装  
- 强制「必须 PR 才能 push main」  
- 非 Skill 体系文件全量自动转换  
- 企业 managed skills 路径  
- CI 上 Windows/macOS runner（成本策略）  

## 状态

设计文档：**已落地**（本目录）。  
实现与实机验收：按各篇「验收记录」节推进，完成后回填勾选与日期。
