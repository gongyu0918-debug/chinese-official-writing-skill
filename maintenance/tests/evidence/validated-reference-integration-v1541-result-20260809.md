# 已验证 reference 原子干净集成结果（2026-08-09）

集成分支：`codex/validated-reference-integration-v1541`

固定底座：`main=fb52e16dc94566d55eb679d3efdf2cbe19113513`

产品提交：`dc8733c4`

## 结论

`PASS / ELIGIBLE FOR LOCAL MAIN FAST-FORWARD`。

本集成只纳入“连续否定式收口”R2 反例簇及 R3 正向会议状态承载。运行时产品差异为 canonical `anti-ai-patterns.md` 同一项目和五份机械镜像；未修改 SKILL、路由、脚本、Hook、FSM、终稿阶段或发布面。

此前通过真实复核的报告审批边界半句去重提交 `7ee89106` 已是当前 `main` 的祖先，并已表现为“使用事实性汇报语言”单句，因此本分支没有重复挑选或产生新差异。请示顺序候选、两步骨架候选、精确 detector、无缺口收口、短通知路由和脚本区块前移均未带入。

## 五提交暂停复核

集成分支从固定底座累计 5 个提交后暂停扩面，完成精确 diff、镜像哈希、完整回归、stub smoke、固定消融、Skill 校验、diff check 和 Git 对象检查。

- `git diff --name-status main...HEAD`：六份 `anti-ai-patterns.md`、一项测试文件、一项确定性消融锚点和四份预注册/结果证据；没有其他产品文件。
- 六份 reference SHA-256 唯一值：`13C0E821AEAEC6171F00D76390CD619AD39E81A1BB217F0182081E1C4D9032EF`。
- `git fsck --full --no-reflogs` 返回 0；仓库历史存在大量 dangling 对象，仅作既有历史状态记录，不属于本候选损坏。

## 实际工程门

| 检查 | 结果 |
| --- | --- |
| 连续否定聚焦测试 | 2/2 PASS |
| `python -B -m unittest discover -s tests -p 'test_*.py'` | 458/458 PASS |
| `OFFICIAL_WRITING_EVAL_STUB=1; npm.cmd run eval:official-writing:smoke` | 20/20 PASS，0 failure，0 error |
| Skill Creator `quick_validate.py` | `Skill is valid!` |
| 固定确定性消融 | `main-fb52e16d` 110/111；Candidate 111/111 |
| 消融唯一差项 | 旧 main 没有新的 P109“连续否定式收口”语义锚 |
| 镜像一致性 | 6/6 同 SHA-256 |
| `git diff --check` | PASS |

这些是工程和加载边界证据，不替代真实写稿。

## 真实写稿与盲审

Alibaba Token Plan 与 Ollama Cloud 的 DeepSeek V4 Flash 0731 均以 `max` 完成 R2/R3 单变量改稿。两家 R3 都把连续否定尾句收成“6月25日，馆务会仅听取相关情况”，保留 2 台、6月1日至20日、318 次、6月25日及未作采购决定的状态含义，没有新增采购、预算、责任、评估、整改或后续动作。

干净匿名裁判 `gpt-5.6-sol` `max` task `019fe4fb-d4d4-7032-8e59-490e3d32051c` 对两组均判 R3 `PASS`、R2 `WARN`、R3 胜。首个存在过程旁白的裁判分歧、无工具读取的分支复放和失败 CLI 调用均完整保留在 `anti-ai-negative-close-v1541-r3-real-result-20260809.md`，未计入有效胜负。

## 合入边界

只允许本地 `main` 快进到本集成 HEAD。此次不移动 `v1.5.40` tag，不推送远端，不创建 Release，不发布 GitHub、ClawHub、skillhub.cn 或其他平台。
