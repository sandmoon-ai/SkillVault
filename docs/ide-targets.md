# IDE 安装路径

由 [`adapters/targets.yaml`](../adapters/targets.yaml) 解析。  
安装属于产物链的最后一环：仅在 Skill **已合入 vault** 且人确认需要落地时执行。

**AI 与 CLI 共用本表。** AI 安装时读 `targets.yaml` 展开路径并复制文件；CLI 使用相同模板。规程见 [`meta-skills/install`](../meta-skills/install/SKILL.md)。

默认范围：**user**。项目级必须同时指定 scope=project 与 project-root。

| IDE | CLI id | User（Linux/macOS） | User（Windows） | Project |
|-----|--------|---------------------|-----------------|---------|
| Cursor | `cursor` | `~/.cursor/skills` | `%USERPROFILE%\.cursor\skills` | `<root>/.cursor/skills` |
| Claude Code | `claude-code` | `~/.claude/skills` | `%USERPROFILE%\.claude\skills` | `<root>/.claude/skills` |
| Codex | `codex` | `~/.agents/skills` | `%USERPROFILE%\.agents\skills` | `<root>/.agents/skills` |
| GitHub Copilot | `copilot` | `~/.copilot/skills` | `%USERPROFILE%\.copilot\skills` | `<root>/.github/skills` |
| Pi | `pi` | `~/.pi/agent/skills` | `%USERPROFILE%\.pi\agent\skills` | `<root>/.pi/skills` |
| OpenCode | `opencode` | `~/.config/opencode/skills` | `%USERPROFILE%\.config\opencode\skills` | `<root>/.opencode/skills` |

## 说明

- 部分工具也扫描 `~/.agents/skills`。安装器写入各 IDE **主路径**，避免同一 Skill 被多路径重复加载。
- 安装复制 Skill 目录时**排除** `SOURCE.md`（溯源留在 vault，不进 IDE）。
- Frontmatter 按 [`adapters/frontmatter.yaml`](../adapters/frontmatter.yaml) 做字段裁剪；vault 源文件不变。
- 未指定 `--scope project` 时，不得写入任何项目目录（治理底线）。

## 示例

```bash
# 用户级（默认）
py cli/sv.py install hello-skillvault --ide cursor --os windows
py cli/sv.py install hello-skillvault --ide claude-code --os linux

# 项目级（显式）
py cli/sv.py install hello-skillvault --ide cursor --os windows \
  --scope project --project-root D:\my-app
```

业务仓库里的 `CLAUDE.md` / `AGENTS.md` 仍留在业务仓；SkillVault 只投影 Skills，不管理那些文件。详见 [architecture.md](./architecture.md)。
