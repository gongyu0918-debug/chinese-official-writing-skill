# `UL-006-R2` Alibaba2 Codex Stop 首轮结果

日期：2026-08-30

状态：`DEFERRED_NEXT_SESSION / CANDIDATE_BRANCH_ONLY / NOT_MAIN`

## 结论

已完成当前启动的 Alibaba Token Plan 2 四题批次；按用户要求不再启动其他 provider。动态能力的 Codex companion 能真实注册、读取 Skill、接收 `UserPromptSubmit` / `PostToolUse` / `Stop` 并形成终态，但当前只有一题真正触发动态修订，且安全 D1 未获选，不能进入 `main`。

事故通报和普通办理通知的 D0 已明显长于材料，不需要动态补长；前者正文安全，后者暴露了与动态 Hook 无关但必须后续处理的普通写稿硬风险。明确80字上限正确旁路。

## 逐题

| 题目 | 真实结果 | 裁决 |
| --- | --- | --- |
| `U1` 未决情况说明 | D0 正文96字，材料103字；真实触发后 D1 为147字。D1 补回“本次材料未附”，但新增由 `823/860` 计算并四舍五入的 `95.7%`，机械门以 `under_length_number_added_dropped_or_changed` 选择 D0；终态 `under_length_complete`，D0 交付 hash 精确一致 | 生命周期闭环；目标未通过。D0 本身漏事实，D1 的透明算术是否应被硬数字门拒绝须拆成下一原子，不能把安全回退冒充解决过短 |
| `U2` 阶段事故通报 | D0 正文115字，材料96字，已超过动态近材料区间，未启动 under-length；普通门终态 complete，交付 hash 一致。完整保留日期、人员、处置、道路和调查状态，并以“后续情况将及时通报”自然收束 | 写稿通过；正确不触发。再次证明该续报句不是材料外承诺，也不是必写模板 |
| `U3` 办理通知 | D0 正文134字，材料72字，未启动 under-length；普通门终态 complete，交付 hash 一致。但新增“梳理”执行动作、材料未给的落款主体“信息中心”和成文日期 `2026年8月30日` | 写稿不通过；属于普通 Skill / reference 风险，不归罪于本次未触发的动态 Hook，下一轮单独修 |
| `C1` 80字上限 | 53字正文，记录 `under_length_bypass=explicit_upper_bound`，普通门终态 complete，交付 hash 一致 | 旁路通过；不设统一100字下限 |

## 待续原子

1. `UL-006-R3-ARITHMETIC`：只验证可由同一句已给数字精确复算的透明比例，比较“允许但非必写”与保持当前硬拒绝；须保护原数、分母、范围和舍入说明，不顺带放开任意新数字。
2. `UL-006-R3-COMPLETENESS`：沿用 U1，只要求 D1 补回 D0 遗漏的“本次材料未附”，不得新增比例；检查事实完整性是否能在不扩机械数字门时获选。
3. `WR-018-NOTICE-ISSUER-DATE`：沿用 U3，只处理材料未给落款主体和日期，以及材料未要求的新执行动作；先跑普通 Skill 真实 A/B，再决定改通知叶还是共享信息选择规则。
4. 其余 `alibaba1`、`ollama`、`opencode`、`minimax` 的同题 Codex Stop 生命周期留待下一轮；不从本轮单 provider 外推稳定性。

## 编排事实

第一次输出根把全局 `-a never` 放在 `exec` 后，四次均在模型调用前被 CLI 参数解析拒绝，0条模型消息，记 `ENV_ORCHESTRATION_INVALID`。修正为全局参数位置后使用全新输出根完成上述四题；这不是产品失败。

首轮结果采集器把“未启动动态事务但普通门已完整交付”的 U2/U3 误记为缺少 Hook record。直接读取隔离 `CODEX_HOME/plugins/data/.../candidate-ai-gate-hook/` 后确认两题均有 `hook_phase=complete`、`delivery_verified=true` 和匹配 `emitted_sha256`；采集器已修正，未重跑模型。

## 实际命令

```powershell
python -B maintenance/tests/evidence/ul006-implicit-underlength-r2/run_live.py --prepare
python -B maintenance/tests/evidence/ul006-implicit-underlength-r2/run_live.py --provider alibaba2
python -B maintenance/tests/evidence/ul006-implicit-underlength-r2/run_live.py --summarize
```

候选 `389b43f4` 的定向单测此前为33/33通过；本结果不改变其“仅候选、待继续验证”状态。
