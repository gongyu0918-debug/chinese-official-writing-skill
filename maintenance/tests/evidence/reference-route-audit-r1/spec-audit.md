# 2026-09-05 规格与开发纪律审计

## 范围与方法

固定公开基线 `5fbb2d26c49d0b780ad11fc4cff008854995ad3f`，本轮产品原型 `22772262b34f43e5cd975fb8b0aaa2f945aa5adb`。审查根 AGENTS、specs 的 README/requirements/coverage/roadmap/public-paid-sync，以及待办台账；不修改产品、测试驱动或冻结 fixture 来源。

本次逐项核对的是登记关系、状态边界和本地证据指向，未重跑历史模型输出，未重新认证全部历史稿件，也未联网刷新平台审核/传播。基线共有 51 个正式需求节、59 条覆盖记录、103 条 roadmap 列表记录和269条待办勾选记录。51项需求均能对应覆盖矩阵（缺项数 0）；编号沿革单独保留，不给孤儿 WR-016 补造需求或完成状态。

审计前7份活动 Markdown 的275个本地链接全部存在。覆盖矩阵36行含直接 Markdown 证据链接、23行仅给版本/样本名或说明；后者属于追溯便利性缺口，不能据此判定证据不存在，也不能借此把历史 DONE 清零。下表逐行保留状态与入口核对结果，行号指冻结基线的 coverage，复核具体记录见[覆盖矩阵](../../../specs/coverage.md)。

## 确认的登记修正与未确认项

1. **WR-028 当前状态滞后。** `git rev-parse main` 为 `5fbb2d26`，该提交含整改专叶、普通镜像和工程接入；`git merge-base --is-ancestor 5fbb2d26 main` 返回0。本地 `origin/main` 为 `5869234b`，根代理另已核验原任务交付中的未推送/未发布边界。当前 requirements/coverage/roadmap/待办改记 `LOCAL_MAIN_INTEGRATED / NOT_RELEASED`；[旧工程记录](../remediation-plan-r1/engineering-result.md)的 `NOT_MERGED` 是当时时点，不回写。
2. **每次 reference 减载的门发生当前授权更新。** 旧 MT-006 允许纯维护声明删除只做结构验证；本轮用户明确每次减载均真实写稿 A/B，路线与样本随目标风险预登记，已写入规格；五路仅为当前 R1 的设计，不固化进 AGENTS。旧[减载结果](../semantic-reference-diet-r1/result.md)保留当时验证方式，既不追溯宣布缺测，也不据旧豁免跳过本轮 A/B。
3. **多种状态并存不等于矛盾。** WR-005/014/023/024/025/026、MT-004/005 的已发布原子和后续拒绝/终止原子分别成立；旧 HOLD 被后续终态取代的文字不当作活动 HOLD。WR-010/012/018/020、WR-009b、采购路由等 WAIT 保留；不为本次新研究复活旧失败路径。
4. **付费边界不代签。** 本地 `codex/paid-outline-review` 为 `08a1e7f4`，当前 main 对它的 ancestry 检查返回 1；保留 `SYNC_REQUIRED / PAID_THREAD_OWNED` 和旧能力范围。本次不读取或修改付费实现，不把其他命名分支的存在当作该分支已完成同步或发布。
5. **宿主/平台状态只按证据时点保留。** Qwen/Kimi/OpenCode 当前兼容性限制、CodeBuddy 的 reference/provider 证据缺口、QwenWork 静态包与在线未验证、DOCX 渲染未声明、平台 pending 审核均不提升为 DONE。已有回执的“当时已发布”不等于今天所有公开面再次验证。
6. **已发布能力可有新反例。** [本轮审核](audit-findings.md)的日期示例错绑与三个终态/回显问题另挂 AH-002b、HK-005b；不否定旧窄范围生命周期证据，也不把旧159项通过冒充新反例已修复。

## 基线59条覆盖记录逐项核对

| 基线行 | 登记项 | 保留的状态边界 | 直接证据链接数 | 本轮处理 |
| ---: | --- | --- | ---: | --- |
| 7 | `WR-001` 事实与状态 | DATE_PROMPT_DIRECTION_TERMINATED；DONE_V1.6.20 | 2 | 直链可达；保留原状态 |
| 8 | `WR-002` 保护性外扩 | 已覆盖 | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 9 | `WR-003` 责任承载 | 已覆盖 | 1 | 直链可达；保留原状态 |
| 10 | `WR-004` 文种用语 | 已覆盖并随 v1.6.6 发布 | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 11 | `WR-005` 短稿自然度、`WR-005b` 语义路由与常用语机械化 | v1.6.7、WR-005b 已发布；后续表项与常用语旧方向 TERMINATED | 2 | 直链可达；保留原状态 |
| 12 | `WR-006` 审稿模式 | 已随 v1.6.9 发布 | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 13 | `WR-007` 语义减载与自然表达 | 已随 v1.6.10 发布 | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 14 | `WR-008` 标题与正文边界 | 已随 v1.6.10 发布 | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 15 | `WR-009` 文后提示与正文分区 | 已随 v1.6.10 发布 | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 16 | `WR-009b` 事务稿原因缺口提示 | CURRENT_BASELINE_SUFFICIENT / WAIT_NEW_COUNTEREXAMPLE | 1 | 直链可达；保留原状态 |
| 17 | `WR-010` 会议结论与承诺证据 | CURRENT_BODY_DONE_NO_NEW_RULE | 1 | 直链可达；保留原状态 |
| 18 | `WR-011` 新闻声明级核验 | DONE | 1 | 直链可达；保留原状态 |
| 19 | `WR-012` 正式发文意图路由 | REJECTED_CANDIDATE / WAIT_NEW_COUNTEREXAMPLE | 1 | 直链可达；保留原状态 |
| 20 | `WR-013` 事实支撑的一般原因与即时作用 | DONE / R13C_BASELINE_TARGET_PASS | 2 | 直链可达；保留原状态 |
| 21 | `WR-014` 证据可见性与事项进度 | R6_TERMINATED_BASELINE_TARGET_NOT_REPRODUCED / R6B_ONE_PROVIDER_RISK / WAIT_NEW_COUNTEREXAMPLE | 4 | 直链可达；保留原状态 |
| 22 | `WR-018` 丰富材料下的事务稿密度 | DONE_CURRENT_PRODUCT_NO_LENGTH_RULE | 2 | 直链可达；保留原状态 |
| 23 | `WR-019` 术语、行业表达与翻译腔 | DONE | 2 | 直链可达；保留原状态 |
| 24 | `WR-020` 长报告与讲话稳定性 | B1_REJECTED / B2_DONE / WAIT_NEW_COUNTEREXAMPLE / CURRENT_LONG_REPORT_2_PROVIDER_PASS | 6 | 直链可达；保留原状态 |
| 25 | `WR-021-SITUATION-CLOSE` 历史情况说明收束原子 | TERMINATED_BASELINE_NOT_REPRODUCED / WAIT_NEW_COUNTEREXAMPLE | 1 | 直链可达；保留原状态 |
| 26 | `WR-023` 申请原因、依据与材料缺口 | R2_SELECTED / DONE_V1.6.22 / R3_TERMINATED_PROMPT_OVERHANDLING | 1 | 直链可达；保留原状态 |
| 27 | `WR-024` 请示缘由、依据与材料缺口 | R1_REJECTED / R2_COMBINED_REJECTED / R3_SELECTED_ENGINEERING_VERIFIED / DONE_V1.6.22 | 1 | 直链可达；保留原状态 |
| 28 | `WR-025/025c` 合作性意见建议与建议反馈 | R3_SELECTED_ENGINEERING_VERIFIED / WR-025c_SELECTED_ENGINEERING_VERIFIED / WR-025d_BASELINE_SUFFICIENT / DONE_V1.6.25 / RELEASED | 3 | 直链可达；保留原状态 |
| 29 | `WR-026` 短意见载体与完整稿件形态 | R1_ADVISORY_REJECTED / R1_SHORT_REJECTED / R2_TERMINATED_PROMPT_ECHO / R3_TERMINATED_PROMPT_ECHO_AND_EXPANSION / R4_REAL_WRITING_PASSED / ENGINEERING_VERIFIED / DONE_V1.6.26 / RELEASED | 3 | 直链可达；保留原状态 |
| 30 | `WR-027` 投诉与情况反映 | R2_REAL_WRITING_PASSED / ENGINEERING_VERIFIED / DONE_V1.6.26 / RELEASED | 1 | 直链可达；保留原状态 |
| 31 | `WR-028` 整改方案专项写作 | LOCAL_MAIN_INTEGRATED / NOT_RELEASED | 4 | 纠正当前登记；旧工程记录不回写 |
| 32 | `WR-008b` 并列小标题与 DOCX 主标题缩进 | TEXT_RULE_SELECTED_ENGINEERING_VERIFIED / DOCX_RENDER_NOT_CLAIMED / DONE_V1.6.25 / RELEASED | 1 | 直链可达；保留原状态 |
| 33 | `OC-003` 算力可研状态、程序边界与点名完整性审稿 | DONE_V1.6.16 / POST_RELEASE_GENERALIZATION_TERMINATED | 3 | 直链可达；保留原状态 |
| 34 | `SB-001` 头重脚轻与裸提纲句搬移 | TERMINATED | 1 | 直链可达；保留原状态 |
| 35 | `HK-001` 无 Hook 闭环 | 已覆盖 | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 36 | `HK-002` 写稿后插入 | 已覆盖的版本和能力保持 | 1 | 直链可达；保留原状态 |
| 37 | `HK-003` 单协调器 | 已覆盖 | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 38 | `HK-004` 宿主薄适配 | OPENCODE_DONE_V1.6.18 / HERMES_R2_DONE_V1.6.19 / DSH_R1_DONE_V1.6.19 / CURRENT_CLI_R1_REVALIDATED；CODEBUDDY_2.141_REAL_PROFILE_LIFECYCLE_PASS_REFERENCE_DENIED_PROVIDER_UNVERIFIED / QWEN_0.22.3_HOOK_INCOMPATIBLE / KIMI_0.39.1_HOOK_UNSAFE / OPENCODE_1.18.25_LIFECYCLE_INCOMPATIBLE | 5 | 直链可达；保留原状态 |
| 39 | `HK-004-QWENWORK-R1` 静态 Skill 包 | STATIC_SKILL_PACKAGE_PASSED / ONLINE_LIFECYCLE_UNVERIFIED / DONE_V1.6.21 | 1 | 直链可达；保留原状态 |
| 40 | `HK-005` 故障回退 | 已覆盖主要路径 | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证；新终态/回显反例另登记 HK-005b |
| 41 | `HK-006` 知情与关闭 | 已覆盖 | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 42 | `HK-008` 终态数据最小留存 | DONE | 2 | 直链可达；保留原状态；新终态/回显反例另登记 HK-005b |
| 43 | `HK-009` Stop 子进程预算与可信失败清理 | ENGINEERING_VERIFIED / DONE_V1.6.23 / RELEASED | 2 | 直链可达；保留原状态 |
| 44 | `UL-001` under-only 触发 | 已覆盖并随 v1.6.5 发布 | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 45 | `UL-002` 安全扩写 | 已覆盖当前事实充分采购请示 | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 46 | `UL-003` 产品准入 | 已覆盖目标功能 | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 47 | `UL-004` 证据迁移 | 已覆盖“同数方面→项”只进入语义核验的窄放宽 | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 48 | `UL-005` 语义验收来源绑定 | DONE_R9_RELEASED / R10_DONE_V1.6.21 | 2 | 直链可达；保留原状态 |
| 49 | `UL-006` 无明确下限的文种化过短兜底 | DONE_V1.6.22；TERMINATED | 3 | 直链可达；保留原状态 |
| 50 | `CL-001` 交付洁净度 | 已覆盖并随 v1.6.5 发布 | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 51 | `RP-001` 重复与高相似句 | 已覆盖并随 v1.6.5 发布 | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 52 | `AH-001` 引用与硬锚 | 基础已发布、窄修复通过；其他能力尚未迁移 | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 53 | `AH-002` 新闻完整日期来源绑定修复 | DONE_V1.6.20 | 1 | 直链可达；保留原状态；新示例错绑另登记 AH-002b |
| 54 | `OV-001` 超长收束 | DONE | 5 | 直链可达；保留原状态 |
| 55 | `OT-001` 提纲冻结与核对 | CAPABILITY_DONE_LOCAL / SYNC_REQUIRED / PAID_THREAD_OWNED / NO_RELEASE | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 56 | `OT-001-composite` 骨架保持的有序改稿 | DONE_CODEBUDDY_ONE_SAMPLE / SYNC_REQUIRED / PAID_THREAD_OWNED | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 57 | 联网公开来源核验 | DONE | 1 | 直链可达；保留原状态 |
| 58 | `OT-002` 提纲修正 | CLOSED_BY_EXISTING_PLANNER / SYNC_REQUIRED / PAID_THREAD_OWNED | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 59 | `RF-001` 红头 DOCX | PAID_PRODUCT_PASS_FONT_FALLBACK / SYNC_REQUIRED / PAID_THREAD_OWNED | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 60 | `MT-001` 真实结果优先 | 已覆盖规则 | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 61 | `MT-002` 可达性 | 当前轮已覆盖并固化回归 | 1 | 直链可达；保留原状态 |
| 62 | `MT-003` 公开面克制 | 持续项 | 0 | 本行无证据 Markdown 直链；保留版本/样本叙述，未重新认证 |
| 63 | `MT-004` 信息熵与重复规则 | MT-004a_WAIT_NEW_COUNTEREXAMPLE / MT-004b_DONE_V1.6.23 / RESEARCH_PLAYBOOK_REJECTED_BASELINE_ROUTE_NOT_REPRODUCED_WAIT_NEW_COUNTEREXAMPLE | 3 | 直链可达；保留原状态 |
| 64 | `MT-005` Description 入口减载 | DONE_202_CHARS | 2 | 直链可达；保留原状态 |
| 65 | `MT-006` 运行时语义 Reference 克制 | REAL_WRITING_PASSED / ENGINEERING_VERIFIED / DONE_V1.6.26 / RELEASED | 1 | 直链可达；保留原状态 |

## 本轮新增/复用的稳定子项

| 编号 | 需求与验证范围 | 当前登记 |
| --- | --- | --- |
| MT-004c | 单一加载条件，逐原子真实写稿 A/B，按风险登记路线；当前 R1 为五路，实际省读与成稿同时判断 | [20稿结果](candidate-r1-result.md)候选有独有硬问题；[命令读取R4—R6](../lint-command-route-r1/result.md)未一致减载，stdin/源码提示撤回；REJECTED / PRODUCT_RESTORED |
| MT-002a | 安装目录与cwd分离时命令可执行；保持lint提示/局部语义修正 | [两份真实终稿、四次命令](../command-cwd-real-draft-r1/result.md)均exit2→exit0且正文不变；两处说明及五镜像已同步，89项回归与五处quick_validate通过；ENGINEERING_VERIFIED / LOCAL_BRANCH_ONLY / NOT_RELEASED，不称减载 |
| WR-020c | 短/长稿批量无错率及实际错误数；真实resume同稿4—7版；D0/Hook终稿分开 | [20稿结果](candidate-r1-result.md)已完成；[七版链结果](../revision-stability-audit-r1/result.md)：28/28技术完成，已按原题面纠正合段过严判定，QUALITY_AUDIT_COMPLETE_GAPS_REGISTERED |
| AH-002b | 目标事实日期与格式示例、旧稿/排除材料的来源角色绑定 | [两路自然D0](../date-source-real-r1/result.md)均正确、默认Hook保持；REAL_R1_NOT_REPRODUCED / NOT_ADMITTED，旧旁路仅归档patch |
| HK-005b | 错回显耗尽、终态重放、晚到事件覆盖与数据回流 | 根代理已离线复现，REPRODUCED_NOT_FIXED |

WR-020c 的无错率只在明示检查范围内成立；错误稿件数、实际错误总数和分项错误数都须保留。技术无效与质量错误分开，四条相关会话不当作28个独立样本；合法的最新修改不判回退，初稿错误不直接否定整个质量闭环。20稿中19份有效、14份未观察到已确认硬问题，仅限两道整改题；六稿同D0默认Hook复放均保留D0，不能推广为总体无错或完整语义核验。

## AGENTS 减法与规则保留映射

按Git UTF-8/LF字节，AGENTS 4014 → 3407，净减 607 bytes（15.12%）。合并了重复的“真实结果通过后再工程”、测试层级与交付真实性说明；同时补回用户明确的轻量消融、功能改动独立worktree、研究复用与主代理复核要求，未因模型版本改变纪律。

| 原纪律/用户明确要求 | 压缩后的承载位置 |
| --- | --- |
| 最小reference/prompt/路由/同稿原型，立即真实验证 | 开发与验证2 |
| 每次reference减载真实写稿A/B，路线与样本按风险预登记 | 具体要求留在规格MT-004c/006；AGENTS仅保留真实验证总原则 |
| 先真实稿有效，再coordinator/adapter/镜像/组装/反控/回退 | 开发与验证3 |
| 候选硬回退先修/停，不扩量表、裁判、工程门掩盖 | 开发与验证3 |
| 新增兜底解决风险，不要求总体文采胜 | 开发与验证3 |
| 同一D0对比、独立采样只观察；迁移证据列未重跑宿主 | 开发与验证4 |
| 文档链接/diff，产品相关unit/smoke/quick validate，合并前全量与包体门 | 开发与验证5 |
| 仓库/分支/HEAD/工作树/基线/授权，保留未知改动 | Git与外部操作1 |
| 功能与较大改动、研究、基线、发布使用独立worktree | Git与外部操作1 |
| 所有代码文档commit，说明目的、范围、实际验证 | Git与外部操作2 |
| 每5commit/范围扩大review、baseline diff、轻量消融、回归 | Git与外部操作2 |
| main/push/tag/Release/平台写入需当次授权 | Git与外部操作3 |
| 禁破坏性reset/force push/无界清理，删除可恢复与路径核准 | Git与外部操作4 |
| 密钥、登录态、私有地址与未脱敏数据不得提交 | Git与外部操作4 |
| canonical/core/adapter/packages/maintenance/output边界 | 产品边界1 |
| 公开/付费隔离、公开修复同步、付费发布单独授权 | 产品边界2 |
| 安装/组装/启用/信任/真实执行分别举证；MIT与第三方许可 | 产品边界3 |
| 新构想先研究复用、职责清楚；复杂审查subagent且主代理复核 | 开发与验证1 |
| 摘要/branch/commit/命令结果/量化/未完成/风险，失败分歧保留 | 交付 |
| 写作少自证、UI简洁 | 交付 |

## 本次验证边界

初次规格审计仅执行Git状态/祖先检查、本地Markdown链接存在性检查、需求编号到覆盖矩阵检查和 `git diff --check`：当时8份活动/审计文档299处本地链接无缺失，56个需求编号无重复且均有coverage映射。它不替代另立的真实写稿结果。

基线以来第5次提交 `c9898219` 后已暂停做独立review、基线diff、轻量消融和相关回归：canonical与五套普通包恢复基线；20稿保留原型开关对照；23项可达性/台账测试通过。review指出压缩AGENTS时漏了脚本验证和通用外部写入授权边界，现已补回；最终减载以本页15.12%为准。七版链fixture漏列动态导入probe依赖，运行后另存补证、比对其规范化字节等于固定基线，不回写冻结fixture，不把事后补证冒充事前冻结。

第10次提交前再次完成[范围扩大检查](integration-validation.md)：命令路径原子获选，整体路由与stdin/源码提示撤回；12份产品文件各仅一行路径说明增量，112项直接回归和五处quick_validate通过。主代理复核193份导入证据及12份真实stream的模型/工具/可见读取量，独立review的两处文档终态/字段含义问题已纠正。不修改上述第5次检查的当时事实。
