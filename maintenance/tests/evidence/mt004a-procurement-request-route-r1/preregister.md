# MT-004a-PROCUREMENT-REQUEST-ROUTE-R1 预注册

## 观察与目标

QwenWork 静态包路径的一份无字数限制采购申请已形成可用正文，但实际读取入口及6个 references，共52029字节。`genre-playbook-request.md` 已说明单项采购申请可由一至两个自然段完成，末尾仍无条件补读 `argument-chains.md` 与 `formal-addressing.md`；主入口又默认进入 `proofreading-checklist.md` 与 `final-review-layers.md`。

本原子只验证：材料单一、文种明确、无复杂模板/附件/多品类/详细论证要求的采购申请，在 `information-selection.md` 与 `genre-playbook-request.md` 已覆盖任务后，能否停止继续读取上述四个通用页。不得修改 description、原因/影响推断边界、Hook、脚本或其他文种叶。

## 先复现后候选

1. 既有 Alibaba Token Plan 2 trace 只算第一份当前基线观察。
2. 先用 Alibaba Token Plan 1、全新简单采购申请复现。只有它也读取请示/申请叶及至少三份上述通用页，才实现候选。
3. 候选只改 `references/genre-playbook-request.md` 的一个停止条件；不改 `SKILL.md`。

## 真实 A/B

- 五条低成本路线，reasoning effort `max`；技术失败不计质量票，不由昂贵模型补写。
- 三题：简单采购申请目标题、含多品类与技术附件的复杂采购请示控制题、普通情况报告控制题。
- 先后臂交错；每个 arm 为固定提交、隔离项目级 Skill、用户级同名 Skill 禁用、只读、ephemeral、无 Hook、零重试。
- 合理的一层原因、目的、即时作用、低强度预期、材料与常识支持的总结和条件性判断不算外扩。材料外数值、用途、程序、责任、日期、完成承诺、状态升级才算硬回退。
- 只有与候选 diff 有关的缺读、串叶、正文功能缺失或候选独有硬回退才否决；模型独有文风差异不归因候选。

## 准入

- 至少3/5技术有效目标配对中，Candidate 实际读取 `information-selection.md` 和 `genre-playbook-request.md`，不读取 `argument-chains.md`、`formal-addressing.md`、`proofreading-checklist.md`、`final-review-layers.md`，且总读取字节下降。
- 目标稿完整保留原因事实、申请事项、数量金额、资金来源、当前状态和请批功能；不得因减载变得功能性过薄。
- 复杂采购控制仍读取必要的 `workflow.md`、`handling-elements.md` 和 `argument-chains.md`；报告控制不串入申请叶。
- 任一候选独有事实、状态、程序、文种或直接可用性硬回退，先拆样本定位；若来自停止条件且最小修复不能消除，拒绝候选并恢复产品。

## 终态

通过则补直接镜像/边界反控后形成可合并候选；不通过则标 `REJECTED` 或 `TERMINATED`，不留中间状态，不用更多门禁替代写稿。
