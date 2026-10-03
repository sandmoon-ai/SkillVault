---
name: skill-name
description: >-
  What this skill does and when to use it. Include trigger keywords so agents
  can match relevant tasks. (Agent Skills: 1–1024 chars.)
license: MIT
compatibility: linux, windows
metadata:
  category: inbox
  tags: []
  vault: own
---

# Skill Name

Format: [Agent Skills](https://agentskills.io/specification).  
Place under `vault/own/<category>/<skill-name>/` — see [docs/taxonomy.md](../../../docs/taxonomy.md).  
Directory name must equal frontmatter `name`.

## When to use

Describe trigger scenarios and keywords.

## Steps

1. ...
2. ...

## Scripts (optional)

Prefer cross-platform Python, or provide both:

- `scripts/helper.sh` (Linux / macOS)
- `scripts/helper.ps1` (Windows)

**Required with any script:** `scripts/tests.yaml` and passing tests  
（见 [`docs/script-testing.md`](../../../docs/script-testing.md)）。

Optional layout per spec: `scripts/`, `references/`, `assets/`.

Do not hardcode a single IDE install path; SkillVault installs into the active IDE.
