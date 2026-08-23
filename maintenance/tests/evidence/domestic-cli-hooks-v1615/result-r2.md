# Qwen Code 与 Kimi Code CLI 原生 adapter 复核

## 取代关系

本文件取代同目录 `result.md` 中“Qwen 没有可分发 Hook 面”和“Kimi wire 不可作为门禁输入”的阶段性结论，不改写旧记录。后续核对以本文件为准：Qwen Code 0.22.0 的 **native extension** 可同时分发 Skill 与 Hooks；Kimi Code CLI 0.38.0 的 native plugin 可分发 Skill 与 Hooks，且官方数据目录中的精确会话 `wire.jsonl` 能以本轮 byte offset 绑定 D0。Kimi 仍有每回合只执行一次 Stop 阻断的宿主上限。

## 环境与安装

| 项目 | 实测值 |
| --- | --- |
| 候选分支基线 | `codex/domestic-cli-hooks-v1615@e0ecde011ee79efab2bda13273f5c2881f24d3a5` |
| Qwen Code | `0.22.0`；隔离 `QWEN_HOME` 与 `QWEN_RUNTIME_DIR` |
| Kimi Code CLI | `0.38.0`；隔离 `KIMI_CODE_HOME` |
| 模型 | OpenCodex `alibaba-token-plan-2/qwen3.8-max` |
| Qwen companion | 最终候选 54 文件；`delivery_cleanliness` fingerprint `31398e9c3855546ee21a5f09ed52ca42a1e109062866745b7082c2bca92b37a1` |
| Kimi companion | 最终候选 53 文件；`delivery_cleanliness` fingerprint `60e914d67db80b0a4d9bb39d897d07971ab328b047f83ccc8241bc4f5213776d` |

- Qwen 使用 `qwen extensions install <本地 companion> --consent` 安装；`extensions list` 显示 `chinese-official-writing-gate 1.6.14` 已启用并发现 `chinese-official-writing`。
- Kimi 使用纯 CLI TUI 的 `/plugins install <本地 companion>` 安装；`/plugins info chinese-official-writing-gate` 显示 `enabled | state: ok`、版本 `1.6.14` 和 1 个 Skill。没有使用 GUI、电脑控制或浏览器登录。
- Kimi 主机另有同名全局 Skill，正式样本使用 `--skills-dir <已安装 plugin 根>/skills` 关闭自动发现并绑定已安装副本；trace 中两份 reference 均从 `plugins/managed/chinese-official-writing-gate/skills/...` 读取。

## Qwen Code 真实写稿与完整生命周期

会话 `f4145b02-eb46-4c3e-a90e-234b372c9e8e` 使用官方 `/chinese-official-writing` 命令加载 extension 内当前 Skill，并读取包内 `information-selection.md`、`genre-playbook-request.md`。稿件保留 6/3 台、完整日期、18→7 分钟、2 台、9.6 万元、待比选和仅申请启动程序；“根据试用情况”是一层低强度关系承接，没有把拟采购写成已批准或既得成效。

adapter 在线处理同一 `turn_id=qwen-1-821fd8706da8aca4` 的 3 次 Stop：

1. 首次 D0 启动交付洁净度检查；
2. 同稿修订进入选定稿回显；
3. 精确回显后放行并脱敏原请求、D0 和候选正文。

Qwen 0.22.0 在三次 Stop 都传入 `stop_hook_active=true`，native adapter 以当前请求的 Stop 计数还原首次与续写语义；没有 `submitted_prompt` 的 Stop 内部 UserPromptSubmit 被忽略，没有另开事务。终态回执：

- `delivery_verified=true`
- `selection=D0`
- 交付正文 154 字符
- 交付 SHA-256 `0ec7efca548eb2dba080b5626a2a9712db7f54898c465fc2d9ffab1b4557411e`
- chat JSONL SHA-256 `90c4e13d0a7c4b6ee6f2420db29542be0160c2caf6d69755ab68ca4c80066463`
- `data_retention_state=raw_turn_data_redacted`

最终正文：

> 关于启动图形工作站采购程序的申请
>
> 我办公室现有终端6台，其中3台频繁卡顿。2026年8月18日至22日，试用共享算力后，批量材料处理平均等待时间由约18分钟降至约7分钟。
>
> 根据试用情况，拟采购图形工作站2台，预算合计不超过9.6万元，配置与供应商待比选。本次仅申请是否同意启动采购程序。
>
> 妥否，请批示。

## 低成本跨 provider 补样

最终候选重组并安装后，只补三条便宜模型路线，不做三模型乘两个宿主的全交叉。adapter 协议映射与模型无关；本节只验证当前包在不同 OpenCodex provider 下的真实 Skill、写稿和宿主生命周期，不把单纯连通性当成通过。

| 宿主 / 精确模型 | 会话 | 真实任务与稿件结果 | Hook / 直接交付结果 | Token 记录 |
| --- | --- | --- | --- | --- |
| Qwen Code / `opencode-go/deepseek-v4-flash` | `2dc0099d-5370-473c-84ae-1393728bfa70` | 同一采购申请；读取当前包 3 个 reference，保留 6/3 台、完整日期、18→7 分钟、2 台、9.6 万元、待比选和仅申请启动程序；目的表述没有升级为既得成效 | 3 次 Stop，`selection=D0`、`delivery_verified=true`、终态脱敏；正文 SHA-256 `da49b880392d539cf2b84ca14f12110afea8d7bd6e9556a55fc8ac88500f7fa5`；chat SHA-256 `c86d6620b7ce24c0f90f47b774827f3982f2458a032e430fe4101744f3ae1785` | 4 请求；总计 179510，其中 cache read 133120 |
| Qwen Code / `ollama-cloud/deepseek-v4-flash:0731` | `6e459161-b151-45ea-92f3-4e1e2cf87f81` | 精确单点改稿；三个 transcript assistant response 均只把 3 台改成 2 台，其余逐字保持，D0 稿件通过 | core 完成 3 次 Stop、`selection=D0`、`delivery_verified=true` 和脱敏，正文 SHA-256 `0491225397d580fe0872630b1a44f9debfe2fe6c5dbb94fe59bb10eea66d7412`；但 Qwen `--output-format json` 的最终 `result` 把两次相同正文拼接为两份，记 `FAIL_DIRECT_USE`。chat SHA-256 `29d7abc48e7f002c5c89674d30ea63a47b5f2f00e92998718f3ad3fb512ce767` | 3 请求；总计 115378，无 cache read |
| Kimi Code / `minimax-cn/MiniMax-M3` | `session_f70ab9dc-d3be-4075-8f8a-ef0e396210b1` | 精确单点改稿；Skill 来源为最终已安装 plugin，只把 3 台改成 2 台，正文换行和其余文字保持；D0 93 字符，SHA-256 `0491225397d580fe0872630b1a44f9debfe2fe6c5dbb94fe59bb10eea66d7412` | 首次 Stop 提取并阻断，模型逐字重交；宿主仍不执行第二次 Stop，core 停在 `delivery_cleanliness_awaiting_revision`。wire SHA-256 `d7ebe25b0c99d51a042592665e2494b77ba9d921c26288a5f58201e995765a72` | 3 请求；input other 28204、cache read 50585、output 475，总计 79264 |

补样结论：OpenCode Go 路线同时通过稿件与 Qwen 完整闭环；MiniMax 路线通过稿件与 Kimi 单 Stop 能力边界；Ollama 路线证明模型单次输出和 adapter/core 均正确，但暴露 Qwen 0.22.0 在该 provider 的多 Stop 最终结果汇总重复，不能把 core 回执冒充直接可用交付。

无效运行保留但不计矩阵：一次 Kimi 启动因 PowerShell 保留变量名冲突，在模型请求前退出；另一次 MiniMax 夹具误把换行传为字面量 `` `n``，虽完成 Skill 与 Stop 生命周期，但不计稿件质量，随后以上述真实换行样本取代。

## Kimi Code CLI 真实写稿与单 Stop 生命周期

会话 `session_d044ffa1-2eeb-42b3-bd3f-cbb11c9e9f77` 的模型调用、Skill 与 references 均来自已安装 plugin。UserPromptSubmit allow 路径没有标准输出，不再把 `{}` 注入模型上下文。adapter 在 UserPromptSubmit 时记录精确 `session_id`、受限于 `KIMI_CODE_HOME/sessions` 的 wire 路径和当时 byte offset；Stop 时只读取该 offset 后的 main-agent records，并取最后一个 `finishReason=end_turn` 的完整 assistant step。

首次 Stop 提取到的 D0 为 172 字符，SHA-256 `869314f5d4b591c1565e6118db422bcbeb3a25a9375f1a3afa6254c0c546b7de`。共享核心返回交付洁净度阻断，模型随后逐字重交同稿。稿件保留全部给定事实与未决状态；“改善设备条件、提升材料处理效率”分别由 3 台卡顿和等待时间 18→7 分钟支撑，是目的表述，不是已取得成效。

Kimi 0.38.0 在一次 Hook 阻断后不再运行第二次 Stop。核心因此如实停在 `delivery_cleanliness_awaiting_revision`，不能验证重交稿、生成终态 hash 或执行终态脱敏。本轮证明的是完整 native adapter 的安装、Skill、事件、D0 提取和首次阻断，不宣称 Kimi 与多 Stop 宿主等价闭环。wire JSONL SHA-256 为 `69123cbb077417cf71178014ab3cb54750d8e0298d8926ee4d14b0348ceb5c48`。

最终正文：

> 关于启动办公设备采购程序的申请
>
> 办公室现有终端6台，其中3台频繁卡顿。2026年8月18日至22日试用共享算力后，批量材料处理平均等待时间由约18分钟降至约7分钟。为改善设备条件、提升材料处理效率，拟采购图形工作站2台，预算合计不超过9.6万元。
>
> 上述采购尚未批准，设备配置与供应商待比选。本次仅申请是否同意启动采购程序。
>
> 妥否，请批示。

## 结论与边界

- Qwen Code：native extension adapter 已形成当前 Skill、真实写稿、三 Stop、hash 绑定交付和终态脱敏闭环。便携 Agent Plugin v1 仍不加载 Hook，不能替代 native extension。
- Kimi Code CLI：native plugin adapter 已完整实现宿主协议映射和当前 D0 获取；宿主单 Stop 上限使多阶段能力只能完成第一次阻断。需要二次语义核验或 hash 回显的能力不得在 Kimi 上标成完整闭环。
- 两个普通 Skill 包仍保持无 Hook；companion 只在用户明确安装并启用后运行。

## 实际命令

```powershell
qwen --version
qwen extensions install <qwen-companion> --consent
qwen extensions list
qwen --debug --auth-type openai --model alibaba-token-plan-2/qwen3.8-max --openai-api-key opencodex-loopback --openai-base-url http://127.0.0.1:10100/v1 -p $prompt -o json
```

```powershell
kimi --version
kimi --auto
# 在纯 CLI TUI 中执行：/plugins install <kimi-companion>
# 在纯 CLI TUI 中执行：/plugins info chinese-official-writing-gate
kimi --model opencodex/alibaba-token-plan-2/qwen3.8-max --skills-dir <installed-plugin-skills> -p $prompt --output-format stream-json
```

```powershell
python -B maintenance/tools/assemble_hook_companion.py --host qwen-code --capability delivery_cleanliness --output <ignored-output>
python -B maintenance/tools/assemble_hook_companion.py --host kimi-code --capability delivery_cleanliness --output <ignored-output>
```

无效但保留的 Kimi 命令：`kimi -p "/plugins install <path>"`。prompt mode 把 slash 文本交给模型而非 TUI command dispatcher，模型开始研究安装；该会话被中止，不算安装证据。

## 官方与实现来源

- [Qwen Code native extensions](https://qwenlm.github.io/qwen-code-docs/en/users/extension/introduction/)
- [Qwen Code Hooks](https://qwenlm.github.io/qwen-code-docs/en/users/features/hooks/)
- [Kimi Code CLI plugins](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/plugins.html)
- [Kimi Code CLI Hooks](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/hooks.html)
- 本机 `@qwen-code/qwen-code 0.22.0`：CLI Stop 路径每次传入 `stop_hook_active=true`，debug trace 记录三次 adapter Hook 成功执行。
- 本机 `@moonshot-ai/kimi-code 0.38.0`：plugin hooks 注入 `KIMI_CODE_HOME/KIMI_PLUGIN_ROOT`；`runStop` 在一次续写后跳过后续 Stop；`session_index.jsonl` 与 `sessions/.../agents/main/wire.jsonl` 是当前官方数据布局。
