# 提纲辅助 Hook

提纲辅助 Hook 是单独启用的起草前增强，用于先把用户材料整理成事实放置提纲，再成稿，并在首次交付前按同一提纲做一次删减式核对。普通 Skill 不依赖本能力。

## 适用场景

- 材料中同时包含多个责任主体、动作和时限，容易被拆成重复章节；
- 用户已经给出标题顺序或提纲，需要保持原结构；
- 材料较少，希望避免为补齐固定骨架而新增目的、要求、流程或后续安排。

## 工作方式

1. `UserPromptSubmit` 提示主 Agent 在起草前调用一次专用 `outline-planner`；
2. 子代理先锁定标题、主送、落款和日期，再分配材料原有事实，不写正文；完整文稿未给精确标题且用户没有排除标题时，可仅按已给事项和文种拟题；用户要求“只输出正文”“仅正文”时不补标题，主送、落款和日期未提供时也不补泛称、占位符或当前日期；材料稀疏时可只用一个不设小标题的自然段，不为凑结构拆分；
3. `PostToolUse:Agent` 将返回的章节和事实单元冻结为本轮提纲；
4. 首次 `Stop` 要求对照提纲做一次删减式核对，第二次 `Stop` 直接放行。

该能力不会自动识别宿主、生成安装文件、修改宿主配置或主动联网。它会增加一次提纲生成和一次有限核对，因此通常比普通 Skill 慢，并会多用一次子 Agent 调用。Codex 仅在插件数据目录保存当前轮次的阶段、Agent ID 和内容哈希，不保存用户原文或提纲正文；Claude Code 与 WorkBuddy / CodeBuddy 版本不另建本能力的状态文件。宿主自身仍会按其正常机制保存会话记录。

## 启用与关闭

下载普通 Skill 不会启用本能力。只有用户明确安装并启用提纲 companion 后，Hook 才会参与写稿。当前已完成以下真实生命周期验证：

- Codex CLI 0.144.6：`spawn_agent → wait → Stop 阻断 → 二次交付`；
- WorkBuddy 内置 CodeBuddy CLI 2.115.0：`outline-planner → PostToolUse → Stop 阻断 → 二次交付`；
- Claude Code 2.1.195：`outline-planner → PostToolUse → Stop 阻断 → 二次交付`。

各宿主按自己的插件方式启用：

### Codex

从已配置的 marketplace 安装 companion：

```text
codex plugin add chinese-official-writing-outline@<marketplace>
```

完全关闭时移除 companion：

```text
codex plugin remove chinese-official-writing-outline@<marketplace>
```

### WorkBuddy / CodeBuddy

临时加载一个已组装并校验的 companion 根目录：

```text
codebuddy --plugin-dir <companion-root>
```

测试或首次使用时，先进入交互会话，确认插件加载完成后再输入写稿请求。已安装版本可用 `codebuddy plugin disable chinese-official-writing-outline` 停用。

### Claude Code

临时加载一个已组装并严格校验的 companion 根目录：

```text
claude --plugin-dir <companion-root>
```

已安装版本可用 `claude plugin disable chinese-official-writing-outline` 停用。

安装、启用、信任和真实运行是四件独立的事；其他版本应先做宿主校验和一次临时会话 smoke。当前任务只需临时关闭时，可直接说“本次关闭 Hook，按普通 Skill 完成”；本轮不会调用提纲 Agent，也不会阻断交付。永久关闭使用对应宿主的禁用或移除命令。

当前 companion 应单独加载，不与其他会阻断 `Stop` 的交付门 companion 同时启用；组合协调仍是后续独立验证项。

## 边界

- 只处理提纲生成、事实放置和纲外内容删减，不补篇幅、不改事实结论；
- 用户以 `《文名》` 指代拟写文件时，书名号默认不进入正式主标题，除非用户明确要求保留；
- 只审不改、解释、安装配置和单句局部修改不调用提纲代理；
- 子代理未成功完成时不阻断普通写稿；判断不确定时保留主 Agent 原稿。
- 会话记录不可读或使用 `--no-session-persistence` 时，前置提纲仍可工作，成稿后的 `Stop` 核对安全跳过。
- WorkBuddy / CodeBuddy 的一次性非交互启动可能在插件注册前收到首条用户请求；需要验证完整生命周期时使用已完成插件加载的交互会话。
