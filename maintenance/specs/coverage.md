# 需求覆盖矩阵

`已覆盖` 表示存在对应产品实现和直接证据；`部分` 表示只有规则、工程链或一部分真实执行；`未覆盖` 表示尚无可交付实现。

| 需求 | 产品入口 | 真实写稿/同稿证据 | Hook/宿主证据 | 状态与缺口 |
| --- | --- | --- | --- | --- |
| `WR-001` 事实与状态 | `references/information-selection.md`、各文种叶 | v1.6.4 W1—W6 | 无 Hook 也成立 | 已覆盖；继续按真实反例迭代 |
| `WR-002` 保护性外扩 | `hooks/capabilities/protective_expansion/`、普通语义 references | 同一 E0/E1 29 组功能终审；W1—W6 | 单 coordinator、三宿主静态 companion | 已覆盖；公开 README 旧示例待替换 |
| `WR-003` 责任承载 | 新闻叶和研究记录 | W4、W5 有效 | 不属于独立 Hook | 部分；跨文种候选未完成 |
| `WR-004` 文种用语 | `references/formulaic-language.md` 及文种叶 | W6 支持 `综上所述` | 不适用 | 部分；20 类事务文书未全部路由 |
| `WR-005` 短稿自然度 | 信息选择、新闻/请示/总结叶 | W1—W6 | D0 仍可能带过程旁白 | 部分；需拦正文外过程文字 |
| `WR-006` 审稿模式 | SKILL 任务模式、Hook bypass | OpenCode Go 自然审稿请求 | 显式 bypass 已有确定性覆盖 | 部分；复合任务与引语反控待做 |
| `HK-001` 无 Hook 闭环 | canonical Skill、普通 packages | v1.6.4 六稿 | 普通镜像排除 Hook | 已覆盖 |
| `HK-002` 写稿后插入 | `UserPromptSubmit` + `PostToolUse` + `Stop` coordinator | 不作为文采门 | Codex/Claude 当前在线、CodeBuddy 旧在线 | 已覆盖生命周期位置 |
| `HK-003` 单协调器 | `hooks/core/gate_stop_hook.py` | 同一任务仅一个 capability | 官方说明同事件多 Hook 可并发，因此保持单 coordinator | 已覆盖 |
| `HK-004` 宿主薄适配 | `hooks/adapters/` | 不适用 | Codex、Claude、CodeBuddy 官方契约与静态包 | 已覆盖结构；CodeBuddy Hooks 仍为 Beta |
| `HK-005` 故障回退 | coordinator 和 capability runtime | 当前 Codex/Claude 均选择 D0 并闭合 hash | CodeBuddy 旧在线 D0 回显恢复 | 已覆盖主要路径；错误终稿不得误标成功继续保留反控 |
| `HK-006` 知情与关闭 | `hooks/README.md`、opt-out classifier | 普通路径六稿；永久移除后真实写稿 | 未确认逐字不变；二次确认后隔离副本17文件移除、SKILL单点编辑 | 永久移除已覆盖；自然审稿语义待扩 |
| `UL-001` under-only 触发 | `hooks/capabilities/under_length/runtime.py` | Alibaba 268→342；Codex 268→350；Claude 268→344 | Codex、Claude 当前在线选择 D1；并行 Skill/材料读取竞态修复后 Codex 事务正常建立并安全选择 D0 | 已覆盖；竞态修复只保证单调状态，不调整篇幅语义门 |
| `UL-002` 安全扩写 | under revision/verdict prompt | 三条 provider 的失败稿驱动语义收窄；三份获选 D1 | 同一能力在两宿主在线执行 | 已覆盖当前事实充分采购请示；稀疏材料仍允许 D0 回退 |
| `UL-003` 产品准入 | 同一 D0/D1 功能门 | 两次独立 SOL max 均为 `ACCEPT` | selection/delivery/final hash 闭环 | 已覆盖目标功能；不以独立 on/off 总胜负替代 |
| `UL-004` 证据迁移 | adapter/core/runtime hash 分层 | CodeBuddy 旧完整在线；当前能力同稿复放 | 当前 CodeBuddy 静态包与 canonical runtime 同 hash | 部分；未冒充当前在线登录成功 |
| `CL-001` 交付洁净度 | `hooks/capabilities/delivery_cleanliness/` | 三 provider 5/5 精确整理；SOL max 全 PASS | 三宿主静态组装；Claude Code、Codex 在线 D1/hash 闭环 | 已覆盖目标功能；CodeBuddy 未重跑当前能力在线生命周期 |
| `RP-001` 重复与高相似句 | `hooks/capabilities/repetition_cleanup/` | 三 provider 5 组；SOL max 功能 PASS，长稿 1 WARN | 三宿主静态组装；Codex 完全重复与高相似均在线 E1/hash 闭环 | 已覆盖并合入本地 main；CodeBuddy/Claude 尚未做当前能力在线样本 |
| `AH-001` 引用与硬锚 | 现有能力有分散保护，尚未抽成共享不变量 | under-length 已有局部旁证 | 尚无统一 contract | 部分；不得使用词频完全相等旧门 |
| `OV-001` 超长收束 | 规格已登记 | 尚未运行 | 尚未接宿主 | 未覆盖；重复清理通过后再验证 |
| `OT-001/002` 提纲核对与修正 | 规格已登记 | 尚未运行 | 当前生命周期缺正文前提纲检查点 | 未覆盖；优先级低于 Stop-only 快速能力 |
| `MT-001` 真实结果优先 | `AGENTS.md`、本规格层 | v1.6.4 已采用 | 篇幅候选暴露了反例 | 已覆盖规则，后续严格执行 |
| `MT-002` 可达性 | SKILL、说明、组装器、维护索引 | 不适用 | reachability/链接最小检查 | 持续项 |
| `MT-003` 公开面克制 | 根 README、维护索引 | 最近五次主要证据 | 内部 HOLD 不进入产品宣传 | 持续项 |

## CodeBuddy 证据迁移明细

旧 CodeBuddy 在线成功包与当前 companion 的宿主层 SHA-256：

| 文件 | SHA-256 | 是否变化 |
| --- | --- | --- |
| `hooks/hooks.json` | `5f02f7b94b7c5b0aedd554d1d6cb2a85d1612f1296868960068b071fd9cf26d9` | 未变化 |
| `scripts/host_gate_adapter.py` | `d7ea6dad98991d7b650a95570aff6b2f7901f7b822db77d84f405d7a8c548cde` | 未变化 |
| `skills/.../hooks/gate_stop_hook.py` | `abe469b00e5b04adefdba240bd78afa4bfeed82b67a5ce0810a13e0bf7786834` | 未变化 |
| `under_length/runtime.py` | 当前组装时要求与 canonical 逐字一致 | 已变化，且是宿主无关能力层 |

旧在线样本完成 D0 180 字、D1 816 字、拒绝 D1、精确 D0 回显；当前变化后的 runtime 已用该原始 D0/D1 复放并拒绝不安全新增流程。Codex 与 Claude Code 又以当前 runtime 完成在线 Stop 生命周期并选择可用 D1。因此 CodeBuddy 当前登录失败记录为环境状态，不再作为篇幅语义开发的阻塞项，但也不写成当前在线成功。

## 官方契约依据

- Codex 官方 Hooks 说明：Stop 在主 Agent 完成响应时运行，携带 `last_assistant_message` 与 `stop_hook_active`；插件可通过根目录 `hooks/hooks.json` 加载，命令 Hook 需要显式信任。同事件的多个 Hook 会并发启动，因此本项目保持单 coordinator。[Codex Hooks](https://learn.chatgpt.com/docs/hooks.md)
- Claude Code 官方说明：Stop 在主 Agent 完成响应时运行；plugin 根使用 `hooks/hooks.json`，脚本通过 `${CLAUDE_PLUGIN_ROOT}`、数据通过 `${CLAUDE_PLUGIN_DATA}` 定位；用 `stop_hook_active` 防止循环。[Claude Code Hooks](https://code.claude.com/docs/en/hooks)
- CodeBuddy 官方说明：plugin Hook 位于根目录 `hooks/hooks.json`，使用 `${CODEBUDDY_PLUGIN_ROOT}` 与 `${CODEBUDDY_PLUGIN_DATA}`；多来源 Hook 合并并并行，Windows 由 Git Bash 执行命令；Hooks 当前为 Beta。[CodeBuddy Hooks](https://www.codebuddy.ai/docs/cli/hooks)
- OpenSpec 只作为文档设计参考：需求、变更和证据分层；本仓库未安装其 CLI 或 workflow。[OpenSpec 核心概念](https://github.com/Fission-AI/OpenSpec/blob/main/docs/overview.md)
