# WorkBuddy / CodeBuddy Hook companion

本目录是 WorkBuddy/CodeBuddy companion 的静态适配层。它不会自行运行、生成文件或修改宿主配置；请从 `hooks/README.md` 按预览、确认、组装、校验、加载和启用顺序操作。

Agent 组装胶水层前必须展示目标目录和文件清单。固定映射如下：

| 静态源 | 插件根目标 |
| --- | --- |
| `chinese-official-writing/hooks/adapters/codebuddy/manifest.json` | `.codebuddy-plugin/plugin.json` |
| `chinese-official-writing/hooks/adapters/codebuddy/hooks.json` | `hooks/hooks.json` |
| `chinese-official-writing/hooks/adapters/host_gate_adapter.py` | `scripts/host_gate_adapter.py` |
| `chinese-official-writing/` | `skills/chinese-official-writing/` |
| `chinese-official-writing/hooks/core/gate_stop_hook.py` | `skills/chinese-official-writing/hooks/gate_stop_hook.py` |

组装后的整个目录才是插件根，不带 `agents/openai.yaml` 或其他宿主 manifest。先运行 `codebuddy plugin validate <插件根>`，再由用户明确选择是否用 `--plugin-dir <插件根>` 加载。未传入该参数时，普通 Skill 仍可独立运行；已安装插件可用 `codebuddy plugin disable <插件>` 禁用。

组装时必须明确能力：默认 `delivery_review`；其余可选值为 `protective_expansion`、`under_length`、`over_length`、`delivery_cleanliness`、`repetition_cleanup`。每次只选一项，选择结果写入插件根 `hook-capability.json`，运行时不再动态探测或生成文件。各能力的用途和边界见上级 `hooks/README.md`。

启用后的 Hook 使用宿主提供的插件数据目录保存本次门禁状态，不扫描其他 Agent，也不主动联网。
