# 国产 CLI、OpenCodex 与 Hook 生命周期结果

## 结论

本轮把“普通 Skill 可用”和“交付 Hook 可用”分开验证。Qwen Code、Kimi Code CLI、ZCode runtime 都能通过本机 **OpenCodex** 调用第三方模型并读取当前仓库的普通 Skill；只有 ZCode 同时具备插件级 Hook 装载、完整 `Stop.last_assistant_message`、插件根/数据根和阻断续跑语义，形成可工程化的第四宿主候选。

ZCode 候选不是新造门禁核心：`.zcode-plugin` 只提供 manifest 与原生 `process` Hook，运行时复用现有 Claude-compatible 薄适配器和唯一 core。专用 companion 为54文件，`delivery_cleanliness` 组装 fingerprint 为 `55592d126221df91488a81e7cc6f001581b87964a7b0f0da5cb3010dab4bd237`。

Qwen Code 当前适合继续使用普通 Qwen package，并保留用户/系统 settings 级 Hook 研究；其官方 Agent Plugin v1 明确不装载 Hook，不能把 settings 原型包装成可分发插件。Kimi Code CLI 0.38.0 的 Stop 输入没有完整成稿，也没有 transcript 路径，当前不接完整交付门禁。

## 环境与边界

| 项目 | 实测版本/状态 |
| --- | --- |
| Qwen Code | `@qwen-code/qwen-code 0.22.0` |
| Kimi Code CLI | `@moonshot-ai/kimi-code 0.38.0` |
| ZCode | `zcode-app-cli 3.8.1-15` 社区 wrapper，携带 ZCode Agent runtime `0.16.3` |
| OpenCodex | `@bitkyc08/opencodex 2.26.0`，loopback `127.0.0.1:10100` |
| 仓库基线 | `main@e3ed9bb374fd13234ea0eff9ea61c9e0f3cc7e69`；独立分支 `codex/domestic-cli-hooks-v1615` |

- 全程只用 CLI；没有调用 GUI、电脑控制或浏览器登录。
- Qwen Computer Use 已关闭；ZCode `browser-use` 插件显式 disabled/suppressed。
- observer 只保存事件字段名、类型、文本长度与 SHA-256，不保存原始提示词或正文。
- OpenCodex 当前可见 Alibaba、xAI、Ollama Cloud、DeepSeek、MiniMax 等 provider；本轮宿主协议成立后只做最小真实写稿，不把 provider 数量冒充质量结论。
- ZCode 没有可确认的官方独立 CLI。本结果准确表述为“社区 wrapper 携带的官方 runtime”；wrapper 会给 Agent 调用隐式加入 `--browser-use=headless`，因此真实写稿直接调用其 `vendor/zcode.cjs`，没有经过 wrapper 提示词路径。

## 真实写稿与生命周期

| 宿主 | 模型/当前 Skill | 成稿质量 | Hook 事实 | 判定 |
| --- | --- | --- | --- | --- |
| Qwen Code | OpenCodex `alibaba-token-plan-2/qwen3.8-max` provider 连通；唯一 wrapper 强制读取当前 `packages/qwen-code` 时使用 `qwen3.6-flash` | 当前包样本新增“使用年限较长、性能衰减、我办、效率提升显著”等材料外事实，质量 FAIL。另一次 qwen3.8-max 稿件事实安全，但实际读取的是全局旧版1.5.34，只能证明协议字段，不能算当前候选写稿通过 | `UserPromptSubmit`、`PostToolUse(read_file)`、`Stop` 均触发；Stop 有完整正文，当前包失败稿为229字符，SHA-256 `7ee5481da3d188839e33a088e2a9ed769504bd47fe5df2c1505ab44700a87d4e` | 普通 Skill/Stop 字段成立；写稿未形成当前包的稳定通过，官方插件又不装载 Hook，不工程化 |
| Kimi Code CLI | OpenCodex `minimax-cn/MiniMax-M3`；显式读取当前 `packages/agent-skills` | 事实、金额和未决状态基本完整；“待程序启动后按相关规定开展后续工作”是材料外泛化后续句，“请示事项”混入申请，记为可用但不洁净通过 | `UserPromptSubmit`、4次 `PostToolUse(Read)`、`Stop` 触发；Stop 只有 `client_type,cwd,hook_event_name,session_id,stop_hook_active`，无正文或 transcript 路径 | 普通 Skill 可用；Stop 缺 D0，不能接完整交付门禁 |
| ZCode 基线 | OpenCodex `alibaba-token-plan-2/qwen3.8-max`；当前 `packages/agent-skills` | 首份基线正文事实安全，但带“已完成资料核对”等正文外说明，直接交付 FAIL | 插件 observer 收到完整 Stop；`ZCODE_*` 与 `CLAUDE_*` 兼容根变量同时存在 | 协议可用，进入最小 companion 实验 |
| ZCode 既有 Claude companion | 同上；显式加载 companion 内当前 Skill | 189字符采购申请正文直接可用 | `Skill`、`Read`、3次同 SHA Stop；`delivery_cleanliness` 选择洁净 D0，SHA-256 `7ee93ae62b56286ae48ffcc53a041727b55cc9d11929ba2918b646850100b79a` | 证明现有薄适配器可被 ZCode 兼容运行；D0 本身洁净，不能宣称 Hook 修好了基线 |
| ZCode 专用 companion | 同上；`.zcode-plugin` 54文件包内当前 Skill | 210字符采购申请保留6/3台、完整试用日期、18→7分钟、2台、9.6万元、尚未批准、配置/供应商待比选和只申请启动程序；“已影响日常办公”“作用明显”为给定卡顿及实测降时支持的一层作用判断，标题语序略生硬但可直接使用 | 插件列举为1 Skill/3 Hooks；`Skill`、2次 `Read`、3次同 SHA Stop；D0/hash/终态脱敏闭环，SHA-256 `d848a952a90b1f4788ea4919af98659a730bda4fffec4b9e01849fe66ee509c9` | 生命周期与当前写稿通过；ZCode 静态 adapter 可作为干净合并候选 |

ZCode 专用 companion 最终正文：

> 关于启动采购2台图形工作站的申请
>
> 办公室现有终端6台，其中3台频繁卡顿，已影响日常办公。2026年8月18日至22日，试用共享算力开展批量材料处理，平均等待时间由约18分钟降至约7分钟，算力支撑对提升工作效率作用明显。为进一步改善办公条件、满足批量材料处理需求，拟采购图形工作站2台，预算合计不超过9.6万元。
>
> 目前，本次采购尚未批准，具体配置和供应商有待比选确定。本次仅申请是否同意启动采购程序。
>
> 妥否，请批示。

## 协议边界

### Qwen Code

- Stop 提供 `last_assistant_message`、`stop_hook_active` 和 transcript 路径，直接薄适配在技术上可行。
- 官方 Agent Plugin v1 只分发 skills 与 MCP，commands、agents、hooks 会被忽略；当前没有可靠的插件内 Hook 分发面。
- settings 级 Hook 能运行，但缺少与 Skill 包同生命周期的安装/启用/数据根契约。本轮不把本机 settings 原型加入产品。

### Kimi Code CLI

- 安装包 `dist/main.mjs` 的 `runStop` 只调用 `withSessionFacts({ stopHookActive: false })`；实际 Stop 事件与源码一致，没有末次成稿。
- 隔离会话目录的 wire 日志可以事后找到文本，但它是未文档化存储格式，且不能证明 Stop 时序和落盘完成，不作为门禁输入。

### ZCode

- 插件根支持 `.zcode-plugin/plugin.json` 与 `hooks/hooks.json`；项目级 Hook 配置不生效，必须显式加载插件。
- `process` Hook、`ZCODE_PLUGIN_ROOT/DATA`、完整 Stop 成稿和阻断续跑均已观察；runtime 同时提供 Claude 兼容根变量，所以无需复制第二份门禁核心。
- 社区 wrapper 的帮助/转发层列出 `--max-turns`、`--allowed-tools`，runtime 0.16.3 实际拒绝 `--max-turns`。该次调用在模型前退出，记为技术失败；成功样本使用 `plan` 模式、只读 PreToolUse guard 和禁用 browser-use 的直接 runtime。

## 工程改动与准入边界

- 新增 `hooks/adapters/zcode/{manifest.json,hooks.json,README.md}`。
- companion 组装器新增 `--host zcode`，目标 manifest 为 `.zcode-plugin/plugin.json`。
- 既有 Claude-compatible adapter 只增加 `ZCODE_PLUGIN_ROOT/DATA` fallback；核心、capability 和写作规则未改。
- `host-capabilities.json` 区分 Qwen/Kimi 的普通 Skill 能力与 ZCode 的已验证生命周期。
- 普通 Qwen/Agent Skills 包仍不包含 Hook；ClawHub 无 Hook 包策略不变。

本轮只有 ZCode adapter 候选值得合并。Qwen 需要先出现官方可分发 Hook 面，或形成经用户明确安装的稳定 settings companion；Kimi 需要 Stop 官方提供完整成稿或稳定文档化 transcript 后再继续。两者不是永久终止，只是当前最小工程边界不成立。

## 实际命令

```powershell
qwen --version
kimi --version
node <zcode-cli-entry> version
ocx --version
ocx models
npm list -g --depth=0 @qwen-code/qwen-code @moonshot-ai/kimi-code zcode-app-cli @bitkyc08/opencodex
```

```powershell
qwen --auth-type openai --model alibaba-token-plan-2/qwen3.8-max --openai-api-key opencodex-loopback --openai-base-url http://127.0.0.1:10100/v1 --safe-mode -p '只回复QWEN_READY，不要解释。' -o json
kimi doctor
ocx export --client kimi --json
ocx export --client zcode --json
```

```powershell
py -3 maintenance/tools/assemble_hook_companion.py --host zcode --output output/domestic-cli-hooks-v1615/zcode-native-companion --capability delivery_cleanliness
node <zcode-cli-entry> plugins list
node <zcode-cli-entry> --prompt $zcodePrompt --mode plan --surface terminal
```

失败且保留的命令形态：

```powershell
node <zcode-cli-entry> --prompt $zcodePrompt --mode plan --max-turns 8 --allowed-tools "Skill,Read,Glob,Grep" --disallowed-tools "Bash,Edit,Write,WebFetch,WebSearch,Agent" --surface terminal
```

结果：退出码1，`Unknown option '--max-turns'`；没有模型调用。

## 官方与实现来源

- [Qwen Code Hooks](https://qwenlm.github.io/qwen-code-docs/en/users/features/hooks/)
- [Qwen Code Agent Plugins v1](https://qwenlm.github.io/qwen-code-docs/en/users/extension/agent-plugins/)
- [Qwen Code model providers](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/model-providers/)
- [Kimi Code CLI Hooks](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/hooks.html)
- [Kimi Code CLI providers](https://www.kimi.com/code/docs/en/kimi-code-cli/configuration/providers)
- [ZCode Hooks](https://zcode.z.ai/en/docs/hooks)
- [ZCode plugins](https://zcode.z.ai/en/docs/plugin)
- [ZCode providers/configuration](https://zcode.z.ai/en/docs/configuration)
- [ZCode community CLI wrapper](https://github.com/kingsword09/zcode-cli)
- [OpenCodex](https://github.com/lidge-jun/opencodex)

本地实现交叉检查：

- `@moonshot-ai/kimi-code/dist/main.mjs` 的 `runStop` 输入只含 session facts 与 `stopHookActive`。
- `zcode-app-cli/bin/zcode.js` 定义并默认注入 `--browser-use=headless`；成功测试绕过该 wrapper。
- `zcode-app-cli/vendor/zcode.cjs` 同时解析 `.zcode-plugin`、`.claude-plugin` 和插件变量，实际事件 observer 又确认四个根/数据环境变量均存在。
