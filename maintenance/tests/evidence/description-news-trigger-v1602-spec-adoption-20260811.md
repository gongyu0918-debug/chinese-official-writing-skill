# Description 精简规格纳入说明

日期：2026-08-11

结论：`USER-SPECIFIED CONSERVATIVE ENTRY / TWO-PROVIDER NON-INFERIOR SIGNAL / THREE-PROVIDER GATE NOT ESTABLISHED / NO QUALITY-UPLIFT CLAIM`

## 产品范围

- 固定历史基线：`9abc48794ebf82b8e918c593ebdada8cc080fe61`。
- 已验证的隔离候选：`387882c077b3c78801b7f1a63524fca886ab87fc`。
- 本次把活跃 GitHub/SkillHub 运行面的 description 首句收敛为能力说明：“用于中文公文、事务性材料和新闻稿件的起草、改写、压缩和复核”。机关、企事业单位、学校和新闻机构四类入口后置保留；末句“个人求职”排除项保留。后续文种词表、正向新闻别名和其他排除项不变。只压缩“明确要求”“对这类材料做”等重复连接语，不删触发文种；最终长度为 280 字。
- 已冻结的 OpenClaw/ClawHub v1.6.0 不随本次改动。

## 既有真实路由证据

原矩阵使用 Alibaba DeepSeek V4 Flash 0731、Ollama DeepSeek V4 Flash 0731 和 MiniMax M3，均为 `max`；42 次调用全部为首个 final、零重试。Candidate 曾出现一次个人求职题独有读取，另有一次新闻题未读取；同时存在四个全局同名 Skill 污染样本。该轮没有证明新闻路由增益，也不能把单次反向信号归因为稳定回退。

随后对个人求职/简历负向和新闻正向做 48 次新鲜配对复放：

- 明含“个人求职”的 18 个臂均未路由；原 Alibaba Candidate 单例未复现；
- “校招求职信”的少量路由在三家 provider 间方向相反；
- 新闻有效配对大多两臂均路由，只有一个 MiniMax 单对 Candidate 正向差异，未跨 provider 复现；
- 7 个读取全局副本的新闻臂按预注册作废。

两轮合计 90 次真实路由调用。结果支持“没有确认出稳定 Candidate 独有错路由”，不支持“Candidate 提高新闻流量”或“整体写稿质量提升”。

## 本次裁决

用户在看到较宽候选的路由结果后，最终收窄规格：首句只说明能力，四类单位范围后置，不删除“个人求职”。该 280 字候选又做了三轮、48 次正式路由调用：

- Ollama Cloud：4/4 配对有效；
- Alibaba `tokenplan2`（实际 provider id `alibaba-token-plan-2`）：4/4 配对有效，未回退旧 Token Plan；
- MiniMax M3：最终只有 2/4 配对有效。即使同时隔离 `HOME`、`USERPROFILE` 和 `CODEX_HOME`，N1/O1 仍读取 Windows 实际用户 KnownFolder 下的 `.agents` 同名 Skill，按预注册作废。

有效样本没有形成跨 provider 重复的 Candidate 独有错路由。唯一 Candidate 独有信号是 Ollama 的一个事务正向题未读取 Skill；同一 provider 的另一负向题则为 Baseline 独有误触发，方向不一致。严格的“三 provider 每家至少三对”门槛没有满足，因此不能写成三 provider 非劣通过，也不能宣称新闻流量提升。

用户明确把能力优先、新闻前置、单位范围后置和保留“个人求职”作为人类可读的入口规格。本次在完整披露 MiniMax 污染和严格门未建立的前提下按用户规格纳入；Ollama 与 Token Plan 2 的八个有效配对仅作为未见稳定回退的支持信号。

原始结果仍保留在隔离分支：

- `tests/evidence/description-news-trigger-v1601-real-route-result-20260811.md`
- `tests/evidence/description-news-trigger-v1601-n4-news-replay-result-20260811.md`
- `codex/description-conservative-route-v1602@359f08310a1ceb443ed055ff772f0f7c782c443e`

本原子未发布、未修改 `main`、未触碰 ClawHub。
