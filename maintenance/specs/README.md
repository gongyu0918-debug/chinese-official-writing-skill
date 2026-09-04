# 轻量需求规格

本目录是产品需求、当前变更和验证覆盖的中间层。它借鉴 OpenSpec 的“需求为真、变更单独记录、证据可追踪”，但不安装 OpenSpec，不增加 slash command、审批流或归档工具。

## 文件

| 文件 | 回答的问题 |
| --- | --- |
| [`requirements.md`](requirements.md) | 产品长期必须做到什么 |
| [`roadmap.md`](roadmap.md) | 哪些已经完成、哪些候选已拒绝或终止、哪些等待新反例、下一步做什么 |
| [`coverage.md`](coverage.md) | 每项需求由什么产品文件、真实稿件和 Hook 证据覆盖 |
| [`public-paid-sync.md`](public-paid-sync.md) | 公开 `main` 与付费提纲候选如何同步、哪些差异可以保留 |
| [`../docs/待办.md`](../docs/待办.md) | 当前迭代的执行细目、环境限制和未闭环反例 |

历史发布、预注册、完整盲审和原始回执仍放在 `maintenance/tests/evidence/`；这里仅链接，不复制大段过程。公开产品说明仍放根 `README.md`；运行时写作规则仍只放 canonical Skill 与 references。

## 更新规则

1. 新要求先归入一个稳定编号；同一机制的新表述补充到原编号，不重复建项。
2. `requirements.md` 只写长期行为和验收场景，不写某次模型票数、临时路径或内部命令。
3. `roadmap.md` 使用 `DONE`、`IN_PROGRESS`、`HOLD`、`REJECTED`、`TERMINATED`、`WAIT_NEW_COUNTEREXAMPLE`、`TODO`。`HOLD` 只表示仍有明确下一原子的活动候选；`REJECTED` 表示已测试候选不准入但不否定需求；`TERMINATED` 表示当前实现方向经多轮最小化仍有硬回退并停止；`WAIT_NEW_COUNTEREXAMPLE` 表示当前基线已覆盖已知场景，只有新的真实失败才重开。环境失败、产品失败和候选拒绝分开记录。
4. `coverage.md` 必须区分：规则存在、真实写稿响应、同稿 Hook 修订、宿主在线生命周期、发行状态。任一列缺失时不得用另一列替代。
5. 写作与 Hook 修稿能力先做最小候选和真实写稿；只有真实输出证明目标机制有效，才精修 coordinator、adapter、组装、镜像和回退测试。
6. 宿主适配只有在该宿主协议文件或中央 coordinator 变化时才要求重跑在线生命周期。若宿主胶水与旧成功样本逐字相同，可用“官方协议同构 + 旧在线实证 + 当前共享能力在其他宿主在线验证 + 当前同稿复放”迁移证据，并明确未重跑。
7. 每次发布后把已发布需求状态写回本目录，并同步 `待办.md` 的当前边界；旧 evidence 保留原文，不回写历史结论。
8. 每次 reference 减载均逐原子做真实写稿 A/B，路线与样本随目标风险预登记，包括纯维护文字删除；当前 R1 的五路设计不固化为后续统一门槛，不回补或改写旧试验结论。批量成稿和同稿 4—7 版质量稳定性按 `WR-020c` 分层统计，D0 与 Hook 终稿分别举证。

## 最小开发顺序

```text
需求与真实反例
  -> 最小 reference / prompt / 强制路由原型
  -> 少量真实写稿或同一 D0 修订
  -> 目标风险确实下降且没有候选独有硬回退
  -> 正式能力核心与有限状态机
  -> 宿主薄适配、组装和必要故障回退
  -> 合并与发布检查
```

不要在语义尚未通过时先扩张三宿主矩阵、全量回归、盲审流水或复杂打包；这些只能证明工程稳定，不能证明稿件可用。

## 本轮审计与登记

2026-09-05 的[逐项规格审计](../tests/evidence/reference-route-audit-r1/spec-audit.md)记录现有状态、证据入口和 AGENTS 规则保留映射；[审核发现](../tests/evidence/reference-route-audit-r1/audit-findings.md)登记已准入的命令路径修正与待修 Hook 问题，完整结论见[本轮结果](../tests/evidence/reference-route-audit-r1/result.md)。当前新增子项为 `MT-004c` 渐进路由、`MT-002a` 命令可执行、`WR-020c` 批量与多版质量、`AH-002b` 日期来源角色和 `HK-005b` 终态/回显；活动状态见 roadmap，不能用原型或旧测试记 DONE。
