# OpenClaw 兼容包

这是 GitHub 仓库内维护的 OpenClaw 兼容包，当前 GitHub 版本为 `1.6.6`，采用仓库根目录的 MIT 许可证。适配副本使用 `name: chinese_official_writing`，用于兼容 OpenClaw 的匹配规则；正文规则由 canonical Skill 同步，Hook 和交付门禁不进入本包。

```text
packages/openclaw/
└── skills/
    └── chinese_official_writing/
        ├── LICENSE
        ├── SKILL.md
        ├── references/
        └── scripts/prose_lint.py
```

从仓库根目录同步适配副本：

```powershell
python .\maintenance\tools\sync_adapters.py
```

本目录的更新只表示 GitHub 兼容包已同步，不代表 ClawHub 或其他外部市场已经发布同一版本。
