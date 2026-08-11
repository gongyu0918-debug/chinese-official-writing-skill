# Candidate Direct Fact State R2 受控复验预注册

日期：2026-07-29

## 目的

R1 两题匿名结果均为 Candidate 小胜，但同题两臂实际读取的 reference 集合不一致，实际模型和 thinking 也未在原始运行记录中闭合。R2 不修改产品，只固定读取清单和运行证据，用于判断 `information-selection.md` 新增单句的组件级因果效应。

固定对象：

- 发布基线：`v1.5.28=f7570d4df5064582946732d283d30e86063ef142`
- Candidate 产品提交：`a3134679be2198ea59290cf87292e0cfd0b8140c`
- Candidate 产品句：`已选入正文的事项，直接陈述该事项已给的业务事实和当前状态。`
- 两套包各 29 个同路径文件；除 `references/information-selection.md` 的上述单句外，逐文件字节一致
- R2 不增加、删除或改写任何产品 Prompt、路由、脚本、正则、FSM、输出模式或版本字段

## 任务与固定读取清单

两臂使用同一 `request.txt`、同一实际模型、同一 thinking、同一宿主条件、同一文件顺序，各取首个技术有效输出；不返修、不补抽、不向写手说明候选机制、预期答案或 P0 风险词。

### S15：1200 字左右工作总结

起草前按序读取：

1. `SKILL.md`
2. `references/information-selection.md`
3. `references/workflow.md`
4. `references/genre-playbooks.md`
5. `references/handling-elements.md`
6. `references/argument-chains.md`

完整 D0 形成后按序读取：

7. `references/final-review-layers.md`
8. `references/proofreading-checklist.md`

不读取 `task-route-cards.md`、`official-style.md`、`anti-ai-patterns.md`、其他文种叶、格式叶、脚本、根仓库、另一臂包、旧稿、测试证据、memory 或网络内容。

### C01：500—700 字材料稀疏异常通报

起草前按序读取：

1. `SKILL.md`
2. `references/information-selection.md`
3. `references/task-route-cards.md`

轻量卡结束 reference 路由，成稿后不新增读取其他 reference。禁止读取 `workflow.md`、`genre-playbooks.md`、完整复核 reference、其他文种叶、脚本、根仓库、另一臂包、旧稿、测试证据、memory 或网络内容。

## 运行有效性

每臂必须保存：

- 原始任务、Skill 包和全部已读文件的路径及 SHA-256
- 读取顺序和阶段
- 首个原始响应、最终输出及 SHA-256
- `single_call=true` 和 `first_output_status=technically_valid`
- requested/actual model 与 thinking
- 原始会话或 rollout 标识、调用时间和可复核的读取轨迹
- 开始与结束的 tracked worktree 状态

主任务从原始 rollout 的 `turn_context` 独立核验实际模型、thinking 和读取轨迹。任一臂出现越界读取、空稿、二次生成、事实写后补写、工具异常，或实际模型/thinking 无法核验，整对作废；不得只补抽一臂。

## 匿名核验

匿名映射在生成后随机确定。hard verifier 和 blind judge 只读取原始任务与匿名稿：

1. 先核验事实、数字、日期、主体、状态、文种、格式、篇幅和输出模式。
2. 再核验无锚定否定、外围未决、自证边界、材料外程序或承诺；合法调查、核查、研究进行态必须保留。
3. 最后比较重复解释、逐项复述、段落句词观感和直接修改成本。

## 合并门

R2 两题均须技术有效并满足：

1. Candidate 无独有的事实、数字、日期、主体、状态、文种、格式、篇幅或输出模式硬回退。
2. Candidate 不新增 P0；C01 完整保留“正在核查、继续监测、核查完成后通报结果”。
3. 至少一题 Candidate 明确胜出，另一题不劣于基线；若出现一题明确落后或任何硬回退，不合并、不发布。
4. 与 R1 合并观察时，Candidate 至少 3/4 胜出且其余不劣；R1 仅作探索性真实运行证据，不替代 R2 的组件级因果证据。

通过只说明该单句具备合并资格。合并后仍须完成 1.5.29 发布级全量回归、固定 1.5.28 消融、Promptfoo smoke、镜像与发行包检查、轻量冷审，全部通过后才允许发布。
