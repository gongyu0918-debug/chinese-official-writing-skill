# Hook 与 review gate 复杂度复核

日期：2026-08-17

基线：`main@4271310810086c2970c0b404a148870810385e6b`，初始产品与 `v1.6.6^{commit}=b49da7f2a5a8ac2327252d29efd66f1d54ccbc35` 一致。本文件先记录静态审计，随后记录按该边界完成的行为等价拆分。

## 实测结果

AST 以函数行数和 `if/for/while/try/with/match/bool/comprehension` 决策节点计数：

| 文件与函数 | 行数 | 决策节点 | 判断 |
| --- | ---: | ---: | --- |
| `scripts/review_gate.py:evaluate_candidate` | 313 | 117 | 上帝函数；混合协议校验、修复授权、操作规划、锚点保护、文档不变量和 D0/D1 选择 |
| `scripts/review_gate.py:detect_transaction` | 183 | 32 | 高复杂度事务入口；同时负责输入绑定、恢复、快照、初始状态、检测与 repair packet |
| `scripts/review_gate.py:locate_candidates` | 131 | 27 | 规则聚合器偏大；后续只按领域拆表，不改正则语义 |
| `scripts/review_gate.py:_dispatch_transaction_locked` | 120 | 19 | 状态调度偏长，但低于前两项风险 |
| `hooks/core/gate_stop_hook.py:handle_stop` | 129 | 53 | Hook 目录唯一明确越界的上帝函数；混合 capability 顺序、普通事务 bootstrap、repair/verdict/emit 和回显恢复 |
| `hooks/capabilities/delivery_cleanliness/runtime.py:advance` | 71 | 15 | 可接受的有限状态推进器 |
| `hooks/adapters/host_gate_adapter.py:_map_event` | 60 | 24 | 接近上限，但属于宿主协议映射边界 |
| `hooks/capabilities/under_length/runtime.py:advance` | 60 | 14 | 可接受 |

全量 `hooks/**/*.py` 中，只有 `handle_stop` 同时超过现有80行/25决策约束。其余 capability 不是“一堆上帝函数”，不应为统一风格全部重写。

## 字典与规则表

- `detect_transaction` 内初始状态为31字段，是当前最大“上帝状态”风险；这些字段同时构成持久化协议，不能简单拆成互不一致的多个文件。
- repair packet 为16字段，verification packet 为10字段；应由纯 builder 统一构造和校验，而不是删除字段。
- Hook capability 内最大的字典为保护性外扩 contract 的14项响应结构，具有明确 schema 语义，不按数量直接判“魔法字典”。
- `review_gate.py` 的保护性模式、结构锚和敏感标签是领域规则表。真正风险是全部集中在3314行模块并被多个职责共同读取，而不是使用 tuple/set 本身。

## 魔法数字

核心 Hook 已将主要运行阈值命名为 `MAX_STOP_ATTEMPTS`、`SAFE_KEY_MAX_LENGTH`、`GATE_SUBPROCESS_TIMEOUT_SECONDS` 和 `MIN_FENCED_JSON_LINES`。当前需优先处理的散落值为：

1. `review_gate.py` 多处重复的最小超时1秒、最大超时3600秒；
2. CLI 的180秒默认 repair/verdict timeout；
3. dispatch lock 的0.02秒轮询间隔和5秒宽限；
4. 正则中的窗口长度。前三类可直接命名；正则窗口会影响语义召回，必须先有正反例 characterization，不做机械替换。

## 拆分顺序

### C1：先拆 `handle_stop`

保持 `handle_stop(event)` 公共签名、返回 envelope、状态字段、reason、Stop预算和 capability 顺序不变，只提取：

- selected-output 回显阶段；
- repair response 阶段；
- verdict response 阶段；
- terminal emit 阶段；
- awaiting-repair 与 unknown-state 收口。

目标是让 `handle_stop` 只负责读取 record、依次询问 capability、bootstrap 普通事务并分派 phase。拆分后每个函数不超过80行/25决策。

### C2：再拆 `detect_transaction`

提取超时校验、输入快照、backup builder、initial-state builder 和既有事务恢复。持久化 JSON 仍保持单一 state 文件和原字段，不在本原子改 schema。

### C3：最后拆 `evaluate_candidate`

依次提取 repair envelope 校验、单项 operation 规划、operation 应用与锚点复核。所有现有 reason 字符串和返回 D0/D1 必须逐字保持；不在重构中放宽或收紧语义门。

### C4：规则表分域

只有前三项行为等价后，再把保护性表达、结构锚、状态强度和篇幅规则移入各自模块。移动前后正则对象及顺序逐项比对，避免形成新的“万能规则文件”。

## 最小验证

每个原子只运行直接相关检查：

1. characterization：同一事件序列的返回 JSON、record/state、reason、选择 hash 逐字一致；
2. `test_gate_stop_hook` 加所改 capability 的定向测试；
3. `test_review_gate` 只在拆 `review_gate.py` 时运行；
4. `test_complexity_contract` 将已拆函数从“已知债务下限”改成真实上限；
5. companion 组装一次、`git diff --check`、canonical 普通无 Hook 路径零变化。

真实写稿先验证语义候选；上述重构随后进行，不用工程测试替代写稿质量。

## 实施进度

- C1 已完成：`handle_stop` 从129行/53个决策节点降至41行/16个，提取函数均低于80行/25个决策节点。
- 超时与锁策略已命名：1—3600秒边界、180秒默认值、0.02秒轮询和5秒锁宽限均保持原值。
- C2 已完成：`detect_transaction` 从183行/32个决策节点降至52行/4个；输入绑定、恢复、备份、31字段初始状态、marker 校验和 repair staging 分别由小函数承担。持久化文件、字段、状态名、reason 和数值未改。
- C3 已完成：`evaluate_candidate` 从313行/117个决策节点降至46行/7个；输入 envelope、单项 action、span、replacement、operation、硬锚和全文不变量保持原先顺序与 reason，所有辅助函数均低于80行/25个决策节点。
- 当前剩余的显式债务是规则聚合器 `locate_candidates`（131行/27个决策节点）和 `_dispatch_transaction_locked`（120行/19个决策节点）；规则表和正则窗口尚未移动或改值。
