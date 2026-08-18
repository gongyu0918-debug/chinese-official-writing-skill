# 提纲 Hook 真实优先探索结果

日期：2026-08-18  
固定基线：`6fd4a5f2657ffc13eb0f6c7f7cda776c1884dae0`

## 目标

验证提纲能力是否需要独立于交付复核的前置生命周期，并以真实写稿结果决定是否进入工程化。探索阶段不改 canonical 产品，不以确定性工程测试替代成稿质量。

## 官方生命周期依据

- Claude Code 官方 Hook 文档说明 `UserPromptSubmit` 在主模型处理请求前触发，`PostToolUse` 在工具完成后触发，`SubagentStart` / `SubagentStop` 分别在子代理开始和完成时触发，`Stop` 在回复结束时触发：<https://code.claude.com/docs/en/hooks>。
- Claude Code 官方子代理文档说明插件可在 `agents/` 中分发专用子代理，也可用 `--agents` 进行当前会话原型验证：<https://code.claude.com/docs/en/sub-agents>。

## 被否定的路线

`plan` 权限模式配合 `ExitPlanMode` 的真实调用只输出提纲和“请确认”提示，没有调用 `ExitPlanMode`，也没有形成正文。该路线不适合一次性写稿，原始流位于忽略目录 `output/outline-hook-real-first/lifecycle-probe-r1/`，终稿 SHA-256 为 `c9ff99b53dec920abce9433b02d1709443e5e2a614922f09327f3c48bab84336`。

## 真实写稿迭代

同一校园网络安全工作方案先比较普通 Skill 与前置提纲子代理。普通稿重复设置“主要任务及时间安排”和“责任分工”，并增加协作、报告等材料外要求。早期提纲代理也出现固定四章、过程回显和材料外动作；随后仅收紧事实放置任务，不进入产品工程。

可用的事实放置合同是：

1. 子代理只拆分主体、动作、对象、数字、日期和状态；
2. 每项事实只进入一个章节，责任、动作和时限不拆成重复章节；
3. 用户给定提纲原样保留；材料稀疏时不补固定骨架；
4. 子代理不提供红线示例、字数建议、通用结构或正文；
5. 主模型成稿后按同一提纲做一次删减式符合性修订，不新增替代句。

## 完整插件生命周期结果

隔离插件未使用 `--agents` 或额外系统提示；插件自身提供 `outline-planner`、`UserPromptSubmit` 接引、`PostToolUse:Agent` 冻结和一次 `Stop` 符合性修订。三项均使用 max、首个完整结果、零重试。

| 任务 | 模型 | 实际事件 | 结果 | 终稿 SHA-256 |
| --- | --- | --- | --- | --- |
| 校园网络安全事件处置工作方案 | `opencode-go/deepseek-v4-flash` | 1 次 Agent；`UserPromptSubmit`、`PostToolUse:Agent`、两次 `Stop` 均成功 | 6 项事实各出现一次，无纲外目的、要求、流程或后续动作 | `b69c994c09b470598ee12dcab57d9c1c44d69a99e29a06d76696b31354e3b8f0` |
| 暑期延时开放情况报告，用户固定三段提纲 | `ollama-cloud/deepseek-v4-flash:0731` | 同上 | 三个标题及顺序原样保留；数据、反馈状态和后续动作不重复 | `8ec6bdcf680c3a5c23637780674fee1efe34d6a2bfceeddf1677ff1f13c980d5` |
| 秋季开学校园安全检查通知 | `alibaba-token-plan-2/deepseek-v4-flash-0731` | 同上 | 责任、动作、时限合并表达，无材料外检查、整改、联系人或报送对象 | `88cabc9949f088ce18a16a1874a5c4bb05bdc8e4b0ea19fad44628998972fdd1` |

Alibaba 首轮把用户用于指代文名的书名号带入正式标题；同模型 Skill-only 对照没有该问题，故认定为候选回退。接引补充“`起草《文名》` 的书名号默认不属于正式标题”后，同题复跑通过。失败首轮和通过复跑分别保留于 `output/outline-hook-real-first/claude-plugin-responsibility-r1-alibaba/`、`claude-plugin-responsibility-r2-alibaba/`。

## 结论与边界

- 真实稿支持“前置事实放置子代理 + 成稿后一次提纲符合性删减”，不支持只靠 `plan/ExitPlanMode`，也不支持只在入口增加提示。
- 当前实证只覆盖 Claude Code 2.1.195 的插件子代理和 Hook 生命周期。Codex、WorkBuddy / CodeBuddy 尚无同一候选的在线子代理生命周期证明，不得宣称已兼容。
- 首次 `Stop` 主动阻断后，Claude Code 在第三方 Anthropic 网关链仍会显示既有 `stop-hook-error` 通知；本轮每次 Hook 回执均为 `exit_code=0`、`outcome=success`，第二次 `Stop` 放行且进程返回 0。该 UI 兼容提示继续如实保留。
- 下一步只组装 Claude Code 静态 companion；普通 Skill 不启用、不运行、不写本地事务文件。是否与其他 `Stop` 门禁组合，须另做协调设计和真实生命周期验证，本原子不并行加载两套 `Stop` 修改器。

## 工程候选复跑

把原型收敛为 capability-first 的 Claude Code companion 后，第一次复跑秋季开学通知仍产生了材料外的“校内各单位”、向“学校”报送、`××学校` 和当前日期。该失败稿 SHA-256 为 `d08f2c58a01ee3ea66a37da0874ad976db6f27e1997681f1f1c7e9280d8dfcee`。因此，提纲合同进一步冻结标题、主送、署名和成文日期四类文档要素；材料未给时明确标为“无”，Stop 只删除材料外文档壳，不补替代项。

同一已组装候选随后复跑三题，均使用 max、零重试；每题恰调用一次 `chinese-official-writing-outline:outline-planner`。这三题为避免留下会话记录而使用 `--no-session-persistence`，实际触发的 `UserPromptSubmit`、`PostToolUse:Agent`、`Stop` 回执均为 `exit_code=0`、`outcome=success`；由于没有可读会话记录，`Stop` 按故障回退边界直接放行，因此三题只证明前置提纲和冻结上下文的写稿效果，不用于证明后置修订生命周期。

| 任务 | 模型 | 结果 | 终稿 SHA-256 |
| --- | --- | --- | --- |
| 校园网络安全事件处置工作方案 | `opencode-go/deepseek-v4-flash` | 事件、处置、复核三组事实各出现一次；未补纲外工作要求、责任结论或后续事项 | `6594a24a3e818ccbb1a6c81012c63117303fd1c284136fd7ccbd2b30e9a63ae9` |
| 暑期延时开放情况报告，用户固定三段提纲 | `ollama-cloud/deepseek-v4-flash:0731` | 三个标题和顺序原样保留；数字、反馈状态和后续安排不重复 | `e563b349cacb73ef0ba6a8c8ba082e548fd830f90a1a737b8651966e42f06a00` |
| 秋季开学校园安全检查通知 | `alibaba-token-plan-2/deepseek-v4-flash-0731` | 不再补主送、署名、日期或报送对象；六项材料事实各出现一次 | `efcfd2743e818903be9b747b21c66c074cd5243efc97f044435995bf0afa0267` |

Alibaba 复跑的 `CLAUDE_CONFIG_DIR` 与临时目录保持隔离，初始化记录只加载目标插件；启动命令因 PowerShell 的只读 `$HOME` 变量名冲突，没有把进程 HOME 改到临时目录。该环境差异如实保留，不用它证明完全隔离；OpenCode Go 与 Ollama 两题使用了独立 HOME、配置和临时目录。

另用正常的临时会话复跑同一 Alibaba 通知题，HOME、配置和临时目录均隔离。实际事件为 `UserPromptSubmit → PostToolUse:Agent → Stop(block) → Stop(allow)`，四次 Hook 均为 `exit_code=0`、`outcome=success`，进程返回 0，零重试。终稿未补主送、署名、日期或报送对象，SHA-256 为 `406bf03ad4c72ae760d120e9ab93a955b8dda834a5efe0a3e00927a766ddb746`。这轮证明正常 Claude 会话可以完成一次有界提纲修订；会话记录不可用时安全保留主 Agent 原稿。

工程候选只声明 Claude Code 支持。Codex 和 WorkBuddy / CodeBuddy 没有相同子代理生命周期实证，组装器会拒绝为这两个宿主生成提纲 companion。

## 开关、改稿与长稿实测

随后用当前工程候选补做 5 次真实调用，仍为 max、零重试、独立 HOME / 配置 / 临时目录。评分只看提纲遵从、事实唯一落位、事实增删和生命周期，不以整体文采胜负收紧门禁。

1. **显式关闭**：OpenCode Go 在 companion 已加载时收到“本次关闭 Hook”。实际 `Agent=0`，`UserPromptSubmit` 与 `Stop` 均无门禁输出、无阻断，证明当前任务旁路生效。普通 Skill 终稿仍出现“已按某卡成稿”和 Markdown 分隔线，SHA-256 为 `8f3592a61490fc36056b5173ebaee1876a0551fd4cdbb41bac643f5f331e9287`；这是关闭后的普通路径交付洁净度波动，不归因于提纲 Hook，也不在本原子顺带修复。
2. **多章节事实归位**：Ollama 同题无 Hook / 有 Hook 终稿分别为 `ff30a85fd609abdefa3ce6a01818be18e311efd6ea41a55e43870560b8fb04f3`、`15b3309fcf13c989cc84d09ab41d3f176bf23e86b179868b79c9b9f6a1336877`。两稿均事实完整；无 Hook 稿两次写“9月7日至8日复核”，有 Hook 稿只保留一次并把9项问题落在问题处置章，没有新增内容。
3. **实质改稿准确性**：Alibaba 同题有 Hook / 无 Hook 终稿分别为 `3ed64c17bf225977228f19aac5c7b1480813d9ceeafcdf7467f5954511654288`、`28ae499f02178d9a7bec013964db138a702a490560db88e1be09565e9b4a6cf0`。两稿均保留全部数字、日期、主体和状态；无 Hook 稿新增“各业务环节衔接顺畅”和“配件到货后及时完成更换”，有 Hook 稿没有这两处材料外结论与动作。
4. **长稿逻辑与 Stop 副作用**：OpenCode Go 的五章报告无 Hook 为1020个非空白字符，SHA-256 为 `dff4640c7656bec34379555d592b3ca3034862ff16579d743209bc7c693bb6bd`；首版有 Hook 为843个字符，SHA-256 为 `14aab6029c45c6d06f2f985377a1f65b9764ea918799c162988e395cd6acf627`。两稿均事实与结构正确，但首版 Stop 把正常分组衔接一并压缩。修正 Stop 职责后只重跑有 Hook 臂，初稿与 Stop 后终稿逐字相同，均为821个字符，SHA-256 均为 `9a038ca18d011a98064f2b28af717ee1f3b7a314ea72ad97340d65509a9b4c0e`；四次 Hook 回执成功，先 block 后 allow。由此证明后置核对不再压缩合规正文，但首次写稿仍低于用户的1000字下限。

当前证据支持：显式开关有效；固定提纲、事实唯一落位和实质改稿有可见收益；正常会话中的一次 Stop 核对可运行且修正后不再改写合规稿。证据不支持“普遍提升长稿”或“保证达到篇幅下限”；长稿两臂都逻辑一致，候选更短属于首次写稿差异，篇幅补足仍是另一项独立能力。
