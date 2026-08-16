# 短稿自然度 R2 候选直写

日期：2026-08-17

R1 的4个完整候选全部低于明确篇幅下限。本轮不重复 A/B，也不改路由胶水；只在 R1 已有效的 Ollama、Alibaba 四题上各直写一次候选，判断语义规则自身是否同时满足篇幅和自然度。

- 固定 N03—N06，模型分别为 `ollama-cloud/deepseek-v4-flash:0731` 和 `alibaba-token-plan-2/deepseek-v4-flash-0731`，max、1200秒、0 retry、两条 provider lane、每家串行。
- 候选必须读取 R2 页，普通无 Hook。
- 四稿均须满足题面篇幅，保留事实、数字、状态、结构和文种；不得出现同一事实跨开头/分项/结尾复述、空泛收束、Markdown 或材料外扩。
- 任一稿篇幅、事实或状态失败即停在候选直写，不做 A/B、SOL 或工程集成。四稿均过后才进入小 A/B。

R2 页规范化 SHA-256：`e4c9d71d4a633c886b83f1648890047c9a626853ba542e9c78e983abbbaabed5`。
