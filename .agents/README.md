# deepseek-tui / Agents Adapter

本目录提供 deepseek-tui 和兼容 `.agents/skills` 约定的 agent 工具适配副本：

```text
.agents/
└── skills/
    └── chinese-official-writing/
        └── SKILL.md
```

deepseek-tui 可识别仓库根目录 `skills/`，也会检查 `.agents/skills/`。本仓库保留两处副本，便于不同工具按自己的默认目录加载。

源文件以仓库根目录 `chinese-official-writing/` 为准。发布或更新前运行：

```powershell
python .\tools\sync_adapters.py
```
