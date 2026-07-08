# 弱模型真实复测失败记录（回退本轮 prompt 补丁）

日期：2026-07-08

起点：`982a55b test: record six-prompt availability and url review guard`

本轮尝试：在 `SKILL.md`、`references/workflow.md`、`references/review-checklist.md` 中用最小软性提示补强三类上一轮共性问题：

- 已给发送人、落款、成文日期和定点报送时间时，不写“略”“日期略”，不把定点时间改成截止时间。
- 活动、赛事、节假日提醒类通知不扩展值班值守、巡查记录、责任处理等执行链条。
- 稀疏排查材料只写已给结论，不补检查方法、技术路径、后续管理或日常检查机制。

同时新增确定性 P107/P108。工程验证曾通过：

- `python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary`：43 tests OK
- `python -m unittest discover -s tests`：107 tests OK
- `git diff --check`：通过，仅 LF/CRLF 提示
- `python tools/run_real_prompt_ablation.py --baseline-root output\release-baselines\982a55b --baseline-label baseline-982a55b --current-root . --out output\real-prompt-vs-982a55b-weak-format-sparse-fix`
  - baseline `106/108`
  - current `108/108`

说明：上述消融不调用 LLM，只能证明确定性规则支撑，不能证明真实写作质量。

## 真实复测

writer A：`gpt-5.3-codex-spark`，low reasoning，加载当前 skill。

writer B：`gpt-5.5`，low reasoning，加载当前 skill。

verifier：独立上下文 `gpt-5.5`，low reasoning，只看 prompt、两个 writer 输出和网页事实摘要。

复测仍使用上一轮 6 个真实 prompt：

1. 采购 5090 用于 35B 小模型、版慎通、harness、脱敏、OCR、文生图。
2. 微博发送量、阅读量、粉丝数、增长率、高峰时段、本地新闻弱和下一步投放。
3. 东方财富转载工信部 Claude Code 风险提示，改成本单位通知，排查具体版本，发现删除，无也报无，7 月 10 日 15:00 钉钉发送至技术应用部，落款二十一世纪出版社。
4. 新华网气象文章改成上下班路上注意防范通知，落款二十一世纪出版社集团办公室。
5. 6 月 11 日至 7 月 19 日世界杯期间禁止赌球、强化考勤、但祝观赛愉快的通知，发送人红星出版社办公室，发给各部门、下属子公司。
6. 已排查 OpenClaw 安装情况报告，未发现本单位安装 OpenClaw 及任何小龙虾变种软件；报告对象江西出版集团，发送方红星出版社。

## 独立 verifier 结论

总体：WARN，不达到可发布质量。

逐项结论：

| Prompt | 弱模型 | 强模型 |
| --- | --- | --- |
| 1 采购 5090 情况说明 | PASS | PASS |
| 2 微博情况说明 | PASS | PASS |
| 3 Claude Code 排查通知 | WARN | WARN |
| 4 暴雨通勤防范通知 | WARN | WARN |
| 5 世界杯纪律通知 | WARN | PASS |
| 6 OpenClaw 排查报告 | FAIL | PASS |

关键问题：

- 弱模型 Prompt 3 把“发现请删除”扩成“删除或升级”，且追加来源说明。
- 弱模型 Prompt 4 继续补入“居家办公或延迟出行”“涉户外作业同事”“单位道路值班联系人”等用户和网页摘要未给内容。
- 弱模型 Prompt 5 未明确写入“禁止赌球”，并补入“落实情况纳入日报”等新增管理要求。
- 弱模型 Prompt 6 继续补造“全量终端检查”“可执行文件、服务项与客户端残留”“最新巡检清单和本地应用目录核对”“未发现安全配置异常”等未给事实。
- 强模型仍在 Prompt 3、4 追加来源说明，并在 Prompt 3 补写网页摘要未提供的“回传用户地域、身份标识”等细节。

两次以上共性问题：

1. 事实外扩仍反复出现：弱模型 Prompt 4、6，强模型 Prompt 3 也有轻微补事实。
2. 附加说明/来源说明残留：弱模型 Prompt 3、4，强模型 Prompt 3、4。
3. 正式格式不稳或任务重点弱化：弱模型 Prompt 3、4、5、6。
4. 把建议、排查或提醒写成额外管理动作：弱模型 Prompt 4、5、6。

## 处理决定

本轮 prompt 补丁虽然让确定性消融通过，但没有形成真实写作稳定改善。按“有问题就回退”的 loop 要求，已回退本轮未提交的 prompt/reference/P107/P108 改动，工作区恢复到 `982a55b` 后只保留本失败证据文件。

下一轮不建议继续在入口文件叠加更长的负面清单。更可取的方向是先做二次修改链路测试：让弱模型对失败稿执行“只删未给事实、保留已给要点、只输出正文”的自然语言二次修改，看二次修改是否比继续加规则更稳定。
