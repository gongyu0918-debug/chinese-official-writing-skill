# WR-020a1 与 WR-014-R4 原子结果

## 结论

- `WR-020a1`：`REJECTED_FOR_FIRST_DRAFT`。内部决策分析前置有限建议有写作价值，但两轮首次起草候选分别出现薄稿、年度报告结构弱化、信息缺失状态和草案归属扩张，不进入产品。以后若继续，只能对已有稿中已经存在的建议段作精确搬移。
- `WR-014-R4`：`PASS_REVISION_ONLY_CANDIDATE`。最终候选只在复核或改稿时处理“本次材料未提供数值”被写成计划/草案未提出、未设置、尚未确定、待明确或待会议决定的问题；缺失值不影响文种功能时只保留已明确动作，不转述材料视角。首次起草的宽泛三态/结构提示均不接入。

## WR-020a1 从长稿回退到停止

同一 Terra 模型的首轮 baseline 把“继续开展两种保障方式报价和风险评估”的建议放在专题分析末段；candidate 把建议移到前部，但两篇都明显压短，年度报告又弱化受托说明和分节结构。R2 明确只搬移已有结论、不授权缩短全文后，L1恢复了10项分类、860项拆分、3.8小时、预算、A/B原因和两次中断，却新增：

- 把“材料没有给新指标值”写成“未设定新的指标值”；
- 把2026年草案和年度审议关系带入内部专题分析；
- L2写成“具体指标值以审议后的年度安排为准”。

目标位置改善不能覆盖这些状态和文种回退，因此不修改报告/长稿 reference，不增加固定结论位置、段长门或 Hook。

## WR-014 三态与长报告

### 非区分控制

首组三态题把正确状态直接写进用户禁令，Terra baseline/candidate 近乎逐字通过，只算正向控制。删除答案式禁令后，Luna baseline/candidate 仍都正确区分：

- 本次材料未提供新指标值；
- 安全评估已完成但报告未附；
- 安全评估明确未开展。

这说明短稿没有稳定共同缺口，不能用三态总规则进入产品。Alibaba Token Plan 的 DeepSeek V4 0731 max 两臂均在写稿前返回 `unreadable_encrypted_agent_task`，没有形成稿件，记 `TECHNICAL_INVALID`，不计质量。

### 年度长报告复现

同一长报告中：

- 历史 Terra baseline/candidate 已分别写过“尚未确定”和“未设定”；
- R4C broad candidate 写成“草案未提出新的指标值”，broad 规则拒绝；
- R4D Terra candidate 安全省略缺失指标状态，完整保留12/10/2、860拆分、3.8小时、两次中断、预算差额、A/B原因、4项草案和保障方式未决；
- Luna baseline 再次写成“现阶段未提出新的指标值”，并错误把保障方式和预算差额交年度会议审议；
- Luna R4D candidate 修复指标状态和错误审议关系，但新增“受中心委托”的错误受托关系，不能据此批准首次起草规则。

### 同一 D0 精确改稿

E1 的材料只说明当前材料未提供新指标值，现稿却写成“草案未提出＋尚待会议审议确定”；E2 的材料明确新指标尚未确定并已列入会议审议。Luna 结果：

| 臂 | E1 | E2 | 硬回退 |
| --- | --- | --- | --- |
| baseline | 删除伪状态，但改成“本次材料未提供……”材料旁白 | 完整保留真实未决 | 无事实回退，直接使用成本1句 |
| candidate | 只保留“继续按月复核”，删除材料旁白 | 与 baseline 逐字相同，完整保留真实未决 | 无 |

这一结果支持复核/改稿原子，不支持把同一句扩成首次起草结构规则。canonical 与四套普通镜像只增加这一条修正边界；不改 SKILL 入口、description、长稿/报告叶、Hook 或 lint。

## 实际模型与工程验证

- 有效 Desktop 线程：Terra 的 WR-020a1 baseline/candidate/R2、WR-014 R4控制、R4C长报告和R4D长报告；Luna 的R4B非引导三态、R4D长报告和R4E同稿修正。
- 技术无效：Alibaba Token Plan / DeepSeek V4 0731 max 两条 encrypted task 路由失败。
- `python -B -m unittest maintenance.tests.test_skill_boundary maintenance.tests.test_repository_reachability -q`：85项通过。
- canonical `quick_validate.py`：`Skill is valid!`。
- canonical 与四套普通镜像的 `information-selection.md` SHA-256 唯一值为1。
- `git diff --check`：通过。

## 剩余风险

首次起草的复杂年度报告仍可能生成缺失指标伪状态、错误受托关系或错误审议主体；本候选只降低复核/改稿阶段的直接使用成本，不宣称首次长稿稳定性已经解决。下一高价值原子仍是 `WR-020b1` 讲话任务卡，必须只核对输入，不同时改造全文节奏或新增责任。
