# 项目维护历史索引

本目录保存不需要在每次 Codex run 中注入、但必须长期可追溯的项目维护记录。这里的材料是证据和历史背景，不是当前运行时指令；当前规则以仓库根 [`AGENTS.md`](../../../AGENTS.md) 为准。

## AGENTS 历史快照

- [`AGENTS-control-plane-v1.6.0-pre-v1601.md`](AGENTS-control-plane-v1.6.0-pre-v1601.md) 是本轮进一步去重前的 v1.6.0 轻量工程控制面快照；与当时根文件规范化文本一致。
- [`agents-control-plane-v1601-result-20260811.md`](../../tests/evidence/agents-control-plane-v1601-result-20260811.md) 记录去重候选的 Kimi、Grok、Qwen 匿名审查、一次上下文污染作废及共同意见修正。
- [`AGENTS-history-through-v1.5.39.md`](AGENTS-history-through-v1.5.39.md) 是精简前根 `AGENTS.md` 的完整 Git blob 快照，覆盖 1.4.1—1.5.39 的发布、接手、候选实验、阻断、回滚、评测和平台传播流水。
- 为保持迁移前后事实和检索关键词完全一致，快照正文未改写。正文中的 `tests/evidence/...`、`tools/...`、`output/...` 等路径均以仓库根为起点解释，不以本目录为起点。
- 快照中的“当前”“最新”“待发布”等措辞只表示记录写入当时的状态，不覆盖根 `AGENTS.md` 的当前发布基线。

## 逐版发布证据

- v1.6.20 的 GitHub、SkillHub.cn 与 ClawHub 发布回执见 [`release-1.6.20.md`](../../tests/evidence/release-1.6.20.md)；本地候选固定基线、AH-002 真实生命周期、四个 references 减载原子的终态、发布门和两类平台包预检见 [`release-1.6.20-rc.md`](../../tests/evidence/release-1.6.20-rc.md)。
- v1.6.20 当前无字数限制事务稿的五路15份真实写稿、合理推断边界、篇幅诊断和残余风险见 [`short-inference-r1/baseline-result.md`](../../tests/evidence/short-inference-r1/baseline-result.md)；目标原子 `WR-013d/WR-018-R2` 转为 `WAIT_NEW_COUNTEREXAMPLE`，普通写稿规则未改。
- v1.6.20 后 `UL-005-R10` 扩写指令与 verifier 合理推断口径的四轮75份候选/基线真实稿、稀疏精确回退、五提交 checkpoint 和最终未合并候选见 [`short-inference-r1/underlength-r4-result.md`](../../tests/evidence/short-inference-r1/underlength-r4-result.md)；R1—R3 失败及最小修复分别保留在同目录。
- v1.6.19 后四个 references 减载原子的190次五路真实任务、实际读取、最小R2、逐稿复核与终态见 [`reference-slimming-r1/result.md`](../../tests/evidence/reference-slimming-r1/result.md)；四项产品均恢复发布基线，无Hook、包体、description或版本变化。
- v1.6.19 的 GitHub、SkillHub.cn 与 ClawHub 发布回执见 [`release-1.6.19.md`](../../tests/evidence/release-1.6.19.md)；本地候选范围、Hermes 与 DeepSeek Harness 真实生命周期依据、固定基线验证和两类平台包预检见 [`release-1.6.19-rc.md`](../../tests/evidence/release-1.6.19-rc.md)。
- v1.6.18 的 GitHub、SkillHub.cn 与 ClawHub 发布回执见 [`release-1.6.18.md`](../../tests/evidence/release-1.6.18.md)；本地候选范围、OpenCode 真实交互依据、固定基线验证和两类平台包预检见 [`release-1.6.18-rc.md`](../../tests/evidence/release-1.6.18-rc.md)。
- OpenCode 1.18.23 / Hermes Agent 0.20.0 的首轮生命周期研究、当前 Skill 三题真稿、OpenCode 同稿收益、Alibaba Token Plan 2 交互共享门禁、无头旁路、竞态修复和当时 Hermes `BASELINE_NOT_REPRODUCED` 终态：[`hk004-opencode-hermes-r1/result.md`](../../tests/evidence/hk004-opencode-hermes-r1/result.md)。OpenCode adapter 已随 v1.6.18 发布。后续 Hermes Agent 0.20.5—0.20.6 单次语义复核重开、跨线程预载修复、真实采购/情况说明、固定 D0 223→182、post hash 闭合、transform 前持久化反例、新建 inline/query-file 边界和未发布 adapter 候选见 [`hk004-hermes-r2/result.md`](../../tests/evidence/hk004-hermes-r2/result.md)。
- DeepSeek Harness 0.1.1-rc.2 官方 bridge 的 Stop/D0 缺口、原生 Profile Bundle、OpenCodex provider-default/max 精确配置、两份当前 Skill 真稿、多 Stop/hash/脱敏与本轮 Qoder `DEFERRED_BY_USER` 边界见 [`hk004-deepseek-harness-r1/research.md`](../../tests/evidence/hk004-deepseek-harness-r1/research.md) 和 [`result.md`](../../tests/evidence/hk004-deepseek-harness-r1/result.md)。
- v1.6.17 的 GitHub、SkillHub.cn 与 ClawHub 发布回执见 [`release-1.6.17.md`](../../tests/evidence/release-1.6.17.md)；本地候选范围、真实写稿依据、测试和两类平台包预检见 [`release-1.6.17-rc.md`](../../tests/evidence/release-1.6.17-rc.md)。
- v1.6.16 的 GitHub、SkillHub.cn 与 ClawHub 发布回执见 [`release-1.6.16.md`](../../tests/evidence/release-1.6.16.md)；本地候选范围、OC-003 真实写稿依据、测试、清洁包和 dry-run 记录见 [`release-1.6.16-rc.md`](../../tests/evidence/release-1.6.16-rc.md)。
- v1.6.15 的 GitHub、SkillHub.cn 与 ClawHub 发布回执见 [`release-1.6.15.md`](../../tests/evidence/release-1.6.15.md)；本地候选范围、真实写稿依据、测试、清洁包和 dry-run 记录见 [`release-1.6.15-rc.md`](../../tests/evidence/release-1.6.15-rc.md)。
- v1.6.14 的 GitHub、SkillHub.cn 与 ClawHub 发布回执见 [`release-1.6.14.md`](../../tests/evidence/release-1.6.14.md)；本地候选范围、真实写稿依据、测试、清洁包和 dry-run 记录见 [`release-1.6.14-rc.md`](../../tests/evidence/release-1.6.14-rc.md)。
- v1.6.13 的 GitHub、SkillHub.cn 与 ClawHub 发布回执见 [`release-1.6.13.md`](../../tests/evidence/release-1.6.13.md)；本地候选范围、真实写稿依据、测试、清洁包和 dry-run 记录见 [`release-1.6.13-rc.md`](../../tests/evidence/release-1.6.13-rc.md)。
- v1.6.12 的 GitHub、SkillHub.cn 与 ClawHub 发布回执见 [`release-1.6.12.md`](../../tests/evidence/release-1.6.12.md)；本地候选范围、真实写稿、测试、清洁包和 dry-run 记录见 [`release-1.6.12-rc.md`](../../tests/evidence/release-1.6.12-rc.md)。
- v1.6.11 的 GitHub、SkillHub.cn 与 ClawHub 发布回执见 [`release-1.6.11.md`](../../tests/evidence/release-1.6.11.md)；本地候选范围、清洁包、验证和 dry-run 记录见 [`release-1.6.11-rc.md`](../../tests/evidence/release-1.6.11-rc.md)。
- v1.6.10 的 GitHub、SkillHub.cn 与 ClawHub 发布回执见 [`release-1.6.10.md`](../../tests/evidence/release-1.6.10.md)；本地候选范围、清洁包、验证和 dry-run 记录见 [`release-1.6.10-rc.md`](../../tests/evidence/release-1.6.10-rc.md)。
- v1.6.9 的 GitHub、SkillHub.cn 与 ClawHub 发布回执见 [`release-1.6.9.md`](../../tests/evidence/release-1.6.9.md)；本地候选范围、清洁包、三宿主静态组装和验证记录保留在 [`release-1.6.9-rc.md`](../../tests/evidence/release-1.6.9-rc.md)。
- 超长收束、短稿局部去重和 README 制度示例的真实稿先行、Claude Code 在线 D1 与 SOL max 终审：[`v168-overlength-shortdraft-real-first/result.md`](../../tests/evidence/v168-overlength-shortdraft-real-first/result.md)。当前 GitHub、SkillHub.cn 与 ClawHub 发布回执见 [`release-1.6.8.md`](../../tests/evidence/release-1.6.8.md)，本地候选边界、冷审修复、测试与组包记录见 [`release-1.6.8-rc.md`](../../tests/evidence/release-1.6.8-rc.md)。
- 上一 GitHub、SkillHub.cn 与 ClawHub 发布证据：[`release-1.6.7.md`](../../tests/evidence/release-1.6.7.md)。对应本地候选记录保留在 [`release-1.6.7-rc.md`](../../tests/evidence/release-1.6.7-rc.md)。
- 上一 GitHub 与 SkillHub.cn 发布证据：[`release-1.6.6.md`](../../tests/evidence/release-1.6.6.md)。本地候选边界、测试和组包记录保留在 [`release-1.6.6-rc.md`](../../tests/evidence/release-1.6.6-rc.md)。
- 上一 GitHub 与 SkillHub.cn 发布证据：[`release-1.6.5.md`](../../tests/evidence/release-1.6.5.md)。对应候选、Codex 并发读取修复、CodeBuddy 静态迁移和候选包哈希保留在 [`release-1.6.5-rc.md`](../../tests/evidence/release-1.6.5-rc.md)。
- 上一正式发行版见 [`release-1.6.4.md`](../../tests/evidence/release-1.6.4.md)；更早版本与上一版 Hook 真实写稿结果分别见 [`release-1.6.3.md`](../../tests/evidence/release-1.6.3.md) 和 [`v162-hook-writing-real-ab-final-result-20260812.md`](../../tests/evidence/v162-hook-writing-real-ab-final-result-20260812.md)。
- v1.6.4 后篇幅不足 Hook 最新真实写稿、Codex/Claude 在线 D1 与 SOL max 结果：[`v164-under-length-real-first-result-20260814.md`](../../tests/evidence/v164-under-length-real-first-result-20260814.md)。第一次只会回退 D0 的三宿主记录继续保留在 [`v164-under-length-three-host-live-result-20260814.md`](../../tests/evidence/v164-under-length-three-host-live-result-20260814.md)。
- v1.6.10 后篇幅验收自审、类别收紧和同模型独立 verifier Agent 的真实复测及 HOLD 结论：[`post-v1610-underlength-verifier-risk-20260820.md`](../../tests/evidence/post-v1610-underlength-verifier-risk-20260820.md)。
- v1.6.11 后 `UL-005` 来源完整性原型、`OT-001` Stop 收紧、WorkBuddy / CodeBuddy 的 OV/提纲生命周期、description 减载、竞品原子和状态冲突收口：[`post-v1611-research-closeout-20260820.md`](../../tests/evidence/post-v1611-research-closeout-20260820.md)。
- v1.6.11 后 description HOLD 的18次扩大写稿、会议争议来源原子、联网来源用途/停止原子及 main→付费同步：[`post-v1611-expanded-real-writing-20260820.md`](../../tests/evidence/post-v1611-expanded-real-writing-20260820.md)。
- v1.6.11 后 SkillHub / ClawHub 当前在线73项发现、综合与单原子竞品复核、许可证边界及会议承诺语义真实 A/B：[`post-v1611-live-market-refresh-20260820.md`](../../tests/evidence/post-v1611-live-market-refresh-20260820.md)。
- v1.6.11 后 `UL-005` 单稿事实台账的简单对抗题、跨 span/同义改写缺口与 WorkBuddy / CodeBuddy 无效生命周期：[`ul005-fact-ledger-r2-live-20260821.md`](../../tests/evidence/ul005-fact-ledger-r2-live-20260821.md)。
- v1.6.12 后 `UL-005` 同一事实 span 的正反 CodeBuddy 生命周期、61→111风险 D1 回退和61→114受控 D1 选择：[`ul005-fact-ledger-r9-codebuddy-20260822.md`](../../tests/evidence/ul005-fact-ledger-r9-codebuddy-20260822.md)。该结果取代 R2 HOLD 的当前状态，旧失败证据保留。
- v1.6.11 后新闻声明级三冲突来源矩阵与安全正文 A/B，含局部改善、后续硬回退和最终 HOLD：[`post-v1612-news-claim-matrix-result-20260821.md`](../../tests/evidence/post-v1612-news-claim-matrix-result-20260821.md)。固定题面和预注册分别见 [`post-v1612-news-claim-matrix-prompt.txt`](../../tests/evidence/post-v1612-news-claim-matrix-prompt.txt)、[`post-v1612-news-claim-matrix-preregister-20260821.md`](../../tests/evidence/post-v1612-news-claim-matrix-preregister-20260821.md)。
- v1.6.12 后 `WR-011` 三轮25份真实稿、三次原子修正、五路最终候选和镜像回归：[`post-v1612-news-claim-matrix-r3-result-20260822.md`](../../tests/evidence/post-v1612-news-claim-matrix-r3-result-20260822.md)。该结果取代上一轮 HOLD，新闻叶及四套镜像已进入本地 main；旧失败证据保留不改。
- v1.6.12 后联网来源用途分型、有限补搜、同一实际打开页元数据与 URL 绑定的 R2d—R2h 五路真实写稿：[`online-source-use-r2h-result-20260822.md`](../../tests/evidence/online-source-use-r2h-result-20260822.md)。用途和命中页绑定完成；严格一次工具调用保留为非确定性限制。
- v1.6.12 后一般原因/即时作用、活动发布者角色和非新闻控制的五路真实写稿：[`wr013b-r8-role-effect/result-r84.md`](../../tests/evidence/wr013b-r8-role-effect/result-r84.md)。
- v1.6.13 后 `HK-008` 终态数据减载、SkillHub 扫描分歧复核、84项回归及 CodeBuddy 2.115.0 真实 Stop 生命周期：[`hk008-retention-redaction-20260822/result.md`](../../tests/evidence/hk008-retention-redaction-20260822/result.md)。
- v1.6.14 后 `HK-008b` 启动失败、缺 state、中断恢复、并发 owner、锁 I/O 分流和起草分类结果：[`hk008-bootstrap-cleanup-r1/result.md`](../../tests/evidence/hk008-bootstrap-cleanup-r1/result.md)。可归因产品原子已进入 v1.6.15。
- v1.6.14 后国产 CLI Hook 研究：[首轮 Qwen/Kimi/ZCode 边界与 ZCode companion](../../tests/evidence/domestic-cli-hooks-v1615/result.md)；[Qwen native extension 与 Kimi native plugin 的当前 Skill 真实写稿、Stop、hash/wire 和宿主限制复核](../../tests/evidence/domestic-cli-hooks-v1615/result-r2.md)。后者取代首轮关于 Qwen/Kimi 无 adapter 的阶段性结论，三个公开 adapter 已进入 v1.6.15。
- v1.6.14 后术语/行业词/英文/翻译腔、长报告/讲话、会议规则状态和 description 制度簇的在线竞品、官方语料及原子预注册：[`post-v1614-writing-quality-r1/market-corpus-research.md`](../../tests/evidence/post-v1614-writing-quality-r1/market-corpus-research.md)、[`post-v1614-writing-quality-r1/preregister.md`](../../tests/evidence/post-v1614-writing-quality-r1/preregister.md)。当前仅为研究与真实写稿入口，不等于产品已接入。
- 同轮真实写稿结果：[`WR-019d翻译腔`](../../tests/evidence/post-v1614-writing-quality-r1/wr019d-r2-result.md)、[`WR-019c英文/标准译名`](../../tests/evidence/post-v1614-writing-quality-r1/wr019c-r3-result.md)、[`WR-020长报告/讲话`](../../tests/evidence/post-v1614-writing-quality-r1/wr020-longform-result.md)、[`WR-010-M2会议规则状态`](../../tests/evidence/post-v1614-writing-quality-r1/wr010-m2-result.md)、[`MT-005b6/b6a description`](../../tests/evidence/post-v1614-writing-quality-r1/mt005b6-result.md)。019c/019d已进入 v1.6.15；其余按各自结果保留当前基线。
- `WR-020a1` 内部决策分析前置结论两轮缩小、`WR-014-R4` 三态/长报告/同一D0修正和 provider 技术失败：[`预注册与迭代`](../../tests/evidence/post-v1614-writing-quality-r2/preregister.md)、[`结果`](../../tests/evidence/post-v1614-writing-quality-r2/wr020a1-wr014-r4-result.md)。020a1首次起草拒绝；R4复核/改稿单句已进入 v1.6.15。
- `WR-014-R5` 采购总体决定、局部未定节点和具体采购阶段三题的五路 Codex Desktop 写稿、官方表达校准及 Hook 只读诊断：[`结果`](../../tests/evidence/wr014-r5-procurement-state-scope/result.md)。四个范围有效样本的目标层级4/4通过，其中两稿另有输出形状或材料外事实硬失败；当前产品对本目标足够，不新增禁词、reference、Hook或adapter。
- v1.6.16 后 `WR-014-R6/R6b`、`WR-013c`、`WR-020a2` 的持续动作、证据可见性、短采购影响强度和长稿结论范围真实写稿：[`预登记`](../../tests/evidence/post-v1616-writing-stability-r1/preregister.md)、[`官方校准`](../../tests/evidence/post-v1616-writing-stability-r1/research.md)、[`结果`](../../tests/evidence/post-v1616-writing-stability-r1/result.md)、[`五提交复核`](../../tests/evidence/post-v1616-writing-stability-r1/five-commit-review.md)。没有跨模型共同目标失败，产品0差异；Ollama长稿两次技术失效和7份有效稿中6份正文外包装如实保留。
- `WR-020b1` 讲话输入任务卡三次最小收窄的真实写稿与拒绝结果：[`预注册`](../../tests/evidence/wr020b1-speech-task-card/preregister.md)、[`结果`](../../tests/evidence/wr020b1-speech-task-card/result.md)。任务卡候选为 `REJECTED`，沿首次起草任务卡继续收窄的实现方向为 `TERMINATED`；后续只研究已有稿任务段的精确复核、搬移或删除。
- `WR-020b2a` 已有讲话稿单段精确搬移的四路真实改稿：[`结果`](../../tests/evidence/post-v1615-backlog-recovery-r1/wr020b2a-speech-move-result.md)。三条严格有效路线均只搬移目标段，当前产品已覆盖，不增加新规则。
- `WR-020b2b` 已有讲话稿材料外任务句的精确删除：[`结果`](../../tests/evidence/post-v1615-backlog-recovery-r1/wr020b2b-speech-delete-result.md)。Alibaba/Luna有效路线洁净通过；Ollama删除正确但正文包装失败，风险保留，不重复堆规则。
- `WR-020b2c` 已有讲话稿任务段归属与材料外责任的三路只审定位：[`结果`](../../tests/evidence/post-v1615-backlog-recovery-r1/wr020b2c-speech-review-result.md)。三路均命中预登记问题；同时发现样稿还有联络人段错挂和方法自述，当前产品已覆盖，不为题面遗漏新增规则。
- `OC-003` 算力可研状态、程序与完整性审稿：早期研究已由[`R2分层结果`](../../tests/evidence/oc003-r2-state-layering/result.md)取代；后续[`R3点名完整性与渐进路由`](../../tests/evidence/oc003-completeness-boundary-r3/result.md)用五个便宜 provider 验证减载后仍保留合理分析和四项实质缺口。[已合入能力冷审](../../tests/evidence/oc003-postmerge-cold-review-r1/result.md)仅使用 Grok 4.6 与 Kimi K3 做冷审，不计普通写稿准入。[R2状态收口](../../tests/evidence/oc003-status-closeout/result.md)。发布后的[状态谓语泛化原子](../../tests/evidence/oc003-state-predicate-general-r1/result.md)以36次有效真实复核/改稿终止产品泛化方向，v1.6.16 产品原文保持不变。
- v1.6.15 发布后一次点赞回落的 v1.6.14/v1.6.15 短稿同题诊断：[`预登记`](../../tests/evidence/v1615-like-signal-short-writing-r1/preregister.md)、[`结果`](../../tests/evidence/v1615-like-signal-short-writing-r1/result.md)。五路30臂未复现系统性偏短回退，但活动新闻完整年份在两版均4/5遗漏，MiniMax 候选另有材料外活动细节和代码块交付。
- `WR-001-DATE` 活动新闻完整日期原子的两轮最小化：[`R1`](../../tests/evidence/wr001-date-r1/r1-result.md)、[`R2`](../../tests/evidence/wr001-date-r1/r2-result.md)。候选均提升年份命中，但 Ollama 两轮材料外活动过程阻止准入；产品已恢复，重复提示词方向终止。
- `AH-002` 以不同机制处理同一风险：自然漏年基线、冻结写后续写、单一来源日期纯机械原型、歧义反控和三 provider 九次 Claude Code 真实生命周期见 [`live-result.md`](../../tests/evidence/ah002-news-date-completeness-r1/live-result.md)。Alibaba Token Plan 2 与 OpenCode Go 达到预登记门；实现已随 v1.6.20 发布至 GitHub 与 SkillHub.cn，ClawHub 继续无 Hook。
- v1.6.15 后恢复分支的短稿诊断、日期原子恢复、付费候选本地整合和30提交最终检查点：[`最终收口复核`](../../tests/evidence/post-v1615-backlog-recovery-r1/final-closeout-review.md)。该记录不改变 `main`、tag 或平台版本。
- v1.6.15 后 WR-020、OC-003、发布状态、旧 HOLD 终态和本地付费候选的纯维护 main 回填候选：[`状态回填结果`](../../tests/evidence/post-v1615-status-main-backfill-r1/result.md)。该候选排除 OC-003 产品 reference、镜像和全部付费源码。
- v1.6.15 后状态回填的 Kimi K3 / Grok 4.6 独立 Codex CLI 冷审、失效尝试和状态标记收口：[`post-v1615-status-cold-review-r1/result.md`](../../tests/evidence/post-v1615-status-cold-review-r1/result.md)。两份有效终判均为 `PASS / SOURCE_BOUNDARY:CLEAN`；原始输出保存在忽略目录，不进入公开产品。
- 本地付费权威状态：`codex/paid-outline-review` 收敛 OT-001/组合生命周期、OT-002 与 RF-001；以 current main 的祖先关系和付费 worktree 清洁状态核验同步，不在活动索引固化易过期 tip。详细源码和证据只留付费分支，公开 main、tag 和三个平台不含付费实现。
- v1.6.13 后 `OV-001` 超长判定校准与 sentence-target 原子：[`五路写稿`](../../tests/evidence/post-v1613-writing-atoms-r1-20260822/ov001-judgment-writer-result.md)、[`三题15/15判定`](../../tests/evidence/post-v1613-writing-atoms-r1-20260822/ov001-judgment-verifier-result.md)、[`CodeBuddy 328→236`](../../tests/evidence/post-v1613-writing-atoms-r1-20260822/ov001-judgment-live-result.md)、[`CodeBuddy 496→229`](../../tests/evidence/post-v1613-writing-atoms-r1-20260822/ov001-cb-r3-result.md)及[`四方盲审公开摘录`](../../tests/evidence/post-v1613-writing-atoms-r1-20260822/ov001-four-reviewer-extract.md)。
- `WR-014-R3` 能力/选项与计划意向的修正归因、五路 A/B 真实写稿和最终45字符状态锚：[`wr014-r3-capacity-plan-20260822/result.md`](../../tests/evidence/wr014-r3-capacity-plan-20260822/result.md)。
- `MT-005c` Codex CLI 同体 Skill 隔离 A/B 初轮结果：[`mt005c-codex-cli-20260822/result.md`](../../tests/evidence/mt005c-codex-cli-20260822/result.md)；合并前全量门发现“学校”关键词回退，196字最小回补虽触发正确但两份正向真实稿出现状态/安排硬失败，最终拒绝接入并恢复204字：[`mt005c-school-repair-followup-20260823.md`](../../tests/evidence/mt005c-school-repair-followup-20260823.md)。
- `MT-005b6b` description 两字原子的预登记、相对路径 trace 校准、两轮实施细则正向稿、私人生活边界和五提交复核：[`R1`](../../tests/evidence/mt005b6b-description-atom/r1-result.md)、[`R2`](../../tests/evidence/mt005b6b-description-atom/r2-result.md)、[`review`](../../tests/evidence/mt005b6b-description-atom/five-commit-review.md)。204字降为202字的原子已进入 v1.6.15。
- `OC-001` 十二份官方通知、报告、纪要、采购与新闻稿件的结构/论证方法及当前写稿差距基线：[`official-corpus-gap-r2-20260822/result.md`](../../tests/evidence/official-corpus-gap-r2-20260822/result.md)；后续 `WR-018` 五路三文种真实写稿为13/15硬通过、0/15功能性过薄，不新增密度规则：[`wr018-rich-material-baseline-20260822/result.md`](../../tests/evidence/wr018-rich-material-baseline-20260822/result.md)。
- `WR-014-R3` 五提交的最终树复核、原始反例消融、87项回归和负向原型残留检查：[`post-v1613-wr014-five-commit-review-20260822.md`](../../tests/evidence/post-v1613-wr014-five-commit-review-20260822.md)。
- v1.6.13 后四类公开原子的净范围、MT-005c 淘汰、真实写稿、全量门、包体检查和双轮冷审：[`post-v1613-atomic-main-integration-20260823.md`](../../tests/evidence/post-v1613-atomic-main-integration-20260823.md)。
- v1.6.12 后头重脚轻/裸提纲句 R3.1—R3.5 的多轮最小化、硬回退与方向终止：[`sb001-r3-subject-preserving-result.md`](../../tests/evidence/sb001-r3-subject-preserving-result.md)。
- v1.6.11 后内部情况说明、明确正式报告和普通业务函三题正式发文意图 A/B：[`v1612-formal-issuance-intent-result-20260821.md`](../../tests/evidence/v1612-formal-issuance-intent-result-20260821.md)。
- 当前 main、付费分支和实验组合的未完成工程、观察项及可达性盘点：[`post-v1610-registered-engineering-audit-20260820.md`](../../tests/evidence/post-v1610-registered-engineering-audit-20260820.md)。
- v1.6.10 后 main、付费叠加、组合实验与风险台账的 Qwen/Grok/Kimi 三路冷审及共享硬锚窄修复：[`post-v1610-cross-cold-review/result.md`](../../tests/evidence/post-v1610-cross-cold-review/result.md)。
- v1.6.10 后修辞性方面压缩的 Claude Code 在线 D1 与相对期限变化的同稿 D0 生命周期：[`post-v1610-hard-anchor-live-gate-result-20260820.md`](../../tests/evidence/post-v1610-hard-anchor-live-gate-result-20260820.md)。
- 交付洁净度 5 组真实 D0、SOL max、首次 adapter 漏接、D0 安全回退与 Claude Code 在线 D1：[`delivery-cleanliness-real-first/result.md`](../../tests/evidence/delivery-cleanliness-real-first/result.md)。
- Hook 永久移除的二次确认、隔离副本真实删除和删除后普通写稿：[`hook-permanent-removal-real-result-20260814.md`](../../tests/evidence/hook-permanent-removal-real-result-20260814.md)。
- 重复句与高相似句三 provider 真实删除及 SOL max 功能终审：[`repetition-real-first/result.md`](../../tests/evidence/repetition-real-first/result.md)。
- 合并后 Codex 多能力真实兼容验证，含交付洁净度、重复清理、保护性外扩、篇幅不足、普通路径与用户旁路：[`codex-main-multi-capability-real-result-20260814.md`](../../tests/evidence/codex-main-multi-capability-real-result-20260814.md)。
- v1.6.10 后状态、进行态与责任主体的5个真实小样本及独立 SOL 复核：[`post-v1610-state-responsibility-result-20260819.md`](../../tests/evidence/post-v1610-state-responsibility-result-20260819.md)。
- v1.6.10 后按缺口各补一条的当前宿主在线样本，以及中文计数保守回退结果：[`post-v1610-host-capability-gaps-result-20260819.md`](../../tests/evidence/post-v1610-host-capability-gaps-result-20260819.md)。
- 上一正式发行版：[`release-1.6.2.md`](../../tests/evidence/release-1.6.2.md)。
- 当前仓库目录、GitHub OpenClaw 兼容包和 README 收敛结果：[`repository-layout-v161-result-20260812.md`](../../tests/evidence/repository-layout-v161-result-20260812.md)。
- 1.5.x 的发布门禁、提交与 tag、清洁包、平台回执和传播状态保存在 `maintenance/tests/evidence/release-1.5.x.md`。
- 上一正式发行版：[`release-1.6.1.md`](../../tests/evidence/release-1.6.1.md)。
- 发布前本地候选快照：[`release-1.6.1-rc.md`](../../tests/evidence/release-1.6.1-rc.md)。该文件保留当时测试和许可边界，不覆盖最终发布记录。
- 更早正式发行版：[`release-1.6.0.md`](../../tests/evidence/release-1.6.0.md)。
- 不改版本、不发布的许可证范围清理：[`license-scope-cleanup-result-20260812.md`](../../tests/evidence/license-scope-cleanup-result-20260812.md)；当前 README 制度类同题写稿见 [`readme-v161-institution-same-task-comparison-20260812.md`](../../tests/evidence/readme-v161-institution-same-task-comparison-20260812.md)，上一份报告类对照保留在 [`readme-v160-same-task-comparison-20260812.md`](../../tests/evidence/readme-v160-same-task-comparison-20260812.md)。
- 相邻正式版本：[`release-1.5.41.md`](../../tests/evidence/release-1.5.41.md)、[`release-1.5.40.md`](../../tests/evidence/release-1.5.40.md)。
- 1.5.39 自包含 A/B、匿名裁决及 Word 对齐修复：[`v1539-compact-repro-pack-20260808.md`](../../tests/evidence/v1539-compact-repro-pack-20260808.md)。
- 其他预注册、候选、盲审、消融和真实写稿记录继续在 `maintenance/tests/evidence/` 中按版本号、候选代号或日期检索。

## 根 AGENTS.md 的控制面依据

- [OpenAI 官方 AGENTS.md 指南](https://learn.chatgpt.com/docs/agent-configuration/agents-md)：Codex 每次 run 构建指令链，按全局到项目根、再到当前目录合并；`project_doc_max_bytes` 默认 32 KiB，并建议规则保持简洁。
- [agentsmd/agents.md](https://github.com/agentsmd/agents.md)：把 `AGENTS.md` 定位为面向 coding agents 的 README，示例集中于开发环境、测试和 PR 约束。
- [agentmd/agent.md](https://github.com/agentmd/agent.md)：建议的工程章节包括项目结构、build/test、代码风格、架构、测试、安全、Git 和配置。
- 本仓库据此把根 `AGENTS.md` 限定为工程控制面；产品写作行为只保存在 canonical Skill 和 references，不在根文件复述。

## 取证规则

1. 判断当前发布状态时，优先核对根 `AGENTS.md` 与对应 `release-<version>.md`，再按需回看历史快照。
2. 候选基线、发布提交、annotated tag object、tag 解引用提交、GitHub Release、平台上传回执、公开 latest 和审核/索引传播是不同事实，不得互相代替。
3. 历史记录含 pending 或公开索引滞后时，不得据此重复提交；应先核对正式回执和当前公开状态。
4. 未发布候选和隔离实验不得改称正式版本，也不得从历史快照直接恢复到产品树。
