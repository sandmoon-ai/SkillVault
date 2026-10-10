---
name: grill-me
description: >
  User-invoked relentless interview to sharpen a plan or design. Use when
  the user says grill-me, grill this plan, or wants a grilling session
  before building. Delegates to the grilling skill.
license: MIT
compatibility: linux, macos, windows
disable-model-invocation: true
metadata:
  category: engineering
  tags: [matt-pocock, grilling, interview]
  vault: imported
---
> SkillVault import from [mattpocock/skills](https://github.com/mattpocock/skills). Install via SkillVault; do not hardcode IDE skill paths.

# Entry skill

Upstream is a one-line Skill-tool dispatcher. On hosts without reliable Skill chaining, execute the composed skills explicitly:

1. Load and follow the `grilling` skill from this SkillVault suite (sibling install: `grilling/SKILL.md`). Do not invent a second protocol.

If your host can invoke skills by name via a Skill tool, calling `grilling` is equivalent.
