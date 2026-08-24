# Kimi Code CLI Hook companion

本目录是 Kimi Code CLI companion 的静态适配层。它不会自行运行、生成文件或修改 Kimi Code 配置；请从 `hooks/README.md` 按预览、确认、组装、校验、安装和启用顺序操作。

Agent 组装胶水层前必须展示目标目录和文件清单。固定映射如下：

| 静态源 | plugin 根目标 |
| --- | --- |
| `chinese-official-writing/hooks/adapters/kimi-code/manifest.json` | `kimi.plugin.json` |
| `chinese-official-writing/hooks/adapters/kimi-code/gate_stop_hook.py` | `scripts/gate_stop_hook.py` |
| `chinese-official-writing/` | `skills/chinese-official-writing/` |
| `chinese-official-writing/hooks/core/gate_stop_hook.py` | `skills/chinese-official-writing/hooks/gate_stop_hook.py` |

组装后的整个目录才是 Kimi plugin 根。安装前使用 Kimi Code CLI 的 `/plugins install <plugin 根>`，再用 `/plugins info chinese-official-writing-gate` 核对 Skill 与三类 Hook；启用、停用和移除使用 `/plugins` 命令，不直接修改其他插件记录。Kimi 会把本地安装复制到 `KIMI_CODE_HOME/plugins/managed/`，修改原组装目录不会自动更新已安装副本。

Kimi 0.38.0 的 `Stop` 事件没有正文或 transcript 路径。本适配层只按事件中的精确 `session_id` 查询 `KIMI_CODE_HOME/session_index.jsonl`，并读取该会话 `agents/main/wire.jsonl` 中当前回合最后一个已完成 assistant step；不枚举其他会话，不读取凭证。当前实现绑定并验证 0.38.0 的公开数据目录与 wire 记录词汇；无法确认索引、路径、当前回合边界或完整 `</think>` 分隔时 fail-open。

Kimi 会把非空的 UserPromptSubmit Hook 标准输出注入模型上下文，因此 allow 路径完全静默，只有阻断时才输出宿主规定的结构化 JSON。若系统同时存在同名用户级 Skill，在线验收应使用 `--skills-dir <已安装 plugin 根>/skills` 关闭自动发现并绑定本包副本；这只限定测试的 Skill 来源，不替代 plugin 安装或 Hook 生命周期。

Kimi 每回合最多接受一次会让模型续写的 Stop block；这一宿主限制低于 Codex、Claude、CodeBuddy、Qwen 和 ZCode 的重复 Stop 能力。adapter 会完整接入首次 D0 与共享核心，但需要多次 Stop 的修订、语义复核和最终回显不能据此宣称闭环。组装器仍提供全部静态能力选择，启用前应以当前版本真实生命周期确认目标能力；无法确认时使用普通 Skill。

组装时必须明确能力：默认 `delivery_review`；其余可选值为 `protective_expansion`、`under_length`、`over_length`、`delivery_cleanliness`、`repetition_cleanup`。每次只选一项，选择结果写入 plugin 根 `hook-capability.json`。当前静态命令与在线证据使用 Windows `py -3`；其他平台未完成在线验证。

启用后的 Hook 在 `KIMI_CODE_HOME/plugin-data/chinese-official-writing-gate` 暂存当前门禁状态，核心到达终态时按统一规则脱敏；它不主动联网。
