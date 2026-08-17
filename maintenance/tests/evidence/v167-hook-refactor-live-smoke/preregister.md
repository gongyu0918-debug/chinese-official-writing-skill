# v1.6.7 Hook 重构后真实生命周期 smoke

## 固定对象

- 候选提交：`09f4a4b32f5f997f8f21ef16b020f8c234b7d090`
- 产品树：`61763a444411b09ce3181303f35491633397476e`
- 宿主：Claude Code `2.1.195`
- 静态 companion：`claude-code` + `delivery_review`
- 模型：`alibaba-token-plan-2/deepseek-v4-flash-0731`
- 思考档位：`max`
- 调用次数：1；外层重试：0；超时：1200秒

## 目的

本次只核验行为保持型重构后的真实在线链路，不据此宣称 Hook 提升写稿质量。使用既有《预约接口异常情况说明》题面，要求真实读取组装包内 Skill，生成完整正文，并让已加载 companion 接收 `UserPromptSubmit`、`PostToolUse:Read` 和 `Stop`。

## 技术通过条件

1. 精确模型和 `max` 档位绑定，命令正常退出且只有一个成功终态；
2. Skill 入口读取成功，没有越出组装包 Skill 根的读取；
3. companion 被注册，三类事件均有 started/response 记录；
4. 本地插件数据中存在 adapter turn 和门禁 transaction；
5. 最终正文非空，门禁选择及输出哈希能够闭合；
6. 任一条件失败即记录失败，不重跑、不补样。

## 后续边界

通过后只运行 Hook 核心、review gate、复杂度和组装合同的直接回归，不运行无关全量测试。常用语机械化 R1—R6 的 HOLD 结论不因本 smoke 改变。
