# R2 技术记录

R2 仅执行 `r2-amendment.md` 点名的 S01、S03、S05。三题均取得一个完整 `result`，没有再次复跑。

| 题目 | 模型 | session | 时长 | Read | 终态 |
| --- | --- | --- | ---: | --- | --- |
| S01 | `opencode-go/deepseek-v4-flash` | `9e042471-6703-42b4-a1ae-53a388f2f956` | 284.876秒 | SKILL、information-selection、formulaic-language、genre-routing、genre-playbook-work-summary | success，exit 0 |
| S03 | `ollama-cloud/deepseek-v4-flash:0731` | `bc865e4d-7f09-4d44-99db-ce09db339db3` | 267.032秒 | SKILL、information-selection、formulaic-language、genre-routing、genre-playbooks | success，exit 0 |
| S05 | `alibaba-token-plan-2/deepseek-v4-flash-0731` | `7497794d-f4d8-4cb0-8f71-f4e7b47bf4e0` | 408.932秒 | SKILL、information-selection、formulaic-language、genre-playbooks | success，exit 0 |

三题均为精确模型、`apiKeySource=none`、Read-only、0 web search、0 retry、无插件、无 Hook；流记录没有无效 JSON 行。

## R2 稿件固定值

| 题目 | 非空白字符 | 用户区间 | SHA-256 |
| --- | ---: | --- | --- |
| S01 | 302 | 300—380 | `eaa34a98e8fd7473b6c2f4be74b8701f04f0fe872efe1fc648dfe15678d1b0e7` |
| S03 | 330 | 320—400 | `bdbb4a36cfdadebe0c11564c34d5a7d263c0c248185167e558051b5b4bc61a5d` |
| S05 | 318 | 300—380 | `0289fa418542c2e1474ed9a8f32f3c2e0aaf5d4328cf82a3e1f1b73d6eaf88cf` |
