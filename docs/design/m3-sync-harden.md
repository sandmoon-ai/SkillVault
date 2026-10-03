# M3 — Sync 与硬化设计

**状态：** 已完成（2026-10-03）  

**关联：** [status.md](../status.md)、[architecture.md](../architecture.md)、[`cli/`](../../cli/)  
**上游 URL↔vault 定时检知**见 [upstream-watch.md](./upstream-watch.md)（勿与本文混淆）。

## 1. 目标

1. **Vault↔IDE Sync 可测：** 用 fixture 锁定「vault 有、IDE 无 → 待装；IDE 有、vault 无 → 孤儿」报告语义  
2. **换机可复现：** 文档写清 clone → 装依赖 → install 的清单  
3. **现状对齐：** `docs/status.md` 与仓库真实能力一致  

> 命名说明：今日 `cli/sync_cmd.py` 实现的是**上游 registry 再拉取**；本文规格是 **vault↔IDE 有无对照**（实现时可用子命令如 `sv status` / `sv doctor`，或拆分 `sync --target ide`，避免一词两义）。

## 2. Vault↔IDE Sync 行为规格

### 2.1 命令（目标形态）

```bash
# vault ↔ IDE 有无对照（本里程碑）
py cli/sv.py sync --ide <ide> --os <os> [--scope user|project] [--project-root <path>]

# 上游 registry 再拉取（既有能力；勿与上混用同一条命令）
py cli/sv.py sync <name>|--all [--apply]
```

### 2.2 报告语义

| 类别 | 含义 | 建议动作 |
|------|------|----------|
| pending_install | vault 有、目标 IDE 目录无同名 skill | `sv install <name> ...` |
| orphan_in_ide | IDE 有、vault 无对应 name | 人工确认：迁回 vault 或删除 IDE 侧 |
| in_sync | 两侧都有同名目录 | 不强制内容 diff（本周期不做哈希比对） |

输出：stdout 人类可读；可选日后加 `--json`（非本周期必须）。

### 2.3 范围

- 扫描 vault：`own` + `imported` 下所有含 `SKILL.md` 的包（跳过 `_template`）  
- 扫描 IDE：`resolve_install_dir` 的父目录下一级子目录名  
- **不**自动安装、**不**自动删除  

## 3. 实现任务拆解

### 3.1 Fixture 单测

| 文件 | 覆盖 |
|------|------|
| `tests/test_sync.py` | 临时 vault + 临时 home：一侧缺则 pending；一侧多则 orphan；两侧齐则 in_sync |

### 3.2 换机清单（写入本文 §5 与 status）

新机器最小步骤：

1. `git clone` 本仓库  
2. Python 3.11+；`pip install -e ".[dev]"`（或按 `pyproject.toml`）  
3. `py -m pytest` 确认环境  
4. `py cli/sv.py list`  
5. `py cli/sv.py install <skill> --ide <ide> --os <os>`（按需）  
6. （可选）按 meta-skills 用 AI 安装  

### 3.3 文档收束

- 刷新 [status.md](../status.md)：已完成 / 进行中 / 明确不做  
- README「当前进度」链到本目录  
- 确认 [architecture.md](../architecture.md) 与实现无矛盾（有则改 architecture，不另开分叉叙事）  

## 4. 完成标准

- [x] `tests/test_ide_sync.py` 合入且 CI 绿  
- [x] 换机清单可按步骤执行（至少作者自测一遍）  
- [x] `status.md` 与设计目录链接完整  
- [x] 验收记录已填  

## 5. 换机清单（定稿）

```text
1. git clone <SkillVault>
2. cd SkillVault
3. 创建 venv（推荐）并 pip install -e ".[dev]"
4. py -m pytest
5. py cli/sv.py list
6. py cli/sv.py install hello-skillvault --ide cursor --os <your-os>
7. （可选）py cli/sv.py sync --ide cursor --os <your-os>
```

Windows 注意：bash 若为 WSL stub，脚本测试会 skip bash runner（见 `docs/script-testing.md`）。

## 6. 验收记录（实现后填写）

| 日期 | sync 单测 | 换机清单自测 | status 已刷新 |
|------|-----------|--------------|---------------|
| 2026-10-03 | pass（test_ide_sync） | pass：list / install 已有；`sv sync --ide cursor --os windows` 输出 pending/orphan/in_sync | pass |

## 7. 非目标（M3）

- sync 自动双向镜像或内容 hash 强制一致  
- GUI  
- 企业 managed 路径  
- 上游定时检知（见 [upstream-watch.md](./upstream-watch.md)，不在本篇实现清单内重复）  
