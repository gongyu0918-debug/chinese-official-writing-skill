# Codex main 多能力真实兼容验证

本轮只验证已经合入本地 `main` 的能力能否在同一套 Codex companion 中独立运行，不把样本结果作为收紧规则、扩大检测词表或调整门禁阈值的依据。测试中出现的语义分歧只记录；只有崩溃、能力串线、循环、终稿哈希错配等确定性工程故障才进入修复范围。

## 固定对象与执行

- 本地 `main`：`f2012def5ecf00ed2341fbbad195cedf85a440db`。
- Codex：`codex-cli 0.144.6`。
- 路线：`opencode-go/deepseek-v4-flash`、`ollama-cloud/deepseek-v4-flash:0731`、`alibaba-token-plan-2/deepseek-v4-flash-0731`，均为 max。
- 三条 provider lane 并行、lane 内串行；8 次真实调用，1200 秒上限，0 retry，最大并发 3。
- R1 在模型调用前因隔离 `CODEX_HOME` 未预建而作废，记 `ENV_ORCHESTRATION_INVALID`，不计质量结果。
- R2 完成 8/8 技术终稿，但测试指令把“首个成稿”等字样带入部分 D0，只作合并前兼容旁证，不用于调整产品。
- R3 从已合入的本地 `main` 重新运行，8/8 均返回非空终稿、无超时、无重试、无循环和哈希错配。

## R3 结果

| 场景 | 路线 | 观察结果 |
| --- | --- | --- |
| 普通 Skill、无 Hook | OpenCode Go | 普通写稿完成；无 capability 事务或插件数据。 |
| 默认交付复核、清洁 D0 | Ollama Cloud | 原稿逐字交付，普通事务闭环。 |
| 交付洁净度 | OpenCode Go | 选择 D1，精确清除过程包装；`delivery_verified=true`。 |
| 保护性外扩 | Ollama Cloud | 观察器判 `clear`，选择 E0 并逐字回显；这是本样本的语义选择，不据此改门禁。 |
| 完全重复句 | Ollama Cloud | 选择 E1，删除一处完全重复句，终稿哈希与选中稿一致。 |
| 高相似零增量复述 | Alibaba Token Plan 2 | 选择 E1，保留信息较完整句，删除同义复述，终稿哈希与选中稿一致。 |
| 篇幅不足 | Alibaba Token Plan 2 | 模型实际读取已安装 Skill 与 268 字 D0，但事件记录为 `skill_seen=false`，未建立篇幅事务，最终逐字回显 D0。既有独立 Codex/Claude 在线 D1 证据不受此样本推翻；本项只记宿主读取识别观察。 |
| 用户当前任务关闭 Hook | OpenCode Go | 记录 `bypass=user_requested`，未建立 capability 事务，正常完成正文。 |

R3 中交付洁净度、两类重复清理各自只产生本能力的选择凭证；普通路径、默认复核、保护性外扩、篇幅不足和用户旁路均未出现其他 capability 串线。测试后没有修改 `main` 门禁。

## 证据绑定

- R3 manifest SHA-256：`3C3D23EE68529320DBAEEDF332C69CBE1B2A2DF68F50309FCE2BA30B3A3BA279`。
- R3 detached launcher receipt SHA-256：`2A53CDC5DF5C6A67298C8FF62FE928AA6B7276524B8EB593C80D781BC0106E86`；launcher stderr 为空。
- R2 manifest SHA-256：`A570EEBB3A5A748ADB706FD216DE0FEDBB76BEE0C509F6AEEA8FDA944BBD5DE4`。
- 篇幅不足 R3 插件记录 SHA-256：`0BB267E3761BF6F8397C10C69C2DC5D50103942AE4AC420709F90E8F641B0A5C`；stdout JSONL SHA-256：`F227B963629790CA022435CFAB2933409DC5EDF01B9E3FF9003ABAD11682799E`。
- 保护性外扩、完全重复、高相似复述的插件记录 SHA-256 依次为 `E5935F55CE7D47026450E65D9A644FEC8AAFBFF7936D1A0298343550F5C9D436`、`E95C6A30362BFFFFA93B49F9BAB1B7AAD4E1F47F42216D5D5430AE6064DBCB5A`、`428D1E75C550A7FE6CA031AA0D80DAC25B727BDF63F8D726B8E53074BEB95CAC`。

原始运行目录位于本地 ignored `output/research-worktrees/repetition-cleanup-capability/output/codex-multi-capability-real-r1/`，未提交缓存、登录态或运行目录。

## 结论与剩余项

重复句与高相似句 capability 已合入本地 `main`，并在 Codex 中完成两条真实 E1 生命周期；交付洁净度也完成 Codex E1。多能力静态互斥、运行隔离和终稿哈希闭环未见确定性回退。

仍需保留两项观察：CodeBuddy 当前能力尚未在线重跑；本次合并后篇幅样本未识别 Skill read，后续只做一条最小复现来区分宿主事件形态与偶发执行差异，不以此收紧篇幅语义门。保护性外扩本样本选择 E0 同样不触发规则调整。
