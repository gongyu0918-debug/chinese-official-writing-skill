# 模型职责修订

2026-08-25 用户明确校正模型用途：Kimi K3、Grok 4.6、Qwen 3.8 Max 只用于冷审或复杂构建评审，不用于普通真实写稿；真实写稿与审稿 A/B 使用 DeepSeek V4 Flash 0731 的可用 provider、OpenCode Go DeepSeek V4 Flash 和 MiniMax M3。

据此，`natural-preregister.md` 中候选通过后使用 Kimi K3 做非回退复核的计划取消，改为使用上述 DeepSeek V4 Flash provider。此前已完成的 Kimi 稿只保留为历史辅助观察，不计入本轮写稿准入。

R3D MiniMax main 基线完成写稿；候选臂持续重复目录探测和受限命令，未进入审稿，人工终止并记为 `TECH_INVALID_AGENT_LOOP`，不计质量胜负。后续先用 DeepSeek V4 Flash 做候选收敛验证，再决定是否值得重跑 MiniMax。
