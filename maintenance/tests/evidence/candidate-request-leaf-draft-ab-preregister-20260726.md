# 请示/申请叶子新建场景 A/B 预注册

## 路由校准

`candidate-request-leaf-restart-preregister-20260726.md` 登记的三组简单局部修改在实际运行中命中 `task-route-cards.md` 的二次局部修改卡，Candidate 与 Baseline 均未读取文种 playbook。该组只作为轻量路由 smoke，不计入叶拆分胜负，也不据此修改 Candidate。

请示/申请原子叶只影响新建或确需常规、完整骨架的任务。本轮改用三个正常新建场景，直接检验：

- Candidate：`SKILL.md`、`information-selection.md`、`genre-playbook-request.md` 及实际按需复核材料；
- Baseline：`SKILL.md`、`information-selection.md`、`genre-playbooks.md` 及实际按需复核材料。

## 固定对象

- 稳定基线：`faba4c1f410b3007d60671b3d2ead6d78a2ea8a4`
- Candidate 产品：`123d0d13a3879075b82457d7e012b314b8623413`
- 唯一产品变量：请示/申请规则由通用 playbook 原样迁移到独立叶子。
- Candidate Prompt、叶子内容、路由、复核和输出方式保持冻结。

## 三个自然场景

1. 新建档案防磁柜购置请示：事实、预算、经费来源、完成期限、主送、发文单位和成文日期完整。
2. 新建网络安全培训请示：培训对象、内容、时间、人数、地点、预算、来源和请批事项完整。
3. 新建公共文化活动场地使用申请：活动内容、时间、人数、场地、恢复安排、接收单位、申请单位和日期完整。

三题原始 Prompt 不写入 P0 风险词、候选机制、目标句式或答案。Candidate 与 Baseline 使用同一模型、同一 thinking、逐字一致输入，各取首个技术有效输出，不补抽。Writer、运行核验者和匿名 Judge 相互独立。

## 有效性与验收

1. 运行证据必须确认双方提交、输入和实际 reference；未触发对应叶子的题不计胜负，只记路由证据。
2. 先检查事实、数字、日期、主体、状态、文种、格式、输出模式和 P0，再比较结构、重复解释、自然度和直接修改成本。
3. 三题均无 Candidate 独有硬回退，且 Candidate 至少一题明确优于 Baseline、其余题不劣，方可判定具备合并资格。
4. 三题均难分且无 Candidate 独有负项，只能证明减载非劣；是否合并需结合 85.97% 的确定性减载收益和完整工程回归决定。
5. 一胜一负或出现 Candidate 独有轻微负项时维持 `MIXED`；先判断是否与缺失的通用 playbook 共性规则有关。
6. 同一机制在三个正常场景复现后，才允许一次最小修复；否则只记录，不一例一修。
7. 若完整独立叶仍不稳定，下一步只缩小迁移原子，不放弃请示专项渐进式路由方向。
