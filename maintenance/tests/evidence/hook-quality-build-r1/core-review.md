# Core / shared / Claude 有界收口复核

本次已发现的阻断反例均已修复，最后反控通过；没有据本轮证据仍需开放的 P1/P2。此结论只覆盖任务来源绑定、读取边界、取消/终态和默认预处理交接，不代表完整事实核验，也不解除 [factual 原子 HOLD](factual/README.md)。未运行模型、原生宿主或全量测试，未修改产品；只补本报告与反控脚本，交由主代理统一提交。

基线为 `b77f6381438c8fa01f8576c205d13af4b8a987fd`。最后检查的工作树文件 SHA256：

| 文件 | SHA256 |
| --- | --- |
| `hooks/core/gate_stop_hook.py` | `ffd76a115739dda683e248d929feba86a5f22b9c93c6193513ddb09833b58da1` |
| `hooks/shared/revision_context.py` | `c30515769bbd04ad351d03447245f7798352f9132ab45e1eba7043496ff0c00c` |
| `hooks/adapters/claude-code/gate_stop_hook.py` | `ec180bb1e6e67c9e5a7ee18d6fcb4915db23b743c367de9ae94ddc3a49dcf663` |

以上路径均在 `chinese-official-writing/` 下；审查期间主代理修正了工作树，下列“修复前”不冒充最后版本仍有的问题。

## 发现与最终状态

**已解除 P1：默认洁净度不能替代原默认门禁。** 原新增路径在清理精确回显后进入终态并脱敏，跳过 `_bootstrap_transaction`、`_prepare_gate_draft` 和 detect。用同一窄输入调用现有日期纯函数可确认：材料给 `2026年9月5日`、D0 为“下面是正文。\n\n9月5日，中心举办读书交流活动，共20人参加。”时，原日期预处理可补年，而原清理路由会先接管。该证据是可指认的被遮蔽能力，不是把 P6/M6 已观察到的未修正文误报成候选回退。

最后实现将默认清理标为 `cleanliness_prepass`；在真实回显已验证时保存审计、移除其终态子状态并继续普通门禁。`core:1120–1136`、`core:1919–1927` 的交接反控确认：回显正文原样到达后续 bootstrap。清理失败有明确失败出口。主代理另行负责真实串行链与后续模型裁决证据；本审的内存反控没有代替这些证据。

**已解除 P1：新交接不得吞掉并发失败回执。** 修复前，预处理完成后的 `_write_record` 若发现另一个 Stop 已写入 `raw_turn_data_redacted + failed_bounded + hook_selected_output_echo_budget_exhausted`，会刷新 caller 并返回 False；交接分支仍返回 None，随后 `stop_hook_active=True` 路径返回 `continue:true`。单个内存反例确实得到该错误响应。最后 `_handle_stop` 在清理分支返回 None 后立即重新处理已脱敏终态，复验得到 `continue:false`，并且不进入 bootstrap。位置：`core:1907` 附近的清理调用与其后的终态再检查。没有把这一响应错误描述成原文写回。

**已解除 P2：独立新稿误接旧材料、读取路径不实。** 修复前，前一稿含“甲局已完成10项”，下一条为“请修改下面这份报告，给我完整正文。\n\n乙校开展开学检查，结果尚待复核。”，recover 会把甲局材料接入乙校稿。最后 `revision_context:12–22` 不再用“完整正文/全文”单独证明同稿，并拒绝“修改下面这份”；同一反例返回 None，明确“刚才的报告”仍能恢复。读取凭证最后只接受 Read，且以 resolve/is_relative_to 约束本 Skill；`../LICENSE` 反例已拒绝。`is_error=True` 的失败 Read 原本就会拒绝，本次再核对通过，没有把它误记为已修的新缺陷。

**已解除 P2：取消在入场检查后到达时仍写新 raw。** 已脱敏终态在 bind 锁内一直能阻止迟到写入，初始反控为 0 次写入；问题只在取消发生于 handle 入场检查之后、recover 期间，且第一次清理因锁竞争尚未形成终态的窗口。最后 bind 锁内检查 pending marker；Stop 在 bind 后及退出前处理新到 HostAbort。以当前 turn 已有 `skill_seen=True` 的同一控制流复验：分派取消、0 次 raw 写入、没有启动清理。`_write_bootstrap_inputs` 的终态与 pending marker 两项反控也均返回 False，request/draft/source 全部 0 写入。没有将该窗口夸成普通取消必然恢复已清理原文。

## 已核对的边界

Claude 只在 Stop 映射 `transcript_path`；recover 同时绑定 session、当前完整 prompt、非 sidechain 和有限用户回合。来源仅由用户材料与修改要求按时间组成，未把 assistant 旧稿写成事实依据。`source.txt` 与 request/draft 共用短状态锁写入，detect 接收 `--source`；`source_text` 属于 raw 脱敏键。它仍不是通用的多文档识别器，也未把按时间排列的修改要求转换成已裁定的完整事实表。

`_body_only_has_wrapper` 仍是首段窄模式识别；否定句或引用“只发正文”的措辞可能匹配选择器。只读观察尚未证明用户要求的解释被删除，清理本身仍要求保留用户指定内容，故没有据此另列 P2 或扩充本轮工程。最终串行流程、真实可用性及其他宿主由主代理和质量审核分别举证。

## 实际验证

脚本：[core_review_probe.py](core_review_probe.py)。执行命令：

```text
python -B -X utf8 maintenance/tests/evidence/hook-quality-build-r1/core_review_probe.py
```

最后输出 `status=PASS`：四项来源/读取边界、两项输入写入保护、入场后取消、正常预处理交接、并发失败终态交接均符合预期。脚本只使用纯函数、内存 transcript、mock 文件提交与 coordinator 状态；不写产品或运行时文件、不调用模型、不生成 verifier PASS，不把这些反控当成真实模型质量结果。修复前失败响应和触发条件已在上文保留。
