# UL-005 单稿事实台账 R2

## 候选边界

本轮只验证 under-length 语义验收中的一个候选：对每个非空 D1 增量建立事实台账，并把 subject、object、predicate、status、intensity 绑定到请求或 D0 的精确 span、起止位置和 SHA-256。`relation=same` 必须逐字一致；`relation=restatement` 或 `transparent_derivation` 的 candidate 必须仍出现在冻结的请求或 D0 中。该原型不宣称完成中文语义解析，独立 verifier 仍负责最终判断；台账缺失、span/hash 不一致或语义字段无法绑定时逐字回退 D0。

候选不改变宿主胶水、来源文件或公开包，不运行第三方脚本，不启动付费模型矩阵。

## 同一 D0 修订样本

原始 D0（26 字，SHA-256 `58fa112890b428219c546b5827c027e0def0b947c9336171bd7384742d8ed781`）：

```text
关于开展业务培训的通知

各部门：
现组织业务培训。
```

候选 D1（85 字，SHA-256 `c4a69c174a09e3d3cc004bc3205dfd3afa2b538b7e6f068c769abc230eb43c8e`）：

```text
关于开展业务培训的通知

各部门：
现组织业务培训。培训内容围绕日常业务，培训安排按既定计划进行；各部门统筹工作与学习，参训人员完成学习任务并学以致用，当前安排保持不变。
```

D1 的唯一增量为新增培训事实段；台账引用请求中的连续 span“培训安排按既定计划进行；要求各部门统筹工作与学习，参训人员完成学习任务并学以致用，当前安排保持不变”，并逐项绑定五类语义字段。当前实现通过该同稿生命周期：D1 进入 verifier，完整台账通过后可选择 D1，回显 hash 闭合。另有 1 条 authority-grounded restatement 通过：候选谓语“组织”虽不同于所引 span 中的“开展”，但该词已在冻结请求/D0 出现；因此实现没有退化为只允许逐字复制。

## 两条对抗题

1. 真实但无关 span：请求同时含“办公室收到三份材料”和培训要求；D1 增量是培训安排，台账却引用“办公室收到三份材料”（span SHA-256 `a505f2683131f0d2bccd9bcb56b3d0f75d2007366a3ee2f3db07382654800f85`）。实现拒绝：事实角色无法同时在所引 span 与增量中成立，选择 D0。
2. 局部相关 span但新增谓语：请求/D0 含“各部门统筹工作与学习”，D1 改为“各部门统筹工作与学习并完成考核”。D0 SHA-256 `d2097ecff17c98645c995d83c24b70d8da17d98b744524c3ac70d345f61f7837`，D1 SHA-256 `b030638d862a1c036e6de9b71e2259aa7b692a502058b74aa2ae49c6e80eb9d6`；台账将 source predicate“统筹”绑定 candidate predicate“完成考核”，实现拒绝，选择 D0。

## 实际验证

```text
python -B -m unittest maintenance.tests.test_under_length_capability -q
Ran 13 tests in 1.705s — OK

python -B -m unittest maintenance.tests.test_shared_hard_anchors maintenance.tests.test_host_gate_adapter maintenance.tests.test_hook_layer_contract -q
Ran 37 tests in 16.835s — OK
```

新增 1 个合法同稿生命周期样本和 2 个确定性对抗题；没有运行在线模型，因此不能把本轮写成 CodeBuddy/WorkBuddy 或跨宿主在线闭环。候选是否扩入主线继续 HOLD，下一步应使用同一 D0 的少量真实 verifier / 宿主写稿，观察合法同义转述能否在保留五类字段绑定的同时通过，以及是否出现“source span 正确但关系不相关”的模型自审放行。
