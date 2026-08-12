# 宿主插件

本目录保存三套彼此独立的可安装插件根：`codex/`、`codebuddy/`、`claude-code/`。每套插件都包含自己的 manifest、Hook 事件配置、薄适配器和 `skills/chinese-official-writing/` 运行副本，可以在宿主缓存后独立工作。

插件内的 `skills/<name>/SKILL.md` 是宿主发现规范要求的入口，不是第二套产品规则，也不使用父目录跳转。产品规则只维护在包根 `SKILL.md`、`references/`、`scripts/` 和 `hooks/`；运行 `python -B maintenance/tools/sync_adapters.py` 后生成插件副本，不要直接编辑副本。

普通 Skill 安装不会自动启用这些插件或 Hook。用途、启用边界、失败回退和已验证范围见 [`../hooks/README.md`](../hooks/README.md)。
