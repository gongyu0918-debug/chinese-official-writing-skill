# DeepSeek Harness 官方协议与配置研究

## 官方边界

- 官方仓库：<https://github.com/deepseek-ai/deepseek-harness>；本轮浅克隆固定 `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`。
- 官方生命周期说明：<https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/agent-lifecycle.md>。`agent/turn-stopping` 在 turn 关闭前串行执行；listener 可用 `agent.steer()` 让同一 turn 再执行一步。
- 官方 CLI/Profile Bundle 说明：<https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/cli/reference/README.md>。带 `dsh.bundle.patch` 的本地包可由 `dsh plugin --profile <name> add <path>` 加入 profile，重启后进入配置层。
- 官方 Claude Code bridge `@deepseek-ai/dsh-hooks-claude-code@0.1.1-rc.2` 为 MIT；其 README 明确 Stop 省略 `last_assistant_message`、恒报 `stop_hook_active:false`，也没有连续阻断上限：<https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/hooks/hooks-claude-code/README.md>。

因此官方 bridge 能证明阻断→steer 的宿主语义，但不能把本门禁需要的完整 D0 传给共享核心。原生 plugin 在同一 `agent/turn-stopping` 时读取 `agent.session.events`，实际观察到当前 turn 的非中断 `assistant/message` 已存在，故无需改 DSH、无需读取磁盘会话，也无需复制官方 bridge。

## OpenCodex 精确配置

- `opencodex 2.32.0` 的 `help export` 把 `dsh` 列为原生 client；`opencodex export --client dsh --out <new-file>` 生成 DSH `llm-pi-ai` provider，使用回环 `http://127.0.0.1:10100/v1` 和非秘密 bearer 占位。
- 本轮导出27个模型。`alibaba-token-plan-2/deepseek-v4-flash-0731` 行未声明 `reasoningEfforts`，因此只精确选择 provider/model，实际 request header 无 effort，不写成 `max`。
- `opencode-go/deepseek-v4-flash` 行明确声明 `low/high/max`；在 `agent-default-model` 中选择该 model 并写 `reasoningEffort: max` 后，实际压缩 session 的 `request/header` 为：`{"provider":"opencodex","model":"opencode-go/deepseek-v4-flash","reasoningEffort":"max"}`。
- 两个 session 都有 `skill` 工具调用 `{"name":"chinese-official-writing"}`；adapter 又核对 tool result 的 `resourceBase` 等于 companion 内 Skill，避免同名外部 Skill 误启动门禁。

## 方案选择

最终 companion 是无第三方运行依赖的本地 DSH Profile Bundle：根 `package.json` 声明 `dsh.bundle.patch`，`cordis.patch.yml` 插入一条原生 plugin，`index.mjs` 只做事件映射、Python core 调用、turn/Stop 绑定、hash 回执和故障 D0 回退。普通 Skill 安装不启用；组装器不安装或修改 profile。
