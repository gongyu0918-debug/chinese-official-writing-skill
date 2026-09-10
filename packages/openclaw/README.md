# OpenClaw 兼容包

本目录仅保留 OpenClaw 构建说明，当前 GitHub 版本为 `1.6.32`，采用仓库根目录的 MIT 许可证。适配副本使用 `name: chinese_official_writing`，用于兼容 OpenClaw 的匹配规则；正文规则由 canonical Skill 同步，Hook 和交付门禁不进入本包。

```text
output/compatibility-packages/openclaw/
└── skills/
    └── chinese_official_writing/
        ├── LICENSE
        ├── SKILL.md
        ├── references/
        └── scripts/prose_lint.py
```

从仓库根目录生成无 Hook 安装包（不修改本目录）：

```powershell
python .\maintenance\tools\sync_adapters.py --host openclaw
```

生成目录可供 OpenClaw 安装或作为 ClawHub 发布输入；生成成功不代表外部市场已发布。已有输出不会被覆盖，再次构建请指定新的 `--output-root`。见[构建与归档说明](../README.md)。
