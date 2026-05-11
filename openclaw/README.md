# OpenClaw / ClawHub 适配

ClawHub 发布目录为 `openclaw/skills/chinese_official_writing/`。主仓库技能名为 `chinese-official-writing`，OpenClaw 适配副本使用 `name: chinese_official_writing`。

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
clawhub skill publish .\openclaw\skills\chinese_official_writing --slug chinese-official-writing --name "中文公文写作" --version 1.2.14 --tags "chinese,official-document,writing,gongwen,ai-compute"
```
