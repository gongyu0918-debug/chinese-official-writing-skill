# Codex Hook companion

本目录是 Codex companion 的静态适配层。它不会自行运行、生成文件或修改 Codex 配置；请从 `hooks/README.md` 按预览、确认、组装、校验、安装和启用顺序操作。

Agent 组装胶水层前必须展示目标目录和文件清单。固定映射如下：

| 静态源 | 插件根目标 |
| --- | --- |
| `chinese-official-writing/hooks/adapters/codex/manifest.json` | `.codex-plugin/plugin.json` |
| `chinese-official-writing/hooks/adapters/codex/hooks.json` | `hooks/hooks.json` |
| `chinese-official-writing/hooks/adapters/host_gate_adapter.py` | `scripts/host_gate_adapter.py` |
| `chinese-official-writing/` | `skills/chinese-official-writing/` |
| `chinese-official-writing/hooks/core/gate_stop_hook.py` | `skills/chinese-official-writing/hooks/gate_stop_hook.py` |

组装后的整个目录才是插件根。Codex 专用的 `agents/openai.yaml` 可保留；不得带入 CodeBuddy 或 Claude Code manifest。

组装时必须明确能力：默认 `delivery_review`；如用户选择保护性外扩精确删除，则使用 `protective_expansion`。选择结果写入插件根 `hook-capability.json`，运行时不再动态探测或生成文件。

正式启用前由当前 Codex 版本完成校验、注册、信任确认和事件检查；无法确认时使用普通 Skill。关闭当前任务可说“本次关闭 Hook”；完全移除使用 `codex plugin remove <插件>@<marketplace>`。
