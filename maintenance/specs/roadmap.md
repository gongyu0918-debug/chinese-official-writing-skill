# 状态与下一步

状态只表示当前仓库事实：`DONE` 已完成或已合并，`IN_PROGRESS` 有当前候选，`HOLD` 已实现但未达到产品准入，`TODO` 尚未实现。

## DONE

- `WR-001/002/005`：v1.6.4 普通语义规则、保护性外扩精确删除、新闻边界和短稿收束已合并本地 `main@b0b5012e`；六份真实写稿和 SOL 校准见 [`v164-real-writing-final/result.md`](../tests/evidence/v164-real-writing-final/result.md)。
- `HK-001/003/004/006`：普通路径独立闭环、capability-first 单协调器、三宿主静态 adapter 和用户知情边界已建立；永久移除采用 README 语义说明与二次确认，未确认0改动、确认后隔离副本精确删除并完成真实写稿。
- SkillHub 已加入 `office-efficiency`、`content-creation` 轻量检索信号；不声称平台写入双分类。
- GitHub 当前包统一 MIT；普通兼容包不含 Hook，OpenClaw GitHub 兼容包随仓库维护。

## IN_PROGRESS

- `WR-003`：跨文种责任承载已有官方研究，尚未形成小型真实写稿候选。
- `WR-004`：公文常用语和文种尾语已有中央参考候选；责任书、公开信、倡议书、建议信、编者按、讲解稿、宣传手册/材料等仍需轻量路由。
- `WR-006`：审稿模式已有自然请求实跑，复合任务和材料引语反控尚待独立小原子。
- GitHub README 制度示例替换：旧示例仍含保护性尾句，需用当前版本重新成稿、冻结和替换，不改写历史 evidence。

## HOLD

- `UL-001—004` 篇幅不足 Hook：候选产品为 `b81222fa`，证据整理提交为 `ee991cdf`。Codex 与 Claude Code 当前指纹已完成真实触发、D1 检查和 D0 hash 回退；CodeBuddy 旧在线样本与当前宿主胶水逐字相同，可作迁移证据。仍然 HOLD 的主因不是 CodeBuddy 未登录，而是当前没有一份 D1 被选择为可直接使用终稿，且 Codex D0 含过程旁白。
- 旧 `length-band-hook-v162`、`under-length-hook-v162-v2`、`v163-protective-expansion-gate` 继续保持历史 HOLD，不复活旧验收结论。

## TODO：下一轮最短路径

1. 先不改正式 Hook 胶水。把 `under_length` 修订指令作为强制二次提示直接作用于 3—5 份真实短 D0，测试能否产生至少一份安全、自然、达标的 D1。
2. 只围绕真实失败修改篇幅 reference/prompt：首稿过程旁白、为凑字新增流程、重复句式、数字归属和状态升级。
3. 有合格 D1 后交独立 SOL max 审同源增量；没有合格 D1 则继续修语义，不跑全量回归和三宿主矩阵。
4. 语义门通过后，把已经验证的 prompt/规则接回当前单一 coordinator；只补直接相关 unit、两宿主在线 smoke 和 CodeBuddy 迁移核验。
5. 只有宿主 adapter 或 coordinator 变化时，待用户可登录后补 CodeBuddy 在线复测；若只改宿主无关 runtime，不以重复登录作为阻塞条件。
6. 最后一次性完成镜像、组装、最小回退、版本和发行检查。

## 不再重复

- 不把生命周期触发成功称为写稿质量成功。
- 不为没有合格 D1 的候选运行空 SOL 盲审。
- 不用独立采样的 Hook on/off 总胜负替代同一 D0/D1 的功能增量。
- 不在每个小修复后跑全量测试；全量门只在合并或发布前运行一次。
- 不因 CodeBuddy 暂时无法登录而反复创建隔离配置、复制认证文件或重跑零 token 会话。
