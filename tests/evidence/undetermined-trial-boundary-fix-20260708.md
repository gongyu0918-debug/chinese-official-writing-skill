# 2026-07-08 未定试用/拟评估口径最小修复记录

## 背景

在 `8fe0a88` 后继续做真实写作测试时，独立 verifier 发现一个达到修复门槛的共性问题：用户明确说明“准备评估、尚未试用、不要写成已采购/已部署/已形成结果”时，强弱模型都会把材料收束成带有试用效果、推进条件或后续推进安排的正式链条。

典型样本：

- 稿件审校工具只是准备评估，但弱模型写“结合实际试用效果”，强模型写“继续推进必要”。
- SmartAudit 尚未正式使用、试用范围/时间/费用都没定，但强弱模型均出现“推进”“后续安排”等口径。

## 最小修复

本轮只做 prompt/reference 层软性约束，不新增硬 lint、不新增脚本、不增加默认阻断。

修改内容：

- `SKILL.md`：在既有“考察、评估、建议、拟测试”口径规则旁补一句，用户明确强调未定、准备评估、尚未试用或不要写成结果时，不补写试用效果、推进条件、实施安排或后续推进链条；这类稿件通常不写“下一步”段，确需收尾时只写“相关事项尚待明确”或“待明确后再研判”。
- `references/workflow.md`：同步同一条起草口径，避免只在入口出现。
- `references/review-checklist.md`：增加“未定事项口径”复核项。
- `tools/run_real_prompt_ablation.py`：新增 P101。
- `tests/test_real_prompt_ablation.py`：增加 P101 规则存在性断言。
- 通过 `tools/sync_adapters.py` 同步 `skills/`、`.agents/`、`.qwen/`、`hermes/`、`openclaw/` 等镜像。

## 确定性验证

定向测试：

- `python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary`
- 结果：43 tests OK。

基线消融：

- baseline：`8fe0a88 test: record second-round repair follow-up`
- 命令：`python tools/run_real_prompt_ablation.py --baseline-root output\release-baselines\pre-undetermined-chain-8fe0a88 --baseline-label baseline-8fe0a88 --current-root . --out output\real-prompt-vs-8fe0a88-undetermined-chain-direct`
- 结果：baseline `100/101`，current `101/101`；baseline 只失败新增 P101。

## 真实写稿复测

### 第一轮复测

第一轮修复后，弱模型和强模型仍在 SmartAudit 场景写出“按程序推进相关工作”等收尾。独立 verifier 判定为“部分有效”，建议保留方向但继续小收紧。

### 第二轮复测

第二轮收紧后，使用同类真实 prompt 复测：

1. TestPlug 排查通知，强调不是已经排查完、未给单位不要补。
2. 新稿件审校工具情况说明，准备评估、未定、只知道支持 Word/PDF。
3. 世界杯提醒通知，要求柔和并保留祝愿。
4. SmartAudit 报告，尚未正式使用，只准备小范围试用，范围/时间/费用未定。

独立 verifier 结论：

| Prompt | 弱模型替代 `gpt-5.4-mini low` | 强模型 `gpt-5.5 low` | 主要依据 |
| --- | --- | --- | --- |
| S1 TestPlug 通知 | PASS | WARN | 弱模型准确写成自行排查，未补单位；强模型方向正确，但“经排查已安装”略像结果链条节点。 |
| S2 审校工具情况说明 | PASS | PASS | 两组都明确拟评估、尚未确定、准备阶段，未写成采购、部署或已形成结论。 |
| S3 世界杯提醒 | WARN | WARN | 两组保留祝愿并柔化语气；弱模型格式略简，强模型自动补当前日期。 |
| S4 SmartAudit 报告 | PASS | WARN | 弱模型明确未正式使用、未定范围/时间/费用、未形成结果；强模型未写成已上线或完成，但补了当天日期并轻微增加“审慎研判”管理表述。 |

## 判断

修复 **部分有效**，值得保留：未定、尚未试用材料没有再被明显写成完整推进链条，弱模型替代在 S2/S4 表现明显改善。

但当前候选仍不能直接发布：强模型仍有自动补当前日期、轻微管理表述扩展的 WARN；弱模型在柔和提醒类通知上格式仍偏简。下一轮如果继续推进，应继续覆盖“未定事项、未试用、只提醒、不要补单位/日期”场景，不应把本轮包装成发布通过。
