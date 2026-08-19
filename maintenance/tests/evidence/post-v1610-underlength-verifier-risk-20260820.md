# 篇幅不足语义验收剩余风险复测

## 绑定与结论

- 基线：本地公开 `main@3084ee567eefb80b47e1cd40aea1a13399734282`。
- 实验分支：`codex/post-v1610-underlength-inference-boundary`。
- 结论：`HOLD`。现有写稿模型兼任语义验收时，会把自身新增的目的、动作、状态强化或重复解释低估为 `reasonable_inference`、`transparent_derivation` 或 `restatement`。仅收紧类别说明、换成同模型独立 Agent，均未稳定消除误放。
- 所有产品和测试代码试改均已撤回；本分支没有保留 runtime 行为变化，不合并、不发布。

## 触发来源

付费提纲与篇幅不足组合 R8 将 D0 从268字补至347字，内部门禁选择 D1；全新 SOL max 判 `REJECT`，指出新增“为掌握现有设备状况”“核对了设备数量和使用情况”等材料外目的、动作、因果关系，以及“一一对应”的重复补字。R11 使用材料明确但 D0 未写入的清点事实，268→356字并获 SOL max `ACCEPT`。因此所需边界不是禁用扩写，而是区分材料明示事实与模型自推内容。

## 真实复测

### R1：无激活，技术无效

两题均返回 D0，但只有4个 Hook 事件，模型没有读取 Skill，未建立篇幅事务。该轮记 `ACTIVATION_INVALID`，不把“结果是 D0”冒充风险已消除。技术汇总 SHA-256：`575ba436fe3193878fde610fe2c9a4435850bf8c6eefac7ae62298cce2f203f7`。

### R2：显式 Read 后进入真实生命周期

- 推断型题：候选349字先被既有字段机械门拒绝，最终逐字 D0；该结果安全，但没有穿过本轮待验证的语义类别合同。
- 明示事实题：268→357字、内部门禁选择 D1。独立 SOL max 判 `REJECT`：把材料“现均已恢复使用”强化为“现均已恢复正常使用”，并出现“发生故障，分别于……发生”的重复表达。
- 技术汇总 SHA-256：`aae9f385b474b2d370e1adebdca27988fdaeb63b6113ffbb97c5e5d444dbb326`。

### R3：冻结原 R8 D1 复放

原型曾把 `reasonable_inference` 从篇幅兜底准入类别中移除。固定 R8 候选进入验收后，同一模型将原先三项 `reasonable_inference` 改标为 `transparent_derivation`，最终仍选择被 SOL 否决的 D1。技术汇总 SHA-256：`b5c0d9a855a5d7645c4d862ca6a45eb96a741dd5f5ba83754b10ffc0c5781d77`。

这说明自由类别由同一模型生成时，机械拒绝某个类别不能形成可靠边界。

### 独立 verifier Agent 原型

在 ignored 隔离包中加入无工具、独立上下文的私有 `fact-verifier` Agent；主 Agent 遇到验收反馈时调用一次并逐字回传 JSON。

| 原型 | 固定坏 D1 | 固定好 D1 | 结果 |
| --- | --- | --- | --- |
| R1 | Agent 将三项标为 `reasonable_inference`，但仍整体 PASS | 全部重述，PASS | 坏稿仍被选 D1 |
| R2 | 明确规定出现 `reasonable_inference/new_specific_fact` 必须 FAIL；Agent 随后把相关内容重标为 `transparent_derivation` 并 PASS | 重述/透明关系，PASS | 坏稿仍被选 D1 |

- 两轮每题均真实调用1次 Agent，插件指纹前后无漂移；不是路由或回传故障。
- R1 技术汇总 SHA-256：`dba87a9abb665d68eeda565cb1d037d78fb6bad6c57047a8e0a53caa8715b381`。
- R2 技术汇总 SHA-256：`6bb2dc2c85dfc2e0213f36a824e00a9d8ab109132a3e680b63b5cb3a5317f689`。

## 根因与下一候选

1. 当前 verdict 的类别和总判均由模型自由填写，缺少可机械核验的来源绑定；同一增量可以在不同轮次被改标为推断、透明归纳或重述。
2. 同 provider、同模型的独立 Agent 能减少上下文污染，但不能替代更强判别能力；仅增加 Agent 不足以准入。
3. 下一原子只能在以下两类设计中择一先做最小真实原型：
   - 来源 span 绑定：新增事实必须引用请求或材料中的精确 span，并由 runtime 校验 quote/hash；没有可验证来源则回退 D0。
   - 真正独立且能力更强的 verifier：宿主能够明确选择与 writer 不同的模型/上下文，并冻结输入、输出和失败回退；不得在用户不知情时联网或上传材料。
4. 任何新方案先用固定 R8 坏稿和固定 R11 好稿验证：坏稿必须 D0，好稿必须 D1。通过后才补 coordinator、adapter、组装器和跨宿主工程门。

## 当前安全边界

- 现有 under-length 在部分不安全候选上仍会正确回退，但不能据此声称语义验收已覆盖所有细微外扩。
- 稀薄材料继续允许逐字 D0；不得为了提升 D1 采纳率放宽事实或状态门。
- 付费提纲有序组合继续保留为实验候选，不因单个 R11 成功稿直接合入付费分支。
