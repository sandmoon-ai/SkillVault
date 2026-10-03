# 个人私有仓（L3）— 书系与私有 own Skills

**状态：** 已定案（2026-10-03）  
**关联：** [taxonomy.md](../taxonomy.md)、[status.md](../status.md)、公开仓 `sandmoon-ai/SkillVault`

## 1. 决策

书系 / 个人学习笔记类 Skill **不放进公开仓**，以免误标开源许可或公开再分发衍生内容。

| 仓库 | 可见性 | 内容 |
|------|--------|------|
| `sandmoon-ai/SkillVault` | 公开 | CLI、门禁、文档、公开样例（如 `hello-skillvault`、imported 样例） |
| `sandmoon-ai/SkillVault-personal` | **私有** | 含书系 `from-book` 等个人 own Skills；用于多机同步 |

## 2. 多机同步（私有仓）

在每台需要书系的机器上：

```bash
git clone https://github.com/sandmoon-ai/SkillVault-personal.git
cd SkillVault-personal
pip install -e ".[dev]"
py cli/sv.py list
py cli/sv.py install --all --ide cursor --os windows   # 按本机 IDE/OS 调整
# 或: py cli/sv.py install minto-pyramid --ide cursor --os windows
```

换机 / 更新：

```bash
git pull
py cli/sv.py install <skill> --ide <ide> --os <os> --force
# 或 doctor 看 pending 后按需安装
py cli/sv.py doctor --ide cursor --os windows
```

## 3. 与公开仓的关系

- **贡献开源脚手架 / 门禁 / 公开样例** → PR 到 `SkillVault`。  
- **增删改书系与私有 own** → 只在 `SkillVault-personal` 提交（勿把书系 PR 进公开仓）。  
- 定期把公开仓 `main` merge / rebase 进私有仓，以领取 CLI 与门禁更新（由维护者在私有仓操作）。

## 4. 公开仓约定

- 公开 `vault/own` **不得**再合入 `from-book` 书系包。  
- taxonomy 中的 `from-book` 标签仅用于**私有仓**内组织；公开文档可提及该标签语义，但不承载书系正文。  
- CI / Ruleset 只约束公开仓。

## 5. 非目标

- 不在公开 CI 中扫描私有仓内容。  
- 本阶段不做「双 root / SKILLVAULT_EXTRA_ROOT」自动合并；两仓择一工作目录即可（日常用私有仓即可覆盖公开能力 + 书系）。
