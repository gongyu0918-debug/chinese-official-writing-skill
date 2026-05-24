# Expanded Ablation Summary

本文件仅记录脱敏测试结论，不包含原始公文、真实项目材料、内部路径或个人信息。

## 覆盖文体

本轮扩展消融覆盖 22 类常见正式文体，并分别设置 10 类通用场景任务：

通知、请示、报告、说明、方案、申请、函、复函、批复、意见、决定、公告、公示、通报、会议纪要、工作要点、工作总结、调研报告、可研报告、实施方案、建设方案、审查材料。

另对 5 类 AI 算力与技术服务文档进行专项校准：

算力服务可研报告、算力资源采购方案、GPU/服务器租赁技术需求、云端部署成本对比说明、技术服务审查材料。

## 消融方式

每类任务使用两组输出进行对比：

- Baseline：只给最小写作提示，不加入文种、视角、反 AI 句式、分段复核等约束。
- Skill：启用 `chinese-official-writing`，按提纲、段落、小段、逐段复核、章节复核和全文复核流程生成。

本轮为合成提示下的 smoke/regression 测试，共覆盖 27 类任务、270 个场景。测试输出由本仓库脚本生成，用于验证规则约束、文种覆盖和审查流程，不使用真实公文或内部项目材料。

## 主要观察

- Baseline 更容易出现旁白式表达、教学式开头、二元对照句和泛化结论。相关反例仅保留在测试输出和技能反例区，不在本摘要展开原句。
- Skill 输出更能保持主办单位或项目单位视角，文种结构更稳定，事项、依据、责任、时限、验收和后续管理更清楚。
- 在算力、服务器租赁和云端部署成本对比类任务中，Skill 输出更能把需求来源、Token 消耗、费用换算、租赁成本、SLA、并发、安全和验收要求连成一个决策链条。
- 长文任务中，Skill 的分段复核流程能减少重复背景、概念解释和空泛表述，便于后续进入 Word 文档排版和人工审核。

## 脚本检查

使用 `prose_lint.py` 对合成测试输出进行扫描。本轮命令如下：

```powershell
python .\tools\run_ablation.py --out output\expanded-ablation
python .\chinese-official-writing\scripts\prose_lint.py output\expanded-ablation\baseline.md --json
python .\chinese-official-writing\scripts\prose_lint.py output\expanded-ablation\skill.md --json
```

本轮合成输出扫描结果为：Baseline 命中 1594 条风险，其中 high 351 条、medium 432 条、low 811 条；Skill 输出命中 1 条 low 级术语重复提示。该结论仅限本轮合成样本和现有检查规则。

## 隔离 Agent 对照

另启动模型无关 A/B/C 三个隔离上下文进行对照：Writer A 调用技能规则生成样稿，Writer B 不读取技能规则、按普通提示生成样稿，Evaluator C 只根据 A/B 输出和公开公文风格参照进行评估。该轮原始输出不纳入仓库发布内容，仅用于发布前校准。

该轮模型无关全量生成覆盖 27 类文体、每类 10 次，共 270 个任务；A/B 写稿有效批次为 9/9，C 独立评估有效批次为 7/9，详见 `agent-public-ablation-summary.md`。该结果已用于补充安装提示、显式 Skill 上下文和空返回检测，也说明本测试不能替代人工审稿。

该结果只证明规则约束和工作流有效，不代表具体事实、数据、政策依据或金额已经通过业务审核。
