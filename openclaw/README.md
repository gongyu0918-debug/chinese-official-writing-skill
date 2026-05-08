# OpenClaw / ClawHub Adapter

本目录提供 OpenClaw / ClawHub 发布副本：

```text
openclaw/
└── skills/
    └── chinese_official_writing/
        └── SKILL.md
```

主技能目录为了兼容 Codex 与 Claude Code 使用 `chinese-official-writing`。OpenClaw 文档示例使用 snake_case 技能名，因此本适配副本将 frontmatter 中的 `name` 同步为 `chinese_official_writing`。

发布或更新前运行：

```powershell
python .\tools\sync_adapters.py
```

ClawHub 发布目录建议指向：

```powershell
clawhub skill publish .\openclaw\skills\chinese_official_writing --slug chinese-official-writing --name "中文公文写作" --version 1.1.0 --tags "chinese,official-document,writing,gongwen,ai-compute" --changelog "Add multi-agent adapters and expanded ablation coverage."
```
