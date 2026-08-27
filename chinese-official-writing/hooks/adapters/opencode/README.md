# OpenCode Hook companion

本目录是 OpenCode companion 的静态适配层，只支持常驻交互 CLI（包括 `opencode --mini`）。OpenCode 1.18.23 的 `run` 无头命令会在 `session.idle` 插件处理完成前退出，且官方没有同步 `Stop` 或最终文本替换事件；因此本 adapter 在 `opencode run` 中不启动门禁，也不得宣称无头交付已受保护。

组装后的 `.opencode/` 是项目级覆盖目录：

| 静态源 | 项目目标 |
| --- | --- |
| `chinese-official-writing/hooks/adapters/opencode/opencode_gate_plugin.js` | `.opencode/plugins/chinese-official-writing-gate.js` |
| `chinese-official-writing/` | `.opencode/skills/chinese-official-writing/` |
| `chinese-official-writing/hooks/core/gate_stop_hook.py` | `.opencode/skills/chinese-official-writing/hooks/gate_stop_hook.py` |
| 组装时选择的能力 | `.opencode/hook-capability.json` |

组装器只生成静态目录，不复制到业务项目、不修改 `opencode.json`、不设置环境变量，也不启动 OpenCode。用户确认目标项目后，先预览其现有 `.opencode/`，再合并上述精确文件；不要覆盖其他项目插件或 Skill。

OpenCode 会同时扫描项目 `.opencode/skills`、用户级 `.agents/skills` 和 `.claude/skills`。若存在另一个同名 `chinese-official-writing`，官方实现会记录重名但最终来源可能不稳定。本 adapter 只在模型实际加载本 companion 内的 Skill 时启动；检测到同名外部副本时保持普通写稿并写本地警告。启用前应移除或改名旧副本；隔离验证可显式设置 `OPENCODE_DISABLE_EXTERNAL_SKILLS=1`，adapter 不会替用户静默设置该开关。

本适配使用 `session.idle` 读取同一 session 的当前请求、已完成的 `skill`/`read`/`bash` 工具记录和末次助理文本，再把事件映射到共享门禁。门禁要求继续时，adapter 延迟一次调用官方 `session.prompt`；发送前重新核对外部用户消息、末次助理稿 hash 和续写计数，任一变化都取消旧续写、保留当前可见 D0 并脱敏旧事务。若插件在门禁未终态时重载，adapter 不猜测或重放已消费的中间状态，同样安全回退 D0；已进入 `session.prompt` 派发的同进程实例则继续由原实例单独完成，重载实例不重复发送。因此 TUI 会依次显示 D0、中间复核响应和最终选择，属于可见二次生成，不是同步拦截或原位替换。

默认数据父目录为 OpenCode 的 XDG 数据目录下 `chinese-official-writing-gate`；设置了绝对 `OPENCODE_DB` 时使用数据库同级目录。需要固定位置时可在启动 OpenCode 前设置 `COW_OPENCODE_GATE_DATA`。共享核心会在该父目录下创建精确的 `candidate-ai-gate-hook` 子目录；adapter 另用 `opencode-adapter-state` 保存不含正文的当前回合 hash 和派发相位，终态、回退或成功派发后删除精确状态文件。adapter 不联网、不扫描其他 session，也不把正文写入日志。若 Python/core 本身不可用，精确中止也可能失败，仍按上级说明人工清理未完成事务。

组装时必须明确能力：默认 `delivery_review`；其余可选值为 `protective_expansion`、`under_length`、`over_length`、`delivery_cleanliness`、`repetition_cleanup`。每次只选一项，运行时不动态探测或改写配置。当前在线证据使用 Windows、OpenCode 1.18.23 和项目级本地插件；其他平台需先确认可用的 `python3`/`python` 与同一交互生命周期。
