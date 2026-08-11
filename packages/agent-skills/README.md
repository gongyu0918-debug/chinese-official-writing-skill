# deepseek-tui / Agents 适配

这个目录面向 deepseek-tui 和兼容 `.agents/skills` 约定的 agent 工具。deepseek-tui 会检查项目根目录的 `skills/` 和 `.agents/skills/`，因此仓库同时保留两处副本，方便不同工具按默认路径加载。

```text
.agents/
└── skills/
    └── chinese-official-writing/
        └── SKILL.md
```

主技能目录是仓库根目录的 `chinese-official-writing/`。修改主目录后运行同步脚本：

```powershell
python .\tools\sync_adapters.py
```
