# 产品候选直连技术记录

三题均取得一个完整 `result`，没有重跑、补题或换模型。

| 题目 | 模型 | session | 时长 | Read 数 | 终态 |
| --- | --- | --- | ---: | ---: | --- |
| C01 | `opencode-go/deepseek-v4-flash` | `61e6ed8e-db98-412c-a7b4-74e8b61c6a12` | 82.300秒 | 3 | success，exit 0 |
| C02 | `ollama-cloud/deepseek-v4-flash:0731` | `74df68de-c6a7-4e32-a34d-b363541ace63` | 109.197秒 | 5 | success，exit 0 |
| C03 | `alibaba-token-plan-2/deepseek-v4-flash-0731` | `ce4d1aa4-ea56-4caa-a959-e19942d7010f` | 124.404秒 | 13 | success，exit 0 |

三题均为精确模型、`apiKeySource=none`、Read-only、0 web search、0 retry、无插件、无 Hook；流记录没有无效 JSON 行。三题都读取了新增 `formulaic-language.md`。C01 没有继续读取新闻叶，但由 formulaic route 完成标识；C03 的13文件读取暴露出责任书仍缺少直接文种叶接引。

| 题目 | 非空白字符 | 用户区间 | SHA-256 |
| --- | ---: | --- | --- |
| C01 | 190 | 180—240 | `6fadbe1c0a496c2c1105245e44dbf7772e1a7b8e87758777d5e527a9fc4e7110` |
| C02 | 358 | 350—430 | `626d826f3a29fece591ee81ca57ec911c1320df2f17ac60d43108eb4ced8b252` |
| C03 | 352 | 320—400 | `ceb081a0e2a972fe9fda40d0042245d2503cdaae5a3c30de87346e05d31c30b1` |
