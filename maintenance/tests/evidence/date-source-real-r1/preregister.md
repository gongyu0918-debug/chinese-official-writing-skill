# 日期来源角色：自然真实 D0，R1

固定产品基线为 `5fbb2d26c49d0b780ad11fc4cff008854995ad3f`，本轮先不应用旧日期补丁。两条既有低价路线各写一份同题真实 D0：`alibaba-token-plan-2/deepseek-v4-flash-0731`、`minimax-cn/MiniMax-M3`，均为 `max`，不补抽样、不改造 D0、不自动切换模型。

题面见 [case.json](case.json)：目标活动事实日期为 ISO `2026-09-05`，中文 `2020年9月5日` 明确仅为格式示例且不得进入消息。让模型自然选择日期写法；不要求月日格式。最初提出的指定“9月5日”设计在冻结前经代码检查发现会触发现有裸月日旁路，已取消；该设计未调用模型、未生成 D0。

模型使用现有 Claude CLI 和低价调用环境。内置工具设为空，关闭 Skills，仅允许空 MCP 配置并使用 strict MCP 和 dontAsk；不得提供 Shell、网络、注册表或文件写入工具。以 init 工具/MCP/Skills 清单及实际 tool_use 记录检查禁用结果，模型身份在 init、assistant、usage 三处绑定。技术失败保留，不自动重试。

为遵守无工具要求，Harness 将固定基线的 `SKILL.md` 和 `references/genre-playbook-news-message.md` 原文读入并提供为上下文，逐文件记录 hash。这是固定上下文的日期目标实验，不评估模型主动选读路由或完整 Skill 代理工作流。

每份技术有效的真实 D0 原样进入同一基线默认 `delivery_review`。复用 [六稿重放脚本](../hook-audit-quality-r1/replay_real_d0.py) 的真实 core 子进程；Skill 激活事件映射自 Harness 的实际上下文文件读取，明确不是 Claude 模型工具读取或原生宿主 Hook 安装证明。每个 block，包括逐字回显，继续使用同路线、同样禁用全部工具的真实模型回复，最多四次；保存全部输入、回应、事件与 hash。

只有真实 D0 未写错年，而同 D0 默认 Hook 实际把示例年份写入活动，才进入候选验证。届时仅对同 D0 验证最小保守旁路，并增加一条正常中文完整事实日期反控；不接入 adapter、镜像或其他终态工程。若两份自然 D0 都无法复现，记 `NOT_REPRODUCED`，停止候选，旧日期补丁保持 `NOT_ADMITTED`；不把未复现当作不存在已知离线缺陷。

先执行 `run.py --prepare --output <NEW_OUTPUT> --core-root <BASELINE_TREE>` 冻结完整上下文及脚本指纹，再分别以 `--provider alibaba2` 和 `--provider minimax` 运行。输出目录必须全新；完成、失败及孤立 raw 均不得覆盖。

运行后记录见 [结果](result.md) 与 [两稿及四次调用证据](result.json)；本预登记创建时尚未执行模型调用。
