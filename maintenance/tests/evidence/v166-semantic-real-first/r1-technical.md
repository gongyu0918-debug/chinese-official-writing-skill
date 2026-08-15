# R1 技术记录

## 调用前包装错误

第一次启动第一波时，PowerShell 临时变量误用只读变量 `$HOME`，S01、S03、S05 均在模型调用前停止。没有 provider 请求，不计模型重试。

## 第一波

修正变量名后，S01、S03、S05 各发出一次正式调用。CLI 使用 `--output-format json --verbose` 时把完整事件数组写入标准输出，输出超过工具回传上限；S01 可确认 `exit=1`，S03、S05 的终端回执被截断，三个隔离配置均未留下会话正文。三题均记 `TECHNICAL_INVALID_OUTPUT_CAPTURE`，不读取、不评分、不从截断片段选择正文。

## 第二波

第二波改用 `stream-json` 逐行过滤，只保留 init、Read 路径和 result；没有改变题面、模型、system prompt 或采样设置。

| 题目 | 模型 | session | 时长 | Read | 终态 |
| --- | --- | --- | ---: | --- | --- |
| S02 | `opencode-go/deepseek-v4-flash` | `c60aff36-16a3-4ade-b92a-3d86873a2e9e` | 188.320秒 | SKILL、information-selection、formulaic-language、task-route-cards | success，exit 0 |
| S04 | `ollama-cloud/deepseek-v4-flash:0731` | `89aff85d-349e-4f7e-a45c-c1ddd267ce17` | 119.438秒 | SKILL、information-selection、formulaic-language、genre-routing、genre-playbooks | success，exit 0 |
| S06 | `alibaba-token-plan-2/deepseek-v4-flash-0731` | `5825c7af-a642-4ba4-823a-bfe59f592b7c` | 288.784秒 | SKILL、information-selection、formulaic-language | success，exit 0 |

三题均为 `apiKeySource=none`、Read-only、0 web search、0 retry。第一波无效稿不进入质量结论。

## 有效稿固定值

下表字数按删除全部空白字符后计算，稿件原文见 `drafts/`。

| 题目 | 非空白字符 | 用户区间 | SHA-256 |
| --- | ---: | --- | --- |
| S02 | 194 | 350—430 | `a1a5b091cfdd44152c9e3016f8793803f3304ea46667e6e08f259544241259b9` |
| S04 | 322 | 320—400 | `05479b1e576bbf43f6c614bd5384cbe5ee9992178cf4d88420164cf224fdcb38` |
| S06 | 192 | 180—240 | `db5fc7a2e8b9e6accdc06f6acb6f867bba843c0446ad288ad37f00643522ff73` |
