# 篇幅不足 Hook：先真实写稿、再补最小工程门

日期：2026-08-14

固定发行基线：`v1.6.4^{commit}=a737791c8ed6fbae82e4a72fb3931e901faafc07`

真实语义修复提交：`999bf92070871243c71e8eaa17fd4eb21673a7a3`

当前候选：`56391e4f2d4e102d3c72b17eb22313efd9dadf4d`

结论：**under-only 目标功能通过真实写稿和 Codex、Claude Code 在线生命周期验证，可进入集成候选。CodeBuddy 当前只完成同指纹静态迁移，不宣称在线执行。**

## 真实写稿先行

第一轮直接把旧扩写提示交给三条指定模型路线，结果并不合格：

- `ollama-cloud/deepseek-v4-flash:0731` 的 W3 从 94 字扩到 377 字，但补入业务增长、服务效果和预算影响等材料外判断；
- `alibaba-token-plan-2/deepseek-v4-flash-0731` 的 W5 从 123 字扩到 378 字，但补入展示互动、参与体验、意见卡内容和统计用途；
- `opencode-go/deepseek-v4-flash` 的 W6 从 231 字扩到 522 字，出现材料外评价和重复扩写；同路线 W4 遇到上游 SSE 格式错误，没有可用终稿，记技术无效且未重试。

据此只修改扩写语义：公文常识限于文种结构、顺序和衔接；新增句的谓词必须能回指请求、材料或 D0；禁止用材料外场景、原因、目的、流程、效果、评价、体验和反馈补字。事实不足时允许逐字返回 D0。

第二轮中，W3、W5 已保守返回原 D0；W6 虽扩至 496 字，但因重复和新增透明计数被机械门拒绝。随后使用事实充分、下限缺口约 19% 的 S1 多品类采购请示继续验证：

| 轮次 | 精确模型 | D0→D1 | 结果 |
| --- | --- | --- | --- |
| R3 | Alibaba Token Plan 2 DeepSeek V4 Flash 0731，max | 268→329 | 事实安全，但距 330 字下限差 1 字 |
| R4 | 同上 | 268→407 | 事实安全，但重复小计和总额，语义验收拒绝 |
| R5 | 同上 | 268→342 | 机械检查通过；事实、状态、文种、自然度和直接使用通过 |

R5 D0 SHA-256 为 `0de60e16bc72bf7d7baacb4fe8ebba973628f896898bc8d37bb5b783caf2b907`，D1 SHA-256 为 `4fb674590e8f2d6d732df4b1fc1d976e6fe32523225939ba51a85646f1ac11f5`。独立 `gpt-5.6-sol` max 只读冻结匿名包，裁决 `ACCEPT`，可用修订为 R5 D1；verdict SHA-256 为 `B02517ACAC73A2F9CB77E16BB3134B89B827EC78B67362C59F24F2755C037C65`。

## 两宿主真实在线生命周期

同一份 268 字 D0 分别经过真实 Hook 的 Stop、一次修订、语义判定、选择和精确终稿回显：

| 宿主 | 精确模型与档位 | D0→终稿 | 事务与哈希 | 结果 |
| --- | --- | --- | --- | --- |
| Codex | `alibaba-token-plan-2/deepseek-v4-flash-0731`，max | 268→350 | `under_length_complete`；candidate、selected、delivery、final 均为 `0a6fdddf3a2cd87d39ace0ab69a7b83f7a404d2f4d5530ba87d770043348a0f2` | D1，`semantic_pass`，exit 0，0 retry，237.281 秒 |
| Claude Code | `ollama-cloud/deepseek-v4-flash:0731`，max | 268→344 | `under_length_complete`；candidate、selected、delivery、final 均为 `92b7c413a6eaddd19bcbd3bd2dc5f19ed043b3ad22045b38fd8da34c8125077c` | D1，`semantic_pass`，exit 0，0 retry，304.125 秒 |

另一名全新 `gpt-5.6-sol` max 裁判只读在线匿名包。输入 packet SHA-256 为 `55B7974590C477244C3E46D13743AEB7CAF366D26C46A5D54C8A7901EED67117`，rubric SHA-256 为 `91E209C3504EF6A9EE998149E60D8A5AE23B22EEA33FA5C8D20CE0E9F5D85E49`。裁决 `ACCEPT`：Codex 与 Claude 两份 D1 的事实、状态、篇幅、文种和直接使用均为 PASS；D0 仅因篇幅不足为 WARN。verdict SHA-256 为 `C14F741C5A26A7D4346D1A91CE75155141E4775EE2425EB6915FB7BB7A11B7F6`，receipt SHA-256 为 `2DAF5242C4BDB9BBA47E215A884CBF1BECB8018C7A139CCDD3F1C62E826DED2E`。

## 当前候选的最小工程门

- 真实运行后修复了常见入口表达：`只输出正文，350—450字`、`起草……，450—550字` 现在可识别；引用“材料正文 300—400 字”仍不会误作输出约束。
- 当前 `runtime.py` SHA-256 为 `A189A59EAA1704897D53FCA5DA623F88D4E4022E5C6E48496B97E68610DAAAE4`。
- 当前 HEAD 重新组装的 Codex、CodeBuddy、Claude Code companion 内 `runtime.py` 均与 canonical 同 hash；三包分别为 47、46、46 个文件，均记录 `installed=false`、`enabled=false`、`network_used=false`。
- `python -B -m unittest maintenance.tests.test_under_length_capability maintenance.tests.test_host_gate_adapter maintenance.tests.test_hook_layer_contract -q`：29/29 PASS。
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- `python -B -m py_compile chinese-official-writing/hooks/capabilities/under_length/runtime.py` 与 `git diff --check`：PASS。

## 边界和剩余风险

1. 本能力只处理低于明确下限的稿件，不包含超长压缩。
2. 目前已证明一份事实充分的采购请示能在两宿主形成可用 D1；稀疏材料仍可能安全回退 D0，这属于既定失败策略，不承诺每题都能补足。
3. CodeBuddy 2.136.0 的当前在线调用在模型前因登录失效返回 0 token；当前 HEAD 仅有自包含包和同 hash 迁移证据，恢复登录后补一份真实触发即可，不能把静态组装称为在线成功。
4. 透明归纳中新出现的中文计数词仍可能被机械门保守拒绝；现有结果不受影响，后续应以真实同稿样本决定是否放宽，不在本原子顺手扩规则。
5. 一次隔离 Codex 注册因 PowerShell `$HOME` 变量冲突误用了用户目录；注册和 marketplace 已由 Codex CLI 成功移除，但 `C:\Users\admin\plugins\cache\under-length-online-r5` 仍是未激活缓存残留。它不在仓库、不在当前插件注册表，也不影响本候选，但需通过受支持的缓存清理入口处理。

旧的 [`v164-under-length-three-host-live-result-20260814.md`](v164-under-length-three-host-live-result-20260814.md) 保留第一次真实生命周期只会回退 D0 时的 HOLD 事实；本文件记录其后的真实语义修复和复测，不回写旧运行结果。
