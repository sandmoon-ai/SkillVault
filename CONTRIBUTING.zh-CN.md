# 参与贡献 SkillVault

[English](./CONTRIBUTING.md)

感谢贡献。本仓库是**公开的 Agent Skill 制度库**：Git 为真相源，安装只是投影到各 IDE。外部贡献者**不能直接推 `main`**，请使用 **fork + Pull Request**。

## 可以贡献什么

| 类型 | 落点 | 说明 |
|------|------|------|
| 收录公开 Skill | `vault/imported/<category>/<name>/` + `registry/sources.yaml` + intent | 走下方门禁 A→C |
| 自建原创 Skill | `vault/own/<category>/<name>/` | 从 `vault/own/_template/` 复制 |
| CLI / 文档 / 设计 | `cli/`、`docs/`、`meta-skills/` 等 | 常规代码评审 |

把 Skill **装到自己电脑**不需要开 PR（`sv install` 或 install meta-skill 即可）。

不要提交「只改 `.cache/`」的 PR——缓存是本地产物，不是 vault。

## 基本规则

1. 包格式：[Agent Skills](https://agentskills.io/specification)（目录名 = `name` + `SKILL.md`）。
2. 类目：[docs/taxonomy.md](docs/taxonomy.md)。新收录优先 `inbox`，Gate B 再归类。
3. 禁止密钥、大二进制、以及仅限内部的流程文档进入本公开仓。
4. `scripts/` 下脚本必须有 `scripts/tests.yaml` 且 pytest 通过——[docs/script-testing.md](docs/script-testing.md)。
5. 上游许可须兼容；在 `SOURCE.md` / registry 中写明。
6. 维护者审门禁；CI（`Skill script tests`）必须绿。

## 路径 A — 收录公开 Skill

```text
Fork → 建分支
  → intents/<name>.md（复制 intents/_template-import.md）
  → Gate A（提议收录；合入前须认可）
  → 拉取进 .cache（CLI 或 AI meta-skill）— 只看摘要
  → 安全检查报告（实现后必附；此前按 docs/design/import-security.md 自查）
  → 转化为 Agent Skills 布局 + SOURCE.md
  → PR：vault/imported/... + registry/sources.yaml（+ intent）
  → 在 PR 上做 Gate B/C（diff + 安全报告）
  → CI 绿且维护者批准后合并
```

在 fork 克隆上常用命令：

```bash
pip install -e ".[dev]"
py cli/sv.py import <url> [--ref <ref>]          # 默认只进 cache；审过再用 --apply
# 人审通过后：
# py cli/sv.py import <url> --apply --category <cat> --name <name>
py -m pytest tests/test_skill_scripts.py -v
```

AI 通路（门禁相同）：在仓库工作区按 [meta-skills/import-from-url](meta-skills/import-from-url/SKILL.md) 执行。

设计细节：[docs/design/m2-import.md](docs/design/m2-import.md)、[docs/design/import-security.md](docs/design/import-security.md)。

## 路径 B — 追加自建（`own`）Skill

1. 复制 `vault/own/_template/` → `vault/own/<category>/<skill-name>/`。
2. 填写 `SKILL.md`（`name`、带触发条件的 `description`、`metadata.category` 与目录一致）。
3. 若有 `scripts/`，补 `scripts/tests.yaml` 并跑通 pytest。
4. 开 PR。纯 `own` 不必写 import intent（PR 说明写清用途即可）。

## Pull Request 检查清单

- [ ] 变更目的单一（收录 / 自建 / 工具）
- [ ] 收录：intent + `SOURCE.md` + registry 条目
- [ ] 收录：附安全报告或链接（扫描器未就绪前附自查摘要）
- [ ] 脚本：有 `tests.yaml`；CI `Skill script tests` 通过
- [ ] 无密钥；第三方内容已注明许可
- [ ] 若影响使用方式，已更新文档

## 合并之后（使用者本机）

```bash
git pull
py cli/sv.py install <skill> --ide <ide> --os <os> [--force]
```

## 维护者

- 分支 Ruleset `protect-main` 要求 `Skill script tests`；禁止 force push / 删分支——[docs/ci.md](docs/ci.md)。
- 外部变更优先经 PR 合并。
- Gate 是否通过由人决定；CI 不能代替 A–C。
- Intent 中 Gate 批准人签字**必须是人类**（账户名或 PR review）；Agent 可起草材料，禁止代签。

## Issue 与 Milestone

制造与验收按 [docs/design/issue-milestone-standard.md](docs/design/issue-milestone-standard.md) 开 Issue，并挂到对应 Milestone。  
开 Issue 时优先选用仓库模板（制造任务 / 验收 / 收录提案 / 缺陷）。  
Agent 在本仓做 PR/Issue/Milestone 时遵循 [meta-skills/github-ops](meta-skills/github-ops/SKILL.md)。

## 疑问

请开 GitHub Issue，说明来源 URL、许可，以及为何适合放进共享 vault。
