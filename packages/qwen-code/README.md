# Qwen Code 普通 Skill

从仓库根目录运行 `python .\maintenance\tools\sync_adapters.py --host qwen`，把生成的 `output/compatibility-packages/qwen-code/skills/chinese-official-writing/` 复制到 Qwen Code 的 Skill 目录。

普通包不含 Hook。Qwen Code 的 native extension Hook 继续使用 [静态适配](../../chinese-official-writing/hooks/adapters/qwen-code/README.md)及现有组装器；它与 QwenWork 是不同宿主。见[构建选项](../README.md)。
