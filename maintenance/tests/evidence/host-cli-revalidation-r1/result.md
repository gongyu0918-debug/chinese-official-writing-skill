# HK-004 CLI 宿主复测与当前短稿结论

日期：2026-08-29—30。固定基线：`main@7b59ee0e650ea65c25c2f3246dfc4c422c264e15`。本轮只在独立 worktree 和隔离 profile 中测试，不控制 GUI，不修改宿主本体，不发布、不推送。普通写稿只用已登记的低成本模型；高成本模型只在独立 Codex Desktop 任务中盲审 Hook 与证据，不参与写稿。

## 结论

1. 已逐一运行本机当前有 CLI 的十个入口：Claude Code、Codex、CodeBuddy、ZCode、Qwen Code、Kimi Code CLI、OpenCode、Hermes Agent、DeepSeek Harness 和 OpenClaw。QwenWork 没有公开 CLI/headless/API，不用 Qwen Code 冒充。
2. 同一无字数限制采购申请 `S1` 的十份实际正文内容均形成现状/缘由、拟采购事项、未决字段、请求落点和一层合理作用，没有出现功能性过薄。Kimi、Qwen、OpenCode、OpenClaw 的失败发生在事实安全、Hook 生命周期或直接交付形态，不是篇幅不足。
3. 明确 240—300 字的 `S2` 在 Claude Code、Codex、ZCode、DeepSeek Harness 四种当前 companion 宿主得到范围内、事实状态可接受且直接可用的终稿；CodeBuddy 2.141.0 的真实 profile 另完成一次 Stop、长度和终态脱敏，但 reference 读取被拒、终稿含单 provider 的“预定时间”软性无依据措辞，不能并入无条件质量 PASS；Qwen Code 关闭 Hook 时另得到一份245字符的干净终稿。当前短稿状态仍收口为 `NO_COMMON_SHORT_REGRESSION / WAIT_NEW_COUNTEREXAMPLE`，不增加统一最短字数门，也不改普通写稿 reference。
4. 最新宿主兼容性不是全绿：Qwen Code 0.22.3 的多 Stop headless 会把阻断前正文与续写正文同时聚合到最终输出；Kimi Code 0.39.1 出现材料外职责/程序并停在 D0；OpenCode 1.18.25 停在 `awaiting_repair` 且保留原始事务；OpenClaw 只证明 Skill 内容生成，最终输出仍混入大量推理。它们分别记精确失败，不写成 `HOLD`，也不把旧版本成功外推到新版本。
5. 预登记的 `N1/U1/M1/L1` 又各用两家低成本 provider 完成有效真稿：活动新闻和未决情况说明完整保留日期、人数层级与未决状态；会议纪要守住纠正后的决定、无人承接提议和暂定日期；两份长报告的正文去空白计数分别为1948、2123，进入1800—2400合同。没有出现跨 provider 的共同目标失败，因此不启动互联网校准后的新产品规则。

## 当前 CLI 宿主结果

| CLI | 实测版本 | S1 写稿 | Hook / 交付结果 | 当前状态 |
| --- | --- | --- | --- | --- |
| Claude Code | 2.1.251 | 完整、不薄 | `delivery_review` 完整 Stop、终态 hash 与脱敏 | `CURRENT_CLI_PASS` |
| Codex | 0.151.0 | 完整、不薄 | S1 `delivery_review`、S2 `under_length` 均闭合；S2 `delivery_verified=true` | `CURRENT_CLI_PASS` |
| CodeBuddy | S1：内置2.115.0；S2：2.141.0 | 两份均不薄；2.141.0 的必要 reference 读取被宿主拒绝 | 2.141.0 真实 profile 完成 S2 一次 Stop、精确终稿与终态脱敏；stdout 显示原生 `copilot.tencent.com` 路线，OpenCodex provider 注入未被证明；终稿另有单 provider 的“预定时间”软性无依据措辞风险 | `CURRENT_REAL_PROFILE_LIFECYCLE_PASS / REFERENCE_READ_DENIED / PROVIDER_INJECTION_UNVERIFIED` |
| ZCode | wrapper 3.10.1-17 / runtime 0.16.5 | 完整、不薄 | 当前 Stop、终态与脱敏闭合 | `CURRENT_CLI_PASS` |
| Qwen Code | 0.22.3 | 正文内容完整、不薄 | 开 Hook 时同一正文重复；JSON 输出模式仍重复；无 Hook 消融为单一干净正文 | `SKILL_PASS / HOOK_DIRECT_OUTPUT_INCOMPATIBLE` |
| Kimi Code CLI | 0.39.1 | 不薄，但 D0 已新增一般性收文主体、职责、程序和签发语 | 当前 adapter 未形成安全终稿，选择 D0 只说明没有选更差修订，不代表 D0 可用；原始事务未清理 | `CURRENT_HOOK_UNSAFE / VERSION_DOWNGRADED` |
| OpenCode | 1.18.25 | D0完整、不薄、事实状态可接受 | 1.18.25 不继承已发布1.18.23成功；生命周期停在 `awaiting_repair`，repair JSON 可见，原始事务保留 | `SKILL_PASS / CURRENT_LIFECYCLE_INCOMPATIBLE` |
| Hermes Agent | 0.20.6 | 完整、不薄 | 已声明的新建不可恢复 query 范围内同步 KEEP、hash 闭合 | `CURRENT_CLI_PASS_WITH_EXISTING_SCOPE` |
| DeepSeek Harness | 0.1.1-rc.2 | 完整、不薄 | headless 原生 Stop、终稿 hash 与脱敏闭合 | `CURRENT_CLI_PASS_WITH_EXISTING_SCOPE` |
| OpenClaw | 2026.7.1-2 | 正文内容完整、不薄 | 无 Hook；直接输出混入推理和改稿过程 | `SKILL_CONTENT_PASS / DIRECT_BODY_FAIL / NO_HOOK` |

QwenWork 继续为 `STATIC_SKILL_PACKAGE_PASSED / ONLINE_LIFECYCLE_UNVERIFIED`；没有 CLI 就不进入本轮在线矩阵。

## S2 明确下限题

计数采用独立标题之外的正文去空白字符数；括号内为同一正文的 CJK 统一汉字数，只用于复核计数口径，不把汉字数冒充用户合同。完整可见输出若含独立标题，会比表中正文计数更长。

| 宿主 | 低成本模型 | 终稿计数 | 判定 |
| --- | --- | ---: | --- |
| Claude Code 2.1.251 | Alibaba Token Plan 2 DeepSeek V4 Flash，max | 289（241） | PASS |
| Codex 0.151.0 | OpenCode Go DeepSeek V4 Flash，max | 294（249） | PASS；Stop 1，终态脱敏 |
| CodeBuddy 2.141.0 | CodeBuddy 原生 DeepSeek V4 Flash，max | 293（248） | 真实 profile 生命周期/长度 PASS；Stop 1，终态脱敏；reference 读取被拒、OpenCodex注入未证明、“预定时间”属单 provider 软性措辞风险，不计无条件质量 PASS |
| ZCode 3.10.1-17 | OpenCode Go DeepSeek V4 Flash | 286（241） | PASS |
| DeepSeek Harness 0.1.1-rc.2 | MiniMax M3，max | 248（208） | PASS |
| Qwen Code 0.22.3，无 Hook 消融 | Ollama DeepSeek V4 Flash 0731 | 245（205） | 写稿 PASS；证明重复来自 Hook/宿主交互 |
| Qwen Code 0.22.3，开 Hook | 同上 | 520；正文约507且标题两次 | 直接交付 FAIL；不是短稿失败 |

旧内置 CodeBuddy 2.115.0 同题另得269（225）字符，用于观察版本迁移，不重复计为第六种宿主。

## Qwen 0.22.3 消融与官方协议

- 同模型、同提示、同 Skill，关闭 Hook 时只输出一份245字符正文；开启当前 companion 后，`stream-json` 与 `json` 两种模式都把正文重复聚合。故障可归因于 Hook/宿主交互，不是当前写稿 reference。
- Qwen 官方 Hook 文档说明 Stop 提供 `last_assistant_message`、`stop_hook_active` 和阻断反馈；`MessageDisplay` 在 TUI、headless 与 ACP 使用同一 payload，但属于 fire-and-forget，输出和退出码均被忽略。当前公开面没有能够替换或抑制已经输出的早期 assistant message 的安全控制点。
- 因此不制作“看似支持、实际只观察”的伪 adapter，也不修改 Qwen 宿主。0.22.0 的历史成功仍保留为历史证据；0.22.3 只推荐普通 Skill，完整多 Stop companion 降级为不兼容。

官方来源：

- <https://qwenlm.github.io/qwen-code-docs/en/users/features/hooks/>
- <https://www.codebuddy.ai/docs/cli/hooks>
- <https://www.npmjs.com/package/@tencent-ai/codebuddy-code>

## 短稿判断

本轮没有把“正文必须长于提示词”设成门。`S1` 只看文种是否完成现状/缘由、拟办事项、未决状态、请批落点和有事实支撑的一层作用；简洁但功能完整即通过。十个 CLI 的实际正文都没有因保守而只剩材料摘要或裸提纲句。`S2` 才执行明确的240—300字符合同：四种当前 companion 得到无争议质量 PASS，CodeBuddy 2.141.0 得到范围内终稿和真实 profile 生命周期但保留证据/措辞限制，Qwen 无 Hook 另得范围内干净正文。

因此，当前可证结论是“已解决已知的跨 provider 系统性过短问题，当前未见共性短回退”，不是“任何模型、任何材料永远不会短”。新反例只有同时满足以下条件才重开：真实正文遗漏文种必要关系；问题在至少两家独立 provider 复现；且能归因到当前产品规则、Hook 或 adapter。材料稀疏但功能完整的短稿不算失败；一层合理归因、即时作用、低强度预期和条件性总结继续允许。

## 跨文种扩大真稿

所有有效样本均通过 Claude Code 2.1.251 CLI 加载当前 Skill 与 `delivery_review` companion，写稿模型只用登记的低成本路线。第一次未注入 OpenCodex loopback 的 `unrecognized_model` 运行按预登记记技术无效，不进入下表。

| 用例 | 两家低成本 provider | 正文计数 | 目标判定 | 残余观察 |
| --- | --- | ---: | --- | --- |
| `N1_DATED_ACTIVITY_NEWS` | Alibaba Token Plan 2 / OpenCode Go DeepSeek V4 Flash | 164 / 160 | 2/2 保留2026年8月26日、52/49/3范围、引语归属、分类反馈未完成与补充交流未定；只概括一层现场交流作用 | 无共同目标失败 |
| `U1_UNRESOLVED_SITUATION` | Alibaba Token Plan / MiniMax M3 | 140 / 152 | 2/2 区分联调已完成、记录已形成但未附、演练未开展且未安排、采购询价中且未决定 | 无共同目标失败 |
| `M1_NOISY_MINUTES` | Ollama / Alibaba Token Plan 2 DeepSeek V4 Flash | 213 / 217 | 2/2 采用纠正后的9月5日试运行口径，守住信息中心与业务处正式责任、采购提议未决定、9月10日仅暂定 | 无共同目标失败 |
| `L1_LONG_REPORT` | MiniMax M3 / OpenCode Go DeepSeek V4 Flash | 正文1948 / 2123；含独立标题全文1968 / 2138 | 2/2 进入1800—2400合同，事实和五类状态完整，结构含进展依据、问题原因、保持原强度的下一步考虑 | 各有个别可商榷推断，但没有同一硬事实/状态问题；不据单 provider 改规则 |

长报告本轮证明当前 Skill 具备真实写作价值：两稿均完整覆盖23个必要字面量，后半篇仍有问题分析和条件性后续，没有退化成头重脚轻的材料罗列。MiniMax 单稿把37项待补进一步解释为来源数据/字段口径问题，OpenCode Go 单稿写“指标口径一致”“工作量相对有限”，这些均非材料明示；它们没有跨 provider 复现，也不是本轮产品 diff 造成，故登记为单 provider 审慎观察，不误判为共同失败，也不触发更严门禁。

## 原始证据与实际命令

原始 stdout/stderr、终稿、receipt、隔离 profile 和 Hook 事务保存在忽略目录 `output/host-cli-revalidation-r1/`；关键回执包括：

- `claude-2.1.251-s1/run/receipt.json`
- `codex-0.151.0-s1/run-current-r3/receipt.json`
- `codex-0.151.0-s2/run-current-r1/receipt.json`
- `codebuddy-2.141.0-s2/run-opencodex-r3/receipt.json`
- `zcode-3.10.1-17-s1/run-latest-r4/receipt.json`
- `qwen-0.22.3-s2/run-current-r1/receipt.json`
- `qwen-0.22.3-s2-ablation/run-no-hook-r1/receipt.json`
- `qwen-0.22.3-s2-json/run-hook-json-r1/receipt.json`
- `kimi-0.39.1-s1/run-latest-r3/receipt.json`
- `hermes-0.20.6-s1/run-current-r1/receipt.json`
- `dsh-0.1.1-rc.2-s1/run-current-r2/receipt.json`
- `openclaw-2026.7.1-2-s1/run-current-r2/receipt.json`
- `expanded/n1-alibaba2/run-r2/receipt.json`
- `expanded/n1-opencodego-r2/run/receipt.json`
- `expanded/u1-alibaba-r2/run/receipt.json`
- `expanded/u1-minimax-r2/run/receipt.json`
- `expanded/m1-ollama/run/receipt.json`
- `expanded/m1-alibaba2/run/receipt.json`
- `expanded/l1-minimax/run/receipt.json`
- `expanded/l1-opencodego/run/receipt.json`

CodeBuddy 2.141.0 的全局 `CODEBUDDY_PLUGIN_DATA` 终态记录已脱敏摘录到可提交证据 [`codebuddy-2.141.0-s2-lifecycle.json`](codebuddy-2.141.0-s2-lifecycle.json)。记录显示 `stop_attempts=1`、`delivery_verified=true`、`data_retention_state=raw_turn_data_redacted`，独立从 stdout 提取的终稿 SHA-256 与 `87035a9e...` 完全一致。这只能证明真实 profile 生命周期，不能冒充隔离 data root；stdout 的 `apiKeySource=copilot.tencent.com` 也不能证明 OpenCodex provider 注入。

实际使用的命令族：

```text
npm view <CLI-package> version
py -3 maintenance/tests/evidence/host-cli-revalidation-r1/run_capture.py --case-id <case> ... -- <real CLI command>
npx -y @anthropic-ai/claude-code@2.1.251 ... -p <prompt>
npx -y @openai/codex@0.151.0 exec ... -
npx -y @tencent-ai/codebuddy-code@2.141.0 -p ...
npx -y zcode-app-cli@3.10.1-17 ... <prompt>
npx -y @qwen-code/qwen-code@0.22.3 ... <prompt>
npx -y @moonshot-ai/kimi-code@0.39.1 ... <prompt>
opencode ...
hermes chat -q <prompt>
dsh --profile headless <prompt>
openclaw agent ...
```

三项高成本盲审只在独立 Codex Desktop 任务读取固定提交、原始回执和官方宿主协议，分别使用 Qwen3.8 Max、Grok 4.6 与 Kimi K3，思考强度均为 ultra；它们不产生新稿，也不替代低成本真稿准入。三路终判与交叉裁决见 [`hook-cold-review.md`](hook-cold-review.md)。

## 产品影响和剩余风险

- 本轮产品字节、普通 references、description、Hook core 和 adapter 均为0差异；不产生版本更新候选。
- CodeBuddy 2.141.0 已补最新 CLI、当前 Skill 触发、真实 profile Hook、精确终稿和可提交生命周期记录，但没有补齐隔离 data root、reference 实际读取、S1 或 OpenCodex provider 注入；状态精确降为真实 profile 生命周期通过，不把生命周期通过写成无条件文稿质量或完整 provider 适配通过。
- Qwen 0.22.3、Kimi 0.39.1、OpenCode 1.18.25 需要新的宿主可控终稿面或新的真实反例后再开单原子；当前不留无人处理的 `HOLD`。
- OpenClaw 仍只有普通 Skill 内容证据，不能宣传正文直交或 Hook。
- 本轮只测试 Windows CLI/headless；不外推 POSIX、TUI、IDE、恢复会话或未声明 capability。
