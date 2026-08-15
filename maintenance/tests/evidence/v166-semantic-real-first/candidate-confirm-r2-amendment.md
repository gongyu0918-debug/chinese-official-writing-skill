# C02 产品修复后复测

C02 首次候选直连稿的目标功能通过，但新增`今年`这一未给时间事实。产品提交 `ef881458` 已增加通用时间锚规则，并把20类材料单一任务收窄为直接叶。

本轮只复测 C02，一次调用：`ollama-cloud/deepseek-v4-flash:0731`、max、1200秒、0 retry、独立环境、Read-only、无 Hook、无 web search。题面逐字不变，system 仍只要求读取当前 SKILL 并按实际路由写稿，不注入修复内容。

通过条件：

- 不新增`今年`、`本年`、具体年份或其他相对时间锚；
- `我们将继续`等一般延续由演讲人或服务队承担，不新增具体活动、期限、程序或已实现成效；
- 350—430字，事实、状态、文种和直接使用通过；
- 必须读取 SKILL、information-selection 和 formulaic-language；不得读取 workflow、genre-routing、整套复核清单或其他与单一演讲词无关的长 reference。
