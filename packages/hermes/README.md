# Hermes 适配

这个目录保留 Hermes 可读取的普通 Skill 副本。副本内容来自根目录 `chinese-official-writing/`，不包含交付 Hook。

```text
packages/hermes/
└── skills/
    └── chinese-official-writing/
        └── SKILL.md
```

修改主技能目录后运行同步脚本：

```powershell
python .\maintenance\tools\sync_adapters.py
```
