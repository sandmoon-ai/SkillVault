---
name: grill-with-docs
description: >
  User-invoked grilling session that also writes glossary and ADRs as
  decisions crystallise. Use when the user wants grill-with-docs or a
  grilling session that updates project domain docs. Composes grilling +
  domain-modeling.
license: MIT
compatibility: linux, macos, windows
disable-model-invocation: true
metadata:
  category: engineering
  tags: [matt-pocock, grilling, interview, adr, glossary]
  vault: imported
---
> SkillVault import from [mattpocock/skills](https://github.com/mattpocock/skills). Install via SkillVault; do not hardcode IDE skill paths.

# Entry skill

Upstream is a one-line Skill-tool dispatcher. On hosts without reliable Skill chaining, execute the composed skills explicitly:

1. Load and follow the `grilling` skill from this SkillVault suite (sibling install: `grilling/SKILL.md`). Do not invent a second protocol.
2. Load and follow the `domain-modeling` skill from this SkillVault suite (sibling install: `domain-modeling/SKILL.md`). Do not invent a second protocol.

If your host can invoke skills by name via a Skill tool, calling `grilling`, `domain-modeling` is equivalent.
