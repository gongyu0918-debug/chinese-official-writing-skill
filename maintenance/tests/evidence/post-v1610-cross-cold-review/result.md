# v1.6.10 后多范围三路冷审结果

## 绑定

- 冻结范围：`v1.6.10..3084ee56`、`3084ee56..b0e72a26`、`b0e72a26..c3477de3`、`3084ee56..740154b3`。
- packet SHA-256：`fc4cda2cb0e3a7be0dca3e78b39c24c5ab2c9ab561c95f986b012adc20a85489`。
- Qwen：`alibaba-token-plan-2/qwen3.8-max`，`ultra`，780.125秒，0 retry，JSON 有效；final SHA-256 `3373c97090d7202f7afb4eb3fd53d4c094a665112c66abebf4353cef47542840`。
- Grok：`xai/grok-4.6`，`ultra`，463.015秒，0 retry，JSON 有效；final SHA-256 `e307a3c89957c99ce4f64d39e6998782a517df371ba3e99aa29e7038aff80156`。
- Kimi：`ollama-cloud/kimi-k3`，`ultra`，26.265秒后返回 `402 Payment Required`，未形成 final，记 `INVALID_PROVIDER_BALANCE`，未补跑、未改用其他 Kimi 路由。

两份有效审查均绑定同一 packet hash；原始流、stderr、packet、freeze 与 manifest 保存在 ignored 的 `output/post-v1610-cross-cold-review/formal-r1/`。

## 交叉复现与处理

1. Qwen 的 P1 成立：旧回指豁免按前一字符跳过所有汉字数量，`会后三天→两天`、`前三项→五项`均逃过机械门。当前修复只跳过`前一项/后一项/上一项/下一项`。
2. Grok 的两个 P2 成立：`一方面/另一方面`被误记为业务数量；`第N项`被抽成`N项`，可能错误进入“方面→项”透明归纳。当前修复忽略修辞性`一方面`，并把`第N项`保留为序号硬锚。
3. Qwen 指出的证据时序冲突成立：106字同稿的192字样本发生在透明归纳放宽前，190字样本发生在放宽后。历史证据不改原结果，只追加先后与取代关系；coverage 同时保留两阶段事实。
4. 两家共同确认 `UL-005` 仍是准入阻断。透明数量归纳也依赖当前语义 verifier，必须纳入来源绑定或异模型 verifier 的固定坏稿/好稿复测，不能只记录付费组合 R8。

## 付费叠加层仍需处理

- `OT-001` 当前是 Agent 输出进入会话后的语义冻结与一次删减式 Stop 核对，不是结构化章节清单/hash 的机械核验；规格与 coverage 需使用这一真实口径，结构冲突、重复章节、缺项和材料覆盖属于 `OT-002`。
- Claude companion 的 `hooks.json` 仍使用 Windows `py -3`。Claude 官方现支持跨平台 exec form 的 `command + args`；切换前需在付费分支做 Windows 在线 smoke，并保留 macOS/Linux 未实跑边界。
- 组合包只有修改型 Stop 被单 coordinator 接管；`UserPromptSubmit` 与 `PostToolUse:Agent` 的两个独立 command handler 仍可能并发，但当前分别只做提纲上下文与交付状态记录。文档不得把它描述为所有事件均严格串行。
- Codex 与 WorkBuddy / CodeBuddy 的组合生命周期仍未运行；R8/UL-005 未闭环前不开放入口。
- Codex 与 WorkBuddy / CodeBuddy 历史样本记录了相同终稿 hash，但没有归档两份可独立绑定的原始 transcript；当前只能保留为证据来源限制，不能据此反推产品故障。

## 准入结论

- 本轮共享硬锚窄修复可进入候选；不改变篇幅语义 verifier 的类别和放行规则。
- 付费组合、提纲结构化修正与 `UL-005` 继续 HOLD；本轮不合入 `main`、不合入付费分支、不发布。

## 实际验证

- `test_shared_hard_anchors + test_under_length_capability + test_over_length_capability + test_hook_layer_contract + test_repository_reachability`：53/53 PASS。
- under/over 直接生命周期反控：`会后三天→会后两天`两路均以 quantity 原因回退；修辞性`一方面/另一方面`可安全压缩；新增`第二项`不得借“两方面”进入透明归纳，`DIRECT_LIFECYCLE_OK`。
- Skill Creator `quick_validate.py chinese-official-writing`：`Skill is valid!`。
- 三份 tracked 冷审 JSON 可解析；`git diff --check` PASS。
- ignored manifest SHA-256：`ca158744120a1fb2d8b582698ea24984a5a02a12ef2e8f0beebd50b62d2a482f`。
