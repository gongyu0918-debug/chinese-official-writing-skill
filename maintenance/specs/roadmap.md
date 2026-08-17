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
- SkillHub 已加入 `office-efficiency`、`content-creation` 轻量检索信号；不声称平台写入双分类。
- GitHub 当前包统一 MIT；普通兼容包不含 Hook，OpenClaw GitHub 兼容包随仓库维护。
- v1.6.6 GitHub 与 SkillHub.cn 发布回执见 [`release-1.6.6.md`](../tests/evidence/release-1.6.6.md)；ClawHub、Red SkillHub 及其他平台未在该轮上传。SkillHub 公开 latest 与签名已传播，Keen、Sanbu 安全报告均为 benign。
- v1.6.7 GitHub、SkillHub.cn 与后续 ClawHub 无 Hook 包同步回执见 [`release-1.6.7.md`](../tests/evidence/release-1.6.7.md)。ClawHub 公开 latest、33文件清单与全新安装逐文件复核均已闭环，Hook为0；Red SkillHub 及其他平台未上传。SkillHub tags.latest 已更新，公开 latest 与签名仍在异步传播。

## IN_PROGRESS

- `WR-006`：审稿模式已有自然请求实跑，复合任务和材料引语反控尚待独立小原子。
- GitHub README 制度示例替换：旧示例仍含保护性尾句，需用当前版本重新成稿、冻结和替换，不改写历史 evidence。

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

1. `AH-001` 引用与硬锚：把值、归属和必要出现保护抽成修稿能力的共享不变量，不另起并行 Hook，也不恢复词频完全相等的旧机械门。
2. `OV-001` 超长收束：以已验证的重复清理作为压缩前置，先直接测试一次受控 D0→D1；产生可用压缩稿后才接 coordinator。
3. `OT-001/002` 提纲核对与修正：最后处理。先设计正文前的提纲冻结/确认检查点，再测试提纲修正和终稿一致性；没有冻结提纲时不在 Stop 猜测。

## 不再重复

- 不把生命周期触发成功称为写稿质量成功。
- 不为没有合格 D1 的候选运行空 SOL 盲审。
- 不用独立采样的 Hook on/off 总胜负替代同一 D0/D1 的功能增量。
- 不在每个小修复后跑全量测试；全量门只在合并或发布前运行一次。
- 不因 CodeBuddy 暂时无法登录而反复创建隔离配置、复制认证文件或重跑零 token 会话。
