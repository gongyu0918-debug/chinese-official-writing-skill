# 当前可用程度真实写稿测试（6 个 prompt）

日期：2026-07-08

目的：按用户要求优先测试 6 个真实 prompt，观察当前 skill 在弱模型和强模型下的文种判断、要点置入、联网事实处理、事实边界、Markdown 残留和完成度。

## 测试设置

- 弱模型 writer：`gpt-5.3-codex-spark`，low reasoning。
- 强模型 writer：`gpt-5.5`，low reasoning。
- 两个 writer 均要求只读仓库，先读取 canonical `chinese-official-writing/SKILL.md`，按需读取 references。
- 独立 verifier：`gpt-5.5`，low reasoning。只看原 prompt 与两组稿件，不参与写作，不修改仓库。
- 联网来源：
  - 东方财富转载工信部风险提示：Claude Code 2.1.91 至 2.1.196 版本存在安全后门隐患，建议排查、卸载或升级。
  - 新华网转载中国天气网暴雨橙色预警：7月8日08时至9日08时多地大到暴雨，伴随短时强降水、雷暴大风等风险。

## 6 个 prompt

1. 电脑采购情况说明：采购 5090，用于 35B 小模型测试、版慎通、校准、harness、敏感资料脱敏、OCR、文生图等。
2. 微博情况说明：日均 200 条、日均阅读量 100 万次、粉丝 500 万、较上月增长 5%，晚间 9 时至 11 时为高峰，本地新闻流量较弱。
3. 将 Claude Code 风险提示改为二十一世纪出版社内部通知，要求员工排查相关版本，有则删除，无也反馈无，7月10日15:00 钉钉报技术应用部，落款日期为当天。
4. 将气象文章改为上下班路上注意防范通知，落款二十一世纪出版社集团办公室。
5. 写 6月11日至7月19日世界杯期间禁止赌球、强化考勤但祝观赛愉快的通知，红星出版社办公室发给各部门、下属子公司。
6. 写已排查 OpenClaw 安装情况报告，未发现 OpenClaw 及任何小龙虾变种软件，报告对象江西出版集团，发送方红星出版社。

## verifier 结论

| Prompt | 弱模型 | 强模型 |
| --- | --- | --- |
| 1. 电脑采购情况说明 | WARN | PASS |
| 2. 微博情况说明 | WARN | PASS |
| 3. Claude Code 版本排查通知 | FAIL | PASS |
| 4. 气象文章改上下班防范通知 | WARN | PASS |
| 5. 世界杯期间禁止赌球通知 | WARN | PASS |
| 6. OpenClaw 排查报告 | FAIL | PASS |

## 共性问题

1. 弱模型 Markdown 残留明显，包括 `**` 加粗、项目符号、行尾双空格和正式稿压缩成一行。
2. 弱模型容易补造流程、责任、台账、巡检方式、管理要求等未给事实。
3. 弱模型正式公文格式不稳，常缺主送或落款，或加入“示例”“报送人”“发布”等不合适字段。
4. 弱模型会把“情况说明/通知/报告”写成半结构化提纲，正文完成度不足。
5. 强模型整体可用程度明显高于弱模型，6 个 prompt 均为 PASS；仍有轻微润色性扩展，但未构成主要阻断。

## 当前判断

- 当前 skill 对强模型低思考写作基本可用，文种、要点置入和事实边界总体稳定。
- 弱模型低思考下仍不适合直接交付正式稿，建议配合二次修订模式或强模型复核。
- 本轮同步补充了低风险格式检测：`markdown-line-break`，仅在 `--format` 下作为 low 级提示，不作为硬阻断。

## 同步验证

- `python -m unittest discover -s tests`：107 tests OK。
- `python .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\pre-delivery-repair-0afb4fd --baseline-label baseline-0afb4fd --current-root . --out output\real-prompt-vs-0afb4fd-markdown-line-break`：baseline 95/97，current 97/97。
- `python C:\Users\2\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：Skill is valid。
- `npm run eval:official-writing:smoke`：20/20 passed，judge consistency 1.0。首次因 `python` 不在 PATH 失败，补 PATH 后遇到沙盒网络拦截 npm registry，经授权联网重跑通过。
- `git diff --check`：通过。
