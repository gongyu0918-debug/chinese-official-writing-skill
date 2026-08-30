# RESEARCH-PLAYBOOK-LEAF-R1 预登记

日期：2026-08-31。

固定基线为 `main@5cb26b75395f598838267a88dd7825cad4fcac12`。本实验只在独立工作树 `codex/research-playbook-leaf-r1` 运行；冻结发布源 `codex/release-v1.6.22@62ba9e8206e5b11f08a8f28ebdfe95b08e30ccfe` 不修改、不重建、不移动。本阶段不修改 canonical Skill、references、Hook、版本、包体或 description。

## 原子与假设

`genre-playbooks.md` 同时包含函、通知、讲话、调研/研究/可研和采购等文种。当前调研/研究/可研小节仅约 0.9 KB；如果真实长稿会读取整个组合页，把已有小节原样迁入专叶并直达，可能减少约 4 KB 无关读取，同时隔离通知、讲话和采购规则。

这不是新增写作规则。基线没有稳定读取组合页时，静态体积差不构成产品收益，原子直接终止。

## 真实写稿题

- `RESEARCH-SERVICE-SURVEY`：依据调查样本、办理数据、访谈归因和未决扩围状态，起草 1600—2200 字的政务服务调研报告。重点观察结构均衡、后半篇论证、事实与建议绑定、条件性结论。
- `RESEARCH-EQUIPMENT-SHARING`：依据设备台账、预约记录、访谈和待定投入状态，起草 1600—2200 字的研究报告。重点观察数据性质、问题—原因—建议链和未决状态。
- `NOTICE-TRAINING-CONTROL`：起草内部培训通知，作为仍应使用组合 playbook 的相邻文种控制。
- `REQUEST-PROCUREMENT-CONTROL`：起草稀疏采购申请，作为不得误读研究专叶的直达文种控制。

## 分阶段执行

第一阶段只运行两家低成本 provider：

- `alibaba-token-plan-2/deepseek-v4-flash-0731`
- `opencode-go/deepseek-v4-flash`

每家运行四题，`reasoning=max`、read-only、ephemeral、Hook 关闭、零质量重抽。只有两家在两个研究目标题中均产生有效终稿，并且实际命令 trace 均读取精确隔离 Skill 下的 `references/genre-playbooks.md`，才扩大当前基线到其余三家：

- `alibaba-token-plan/deepseek-v4-flash-0731`
- `ollama-cloud/deepseek-v4-flash:0731`
- `minimax-cn/MiniMax-M3`

未达到该门时记为 `REJECTED_BASELINE_ROUTE_NOT_REPRODUCED`，不创建产品叶。

## 候选范围

基线门成立后，候选只允许：

1. 新增 `references/genre-playbook-research.md`，原样承接现有“调研报告/研究报告/可研报告”小节及必要的自包含使用说明；
2. 从 `genre-playbooks.md` 移除该小节并修正目录；
3. 在 `SKILL.md` 将调研、研究、可研起草直达新叶，从组合页对应条件中删除三者。

真实 A/B 之前不改 deterministic provider、镜像、测试或包体。不得同时改长稿规则、事实边界、description、Hook、其他文种叶或新增禁词。

## A/B 裁决

- 五家低成本 provider 使用完全相同题目，每家每题每臂只取首个有效结果；基线与候选顺序交错。
- 目标题应稳定改读研究专叶，且命中新叶时实际读取字节低于基线组合页；通知仍读组合页，采购申请不误读研究叶。
- 所有有效候选稿必须保留题面主体、数字、日期、范围和“尚未决定/未明确/待核”等状态；不得补预算、审批结果、责任单位、硬期限或已取得成效。
- 基于给定事实、访谈归因和常识直接支持的一层原因、即时作用、真实归纳、低强度预期或条件结论允许成立，不因其未逐字复述材料判失败。
- 长稿不能只改写提示词或明显头重脚轻；问题、原因、建议和条件风险应有实质论证，后半篇不能退化为裸提纲句或空泛口号。
- 只有候选 diff 可归因的事实、状态、文种、路由、输出形状、必要内容遗漏或直接可用性硬回退否决候选。随机文采差异、标题偏好、技术失败、自动字面误报和基线自身问题不冒充 diff 失败。
- 如果候选需要新增第二个产品原子、堆叠强制提示或改写原有研究规则才能成立，终止本候选。

## 工程门

真实 A/B 通过后，才补 deterministic provider、路由单测、五份公开兼容包镜像、reference 链接、quick validate、包体与状态一致性检查。未运行的命令不得写为通过。
