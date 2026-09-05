# 硬停适配范围与直接协议验证

本页只记录 `continue:false` 的适配器边界；同稿 core 原型与原生宿主运行分别验收。基线为 `3532afd6619ac6256558e9552b92d03da5ae9c0f`。未修改付费/Pro、宿主安装或系统设置，未由本项启动模型。

## 本次实现

- Codex：`hooks/adapters/host_gate_adapter.py` 的 `host == "codex"` 分支优先保留 `continue:false`、`stopReason`、`systemMessage`，不会把同包中的 `decision:block` 再发成续写指令。
- Claude 与 ZCode：两者实际由组装器共用 `hooks/adapters/claude-code/gate_stop_hook.py`，同样优先保留硬停。ZCode 不使用 `host_gate_adapter.py`。
- Qwen：`hooks/adapters/qwen-code/gate_stop_hook.py` 增加相同归一化。[官方 Stop 文档](https://qwenlm.github.io/qwen-code-docs/en/users/features/hooks/#stop)明确给出 `continue:false` 与 `stopReason`；原 0.22.3 正文重复风险继续独立保留，不据协议透传宣称该版本原生交付通过。
- 只传允许的停止字段；故障消息为空或类型不合法时保留固定停止说明。普通 `decision:block` 和 allow 保持，未新增续写预算或恢复循环。

实际运行：

```text
python -B -m unittest maintenance.tests.test_host_gate_adapter.HostGateAdapterTests.test_codex_hard_stop_precedes_continuation_and_keeps_failure_message maintenance.tests.test_claude_gate_adapter.ClaudeGateAdapterTests.test_hard_stop_precedes_continuation_and_keeps_failure_message maintenance.tests.test_zcode_gate_adapter.ZCodeGateAdapterTests.test_hard_stop_precedes_continuation_and_keeps_failure_message
python -B -m unittest maintenance.tests.test_host_gate_adapter maintenance.tests.test_claude_gate_adapter maintenance.tests.test_zcode_gate_adapter
python -B -m unittest maintenance.tests.test_qwen_gate_adapter
```

首组三项通过（1.692秒）；相关三套29项通过（30.099秒）；Qwen四项通过（0.977秒）。反控涵盖硬停优先于续写、故障消息保留、非协议字段剔除、无有效消息时仍停止，以及原有正常 block/allow。均为直接协议/组装测试，不是原生宿主停止证明。

## 尚未修复的宿主面

以下位置按基线记行号；本轮没有为未知协议猜测新的终止字段。

| 宿主 | 当前代码位置与剩余行为 | 最窄后续验证 |
| --- | --- | --- |
| CodeBuddy | `host_gate_adapter.py:292–300,354–355` 只把 `decision:block` 转为 `continue:false` 并 exit2，表示续写阻断；core 单独硬停仍会进入 allow，未修复。 | 用实际已选稿核对 exit0 的停止字段是否被原生 CLI 识别。仅向 stderr 写警告不能证明用户看见失败，故没有把诊断日志包装成修复。 |
| Kimi | `kimi-code/gate_stop_hook.py:405–416` 只映射 permission deny，core 单独硬停仍变成 allow。 | [官方文档](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/hooks.html)只说明 Stop 阻断可让模型继续；需确认独立终止 API。旧单 Stop 和 0.39.1 不安全边界不变。 |
| OpenCode | `opencode/opencode_gate_plugin.js:498–506` 将非 block 当终态 allow；`508–515` 达宿主上限只停止插件续写，不能撤回已有消息。 | 先证明同步取消/终态失败的原生控制点；异步 idle 和已有 1.18.25 生命周期失败不能靠换字段解决。 |
| DeepSeek Harness | `deepseek-harness/index.mjs:134–138` 把非 block 当 allow；`339–349` 的 D0 fallback mismatch 也只记回执后退出。 | 已安装 0.1.1-rc.2 的 `@deepseek-ai/dsh-agent/lib/types/runtime-types.d.ts:74–80` 提供 `Agent.cancel(cause, options)`，但须做同稿原生取消原型；本次未新增该能力。 |

DSH [官方 Claude bridge 说明](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/hooks/hooks-claude-code/README.md)明确表示 `continue:false` 只被记录而不会终止运行。该 bridge 与本仓库原生 DSH adapter 是两条实现，不能混用其能力声明。Hermes 使用同步 transform，未经过共享多 Stop 回显链；OpenClaw 无 Hook。

## 原型与可见输出边界

临时原型已逐字复制到本轮 `output/hook-four-fixes-r1/echo-prototype/`，保留原运行绝对路径，不覆盖原证据。真实 MiniMax SHORT D0 的正文 hash 为 `b10b3b51d19fb1fdb13cce686c40c23afea0031e9e12996dd62e20781ad1d424`；故障输入是同题另一份已存真实稿，属于事件注入，不能说模型自然连续错回显。

两臂各三条 core 路径显示：正常精确回显、错一次后精确回显保持原结果；连续错至预算耗尽及其 Stop 重放，基线 allow 且未验证，原型硬停且未验证，均完成脱敏。该试验没有原生宿主和模型调用。

已保存的 Claude 2.1.251 原生正常链中，assistant 正文和中间修订 JSON 先于后续 Stop 出现在 stream。因此停止 API 只能阻止继续运行或成功认证，不能撤回已经显示的错误文本。新原生证据必须同时核对实际 assistant、Stop 载荷、返回、后续模型调用数、result/用户可见终态和选定稿 hash；仅 core 返回 false 或 CLI exit0 不足以证明错误稿未交付。
