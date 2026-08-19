# v1.6.10 后缺口能力在线样本结果

## 范围

本轮只为覆盖矩阵中仍缺当前版本在线证据的能力各补一个宿主样本，不重复已经完成的功能，也不据此扩大能力边界。所有包均由当前 `main` 的静态 adapter 与 canonical capability 组装；普通 Skill 路径未启用 Hook。

## 结果

| 能力 | 宿主与模型 | 同稿结果 | 生命周期与选择 |
| --- | --- | --- | --- |
| 篇幅不足中文计数保守回退 | WorkBuddy 5.3.13 / CodeBuddy CLI 2.115.0；DeepSeek V4 Flash，max | D0 106 字，候选 192 字；候选新增“两项、一项”等数量表达 | UserPromptSubmit、PostToolUse、Stop 均在线；机械门以 `under_length_quantity_added_dropped_or_changed` 选择 D0，原稿与交付 hash 同为 `f1472c5c…`，`delivery_verified=true` |
| 交付洁净度 | WorkBuddy / CodeBuddy；DeepSeek V4 Flash，max | 删除“下面是整理结果”、Markdown 包装及文后说明，正文逐字保留 | 选择 D1；原稿 `bd788e2b…`，交付 `d35b65e6…`，`delivery_verified=true` |
| 重复句与高相似句 | Claude Code 2.1.195；`opencode-go/deepseek-v4-flash`，max | 删除短稿中完全重复的第二句，保留恢复状态与原因核查两个不同信息 | 实际读取 Skill 后完成三事件和 repetition transaction；选择 E1，原稿 `8e50efa7…`，交付 `4f012274…`，`delivery_verified=true` |
| 超出上限收束 | Codex CLI 0.144.6；`opencode-go/deepseek-v4-flash`，max | 313 字压至 137 字，低于 220 字上限；数字、状态、职责和归属关系均保留 | 当前插件真实注册并读取 Skill；一次压缩后选择 D1，原稿 `31dcf678…`，交付 `be822015…`，`delivery_verified=true` |

## 中文计数的独立同稿复核

另用同一 106 字 D0 请求扩写到 180—230 字。真实 D1 为 206 字，事实与文种可用，但为了自然归纳新增“两项、前一项、后一项”。当前机械门把这些表达视为新增数量，保守选择 D0。CodeBuddy 在线样本以另一份 192 字 D1 重现同一结果，并完成 D0 精确交付。

本轮结论是“保守回退可用”，不是放宽中文数量保护。若以后要允许透明归纳，必须另做同一 D0/D1 的窄规则与真实稿验证。

## 未计入的尝试

- Claude 首次样本只证明插件和 Stop 事件在线，但模型没有读取 Skill，`skill_seen=false`，未计为重复清理能力样本；强制读取后的 R3 才计入上表。
- CodeBuddy 首次 PTY 会话未实际发送 prompt，也未发生模型调用，未计入。
- Codex 首次 runner 使用 PowerShell shim 触发权限错误，第二次隔离配置缺少代理认证返回 401；修复 runner 和隔离配置后的 R3 才计入。测试期间复制到隔离目录的认证文件已删除，未提交。

## 边界

- 每种原有缺口只补一个当前宿主在线样本；不由单一样本推定所有宿主、所有能力均已在线重跑。
- 这些样本验证 Hook 生命周期、选择和终稿 hash，不重新收紧已发布的语义门禁。
- 本轮没有新增 Hook 功能，也没有发布平台操作。
