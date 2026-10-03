---
name: hello-skillvault
description: >-
  Smoke-test SkillVault install. Use when verifying that a skill was installed
  correctly into an IDE user or project skills directory.
license: MIT
compatibility: linux, windows
metadata:
  vault: own
---

# Hello SkillVault

Conforms to [Agent Skills](https://agentskills.io/specification).

## When to use

- After running `sv install hello-skillvault --ide <ide> --os <os>`
- When checking that user-level vs project-level install paths are correct

## Steps

1. Confirm this file exists under the target IDE skills directory as `hello-skillvault/SKILL.md`.
2. Confirm `SOURCE.md` is **not** present (install must exclude vault provenance files).
3. On Linux/macOS, optional helper: `scripts/hello.sh`
4. On Windows, optional helper: `scripts/hello.ps1`
5. Script tests: `scripts/tests.yaml` — run `py -m pytest tests/test_skill_scripts.py -k hello-skillvault`

## Notes

This skill is intentionally tiny. It exists so SkillVault can validate the install pipeline across IDEs and OSes.
All bundled scripts are covered by smoke tests (repo policy).
