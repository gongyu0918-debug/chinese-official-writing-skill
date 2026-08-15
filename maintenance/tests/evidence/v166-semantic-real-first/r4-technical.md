# R4 技术记录

八题均取得一个完整 `result`，没有重跑、补题或换模型。三条 provider lane 并行，每条 lane 内按题号串行。

| 题目 | 模型 | session | 时长 | 终态 |
| --- | --- | --- | ---: | --- |
| S13 | `opencode-go/deepseek-v4-flash` | `d0a37f0e-5887-413e-a3ed-368fed16be18` | 163.595秒 | success，exit 0 |
| S14 | `opencode-go/deepseek-v4-flash` | `1226be3f-1238-462a-a380-772b7639a8a5` | 71.676秒 | success，exit 0 |
| S15 | `opencode-go/deepseek-v4-flash` | `af362c53-ad17-43ee-ae37-afe3d3cfa29d` | 635.918秒 | success，exit 0 |
| S16 | `ollama-cloud/deepseek-v4-flash:0731` | `32571b54-51bc-4759-9a5a-73d6f99f4bc6` | 93.181秒 | success，exit 0 |
| S17 | `ollama-cloud/deepseek-v4-flash:0731` | `3eab9802-d670-41a5-b9c1-2997b277ce6d` | 70.817秒 | success，exit 0 |
| S18 | `ollama-cloud/deepseek-v4-flash:0731` | `85b94b8d-1bec-4f94-977a-c9567cae6132` | 293.054秒 | success，exit 0 |
| S19 | `alibaba-token-plan-2/deepseek-v4-flash-0731` | `6fbb8457-234a-4248-a5c3-9aeaa0b7e28d` | 109.458秒 | success，exit 0 |
| S20 | `alibaba-token-plan-2/deepseek-v4-flash-0731` | `e9576c56-3c19-4e59-9140-5d970a7569d8` | 205.089秒 | success，exit 0 |

八题均为精确模型、`apiKeySource=none`、Read-only、0 web search、0 retry、无插件、无 Hook；流记录没有无效 JSON 行。Read 范围只含冻结入口、information-selection、研究 formulaic reference 和当前任务所需文种 reference。

## 稿件固定值

| 题目 | 非空白字符 | 用户区间 | SHA-256 |
| --- | ---: | --- | --- |
| S13 | 360 | 350—430 | `60760c9f1c5a80c6d13c61a5a6d89e414482b6cb93ee84e2750317f05252d0f4` |
| S14 | 328 | 320—400 | `e6f15522cf250f6b7b03eefcbef7a9e5b8f7bbc42d352dd1e48f4a383101cff8` |
| S15 | 213 | 350—430 | `7dc3e1a4a18c2734fbbf5930b47451de23f467a2c850b0f019830124613b38cb` |
| S16 | 151 | 320—400 | `5a8cf86c102f97d532c013d7bf598220a475446b9c4906bf65da4e7032c70fd5` |
| S17 | 157 | 320—400 | `8db1405a09073e416ea293ee399ec54d7ecc4776935f7efcd8e02cca4c944dd9` |
| S18 | 355 | 350—430 | `90afa2a95d80546e16842176bbc5c823bf6a6f6bf607a23eaf5a24df4e9235bc` |
| S19 | 317 | 320—400 | `74996554bbac8c146a100c74d9b80563c91f3447140f1ccfbb121a61dd0ed3c1` |
| S20 | 182 | 350—430 | `e4db0b5f08d1244307e6dfa9f9bddd0ee743d4416aeb838bd1f19e49dc4ef9c5` |
