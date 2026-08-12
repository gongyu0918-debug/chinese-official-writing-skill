# v1.6.2 写稿与 DIFF 冷审技术冻结

- 写稿盲包 SHA-256：`2171a88fda22e81c9523a075d733bdf3ddd158451f956aa43dcf7d1872196dbc`
- v1.6.0 全量 DIFF 冷审包 SHA-256：`2afa02c24ded9a178160cd6b435277ee95e2774dea106f066a75a3b9c594abf7`
- 三名裁判均使用相同 prompt、max、独立配置/临时目录、1200 秒单次上限、零重试；模型路径探针均为 200。
- Grok4.5 `xai/grok-4.5`：VALID，157.281 秒；完整 9 组写稿 JSON 和 DIFF findings 已冻结。final SHA-256 `f504e1417aad12aa3f2c0acc01985bd646828fe8216fd92bcf6a80628bfc8cd7`。
- Kimi K3 `kimi/k3`：INVALID(timeout)，1200.031 秒；init/assistant 路径正确，但无 result/final，零重试，不补跑。
- Qwen3.8-max `alibaba-token-plan-2/qwen3.8-max`：INVALID(timeout)，1200.015 秒；init/assistant 路径正确，但无 result/final，零重试，不补跑。
- `receipts.json` SHA-256：`695af3bf7e2d9cd592f3cc2f152dfa50665976fc234006d16a04e60cedb91a65`。
- `hashes.json` SHA-256：`0f6ca71984ec4037fca2f896eaa24eaa3dbfa10f5e55f16e92c458b3dd39284c`。

本冻结发生在读取 mapping 前。Kimi/Qwen 的无终态不能作为胜负或 DIFF 结论，Grok 的单份有效结果也不能表述为三模型共识。后续解盲和源码归因必须完整保留两个 INVALID，并逐项复核 Grok findings；模型票数不能覆盖确定性门。
