# Candidate A 三稿盲审解盲与裁决

日期：2026-07-15

四份裁判原文已先在 `df9add8` 提交。本文件随后公开来源映射并按预设门槛裁决。

## 来源映射

### gpt-5.6-luna 稿件包

| 任务 | A | B | C |
|---|---|---|---|
| T01 | candidate A | strict no-Skill | current 1.5.14 |
| T02 | current 1.5.14 | candidate A | strict no-Skill |
| T03 | strict no-Skill | current 1.5.14 | candidate A |
| T04 | candidate A | current 1.5.14 | strict no-Skill |

### gpt-5.6-terra 稿件包

| 任务 | A | B | C |
|---|---|---|---|
| T01 | strict no-Skill | candidate A | current 1.5.14 |
| T02 | candidate A | current 1.5.14 | strict no-Skill |
| T03 | current 1.5.14 | strict no-Skill | candidate A |
| T04 | strict no-Skill | current 1.5.14 | candidate A |

## 解盲结果

### Candidate A 与 strict no-Skill

| 同模型任务 | 异模型裁判 | Sol 裁判 | 两名裁判共识 |
|---|---|---|---|
| Luna T01 | candidate > no-Skill | candidate > no-Skill | candidate 在前 |
| Luna T02 | candidate > no-Skill | candidate > no-Skill | candidate 在前 |
| Luna T03 | candidate > no-Skill | candidate > no-Skill | candidate 在前 |
| Luna T04 | candidate > no-Skill | candidate > no-Skill | candidate 在前 |
| Terra T01 | no-Skill > candidate | candidate > no-Skill | 分歧 |
| Terra T02 | candidate > no-Skill | candidate > no-Skill | candidate 在前 |
| Terra T03 | candidate > no-Skill | candidate > no-Skill | candidate 在前 |
| Terra T04 | candidate > no-Skill | candidate > no-Skill | candidate 在前 |

两名裁判在 7/8 个固定同模型任务中一致把 candidate 排在 strict no-Skill 前，1/8 分歧。该数字只表示本轮排序共识，不等同 7 次“全面领先”：四份报告均明确多数组合只是小胜，并且存在硬边界问题。因此本轮不能据此宣传 80%—90% 场景领先。

### Candidate A 与 current 1.5.14

- 两名裁判一致把 candidate 排在 current 前：Luna T01、T02、T03，共 3/8。
- 两名裁判一致把 current 排在 candidate 前：Terra T04，共 1/8。
- 裁判分歧：Luna T04、Terra T01、T02、T03，共 4/8。

Candidate A 没有形成相对 current 1.5.14 的稳定质量提升。

## 硬回退复核

以下问题均由两名裁判独立指出，并可在原稿复核：

1. Luna T04 candidate 遗漏用户明确给出的会议地点“第二会议室”。这是会议纪要要素和 Prompt 遵循回退。
2. Terra T01 candidate 写成“总馆及5个分馆、政务服务中心分馆”，与材料中的 6 个点位形成数量表达冲突。
3. Terra T04 candidate 把材料中的报告、建议和未决事项扩写为“会议认为”“会议要求”“会议明确”，并细化两部门数据职责。异模型裁判判 WARN，Sol 裁判判 FAIL；current 1.5.14 在该题更稳。

以上任一项已足以触发预设的零硬回退门槛。篇幅长短没有用于裁决质量；只在用户明确给出范围时记录为 Prompt 遵循项。

## 裁决

Candidate A 方向有正向信号：解除“宁可短写”后，相对 strict no-Skill 的信息利用和整体排序明显改善。但本候选出现事实、会议纪要要素和结论强度回退，且相对 current 1.5.14 不稳定，裁决为 **REJECT**。

本候选不进入 Sol writer 和 H01—H12 发布级留出矩阵。先撤回产品修改，再从 1.5.14 基线设计更窄的新候选；后续仍以同模型 strict no-Skill、current 基线和零硬回退验证。

## 五提交检查点

自上次检查点后的候选产品、自然 writer、匿名包、裁判原文和本次解盲共形成五个提交。轻量 review、固定 1.5.13 确定性消融、全量回归、Promptfoo smoke、真实同模型三方盲审和 Sol 复核均已完成。工程回归通过不能覆盖本次真实写稿硬回退，故按真实写稿门槛拒绝候选。
