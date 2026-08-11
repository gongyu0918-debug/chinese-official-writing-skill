# Description 精简规格纳入说明

日期：2026-08-11

结论：`USER-SPECIFIED ENTRY RELIEF / NO STABLE ROUTING REGRESSION / NO QUALITY-UPLIFT CLAIM`

## 产品范围

- 固定历史基线：`9abc48794ebf82b8e918c593ebdada8cc080fe61`。
- 已验证的隔离候选：`387882c077b3c78801b7f1a63524fca886ab87fc`。
- 本次只把活跃 GitHub/SkillHub 运行面的 description 首句改为“用于中文公文、事务性材料、新闻稿件起草、改写、压缩和复核”，并从末句删去“个人求职”。后续文种词表、正向新闻别名和其他排除项不变。
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

用户再次明确把该文字作为入口减载和人类可读性规格，而不是以路由质量提升为合入前提。结合 48 次复放已撤销最初单例回退推断，本次按用户规格纳入；证据口径只写减载与未见稳定路由回退。

原始结果仍保留在隔离分支：

- `tests/evidence/description-news-trigger-v1601-real-route-result-20260811.md`
- `tests/evidence/description-news-trigger-v1601-n4-news-replay-result-20260811.md`

本原子未发布、未修改 `main`、未触碰 ClawHub。
