# 通用 Agent Skills 适配

这个目录面向兼容 Agent Skills 目录约定的工具。当前已在 Kimi Code CLI 与 ZCode runtime 中完成真实发现和写稿；它保存普通 Skill 副本，不包含交付 Hook。

```text
packages/agent-skills/
└── skills/
    └── chinese-official-writing/
        └── SKILL.md
```

主技能目录是仓库根目录的 `chinese-official-writing/`。修改主目录后运行同步脚本：

```powershell
python .\maintenance\tools\sync_adapters.py
```
