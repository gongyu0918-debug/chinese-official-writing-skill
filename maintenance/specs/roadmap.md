# 状态与下一步

状态只表示当前仓库事实：`DONE` 已完成或已合并，`IN_PROGRESS` 有当前候选，`HOLD` 已实现但未达到产品准入，`TODO` 尚未实现。

## DONE

- `WR-001/002`：v1.6.4 事实与状态规则、保护性外扩精确删除和新闻边界已发布于 `v1.6.4@a737791c`；六份真实写稿和 SOL 校准见 [`v164-real-writing-final/result.md`](../tests/evidence/v164-real-writing-final/result.md)，发行回执见 [`release-1.6.4.md`](../tests/evidence/release-1.6.4.md)。
- `HK-001/003/004/006`：普通路径独立闭环、capability-first 单协调器、三宿主静态 adapter 和用户知情边界已建立；永久移除采用 README 语义说明与二次确认，未确认0改动、确认后隔离副本精确删除并完成真实写稿。
- `UL-001—004`：篇幅不足 Hook 已按真实写稿优先完成语义修复，并随 `v1.6.5@81061bd7` 发布。Alibaba 直修 268→342，Codex 在线 268→350，Claude Code 在线 268→344；两次独立 SOL max 均判可用 D1 `ACCEPT`。CodeBuddy 当前只保留同构静态迁移证据，不冒充在线成功。结果见 [`v164-under-length-real-first-result-20260814.md`](../tests/evidence/v164-under-length-real-first-result-20260814.md)。
- `CL-001`：交付洁净度已先用三条指定 DeepSeek V4 Flash 路线完成 5/5 同稿真实整理，再接入独立静态 capability，并随 v1.6.5 发布。SOL max 五组全 PASS；Claude Code 与 Codex 在线生命周期均选择 D1 并闭合哈希。结果见 [`delivery-cleanliness-real-first/result.md`](../tests/evidence/delivery-cleanliness-real-first/result.md)。
- `RP-001`：重复句与高相似句已先完成三 provider 的 5 组真实删除和 SOL max 功能终审，再接入纯删除 capability，并随 v1.6.5 发布。长稿 1 个自然度 WARN 保留为后续样本，不影响已验证的目标功能。
- SkillHub 已加入 `office-efficiency`、`content-creation` 轻量检索信号；不声称平台写入双分类。
- GitHub 当前包统一 MIT；普通兼容包不含 Hook，OpenClaw GitHub 兼容包随仓库维护。
- v1.6.5 GitHub 与 SkillHub.cn 发布回执见 [`release-1.6.5.md`](../tests/evidence/release-1.6.5.md)；ClawHub、Red SkillHub 及其他平台未在该轮上传。

## IN_PROGRESS

- `WR-003`：跨文种责任承载已有官方研究，尚未形成小型真实写稿候选。
- `WR-004`：公文常用语和文种尾语已有研究分支中央参考候选，但尚未进入 v1.6.5 产品；责任书、公开信、倡议书、建议信、编者按、讲解稿、宣传手册/材料等仍需先做轻量真实写稿。
- `WR-005`：短稿同义复述、连续自证和过程包装已有普通规则与可选 Hook 兜底；仍需先验证普通无 Hook 写稿，再决定是否补路由或 lint。
- `WR-006`：审稿模式已有自然请求实跑，复合任务和材料引语反控尚待独立小原子。
- GitHub README 制度示例替换：旧示例仍含保护性尾句，需用当前版本重新成稿、冻结和替换，不改写历史 evidence。

### 本轮收束顺序

1. `WR-004` 事务文体路由：先用最简 reference 或强制路由覆盖代表性文体，立即做少量真实写稿；通过后才整理中央参考、文种叶和路由。
2. `WR-003` 责任主体与合理推断：先验证新闻、会议、请示、总结等真实稿中的责任承载、近邻继承和无头结论；通过后才形成跨文种规则。
3. `WR-005` 短稿自然度：先在普通无 Hook 路径验证同义复述、连续自证、过程旁白和正文外包装；通过后才决定是否补 lint、Hook 兜底或其他胶水。
4. 本轮不以工程门代替写稿。只在真实稿证明目标机制有效且没有候选独有硬回退后，补直接相关的路由、镜像、故障回退和最小测试。

## HOLD

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
