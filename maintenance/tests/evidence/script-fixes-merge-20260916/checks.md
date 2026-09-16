# 合并前检查

以下只验证程序、路径和包结构；成稿验收见真实写稿记录。

## 程序

在本worktree执行：

```text
python -B -m unittest maintenance.tests.test_script_quality_r1 maintenance.tests.test_reading_process_lint maintenance.tests.test_lint_context_fusion maintenance.tests.test_review_regressions.ProseLintStructureTests maintenance.tests.test_review_regressions.UnresolvedStateChainTests maintenance.tests.test_review_regressions.ProseLintCliTests maintenance.tests.test_review_regressions.CleanProseCorpusTests maintenance.tests.test_protective_negative_tail_lint maintenance.tests.test_draft_length maintenance.tests.test_markdown_opt_in maintenance.tests.test_placeholder_blind_spot_fix maintenance.tests.test_scene_filler_lint maintenance.tests.test_explanatory_tail_cluster
```

142项通过，17.837秒。未运行混合历史词句断言的全量discover，也不把程序测试数量称为真实写稿覆盖。

```text
python maintenance/tools/audit_product_surface.py --root chinese-official-writing
python C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py chinese-official-writing
git diff --check
```

均通过。路径工具明确说明可达不等于语义有效。

## 来源与隔离

baseline为82cc2819，candidate为ac0da985。Git内容仅改两份scripts和prose-lint-usage.md；anti-ai-patterns.md的Git blob完全一致。原生runner的git快照使用LF，工作树副本使用CRLF，另70文件只有换行差异；归一换行后仅上述3文件改变。原始快照指纹照实保留，未回写冻结文件，见snapshot-scope.json。

旧脚本修复来自baed9860/0bf75d75，本分支cherry-pick为cef8eebf/59b10c6d；后续选择1401407e中的脚本与最小使用说明，未接入其抗AI修改。以前只有scripts变化的首次4次原生证据保留，另外4次误重复不追加票数。

本机安装在合并前核对：安装目录、Codex缓存及state中的162份Skill文件一致；当前普通源绑定77a0c86a。合并后复用已有同步器更新，签名/安装/启用/Hook信任结果分别记录，安装验证不冒充新宿主写稿验证。
