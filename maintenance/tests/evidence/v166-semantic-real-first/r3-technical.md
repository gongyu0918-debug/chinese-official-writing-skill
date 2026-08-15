# R3 技术记录

六题均取得一个完整 `result`，没有重跑、补题或换模型。三条 provider lane 并行，每条 lane 内按题号串行。

| 题目 | 模型 | session | 时长 | 终态 |
| --- | --- | --- | ---: | --- |
| S07 | `opencode-go/deepseek-v4-flash` | `8cd83ee8-644c-4b98-b0b4-f1b6e1025d29` | 341.345秒 | success，exit 0 |
| S08 | `opencode-go/deepseek-v4-flash` | `23d54973-4d92-4f4d-9f43-a01fe068c27e` | 69.245秒 | success，exit 0 |
| S09 | `ollama-cloud/deepseek-v4-flash:0731` | `1c0508a0-9174-4103-b4d9-5f526cd946e3` | 75.818秒 | success，exit 0 |
| S10 | `ollama-cloud/deepseek-v4-flash:0731` | `0bb30ca6-b3d3-49cf-a7de-36378a0d8ad3` | 6.409秒 | success，exit 0 |
| S11 | `alibaba-token-plan-2/deepseek-v4-flash-0731` | `77007cb0-7c3c-4e21-ba0f-12787a614aaa` | 13.836秒 | success，exit 0 |
| S12 | `alibaba-token-plan-2/deepseek-v4-flash-0731` | `7ff88b18-aedc-4881-99b6-bf944090aea2` | 172.710秒 | success，exit 0 |

六题均为精确模型、`apiKeySource=none`、Read-only、0 web search、0 retry、无插件、无 Hook；流记录没有无效 JSON 行。所有 Read 均为冻结入口、information-selection、研究 formulaic reference 和当前任务需要的文种 reference。

## 稿件固定值

| 题目 | 非空白字符 | 用户区间 | SHA-256 |
| --- | ---: | --- | --- |
| S07 | 167 | 320—400 | `fac710efb8896cf9338da7eba9afd71358cdc3bea7985ea7f2a085f3a97593b0` |
| S08 | 363 | 350—430 | `1fa0c45927aa3efafd13c5e6e686fb41b9e8b06fbda1e4aff2c9a2c4d4a23b85` |
| S09 | 297 | 300—380 | `364d41b9379c8adee9dd2852884660a4a60631f45cc4a63c2796df92af37f553` |
| S10 | 170 | 320—400 | `35b593b7093fecc8c9fe564363c06c78ec63b94936bc56396618a734d41d9e35` |
| S11 | 455 | 300—380 | `38d8e27bdfa31e047d7eff86c00f3d481d9de02cdfc0fc228f952e825047d156` |
| S12 | 189 | 350—430 | `952d2d4926c5698bf4f823ff7ed98d3cd62c195266c4b84afbac295ec66b5bea` |
