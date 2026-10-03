# 本机 orphan Skill 溯源（A/B）

**状态：** 2026-10-03 核对  
**关联：** [personal-vault.md](./personal-vault.md)、[taxonomy.md](../taxonomy.md)

## A — PM 阶段 / Sprint / utility

| 项 | 值 |
|----|-----|
| **原始仓** | [product-on-purpose/pm-skills](https://github.com/product-on-purpose/pm-skills) |
| **许可** | Apache-2.0 |
| **路径** | `skills/<name>/SKILL.md`（约 68 个正式 Skill） |
| **收录策略** | 公开仓 `vault/imported/<category>/<name>/`，从该仓拉取并写 SOURCE；勿把本机改过的副本当上游 |

类目映射（SkillVault taxonomy）：

| 名前缀 | category |
|--------|----------|
| foundation-* | foundation |
| discover-* | discover |
| define-* | define |
| deliver-* | deliver |
| develop-* | engineering |
| iterate-* / measure-* | ops |
| tool-* / utility-* | meta |

## B — 设计 / 出图类（已再追）

聚合仓 [sickn33/agentic-awesome-skills](https://github.com/sickn33/agentic-awesome-skills) **不是**最原始出处。

| 本机目录名 | **原始仓** | 仓内路径 | 许可 |
|------------|------------|----------|------|
| design-taste-frontend | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | `skills/taste-skill/` | MIT |
| design-taste-frontend-v1 | 同上 | `skills/taste-skill-v1/` | MIT |
| gpt-taste | 同上 | `skills/gpt-tasteskill/` | MIT |
| high-end-visual-design | 同上 | `skills/soft-skill/` | MIT |
| industrial-brutalist-ui | 同上 | `skills/brutalist-skill/` | MIT |
| minimalist-ui | 同上 | `skills/minimalist-skill/` | MIT |
| redesign-existing-projects | 同上 | `skills/redesign-skill/` | MIT |
| full-output-enforcement | 同上 | `skills/output-skill/` | MIT |
| stitch-design-taste | 同上 | `skills/stitch-skill/` | MIT |
| brandkit | 同上 | `skills/brandkit/` | MIT |
| image-to-code | 同上 | `skills/image-to-code-skill/` | MIT |
| imagegen-frontend-web | 同上 | `skills/imagegen-frontend-web/` | MIT |
| imagegen-frontend-mobile | 同上 | `skills/imagegen-frontend-mobile/` | MIT |

**结论：** B 类一律以 **Leonxlnx/taste-skill** 为 registry/SOURCE 上游；聚合仓仅作传播路径。

## C — 书系等

无 GitHub Skill 源 → 仅 [SkillVault-personal](https://github.com/sandmoon-ai/SkillVault-personal)（L3）。
