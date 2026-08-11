# README v1.6.1 institution same-task comparison

## Scope and fixed inputs

- This is a post-release README evidence update. It does not move `v1.6.1`, change package versions, change the canonical Skill, references, scripts or Hook behavior, or publish to SkillHub/ClawHub.
- Writer model: `gpt-5.6-sol`, reasoning effort `ultra`; each arm returned its first draft once, with zero retry.
- Prompt SHA-256 after UTF-8/LF normalization and removal of the final newline: `fbf7456bfb50c81a72feed522cdb1bd036c3f041b6e25270cd4d4bdad6fcf696`.
- No-Skill arm: independent `fork_turns=none` writer, explicitly prohibited from tools, local files and Skills; the writer confirmed no tool call, file read or retry.
- Skill arm: detached v1.6.1 worktree at `239eb72edc9cee513a4f76c13b9ed38f223fe32b`; no main-worktree, README, evidence, memory or other same-name Skill was read.

The Skill writer read exactly these files:

| File | SHA-256 |
| --- | --- |
| `chinese-official-writing/SKILL.md` | `47ce3d74e3bd9bc402f5c9cdf2d2e3f351681e5df8a38e430e1689fab2c8ad9e` |
| `references/information-selection.md` | `0f2f80cba289aa728d8fc85fa00cbdcb0fb096af87cfb1a49831356ceae82d5f` |
| `references/genre-playbook-institution-rules.md` | `ed3b45dae82bc3a7177448dbb572e056c6595d0bb781c88cedda374f46a46efd` |
| `references/anti-ai-patterns.md` | `ec07e21c823a02d0039a103a4c1abd417b8de28a789d6606603fc4823f8ac4fd` |

## Original prompt

```text
请根据以下材料，起草《明川市政务服务中心服务事项信息变更管理办法（试行）》，控制在1000字左右，只输出可直接使用的制度正文，不附起草说明。

材料：
1. 适用于中心综合窗口办理的事项名称、申请材料、办理时限、办理方式、咨询电话等信息变更。
2. 业务科室提出变更，填写变更单，写明变更内容、变更理由和拟生效日期；涉及增加申请材料、延长办理时限或暂停办理的，应附业务主管部门书面意见。
3. 运行管理科只核对变更单是否完整、拟变更内容与现有系统配置是否一致，不对业务依据作合法性判断；材料不完整的退回补正，材料完整的在2个工作日内反馈核对结果。
4. 信息技术科根据确认后的变更单在测试环境配置；业务科室负责核验。核验通过后，信息技术科在拟生效日前1个工作日完成正式环境发布；未通过的，恢复测试环境原配置并将问题退回业务科室。
5. 因系统安全风险或上级紧急通知需当天变更的，业务科室标注“紧急”，经运行管理科负责人确认后可当天配置，变更单在2个工作日内补齐。
6. 每次变更记录变更前后内容、操作人员、发布时间和核验结果；记录保存2年。
7. 运行管理科每季度汇总变更次数、退回补正和紧急变更情况，但不评价业务依据是否合法。
8. 办法处于试行拟稿阶段，试行期拟为6个月，具体起止日期尚未确定；试行期满后是否转为正式制度另行决定。
```

## First outputs

No-Skill output: 920 Han characters, 1002 non-whitespace characters; normalized SHA-256 `a3dab78129a32ce88fe4f506f1ccbc18b65ca1adedea69677693cffdc472b64c`.

```text
明川市政务服务中心服务事项信息变更管理办法（试行）

第一条　为规范明川市政务服务中心服务事项信息变更管理，确保综合窗口事项信息及时、准确更新，制定本办法。

第二条　本办法适用于中心综合窗口办理事项的名称、申请材料、办理时限、办理方式、咨询电话等信息的变更。

第三条　服务事项信息变更由业务科室提出，运行管理科负责材料完整性和系统配置一致性核对，信息技术科负责系统配置和正式环境发布，业务科室负责变更内容核验。

第四条　业务科室提出信息变更时，应当填写变更单，写明拟变更内容、变更理由和拟生效日期。涉及增加申请材料、延长办理时限或者暂停办理的，应当同时附业务主管部门书面意见。

第五条　运行管理科收到变更单后，只核对变更单是否完整，以及拟变更内容与现有系统配置是否一致，不对变更所依据的业务规定作合法性判断。

变更材料不完整的，运行管理科应当退回业务科室补正；材料完整的，应当自收到材料之日起2个工作日内反馈核对结果。

第六条　业务科室根据退回意见补正材料后，应当重新提交运行管理科核对。补正后的办理时限按照重新提交之日起计算。

第七条　变更单经运行管理科核对确认后，转交信息技术科。信息技术科应当按照确认后的变更单，在测试环境完成配置。

第八条　测试环境配置完成后，由提出变更的业务科室对事项名称、申请材料、办理时限、办理方式、咨询电话等拟变更内容进行核验，并如实记录核验结果。

第九条　业务科室核验通过的，信息技术科应当按照变更单载明的拟生效日期，在拟生效日前1个工作日完成正式环境发布。

业务科室核验未通过的，信息技术科应当恢复测试环境原配置，并将存在的问题退回业务科室处理。问题处理完成后，按照本办法规定重新配置、核验。

第十条　因系统安全风险或者上级紧急通知，需要在当天完成变更的，业务科室应当在变更事项中标注“紧急”。经运行管理科负责人确认后，信息技术科可以当天配置。

紧急变更涉及的变更单及相关材料未能同步提交完整的，业务科室应当自紧急变更之日起2个工作日内补齐。

第十一条　每次变更均应当形成完整记录。记录内容包括变更前内容、变更后内容、操作人员、发布时间和核验结果。变更记录保存期限为2年。

第十二条　运行管理科每季度汇总服务事项信息变更情况，汇总内容包括变更次数、退回补正情况和紧急变更情况。季度汇总只反映变更办理情况，不评价相关业务依据是否合法。

第十三条　本办法试行期拟为6个月，具体起止日期另行确定。试行期满后是否转为正式制度，另行决定。
```

v1.6.1 Skill output: 705 Han characters, 765 non-whitespace characters; normalized SHA-256 `287aaf7fe1bcdc40fb703313837c16d03734102dc3caf6ac391046229f92c958`.

```text
明川市政务服务中心服务事项信息变更管理办法（试行）

第一章　总则

第一条　为规范明川市政务服务中心服务事项信息变更管理，明确办理程序和职责分工，制定本办法。

第二条　本办法适用于中心综合窗口办理的事项名称、申请材料、办理时限、办理方式、咨询电话等信息的变更。

第二章　变更申请与核对

第三条　服务事项信息变更由业务科室提出。业务科室应当填写变更单，写明变更内容、变更理由和拟生效日期。

第四条　变更涉及增加申请材料、延长办理时限或者暂停办理的，业务科室应当随变更单附业务主管部门书面意见。

第五条　运行管理科负责核对变更单是否完整、拟变更内容与现有系统配置是否一致，不对变更所依据的业务规定作合法性判断。

第六条　变更材料不完整的，运行管理科退回业务科室补正；材料完整的，运行管理科应当在2个工作日内反馈核对结果。

第三章　配置、核验与发布

第七条　信息技术科根据确认后的变更单，在测试环境进行配置。业务科室负责对配置内容进行核验，并形成核验结果。

第八条　核验通过的，信息技术科应当在拟生效日前1个工作日完成正式环境发布。

第九条　核验未通过的，信息技术科应当恢复测试环境原配置，并将有关问题退回业务科室。

第四章　紧急变更

第十条　因系统安全风险或者上级紧急通知需要当天变更的，业务科室应当在变更单中标注“紧急”。经运行管理科负责人确认后，可以当天配置。

第十一条　紧急变更的变更单未填写完整的，业务科室应当在2个工作日内补齐。

第五章　记录与汇总

第十二条　每次变更均应当记录变更前内容、变更后内容、操作人员、发布时间和核验结果。变更记录保存2年。

第十三条　运行管理科每季度汇总服务事项信息变更次数、退回补正情况和紧急变更情况。季度汇总不对变更所依据的业务规定是否合法作出评价。

第六章　附则

第十四条　本办法处于试行拟稿阶段，拟试行6个月，具体起止日期尚未确定。试行期满后是否转为正式制度，另行决定。
```

## Blind evaluation

The scoring-rubric task was dispatched without either output and received only the prompt facts. Its hard-boundary rule allowed ordinary purpose clauses, references and sequencing, while treating new concrete duties, deadlines, procedures, authority, state, legal basis, interpretation rights or penalties as unsupported additions.

- Judge 1 (`gpt-5.6-terra`, `max`): anonymous `A` was Skill and `B` was no-Skill. Verdict: `A PASS`, `B WARN`, winner `A`; direct-use cost `1` versus `3`.
- Judge 2 (`gpt-5.6-sol`, `max`): reverse mapping, anonymous `A` was no-Skill and `B` was Skill. Verdict: no-Skill fact/state `FAIL`, Skill fact/state `PASS`, winner `B`; direct-use cost `3` versus `2`.
- Both judges independently identified the no-Skill additions: a new deadline start point, mandatory resubmission and recomputed deadline after supplementation, a new repeat-configuration procedure after failed verification, and expanded emergency supplementation duties.
- Judge 1 rated the Skill draft slightly short. Judge 2 rated its length `WARN` and noted that the actor for same-day configuration is implicit rather than repeated explicitly.

Judge 1 raw verdict:

```text
A：PASS
硬事实/状态：全部保留，包括试行拟稿阶段、拟试行6个月、起止日期未定及期满另行决定。
制度结构与职责边界：六章结构完整；业务科室、运行管理科、信息技术科职责清楚，运行管理科“不作合法性判断”边界明确。
约1000字完成度：4/5，内容完整但略偏短。
自然度：4/5。

B：WARN
硬事实/状态：大部保留，但未明确“处于试行拟稿阶段”。新增补正后重新提交并重新计算时限、问题处理后重新配置核验、紧急变更补齐“相关材料”等具体程序和义务；“自收到材料之日起”“自紧急变更之日起”也补入了题面未给出的期限起算点。
制度结构与职责边界：流程衔接顺畅、职责清楚，且保留运行管理科不作合法性判断的边界；但新增程序改变了原有操作边界。
约1000字完成度：5/5。
自然度：5/5。

总体：A优。
直接用于README的成本分（1低—5高）：A 1/5；B 3/5。
```

Judge 2 raw verdict:

```json
{"A":{"fact_state":"FAIL","structure":"PASS","length":"PASS","naturalness":"PASS","direct_use_cost":3,"issues":["第五条新增“自收到材料之日起”的期限起算规则。","第六条新增补正后重新提交及办理时限自重新提交之日起计算的程序和期限规则。","第九条新增问题处理完成后重新配置、核验的程序要求。","第十条将补齐范围扩大至“变更单及相关材料”，并新增“自紧急变更之日起”的期限起算规则。"]},"B":{"fact_state":"PASS","structure":"PASS","length":"WARN","naturalness":"PASS","direct_use_cost":2,"issues":["全文明显短于“1000字左右”的要求，可适度补充职责和流程衔接。","第十条“可以当天配置”未明确配置主体为信息技术科，虽可由上下文推知，但直接使用时宜补明。"]},"winner":"B","reason":"B完整覆盖材料规定，结构清楚，未新增期限起算、补正重提或问题处理后的具体程序，事实边界更稳；主要不足是篇幅偏短和紧急配置主体略有省略。A虽更接近目标篇幅，但新增多项具体程序、义务及期限起算规则，直接使用前需要实质删改。"}
```

## Mechanical attribution and conclusion

The no-Skill output is closer to the requested length, but its added rules would change how the institution operates and therefore require substantive deletion. The Skill output preserves the three departmental roles, the limited legality-review boundary, all given deadlines, the failed-verification rollback, and the unresolved trial status without inventing an effective date, interpretation right, punishment or automatic conversion. Its visible trade-off is under-length delivery.

Both reverse-mapped judges prefer the v1.6.1 Skill output. This one institutional-writing example is appropriate for the README because the difference is tied to the released institution-rule and information-selection paths. It is not evidence of universal model superiority and does not establish that the Skill always meets requested length.
