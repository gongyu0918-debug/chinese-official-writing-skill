# HK-004 Qoder CLI / DeepSeek Harness adapter R1 预登记

## 固定基线与范围

- 基线：本地 `main` 提交 `3c363257fee2e823f96253682331ef4ec5128fb7`。
- 宿主：Qoder CLI `1.1.32`、DeepSeek Harness `0.1.1-rc.2`。
- 只研究并实现宿主薄适配、静态 companion、组装和直接相关测试；不改写普通写稿规则，不发布、不推送。
- 默认能力为 `delivery_review`。真实写稿优先使用 OpenCodex 的 `alibaba-token-plan-2/deepseek-v4-flash-0731`；模型或登录不可用的宿主不得用模拟事件冒充在线写稿。

## Qoder 原子

1. 用官方插件目录和 `hooks.json` 验证 `UserPromptSubmit`、`PostToolUse`、`Stop` 实际载荷、插件根和数据根。
2. 同一回合必须把完整 D0 交给共享门禁；阻断时由宿主继续一次，后续 Stop 重新核对；失败逐字保留 D0。
3. 以稀疏采购申请真实写稿验证 Skill 触发、正文交付、事实/状态锚、Stop 回执和可见终稿 hash。若账号未登录，只能登记已实测的装载/事件边界，不得标成完整在线闭环。

## DSH 原子

1. 先实测官方 `@deepseek-ai/dsh-hooks-claude-code` bridge。官方 bridge 若不能向 Stop 提供当前 D0，不把协议名相似当成产品可用。
2. 仅当 DSH 当前开放的 `agent/turn-stopping` 能从同一 agent、同一 open turn 取得最后 assistant message，才制作原生薄 adapter；adapter 最多 steering 一次，并重建 continuation Stop 位置。
3. 在隔离 `DSH_HOME` 的 headless profile 中用当前 Skill 跑稀疏采购申请；检查 Skill 被真实加载、D0/D1 或 KEEP、共享硬锚、终态脱敏和最终 stdout 一致性。

## 通过、回退与终止

- 产品通过：至少一个当前 Skill 真稿在对应宿主完成完整写后生命周期，目标风险得到改善或安全 KEEP，且无事实、状态、文种、长度或正文交付硬回退。
- 工程通过：官方装载/校验成功；确定性测试覆盖字段缺失、重复 Stop、跨回合、错误输出和 D0 回退；组装包无额外宿主 manifest、无失效链接、无密钥。
- 宿主认证、当前协议或模型技术失败单独记录。不能取得完整 D0、不能绑定当前回合或不能安全回显时终止完整 adapter，不以 `HOLD` 代替结论；仍可保留有明确用途的静态/部分兼容结论。
