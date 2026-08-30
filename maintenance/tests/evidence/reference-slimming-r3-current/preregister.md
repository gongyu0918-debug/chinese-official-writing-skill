# References 当前路由与下一拆分基线预登记

日期：2026-08-31。

固定产品基线为 `main@6c15efca83916cd29b1036ed265f83fc1b70280f`。本实验只在独立工作树 `codex/post-v1622-reference-hook-audit-r1` 保存研究脚本、真实输出索引和结论；冻结发布源 `codex/release-v1.6.22@62ba9e8206e5b11f08a8f28ebdfe95b08e30ccfe` 不修改、不重建、不移动。当前阶段先测基线读取，不创建产品候选，不修改 canonical Skill、references、Hook、版本、包体或 description。

## 目标

只回答两个问题：

1. 当前“只审不改”任务是否稳定直达已经存在的请示/申请、报告和可研细查叶，还是仍会加载无关的通用复核大页；通知只审作为相邻控制，观察通用文种检查页是否形成新的真实拆分信号。
2. 明确的去 AI 味改写是否稳定读取 14 KB 的 `anti-ai-patterns.md`，且任务实际上只使用必要英文/翻译腔、过程旁白或句群节奏中的一个窄面；只有稳定读取才讨论新的单面叶，不先拆文件。

历史终态继续有效：不重试 `MINUTES-CHECKLIST-LEAF-R1`、`NOTICE-LEAF-CURRENT-R1`、`PROCUREMENT-ANNOUNCEMENT-LEAF-R1/R2`、`REVIEW-LAYER-SPLIT-R1`、`FINAL-BODY-LEAF-R1`、`WORKFLOW-REVISION-LEAF-R1` 或 `AI-COMPUTE-BASIC-LEAF-R1/R2`。静态文件体积不能替代真实加载收益。

## 原子与题目

### `REVIEW-DIRECT-ROUTE-REVALIDATION`

- 请示/申请只审不改：检查请批事项、缘由、金额状态和请批语，只输出位置、风险层级、修改建议。
- 情况报告只审不改：检查最新状态、旧判断回流、报告文种和材料外承诺。
- 可研摘要点名只审：只检查数据性质、成本可比性和未决结论，不自动扩展完整技术审查。
- 通知只审相邻控制：检查对象、事项、时间、反馈关系和落款日期，不改写全文。

先观察 `review-checklist.md`、`genre-checklist.md`、三个细查叶、`final-review-layers.md`、`workflow.md`、`handling-elements.md` 和 `anti-ai-patterns.md` 的实际读取。现有直达叶已稳定工作时不做重复拆分。只有至少 3/5 有效 provider 在同一任务类型稳定加载可以由窄叶完整替代的无关大页，才允许另行预登记一个路由或搬移候选。

### `ANTI-AI-SINGLE-SURFACE-ROUTE`

- 必要英文与翻译腔改写：保留 `AI`、`API` 和未决状态，处理无功能英文口号及介词框架。
- 过程旁白改写：删除“根据用户要求”“本次修改”等非正文包装，只交完整正文。
- 句群节奏改写：处理成簇的同一段首、空泛抽象词和口号式收束，同时保留事实和一层合理作用。

先观察 `anti-ai-patterns.md` 是否在三题中稳定加载，以及是否还同时加载无关复核页。只有至少两题各有 3/5 有效 provider 读取完整反 AI 页，且窄面内容可以在不重复事实边界、文种和总审的情况下自包含，才允许创建单一窄叶候选。不得同时拆三个面，也不得用新的禁词表或硬清洗替代语义判断。

## 模型与执行

五条路线均通过 Codex CLI / OpenCodex catalog，`reasoning=max`、read-only、ephemeral、Hook 关闭、零质量重抽；每个 provider 每题只取首个结果：

- `alibaba-token-plan-2/deepseek-v4-flash-0731`
- `alibaba-token-plan/deepseek-v4-flash-0731`
- `ollama-cloud/deepseek-v4-flash:0731`
- `opencode-go/deepseek-v4-flash`
- `minimax-cn/MiniMax-M3`

保存终稿/审稿意见、JSONL trace、stderr、usage、实际读取文件和读取字节。provider 失败、缺终止信号或未读取精确隔离 Skill 记技术无效，不替产品补写结果。

## 裁决口径

- 只审任务必须保持“位置、风险层级、修改建议”，不得重写全文、补 0—100 分或把材料缺口写成既定事实。
- 改写任务必须只交可直接使用正文，保留主体、数字、日期、范围、必要英文、当前状态和用户指定结构。
- 材料事实、常识以及二者直接支持的一层原因、目的、即时作用、真实归纳、低强度预期或条件结论均可成立；不能因这些关系未逐字出现在材料中判失败。
- 只有与本轮路由或后续单原子 diff 可归因的事实、状态、文种、输出形状、必要内容遗漏或直接可用性回退才否决候选。随机文采差异、标题偏好、技术失败和 baseline 自身问题不冒充 diff 失败。
- 先完成全部基线 trace 和逐稿复核。未达到真实加载门时直接 `REJECTED_BASELINE_ROUTE_NOT_REPRODUCED`；达到门时一次只做一个最小候选，先真实 A/B，写稿通过后才补工程门。
