# Markdown 候选选择性采用审查

## 结论

建议按最小范围选择性采用，不整分支合入。R30 两页文档规则有真实稿件支持；`--allow-markdown` 经本轮增量修复后边界正确，未发现新的确定缺陷。Python 检查只证明脚本行为、路径和回归状态，不作为写稿语义质量证明。

## 此前审查结论

审查对象为外部分支 `b25601bb` 相对父提交 `1f2e9da8` 的两次提交，并比较 R30 文档候选 `52fcaab1`。

建议采用：

- R30 的两页产品改动：在 `anti-ai-patterns.md` 删除笼统的“来源样式优先”，在 `writing-rules.md` 的交付位置集中规定普通文字稿清除标题井号、加粗、分隔线和整稿代码围栏，同时保留用户明确要求的 Markdown、代码和模板。
- `prose_lint.py` 的显式 Markdown 选择参数，但须保留旁白、占位、装饰符等非 Markdown 风险检查；本轮最终增量已完成该修复。
- `prose-lint-usage.md` 关于显式格式参数和“最终采用最后一次扫描文本”的说明。
- `compatibility-scene-routing.md` 删除不存在的“编号检查步骤”，改为指向首页写作、复核与交付步骤。

建议排除：

- 首页重复一遍完整交付格式规则，避免入口和共性页双写。
- `draft_length.py --print-body/--print-link`。它把交付输出混入篇幅统计，且 `--print-body` 会隐藏低于下限状态并返回成功，不是本次 Markdown 修复的必要组成。
- 禁止审核意见使用表格、加粗标题或多级标题的规则。审核意见是正文外独立交付件，其表格和加粗不构成正文污染。
- “只有用户明确要求才启动独立复核”的规则。独立复核可在确有需要且宿主支持时启用，只清理旁白、工程或工具自述、可见思考和写稿过程泄露，并保留业务内容、合理分析及有效审核意见。
- `run_real_prompt_ablation.py` 的 2.0 迁移及配套语义词句测试。该 evaluator 对 111 个旧用例跳过了 82 项 `file_terms` 和一项 `heading_lock`，其中 73 个用例没有执行原有个案检查；其结果只能视为静态迁移烟测。

R30 的 20 次原生调用、10 个同题同模型配对只绑定两页文档原型。采购稿整稿围栏从基线 3/4 降至候选 0/4，明确要求 Markdown 的 8 份稿件均保留标题和列表，支持“普通稿去包装、明确 Markdown 保留”的局部采用。同时存在一次列表落实偏离、个别正文内容风险和耗时上升，因此不能据此宣称全文种全面更好，也不能把该证据扩展绑定到后加脚本或其他规则。

## 最终脚本修复增量复核

复核范围仅为 `c06c299e..69914fb3` 中的 `chinese-official-writing/scripts/prose_lint.py` 和 `maintenance/tests/test_markdown_opt_in.py`。

修复恰当：

- 显式允许 Markdown 时，只移除 `markdown-bold`、`markdown-heading` 及 Markdown 列表形式；`western-bullet` 改为继续匹配 `•●◆◇★✅☑` 等装饰符。
- 频繁列表检查在允许 Markdown 时仍统计装饰符，不再因格式选择整体关闭。
- `review-only` 自动允许 Markdown 呈现，使 `## 审核意见`、`**位置**` 和 `- 建议` 不被当作正文污染。
- 自动允许仅影响 Markdown 格式规则。`thought-leak`、`unfinished-placeholder` 及其他内容和交付风险仍正常检查。
- 未显式允许 Markdown 的 `draft-body` 保持原行为，继续报告标题、加粗和西式列表标记。

本轮未发现新的确定 bug。剩余限制是扫描器只覆盖其已定义的 Markdown 形式，不能把“无 finding”解释为所有 Markdown 方言或写稿语义均已验证；这不是本次增量新增的回退。

## 本轮验证

- `git diff --check c06c299e 69914fb3 -- chinese-official-writing/scripts/prose_lint.py maintenance/tests/test_markdown_opt_in.py`：通过。
- `python -m unittest maintenance.tests.test_markdown_opt_in`：4 项通过，0 失败。
- API 边界探针：普通正文的标题、加粗和列表分别返回 `markdown-heading`、`markdown-bold`、`western-bullet`；审核意见的同类呈现不报 Markdown 格式风险；审核意见中的可见思考仍返回 `thought-leak`；显式 Markdown 围栏内的旁白和占位仍返回 `thought-leak`、`unfinished-placeholder`；单个及 8 个装饰符分别保留 `western-bullet` 和 `frequent-list-markers`；Markdown 数字列表在显式允许时不报 `western-bullet`。
- 已有证据记录 120 项相关脚本行为回归通过；script-delta 原生 Markdown 通知两臂均保留指定格式并成功执行扫描。本轮未重复这些外部执行，也不把它们扩张为全文种语义结论。

本审查未修改产品代码或测试，未提交、合并、推送或发布。
