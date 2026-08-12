# v1.6.2 Hook 复杂度与篇幅功能审计

## 绑定

- 固定产品基线：`2135fba6e05ee9a3d9c9f931237a9eb01b0cc107`
- 静态适配架构提交：`1535bc1a13bd44d1c85a2f031a21cc1624f3a172`
- 审计范围：canonical Python、Hook core/adapters、`maintenance/tools/`；不修改写稿规则和门禁判定语义。

## AST 量化结果

| 文件 / 函数 | 行数 | 决策节点 | 结论 |
| --- | ---: | ---: | --- |
| `scripts/review_gate.py:evaluate_candidate` | 301 | 115 | 历史上帝函数，混合候选校验、锚点保护、篇幅/结构不变量和 D0/D1 选择 |
| `scripts/review_gate.py:detect_transaction` | 183 | 32 | 历史高复杂度函数；其 31 字段状态字典是当前最大“上帝状态”风险 |
| `scripts/review_gate.py:locate_candidates` | 126 | 25 | 历史高复杂度候选，宜后续按定位机制拆分 |
| `scripts/review_gate.py:_dispatch_transaction_locked` | 120 | 19 | 历史高复杂度候选，宜后续按状态转换拆分 |
| `hooks/core/gate_stop_hook.py:handle_stop` | 115 | 48 | 受限状态机仍偏大；本轮只增加任务旁路，不重排阶段语义 |
| `hooks/adapters/host_gate_adapter.py:_map_event` | 56 | 20 | 协议边界内可接受，无业务规则字典 |
| `hooks/adapters/claude-code/gate_stop_hook.py:_map_event` | 50 | 20 | 协议边界内可接受，无业务规则字典 |
| `maintenance/tools/assemble_hook_companion.py` 最大函数 | 35 以下 | 25 以下 | 本轮新增代码未形成上帝函数 |

## 魔法数字与字典

- Hook 的四次 Stop、120 字符安全键、20 秒门禁子进程和 fenced JSON 最小行数均使用具名常量。
- adapter 的 120 字符安全键和 16 位 turn digest 已使用具名常量；manifest 的 10/30 秒事件上限由 `sync_adapters.py` 的具名表统一校验。
- `review_gate.py` 的 31 字段 transaction state 和 16 字段 packet 是真实维护风险，但属于已发布门禁协议。目录重构不能证明其语义等价拆分，故本轮登记债务，不借机重写。

## 篇幅 Hook

- 当前产品树不存在 `length_band.py` 或其他自动补字/压缩模块。
- `host-capabilities.json` 明确 `automatic_expansion=false`、`automatic_compression=false`。
- 历史偏短候选的真实写稿结论为 HOLD；本轮不合入该功能，也不在产品 README 中讨论研发候选。

## 后续拆分边界

另立独立 worktree 处理 `review_gate.py`：先把 transaction/packet 提成显式类型，再拆候选定位、repair 应用、锚点与文档不变量、最终选择；每个步骤要求固定基线确定性消融、全量回归和真实 D0/D1 复放。未满足这些门前，不以代码行数为由重写门禁语义。
