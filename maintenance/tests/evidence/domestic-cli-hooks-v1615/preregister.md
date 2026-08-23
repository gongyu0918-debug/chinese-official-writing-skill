# 国产 CLI Skill / Hook 生命周期验证预登记

## 目标

分别验证 Qwen Code、Kimi Code CLI 与 ZCode CLI 的四层事实：

1. CLI 可安装并在无图形界面条件下调用；
2. 可通过本机 OpenCodex loopback 使用第三方模型；
3. 当前中文公文 Skill 可被宿主发现并用于真实写稿；
4. `UserPromptSubmit`、必要的 `PostToolUse` 与 `Stop` Hook 能在真实会话中触发，且 Stop 能看到完整末次正文。

ZCode 使用 `zcode-app-cli` 社区终端壳与其携带的官方 ZCode Agent runtime。结果不得表述为智谱官方独立 CLI 证据。

## 第一轮最小样本

- `QP-0` / `KP-0` / `ZP-0`：只回复固定短语，验证 provider 连通，不加载 Skill，不评价写稿。
- `QH-1` / `KH-1` / `ZH-1`：同一采购申请材料，要求只输出可直接使用正文；显式加载当前 Skill，记录真实 Hook 生命周期。
- 材料：办公室现有 6 台终端中 3 台频繁卡顿；2026 年 8 月 18 日至 22 日试用共享算力后，批量材料处理平均等待时间由约 18 分钟降至约 7 分钟；拟采购 2 台图形工作站，预算合计不超过 9.6 万元；采购尚未批准，配置与供应商待比选；请示事项仅为是否同意启动采购程序。

## 判定

- provider 通过：CLI 退出码为 0，模型与指定路由一致，固定短语正确返回。
- Skill 通过：宿主目录或运行 trace 能证明当前 `chinese-official-writing` 被发现；真实稿落实全部给定事实和未决状态，不新增审批结果、供应商、期限或既得成效。
- Hook 通过：同一真实会话至少出现 `UserPromptSubmit` 与 `Stop`；Stop 的 `last_assistant_message` 非空且哈希对应交付正文。`PostToolUse` 是否出现按宿主实际 Skill 装载机制记录，不强造工具调用。
- 候选适配准入：事件字段可稳定映射到共享 core，阻断返回语义明确，且没有候选独有事实、状态、文种或直接交付硬回退。
- 失败后先拆分认证、Skill、Hook、模型兼容或稿件质量原因；不以增加工程门替代真实修复。

## 边界

- 不使用 GUI、电脑控制或浏览器登录；不写入真实 API key。
- 三套 CLI 均优先使用隔离配置；不修改仓库 `main`、用户全局宿主配置或 OpenCodex provider 登记。
- observer 只保存字段名、类型、长度与文本哈希，不保存 Hook 收到的正文原文。
- 第一轮只跑一个第三方模型；字段与稿件成立后再换 provider 做扩样。
