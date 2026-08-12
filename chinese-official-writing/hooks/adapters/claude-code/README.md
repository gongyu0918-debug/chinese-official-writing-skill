# Claude Code Hook companion

本目录是 Claude Code companion 的静态适配层。它不会自行运行、生成文件或修改 Claude Code 配置；请从 `hooks/README.md` 按预览、确认、组装、校验、加载和启用顺序操作。

Agent 组装胶水层前必须展示目标目录和文件清单。固定映射如下：

| 静态源 | 插件根目标 |
| --- | --- |
| `chinese-official-writing/hooks/adapters/claude-code/manifest.json` | `.claude-plugin/plugin.json` |
| `chinese-official-writing/hooks/adapters/claude-code/hooks.json` | `hooks/hooks.json` |
| `chinese-official-writing/hooks/adapters/claude-code/gate_stop_hook.py` | `scripts/gate_stop_hook.py` |
| `chinese-official-writing/` | `skills/chinese-official-writing/` |
| `chinese-official-writing/hooks/core/gate_stop_hook.py` | `skills/chinese-official-writing/hooks/gate_stop_hook.py` |

组装后的整个目录才是插件根，不带 `agents/openai.yaml` 或其他宿主 manifest。先运行 `claude plugin validate <插件根> --strict`；临时启用时使用 `claude --plugin-dir <插件根>`。不传 `--plugin-dir` 即不会加载该临时 companion；已安装插件可用 `claude plugin disable <插件>` 禁用。

启用后的 Hook 使用宿主提供的插件数据目录保存本次门禁状态，不扫描其他 Agent，也不主动联网。
