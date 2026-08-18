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
