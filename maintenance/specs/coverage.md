# 需求覆盖矩阵

`已覆盖` 表示存在对应产品实现和直接证据；`部分` 表示只有规则、工程链或一部分真实执行；`未覆盖` 表示尚无可交付实现。

| 需求 | 产品入口 | 真实写稿/同稿证据 | Hook/宿主证据 | 状态与缺口 |
| --- | --- | --- | --- | --- |
| `WR-001` 事实与状态 | `references/information-selection.md`、各文种叶 | v1.6.4 W1—W6 | 无 Hook 也成立 | 已覆盖；继续按真实反例迭代 |
| `WR-002` 保护性外扩 | `hooks/capabilities/protective_expansion/`、普通语义 references | 同一 E0/E1 29 组功能终审；W1—W6 | 单 coordinator、三宿主静态 companion | 已覆盖；公开 README 旧制度示例已用事实安全正文替换 |
| `WR-003` 责任承载 | `references/information-selection.md`、中央事务文体叶 | 20份真实稿；C02-R3、C03直连复测 | 不属于独立 Hook | 已覆盖并随 v1.6.6 发布 |
| `WR-004` 文种用语 | `references/formulaic-language.md`、新闻消息叶、SKILL直接路由 | 20类真实写稿，原型19/20；“编者按”修复后目标20/20 | 不适用 | 已覆盖并随 v1.6.6 发布 |
| `WR-005` 短稿自然度与常用语机械化 | `references/short-draft-naturalness.md`、信息选择和文种叶 | 短稿 R3 上限题8次，候选3胜0负1平且硬边界全 PASS；产品接入后两篇在线直写可用；常用语 R1—R6 真实调用 | 交付洁净度与重复清理只作可选兜底 | 短稿自然度已随 v1.6.7 发布；硬下限归 under-length；常用语 R1—R6 均 HOLD，本版未改总表 |
| `WR-006` 审稿模式 | SKILL 任务模式、Hook bypass | OpenCode Go 自然审稿请求 | 自然审稿、复合成稿和引语反控已完成 | 已随 v1.6.9 发布 |
| `WR-007` 语义减载与自然表达 | `references/anti-ai-patterns.md`、`references/genre-playbook-request.md` | R1 16稿；R2—R4 20稿；组合后24/24技术有效 | 不属于独立 Hook | 已集成 `main`；三方冷审无候选独有硬失败，只写到现有事实和状态，压住供应商确定后的后续动作外推 |
| `WR-008` 标题与正文边界 | canonical SKILL 主入口标题条目 | 16/16 生成无回退；12/12 同稿修复，候选6/6精确；自然路由R2两家均通过 | 不属于独立 Hook | 已合入；主标题无句号并空一行、层级标题无句号、编号正文句保留句号 |
| `HK-001` 无 Hook 闭环 | canonical Skill、普通 packages | v1.6.4 六稿 | 普通镜像排除 Hook | 已覆盖 |
| `HK-002` 写稿后插入 | `UserPromptSubmit` + `PostToolUse` + `Stop` coordinator | 不作为文采门 | Codex/Claude 当前在线；WorkBuddy 5.3.13 当前 companion 在线 | 已覆盖生命周期位置 |
| `HK-003` 单协调器 | `hooks/core/gate_stop_hook.py` | 同一任务仅一个 capability | 官方说明同事件多 Hook 可并发，因此保持单 coordinator | 已覆盖 |
| `HK-004` 宿主薄适配 | `hooks/adapters/` | 不适用 | Codex、Claude、CodeBuddy 官方契约与静态包 | 已覆盖结构；CodeBuddy Hooks 仍为 Beta |
| `HK-005` 故障回退 | coordinator 和 capability runtime | 当前 Codex/Claude 均选择 D0 并闭合 hash | WorkBuddy 当前重复清理样本选择 E1并闭合hash，临时关闭零事务 | 已覆盖主要路径；错误终稿不得误标成功继续保留反控 |
| `HK-006` 知情与关闭 | `hooks/README.md`、opt-out classifier | 普通路径六稿；永久移除后真实写稿 | 未确认逐字不变；二次确认后隔离副本17文件移除、SKILL单点编辑 | 永久移除已覆盖；自然审稿语义待扩 |
| `UL-001` under-only 触发 | `hooks/capabilities/under_length/runtime.py` | Alibaba 268→342；Codex 268→350；Claude 268→344 | Codex、Claude 当前在线选择 D1；并行 Skill/材料读取竞态修复后 Codex 事务正常建立并安全选择 D0 | 已覆盖并随 v1.6.5 发布；竞态修复不调整篇幅语义门 |
| `UL-002` 安全扩写 | under revision/verdict prompt | 三条 provider 的失败稿驱动语义收窄；三份获选 D1 | 同一能力在两宿主在线执行 | 已覆盖当前事实充分采购请示；稀疏材料仍允许 D0 回退 |
| `UL-003` 产品准入 | 同一 D0/D1 功能门 | 两次独立 SOL max 均为 `ACCEPT` | selection/delivery/final hash 闭环 | 已覆盖目标功能；不以独立 on/off 总胜负替代 |
| `UL-004` 证据迁移 | adapter/core/runtime hash 分层 | CodeBuddy 旧完整在线；当前能力同稿复放 | 当前 CodeBuddy 静态包与 canonical runtime 同 hash | 部分；未冒充当前在线登录成功 |
| `CL-001` 交付洁净度 | `hooks/capabilities/delivery_cleanliness/` | 三 provider 5/5 精确整理；SOL max 全 PASS | 三宿主静态组装；Claude Code、Codex 在线 D1/hash 闭环 | 已覆盖并随 v1.6.5 发布；CodeBuddy 未重跑当前能力在线生命周期 |
| `RP-001` 重复与高相似句 | `hooks/capabilities/repetition_cleanup/` | 三 provider 5 组；SOL max 功能 PASS，长稿 1 WARN | 三宿主静态组装；Codex 与当前 WorkBuddy companion 均在线 E1/hash 闭环 | 已覆盖并随 v1.6.5 发布；Claude 尚未做当前能力在线样本 |
| `AH-001` 引用与硬锚 | `hooks/shared/hard_anchors.py`；under/over 机械门与既有语义验收 | 24/24 先行实验；12份原型/回放；12次缺口修复真实修订 | 单 coordinator 内共享，不另起 Hook；三宿主 companion 静态组装 | 已集成 `main`；字段、标识数字、汉字数量和篇幅授权边界回归通过，最后窄增量三方冷审均 PASS；其他改稿能力尚未迁移 |
| `OV-001` 超长收束 | `hooks/capabilities/over_length/`、短稿自然收束叶 | 两家 provider 先行原型；同一 D0 498→285，SOL max 六项全 PASS；Qwen 补丁后同稿重放通过 | Claude Code 在线 D1/hash 闭环；Grok 4.6 冷审修复；三宿主静态组装 | 已随 v1.6.8 发布，五项边界补丁随 v1.6.9 发布；Codex/CodeBuddy 当前版本在线样本待补 |
| `OT-001/002` 提纲核对与修正 | 规格已登记 | 尚未运行 | 当前生命周期缺正文前提纲检查点 | 未覆盖；优先级低于 Stop-only 快速能力 |
| `MT-001` 真实结果优先 | `AGENTS.md`、本规格层 | v1.6.4 已采用 | 篇幅候选暴露了反例 | 已覆盖规则，后续严格执行 |
| `MT-002` 可达性 | SKILL、说明、组装器、维护索引 | 不适用 | reachability/链接最小检查 | 持续项 |
| `MT-003` 公开面克制 | 根 README、维护索引 | 最近五次主要证据 | 内部 HOLD 不进入产品宣传 | 持续项 |
| `MT-004` 信息熵与重复规则 | SKILL/reference 路由与叶子停止条件 | 12组真实读取；24次组合写稿 | 不属于 Hook | `OBSERVE`；已扫描重复，尚无真实稿回退，不为去重破坏叶子自包含 |

## 当前语义层收束

- `WR-003/004` 已随 v1.6.6 发布；`WR-005` 短稿自然收束已随 v1.6.7 发布；常用语默认拆分仍 HOLD。
- R1 降低了固定开头词频，却增加了事实硬失败和另一类空泛、重复、自证；R2 工程上稳定，但基线6胜、候选4胜、难分2，且候选仍有1个事实硬失败。
- 单个正式连接词不构成机械化；只有固定开头、承启、总结、结尾或段落骨架成簇复现，且对任务没有功能贡献时，才计入同质化风险。
- 常用语 R4—R6 的更小拆分仍出现硬回退，停止继续修改总表。短稿自然度和实际重复清理由各自已验证机制承担，不用新的统一反机械规则覆盖所有文种。

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
