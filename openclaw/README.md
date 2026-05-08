# OpenClaw / ClawHub 适配

这里放的是 ClawHub 发布用的技能目录。主技能名采用 `chinese-official-writing`，OpenClaw 适配副本按文档示例使用 snake_case，因此发布目录中的 frontmatter 写为 `name: chinese_official_writing`。

```text
openclaw/
└── skills/
    └── chinese_official_writing/
        └── SKILL.md
```

修改主技能目录后，先同步适配副本：

```powershell
python .\tools\sync_adapters.py
```

发布时指向该目录：

```powershell
clawhub skill publish .\openclaw\skills\chinese_official_writing --slug chinese-official-writing --name "中文公文写作" --version 1.2.4 --tags "chinese,official-document,writing,gongwen,ai-compute"
```
