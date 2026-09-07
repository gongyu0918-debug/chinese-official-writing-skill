# 自然字数上限原型 R1：HOLD

基线 `b77f6381438c8fa01f8576c205d13af4b8a987fd`。只补“压到／压缩到 X 字以内”解析的 26 行原型已撤回，未接镜像或新胶水。10% 启动容差未变。

冻结输入是既有自然任务 P6/R5 与 M6/R5 的完整原回复；原任务 Hook 关闭。本次用离线 `over_length` runtime 调度真实空工具 CLI 续写，不是原生宿主 Hook，也不是重新生成 D0。共享 contract 和 hard anchors 固定为基线，避免与并行修复混归因。

| 同稿 | 基线 | 解析原型 |
|---|---|---|
| P6，全文 755 字，原请求“压到700字以内” | 不识别、不触发 | 识别 700；755≤770，仍不触发 |
| M6，全文 579 字，原请求“压缩到500字以内” | 不识别、不触发 | 识别 500；579>550，触发现有压缩流程 |

M6 用 Alibaba2 DeepSeek V4 Flash 0731 与 MiniMax M3、max、每次 300 秒、0 retry。两路各 4 次真实响应，共 8 次；模型名在 init、assistant、usage 三处精确匹配，tools、MCP、Skills、plugins 均为空。CLI 报告费用合计 1.282592 USD，仅是报告值。

| 路线 | 实际压缩稿 | 机械核验后选择 | 最后实际回显 | 校验 |
|---|---:|---|---:|---|
| Alibaba2 | 399 字 | D0 | 447 字 | 未通过精确回显 |
| MiniMax | 427 字 | D0 | 447 字 | 未通过精确回显 |

人工逐稿检查：两份候选保留 D0 正文的业务事项、责任、期限及未决状态，没有恢复演示，正文可直接使用；D0 原有未给地点仍保留，不能称已完成原材料事实修复。机械核验首先因前附文中的 `468`、`500` 被删除而拒绝；附文引语、字段也有差异。两路均未进入语义 verdict。选择 D0 后，两次回显均只返回原稿的 447 字正文，最终 `over_length_technical_failure`、`delivery_verified:false`。冻结 runtime 此时返回 `continue:true`；本次没有运行原生宿主，不据此推线上发生率。

解析反控 12 项：11 项通过，1 项失败。“请只审稿，不改写；检查是否需要压缩到500字以内。”仍被识别为硬上限，现有 core 审稿分类也未拦住。材料引语、材料说明、约数及 100→110 不触发／111 触发的控制通过。旧相关 unit 3 项通过。以上不能代替真实闭环准入；本原型 HOLD，产品已恢复。

实际命令（均在本 worktree 执行）：

```text
python -B output/hook-quality-build-r1/length/run.py --prepare
python -B output/hook-quality-build-r1/length/run.py --provider alibaba2
python -B output/hook-quality-build-r1/length/run.py --provider minimax
python -B output/hook-quality-build-r1/length/check_parser.py
python -B -m unittest maintenance.tests.test_over_length_capability.OverLengthCapabilityTests.test_trigger_requires_more_than_ten_percent_over maintenance.tests.test_over_length_capability.OverLengthCapabilityTests.test_range_and_material_mentions_are_distinguished maintenance.tests.test_review_gate.ReviewGateTests.test_existing_length_violation_may_improve_without_becoming_compliant
```

prepare 与两路 runner exit 0 仅表示执行结束；真实两链均未验证交付。反控脚本 exit 1，保留失败；旧 unit 为 3/3、0.010 秒。

原始稿、prompt、完整 CLI stream、实际 argv、模型绑定、成本、状态、回显及 hash 已按原字节精选[归档](length/manifest.json)，不包含每次调用的私有 `runtime/`。原始工作坐标仍为 `output/hook-quality-build-r1/length/`，归档驱动保留当时坐标和命令。`fixture.json` SHA-256：`5b21d413fad1fde6588ce32445ab2308878f0f8ad9eadfe2e7cdc14074128133`；`prototype.patch`：`3ec4451d5e2b2173a711ddbfb7000a23764858ffc7b7a1cd624b6c16bba24660`。洁净 D1 与新的 400 字要求已作为[R2 明示变体](length-r2-result.md)另登记，结果为技术中断，不能冒充原 M6 请求已通过。
