# Post-fix Hook enabled / disabled 真实写稿 A/B 结果

## 结论

`HOLD`。

固定行为根 `9c2ba63202dbc030bd768b9040cd95c4fc37c237` 的 18 次真实调用全部技术有效，但预注册 SOL 主裁判在两个独立 T3 配对中判定 Enabled 出现 Disabled 没有的状态边界失败：

- P003 / Alibaba：Enabled 把75件在办工单写成“将按计划推进办结”，并增加“确保各项工作按期完成”；材料只给7项问题的完成期限，没有给75件工单的办结计划。
- P009 / MiniMax：Enabled 增加“按规定程序继续推进”“按既定安排继续推进”“按工作计划持续推进”，并把75件在办工单纳入2026年后续推进；材料没有这些程序、计划或状态升级。

同一 `state` 硬维度在两个独立配对重复出现，满足预注册 HOLD 条件。SOL 还判定 P002、P009 存在重复 Enabled-only `facts` 失败；其中 P002 是审稿建议是否构成事实断言的口径争议，不作为本次 HOLD 的必要依据。

所有六个 Enabled 写稿臂最终都选择并原样发射 D0，没有 D1。上述差异因此不能归因于 Hook 改写；它们是 Enabled 样本关联的保守停线信号。预注册规则不允许在解盲后用“Hook 没改稿”豁免。

## 固定执行与隔离

- Claude Code 2.1.195，第三方 Anthropic-format gateway，Claude 登录状态 18/18 均为 `loggedIn=false`、`authMethod=none`。
- 9对、18次调用，9/9配对有效；Alibaba Token Plan 2、Ollama Cloud、MiniMax 各3/3；T1/T2/T3 各3/3。
- Alibaba 固定 `alibaba-token-plan-2/deepseek-v4-flash-0731`，未回退旧 `alibaba-token-plan`；三家均为 `max`。
- 每臂首个 terminal final，外层重试0，超时0。9/9配对题面哈希一致、规范化环境一致，命令只差 Enabled 的显式 `--plugin-dir`。
- Disabled Hook starts 为0。Enabled 共56次 Hook starts、15次 Stop starts、6次 Stop blocks。
- 冻结盲包 SHA-256：`572ac66d932b48c4460a9b7ca19e3be1689a358af996be4784ae50ac5a0ec2b2`。

## SOL 主裁判解盲

主票为 Enabled 1胜、Disabled 7胜、难分1。票数不替代硬停线。

| Pair | Provider | 题型 | 主胜方 | Enabled 硬失败 | Disabled 硬失败 | Enabled-only |
| --- | --- | --- | --- | --- | --- | --- |
| P001 | Token Plan 2 | T1 | Disabled | facts, length | facts | length |
| P002 | Token Plan 2 | T2 | Disabled | facts | — | facts |
| P003 | Token Plan 2 | T3 | Disabled | facts, length, state | facts, length | state |
| P004 | Ollama | T1 | Enabled | facts | facts | — |
| P005 | Ollama | T2 | Disabled | facts | facts | — |
| P006 | Ollama | T3 | 难分 | facts, length | facts, length | — |
| P007 | MiniMax | T1 | Disabled | facts | facts | — |
| P008 | MiniMax | T2 | Disabled | facts | facts | — |
| P009 | MiniMax | T3 | Disabled | facts, state | length | facts, state |

SOL 对多份 T1 的事实判定包含一处明确误读：裁判称“运维人员为恢复主体”属于新增事实，但题面已明确“运维人员于9时20分恢复接口访问”。该项判定原样保留，不用于 HOLD 归因。Kimi、Grok 对 T1 更宽松，也说明事实扩写尺度存在裁判分歧。

## 补充裁判

- Kimi K3 / max：技术有效，Enabled 2胜、Disabled 5胜、难分2。
- Grok4.5 / max：技术有效，Enabled 2胜、Disabled 5胜、难分2。
- Qwen3.8-max / max：经 `alibaba-token-plan-2` 的精确模型路径预检成功，但正式裁判调用在1200秒超时，记 `INVALID`，外层重试0，不补跑、无终稿。

补充裁判对 P003、P009 的事实和状态严重程度并不完全一致：Grok支持部分 Enabled-only 事实失败，Kimi更宽松。该分歧保留；补充票不得覆盖预注册 SOL 主裁判的重复硬停线。

## T2 纯审稿 bypass

三个 Enabled T2 臂均观测到插件和 adapter turn，但全部为：

- gate transaction 0；
- Stop block 0；
- 没有 D0/D1 替换；
- 最终交付保持“问题位置—风险层级—修改建议”的审稿模式，没有重写全文。

因此 review-only bypass 在三家 provider 上真实生效，Hook 没有与 Skill 的“只审不改”路由打架。审稿内容本身仍有质量差异：多份意见在指出材料外安装、验收和效果承诺后，又建议了未经确认的采购或验收流程；这是模型审稿质量问题，不是 Hook 篡改。

## T1、T3、D0/D1 与篇幅

六个 Enabled 写稿臂全部 `TERMINAL_D0 / no_review_candidate`，D0 6、D1 0，final 与 D0 及 state output hash 全部一致。

| Provider | T1 Disabled / Enabled | T3 Disabled / Enabled |
| --- | --- | --- |
| Token Plan 2 | 192 / 132 | 383 / 483 |
| Ollama | 180 / 181 | 363 / 372 |
| MiniMax | 195 / 201 | 733 / 882 |

- T1 要求180—260字；只有 Token Plan 2 Enabled 的132字不达标，而同对 Disabled 192字达标。这是一次 Enabled-only length 失败，未在第二个配对重复。
- T3 要求800—1000字；只有 MiniMax Enabled 的882字达标，其余5稿均不足。三个 Enabled 样本都比同对 Disabled 更长、更接近下限，但 Hook 全部选择D0，不能把这种样本差异称为 Hook 质量收益。
- 没有真实 D1，故 length-nonworsening 的 D1 约束没有被本矩阵实际触发；只能确认 Hook 没有把 D0 变短或改坏。独立“篇幅门禁”仍未增加，本轮也没有混入该功能。

## 三层是否打架、Hook 是否过严

三层职责没有形成自动冲突：

1. Skill/reference 负责写稿或纯审稿语义路由。
2. `prose_lint.py` 对12份 T1/T3 final 以 draft-body + format + structure 扫描，只报1个 low `empty-filler`：P009 Enabled 的“按工作计划持续推进相关工作”。
3. Hook 不接收 lint 结果；`review_gate.py` 在同稿中判 `no_review_candidate` 并保留 D0。

这是一处覆盖范围分歧，不是脚本互相调用或循环改写：lint 是只读建议，Hook 的 D0 回退保持安全。但它也证明 Hook 不能代替 lint、事实核对、文种审查或篇幅门禁。

Hook 的内容处理没有过严到破坏终稿：六个写稿臂均原样保留 D0，T2 全部直接放行。交互路径仍偏重：六个写稿臂在无候选、无D1时各发生一次 Stop block，只为发射未改的D0。这是可复现的额外轮次和延迟，应视为流程过触发，不能宣传为质量收益。

同时，Hook 对外扩风险的覆盖并不完整。P003、P009 的材料外计划和状态升级进入 D0 后都未被 locator 命中；D0 fallback 防止了有害修复，却没有兜住这些初稿外扩。Hook 应描述为窄域、有界的末端保护，不是全面兜底。

## 证据与边界

- 预注册提交：`887c2cdf542679eb8cf73c3a90c7e1691d50ad3b`。
- 18臂 raw、盲包、事务和技术封包提交：`6aa107d91ec8f62998448fc3daf20661ce89ca36`。
- SOL/Kimi/Grok 原始裁判、Qwen 超时回执和裁判哈希提交：`ec09a3e59ff19c0d5aaf1dbb7442c6280ee5fbf9`。
- 原始大证据与本简洁结果分离；最终集成无需带入 raw 提交。
- 未修改产品包、host 配置、篇幅门禁或后续 packaging；未发布、未合并 main。

本轮支持的结论是：纯审稿 bypass 有效、D0 回退未破坏正文、三层没有自动互相改写；但所有写稿臂均为D0、无D1质量证据，存在固定额外 Stop，且对初稿外扩和篇幅不足覆盖有限。按预注册硬规则保持 `HOLD`。
