# current vs 1.5.2 真实写稿回退判定

日期：2026-07-08

目的：用户要求在多轮候选修改后与 `1.5.2` 发布基线做真实写稿对比，判断是否造成边界漂移和功能性回退。

## 方法

- baseline：`v1.5.2`，commit `70efc9ce74fe956497b5044ee14f60e2b94c5e55`。
- current：测试时 HEAD `fd4066a22e381ff93ae3e2fd3c0b5c0eff4692b5`。
- writer：同一弱模型 `gpt-5.3-codex-spark`，低思考。
- prompts：6 个真实场景，覆盖电脑采购说明、微博情况说明、Claude Code URL 改通知、气象 URL 改通知、世界杯期间通知、OpenClaw 排查报告。
- verifier：独立 `gpt-5.5`，低思考，只看 prompt 与两组输出，判定是否回退。

## 确定性消融

候选状态下：

- `baseline-1.5.2`：`84/106`。
- `current`：`106/106`。

该结果只说明 deterministic 用例覆盖更多，不代表真实写稿质量改善。

## 真实写稿 verifier 结论

| 场景 | 谁更好 | 判定 |
| --- | --- | --- |
| P1 电脑采购情况说明 | baseline 略好 | current 仍补事实，并把情况说明推向“请领导审议”的请示口径。 |
| P2 微博情况说明 | 持平 | 两者都补运营机制和分析结论，current 没有明显改善。 |
| P3 URL 改通知 | baseline 略好 | current 范围外扩更重，仍未落实“如有请删除”，仍把定点时间写成截止时间。 |
| P4 气象 URL 改通知 | baseline 更好 | current 落款日期缺失，格式完整性下降，并补未给安排。 |
| P5 世界杯期间通知 | baseline 略好 | current 外扩少于 baseline 的值班链条，但落款日期缺失，正式通知格式回退。 |
| P6 OpenClaw 排查报告 | baseline 略好 | current 事实外扩仍严重，并新增“风险可控”“附件清单”等未给结论和材料。 |

总体结论：`current` 相对 `1.5.2` 没有改进，存在轻度功能性回退。

## 处理决定

按“有问题就回退”的目标要求，已将影响 skill 行为、镜像入口、lint、sync、README 和确定性测试门槛的候选改动恢复到 `v1.5.2` 内容。

回退后验证：

- 产品路径与 `v1.5.2` 无差异。
- `git diff --check` 通过。
- `python -m unittest discover -s tests`：105 tests OK。

后续所有新修改必须重新以 `1.5.2` 作为基线，先做真实写稿 A/B，再判断是否进入发布候选。
