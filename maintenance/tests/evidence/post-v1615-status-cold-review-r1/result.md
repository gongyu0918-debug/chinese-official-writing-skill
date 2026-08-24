# v1.6.15 后状态回填双模型冷审结果

日期：2026-08-25。

## 结论

`PASS_DUAL_COLD_REVIEW / SOURCE_BOUNDARY_CLEAN / MINIMAL_STATUS_CLEANUP_APPLIED`。

两位审稿者均在全新 Codex CLI 只读会话中审查固定 `main@8aab5e61`、状态回填 `b9950f8a` 和 `v1.6.14..v1.6.15` 产品差异。Kimi K3 与 Grok 4.6 的有效终判均为 `PASS`，没有 P0、P1 或 P2；均确认状态回填没有夹带 canonical 产品、Hook、adapter、普通镜像或付费源码，公开/付费边界为 `CLEAN`。

## 有效审稿

| 审稿者 | Codex session | 推理强度 | 终判 | 原始输出 |
| --- | --- | --- | --- | --- |
| `ollama-cloud/kimi-k3` | `01a0347c-918b-77f0-bf56-e24e66fcf782` | max | `PASS / SOURCE_BOUNDARY:CLEAN`；无 P0/P1/P2 | `output/post-v1615-status-cold-review-r1/kimi-k3-final.md`，SHA-256 `cec6e9772b1162979afdb459f61f158aaa24d3d563b337ee49514c068419bd89` |
| `xai/grok-4.6` | `01a0349b-29ba-74d1-8da2-37f040f331b4` | high | `PASS / SOURCE_BOUNDARY:CLEAN`；无 P0/P1/P2 | `output/post-v1615-status-cold-review-r1/grok-4.6-r4-final.md`，SHA-256 `e246344fa5dbac0f67ebc28efb2961bec7db602e5eb92410ee40714312bb4cb9` |

Kimi 终端记 `tokens used=7,480,739`，其中包含其逐文件读取产生的大量输入与缓存计数；Grok 最终无工具审查包记 `tokens used=54,433`。二者只用于冷审，不是写稿质量票数。

## 失效执行

- Grok R1 `01a0347c-91d5-7c33-9919-53714168d403`：约25分钟后仍扩大读取、没有终判，人工停止，`TECH_INVALID_NO_FINAL`。
- Grok R2 `01a03495-087d-7ce1-8845-f4fe243bb728`：只读策略反复拒绝组合命令并超过12次尝试，人工停止，`TECH_INVALID_TOOL_POLICY_LOOP`。
- Grok R3 `01a03498-80d8-74a0-bdea-7c03b02ffad3`：wrapper 未把管道包附加到参数 prompt；模型正确拒绝空包，`TECH_INVALID_PACKET_NOT_DELIVERED`。原始输出 SHA-256 `4694296273daee2fad28ec6fd24d9aa1838bd23a249156797588705f604544ea`。
- R4 改用支持 pipeline 的真实 Codex CLI shim，把指令和精确 Git 审查包全部经 stdin 送入；终端回显了完整 `<review_packet>`，模型不调用工具后形成有效终判。

## 可复现发现与处理

两份冷审只有非阻断状态措辞问题，已最小处理：

1. `待办.md` 的“v1.6.14 已发布状态”旧标题改为“v1.6.14 起已发布状态与后续研究”；
2. 根 README 的 v1.6.12 历史行不再把已收口候选统称“保持 HOLD”，改为“未进入公开版”；
3. 付费候选终态统一为 `DONE_LOCAL_PAID_NO_RELEASE`；
4. `WR-020b1` 明确区分任务卡候选 `REJECTED` 与沿该机制继续收窄的实现方向 `TERMINATED`。

Kimi 另说明其只做静态冷审，未在审稿沙箱复跑 Python；主审必须另行执行实际回归。Grok 没有发现其他从固定输入包可证实的问题。

## 主审回归

- `git diff --check`：通过；仅有 Windows 后续检出换行提示，无空白错误。
- `python -m unittest maintenance.tests.test_status_ledger_consistency maintenance.tests.test_repository_reachability maintenance.tests.test_skill_boundary`：91/91 通过。
- `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：通过，输出 `Skill is valid!`。
- 相对固定 main 共44个差异路径；`chinese-official-writing/`、`hooks/`、`packages/` 产品或镜像路径为0。新增根 README 差异只清理公开历史表中的旧 HOLD 措辞。

## 边界

本结果只支持状态回填与上述状态措辞清理，不证明 `OC-003` 产品候选可合入，也不替代下一轮短稿真实写稿。没有 push、tag、Release 或平台写入；付费源码仍只在本地付费分支。
