# 登记工程与研究状态盘点

## 绑定

- 本地公开基线：`main@3084ee567eefb80b47e1cd40aea1a13399734282`，clean；相对 `origin/main` 本地领先6个提交，不冒充已推送远端。
- 付费叠加层：`codex/paid-outline-review@b0e72a263c87bf19d3eaa36b2600caee61880669`，clean，包含当前 `main`。
- 付费实验组合：`codex/paid-outline-post-sync-r2@c3477de3cb29251a8df13b4ff1ccb7b60ed2bb58`，clean，包含当前付费叠加层。

## 尚未完成的工程项

| 项目 | 当前状态 | 下一动作 | 真实验证要求 |
| --- | --- | --- | --- |
| `UL-005` 篇幅验收来源绑定/真正独立 verifier | HOLD；同模型自审和同模型独立 Agent 均误放固定坏 D1 | 先做来源 span+hash 或异模型 verifier 的最小原型，不先补胶水 | 固定 R8 坏稿必须 D0，固定 R11 好稿必须 D1 |
| `OT-001-composite` 提纲+篇幅有序组合 | Claude 目标链有成功 D1与安全 D0；仍受 `UL-005` 风险约束 | UL-005 未闭环前不合入付费分支；随后再做祖先/allowlist/clean/smoke | Claude 已有；Codex、WorkBuddy / CodeBuddy 组合尚无在线生命周期 |
| `OT-002` 用户提纲修正 | 未实现、无专门样本 | 先做正文前最小修正原型，处理层级冲突、重复章节、缺失必需部分、材料覆盖 | 先真实提纲与成稿，不先扩三宿主工程 |
| 付费同步与 allowlist | r2 修改共享 Claude adapter，当前不在显式付费差异 allowlist | 共享宿主修复应先进入 `main` 再同步付费，或经明确授权扩 allowlist | adapter 变化后补 Claude smoke，不补普通写稿矩阵 |
| 候选可达性计数刷新 | main 28脚本/21 CLI/195活动 Markdown；paid 30/23/197；r2 30/23/198 | 候选确定或合入后刷新证据计数 | 无需真实写稿 |

## 仅观察或历史 HOLD

- `MT-004` 信息熵与重复规则：维持 `OBSERVE`；没有真实稿回退，不建立公共大字典。
- 本地 Qwen3.8 27B：5项技术完成但无可核验 Skill 读取回执，继续作为实验资产，不纳入正式任务池。
- `WR-005` 常用语机械化 R1—R6：已有事实、篇幅、职责和文种回退，保持 HOLD，不继续叠 prompt。
- 组合延迟212—1106秒：当前作为付费体验成本观察；功能正确前不单开性能工程。
- 旧 `length-band-hook-v162`、`under-length-hook-v162-v2`、`v163-protective-expansion-gate`：历史 HOLD，不复活旧准入结论。

## 可达性与孤儿结论

三个工作树的 `maintenance.tests.test_repository_reachability` 均为7/7 PASS；付费定向 outline/Claude adapter 在 paid 为19/19、r2为21/21。当前未发现新孤儿脚本、孤儿 Markdown 或只有测试可达的 CLI。

旧维护证据中的28脚本、21 CLI、195活动 Markdown 只对应当前 `main`；不能继续当作 paid/r2 数量。静态入口通过不替代 Codex、WorkBuddy / CodeBuddy 的真实组合生命周期。
