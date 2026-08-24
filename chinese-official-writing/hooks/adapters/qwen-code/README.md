# Qwen Code Hook companion

本目录是 Qwen Code companion 的静态适配层。它不会自行运行、生成文件或修改 Qwen Code 配置；请从 `hooks/README.md` 按预览、确认、组装、校验、安装和启用顺序操作。

Agent 组装胶水层前必须展示目标目录和文件清单。固定映射如下：

| 静态源 | extension 根目标 |
| --- | --- |
| `chinese-official-writing/hooks/adapters/qwen-code/manifest.json` | `qwen-extension.json` |
| `chinese-official-writing/hooks/adapters/qwen-code/hooks.json` | `hooks/hooks.json` |
| `chinese-official-writing/hooks/adapters/qwen-code/gate_stop_hook.py` | `scripts/gate_stop_hook.py` |
| `chinese-official-writing/` | `skills/chinese-official-writing/` |
| `chinese-official-writing/hooks/core/gate_stop_hook.py` | `skills/chinese-official-writing/hooks/gate_stop_hook.py` |

组装后的整个目录才是 Qwen 原生 extension 根。`qwen-extension.json` 必须与目录名 `chinese-official-writing-gate` 一致；便携 Agent Plugin v1 不加载 Hook，不能替代本原生 extension。先由组装器完成 manifest、文件闭包和本地事件 smoke；用户确认后运行 `qwen extensions install <extension 根> --consent`，再用 `qwen extensions list` 核对版本、Skill 和启用状态。启用和移除使用 `qwen extensions`，不要直接修改其他 extension 的状态文件。

本适配层使用 Qwen 原生 `UserPromptSubmit`、`PostToolUse`、`Stop` 事件。请求只读取宿主单独保留的 `submitted_prompt`，避免把 Skill 注入内容或 Stop 续写理由当成用户原始材料；没有该字段的内部续调用不会新建门禁事务。用户以官方 `/<skill-name>` 方式直接调用本 extension 的 Skill 时，Qwen 不产生模型侧 `skill` 工具事件，adapter 只对行首完整命令 `/chinese-official-writing` 记录本包 Skill 已加载；普通文本提及或同前缀名称不会冒充加载。Qwen 0.22.0 在首次及后续 Stop 均传入 `stop_hook_active=true`，adapter 以当前请求内的 Stop 序号还原首次 D0 与续写轮，不把宿主该字段直接冒充 Claude 语义。Qwen 的外部 hooks 文件只替换 `${CLAUDE_PLUGIN_ROOT}`，因此命令使用该兼容变量定位脚本。运行数据写入 `QWEN_RUNTIME_DIR`，未单独设置时依次使用 `QWEN_HOME` 或事件 transcript 所在的 Qwen runtime 根。

组装时必须明确能力：默认 `delivery_review`；其余可选值为 `protective_expansion`、`under_length`、`over_length`、`delivery_cleanliness`、`repetition_cleanup`。每次只选一项，选择结果写入 extension 根 `hook-capability.json`，运行时不再动态探测或生成配置。

当前静态命令与在线证据使用 Windows `py -3`；其他平台没有完成在线验证，无法确认解释器时使用普通 Skill。启用后的 Hook 只读取当前事件和宿主给出的当前 transcript 路径，不扫描其他会话，也不主动联网。
