# 状态与下一步

状态只表示当前仓库事实：`DONE` 已完成或已合并，`IN_PROGRESS` 有当前候选，`HOLD` 已实现但未达到产品准入，`TODO` 尚未实现。

## DONE

- `WR-001/002`：v1.6.4 事实与状态规则、保护性外扩精确删除和新闻边界已发布于 `v1.6.4@a737791c`；六份真实写稿和 SOL 校准见 [`v164-real-writing-final/result.md`](../tests/evidence/v164-real-writing-final/result.md)，发行回执见 [`release-1.6.4.md`](../tests/evidence/release-1.6.4.md)。
- `HK-001/003/004/006`：普通路径独立闭环、capability-first 单协调器、三宿主静态 adapter 和用户知情边界已建立；永久移除采用 README 语义说明与二次确认，未确认0改动、确认后隔离副本精确删除并完成真实写稿。
- `UL-001—004`：篇幅不足 Hook 已按真实写稿优先完成语义修复，并随 `v1.6.5@81061bd7` 发布。Alibaba 直修 268→342，Codex 在线 268→350，Claude Code 在线 268→344；两次独立 SOL max 均判可用 D1 `ACCEPT`。CodeBuddy 当前只保留同构静态迁移证据，不冒充在线成功。结果见 [`v164-under-length-real-first-result-20260814.md`](../tests/evidence/v164-under-length-real-first-result-20260814.md)。
- `CL-001`：交付洁净度已先用三条指定 DeepSeek V4 Flash 路线完成 5/5 同稿真实整理，再接入独立静态 capability，并随 v1.6.5 发布。SOL max 五组全 PASS；Claude Code 与 Codex 在线生命周期均选择 D1 并闭合哈希。结果见 [`delivery-cleanliness-real-first/result.md`](../tests/evidence/delivery-cleanliness-real-first/result.md)。
- `RP-001`：重复句与高相似句已先完成三 provider 的 5 组真实删除和 SOL max 功能终审，再接入纯删除 capability，并随 v1.6.5 发布。长稿 1 个自然度 WARN 保留为后续样本，不影响已验证的目标功能。
- `WR-003`：20份真实稿与候选直连复测已验证跨文种责任承载；最小规则和镜像已随 `v1.6.6@b49da7f2` 发布。
- `WR-004`：20类事务文体已完成真实写稿，原型19/20功能成立；“编者按”标识修复后目标功能20/20，中央直接叶已随 `v1.6.6@b49da7f2` 发布。
- `WR-005` 短稿自然度：上限题 R3 为候选3胜、基线0胜、难分1，候选四稿硬边界全 PASS；最小路由接入后又以 Ollama 报告和 Alibaba 新闻完成两篇在线直写，均读取新叶且可直接使用，已随 `v1.6.7@44347003` 发布。明确篇幅下限继续由 under-length 处理。
- `OV-001` 超长收束：真实 D0 498→285、SOL max 六项 PASS、Grok 4.6 冷审修复和最终机械门重放已完成，随 `v1.6.8@6b1dc2c5` 发布。ClawHub 同步的是无 Hook 写作规则。
- `WR-006` 自然审稿：OpenCode Go 真实审稿和自然审稿、复合成稿、材料引语三类路由反控已完成，随 `v1.6.9@5047c224` 发布。
- `OV-001` 发布后边界补丁：软性“约、左右、上下”、长引语、无标点编号正文、否定责任短语和同动词多拟办对象修复已随 `v1.6.9@5047c224` 发布。
- SkillHub 已加入 `office-efficiency`、`content-creation` 轻量检索信号；不声称平台写入双分类。
- GitHub 当前包统一 MIT；普通兼容包不含 Hook，OpenClaw GitHub 兼容包随仓库维护。
- v1.6.6 GitHub 与 SkillHub.cn 发布回执见 [`release-1.6.6.md`](../tests/evidence/release-1.6.6.md)；ClawHub、Red SkillHub 及其他平台未在该轮上传。SkillHub 公开 latest 与签名已传播，Keen、Sanbu 安全报告均为 benign。
- v1.6.7 GitHub、SkillHub.cn 与后续 ClawHub 无 Hook 包同步回执见 [`release-1.6.7.md`](../tests/evidence/release-1.6.7.md)。ClawHub 公开 latest、33文件清单与全新安装逐文件复核均已闭环，Hook为0；Red SkillHub 及其他平台未上传。SkillHub tags.latest 已更新，公开 latest 与签名仍在异步传播。

## IN_PROGRESS

- `WR-007` 语义减载与自然表达：R1 后以 R2—R4 继续完成20次真实写稿；最终两份 reference 已合入 `main`。组合后24/24次真实写稿技术有效，SOL/Grok/Qwen 均未发现候选独有硬失败。
- `WR-008` 标题与正文边界：真实生成、同稿修复和自然路由均已完成；规则已合入主入口现有标题格式条目，不增加格式脚本。
- `AH-001` 共享硬锚：24次先行实验和12份原型/回放后已接入 under/over；三方 DIFF 冷审确认的5个缺口已以9次真实修订复核，直接合同和三宿主静态组装通过。其他改稿能力后续按实际需要迁移。
- WorkBuddy/CodeBuddy 当前在线生命周期：WorkBuddy 5.3.13、CodeBuddy CLI 2.115.0 已完成当前 companion 的 UserPromptSubmit、PostToolUse、Stop、事务、E1 选择及终稿 hash 闭环；`--print` 会在阻断后退出，完整续跑采用交互生命周期。
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

## TODO：已登记但不在本轮展开

1. `OT-001/002` 提纲核对与修正继续延后到下一轮，不在本轮创建实验 worktree。届时先设计正文前的提纲冻结/确认检查点，再测试提纲修正和终稿一致性；没有冻结提纲时不在 Stop 猜测。
2. ClawHub 分类与话题整理按用户最后指令留到下一版本，不修改已经发布的1.6.9。

## 不再重复

- 不把生命周期触发成功称为写稿质量成功。
- 不为没有合格 D1 的候选运行空 SOL 盲审。
- 不用独立采样的 Hook on/off 总胜负替代同一 D0/D1 的功能增量。
- 不在每个小修复后跑全量测试；全量门只在合并或发布前运行一次。
- 不因 CodeBuddy 暂时无法登录而反复创建隔离配置、复制认证文件或重跑零 token 会话。
