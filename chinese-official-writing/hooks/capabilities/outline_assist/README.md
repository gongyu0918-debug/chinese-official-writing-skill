# 提纲辅助 Hook

提纲辅助 Hook 是单独启用的起草前增强，用于先把用户材料整理成事实放置提纲，再成稿，并在首次交付前按同一提纲做一次删减式核对。普通 Skill 不依赖本能力。

## 适用场景

- 材料中同时包含多个责任主体、动作和时限，容易被拆成重复章节；
- 用户已经给出标题顺序或提纲，需要保持原结构；
- 材料较少，希望避免为补齐固定骨架而新增目的、要求、流程或后续安排。

## 工作方式

1. `UserPromptSubmit` 提示主 Agent 在起草前调用一次专用 `outline-planner`；
2. 子代理先锁定标题、主送、落款和日期，再分配材料原有事实，不写正文；未提供的文档要素不补泛称、占位符或当前日期；
3. `PostToolUse:Agent` 将返回的章节和事实单元冻结为本轮提纲；
4. 首次 `Stop` 要求对照提纲做一次删减式核对，第二次 `Stop` 直接放行。

该能力不会自动创建安装文件、修改宿主配置或联网，也不在本地另建提纲事务文件。它会增加一次提纲生成和一次有限核对，因此通常比普通 Skill 慢。

## 启用与关闭

当前已在 Claude Code 2.1.195 完成真实生命周期验证。组装时明确选择 `outline_assist`：

```text
python -B maintenance/tools/assemble_hook_companion.py --host claude-code --capability outline_assist --output <新目录>
claude plugin validate <新目录> --strict
claude --plugin-dir <新目录>
```

组装、校验和加载是三个独立步骤；工具不会自动安装或启用。未加载该 companion 即为关闭；已安装时可用 `claude plugin disable chinese-official-writing-outline` 停用。其他 Claude Code 版本应先做严格校验和一次临时目录 smoke。

当前候选应单独加载，不与其他会阻断 `Stop` 的交付门 companion 同时启用。Codex、WorkBuddy / CodeBuddy 尚无本候选的在线子代理生命周期证明，继续使用普通 Skill。

当前任务只需临时关闭时，可直接说“本次关闭 Hook，按普通 Skill 完成”。

## 边界

- 只处理提纲生成、事实放置和纲外内容删减，不补篇幅、不改事实结论；
- 用户以 `《文名》` 指代拟写文件时，书名号默认不进入正式主标题，除非用户明确要求保留；
- 只审不改、解释、安装配置和单句局部修改不调用提纲代理；
- 子代理未成功完成时不阻断普通写稿；判断不确定时保留主 Agent 原稿。
- 会话记录不可读或使用 `--no-session-persistence` 时，前置提纲仍可工作，成稿后的 `Stop` 核对安全跳过。
