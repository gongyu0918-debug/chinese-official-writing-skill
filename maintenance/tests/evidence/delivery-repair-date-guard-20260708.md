# 二次交付修订日期边界复测

日期：2026-07-08

目的：在上一轮弱模型首稿仍有 Markdown 残留、事实外扩和未给日期补入落款的问题后，验证“交付修订模式”是否能作为二次修改链路，把坏稿修成可交付正文。

## 最小修复

只在 `references/review-checklist.md` 的“交付修订模式”中补一句：

> 用户要求只保留已给事实时，未给日期不得用当前日期补入落款，可在正文外短列待确认。

本轮未修改起草默认逻辑，未新增硬阶段、硬阻断、脚本清洗或默认联网。

## 确定性验证

- 新增 P098：二次修订时用户要求只保留已给事实，原始要求未给报告日期，不得用当前日期补入落款。
- 消融基线：`4432fdd`
- 命令：`python .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\pre-audit-guard-4432fdd --baseline-label baseline-4432fdd --current-root . --out output\real-prompt-vs-4432fdd-delivery-date-guard`
- 结果：baseline `97/98`，current `98/98`；baseline 只在新增 P098 失败。

## 真实二次修订测试

原计划使用 `gpt-5.3-codex-spark low` 复测，但该模型触发使用限制，未产出稿件。改用 `gpt-5.4-mini low` 作为小模型复测。

### 二次修改请求

用户将上一版坏稿发回，指出：

- 有 Markdown 加粗、横线、行尾空格。
- Claude Code 通知漏了受影响版本号。
- OpenClaw 报告补了“开发与办公环境”“报告人”和未给日期。
- 要求修干净成能发版本，只保留给过的事实，不解释过程。

### 小模型修订输出摘要

- Claude Code 通知：补回 `2.1.91 至 2.1.196`，保留 `7月10日15:00`、钉钉、技术应用部、二十一世纪出版社、`2026年7月8日`。
- OpenClaw 报告：删除“报告人”“开发与办公环境”和日期，只保留“未发现本单位安装有 OpenClaw 及其任何小龙虾变种软件”、主送江西出版集团、落款红星出版社。
- 未再出现 Markdown 加粗、横线或行尾双空格。

### 独立 verifier

Verifier：`gpt-5.5 low`

结论：

| 稿件 | 判定 | 说明 |
| --- | --- | --- |
| Claude Code 排查通知 | PASS | 格式干净，版本号、报送时间、渠道、落款日期均落实，未见新增实质事实。 |
| OpenClaw 安装情况报告 | PASS | 删除未给的报告人、范围、日期和技术细项；未给报告日期时不补日期是正确处理。 |

总体结论：二次修订链路本轮可交付，无发布阻断。剩余风险是 OpenClaw 报告正式报送前仍需用户按内部签发流程确认是否补成文日期。

## 当前判断

- 弱模型首稿直出仍不稳定，不宜直接宣称发布就绪。
- 二次交付修订链路在本轮样本中能修掉 Markdown 残留、事实外扩和未给日期补入落款问题。
- 该修复是局部、软性、低膨胀的，可保留进入后续发布候选验证。

## 提交前验证

- `python -m unittest tests.test_real_prompt_ablation tests.test_review_regressions`：45 tests OK。
- `python -m unittest discover -s tests`：107 tests OK。
- `python C:\Users\2\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：Skill is valid。
- `git diff --check`：通过。
- `npm run eval:official-writing:smoke`：首次因沙盒网络拦截 npm registry 失败；经授权联网重跑后 20/20 passed，judge consistency 1.0。
