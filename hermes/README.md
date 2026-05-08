# Hermes 适配

这个目录保留 Hermes 可读取的技能副本。副本内容来自根目录 `chinese-official-writing/`，并在 `SKILL.md` 头部保留 Hermes 需要的版本和元数据。

```text
hermes/
└── skills/
    └── chinese-official-writing/
        └── SKILL.md
```

修改主技能目录后运行同步脚本：

```powershell
python .\tools\sync_adapters.py
```
