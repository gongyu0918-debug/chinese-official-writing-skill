# 1.5.5 发布记录

日期：2026-07-09

## 范围

1.5.5 基于 `8b645a2` 的深度 review 结果发布，只包含：

- `references/workflow.md` 事实充分性长段拆分为短 bullet 的最小 reference 结构修复。
- 版本号从 `1.5.4` 同步到 `1.5.5`。
- 同步 Codex、Claude Code、Qwen、Hermes、OpenClaw、Claude plugin、README 和 SkillHub/ClawHub 发布元数据。

未新增脚本硬清洗、lint 规则、默认阻断、默认联网、排版引擎或一例一修规则。

## 真实写稿 A/B

真实写稿 A/B 证据见 `tests/evidence/deep-review-1.5.4-workflow-split.md`。本轮使用 1.5.4 基线和当前候选各 30 类真实用户式 prompt，覆盖 description 声明的主要文种和正式材料类型。post-fix verifier 结论为 `WARN`，但未出现 current 独有且达到三次以上的同类功能性回退，建议保留拆分、不回滚、不继续补丁式追加规则。

## 发布前验证

已运行：

```cmd
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover -s tests
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\local-1.5.4-48f3190 --baseline-label baseline-1.5.4 --current-root . --out output\real-prompt-vs-1.5.4-release-1.5.5
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe C:\Users\2\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2
C:\Users\2\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\tools\run_real_article_eval.py --out output\real-article-release-1.5.5
git diff --check
```

结果：

- 全量 unittest：107/107 通过。
- 1.5.4 确定性消融：baseline `95/95`，current `95/95`。
- quick_validate：`Skill is valid!`
- promptfoo smoke：20/20 通过，skill_win_rate `1.0`，judge_consistency_rate `1.0`。
- 真实样文回归：skill 平均差异率 `0.00%`，关键词命中率 `100.00%`；仍有占位词风险样本，需人工复核。
- `git diff --check`：通过，仅 Windows 换行提示。

## 发布前远端检查

- SkillHub 登录：`skillhub auth whoami` 返回 `userId=437097`。
- SkillHub dry-run：`{"dryRun": true, "slug": "chinese-official-writing", "version": "1.5.5"}`。
- ClawHub 发布前 inspect：远端为 `latestVersion.version=1.5.4`，`displayName=中文公文写作`，`tags.latest=1.5.4`，moderation `clean`；历史 `1.4.15` 遗留带引号 tag key 仍存在，本轮发布命令继续使用等号参数避免新增引号字段。

## 待发布动作

1. 提交本地 release commit。
2. 创建并推送 GitHub tag `v1.5.5`。
3. 发布 ClawHub `chinese-official-writing@1.5.5`。
4. 发布 SkillHub `chinese-official-writing@1.5.5`。
5. 发布后复查 GitHub、ClawHub、SkillHub 远端字段。
