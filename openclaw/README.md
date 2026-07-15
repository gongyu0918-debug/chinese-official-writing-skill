# OpenClaw / ClawHub 适配

ClawHub 发布目录为 `openclaw/skills/chinese_official_writing/`。主仓库技能名和 ClawHub slug 为 `chinese-official-writing`，OpenClaw 适配副本使用 `name: chinese_official_writing`，用于兼容其当前匹配规则。

```text
openclaw/
└── skills/
    └── chinese_official_writing/
        └── SKILL.md
```

同步适配副本：

```powershell
python .\tools\sync_adapters.py
```

发布命令：

```powershell
clawhub skill publish .\openclaw\skills\chinese_official_writing --slug=chinese-official-writing --name=中文公文写作 --version=1.5.14 '--tags=chinese,official-document,writing,gongwen,ai-compute'
```
