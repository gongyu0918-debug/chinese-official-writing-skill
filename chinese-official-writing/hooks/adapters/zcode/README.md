# ZCode Hook companion

本目录是 ZCode companion 的静态适配层。它不会自行运行、生成文件或修改 ZCode 配置；请从 `hooks/README.md` 按预览、确认、组装、校验、加载和启用顺序操作。

Agent 组装胶水层前必须展示目标目录和文件清单。固定映射如下：

| 静态源 | 插件根目标 |
| --- | --- |
| `chinese-official-writing/hooks/adapters/zcode/manifest.json` | `.zcode-plugin/plugin.json` |
| `chinese-official-writing/hooks/adapters/zcode/hooks.json` | `hooks/hooks.json` |
| 既有 Claude-compatible 薄适配器 | `scripts/gate_stop_hook.py` |
| `chinese-official-writing/` | `skills/chinese-official-writing/` |
| `chinese-official-writing/hooks/core/gate_stop_hook.py` | `skills/chinese-official-writing/hooks/gate_stop_hook.py` |

组装后的整个目录才是插件根。ZCode 不读取项目级 Hook 配置，必须按宿主插件方式显式加载该目录；只安装普通 Skill 不会启用 Hook。启用前运行 `zcode plugins list`，确认插件、Skill 和 `UserPromptSubmit`、`PostToolUse`、`Stop` 三类事件均被发现。停用或移除时使用 ZCode 的插件配置，不删除其他插件目录。

本适配层使用 ZCode 的 `process` Hook 与 `${ZCODE_PLUGIN_ROOT}`。薄适配器同时接受 `${ZCODE_PLUGIN_DATA}`；ZCode 提供的 Claude 兼容变量仍可使用，但不复制第二份门禁核心。当前静态命令与在线证据使用 Windows `py -3`；其他平台没有完成在线验证，无法确认解释器时使用普通 Skill。

组装时必须明确能力：默认 `delivery_review`；其余可选值为 `protective_expansion`、`under_length`、`over_length`、`delivery_cleanliness`、`repetition_cleanup`。每次只选一项，选择结果写入插件根 `hook-capability.json`，运行时不再动态探测或生成文件。各能力的用途和边界见上级 `hooks/README.md`。

当前在线证据来自社区 `zcode-app-cli` 携带的 ZCode Agent runtime，不等同于智谱官方发布了独立 CLI。该 wrapper 的提示词路径会隐式加入浏览器参数，因此本轮验证直接调用其携带的 runtime，并禁用 browser-use 插件；产品适配结论只覆盖实际观察到的 ZCode 插件协议。

启用后的 Hook 使用宿主提供的插件数据目录保存本次门禁状态，不扫描其他 Agent，也不主动联网。
