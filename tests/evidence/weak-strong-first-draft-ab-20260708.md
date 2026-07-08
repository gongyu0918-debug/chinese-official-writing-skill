# 2026-07-08 强弱模型真实首稿可用度 A/B

## 测试目的

在当前本地候选 `0caf2db fix: tighten second-round repair boundaries` 上，优先复测用户指定的 6 个真实 prompt，判断当前 skill 在弱模型和强模型首稿生成中的实际可用程度。此轮只读写作测试，不修改 skill 规则，不做发布结论包装。

## 方法

- 写作 agent：
  - weak：`gpt-5.3-codex-spark`，`reasoning_effort=low`
  - strong：`gpt-5.5`，`reasoning_effort=low`
- 每个写作 agent 均要求使用 `chinese-official-writing` skill，只输出可用成稿，不解释过程。
- 链接类 prompt 由主上下文先打开公开链接核对事实摘录，再把“原 prompt + 成稿 + 链接事实摘录”交给独立 verifier。
- verifier：`gpt-5.5`，`reasoning_effort=low`，只看原 prompt 和成稿，按 `PASS/WARN/FAIL` 判断，不读取历史结论。

## Prompt 覆盖

1. 电脑采购情况说明：RTX 5090、35B 小模型、版慎通、harness、敏感资料脱敏、OCR 和文生图辅助。
2. 微博情况说明：日均发送量、阅读量、粉丝量、增长率、阅读高峰、本地新闻偏弱和下一步投放。
3. Claude Code 安全风险网页改本单位通知：要求排查 2.1.91 至 2.1.196，删除或汇报无，7月10日15:00 钉钉报技术应用部，日期写今天。
4. 新华网暴雨橙色预警网页改上下班防范提醒，落款二十一世纪出版社集团办公室。
5. 世界杯期间禁止赌球、强化考勤但祝观赛愉快的通知，红星出版社办公室发给各部门、下属子公司。
6. OpenClaw 安装情况报告：未发现本单位安装 OpenClaw 及任何小龙虾变种软件，报江西出版集团，发送方红星出版社。

## Verifier 逐项结论

| Prompt | weak 结论 | strong 结论 | 主要依据 |
|---|---|---|---|
| P1 电脑采购情况说明 | WARN | PASS | weak 要点基本进入正文，但结尾出现“此致 / 说明。”格式错误，并把情况说明推向“建议尽快采购”；strong 基本可用。 |
| P2 微博情况说明 | WARN | PASS | weak 补出“流量占比与互动效率明显低于热点类内容”“标题、话题和首屏导语优化”等未给事实或措施；strong 简洁稳。 |
| P3 Claude Code 通知 | WARN | WARN | weak 有 `**` 加粗、补项目组/测试环境/临时开发机/主机数量/技术管理中心等；strong 核心可用，但把技术应用部推断成落款，并补异常外联等要求。 |
| P4 暴雨通勤提醒 | FAIL | PASS | weak 标题 Markdown 加粗、搬运地区细节过重、缺日期，并补值班人员和应急联络；strong 场景转换和落款日期较稳。 |
| P5 世界杯通知 | WARN | PASS | weak 核心要求覆盖，但补“重点岗位值班留痕”“宣传、执行与日常巡查”等执行链条；strong 较稳。 |
| P6 OpenClaw 报告 | FAIL | WARN | weak 有 Markdown 加粗、标题位置不规范、补系统目录/运行环境/可识别线索和“（送出）”；strong 内容克制但缺成文日期。 |

## 三次以上共性问题

1. Markdown 残留仍在弱模型首稿中稳定出现：P3 weak、P4 weak、P6 weak 均出现 `**` 加粗或 Markdown 标题痕迹。
2. 事实或措施外扩仍未稳定解决：P2 weak、P3 weak、P3 strong、P4 weak、P5 weak、P6 weak 均有不同程度外扩。
3. 正式格式完整性不稳：P1 weak 结尾错误，P4 weak 缺日期，P6 weak 落款错误，P6 strong 缺日期。

## 发布判断

独立 verifier 结论：当前版本不适合发布为稳定版。strong 模型整体可用度较高，多数样本可直接进入二次修改；weak 模型在 Markdown 残留、事实外扩、落款日期和格式完整性上仍有稳定风险，且已经形成三次以上共性问题。

本轮判断口径：当前 skill “可辅助起草，但不宜作为稳定版发布口径”。此轮没有继续追加 prompt 规则，避免在 `SKILL.md` 中继续堆叠补丁式限制。

## 后续建议

- 不建议继续用单句规则修补弱模型首稿；前序多轮已显示类似 prompt 限制容易局部改善但不能稳定解决首稿质量。
- 后续如继续推进发布，应优先验证二次修改链路、外部 final-draft inspection 或更小的交付前检查机制，但不能变成硬阻断。
- 任何新修复都必须重新跑上一基线消融、强弱模型真实写稿 A/B 和独立 verifier。
