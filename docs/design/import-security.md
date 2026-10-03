# 收录前安全检查（Import Security Scan）

**状态：** v1 已实现（`sv security-scan`；`sv import` 自动扫描；`--apply` 遇 FAIL 默认拒绝）  

**关联：** [m2-import.md](./m2-import.md)、[meta-skills/import-from-url](../../meta-skills/import-from-url/SKILL.md)、[architecture.md](../architecture.md)

## 1. 目标

对拟收纳的 Skill（`.cache` 或转化草稿）在 **合入 vault 之前**跑一轮确定性安全检查；  
**Gate B 人确认时必须同时看到检查报告**（摘要 + 明细），再决定是否继续 Gate C。

```text
fetch → .cache
  → security scan → SECURITY_REPORT.md（或 stdout + 同内容文件）
  →（可选）AI 转化
  → Gate B：人同时审 diff + 安全报告
  → 通过后才 --apply / 写 vault
```

检查是**辅助人审**，不是替代人审；也不能替代脚本 pytest。

## 2. 何时跑

| 时机 | 要求 |
|------|------|
| `sv import` 拉取完成后 | **默认自动**跑 scan，报告写入 cache 旁路文件 |
| AI 收录通路 | Fetch 摘要之后、展示 Gate B 之前 **必须跑并展示** |
| `sv import --apply` / 写 `vault/imported` 前 | 若无报告或报告过期（源树变更），**拒绝合入**并提示先 scan |
| 上游 `sync` 有 diff、准备收纳新版本前 | 对新 cache **再跑一遍**，结果进 Issue/PR 说明 |

## 3. 检查项（v1）

严重级别：`critical`（默认阻断合入）/ `warn`（须人明示接受）/ `info`。

| ID | 级别 | 检查 | 说明 |
|----|------|------|------|
| `secret-pattern` | critical | 疑似密钥/令牌 | 如 `AKIA…`、`api_key=`、私钥头、`ghp_`、`xoxb-` 等启发式；命中列出文件:行 |
| `binary-opaque` | warn | 非文本/大二进制 | 无合理扩展名的 bin、或单文件 > 阈值（建议 512KB）；assets 图片可 info |
| `archive-exec` | warn | 压缩包 / 安装器 | `.zip`/`.tar`/`.exe`/`.dll`/`.so` 等 |
| `script-danger` | critical→warn | 脚本高危片段 | `curl\|bash`、`irm\|iex`、`eval(`、下载后执行、写 `~/.ssh`、改系统目录等；按规则表分级 |
| `exfil-hint` | warn | 外传线索 | 脚本/正文中硬编码可疑外发 URL、webhook、telegram/discord token 形态 |
| `path-escape` | warn | 路径逃逸 | 指令或脚本中 `../` 写到包外、绝对路径写系统目录 |
| `allowed-tools-broad` | warn | frontmatter 工具过宽 | `allowed-tools` 异常宽泛时标出（若字段存在） |
| `size-tree` | warn | 树过大 | 文件数或总大小超阈值（建议：>200 文件或 >5MB） |
| `skill-md-missing` | critical | 无 `SKILL.md` | 无法作为 Agent Skills 包收纳 |
| `license-unknown` | info/warn | 许可不明 | 无 LICENSE 线索时 warn（与 Gate A 许可勾选配合） |

规则表放实现代码/配置（如 `cli/security_rules.yaml`），本设计只定类别与门禁语义。  
**误报允许**：人可在报告上标注「已审接受」后继续；`critical` 需在 intent/Gate B **显式写明接受原因** 才允许合入。

## 4. 报告形态

路径建议（拉取后）：

```text
.cache/import/<id>/_skillvault_security.json    # 机器可读
.cache/import/<id>/_skillvault_security.md      # 给人读；Gate B 展示这份
```

Markdown 报告至少包含：

1. **结论**：`PASS` / `PASS_WITH_WARNINGS` / `FAIL`  
2. **摘要计数**：critical / warn / info  
3. **逐条发现**：ID、级别、文件路径、短摘录、建议  
4. **扫描元数据**：时间、规则版本、扫描根路径  

AI 在 Gate B 对话中应：

- 贴结论 + critical/warn 列表（可折叠长摘录）  
- 附上报告相对路径，便于人打开全文  
- **未展示报告不得请求「确认合入」**

CLI：`sv import` 结束时打印结论一行；`sv security-scan <cache-or-skill-path>` 可单独重跑。

## 5. 与门禁的关系

| 门禁 | 安全检查角色 |
|------|----------------|
| A | 不强制跑（尚可未 fetch）；已知高风险源可在 intent 备注 |
| B | **必看报告**；intent 模板增加勾选 |
| C | 合入 PR 描述应链到报告结论；CI 可选对 `vault/imported/**` 再扫一遍（防直接推送绕过） |

Intent Gate B 勾选（见模板）：

- [ ] 已阅读 `_skillvault_security.md`（或等价输出）  
- [ ] 无未接受的 `critical`；所有 `warn` 已人工确认  

## 6. 双通路

| 通路 | 行为 |
|------|------|
| CLI | fetch 后自动 scan；`--apply` 前校验报告存在且非 FAIL（除非 `--accept-security-risks` + 原因文件，高级慎用） |
| AI | 与 CLI 相同检查器（优先调用 `sv security-scan`）；把 MD 报告纳入 Gate B 材料 |

同一套规则，避免 AI「口头说没事」却无报告文件。

## 7. 实现任务拆解

1. `cli/security_scan.py` + 规则配置 + `sv security-scan`  
2. 挂入 `import_cmd`（fetch 后、`--apply` 前）  
3. 更新 `meta-skills/import-from-url` Gate B 步骤  
4. 单测：夹具包（干净 / 假密钥 / 危险脚本）  
5. 样例收录时附带一份真实报告进 PR 说明（报告本身可不进 vault，或摘要进 SOURCE 备注）

## 8. 完成标准

- [x] 对 `.cache` 技能树可产出 JSON + MD 报告  
- [x] Gate B 材料含报告；模板勾选已更新  
- [x] `--apply` 在 FAIL 时默认拒绝  
- [x] 单测覆盖至少 1 个 PASS、1 个 FAIL 夹具  
- [x] [m2-import.md](./m2-import.md) / [status.md](../status.md) 已链到本文  

## 9. 非目标（v1）

- 完整恶意软件沙箱执行  
- 保证零误报或替代法律/合规审计  
- 对已安装到 IDE 的副本做运行时防护（安装仍只是投影）  
- 自动「修复」上游恶意内容（只报告，转化时人/AI 可删改后再扫）  

## 10. 主流规则调研（2026-10）

结论：**已有面向 Agent Skill 的专门扫描器与 OWASP 清单**；通用密钥扫描（Gitleaks 等）仍是底座。SkillVault v1 应对齐这些类别，而不是自创一套孤立规则。

### 10.1 专门面向 Skill 的主流来源

| 来源 | 性质 | 规则/能力概要 |
|------|------|----------------|
| [OWASP Agentic Skills Top 10](https://owasp.org/www-project-agentic-skills-top-10/) + [评估清单](https://owasp.org/www-project-agentic-skills-top-10/checklist.html) | 风险框架 + 审包清单 | 安装前扫描、密钥扫描（Gitleaks/TruffleHog）、依赖当不可信代码、推荐 SkillSpector 等；多工具组合 |
| [NVIDIA SkillSpector](https://github.com/NVIDIA/SkillSpector)（Apache-2.0） | 开源扫描器 | ~71 模式 / 17 类：注入、外泄、提权、供应链、过度代理、记忆投毒、危险代码 AST、YARA、MCP 等；静态 + 可选 LLM；SARIF/MD/JSON |
| [SkillSafe ruleset](https://skillsafe.ai/security/ruleset_v2026.06.12/) | 公开规则集 | 硬编码凭证、外泄 webhook、agent 记忆/配置投毒、`base64\|exec`、反弹 shell、持久化、Unicode 隐写、ClickFix 社工、hooks/MCP 插件面 |
| [Bitdefender Agent-Skill-Scanner](https://github.com/bitdefender/Agent-Skill-Scanner) | 开源扫描器 | 16 类行为检测：eval/exec、混淆、网络、挖矿、反弹 shell、download-and-exec、不可见 Unicode 等 |
| [Cisco skill-scanner](https://github.com/cisco-ai-defense/skill-scanner) | 开源扫描器 | 签名/YARA/行为/可选 LLM；策略可配；文件数与大小限额 |
| 社区清单（如 RuleSell 10-point、skill-static-review） | 人工审包流程 | 先惰性下载再审；查 `scripts/`；查 description 注入；`xxd` 查零宽/bidi Unicode |

### 10.2 通用（非 Skill 专用）但仍主流的底座

| 工具/规范 | 用途 |
|-----------|------|
| **Gitleaks / TruffleHog / GitHub secret scanning** | 密钥与令牌（OWASP 清单明确要求） |
| **Semgrep / Bandit** | 脚本危险 API（`eval`、`subprocess` 等） |
| **OSV / pip-audit / npm audit** | 若 Skill 带依赖清单时的 CVE |
| **OWASP MCP Cheat Sheet** | 若包内带 `.mcp.json` / 工具描述：投毒描述、rug-pull、最小权限 |

### 10.3 业界反复出现的检查类别（共识）

1. **密钥/凭证**硬编码  
2. **Download-and-execute**（`curl\|bash`、`irm\|iex`、base64 解码执行）  
3. **数据外泄**（webhook/ngrok/requestbin、硬编码外发）  
4. **反弹 shell / 原始 socket**  
5. **持久化**（cron、LaunchAgent、改 shell profile）  
6. **Agent 记忆与配置投毒**（写 `CLAUDE.md` / `MEMORY.md` / `.cursorrules` / `~/.claude`）  
7. **Prompt 注入与隐写**（ignore previous…、零宽/bidi Unicode、homoglyph）  
8. **危险执行原语**（eval/exec/Invoke-Expression；常作能力指示，与组合规则一起判）  
9. **供应链**（嵌套压缩包、异常依赖、安装钩子）  
10. **权限/工具面过宽**（`allowed-tools`、hooks 高频执行、捆绑 MCP）  

### 10.4 对 SkillVault 的建议（相对 §3 v1）

| 策略 | 说明 |
|------|------|
| **v1 自研轻量规则** | 保留：离线、无外呼、可贴进 Gate B；对齐上表 1–7、9 的启发式子集 |
| **v1 增补（相对原稿）** | 增加：`unicode-obfuscation`、`prompt-injection-phrase`、`agent-config-poison`（写记忆/IDE 规则文件） |
| **v1.5+ 可选集成** | Gate B 报告可附加「若本机已装 SkillSpector：`skillspector scan …` 的输出」；不强制依赖商业云 |
| **密钥规则** | 优先复用 Gitleaks 规则思路或调用 `gitleaks`（若 CI/本机可用），避免自维护完整密钥正则库 |
| **不替代人审** | 与 OWASP / skill-static-review 一致：自动化 + 人工勾选；审查时把 Skill 正文当**数据**防审阅注入 |

### 10.5 建议增补进 v1 规则表的 ID

| ID | 级别 | 对齐来源 |
|----|------|----------|
| `unicode-obfuscation` | high/critical | SkillSafe Unicode；RuleSell / Pillar「Rules File Backdoor」 |
| `prompt-injection-phrase` | warn→critical | SkillSpector / 社区 auditor（ignore previous、exfil in description 等） |
| `agent-config-poison` | critical/high | SkillSafe agent memory & config；写 `CLAUDE.md`/`.cursorrules`/`~/.claude` |

§3 原表仍有效；实现时以本节 + §3 合并为 `cli/security_rules.yaml`。  

### 10.6 规则本身的更新作业

规则需定期对照上游演进：**自动化只负责检知并开 Issue，是否采纳由人决定。**  
规格见 [security-rules-watch.md](./security-rules-watch.md)（每月 Ubuntu、钉扎来源指纹、标签 `security-rules`、不自动改 YAML）。  
