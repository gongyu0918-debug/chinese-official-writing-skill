# WR-028 R1 真实写稿结果

## 固定范围

- 基线：`5869234bcfee5aeb7f70762035a8ee593569fbc3`
- R1 产品候选：`38f3fa96027c59d111487627c2e818b6a0498a83`
- 产品差异只有 canonical `SKILL.md` 的整改方案直达路由和 `references/genre-playbook-remediation-plan.md` 新叶；description、Hook、通用事实边界、短稿页、普通方案叶和镜像均未改。
- 五家低成本 provider 各运行三道整改方案正向题和两道相邻文种控制题，思考强度均为 `max`。共形成 25 个候选输出；与基线组成 25 对，其中 21 对两臂技术有效。

## 结果

| 原子 | 有效情况 | 与候选直接相关的结果 |
| --- | --- | --- |
| 短整改方案 | 候选 4/5 隔离有效 | 4 份有效稿均形成原因和可执行措施；Alibaba2、Alibaba1、OpenCode 保留“尚未开展/尚未启动/尚未开始”的未启动状态，Ollama 漏写。相较基线有效稿仅 1/5 保留状态，状态落位和正文直接交付明显改善；MiniMax 因用户 Skill 路径污染剔除。 |
| 中等审计整改 | 4 个有效 A/B 对，另有 1 份候选有效但基线污染 | 四类问题、给定责任、统一期限和实际措施均保留；Ollama、OpenCode 明确保留“尚未启动”，Alibaba2 候选漏写而其基线保留，构成候选独有硬状态回退；MiniMax 两臂均遗漏，不归因于候选。 |
| 长教育整改 | 4 个有效 A/B 对，MiniMax 仅候选有效 | 有效稿均覆盖五类问题、两个阶段以及“正在修订、尚未批准、尚待复核”等状态，能形成纠偏、制度、执行和复核措施。固定台账、培训、月报、考核或过细节点仍偶发，但基线同样存在，未形成候选新增的跨 provider 硬回退。 |
| 整改进展报告控制 | 4 个有效 A/B 对，MiniMax 仅候选有效 | 5/5 候选均未读取整改方案专叶，均保持报告文种和 2/1/1 进展；Alibaba1 的过程旁白属于未读专叶的既有交付波动，不冒充路由回退。 |
| 普通实施方案控制 | 5/5 A/B 有效 | 5/5 候选均未读取整改方案专叶，也未制造审计、督察或整改背景。MiniMax 在正文前自证“不进入整改方案分支”，属于普通方案既有包装风险，不归因于专叶语义。 |

## 机器标记人工校准

- Alibaba2 短稿“整改工作尚未开展”和 Alibaba1 短稿“整改工作尚未启动”与材料状态等义，不能因未逐字命中“尚未开始”判失败。
- MiniMax 普通实施方案正文前提到“不进入整改方案分支”，触发了 `整改方案` 子串，但实际 trace 未读专叶、正文也未改成整改文种；这是包装问题，不是误路由。
- 允许的原因、直接影响、整改必要性、条件性预期和职责范围内未来措施均未被当作事实外扩。只有材料给定状态遗漏、状态升级、错误责任、误路由和正文不可用才作硬失败。

## R1 判定

R1 已证明专叶路由隔离和主要写稿收益，但不能直接进入工程门。Alibaba2 中等审计稿相对其基线漏掉“上述问题均尚未启动整改”，违反预登记的“无候选独有状态硬回退”。下一步只强化一个状态落位原子，并定向复测中等审计题及一份短稿；不改原因、影响、未来措施、目录、篇幅或相邻文种路由，也不重复整套 25 题。

## 实际命令

```powershell
python maintenance/tests/evidence/remediation-plan-r1/run_candidate.py --prepare
python maintenance/tests/evidence/remediation-plan-r1/run_candidate.py --provider alibaba2
python maintenance/tests/evidence/remediation-plan-r1/run_candidate.py --provider alibaba1
python maintenance/tests/evidence/remediation-plan-r1/run_candidate.py --provider ollama
python maintenance/tests/evidence/remediation-plan-r1/run_candidate.py --provider opencode
python maintenance/tests/evidence/remediation-plan-r1/run_candidate.py --provider minimax
python maintenance/tests/evidence/remediation-plan-r1/run_candidate.py --summarize
```

首次候选运行在四家 provider 的第一题完成后因输出根目录绑定错误未写汇总；恢复逻辑只接纳已有 `turn.completed`、非空 final、精确 Skill trace 且无用户/Hook 污染的结果，Alibaba1、Ollama、OpenCode、MiniMax 各恢复 1 题，其他题正常续跑。恢复记录不伪造耗时、Codex 路径或版本。
