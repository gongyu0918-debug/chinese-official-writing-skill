# HK-004 DeepSeek Harness adapter R1 预登记

## 固定基线与范围

- 基线：本地 `main` 提交 `3c363257fee2e823f96253682331ef4ec5128fb7`。
- 宿主：DeepSeek Harness `0.1.1-rc.2`；默认能力 `delivery_review`。
- 只研究并实现 DSH 原生薄适配、静态 Profile Bundle、OpenCodex 精确模型配置、组装和直接相关测试；不改普通写稿规则，不合并 `main`，不推送、不发布。
- 2026-08-27 用户将原“Qoder CLI + DSH”范围收窄为只做 DSH。Qoder 本轮状态为 `DEFERRED_BY_USER / NO_REPOSITORY_CANDIDATE`，不继续实现或测试。

## 原子与通过条件

1. 先实测官方 `@deepseek-ai/dsh-hooks-claude-code` bridge；Stop 不能提供当前完整 D0 时，不把协议名称相似当成可用。
2. 只有当前 open turn 的 `agent/turn-stopping` 能取得同 turn 最后 assistant message，才实现原生 Cordis plugin；按 turn 重建 Stop 次序，阻断只用 `agent.steer()` 续写。
3. 在全新隔离 `DSH_HOME` 中完成 `assemble → dsh plugin add → dump-config → 当前 Skill 真稿`，会话保持宿主默认压缩格式，不依赖原始 JSONL 取稿。
4. 模型必须由 OpenCodex 的 DSH 导出面提供。显式 `max` 只在导出模型声明该档位时配置；没有 `reasoningEfforts` 的模型只记录 provider 默认，不伪称 `max`。
5. 产品通过：至少一份当前 Skill 真稿完成 D0→Stop→终态，最终 stdout hash 与选择稿一致；事实、状态、合理推断、正文交付无硬回退。
6. 工程通过：确定性 smoke 覆盖多 Stop、同名外部 Skill、换回合脱敏；组装包只有一个 DSH manifest，无父目录回指、失效链接或密钥。

## 失败与回退

- 模型或宿主技术失败单独记录，不能冒充质量结果。
- adapter/core 不可用、回合变化或 Stop 超限时，精确中止并优先回退原始 D0；无法保证当前稿与 D0 一致时不得宣称安全闭环。
- 只验证 headless 时不得外推 TUI/Web；只在线验证 `delivery_review` 时，其他 capability 只可标静态可组装。
