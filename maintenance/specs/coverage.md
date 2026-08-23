# 需求覆盖矩阵

`已覆盖` 表示存在对应产品实现和直接证据；`部分` 表示只有规则、工程链或一部分真实执行；`未覆盖` 表示尚无可交付实现。

| 需求 | 产品入口 | 真实写稿/同稿证据 | Hook/宿主证据 | 状态与缺口 |
| --- | --- | --- | --- | --- |
| `WR-001` 事实与状态 | `references/information-selection.md`、各文种叶 | v1.6.4 W1—W6 | 无 Hook 也成立 | 已覆盖；继续按真实反例迭代 |
| `WR-002` 保护性外扩 | `hooks/capabilities/protective_expansion/`、普通语义 references | 同一 E0/E1 29 组功能终审；W1—W6 | 单 coordinator、三宿主静态 companion | 已覆盖；公开 README 旧制度示例已用事实安全正文替换 |
| `WR-003` 责任承载 | `references/information-selection.md`、中央事务文体叶 | 20份真实稿；C02-R3、C03直连复测；v1.6.10 后5个状态/进行态小样本；[官方语料扩样](../tests/evidence/post-v1610-wr003-official-corpus-calibration-20260819.md) | 不属于独立 Hook | 已覆盖；官方扩样支持显式主体、近邻继承和工作事项作主语，未稳定改善的额外措辞已撤回 |
| `WR-004` 文种用语 | `references/formulaic-language.md`、新闻消息叶、SKILL直接路由 | 20类真实写稿，原型19/20；“编者按”修复后目标20/20 | 不适用 | 已覆盖并随 v1.6.6 发布 |
| `WR-005` 短稿自然度与常用语机械化 | `references/short-draft-naturalness.md`、信息选择和文种叶 | 短稿 R3 上限题8次，候选3胜0负1平且硬边界全 PASS；产品接入后两篇在线直写可用；常用语 R1—R6 真实调用 | 交付洁净度与重复清理只作可选兜底 | 短稿自然度已随 v1.6.7 发布；硬下限归 under-length；常用语 R1—R6 均 HOLD，本版未改总表 |
| `WR-006` 审稿模式 | SKILL 任务模式、Hook bypass | OpenCode Go 自然审稿请求 | 自然审稿、复合成稿和引语反控已完成 | 已随 v1.6.9 发布 |
| `WR-007` 语义减载与自然表达 | `references/anti-ai-patterns.md`、`references/genre-playbook-request.md` | R1 16稿；R2—R4 20稿；组合后24/24技术有效 | 不属于独立 Hook | 已随 v1.6.10 发布；三方冷审无候选独有硬失败，只写到现有事实和状态，压住供应商确定后的后续动作外推 |
| `WR-008` 标题与正文边界 | canonical SKILL 主入口标题条目 | 16/16 生成无回退；12/12 同稿修复，候选6/6精确；自然路由R2两家均通过 | 不属于独立 Hook | 已随 v1.6.10 发布；主标题无句号并空一行、层级标题无句号、编号正文句保留句号 |
| `WR-009` 文后提示与正文分区 | `references/information-selection.md`、`scripts/prose_lint.py` | OpenCode Go 同题基线/候选各1稿；候选去除横线包装并形成独立正文外区域 | 不属于独立 Hook；交付洁净度只作可选包装清理 | 已随 v1.6.10 发布；保持正文外独立区域，不增加 Hook |
| `WR-010` 会议结论与承诺证据 | 当前 `references/genre-playbook-minutes.md` 已覆盖议定、未决、责任和期限；内部 claim—evidence sidecar 未实现 | 2026-08-20 三题6稿 A/B：基线3/3正确处理弱意向、未回应指派、明确承诺、后续修正和权威交办；正文候选无改善且把“未确认承接”带入成稿 | 不属于现有 Hook；若做 sidecar 须与 `UL-005` 的来源蕴含一起验证 | `PARTIAL/HOLD`；正文能力已被当前结果覆盖，候选 `9423d951` 不合入；只保留正文外语义相关证据绑定原子 |
| `WR-011` 新闻声明级核验 | `references/genre-playbook-news-message.md`；来源名称/载体、原始出处和限定来源结论分开 | [R3 三轮25稿](../tests/evidence/post-v1612-news-claim-matrix-r3-result-20260822.md)：先复现机构性质与包装回退，再分别收窄名称/载体和限定来源结论；最终五路候选5/5目标通过，1处文字重复 WARN | 不新增 Hook、独立矩阵叶或路由胶水 | `DONE`；上一轮 HOLD 已由后续原子结果取代，最小新闻叶及四套镜像已随 v1.6.13 发布 |
| `WR-012` 正式发文意图路由 | 当前 `references/genre-routing.md` 与 SKILL 已有工作材料/正式发文边界；本轮候选未合入 | [三题6稿 A/B](../tests/evidence/v1612-formal-issuance-intent-result-20260821.md)：内部情况说明方向改善；明确正式报告追加正文外自证，普通业务函新增时间和过程事实 | 不属于 Hook；WorkBuddy / CodeBuddy 2.115.0 六次退出均为0 | `PARTIAL/HOLD`；当前基线已覆盖明确正式发文和普通业务函的主要边界，本轮候选两项硬回退，不合入产品 |
| `WR-013` 事实支撑的一般原因与即时作用 | SKILL 起草入口、`references/information-selection.md`、新闻消息叶 | [R8.4 五路 A—E](../tests/evidence/wr013b-r8-role-effect/result-r84.md)：OpenCode/Ollama/MiniMax 在活动稿写出一层即时作用，Alibaba 部分命中，Luna 保守；采购原因前置与停机控制均安全 | 不新增 Hook；canonical 与四套普通镜像同步 | `DONE`；发布者角色、稀疏活动边界和入口推断冲突已随 v1.6.13 发布 |
| `WR-014` 证据可见性与事项进度 | 当前信息选择、状态和事实边界覆盖三态、资金能力及能力/计划意向；R1 组合原型不合入 | [R3](../tests/evidence/wr014-r3-capacity-plan-20260822/result.md) A五路有效稿守住“可安排”，B四路有效稿守住“拟于”，OpenCode B两次技术失败 | 不新增 Hook、审批模板或保护性声明；canonical 与四套普通镜像同步45字符状态锚 | `DONE`；能力与计划状态反例已原子闭环并随 v1.6.14 发布 |
| `WR-018` 丰富材料下的事务稿密度 | 当前 SKILL、信息选择和三类既有文种路由；没有产品候选 | [五路三文种真实写稿](../tests/evidence/wr018-rich-material-baseline-20260822/result.md)：13/15硬通过，MiniMax一项状态升级、Ollama一项直接交付失败，0/15功能性过薄 | 只读 Codex Desktop 五家 provider；不启用 Hook、不设统一字数门 | `DONE_CURRENT_PRODUCT_NO_NEW_RULE`；丰富材料能按文种展开，无跨模型密度缺口 |
| `SB-001` 头重脚轻与裸提纲句搬移 | R3.1—R3.5 仅在隔离分支验证，产品改动未合入 | [五轮真实顺稿](../tests/evidence/sb001-r3-subject-preserving-result.md)：部分路线可精确搬移，但跨 provider 反复出现未交稿、正文旁白、跨题单位污染、章节/整稿重复和状态改写 | 不新增段长门、结构评分器或 Hook | `TERMINATED`；提示词/路由方向经多次最小化仍有候选独有硬回退，证据保留，产品保持原状 |
| `HK-001` 无 Hook 闭环 | canonical Skill、普通 packages | v1.6.4 六稿 | 普通镜像排除 Hook | 已覆盖 |
| `HK-002` 写稿后插入 | `UserPromptSubmit` + `PostToolUse` + `Stop` coordinator | 不作为文采门 | Codex、Claude Code、WorkBuddy 5.3.13 / CodeBuddy 2.115.0 当前在线 | 已覆盖生命周期位置；各 capability 的 D1 结果仍分项记录 |
| `HK-003` 单协调器 | `hooks/core/gate_stop_hook.py` | 同一任务仅一个 capability | 官方说明同事件多 Hook 可并发，因此保持单 coordinator | 已覆盖 |
| `HK-004` 宿主薄适配 | `hooks/adapters/` | 不适用 | Codex、Claude、CodeBuddy 官方契约与静态包 | 已覆盖结构；CodeBuddy Hooks 仍为 Beta |
| `HK-005` 故障回退 | coordinator 和 capability runtime | 当前 Codex/Claude 均选择 D0 并闭合 hash | WorkBuddy 当前重复清理样本选择 E1并闭合hash，临时关闭零事务 | 已覆盖主要路径；错误终稿不得误标成功继续保留反控 |
| `HK-006` 知情与关闭 | `hooks/README.md`、opt-out classifier | 普通路径六稿；永久移除后真实写稿 | 未确认逐字不变；二次确认后隔离副本17文件移除、SKILL单点编辑；自然审稿、复合成稿和引语反控已完成 | 已覆盖 |
| `HK-008` 终态数据最小留存 | `hooks/core/gate_stop_hook.py`、`hooks/README.md`、`host-capabilities.json` | v1.6.14 的[终态脱敏](../tests/evidence/hk008-retention-redaction-20260822/result.md)已发布；后续[HK-008b](../tests/evidence/hk008-bootstrap-cleanup-r1/result.md)覆盖 detect 失败、缺 state、中断恢复、并发 owner、锁 I/O 分流和起草/审稿分类 | 前序候选已完成当前 CodeBuddy Skill/Read→2次Stop→emit→脱敏；最终候选普通协议未变，54文件重组装/校验通过，38项 Hook、673项全量通过 | `MERGE_CANDIDATE_NOT_RELEASED`；fatal-lock 最终补丁未重跑在线写稿，默认关闭和窄 opt-in 不变，硬退出后无后续 Stop 仍需人工清理，POSIX仅分支单测 |
| `UL-001` under-only 触发 | `hooks/capabilities/under_length/runtime.py` | Alibaba 268→342；Codex 268→350；Claude 268→344 | Codex、Claude 当前在线选择 D1；并行 Skill/材料读取竞态修复后 Codex 事务正常建立并安全选择 D0 | 已覆盖并随 v1.6.5 发布；竞态修复不调整篇幅语义门 |
| `UL-002` 安全扩写 | under revision/verdict prompt | 三条 provider 的失败稿驱动语义收窄；三份获选 D1 | 同一能力在两宿主在线执行 | 已覆盖当前事实充分采购请示；稀疏材料仍允许 D0 回退 |
| `UL-003` 产品准入 | 同一 D0/D1 功能门 | 两次独立 SOL max 均为 `ACCEPT` | selection/delivery/final hash 闭环 | 已覆盖目标功能；不以独立 on/off 总胜负替代 |
| `UL-004` 证据迁移 | adapter/core/runtime hash 分层 | CodeBuddy 旧完整在线；当前能力同稿复放；中文数量透明归纳同稿 106→206 字并由真实 verifier 选 D1 | 当前 WorkBuddy / CodeBuddy 又以 106→190 字候选完成在线事务；新增对象与错归属使语义层选 D0，交付 hash 闭环 | 已覆盖“同数方面→项”只进入语义核验的窄放宽；独立数量变化仍机械回退 |
| `UL-005` 语义验收来源绑定 | `hooks/capabilities/under_length/runtime.py` 的单稿事实台账、同 span 角色绑定与 verifier 填表指引 | R2—R9 依次覆盖真实但无关 span、局部相关但新增谓语、跨 span 拼接、透明改写和低强度推断；[R9](../tests/evidence/ul005-fact-ledger-r9-codebuddy-20260822.md) 对同一61字 D0 拒绝111字风险 D1并接受114字受控 D1 | WorkBuddy / CodeBuddy 2.115.0 两次完成台账、语义选择和终稿 hash；25项 focused、62项相关和655项全量单测通过 | `DONE`；当前原子已随 v1.6.13 发布。结果只证明该台账边界和正反样本，不承诺所有文种、所有模型都能生成安全长稿 |
| `CL-001` 交付洁净度 | `hooks/capabilities/delivery_cleanliness/` | 三 provider 5/5 精确整理；SOL max 全 PASS | 三宿主静态组装；Claude Code、Codex 与当前 WorkBuddy / CodeBuddy 均有在线 D1/hash 闭环 | 已覆盖并随 v1.6.5 发布 |
| `RP-001` 重复与高相似句 | `hooks/capabilities/repetition_cleanup/` | 三 provider 5 组；SOL max 功能 PASS，长稿 1 WARN | 三宿主静态组装；Codex、WorkBuddy / CodeBuddy 与当前 Claude Code 均有在线 E1/hash 闭环 | 已覆盖并随 v1.6.5 发布 |
| `AH-001` 引用与硬锚 | `hooks/shared/hard_anchors.py`；under/over 机械门与既有语义验收 | 24/24 先行实验；12份原型/回放；12次缺口修复真实修订；v1.6.10 后三路冷审复现回指/序号/修辞三处窄缺口；修辞压缩在线选 D1、相对期限变化复放选 D0 | 单 coordinator 内共享，不另起 Hook；三宿主 companion 静态组装；本轮 Claude Code 在线 + 当前 runtime 同稿复放 | 已随 v1.6.10 发布基础能力；窄修复已完成准入，回指豁免仅保留“前一项”等，`第N项`继续硬锚，`一方面/另一方面`不作业务数量；其他改稿能力尚未迁移 |
| `OV-001` 超长收束 | 已发布 runtime、语义判定校准和 observer sentence-target 约束 | [五路真实写稿](../tests/evidence/post-v1613-writing-atoms-r1-20260822/ov001-judgment-writer-result.md) 222—251字且完整；[三题五路判定](../tests/evidence/post-v1613-writing-atoms-r1-20260822/ov001-judgment-verifier-result.md) 15/15方向一致；[四方盲审](../tests/evidence/post-v1613-writing-atoms-r1-20260822/ov001-four-reviewer-extract.md) 两例均4/4选中达标稿 | [CodeBuddy 328→236](../tests/evidence/post-v1613-writing-atoms-r1-20260822/ov001-judgment-live-result.md) 与 [496→229](../tests/evidence/post-v1613-writing-atoms-r1-20260822/ov001-cb-r3-result.md) 均一次压缩、`semantic_pass`、D1/hash闭合 | `DONE`；已随 v1.6.14 发布，不增加段长门，Hook 继续默认关闭、按单能力窄启用；等待成本和跨标题删除风险继续观察 |
| `OT-001` 提纲冻结与核对 | 本地付费候选 `codex/paid-outline-review`；公开 `main` 不含提纲实现 | 既有稀疏正文、完整文稿、固定提纲、改稿和长稿；详细改写已验证未决/已决状态与算术去重，五路组合序列又完成骨架保持、精确修正和压缩 | 历史三宿主在线；当前 WorkBuddy / CodeBuddy 2.115.0 持久会话已完成 outline Agent、Stop 阻断和明确纲外标题21字符删除，其余正文逐字同 hash | 付费候选当前写稿语义和精确删除已闭环，不发布；结构化组合 coordinator、章节/hash 核验及其 Stop 生命周期仍未实现 |
| `OT-001-composite` 骨架保持的有序改稿 | 仅在本地付费候选继续；不进入公开包 | 五个 Codex Desktop 路线依次完成详细改写、精确修正、压缩和必要叶子修复；标题存在状态、文种、段落顺序和未决状态保持，材料外标题错误可修正 | 未新增组合 Hook 或宿主胶水；现有 OT 生命周期不能替代组合生命周期 | `PARTIAL`；真实写稿序列完成，工程化与真实 Stop 组合仍未覆盖 |
| 联网公开来源核验 | `references/external-research.md` 与四套普通镜像 | [R2d—R2h](../tests/evidence/online-source-use-r2h-result-20260822.md)：来源用途不混用；R2h 五路5/5绑定实际打开的上海命中 URL；R2f—R2h 12/15只补搜一次 | 不新增搜索 Hook、代理或调用门禁 | `DONE`；用途分型和命中页绑定已随 v1.6.13 发布。严格一次工具调用为模型/宿主非确定性限制，纯提示词方向已终止 |
| `OT-002` 提纲修正 | 本地付费候选规格 | 尚未运行专门样本 | 复用 OT-001 正文前检查点，不在 Stop 猜提纲 | 未覆盖；不进入公开版能力范围 |
| `MT-001` 真实结果优先 | `AGENTS.md`、本规格层 | v1.6.4 已采用；Codex GUI 本地 Qwen3.8 27B 5项串行评估为4 PASS、1 WARN | 5/5技术完成，但0/5具有可核验读取回执；本地 writer 不兼任终审 | 已覆盖规则；本地27B暂不纳入任务池，64K别名仅保留为实验资产 |
| `MT-002` 可达性 | SKILL、说明、组装器、维护索引 | 不适用 | [当前审计](../tests/evidence/post-v1610-maintenance-reachability-audit-20260819.md)：28脚本、21 CLI、189非入口 Markdown、195活动链接文档均零孤儿或失效入口 | 当前轮已覆盖并固化回归；冻结历史 evidence 旧路径不回写 |
| `MT-003` 公开面克制 | 根 README、维护索引 | 最近五次主要证据 | 内部 HOLD 不进入产品宣传 | 持续项 |
| `MT-004` 信息熵与重复规则 | SKILL/reference 路由与叶子停止条件 | 12组真实读取；24次组合写稿 | 不属于 Hook | `OBSERVE`；已扫描重复，尚无真实稿回退，不为去重破坏叶子自包含 |
| `MT-005` Description 入口减载 | canonical 与四套镜像保持已发布204字；通过项依次删除负向句、新闻细项、重复“征求意见函”和被“公告”覆盖的“采购公告” | 制度、函件、讲话致辞18次扩大 A/B 仍有候选独有硬回退；`MT-005c` 首轮 CLI 触发通过，但[合并前跟进](../tests/evidence/mt005c-school-repair-followup-20260823.md)先暴露显式“学校”缺失，196字回补再出现两份正向稿硬失败 | 既有五路 Desktop、Codex CLI 0.144.6 同体隔离；合并前全量门真实捕获 P058 | `005a/005b1/005b3r2/005b5` 已随 v1.6.12 发布；`005c` 已验证并拒绝接入；`005b2/005b3/005b4` 不动。相对原始280字累计减76字（27.1%） |

## 当前语义层收束

- `WR-003/004` 已随 v1.6.6 发布；`WR-005` 短稿自然收束已随 v1.6.7 发布；常用语默认拆分仍 HOLD。
- R1 降低了固定开头词频，却增加了事实硬失败和另一类空泛、重复、自证；R2 工程上稳定，但基线6胜、候选4胜、难分2，且候选仍有1个事实硬失败。
- 单个正式连接词不构成机械化；只有固定开头、承启、总结、结尾或段落骨架成簇复现，且对任务没有功能贡献时，才计入同质化风险。
- 常用语 R4—R6 的更小拆分仍出现硬回退，停止继续修改总表。短稿自然度和实际重复清理由各自已验证机制承担，不用新的统一反机械规则覆盖所有文种。

## CodeBuddy 证据迁移明细

旧 CodeBuddy 在线成功包与当前 companion 的宿主层 SHA-256：

| 文件 | SHA-256 | 是否变化 |
| --- | --- | --- |
| `hooks/hooks.json` | `5f02f7b94b7c5b0aedd554d1d6cb2a85d1612f1296868960068b071fd9cf26d9` | 未变化 |
| `scripts/host_gate_adapter.py` | `d7ea6dad98991d7b650a95570aff6b2f7901f7b822db77d84f405d7a8c548cde` | 未变化 |
| `skills/.../hooks/gate_stop_hook.py` | `abe469b00e5b04adefdba240bd78afa4bfeed82b67a5ce0810a13e0bf7786834` | 未变化 |
| `under_length/runtime.py` | 当前组装时要求与 canonical 逐字一致 | 已变化，且是宿主无关能力层 |

旧在线样本完成 D0 180 字、D1 816 字、拒绝 D1、精确 D0 回显；当前变化后的 runtime 已用该原始 D0/D1 复放并拒绝不安全新增流程。Codex 与 Claude Code 又以当前 runtime 完成在线 Stop 生命周期并选择可用 D1。2026-08-19，WorkBuddy 5.3.13 / CodeBuddy CLI 2.115.0 先在透明归纳放宽前以106→192字样本完成机械回退；放宽后又以106→190字候选进入语义层，并因新增对象与错归属选择 D0，两个阶段终稿 hash 均与 D0 一致。该组样本只证明对应阶段的保守回退与当前语义拒绝，不推定其他 CodeBuddy capability 均已重跑。

2026-08-20 又以同一 WorkBuddy / CodeBuddy 入口补了两项当前样本：OV 两条超限 D0 均建立事务并安全回显，但未形成压缩候选；付费 OT 收紧候选完成 outline Agent、Stop 阻断和无纲外片段的逐字 D0/D1。它们分别证明 OV 的安全回退和 OT 的 exact replay，不互相替代，也不把 D0 闭环称为 D1 功能收益。

## 官方契约依据

- Codex 官方 Hooks 说明：Stop 在主 Agent 完成响应时运行，携带 `last_assistant_message` 与 `stop_hook_active`；插件可通过根目录 `hooks/hooks.json` 加载，命令 Hook 需要显式信任。同事件的多个 Hook 会并发启动，因此本项目保持单 coordinator。[Codex Hooks](https://learn.chatgpt.com/docs/hooks.md)
- Claude Code 官方说明：Stop 在主 Agent 完成响应时运行；plugin 根使用 `hooks/hooks.json`，脚本通过 `${CLAUDE_PLUGIN_ROOT}`、数据通过 `${CLAUDE_PLUGIN_DATA}` 定位；用 `stop_hook_active` 防止循环。[Claude Code Hooks](https://code.claude.com/docs/en/hooks)
- CodeBuddy 官方说明：plugin Hook 位于根目录 `hooks/hooks.json`，使用 `${CODEBUDDY_PLUGIN_ROOT}` 与 `${CODEBUDDY_PLUGIN_DATA}`；多来源 Hook 合并并并行，Windows 由 Git Bash 执行命令；Hooks 当前为 Beta。[CodeBuddy Hooks](https://www.codebuddy.ai/docs/cli/hooks)
- OpenSpec 只作为文档设计参考：需求、变更和证据分层；本仓库未安装其 CLI 或 workflow。[OpenSpec 核心概念](https://github.com/Fission-AI/OpenSpec/blob/main/docs/overview.md)
