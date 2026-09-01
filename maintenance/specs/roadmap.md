# 状态与下一步

状态只表示当前仓库事实：`DONE` 已完成、已合并或已闭环；`IN_PROGRESS` 有正在验证的候选；`HOLD` 只留给仍有明确下一原子的活动候选；`REJECTED` 表示某个已测试候选不准入；`TERMINATED` 表示当前实现方向经多轮最小化仍有硬回退并停止；`WAIT_NEW_COUNTEREXAMPLE` 表示当前基线覆盖已知场景，只有新的真实失败才重开；`TODO` 尚未实现。

## DONE

- `WR-001/002`：v1.6.4 事实与状态规则、保护性外扩精确删除和新闻边界已发布于 `v1.6.4@a737791c`；六份真实写稿和 SOL 校准见 [`v164-real-writing-final/result.md`](../tests/evidence/v164-real-writing-final/result.md)，发行回执见 [`release-1.6.4.md`](../tests/evidence/release-1.6.4.md)。
- `HK-001/003/004/006`：普通路径独立闭环、capability-first 单协调器及既有宿主 adapter 保持不变；三套国产 CLI adapter 已随 v1.6.15 发布，OpenCode 1.18.23 项目级交互 adapter 已随 v1.6.18 发布。Hermes Agent 0.20.5—0.20.6 新建且不可恢复单题 adapter 已随 v1.6.19 进入 GitHub 与 SkillHub.cn；交互、恢复、one-shot/gateway 继续旁路。Qwen 完成多 Stop/hash/脱敏；Kimi 只完成首次 Stop，宿主单 Stop 上限明确保留。[OpenCode/Hermes R1](../tests/evidence/hk004-opencode-hermes-r1/result.md) · [Hermes R2](../tests/evidence/hk004-hermes-r2/result.md)
- `HK-004-CLI-REVALIDATION-R1`：已逐一运行本机十个真实CLI入口和当前Skill；CodeBuddy 2.141.0只补齐原生provider真实profile一次Stop、精确终稿、独立hash核对和脱敏，隔离data root、reference读取、S1与OpenCodex provider注入未证明；Claude/Codex/ZCode/Hermes/DSH当前声明范围继续成立。Qwen 0.22.3、Kimi 0.39.1、OpenCode 1.18.25分别以`HOOK_INCOMPATIBLE`、`HOOK_UNSAFE`、`LIFECYCLE_INCOMPATIBLE`精确收口，OpenClaw只记无Hook内容；新闻、说明、纪要、长报告又各有两家低成本provider有效真稿，不继承旧版本成功，不留`HOLD`，产品0差异。[结果](../tests/evidence/host-cli-revalidation-r1/result.md)
- `HK-004-DEEPSEEK-HARNESS-R1`：DSH 0.1.1-rc.2 headless 原生 Profile Bundle 已完成全新 profile 安装、OpenCodex 精确模型配置、两份当前 Skill 真稿、多 Stop/hash/脱敏和同名 Skill 反控；只在线覆盖 `delivery_review`，已随 `v1.6.19` 进入 GitHub 与 SkillHub.cn。Qoder 依用户收窄范围 `DEFERRED_BY_USER`。[结果](../tests/evidence/hk004-deepseek-harness-r1/result.md)
- `HK-004-QWENWORK-R1`：QwenWork 无 Hook 静态 Skill 包已按官方个人目录和组织 ZIP 结构完成并随 v1.6.21 发布；34文件镜像、两次同 hash ZIP、包路径低成本真稿和直接反控通过。官方 Stop 未公开完整终稿/回合绑定字段，因此状态为 `STATIC_SKILL_PACKAGE_PASSED / ONLINE_LIFECYCLE_UNVERIFIED / DONE_V1.6.21`，不制作伪 Hook adapter。[结果](../tests/evidence/hk004-qwenwork-r1/result.md)
- `UL-001—004`：篇幅不足 Hook 已按真实写稿优先完成语义修复，并随 `v1.6.5@81061bd7` 发布。Alibaba 直修 268→342，Codex 在线 268→350，Claude Code 在线 268→344；两次独立 SOL max 均判可用 D1 `ACCEPT`。当前候选又把材料明确同数“几方面→几项”送入语义核验：106→206字安全 D1 获选，WorkBuddy / CodeBuddy 的106→190字风险候选仍安全回 D0。结果见 [`v164-under-length-real-first-result-20260814.md`](../tests/evidence/v164-under-length-real-first-result-20260814.md) 与 [`post-v1610-cjk-transparent-quantity-result-20260819.md`](../tests/evidence/post-v1610-cjk-transparent-quantity-result-20260819.md)。
- `CL-001`：交付洁净度已先用三条指定 DeepSeek V4 Flash 路线完成 5/5 同稿真实整理，再接入独立静态 capability，并随 v1.6.5 发布。SOL max 五组全 PASS；Claude Code、Codex 与当前 WorkBuddy / CodeBuddy 在线生命周期均选择 D1 并闭合哈希。结果见 [`delivery-cleanliness-real-first/result.md`](../tests/evidence/delivery-cleanliness-real-first/result.md)。
- `RP-001`：重复句与高相似句已先完成三 provider 的 5 组真实删除和 SOL max 功能终审，再接入纯删除 capability，并随 v1.6.5 发布。当前 Claude Code 已补一条三事件在线 E1/hash 样本；长稿 1 个自然度 WARN 保留为后续观察，不影响已验证的目标功能。
- `WR-003`：20份真实稿与候选直连复测已验证跨文种责任承载；最小规则和镜像已随 `v1.6.6@b49da7f2` 发布。v1.6.10 后又以5个真实小样本细分未决状态、进行态和责任主体边界。当前官方语料扩样确认显式主体、近邻继承与工作事项作主语都成立；额外措辞原型真实稿未稳定改善，已撤回产品改动，只保留[校准证据](../tests/evidence/post-v1610-wr003-official-corpus-calibration-20260819.md)。
- `WR-004`：20类事务文体已完成真实写稿，原型19/20功能成立；“编者按”标识修复后目标功能20/20，中央直接叶已随 `v1.6.6@b49da7f2` 发布。
- `WR-005` 短稿自然度：上限题 R3 为候选3胜、基线0胜、难分1，候选四稿硬边界全 PASS；最小路由接入后又以 Ollama 报告和 Alibaba 新闻完成两篇在线直写，均读取新叶且可直接使用，已随 `v1.6.7@44347003` 发布。明确篇幅下限继续由 under-length 处理。
- `OV-001` 超长收束：真实 D0 498→285、SOL max 六项 PASS、Grok 4.6 冷审修复和最终机械门重放已完成，随 `v1.6.8@6b1dc2c5` 发布；当前 Codex 又完成313→137在线 D1/hash 样本。2026-08-20 的 WorkBuddy / CodeBuddy 2.115.0 补样已闭合 Skill、事务、Stop 和 D0 hash，但两次重复观察均因 `invalid_preserved_segment` 安全回退，不能记为 CodeBuddy 压缩 D1。ClawHub 同步的是无 Hook 写作规则。
- `WR-006` 自然审稿：OpenCode Go 真实审稿和自然审稿、复合成稿、材料引语三类路由反控已完成，随 `v1.6.9@5047c224` 发布。
- `OV-001` 发布后边界补丁：软性“约、左右、上下”、长引语、无标点编号正文、否定责任短语和同动词多拟办对象修复已随 `v1.6.9@5047c224` 发布。
- `WR-007` 语义减载与自然表达：R1—R4及组合真实写稿通过，SOL、Grok、Qwen 未发现候选独有硬失败，随 `v1.6.10@af12b771` 发布。
- `WR-008` 标题与正文边界：真实生成、同稿修复和自然路由通过，随 `v1.6.10@af12b771` 发布。
- `WR-009` 文后提示与正文分区：真实同题稿验证正文外独立分区，随 `v1.6.10@af12b771` 发布。
- `AH-001` 共享硬锚：引用、数字、字段及归属关系保护已接入篇幅不足和超长收束，真实修订与三方冷审通过，随 `v1.6.10@af12b771` 发布。
- `AH-002` 新闻完整日期来源绑定修复已随 `v1.6.20` 进入 GitHub 与 SkillHub.cn：重复日期提示方向继续 `TERMINATED`；不同机制已用三 provider 九次真实 Claude Code 生命周期通过预登记门，Alibaba Token Plan 2 与 OpenCode Go 各至少一题精确补年且控制题逐字不变。只覆盖唯一完整日期与唯一目标新闻文种，多日期、非新闻、歧义材料及其他 capability 旁路；ClawHub 无 Hook。[结果](../tests/evidence/ah002-news-date-completeness-r1/live-result.md)
- `v1.6.22` 小版本已发布：产品tag指向`4b135c50`；GitHub Release已公开，SkillHub.cn的82文件`versionId=277452`已审核通过、公开latest和签名均已切换到1.6.22；ClawHub的`versionId=k972jtvctk9hshdd0kqf149sks8dh3xf`已传播为公开latest，精确33文件、零Hook路径和clean状态闭环。发布前本次复跑100项聚焦、747项全量、111/111确定性消融和20/20 stub smoke均通过。[发布记录](../tests/evidence/release-1.6.22.md) [候选记录](../tests/evidence/release-1.6.22-rc.md)
- `v1.6.23` 小版本已发布：产品tag指向`6a6ededa`，GitHub Release、SkillHub公开latest以及ClawHub公开latest、精确34文件和clean状态均已闭环；SkillHub.cn一次提交返回83文件`versionId=279383`，ClawHub一次提交返回34文件无Hook包`versionId=k97da1z02hxs6cd58a9txyahb98dkv4w`，SkillHub外部安全报告仍为queued，期间未重复提交。发布前756项全量、111/111双侧确定性消融、20/20 stub smoke、五套 quick validate 和最终108项定向门通过；`WR-025 / WR-008b`不在本版tag或包体中。[发布记录](../tests/evidence/release-1.6.23.md) [候选记录](../tests/evidence/release-1.6.23-rc.md)
- `UL-006-CONTRACT-R1 / HK-009-STOP-BUDGET-R1` 已随v1.6.23发布：事故隐式入口的 README、manifest 与运行时统一为仅 `incident_bulletin`，不可达的情况说明/办理通知旧代码已删除；单次 Stop 的 review-gate 子进程共享25秒预算，可信 D0 恢复不污染 stdout，D1 证据损坏不降级，预算耗尽的有限失败立即精确脱敏。目标反例、host adapter stdin/stdout、九宿主契约、独立冷审和756项全量通过；状态为 `DONE_V1.6.23`，无 `HOLD`。[结果](../tests/evidence/post-v1622-hook-contract-r1/result.md) [合入记录](../tests/evidence/post-v1622-hook-contract-r1/main-merge.md)
- `MT-004b-REVIEW-DIRECT-LEAF-R1/R2` 已完成35次当前基线路由和两轮共40次五路真实审稿：请示、报告、通知的点名只审任务不再伴读16.5 KB综合页，可研点审、格式/语气/AI味综合审稿分别保持独立路线；所有稿件保留核心事实、状态和只审不改形状。轻页、五套镜像、确定性反控和756项全量通过后已随v1.6.23发布，状态为 `DONE_V1.6.23`。去AI味单面拆分因15次基线仅1次实际读取而 `TERMINATED`，旧四层审稿拆分不重开。[结果](../tests/evidence/reference-slimming-r3-current/result.md)
- `RESEARCH-PLAYBOOK-LEAF-R1` 已按 `MT-004` 两家复现门运行 Alibaba2/OpenCode 共8次真实写稿。4份调研/研究长稿均为1715—1973字符且完整，但组合 `genre-playbooks.md` 只在1/4目标题读取，未形成跨 provider 共同伴读；状态为 `REJECTED_BASELINE_ROUTE_NOT_REPRODUCED / WAIT_NEW_COUNTEREXAMPLE`，不建立专叶、不扩大三家、不改产品。[结果](../tests/evidence/research-playbook-leaf-r1/result.md)
- `v1.6.21` 小版本已发布：产品 tag 指向 `8086ff25`；GitHub Release与ClawHub公开面已闭环。GitHub公开更新说明已去除内部排除项；SkillHub.cn旧待审提交已撤回并以相同82文件包、相同fingerprint和用户可读说明重新提交为`versionId=276243`，审核与公开传播仍pending。ClawHub保持33文件无Hook包且未重发；`UL-006`、Red SkillHub和付费能力不在v1.6.21产品祖先中。
- `v1.6.20` 小版本已发布：产品 tag 指向 `2fc9d1d4`；GitHub Release、SkillHub.cn 公开搜索与精确签名、ClawHub latest、精确33文件、逐文件哈希和总体clean均已闭环。AH-002 进入 GitHub/SkillHub，ClawHub 继续无 Hook；公开写作规则、description 和 references 相对 v1.6.19 不变。
- `v1.6.19` 小版本已发布：产品 tag 指向 `eef65336`；GitHub Release、SkillHub.cn 公开搜索与精确签名、ClawHub latest、精确33文件和总体clean均已闭环。Hermes 与 DSH adapter 进入 GitHub/SkillHub，ClawHub 继续无 Hook；公开写作规则、description 和 references 相对 v1.6.18 不变。
- `v1.6.18` 小版本已发布：产品 tag 指向 `67a68257`，GitHub、SkillHub.cn 与 ClawHub 公开 latest 均已闭环；OpenCode 常驻交互 adapter 进入 GitHub 与 SkillHub.cn，ClawHub 精确33文件无 Hook 包只同步版本坐标且与本地逐项一致。公开写作规则、description 和 references 相对 v1.6.17 不变。
- `v1.6.17` 维护补丁已发布：产品 tag 指向 `7b457784`，GitHub、SkillHub.cn 与 ClawHub 公开 latest 均已闭环；ClawHub 精确33文件无 Hook 包与本地逐项一致，扫描为clean，期间未重复提交。公开写作规则和 Hook 协议相对 v1.6.16 不变。
- `v1.6.16` 已发布至 GitHub、SkillHub.cn 与 ClawHub；产品 tag 指向 `f6293aaa`，ClawHub 为33文件无 Hook 包。`OC-003` 已进入本版；SkillHub 与 ClawHub 的首次公开索引回读短暂显示1.6.15，后续 latest 均已传播为1.6.16，ClawHub 精确版本文件和安全状态已闭环，期间未重复上传。
- `v1.6.15` 已发布至 GitHub、SkillHub.cn 与 ClawHub；产品 tag 指向 `762b84d4`，ClawHub 为33文件无 Hook 包。国产 CLI Hook adapter、`MT-005b6b`、`HK-008b`、`WR-014-R4`、`WR-019c/019d` 及更早已通过原子均已进入发布历史。
- `OV-001` 语义判定校准与 sentence-target、`HK-008` 终态脱敏、`WR-014-R3` 能力/计划状态锚已随 v1.6.14 发布；Hook 默认关闭和按单能力窄启用不变。
- `WR-013` 一般原因、即时作用与发布者角色边界已完成五路真实写稿、入口冲突消融和非新闻控制，并随 v1.6.13 发布。
- `WR-011` 新闻声明级核验已把机构性质、来源身份/原始出处和限定来源结论拆成三个原子；R3 三轮25稿后五路最终候选5/5守住目标边界，最小新闻叶及四套镜像已随 v1.6.13 发布。
- `UL-005` 当前来源台账原子已闭环：WorkBuddy / CodeBuddy 2.115.0 对同一61字 D0 分别拒绝含强保障、材料外用途和多余请批语的111字 D1，并接受只含同一事实 span 低强度推断的114字 D1；两次终稿 hash 闭合。当前实现与 R9 证据已进入本地 `main`，不外推为所有文种、所有模型的自然扩写保证。[结果](../tests/evidence/ul005-fact-ledger-r9-codebuddy-20260822.md)
- `UL-005-R10` 扩写指令与 verifier 合理推断口径已完成四轮收敛并随v1.6.21发布：最终五路15份候选中扫描仪申请5/5进入下限，活动新闻4/5进入、1份安全D0，稀疏采购5/5逐字D0，包装0/15且无候选独有事实、状态或程序硬回退。状态为 `DONE_V1.6.21`；ClawHub继续无Hook。[结果](../tests/evidence/short-inference-r1/underlength-r4-result.md)
- 联网来源用途分型与命中页绑定已完成：国家规范、本地执行、外省比较不混用，命中页元数据和 URL 绑定实际打开页；R2f—R2h 五路15稿中12稿只做一次定向补搜，最终 R2h 五路5/5写入真实上海命中 URL。严格工具调用次数不能由提示词确定性保证。[结果](../tests/evidence/online-source-use-r2h-result-20260822.md)
- SkillHub 已加入 `office-efficiency`、`content-creation` 轻量检索信号；不声称平台写入双分类。
- GitHub 当前包统一 MIT；普通兼容包不含 Hook，OpenClaw GitHub 兼容包随仓库维护。
- v1.6.6 GitHub 与 SkillHub.cn 发布回执见 [`release-1.6.6.md`](../tests/evidence/release-1.6.6.md)；ClawHub、Red SkillHub 及其他平台未在该轮上传。SkillHub 公开 latest 与签名已传播，Keen、Sanbu 安全报告均为 benign。
- v1.6.7 GitHub、SkillHub.cn 与后续 ClawHub 无 Hook 包同步回执见 [`release-1.6.7.md`](../tests/evidence/release-1.6.7.md)。该版旧传播状态已由 v1.6.10 的 latest、签名和下载包闭环取代。
- `OC-001/WR-018` 已用十二份官方稿件和五路三文种真实写稿校准结构、论证密度和合理推断；15稿中13稿硬通过、0稿功能性过薄，当前产品不增加统一字数门、固定模板或扩写流程。
- `OC-003` 算力可研状态与程序边界已完成，点名完整性审稿也已收口：R2 完成状态分层；R3 最终五个便宜 provider 5/5只读入口与可研叶，仍完整核算数据、解释缺项影响并覆盖成本、技术指标、验收主体与依据。R3 已随 v1.6.16 发布，状态为 `DONE_V1.6.16`，不新增 Hook、程序模板或数值阈值门。[R2](../tests/evidence/oc003-r2-state-layering/result.md) [R3](../tests/evidence/oc003-completeness-boundary-r3/result.md)
- `OC-003` 发布后状态谓语泛化原子完成36次有效复核/改稿：直接前提缺口可支持同对象低强度条件判断，但产品例示跨模型不稳定；最终纯范围候选又在 MiniMax 同题 baseline 通过时独有地把“未安排/未指定”外扩为“尚待研究确定”。条件例示记 `REJECTED`、泛化方向记 `TERMINATED`，产品已恢复 v1.6.16 原文，不留 `HOLD`。[结果](../tests/evidence/oc003-state-predicate-general-r1/result.md)
- `WR-014-R5` 已用总体已决/局部未定、整体未决明示、采购进行中三题核对“尚未形成采购决定”的状态层级；四个范围有效样本的目标层级4/4通过，其中两稿另有输出形状或材料外事实硬失败。当前产品对本目标足够，不增加禁词、reference或Hook；官方语料只用于校准具体阶段和对象的承载方式。[结果](../tests/evidence/wr014-r5-procurement-state-scope/result.md)
- `WR-020b2a/b2b/b2c` 已证明当前产品可以对已有讲话稿做点名搬移、点名删除和只审定位；b2b 的 Ollama 样本删除正确但正文包装失败，作为交付风险保留，不据此增加任务卡、段长门或 Hook。
- `WR-023` 申请原因、依据与材料缺口已完成五路65份真实写稿并选择 R2：申请原因在材料事实与常识可闭合时自然前置；缺事由事假不以泛称代填，年休假可用一般制度依据；稀疏打印机采购全新题5/5形成直接用途且未补具体故障、损失或程序。R3 因提示过度导致材料遗漏和状态升级，终态为 `TERMINATED_PROMPT_OVERHANDLING`；R2 为 `DONE_V1.6.22`，不新增 Hook、description 或统一长度门。[结果](../tests/evidence/wr021-application-reason-r1/result.md)
- `WR-024` 请示缘由、依据与材料缺口已完成五路四臂80份真实写稿并选择拆分后的 R3：请示按缘由—事项—要求组织，紧凑短稿可同句承载；事实、依据和常识可直接支持时允许一层自然理由或用途，缺原因时不编造具体事由。R1 宽泛合并句与 R2 负面枚举分别记 `REJECTED`，R3 为 `SELECTED_ENGINEERING_VERIFIED / DONE_V1.6.22`；单缺口提示形态和材料外“其他安排不变”另项处理，不新增 Hook、description 或统一长度门。[结果](../tests/evidence/wr024-request-reason-r1/r3-result.md)
- `WR-014-R6/R6b`、`WR-013c`、`WR-020a2` 已完成当前基线真实写稿：[结果](../tests/evidence/post-v1616-writing-stability-r1/result.md)。R6原“继续”目标2/2未复现；R6b只有Ollama 1/2把证据未附外推为待后续核验；短采购原因/低强度影响2/2通过；长报告OpenCode目标通过，Ollama两次技术失效。没有跨模型共同目标失败，产品0差异，不留HOLD。
- v1.6.15 短稿诊断已完成五路30臂：未复现跨文种系统性偏短；活动新闻完整年份和个别 provider 的材料外扩写已拆成独立风险，不用“正文必须长于提示词”统一处理。
- 本地付费候选 `codex/paid-outline-review` 收敛 `OT-001`、`OT-001-composite`、`OT-002` 与 `RF-001`；活动台账以“当前 main 是付费分支祖先”作为同步事实，不固化会在下一次同步后失效的 tip。三宿主47文件组装、698项全量和公开零文件检查通过。该状态为 `DONE_LOCAL_PAID_NO_RELEASE`，不反向进入公开版、不发布。
- `UL-006` 已完成拆分并随v1.6.22发布：阶段性事故通报保留动态近转写入口；情况说明和办理通知的隐式入口终止；透明算术因没有安全D1交付而撤回；“已形成但未附”reference因跨provider正文包装终止；短通知只接入不从邮箱/接收方反推落款主体或日期的关系边界。旧五家20稿与新五家15稿通过，状态为`DONE_V1.6.22`，无活动`HOLD`。[事故结果](../tests/evidence/ul006-incident-only-r1/result.md) [联合留出](../tests/evidence/post-v1621-validated-atoms-r1/result.md)

## IN_PROGRESS

- `WR-009c`：稀疏事务申请的未决字段后续写边界。只验证“待明确后另行报批/按程序组织实施”等材料外程序承诺，不同时修改原因推断；有现状、问题或已做尝试时仍允许一层合理原因和即时作用。[来源](../tests/evidence/short-inference-r1/cause-hint-result.md)
- `CL-001-NOHK-R2`：普通无 Hook 写稿仍跨 provider 出现“已读取技能”、正文引导语、横线、自检和 commit/测试说明。只前移或合并现有“只交正文”规则，用短事务稿、新闻、情况说明与长稿做真实 A/B，不增加 description。[来源](../tests/evidence/short-inference-r1/cause-hint-result.md)

## REJECTED

- `FINAL-BODY-LEAF-R1`：稀疏采购、活动新闻、普通长报告对完整总审页的实际读取依次为1/5、0/5、1/5，没有稳定可归因减载入口，不做产品原型。[基线结果](../tests/evidence/reference-slimming-r2/baseline-result.md)
- `WORKFLOW-REVISION-LEAF-R1`：普通长报告0/5读取 `workflow.md`，多材料改稿也只有1/4有效读取；物理拆分不能解决当前路由，不做产品原型。[基线结果](../tests/evidence/reference-slimming-r2/baseline-result.md)

- `MINUTES-CHECKLIST-LEAF-R1`：15个技术有效纪要目标配对中Baseline读取通用检查页为0，搬移小节没有可归因减载，产品已恢复。[汇总](../tests/evidence/reference-slimming-r1/result.md)
- `NOTICE-LEAF-CURRENT-R1`：目标路由仅2/15，且真实通知与采购公告控制出现对象、日期、合同关系和过程包装回退，候选已拒绝并恢复产品。[汇总](../tests/evidence/reference-slimming-r1/result.md)
- `PROCUREMENT-ANNOUNCEMENT-LEAF-R1/R2`：公告写稿质量安全；最小R2消除控制串叶后仍只有2/5 provider形成可归因减载对，低于预登记门，终止继续堆入口提示。[汇总](../tests/evidence/reference-slimming-r1/result.md)
- `REVIEW-LAYER-SPLIT-R1`：局部目标路由0/10、全文能力路由0/5，两家Candidate另有Skill过程旁白；四层物理拆分候选已拒绝并恢复产品。[汇总](../tests/evidence/reference-slimming-r1/result.md)
- `WR-012` 正式发文意图候选：内部情况说明方向成立，但正式报告和普通业务函分别出现正文外自证、材料外时间/过程事实；候选拒绝，当前基线保留。[结果](../tests/evidence/v1612-formal-issuance-intent-result-20260821.md)
- `MT-005b2/b3/b4` description 合并候选：18次扩大真实 A/B 分别复现范围扩大、未给日期、材料外责任/效果或未交稿；候选拒绝，保留当前枚举。[结果](../tests/evidence/post-v1611-expanded-real-writing-20260820.md)
- `MT-005c` 受众合并候选：193字版本缺“学校”，196字最小回补又出现正向稿状态/安排硬失败；候选拒绝，恢复已发布基线。[结果](../tests/evidence/mt005c-school-repair-followup-20260823.md)
- `WR-020b1` 讲话首次起草任务卡：连续三次收窄仍新增职责、流程、任务或保护性自证；候选拒绝，不再沿首次起草任务卡重试。[结果](../tests/evidence/wr020b1-speech-task-card/result.md)

## TERMINATED

- `SHORT-NATURAL-REFERENCE-R1` 普通 reference 原子已终止并恢复产品：五家低成本 provider 完成50次自然基线和R1/R2/R3共150次候选，三轮均未在至少两家稳定改善真实偏短组；R1/R2还出现候选独有的状态遗漏、程序/承诺或新事件内容。显式80字控制保持，合理推断不算失败。后续不再堆reference措辞。[终态](../tests/evidence/short-natural-reference-r1/reference-result.md)
- `AI-COMPUTE-BASIC-LEAF-R1/R2`：R2用五条低成本路线完成15/15技术有效真实任务，完整可研已不串读窄叶，但Ollama相对冻结Baseline仍遗漏2台服务器、每台4张GPU、5.8千瓦和71%四项已给事实；两道简单申请未同时达到稳定省读与无候选硬回退。产品恢复固定Baseline，不做R3。[R2终态](../tests/evidence/reference-slimming-r2/r2-result.md)
- `WR-005` 原短稿自然度 R1/R2 已被上限题 R3 取代；常用语机械化 R1—R6 依次尝试删词、删表、取消加载和按材料选择，仍轮流出现篇幅、职责、文种或材料外号召回退。两个旧方向均终止，不再以 HOLD 呈现。[结果](../tests/evidence/v167-formulaic-mechanicality-real-first/result.md)
- 旧 `length-band-hook-v162`、`under-length-hook-v162-v2`、`v163-protective-expansion-gate` 已被后续正式能力或新原子取代，旧实现方向终止，不复活旧准入结论。
- `SB-001` 章节均衡提示词/路由：R3.1—R3.5 已依次尝试语义叶、路由减载、底稿形态触发、过程隔离和近场卡。虽有多路精确搬移，但最终仍出现 Alibaba 章节/整稿重复、未决状态改写和无关残片，OpenCode 另有一次只承诺交付而未交稿；产品改动不合入，不再向第三处堆规则。[结果](../tests/evidence/sb001-r3-subject-preserving-result.md)
- 联网严格“一次补搜”的纯提示词方向：R2f—R2h 已两次按失败增加最小停止语义，15稿中12稿精确一次；超额调用在 Luna、Ollama 间转移，说明不能靠继续叠字形成确定性门。产品保留有限补搜写作规则；除非出现值得付出工程复杂度的新宿主级机制，不再追加提示词。[结果](../tests/evidence/online-source-use-r2h-result-20260822.md)
- `WR-001-DATE` 新闻完整日期重复提示：R1独立 bullet 和R2合并短句均提升年份命中，但 Ollama 两轮仍补材料外活动过程，未形成稳定净收益；产品未采用该候选并保持已发布基线。完整年份遗漏保留为真实风险，只有出现不同机制和新反例才重开。[R1](../tests/evidence/wr001-date-r1/r1-result.md) [R2](../tests/evidence/wr001-date-r1/r2-result.md)

## WAIT_NEW_COUNTEREXAMPLE

- `WR-009b` 当前通用实质缺口规则已让明确允许提示题5/5、自然 holdout 技术有效4/4给出原因补充建议；两轮显式候选在只交正文和明确拒绝题之间摆动，已恢复产品。若出现当前基线未提示的新自然反例再开，不重试原组合。[结果](../tests/evidence/short-inference-r1/cause-hint-result.md)
- `WR-013d/WR-018-R2` 当前五路新采购、维修与活动新闻共15份真实稿中14份技术有效；申请稿5/5均形成一层合理原因和作用，活动新闻3/4形成有限影响，未复现跨provider功能性过薄。完整年份、包装和个别材料外流程另作既有风险，不据此改普通写稿规则。[结果](../tests/evidence/short-inference-r1/baseline-result.md)
- `SHORT-CURRENT-CLI-R1` 当前同一无上限采购题十个CLI的实际正文均完成文种功能且不薄；240—300字符题在Claude/Codex/ZCode/DeepSeek Harness四种当前companion无争议通过，CodeBuddy 2.141.0为长度/真实profile生命周期通过但有reference拒绝与软性时间措辞风险，Qwen无Hook消融另得245字符干净正文。活动新闻、未决说明和噪声纪要各两家低成本provider也未出现功能性过薄。状态为`NO_COMMON_SHORT_REGRESSION / WAIT_NEW_COUNTEREXAMPLE`；只在新的跨provider功能性过薄反例出现时重开，不把Hook输出聚合、事实外扩或技术失效记成短稿失败。[结果](../tests/evidence/host-cli-revalidation-r1/result.md)
- `MT-004a-PROCUREMENT-REQUEST-ROUTE-R1`：首份 Alibaba2 简单采购申请读取4份额外通用页，但预注册的 Alibaba1 全新复现只读信息选择、轻量卡和申请叶，正文132→219字且事实、状态、合理原因和请批功能通过。跨 provider 稳定过载未成立，不修改 reference；只有另一家低成本 provider 新 trace 再次出现同类过读或真实质量回退才重开。[结果](../tests/evidence/mt004a-procurement-request-route-r1/result.md)
- `WR-012` 当前基线已覆盖内部情况说明、明确正式报告和普通业务函的主要意图边界；只有当前基线出现新的真实误路由才开新机制，不重抽已拒绝候选。
- `MT-005` 当前202字 description 已覆盖已知正向和相邻边界；只有新的真实漏触发或误触发才开单原子，不重跑 b2/b3/b4/c 旧组合。
- `WR-013c` 当前短采购基线两路均能由资源利用率、排队和等待形成合理原因与低强度预期；只有新的真实稿出现共同过薄或共同既成影响外扩才重开。
- `WR-014-R6b` 当前OpenCode可以区分已完成、附件未附与真实效果待观察，Ollama单家仍有核验外推；等待不同材料中的跨模型共同反例，不把单家风险扩成全局禁词。
- `WR-020` 当前长稿基线有写作价值，a2一份有效长稿通过范围目标、另一provider技术失效，b2已覆盖已有稿搬移、删除和只审定位；只有新的有效长稿出现结构、任务归属、结论范围或材料外职责共同反例才重开。
- `WR-010` 当前会议正文已覆盖弱意向、明确承诺、权威修正和未回应指派；没有新的正文反例前不增加 sidecar、负责人/期限补全或渲染工程。
- `WR-001` 重复日期提示方向已经终止，不以统一长度门或更多枚举修复；完整年份风险已由不同机制 `AH-002` 完成并随 v1.6.20 进入 GitHub 与 SkillHub.cn，不再把它记为单纯等待新反例。

## TODO：已登记但不在本轮展开

1. 文件提取失败与降级交付仅作低优先级观察；出现真实扫描 PDF/不支持格式失败后，再验证停止、请求转换和 Markdown 降级，不先并入默认写稿流程。

## 不再重复

- 不把生命周期触发成功称为写稿质量成功。
- 不为没有合格 D1 的候选运行空 SOL 盲审。
- 不用独立采样的 Hook on/off 总胜负替代同一 D0/D1 的功能增量。
- 不在每个小修复后跑全量测试；全量门只在合并或发布前运行一次。
- 不因独立 npx CodeBuddy 的认证失败反复复制登录态；需要真实 CodeBuddy 样本时先核对 WorkBuddy 内置 CLI 的当前登录和版本，并如实区分两个入口。
