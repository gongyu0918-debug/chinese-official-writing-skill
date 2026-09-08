# HK-002b 共享来源关系接口

本接口沿用普通 MIT 的单次 `detect → prepare → finalize → emit`，只增加状态/完成范围与无据时间前置条件的待审位置、局部修订和独立关系核验。尚未合入 main、安装或发布。事实正确性以真实结果为准；API 可执行或 JSON 合法不是语义通过。

实现：[定位与关系包](../../chinese-official-writing/hooks/core/source_fact_review.py)、[事务及共享结果](../../chinese-official-writing/scripts/review_gate.py)、[宿主修订与核验指令](../../chinese-official-writing/hooks/core/gate_stop_hook.py)。

## 输入与调用

`request` 是当前用户请求，`source` 是已有材料绑定机制恢复的有效用户材料，`draft` 是完整 D0。原稿或旧助手正文不是来源。最新明确更正覆盖旧材料；引用位置只定位，核验仍须读取完整 request/source，不能仅凭某个旧句覆盖新更正。

纯函数 `source_fact_review.locate_candidates(request, source, draft)` 返回最多四个 `assessment_status="pending"` 的候选。每项有 `finding_id`、`target`、`span_start/end` 及 `source_relation`，其中 evidence 每项含 `origin="request"|"source"`、连续 `quote`、对应字符位置。索引是 Python 字符串位置，不是 UTF-8 字节偏移。空列表仅说明窄模式未定位到问题。

正常消费沿用 `review_gate.detect_transaction(request_path, draft_path, source_paths, txn, repair_timeout, verdict_timeout)`。`gate_stop_hook._repair_instruction(txn)` 返回本次实际修订指令，绑定材料会直接附入新来源检查包；快照缺失或 hash 不符返回 `None`。

修订响应沿用现有 `repairs` 的 KEEP/DELETE/REWRITE。存在来源候选时，另须逐项返回 `source_assessments=[{"finding_id":...,"status":"error"|"not_error"|"unknown","reason":...}]`。未知和原文成立均只能 KEEP。`prepare_transaction(txn, repairs_path)` 校验原硬锚、目标外文字和结构，只有机械检查通过才产生待核验 D1。不得把材料原有、D0 本来合理省略的信息当成候选新删；不得为通过而减少材料输入。

`source_fact_review.build_relation_packet(request, source, draft, candidate, findings, repairs)` 验证全部实际操作能精确重建 D1，并检查原稿位置和材料引句确实存在。须传完整 findings/repairs（含普通项），结果只列实际改变的来源项；绑定错误抛 `ValueError`。包绑定 `request_sha256/source_sha256/d0_sha256/d1_sha256/packet_sha256`，`resolved/source_relation_supported` 初始为 `null`。包和 hash 不证明来源蕴含。

`gate_stop_hook._verdict_instruction(txn)` 生成当前关系核验指令。独立核验响应在现有 checks 外，须有 `source_fact_corrections_verified`，并逐项给出：

- `finding_id`；
- `d0_issue_status`: `error`、`not_error` 或 `unknown`；
- `d0_issue_resolved/source_relation_supported/other_facts_preserved`: `true`、`false` 或 `null`；
- 说明具体关系的 `reason`。

响应还必须绑定 `source_relation_packet_sha256`。只有实际改动项均确认原稿有错、候选修对、其余事实保持，且原有检查全部通过，`finalize_transaction(txn, verdict_path)` 才能选 D1。无据新增日期/数量、伪造材料引句、只检查 D1 新增变化的旧格式 verdict、未知或未解决项均不能借此通过。仍只有一次修订与一次独立核验，没有新增重写循环或选稿出口。

finalize 从冻结四输入、检测位置及实际修订重建来源关系包，缺失state来源字段不能降级成旧格式核验。已选D1恢复先校验选稿回执绑定的verdict；来源verdict仍要求完整来源凭据，普通旧D1维持原恢复依赖。恢复和共享报告使用同一绑定逻辑，来源凭据缺失不能改发相反的D0冒充原交付。

## 共享结果

`review_gate.source_fact_report(txn, observed_output=None)` 是只读接口，应在宿主清除临时原文前消费。`observed_output` 必须来自本次实际观察到的最终输出，不能填写计划选中的稿件冒充交付。

| 字段 | 含义 |
| --- | --- |
| `schema_version` | 当前为 1 |
| 四个输入 hash | request/source/D0 及已生成 D1；没有 D1 时后者为 null |
| `findings` | 原稿原句/位置、材料证据、初审判断、核验判断及局部问题解决状态 |
| `assessment_status` | pending/error/not_error/unknown；初审判断本身不是独立事实通过 |
| `candidate_resolves_issue` | 独立核验通过时该候选的纠错结果，否则 null |
| `delivered_issue_resolved` | 实际输出匹配选中 D1 且候选已验证修对才为 true；未观察交付为 null |
| `unknown_ids` / `unresolved_ids` | 未知/待核对，与初审认为有错但尚未确认交付修正的项分别列出 |
| `candidate_verdict` | PASS、NOT_RUN、FAIL_OR_INVALID，详情见 reason |
| `selected` / `selected_sha256` | 原事务选稿回执，不等于调用方已经交付 |
| `observed_output_sha256` / `delivery_verified` | 实际观察值与已选稿 hash 是否一致；未提供观察值为 null |
| `full_draft_fact_verified` | 恒为 false；本接口不声称全文事实已核验 |

Pro 消费报告时须重新绑定自己的 request/source/D0/D1 与最终选择。MIT 已在另一条 CLI 链交付，不代表 Pro 本次已交付；不得复制 `delivery_verified` 充当 Pro 的交付证据。此接口不加入 Pro 循环、付费提纲或自有来源锚实现。

原稿保留可以是正确取舍、未知、修订失败或核验失败，不能统称事实通过。两类模式以外的问题、隐含集合范围和存在解释分歧的未完成/未开始不作覆盖承诺。有据归因、影响、可能原因（含逆推）、论证、建议和合理省略不因未逐字出现就被判错。

当前真实结果见[两类原稿纠正](../tests/evidence/hk002b-source-state-r1/result.md)：第二轮五路10份响应，8份选中并实际回显D1、2份因格式失败保留D0；还有1份真实坏候选被独立核验拒收。精确样本与四输入hash见[samples.json](../tests/evidence/hk002b-source-state-r1/samples.json)。这些是canonical事务加CLI真实响应证据，未覆盖新版本原生Stop或Pro自身最终交付。
