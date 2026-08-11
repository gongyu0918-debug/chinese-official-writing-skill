# Hook 未决转进行态预放行删除：预注册

- 固定基线：`b91f25cc49cc8ca1379804a81a1d6e5a4eab987c`（`main`）。
- 候选分支：`codex/hook-progress-preallow-relief-v1554`。
- 唯一产品变量：`chinese-official-writing/scripts/gate_stop_hook.py` 的 repair/verdict 指令，不再把“原因尚未形成结论”改成“正在调查或核查”预判为等价、非新增动作。
- 明确排除：`review_gate.py`、任何机械 gate 规则、Skill/references、路由、检测、发布元数据和模型调用。

## 目标

删除会引导模型把未决状态直接改成进行态的预放行。保留既有“不得新增事实、主体、动作或承诺”“任何一项不能确认即 FAIL”等通用边界，不增加新的词表或规则。

## 成功与停止条件

1. repair 与 verdict 提示均不再包含把未决改为调查/核查进行态即等价、非新增动作的话术。
2. 既有 Hook 状态机测试维持；测试改为验证通用边界和不预放行，不要求具体语义判断结论。
3. focused/full unit、stub smoke、fixed ablation、quick validate、编译、diff 与同步检查通过。任一 Hook 轮次、emit 或 exact echo 回退即停止。
4. 本分支只登记而不运行真实模型测试。

## 后续真实 Hook repair/verdict 验证矩阵（预注册）

T1 “原因尚未查明”被建议改成“正在核查”；T2 “未形成采购决定”被建议改成“正在研究”；T3 点式负检查结论加未决原因；C1 来源明确包含“正在核查”；C2 外围保护尾句可删除；C3 KEEP 原样来源句。每题固定 D0、来源、检测包，候选与基线匿名运行，记录 repair、verdict、D1 和 gate 理由；不将模型的偶然偏好视为 gate 因果。
