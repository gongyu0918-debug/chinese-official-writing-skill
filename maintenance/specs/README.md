# 轻量需求规格

2026-09-06：[v1.6.28发布记录](../tests/evidence/release-1.6.28.md)为当前发行事实；已合入main的两轮Hook修复及新闻日期规则已发布，下文旧轮“未发布”仅指当时。宿主限制、批量与多版质量仍未闭环，市场公开传播与审核单列。

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

2026-09-06 继续构建四项 Hook 质量问题，登记为 `HK-002a` 同稿接续、`CL-001` 默认正文清理、`HK-010` 自然篇幅要求、`HK-002b` 原稿事实复核。工作基线为已发布 main `b77f6381`，独立分支 `codex/hook-quality-build-r1`；[本轮记录](../tests/evidence/hook-quality-build-r1/result.md)分别保留真实参与、正文质量、技术失败与未准入候选，不把全部需求标为完成。

2026-09-05 的[逐项规格审计](../tests/evidence/reference-route-audit-r1/spec-audit.md)记录现有状态、证据入口和 AGENTS 规则保留映射；[审核发现](../tests/evidence/reference-route-audit-r1/audit-findings.md)登记已准入的命令路径修正与待修 Hook 问题，完整结论见[本轮结果](../tests/evidence/reference-route-audit-r1/result.md)。当前新增子项为 `MT-004c` 渐进路由、`MT-002a` 命令可执行、`WR-020c` 批量与多版质量、`AH-002b` 日期来源角色和 `HK-005b` 终态/回显；活动状态见 roadmap，不能用原型或旧测试记 DONE。

本轮获选的命令路径修正和投诉页68-byte删例已随[公开版v1.6.27](../tests/evidence/release-1.6.27.md)发布；新叶清理登记为 `MT-006-RECENT-LEAF-R1`，被拒绝的定向审稿删例、渐进路由原型与未修Hook问题分别保留状态。示例替换已由用户撤销；需求登记继续使用本规格区。

用户随后授权修复四项Hook问题并在合理时合并。[核心修复与真实同稿验证](../tests/evidence/hook-four-fixes-r1/result.md)通过后，合并前补修显式关闭Hook遇清理锁故障仍被阻断的问题；最终788项全量通过，产品提交 `3ce9241e` 已快进合入本地main，未推送或发布。[合并记录](../tests/evidence/hook-four-fixes-merge-r1/result.md)保留原文清理、未适配宿主、成稿事实与多版修改的未完成项；当前状态以roadmap/coverage为准。

本轮继续修复登记为 `REMAINING-HOOK-QUALITY-R1 / MERGED_MAIN / DONE_V1.6.28`：已保留 HK-008 取消清理、DSH 当前回合取消、OpenCode 失败分类和新闻事实年份规则；22次隔离真实调用与4条真实resume七版链共50次真实写稿/修改执行均留证。workflow候选因完整正文缺失及附说明等回退撤回，CodeBuddy/Kimi硬停仍不支持；写稿质量、多版稳定性和原生宿主边界未闭环。详情见[本轮结果](../tests/evidence/remaining-hook-quality-r1/result.md)，本轮没有推送或发布。

2026-09-05 后续授权合并已完成：产品 `a2a817d1`，最终806项全量通过，未推送或发布；纯helper重构与边界见[合并记录](../tests/evidence/remaining-hook-quality-merge-r1/result.md)。随后完成[60次自然任务与五版修改验证](../tests/evidence/natural-writing-stability-r1/result.md)：两处reference候选均拒绝并恢复；自然触发和失败保留口径已写入WR-020c，成稿及多版质量仍在改进。
