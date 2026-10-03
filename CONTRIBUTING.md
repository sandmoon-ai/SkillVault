# Contributing to SkillVault

[中文版](./CONTRIBUTING.zh-CN.md)

Thanks for contributing. This repository is a **public Agent Skill vault**: Git is the source of truth; installs only project skills into IDE paths. External contributors **cannot push `main` directly** — use a **fork + pull request**.

## What to contribute

| Kind | Where | Notes |
|------|--------|--------|
| Import a public skill | `vault/imported/<category>/<name>/` + `registry/sources.yaml` + intent | Follow gates A→C below |
| Author an original skill | `vault/own/<category>/<name>/` | Start from `vault/own/_template/` |
| CLI / docs / design | `cli/`, `docs/`, `meta-skills/`, … | Normal code review |

Installing skills onto **your** machine does **not** require a PR (`sv install` or the install meta-skill).

Do **not** open a PR that only writes into `.cache/` — cache is local and not the vault.

## Ground rules

1. Package format: [Agent Skills](https://agentskills.io/specification) (`SKILL.md` + directory `name`).
2. Categories: [docs/taxonomy.md](docs/taxonomy.md). Prefer `inbox` for new imports until Gate B reclassifies.
3. No secrets, no large binaries, no private/internal-only process docs in this public repo.
4. Scripts under `scripts/` need `scripts/tests.yaml` and must pass pytest — [docs/script-testing.md](docs/script-testing.md).
5. Upstream license must be compatible; record it in `SOURCE.md` / registry.
6. Maintainers review gates; CI must be green (`CI tests`).

## Path A — Import a public skill

```text
Fork → branch
  → intents/<name>.md (from intents/_template-import.md)
  → Gate A (maintainer / you propose; merge waits on approval)
  → fetch into .cache (CLI or AI meta-skill) — summary only
  → security scan report (required when available; until then self-check per docs/design/import-security.md)
  → convert to Agent Skills layout + SOURCE.md
  → PR: vault/imported/... + registry/sources.yaml (+ intent)
  → Gate B/C on the PR (diff + security report)
  → merge when CI green and a maintainer approves
```

Useful commands (from a clone of your fork):

```bash
pip install -e ".[dev]"
py cli/sv.py import <url> [--ref <ref>]          # cache only; do not --apply until reviewed
# after review:
# py cli/sv.py import <url> --apply --category <cat> --name <name>
py -m pytest tests/test_skill_scripts.py -v
```

AI pathway (same gates): open the repo in an agent and follow [meta-skills/import-from-url](meta-skills/import-from-url/SKILL.md).

Design detail: [docs/design/m2-import.md](docs/design/m2-import.md), [docs/design/import-security.md](docs/design/import-security.md).

## Path B — Add an original (`own`) skill

1. Copy `vault/own/_template/` → `vault/own/<category>/<skill-name>/`.
2. Fill `SKILL.md` (`name`, `description` with trigger, `metadata.category` matching the folder).
3. If you add `scripts/`, add `scripts/tests.yaml` and run pytest.
4. Open a PR. No import intent is required for pure `own` skills (a short PR description is enough).

## Pull request checklist

- [ ] Changes match one clear purpose (import / own skill / tooling)
- [ ] Import: intent file + `SOURCE.md` + registry entry
- [ ] Import: security report attached or linked (or explicit self-check summary until scanner ships)
- [ ] Scripts: `tests.yaml` present; CI `CI tests` passes
- [ ] No secrets; license noted for third-party content
- [ ] Docs updated if you change user-facing behavior

## After merge (consumers)

```bash
git pull
py cli/sv.py install <skill> --ide <ide> --os <os> [--force]
```

## Maintainers

- Branch Ruleset `protect-main` requires the `CI tests` check; force-push and branch deletion are blocked — [docs/ci.md](docs/ci.md).
- Prefer merging via PR for all external changes.
- Gate approval is a human decision; bots/CI do not skip A–C.
- Intent Gate sign-off fields must be filled by a **human** (account name or PR review). Agents may draft materials but must not sign as approver.

## Issues and milestones

Manufacturing work follows [docs/design/issue-milestone-standard.md](docs/design/issue-milestone-standard.md).  
Prefer the GitHub issue forms (task / acceptance / import / bug) and attach the matching Milestone.  
Agents operating PRs/Issues/Milestones in this repo should follow [meta-skills/github-ops](meta-skills/github-ops/SKILL.md).

## Questions

Open a GitHub Issue describing the skill source (URL), license, and why it belongs in a shared vault.
