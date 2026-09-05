# 剩余 Hook 与写稿规则修复 R1

状态：`CANDIDATE / NOT_MERGED / NOT_RELEASED`。基线为 `37f22146f64cf2dfcaea7a8a5afba40750215803`，独立分支 `codex/remaining-hook-quality-r1`。本轮保留取消后的清理、DSH 当前回合取消、OpenCode 失败分类和新闻完整日期规则；多轮修改规则候选未通过真实链，已恢复原版。不能据此声称长程写稿稳定性已提升。

reference 原型提交为 `89624a579343e6e659dd60587f9e3f3de113d4ce`，撤回失败 workflow 并同步新闻页的提交为 `511c4856`；最终 Hook 产品提交为 `b2cb9381c589aabdc96f56cc118eb5941e19e6c0`。没有改动 main、发布 tag、平台版本或付费增量。旧合并与发布事实仍见[上一轮合并记录](../hook-four-fixes-merge-r1/result.md)。

## 保留的改动

| 项目 | 实际结果 | 证据与边界 |
| --- | --- | --- |
| HK-008 取消清理 | 同一历史真实 D0，bootstrap 暂停后取消、实际持锁后取消两种时序，含原文文件分别由 4/5 份降为 0；取消后不重新 emit。正常精确回显的 selected 哈希不变，delivery_verified=true。 | [清理报告](raw/cleanup/result.md)、[R2 汇总](raw/cleanup/summary-r2.json)。实际 Python core/detect 子进程，驱动注入时序，0 新模型调用；不代表自然发生率。 |
| HK-005b 宿主失败 | DSH 将 core 的 continue:false 映射为取消当前回合，真实已安装 SDK 从 completed 变为 aborted，保留排队用户请求；OpenCode 不再把失败记为 allow，停止插件续写并请求错误提示。 | [宿主报告](raw/hosts/result.md)、[源码与官方协议查阅](raw/hosts/research.md)。DSH 使用真实 AgentLoop 与无网络 MockAdapter，未重跑原生模型/CLI；OpenCode 仅协议验证，未观察原生 UI。 |
| AH-002b 新闻日期 | 在已有事实规则后增加：事实给出完整年月日时保留年份，用户明确只写月日时遵从，格式示例不作为事实日期。 | 最终规则两路完整日期稿通过；两路“只写月日”和“事实缺年但示例有年”共 4 次控制通过。canonical 规范化 UTF-8/LF 增加 129 bytes，五套镜像一致。不是减载收益，也不是通用来源识别器。 |

清理先做真实 D0 生命周期原型，再补必要状态与反控。独立审查发现 R1 两项候选回退：刷新已脱敏失败回执遇写入故障会删掉旧回执；取消未 bootstrap 的 `t` 会误删活动 `t-inputs` 事务。二者均先保留反例再修正，R2 分别保持旧回执字节与相邻活动事务文件哈希。最终 core SHA-256 为 `7763991df28fddcf7483737a44658948e7bb520602fa109d1fa36da9978fee38`，DSH 为 `35213b67dfe030987c25058d82104976f01a64e23f8d52786d61cd46c61eafc9`，OpenCode 为 `24a30be2ba5cfd1417303f4b61b91215e8045eb6df01b9a94ed238ab18bc72c8`。

## 真实写稿与未准入候选

使用 `alibaba-token-plan-2/deepseek-v4-flash-0731` 与 `minimax-cn/MiniMax-M3`，均 max。共 **50 次真实写稿/修改执行**：22 次隔离的初稿/同稿修订与控制，加上 4 条独立真实会话的 28 个相关版本。不得把这些相关版本当作 50 篇独立稿件或计算通用正确率。fixture、完整最终回复、模型回执和匿名审查均已冻结。

- R1：2 模型 × 2 臂 × 新闻/删除/插段，共 12 次。Alibaba 基线漏掉事实年份，候选保留；MiniMax 两臂均完整。workflow 候选在 MiniMax 删除任务中残留“专题交流”，基线已删净，故拒绝。[匿名审查](raw/writing/writing-prototype-r1/blind-review.json)
- R2：缩小多轮修改规则，新闻页消融掉泛化推断与动作核验新增句，仅保留日期句；另做 6 次候选调用，与固定 R1 基线比较，目标原子均通过，未观察候选独有硬回退。[匿名审查](raw/writing/writing-prototype-r2/blind-review.json)
- 新闻控制：另做 4 次。只写月日遵从用户，事实缺年时不从示例借年。[fixture](raw/writing/news-controls-r1/fixture.json)、[22 次调用与原始流哈希](raw/writing/call-manifest.json)
- 七版链：在另一清洁 worktree 中运行[既有驱动的薄封装](run_chain.py)，两臂固定为基线和 `89624a57`。第 2—7 轮实际 `exec resume` 同一个 thread，没有重拼历史，也未启用 Hook。[fixture](raw/chain/fixture.json)、[session/调用摘要](raw/chain/summary.json)、[匿名审查](raw/chain/blind-review.json)、[解盲映射](raw/chain/blind-mapping.json)

七版链 **28/28 技术完成，9 组已确认硬问题影响 14 个相关版本**。两条 Alibaba 链未观察到登记硬问题，但它们都没有自然读取 workflow，因此不能证明该页带来改善。MiniMax 基线有材料外技术核验范围、未提供的交流主办方、过程前缀，以及删除交流时误删统筹职责；候选前两版只回复“已完成”而没有正文，后续五版持续附加修改说明/自检，另有材料外动作。R1 的工具计数命令失败和虚假完成回复仍计为交付失败，没有当作无效样本移除。

R7 四条**正文**均只完成指定调序；含附注的实际最终回复仅 3/4 精确保持其他内容，末稿只有 2/4 未观察到登记硬问题。MiniMax 候选 R6/R7 正文各 607 去空白字符，附说明后的实际回复分别 686/678；这是完整回复超限及正文交付边界失败，不能误称正文自身超限。R6 未冻结段落边界，合段不计硬错；没有确认旧统计回流，不将“260”中的“60”当旧数据。

据此，workflow 的 R1/R2 均未准入，最终文件与基线 Git blob 完全相同；SKILL.md 不变。本轮保留新闻日期原子，没有批量删规则或扩大渐进路由。新闻原子使用注入的精确路由上下文；自然文件读取仅由七版 CLI trace 单独记录，不能混称自然减载。

## 验证与证据范围

实际相关回归命令：

```text
python -X utf8 -B -m unittest maintenance.tests.test_gate_stop_hook maintenance.tests.test_source_bound_dates maintenance.tests.test_deepseek_harness_gate_adapter maintenance.tests.test_opencode_gate_adapter maintenance.tests.test_skill_boundary
python -X utf8 -B -m unittest maintenance.tests.test_skill_boundary.SkillBoundaryTests.test_packaged_resource_mirrors_match_canonical_bytes
python C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py <canonical 或 agent-skills/qwen-code/qwenwork/hermes 的 Skill 目录>
```

首条执行 171 项、37.232 秒，exit 1：同一个镜像方法的 4 个子测试仅因还原 workflow 时 LF/CRLF 字节不一致失败。按基线镜像原字节恢复后，第二条 1 项在 0.040 秒通过，规范化文本仍等于基线；没有把首轮失败重写成全绿。[原始回归回执](raw/verification/related-tests.json)、[镜像复测](raw/verification/mirror-recheck.json)。五套 quick validate 均通过，[完整命令与结果](raw/verification/quick-validate.json)。OpenClaw 静态包由镜像/边界检查覆盖，未伪装为通用 quick validator 支持。

独立 HK-008 R2 定向反控 15 项通过，R1 旧 63 项日志保留；宿主 16 项直接测试与后续 3 项定向验证通过。这些与相关回归有重叠，不累计成独立测试样本。原型失败、驱动技术无效、CodeBuddy 初次参数顺序错误、独立审查发现的回退均在原始记录中保留。

[原始文件清单](artifact-manifest.json)固定归档字节，`raw/.gitattributes` 禁止 Git 换行转换。22 份 prompt 可由冻结 fixture 精确重建并已逐份比对，原始 stream 留在 output 并登记哈希；七版的全部最终回复、题面、调用 argv、session 元数据和盲审入库，原始 CLI trace 留在独立测试 worktree 并登记[哈希](raw/chain/file-manifest.json)。未打包用户 profile、会话数据库、SDK 依赖、第三方源码缓存或凭证。raw 中的驱动和报告保留执行时目录，复跑须恢复指定 source-root 并另选空输出目录。

文档与需求状态实际执行 `python -X utf8 -B -m unittest maintenance.tests.test_repository_reachability maintenance.tests.test_status_ledger_consistency`，23 项在 0.900 秒通过，[回执](raw/verification/docs-tests.json)。独立审查又对当前完整 tree 窄复放两项原反例，两条命令 exit 0，[复核记录](raw/final-core-review.json)确认失败回执保持、相邻活动事务 10 个文件哈希不变且最后交付验证成功。主代理解盲与新闻控制核对见[裁定](raw/root-adjudication.json)，14 个实际产品改动文件与清洁 main 的核对见[源状态](raw/verification/final-source-state.json)。归档文件/链接/JSON与 Git 索引字节的最后检查见[验收回执](archive-validation.json)。

未运行本轮全量合并/发布门；旧 788 项仅属于上一轮 main，不作为本轮通过证据。

## 未完成与剩余风险

CodeBuddy/Kimi 独立硬停仍为 `UNSUPPORTED`；OpenCode 只能停止插件续写，DSH 当前结论只到 SDK。任何 Stop 都不能撤回已显示的文字；旧在线正常证据不迁移成新失败路径的原生证明。实际宿主是否发出 HostAbort、短预算中断及永久离线残留继续按各宿主边界处理。

持续 I/O 故障、取消标记本身写不下、拥有者不退出且无后续事件时不能保证清理；旧版已失去归属的孤儿不按名称扫描。两个不同 turn 都 bootstrap 时既有的后缀目录碰撞仍未解决，本轮只关闭“未启动 turn 误删相邻事务”的新增触发面。

材料外技术动作、改稿误删非目标事实和只交付正文仍是 WR-020c 的产品质量缺口。后续继续先做同一真实底稿的最小规则/路由原型，再跑实际多版链；本轮不补大状态机或更重裁判来掩盖写稿失败，不声称任意长度、compaction 或百稿稳定性已验证。
