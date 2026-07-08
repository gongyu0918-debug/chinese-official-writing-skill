# delivery-fact-check 候选失败记录（2026-07-08）

## 目标

本轮尝试用最小 prompt/reference 修复两个弱模型真实写作风险：

- URL 改写时漏掉网页中的具体版本、日期、风险等事实锚点。
- 已排查/已核查类报告在用户只给结论时，自动补造排查范围、运行痕迹和后续管理动作。

## 实施内容

- 新增 `references/delivery-fact-check.md` 候选 reference。
- 在 `SKILL.md` 中增加定稿前引用提示。
- 新增确定性消融用例 P102-P103。
- 后续又在主入口补一句“已排查、已核查或已检查类报告若用户只给结论，标题写清事项，正文一段短写，不补根据统一安排、排查范围、运行痕迹、后续管理或日常检查”。

## 工程验证

- `python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary`：43 tests OK。
- `python -m unittest discover -s tests`：107 tests OK。
- `git diff --check`：无空白错误，仅 Windows 换行提示。
- `tools/run_real_prompt_ablation.py --baseline-root output\release-baselines\pre-delivery-check-28f141f ...`：baseline 101/103，current 103/103。

以上只能证明确定性规则存在，不代表真实写稿质量通过。

## 真实写作复测

使用 `gpt-5.4-mini`、低思考、隔离 writer subagent，按真实用户 prompt 写稿；再用独立 verifier 复核。

### 第一轮 6 prompt

- P1 电脑采购说明：PASS，后来复测去掉了“前期测试表明”的既成事实外扩。
- P2 微博情况说明：PASS/WARN，数据覆盖完整，但有轻微评价性泛化。
- P3 Claude Code 网页改通知：第一轮由 FAIL 改到 PASS，能保留 `2.1.91 至 2.1.196`。
- P4 气象网页改通勤提醒：WARN，仍泛化为“近日部分地区”，未稳定保留预警发布时间、预报时段、局地特大暴雨、小时雨量等事实锚点。
- P5 世界杯期间禁止赌球通知：WARN，核心要求覆盖，但仍有格式缺口和机关化措辞。
- P6 OpenClaw 已排查报告：FAIL，仍补造“根据统一安排”“相关办公终端及可疑安装项”“运行痕迹”“后续加强终端软件管理和日常检查”等未给事实。

独立 verifier 结论：保留继续小修，不可作为发布候选。

### targeted 复测 P3/P6

再次使用同模型、低思考、同类 prompt：

- P3 又退回失败：写成“Claude Code 相关版本”，未保留 `2.1.91 至 2.1.196`，并补造“办公电脑、工作终端及相关设备”“报送排查范围、处理情况”等未给字段。
- P6 仍失败：写入“按照有关要求”“办公终端及相关设备安装情况”，仍未压住稀疏事实外扩。

## 结论

该候选虽然在确定性消融中通过，并在单次 P3 样本中出现改善，但真实弱模型复测不稳定，P6 核心风险未解决，P3 也不能稳定保留 URL 事实锚点。因此本轮候选不适合发布，也不应继续在当前形态上叠加 prompt。

处理决定：回退本轮候选代码和镜像，只保留本失败记录，下一轮应重新设计更小、更可执行的方案，而不是继续堆长规则。
