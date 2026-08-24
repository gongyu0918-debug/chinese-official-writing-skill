# OC-003-R3F 专项只审路由最小修复预登记

日期：2026-08-25。

## 触发原因

R3D 同模型 A/B 证明候选不读取整份 `ai-compute-docs.md` 时仍可完成点名完整性审稿，但专项审稿仍先加载通用 `review-checklist.md` 和 `anti-ai-patterns.md`；后者又提示转读 AI 算力页。Alibaba Token Plan 1 因此重新读入长页并扩展比较路径、第三方和安全项目。Ollama 未读长页，但仍把“补同口径材料”具体化为厂商数量和验收角色。

## 唯一候选动作

1. `SKILL.md`：既有可研摘要只做用户点名完整性核对、且未要求语言/格式/AI 味综合审稿时，直接使用可研细查叶，不自动叠加通用审稿页和去 AI 味页。
2. `genre-checklist-feasibility-review.md`：正面允许按点名维度列出指标、费用和依据类别并说明决策影响；同时给出成本比较与验收主体的窄写法，避免把合理推断与材料外数量、路径、主体或程序混淆。

不改 description、通用事实边界、Hook、adapter、版本号或其他文种。

## 真实审稿复测

沿用 `natural-prompt.md`，候选只复跑两个曾暴露目标问题的便宜模型路线：

- Ollama DeepSeek V4 Flash 0731；
- Alibaba Token Plan DeepSeek V4 Flash 0731。

准入要求：

- 读取当前 checkout 的 `SKILL.md` 与 `genre-checklist-feasibility-review.md`，不读取 `review-checklist.md`、`anti-ai-patterns.md` 或 `ai-compute-docs.md`；
- 保留算术、实际/抽样/假设性质和“尚未形成采购决定”状态；
- 完成成本同口径比较、服务技术指标、验收主体和验收依据四项审稿；
- 可以列出与点名维度直接相关的指标或材料类别，并说明缺项为何削弱决策支撑；
- 不规定厂商数量、云端/自建/API 等比较路径，不指定具体部门或第三方，不补数值阈值、合同义务、固定验收程序或用户未点名的审查域。

任一事实、状态、任务模式或四项完整性能力回退，候选不准入。只出现一般审稿礼貌语或不改变实质的篇幅差异，记风格提示，不按硬失败处理。
