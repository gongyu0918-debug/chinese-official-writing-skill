# HK-005b 剩余宿主边界

基线 `37f22146f64cf2dfcaea7a8a5afba40750215803`，工作分支 `codex/remaining-hook-quality-r1`。本项没有模型调用、原生 CLI profile 调用或平台操作。产品仅改 DSH、OpenCode 两个 adapter；四宿主 README 与 `host-capabilities.json` 补齐支持边界，CodeBuddy/Kimi 代码保持原样。由根代理统一提交。

## 两臂与实际结果

先从基线 Git archive 冻结 canonical，再用历史真实稿复放 core：MiniMax D0 的 SHA-256 为 `b10b3b51d19fb1fdb13cce686c40c23afea0031e9e12996dd62e20781ad1d424`；错误回显来自同题另一份真实 Alibaba 稿，SHA-256 为 `3e4b869f35d3f8643500a82bc6b2399dd21e47b9164ff5fbb03daf6dca3623e4`。这是人工事件注入，不是新观察到的模型自然错回显。来源沿用前轮 `hook-four-fixes-r1/echo-prototype`，原始模型来源可追溯到仓内 `maintenance/tests/evidence/hook-audit-quality-r1/frozen-evidence.json`。

`core-replay-events.json` 保存每次真实 Python core 调用、完整事件、响应和终态记录；连续错回显达到预算后及再次 Stop 均为 `continue:false`、`delivery_verified:false`、`raw_turn_data_redacted`。`hard-stop.json` 是后续协议复放的固定输入。

| 宿主 | 基线 | 最小候选 | 可成立的结论 |
| --- | --- | --- | --- |
| CodeBuddy | `_host_response('workbuddy', hard_stop)` → `continue:true` | 代码未改，仍放行 | **UNSUPPORTED**；公开命令 Stop 没有已核实的独立硬停字段。正确调用的两臂及正常 block 反控见 `codebuddy-corrected-mapping.json`。 |
| Kimi | `_host_response(hard_stop)` → `{}`，即静默 allow | 代码未改，仍放行 | **UNSUPPORTED**；公开命令 Hook 只提供 allow/block，Stop block 用来请求续写。 |
| DSH | 真实 packaged adapter 把 false 写成 allow；本机 AgentLoop 最终 `completed` | false 优先分类 halt，`agent.cancel({kind:'hook',reason},{keepInbox:true})`；本机 AgentLoop 最终 `aborted`，保留 Hook 原因 | **SDK_LIFECYCLE_VERIFIED_WITH_MOCK_ADAPTER**；不是当前原生 CLI/模型证明。 |
| OpenCode | false 写成 `shared gate reached a terminal allow` | 不再请求续写，error 日志标明 halt/未验证，并请求 TUI 错误提示；终态重放仍失败 | **PROTOCOL_VERIFIED_PLUGIN_STOP_ONLY**；在 idle 后介入，不调用 `session.abort`，不能撤回已显示正文，也不把新用户回合中断。 |

DSH 对照使用本机已安装 `@deepseek-ai/dsh@0.1.1-rc.2` 的真实 Cordis、SessionStore、AgentRegistry、AgentLoop。只有 LLM Adapter 与 Skill registry 是固定夹具；未加载 profile、凭证、外部工具或网络模型。基线和候选各消费一次历史正文，没有第二请求。`sdk-baseline-r2/result.json` 对照 `sdk-candidate-r2/result.json` 证明最小取消原型；产品版本复验见 `sdk-product-candidate/result.json`，最终加入 `keepInbox:true` 和迟到结果保护的版本见 `sdk-final-candidate/result.json`、完整 `session-events.json` 与 `final-command-2.json`。

最终 SDK 相邻反控还在停止边界排入一个独立用户请求：当前 turn 以 aborted 结束，队列中的原请求完整保留，MockAdapter 请求数仍为 1。直接测试另验证旧 turn 的迟到 core 失败不能取消已开始的新 turn。DSH 的 D0 故障回退若再次错回显，也改为取消；精确 D0 回显仍保留原来的有限结束路径，未将该回退重命名为核验通过。

## 运行记录

```text
python -X utf8 -B output/remaining-hook-quality-r1/hosts/replay_core.py
python -X utf8 -B output/remaining-hook-quality-r1/hosts/run_protocol_probe.py baseline
python -X utf8 -B output/remaining-hook-quality-r1/hosts/run_protocol_probe.py candidate
node output/remaining-hook-quality-r1/hosts/dsh_sdk_probe.mjs <companion> <new-output> output/remaining-hook-quality-r1/hosts/d0.txt [queue]
python -X utf8 -B -m unittest maintenance.tests.test_deepseek_harness_gate_adapter maintenance.tests.test_opencode_gate_adapter
git diff --check
```

两个宿主合计 **16/16** 直接测试通过，18.901 秒；精确解释器/argv/stdout/stderr 见 `final-command-1.json`。范围包括正常 block/allow、false 优先于 block、无效消息兜底、提交阶段硬停、回退错稿/精确稿、迟到回合保护，以及 OpenCode 终态失败重放、提示不可用和既有正常续写/重载反控。SDK 最终命令与 diff 检查见 `final-command-2.json`、`final-command-3.json`。README/能力描述更新后的补充定向验证见 `documentation-followup.json`。不把测试数量换算成真实成稿无错率。

## 保留的无效与失败记录

- `sdk-baseline/` 是首次驱动技术无效输出：创建 Session 时漏传 cwd，core 进程没有正常进入；清理又调用了该版本不存在的 `ctx.stop()`，exit 1。该次 completed 结果**不得计作基线**。驱动改为固定绝对数据路径、`create(...,{cwd})` 和 `ctx.fiber.dispose()` 后使用新目录 `sdk-baseline-r2` 重跑。没有覆盖首次输出。检查默认 `.dsh` 下未生成该测试回执。
- 首次 `replay_core.py` 把 repo 根解析多上一层，`git archive` exit 128，尚未创建冻结目录或调用 core；纠正根目录后才形成有效复放。
- 初版 `protocol-baseline/result.json` 和 `protocol-candidate/result.json` 中仅 CodeBuddy 行把 `_host_response` 参数顺序反了，**这两行无效**。`codebuddy-corrected-mapping.json` 用已核实的 `(host, value)` 顺序补证，确认两臂仍为 allow；其他宿主行不受该驱动错误影响。

## 未完成

CodeBuddy/Kimi 的独立硬停仍未实现；以 exit2、deny 或再发一句“停止”会请求模型续写，不能冒充修复。当前可用范围仍是普通 Skill 与人工终稿核对。OpenCode 的错误提示仅直接协议测试，未声称原生 UI 已显示；原有 1.18.25 生命周期失败仍保留。DSH 没有在当前原生 headless/TUI/Web 重跑新的失败终态，历史在线正常闭环不迁移成当前原生取消证明。四宿主都不能凭 Stop 撤回已显示文字。

取消清理的关联范围：Kimi 最新官方 `Interrupt` 是观察事件，当前 companion 尚未注册；DSH 此前只在 disposed/新 turn 做 core HostAbort；OpenCode 本项不增加异步 session.abort。实际中断清理由本轮 HK-008 独立验收，不能用本项停止分类代替。
