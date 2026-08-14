# 状态与下一步

状态只表示当前仓库事实：`DONE` 已完成或已合并，`IN_PROGRESS` 有当前候选，`HOLD` 已实现但未达到产品准入，`TODO` 尚未实现。

## DONE

- `WR-001/002/005`：v1.6.4 普通语义规则、保护性外扩精确删除、新闻边界和短稿收束已发布于 `v1.6.4@a737791c`；六份真实写稿和 SOL 校准见 [`v164-real-writing-final/result.md`](../tests/evidence/v164-real-writing-final/result.md)，发行回执见 [`release-1.6.4.md`](../tests/evidence/release-1.6.4.md)。
- `HK-001/003/004/006`：普通路径独立闭环、capability-first 单协调器、三宿主静态 adapter 和用户知情边界已建立；永久移除采用 README 语义说明与二次确认，未确认0改动、确认后隔离副本精确删除并完成真实写稿。
- `UL-001—004`：篇幅不足 Hook 已按真实写稿优先完成语义修复并合入本地 `main`。Alibaba 直修 268→342，Codex 在线 268→350，Claude Code 在线 268→344；两次独立 SOL max 均判可用 D1 `ACCEPT`。CodeBuddy 当前只保留同构静态迁移证据，不冒充在线成功。结果见 [`v164-under-length-real-first-result-20260814.md`](../tests/evidence/v164-under-length-real-first-result-20260814.md)。
- `CL-001`：交付洁净度已先用三条指定 DeepSeek V4 Flash 路线完成 5/5 同稿真实整理，再接入独立静态 capability。SOL max 五组全 PASS；Claude Code 在线生命周期精确删除首稿包装并闭合 D1 哈希。结果见 [`delivery-cleanliness-real-first/result.md`](../tests/evidence/delivery-cleanliness-real-first/result.md)。
- SkillHub 已加入 `office-efficiency`、`content-creation` 轻量检索信号；不声称平台写入双分类。
- GitHub 当前包统一 MIT；普通兼容包不含 Hook，OpenClaw GitHub 兼容包随仓库维护。

## IN_PROGRESS

- `WR-003`：跨文种责任承载已有官方研究，尚未形成小型真实写稿候选。
- `WR-004`：公文常用语和文种尾语已有中央参考候选；责任书、公开信、倡议书、建议信、编者按、讲解稿、宣传手册/材料等仍需轻量路由。
- `WR-006`：审稿模式已有自然请求实跑，复合任务和材料引语反控尚待独立小原子。
- GitHub README 制度示例替换：旧示例仍含保护性尾句，需用当前版本重新成稿、冻结和替换，不改写历史 evidence。

## HOLD

- 旧 `length-band-hook-v162`、`under-length-hook-v162-v2`、`v163-protective-expansion-gate` 继续保持历史 HOLD，不复活旧验收结论。

## TODO：下一轮最短路径

1. `RP-001` 重复与高相似句：用短稿和超长稿各取真实样本，先验证 exact-span 删除；高相似句必须经语义判断，不做单阈值自动删除。
2. `AH-001` 引用与硬锚：把值、归属和必要出现保护抽成上述修稿能力的共享不变量，不另起并行 Hook，也不恢复词频完全相等的旧机械门。
3. `OV-001` 超长收束：先把已验证的重复清理作为压缩前置，再直接测试一次受控 D0→D1；产生可用压缩稿后才接 coordinator。
4. `OT-001/002` 提纲核对与修正：最后处理。先设计正文前的提纲冻结/确认检查点，再测试提纲修正和终稿一致性；没有冻结提纲时不在 Stop 猜测。
5. 每项都按“最简 prompt 或强制路由 → 少量真实稿 → SOL max 功能终审 → 必要工程门”推进；一次只接入一个静态 capability。

## 不再重复

- 不把生命周期触发成功称为写稿质量成功。
- 不为没有合格 D1 的候选运行空 SOL 盲审。
- 不用独立采样的 Hook on/off 总胜负替代同一 D0/D1 的功能增量。
- 不在每个小修复后跑全量测试；全量门只在合并或发布前运行一次。
- 不因 CodeBuddy 暂时无法登录而反复创建隔离配置、复制认证文件或重跑零 token 会话。
