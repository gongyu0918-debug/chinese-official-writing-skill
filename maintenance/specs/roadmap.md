# 状态与下一步

状态只表示当前仓库事实：`DONE` 已完成或已合并，`IN_PROGRESS` 有当前候选，`HOLD` 已实现但未达到产品准入，`TODO` 尚未实现。

## DONE

- `WR-001/002`：v1.6.4 事实与状态规则、保护性外扩精确删除和新闻边界已发布于 `v1.6.4@a737791c`；六份真实写稿和 SOL 校准见 [`v164-real-writing-final/result.md`](../tests/evidence/v164-real-writing-final/result.md)，发行回执见 [`release-1.6.4.md`](../tests/evidence/release-1.6.4.md)。
- `HK-001/003/004/006`：普通路径独立闭环、capability-first 单协调器、三宿主静态 adapter 和用户知情边界已建立；永久移除采用 README 语义说明与二次确认，未确认0改动、确认后隔离副本精确删除并完成真实写稿。
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
- `v1.6.11` 已发布至 GitHub、SkillHub.cn 与 ClawHub；产品 tag 指向 `15af538a`，ClawHub 为33文件无 Hook 包。v1.6.10 的公开状态已被本版取代。
- SkillHub 已加入 `office-efficiency`、`content-creation` 轻量检索信号；不声称平台写入双分类。
- GitHub 当前包统一 MIT；普通兼容包不含 Hook，OpenClaw GitHub 兼容包随仓库维护。
- v1.6.6 GitHub 与 SkillHub.cn 发布回执见 [`release-1.6.6.md`](../tests/evidence/release-1.6.6.md)；ClawHub、Red SkillHub 及其他平台未在该轮上传。SkillHub 公开 latest 与签名已传播，Keen、Sanbu 安全报告均为 benign。
- v1.6.7 GitHub、SkillHub.cn 与后续 ClawHub 无 Hook 包同步回执见 [`release-1.6.7.md`](../tests/evidence/release-1.6.7.md)。该版旧传播状态已由 v1.6.10 的 latest、签名和下载包闭环取代。

## IN_PROGRESS

- 当前没有准备合并或发布的公开产品候选。`codex/v1612-ul005-source-binding`、`codex/paid-outline-ot001-r3` 与 description 减载均是隔离实验，不冒充 `main` 增量。
- `MT-005a@dc5382ef` 与 `MT-005b1@14bf2cab` 已分别提交。制度簇四档、函件合并、删除“致辞”和“讲话致辞”并词均出现候选独有事实或承诺，分别 HOLD。只删重复“征求意见函”的 `MT-005b3r2` 与只删被“公告”覆盖的“采购公告”的 `MT-005b5` 均保持正向触发、事实和相邻边界；当前 description 为204字，相对原始280字累计减少76字（27.1%）。
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
- `UL-005` 篇幅验收来源绑定：`codex/v1612-ul005-source-binding@95ef7498` 已证明 span 的范围、原文和 hash 可机械闭合，但任意无关 span 仍可绑定任意增量，不能证明来源蕴含；现有同模型 verifier 又已有 R8 误放记录，因此原型不合入 main，继续 HOLD。下一原子固定原始 R8/R11 文本包并加入“相关局部 span 但新增目的/动作/结果”的对抗题。[本轮结果](../tests/evidence/post-v1611-research-closeout-20260820.md)

## TODO：已登记但不在本轮展开

1. `OT-001` 提纲冻结与终稿核对已完整转存到本地付费候选 `codex/paid-outline-review`；公开 `main` 不含该能力。Stop 收紧实验 `codex/paid-outline-ot001-r3@59531540` 已由本地 Qwen 精确删除纲外标题，并由 WorkBuddy / CodeBuddy 在线闭合无纲外片段的逐字回显；明确片段删除尚未取得当前 CodeBuddy 样本，不同步付费基线。`OT-002` 层级、重复和缺项修正仅在付费候选中继续。
2. `OT-001-composite` 的 Claude 有序组合已形成实验候选，但在 `UL-005` 闭环前不合入付费分支；Codex、WorkBuddy / CodeBuddy 组合入口仍不开放。
3. 会议纪要争议项原子：只在材料存在明确分歧且未表决时，验证“未决状态 + 互斥选项 + 发言来源”的侧车表达；先用同一真实纪要题确认不选边、不升级为决定，再决定是否进入文种叶。
4. 联网研究材料分型原子：只在用户允许联网时区分政策依据、数据支撑、参考案例和表述参考，并为缺口设置有限补搜与停止条件；外省政策不得冒充本地依据。先做一题混合来源报告，不先扩搜索工程。
5. 文件提取失败与降级交付仅作低优先级观察；出现真实扫描 PDF/不支持格式失败后，再验证停止、请求转换和 Markdown 降级，不先并入默认写稿流程。
6. `MT-005b2` 制度簇、`MT-005b3` 函件合并和 `MT-005b4` 讲话致辞均已由真实稿否决；后续只尝试未动的单个重复项或低风险簇，不为随机成功重跑失败原子。每个子原子仍选择最易漏触发的正向文种与相邻误触发题；`MT-005c` 受众合并最后单独处理。

## 不再重复

- 不把生命周期触发成功称为写稿质量成功。
- 不为没有合格 D1 的候选运行空 SOL 盲审。
- 不用独立采样的 Hook on/off 总胜负替代同一 D0/D1 的功能增量。
- 不在每个小修复后跑全量测试；全量门只在合并或发布前运行一次。
- 不因独立 npx CodeBuddy 的认证失败反复复制登录态；需要真实 CodeBuddy 样本时先核对 WorkBuddy 内置 CLI 的当前登录和版本，并如实区分两个入口。
