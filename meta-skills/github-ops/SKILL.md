---
name: github-ops
description: >-
  Run common GitHub workflows for the SkillVault repo (branch, PR, Issues,
  Milestones, labels) with gh. Use when the user asks to open/update a PR or
  Issue, manage milestones, push manufacturing work, or 开 PR / 建 Issue /
  Milestone / 合入检查 — not for importing or installing Agent Skills.
---

# GitHub 常用操作（本库 meta-skill）

短 playbook：减少重复解释。规格细节以文档为准，本文不复制长文。

| 文档 | 用途 |
|------|------|
| [CONTRIBUTING.zh-CN.md](../../CONTRIBUTING.zh-CN.md) / [CONTRIBUTING.md](../../CONTRIBUTING.md) | 对外贡献与门禁 |
| [docs/design/issue-milestone-standard.md](../../docs/design/issue-milestone-standard.md) | Issue / Milestone 标准 |
| [docs/ci.md](../../docs/ci.md) | CI 与 Ruleset |

仓库：`sandmoon-ai/SkillVault`。Windows 上若 `gh` 不在 PATH，试用 `"C:\Program Files\GitHub CLI\gh.exe"`。

## 默认

- 外部变更与制造任务：**分支 + PR**；PR 正文用 `Fixes #n` 关联 Issue  
- 不 `force push` `main`；不跳过 hooks  
- 未请勿改 git config；未请勿 push——用户要求推送/开 PR 时再执行  
- Issue / Milestone 中文内容：经 **UTF-8 JSON 文件** 调 API（见下），避免 PowerShell 管道把中文变成 `?`

## 进度条

```text
GitHub Ops:
- [ ] 确认目标（PR / Issue / Milestone / 仅推送）
- [ ] 本地：分支、提交、测试（若改代码）
- [ ] 远程：push / gh pr create 或 gh issue …
- [ ] 回报链接（PR / Issue / Milestone URL）
```

## 1. 分支与 PR

```bash
git checkout -b <type>/<short-name>    # 例：feat/m1-cli-tests、docs/…
# … 编辑 …
git add <paths>
git commit -m "<why-focused message>"
git push -u origin HEAD
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
- …

## Test plan
- [ ] …

Fixes #<issue>
EOF
)"
```

PowerShell 无 bash heredoc 时：用 here-string 作 `--body`，或 `--body-file`。

标题/说明写清 **why**；制造 Issue 必须挂 `Fixes #n`。

## 2. Issue

- 优先用仓库模板：制造任务 / 验收 / 收录提案 / 缺陷（`.github/ISSUE_TEMPLATE/`）  
- 标题：`动词：对象`（见标准 §2.2）  
- 挂 Milestone：`gh issue create … --milestone "M1 - Install loop"`  
- 标签：`type:task|acceptance|bug|design|import|chore`，可选 `area:*`

```bash
gh issue list --milestone "M1 - Install loop"
gh issue develop <n> --name <branch>    # 若环境支持；否则手动建分支
```

## 3. Milestone

标题格式：`M<n> - <English short name>`（ASCII 连字符 `-`）。

**创建/更新描述（防乱码）：**

1. 用编辑器或 Python 写 UTF-8 JSON：`{"title":"…","description":"…"}`，`ensure_ascii=False`  
2. `gh api repos/sandmoon-ai/SkillVault/milestones --method POST --input body.json`  
3. 更新：`gh api repos/sandmoon-ai/SkillVault/milestones/<n> --method PATCH --input body.json`  

不要把含中文的 Description 经会丢编码的 Shell 字符串管道塞进 API。

只给**即将开工**的 Milestone 拆 Issue；不必一次铺满 M1–M5。

## 4. 合入前检查

```bash
pip install -e ".[dev]"   # 若尚未
py -m pytest -q
gh pr checks <n>          # 或看 PR 页 CI：CI tests
```

Ruleset `protect-main` 要求检查通过；勿 force push / 删 `main`。

## 5. 常用只读

```bash
gh pr view <n> --web
gh issue view <n>
gh api repos/sandmoon-ai/SkillVault/milestones --jq ".[] | [.number,.title] | @tsv"
```

## 不要

- 用本 skill 替代 `import-from-url` / `install`  
- 在 Issue 里贴密钥或完整 `.cache`  
- 静默合入 vault 或跳过 Gate（收录仍走贡献指南）  
- 自动合并 PR，除非用户明确要求且检查已绿  
