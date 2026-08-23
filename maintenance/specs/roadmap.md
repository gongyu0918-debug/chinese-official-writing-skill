# 状态与下一步

状态只表示当前仓库事实：`DONE` 已完成或已合并，`IN_PROGRESS` 有当前候选，`HOLD` 已实现但仍可能继续收窄，`TERMINATED` 经多轮最小化仍有硬回退且当前方向已停止，`TODO` 尚未实现。

## DONE

- `WR-001/002`：v1.6.4 事实与状态规则、保护性外扩精确删除和新闻边界已发布于 `v1.6.4@a737791c`；六份真实写稿和 SOL 校准见 [`v164-real-writing-final/result.md`](../tests/evidence/v164-real-writing-final/result.md)，发行回执见 [`release-1.6.4.md`](../tests/evidence/release-1.6.4.md)。
- `HK-001/003/004/006`：普通路径独立闭环、capability-first 单协调器、Codex、Claude Code、CodeBuddy 三宿主静态 adapter 和用户知情边界已建立；ZCode 第四宿主 adapter 已在独立候选完成真实 CLI 生命周期，待干净合并。永久移除采用 README 语义说明与二次确认，未确认0改动、确认后隔离副本精确删除并完成真实写稿。
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
- `v1.6.14` 已发布至 GitHub、SkillHub.cn 与 ClawHub；产品 tag 指向 `b0e5d5c4`，ClawHub 为33文件无 Hook 包。v1.6.13 及更早公开状态已被本版取代。
- `OV-001` 语义判定校准与 sentence-target、`HK-008` 终态脱敏、`WR-014-R3` 能力/计划状态锚已随 v1.6.14 发布；Hook 默认关闭和按单能力窄启用不变。
- `WR-013` 一般原因、即时作用与发布者角色边界已完成五路真实写稿、入口冲突消融和非新闻控制，并随 v1.6.13 发布。
- `WR-011` 新闻声明级核验已把机构性质、来源身份/原始出处和限定来源结论拆成三个原子；R3 三轮25稿后五路最终候选5/5守住目标边界，最小新闻叶及四套镜像已随 v1.6.13 发布。
- `UL-005` 当前来源台账原子已闭环：WorkBuddy / CodeBuddy 2.115.0 对同一61字 D0 分别拒绝含强保障、材料外用途和多余请批语的111字 D1，并接受只含同一事实 span 低强度推断的114字 D1；两次终稿 hash 闭合。当前实现与 R9 证据已进入本地 `main`，不外推为所有文种、所有模型的自然扩写保证。[结果](../tests/evidence/ul005-fact-ledger-r9-codebuddy-20260822.md)
- 联网来源用途分型与命中页绑定已完成：国家规范、本地执行、外省比较不混用，命中页元数据和 URL 绑定实际打开页；R2f—R2h 五路15稿中12稿只做一次定向补搜，最终 R2h 五路5/5写入真实上海命中 URL。严格工具调用次数不能由提示词确定性保证。[结果](../tests/evidence/online-source-use-r2h-result-20260822.md)
- SkillHub 已加入 `office-efficiency`、`content-creation` 轻量检索信号；不声称平台写入双分类。
- GitHub 当前包统一 MIT；普通兼容包不含 Hook，OpenClaw GitHub 兼容包随仓库维护。
- v1.6.6 GitHub 与 SkillHub.cn 发布回执见 [`release-1.6.6.md`](../tests/evidence/release-1.6.6.md)；ClawHub、Red SkillHub 及其他平台未在该轮上传。SkillHub 公开 latest 与签名已传播，Keen、Sanbu 安全报告均为 benign。
- v1.6.7 GitHub、SkillHub.cn 与后续 ClawHub 无 Hook 包同步回执见 [`release-1.6.7.md`](../tests/evidence/release-1.6.7.md)。该版旧传播状态已由 v1.6.10 的 latest、签名和下载包闭环取代。

## IN_PROGRESS

- `HK-004-ZCode`：社区 CLI wrapper 携带的 ZCode runtime 0.16.3 已通过 OpenCodex 注入 qwen3.8-max，当前 Skill、UserPromptSubmit、Read、Stop、完整 D0、hash 和终态脱敏闭环；专用 `.zcode-plugin` 54文件 companion 已组装。Qwen Code 与 Kimi Code CLI 只完成普通 Skill/事件边界研究，不冒充完整 Hook 适配。[结果](../tests/evidence/domestic-cli-hooks-v1615/result.md)
- v1.6.14 已包含 `WR-013`、`WR-011` R3、`UL-005` R9、联网来源用途/命中页绑定及本轮四个公开原子。正式发文意图仍保留现有基线；付费提纲的结构化组合 Hook 和 `OT-002` 继续只在付费分支推进，不进入公开版。
- `MT-005b2/b3/b4` 的18次扩大真实 A/B 仍分别存在范围扩大、未给日期、材料外责任/效果或未交稿，不接入；独立 `MT-005c` 初轮触发通过后在合并前全量门暴露“学校”缺词，196字回补又出现两份正向稿硬失败，最终恢复已发布204字，不接入。
- `OC-001` 已把十二份官方采购、通知、报告、纪要、总结/调研和活动新闻抽成结构/论证方法基线；`WR-018` 五路三文种为13/15硬通过、0/15功能性过薄，当前产品不增加字数门、固定模板或统一扩写流程。
- `WR-010` 会议承诺语义正文候选完成三题6稿真实 A/B：当前基线3/3已覆盖弱意向、未回应指派、明确承诺、后续修正和权威交办；候选无目标改善且把内部审计措辞带入正式正文，不合入。只保留与 `UL-005` 共同验证的正文外 claim—evidence sidecar 构想。
- `HK-008` 已针对 SkillHub Sanbu 指出的长期快照风险完成终态数据减载：84项 focused 回归和 CodeBuddy 2.115.0 真实采购申请均通过，原请求、D0、观察包和事务文件在终态移除，正文逐字不变；宿主自身日志与终态前异常退出仍按明确边界管理。[结果](../tests/evidence/hk008-retention-redaction-20260822/result.md)
- `HK-008b` 已进入本地 `main`，补齐 detect 失败、缺 state、中断恢复、并发 owner、锁 I/O 分流和“待审核+不修改文件”起草反例；固定基线消融、38项 Hook 和673项全量通过。前序普通协议的 CodeBuddy 生命周期可迁移，最终54文件包另行组装/校验；fatal-lock 补丁未冒充在线重跑。合入不含相邻研究文件，尚未推送或发布。[结果](../tests/evidence/hk008-bootstrap-cleanup-r1/result.md)
- `WR-019c/019d` 已合入本地 `main`：两模型真实稿分别修复 PUE/API 标准译名与翻译式框架，同时守住未知代号、主体不明、合法对比和未决状态；不改 lint、Hook 或 description，尚未推送或发布。019a“口径”和019b行业词当前基线已通过，不增加无收益规则。
- `WR-020a1` 首次起草已在两次缩小后拒绝：前置有限建议有局部价值，但候选出现薄稿、年度报告结构弱化、信息缺失状态和草案归属扩张，不加入固定结论位置。`WR-014-R4` 只保留同一D0已通过的复核/改稿缺失指标修正，并已合入本地 `main`；`WR-020b1` 讲话输入任务卡仍是下一原子。
- `MT-005b6/b6a` 已完成20次真实调用并拒绝接入：19字制度伞词和5字“管理办法”删除均保持触发，但有候选独有职责/依据/责任归属。description 继续204字；下一次只测“实施细则→细则”。
- 会议争议来源原子三组基线已经完整实现目标，不叠加重复规则；联网用途和命中页绑定已由 R2d—R2h 后续原子取代旧组合 HOLD，严格一次工具调用只保留为非确定性限制。
- 新闻声明级核验上一轮的机构性质、来源身份/原始出处混淆和限定来源外推已分别拆成原子；R3 最终五路候选均守住目标边界，不增加 Hook 或矩阵模板。正式发文意图仍只改善内部情况说明，在正式报告和普通业务函存在硬回退。
- 本地 Qwen3.8 27B 评估：Codex GUI 5项串行任务为4份写稿 PASS、1份审稿 WARN，运行稳定但没有可核验的 Skill 文件读取回执。当前不纳入任务池；64K Ollama 别名与证据保留，模型已停止释放显存。
- GitHub README 制度示例替换已随 v1.6.8 发布：历史 evidence 原文未改，公开页使用事实安全的八条制度正文。

### 本轮收束顺序

1. `WR-003/004` 已完成中央 reference、直接路由、新闻标识和普通镜像集成并随 v1.6.6 发布。
2. `WR-005` 常用语机械化已完成 R1—R6。删词、删总表、取消普通加载和“按材料选择”均出现事实、篇幅或文种硬回退；canonical 保持不变，下一版不再改总表或叠加反机械 prompt。
3. 准备合并或发布时再运行一次全量门；候选阶段只保留路由、镜像、构建与可达性最小验证。
4. Hook 复杂度按行为不变的小原子处理：`handle_stop`、超时/锁阈值、`detect_transaction`、`evaluate_candidate`、`_dispatch_transaction_locked` 和 `locate_candidates` 均已完成；当前 Hook core 与 review gate 已无超过80行或25个决策节点的函数。规则表分域留作独立低优先级原子。

## HOLD

- `WR-005` 原短稿自然度 R1/R2：把自然度与硬下限混在一起，分别形成系统性偏短和材料外补字，保留为 HOLD；已由上限题 R3 取代后续方向。
- `WR-005` 常用语机械化候选：R1—R6 均未准入；最终 R6 8/8技术有效，但候选仍有篇幅、职责扩张、安全要求和材料外号召硬失败。结果见 [`v167-formulaic-mechanicality-real-first/result.md`](../tests/evidence/v167-formulaic-mechanicality-real-first/result.md)。
- 旧 `length-band-hook-v162`、`under-length-hook-v162-v2`、`v163-protective-expansion-gate` 继续保持历史 HOLD，不复活旧验收结论。
- `WR-012` 正式发文意图路由：内部情况说明样本方向成立，明确正式报告和普通业务函分别出现正文外自证、材料外时间/过程事实，继续 HOLD。当前 main 的已有边界优于本轮候选，不叠加规则。[结果](../tests/evidence/v1612-formal-issuance-intent-result-20260821.md)

## TERMINATED

- `SB-001` 章节均衡提示词/路由：R3.1—R3.5 已依次尝试语义叶、路由减载、底稿形态触发、过程隔离和近场卡。虽有多路精确搬移，但最终仍出现 Alibaba 章节/整稿重复、未决状态改写和无关残片，OpenCode 另有一次只承诺交付而未交稿；产品改动不合入，不再向第三处堆规则。[结果](../tests/evidence/sb001-r3-subject-preserving-result.md)
- 联网严格“一次补搜”的纯提示词方向：R2f—R2h 已两次按失败增加最小停止语义，15稿中12稿精确一次；超额调用在 Luna、Ollama 间转移，说明不能靠继续叠字形成确定性门。产品保留有限补搜写作规则；除非出现值得付出工程复杂度的新宿主级机制，不再追加提示词。[结果](../tests/evidence/online-source-use-r2h-result-20260822.md)

## TODO：已登记但不在本轮展开

1. `OT-001` 提纲冻结与终稿核对完整保留在本地付费候选 `codex/paid-outline-review`；公开 `main` 不含该能力。当前付费候选已用 WorkBuddy / CodeBuddy 持久会话闭合明确纲外标题的21字符精确删除，其余正文逐字同 hash；不发布。
2. `OT-001-composite` 的真实写稿序列已在五个 Codex Desktop 路线完成“详细改写→精确修正→压缩→叶子修复”，标题存在状态、文种和段落顺序保持，事实错误不被冻结。尚未实现的是结构化组合 coordinator 及其真实 Stop 生命周期；只在付费分支继续，不进入公开版。
3. 会议纪要争议项已由当前 main 三组真实基线覆盖；没有新反例前不增加侧车模板或重复规则。
4. 文件提取失败与降级交付仅作低优先级观察；出现真实扫描 PDF/不支持格式失败后，再验证停止、请求转换和 Markdown 降级，不先并入默认写稿流程。
5. `MT-005b2` 制度簇、`MT-005b3` 函件合并和 `MT-005b4` 讲话致辞均已由真实稿否决；`MT-005c` 也已在合并前跟进中拒绝接入。没有新的实际误触发或漏触发证据前，不为随机成功重跑这些失败原子。
6. `WR-010-M2` 新题已由当前基线完整保持正式规则、候选规则、一次性安排和未回应指派；不增加 claim—evidence sidecar、竞品表格、负责人/期限补全或多格式渲染工程。只有新真实反例才重新启动。

## 不再重复

- 不把生命周期触发成功称为写稿质量成功。
- 不为没有合格 D1 的候选运行空 SOL 盲审。
- 不用独立采样的 Hook on/off 总胜负替代同一 D0/D1 的功能增量。
- 不在每个小修复后跑全量测试；全量门只在合并或发布前运行一次。
- 不因独立 npx CodeBuddy 的认证失败反复复制登录态；需要真实 CodeBuddy 样本时先核对 WorkBuddy 内置 CLI 的当前登录和版本，并如实区分两个入口。
