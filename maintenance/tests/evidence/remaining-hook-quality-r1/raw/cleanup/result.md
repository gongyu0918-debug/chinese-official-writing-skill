# HK-008 取消后的原文清理

R2 候选已降低两个已复现生命周期风险，并消除独立复核发现的两项候选回退，待主代理复核、统一提交。该结果是一个既有真实 D0 的定向故障复放，不是自然发生率或整体成稿可靠率。当前代理没有提交、合并或发布。

- 工作分支：`codex/remaining-hook-quality-r1`；基线：`37f22146f64cf2dfcaea7a8a5afba40750215803`。
- 基线 core SHA-256：`26d79b97e01515f50916232e14a9873a77320e196eacfd4e966faac788772900`。
- R2 core SHA-256：`7763991df28fddcf7483737a44658948e7bb520602fa109d1fa36da9978fee38`。
- 只改 canonical `hooks/core/gate_stop_hook.py` 和直接相关 `maintenance/tests/test_gate_stop_hook.py`，共 339 行新增、16 行删除，其中测试新增 235 行。未编辑 Skill、references、adapters、specs 或付费代码。

## 复放结果

使用上轮真实 MiniMax 成稿的原请求和原 D0，[原样输入及旧生成回执](sample.json) SHA-256 为 `0a66c456842dbd883b3f331abf4d3ce9c9cf3fbd42f1ecd7c39753e5a375b857`。D0 SHA-256 为 `353db1634bb8796131c8b92857aa9d49f4f1401c73dd736efa218a9c8dfee2e5`。本轮 **0 次模型调用、0 新模型费用**；未手工改写 D0，也没有构造模型 repair/verdict。

| 实际生命周期 | 基线 | 最终候选 |
| --- | --- | --- |
| U→读冻结 Skill→Stop 在首次原文写入前暂停→独立 HostAbort 子进程→恢复原写入 | 已标记脱敏后又生成 4 份含原文文件；后续 Stop 仍残留 4 份 | HostAbort 先保留无正文的取消标记，写入者退出时清理；退出后及后续 Stop 均 0 份，request 字段移除 |
| U→读 Skill→实际 OS state-lock 持锁→HostAbort 超时→释放锁→Stop | 取消意图丢失；request 保留，下一 Stop 重新 emit 并产生 5 份含原文文件 | 下一 Stop 消费取消标记并清理，request 移除，0 份含原文文件；不产生 emit |
| 正常 U→读 Skill→Stop→按实际 emit 精确回显→重复 Stop | 本轮未重复运行该正常对照 | selected 与原 D0 哈希相同；两次终态均 allow，delivery_verified=true，原文已清理 |

上述前两项调用实际 core 与实际 detect 子进程；只在宿主外测试驱动中安排暂停或持锁时序，没有替换 gate 检测结果。正常控制的最后回显是驱动逐字复制实际 selected，用于检查状态与哈希，不能证明任一模型或宿主自然回显的成功率。

[R2 精简结果](summary-r2.json)、[基线完整事件](baseline-r2/result.json)、[R2 完整事件](candidate-r2/result.json)、[R2 正常控制](normal-r2/result.json)分别保存。`raw_file_count` 按原文的字节匹配统计，不匹配 JSON 中经过转义的整段 request；因此另以 `request_in_record` 单独记录原文请求是否仍在，不能把文件计数 0 当成原始记录已脱敏。

首轮 [baseline-r1](baseline-r1/INVALID.md) 因驱动读取 Windows 锁定文件失败而无效，已保留，不计为产品结果。[candidate-r1](candidate-r1/result.json) 是首次风险下降原型。随后名称为 [candidate-final](candidate-final/result.json) 的 R1 收口候选仍被独立复核拒绝；它及[复核前报告](result-r1-before-independent-review.md)完整保留，不能按目录中的 final 字样当成最终准入结果。

两项新增反例及 R2 修正分别留证：

- [回执刷新 R1](receipt-refresh-r1/result.json)：已有脱敏失败回执，Stop 或 HostAbort 中一次 `os.replace` 故障会删掉旧回执，下一 Stop 误 allow。[R2](receipt-refresh-r2/result.json)在两触发下都保留原回执字节与邻居记录，后续继续 `continue:false`。这是标明的合成终态故障反控，没有伪装成真实 D0。
- [相邻 turn R1](turn-collision-r1/result.json)：实际核心用同一真实 D0 启动 `t-inputs` 后，仅取消尚未 bootstrap 的 `t`，前者活动事务被删，后续虽 allow 却未验证交付。[R2](turn-collision-r2/result.json)保留活动事务全部文件哈希，精确回显后 `delivery_verified=true`。[基线控制](turn-collision-baseline/result.json)也保留该事务。`_safe_key` 接受这两个 ID，不能假定所有适配器永远提供 UUID。

## 最小变更

复用现有 bootstrap 锁、state 锁和终态：两个输入文件的原子写入与清理共用短 state 锁，detect 子进程仍在锁外；取消原因以独立 `.host-abort` 小标记保存，内容只含允许的原因值。首次写原文前在同一个状态原子写中记录无正文的 `bootstrap_artifacts=true`，脱敏后保留，只有具备该归属事实的 turn 才恢复派生清理路径。bootstrap 的 finally 和后续同 turn 事件重试清理。清理失败保留失败计数与取消标记；刷新已脱敏磁盘回执失败时保留旧回执，首次含 raw 回执仍保留既有隐私兜底；既有失败终态继续返回 `continue:false`。

必要直接反控已验证：晚到 HostAbort 和重复 Stop 不改变失败终态；清理锁仍不可用时保留原 producer 异常，正常返回路径停止而不继续 emit；删除失败不把失败计数记为 0，后续事件可恢复；相邻 turn 的记录和原文目录保持不变；持有 bootstrap 锁时清理函数不会 unlink 锁文件，也不能产生第二位锁拥有者。

## 验证与复用

先运行真实 D0 定向生命周期证明风险下降，再补反控。最终执行：

```powershell
python -B -X utf8 output/remaining-hook-quality-r1/cleanup/replay_cleanup.py --source-root output/remaining-hook-quality-r1/cleanup/source-candidate-r2 --sample output/remaining-hook-quality-r1/cleanup/sample.json --output output/remaining-hook-quality-r1/cleanup/candidate-r2
python -B -X utf8 output/remaining-hook-quality-r1/cleanup/replay_normal.py --source-root output/remaining-hook-quality-r1/cleanup/source-candidate-r2 --sample output/remaining-hook-quality-r1/cleanup/sample.json --output output/remaining-hook-quality-r1/cleanup/normal-r2
python -B -X utf8 output/remaining-hook-quality-r1/cleanup/replay_receipt_refresh.py --source-root output/remaining-hook-quality-r1/cleanup/source-candidate-r2 --output output/remaining-hook-quality-r1/cleanup/receipt-refresh-r2
python -B -X utf8 output/remaining-hook-quality-r1/cleanup/replay_turn_collision.py --source-root output/remaining-hook-quality-r1/cleanup/source-candidate-r2 --sample output/remaining-hook-quality-r1/cleanup/sample.json --output output/remaining-hook-quality-r1/cleanup/turn-collision-r2
python -B -X utf8 -m unittest maintenance.tests.test_gate_stop_hook -k host_abort -k bootstrap_finally -k redacted_stop_retries -k abort_delete_failure -k cleanup_cannot_unlink -k receipt_survives -k unbootstrapped_abort -k redaction_write_failure -k terminal_delivery_redacts -k terminal_user_and_tool_replay -v
git diff --check -- chinese-official-writing/hooks/core/gate_stop_hook.py maintenance/tests/test_gate_stop_hook.py
```

四份驱动均拒绝覆盖已存在的 output；复跑时须使用新的输出目录。四条 R2 复放均退出 0。[R2 直接单测](direct-tests-r2.log)：**15 项通过，3.578 秒**；包括首次 raw 回执写失败仍删除原文这一邻接反控。R1 曾运行 [core 全模块 63 项](core-tests-final.log)，27.328 秒通过；该旧结果不能冒充 R2 全模块重跑或掩盖独立复核发现的回退。总共新增 11 项直接测试。系统已有 `skill-creator/scripts/quick_validate.py chinese-official-writing` 返回 [Skill is valid](quick-validate-r2.log)。AST、证据 JSON、本文直链和 diff 检查见 [validation.json](validation.json)。没有运行全量门、没有重跑线上宿主。

基线的 canonical 86 文件通过 `git cat-file --batch` 原始字节导出；[R2 源清单](candidate-r2-source.json)只有 core 覆盖，Skill 等其余 85 文件仍固定为基线。并行 reference/adapter 更改不在该快照内；这里的纯生命周期证据可以按该明确边界迁移，不能声称当前整个工作树都被这次复放验证。原始输入、脚本、结果与验证日志的哈希见 [artifact-sha256.json](artifact-sha256.json)。

## 剩余边界

持续存储 I/O 不可用时不能保证完成删除；若连取消标记都无法写入，也不能保证恢复取消意图。短暂锁故障释放后，需要 bootstrap 拥有者退出或后续同 turn 事件来重试；没有事件的永久离线残留不由后台扫描解决。旧版已脱敏且已丢失事务归属的孤儿不按名称推断清理。原有两个 turn **都 bootstrap** 时的后缀目录命名碰撞仍是继承边界；本轮仅移除“未启动 turn 也可删除相邻活动事务”的新增触发面，没有做命名迁移或跨 turn 协调器。

这里只验证该 core 生命周期；adapter 是否及时发送 HostAbort、真实 Interrupt 的短超时和宿主中断行为由独立适配证据承担。

动手前核对了[官方 Hooks 文档](https://learn.chatgpt.com/docs/hooks)：Interrupt 针对正在运行的主任务，中断回包不能重新启动任务；其短预算支持“记录意图并由现有生命周期恢复”的做法。[Codex 社区取消问题](https://github.com/openai/codex/issues/42511)仅作问题线索，不作为本候选通过证据。
