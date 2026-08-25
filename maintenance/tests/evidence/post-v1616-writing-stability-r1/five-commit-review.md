# v1.6.16 后写稿稳定性五提交复核

日期：2026-08-26。

## 结论

`PASS / NO_MERGE_BLOCKER / PRODUCT_TREE_UNCHANGED`。

本检查点位于 `codex/post-v1616-writing-stability-r1@14d443c5`，相对固定 `main@6d7fc0ec8f1227638652527670f251eba9d76f86` 恰为5个提交。复核完成前没有继续扩展原子或制作产品候选。

独立只读冷审逐项复核 `main...HEAD`、预登记、R6b补充预登记、官方校准、结果页及忽略目录中的7份有效终稿，结论为 `PASS`，没有合并阻断。冷审确认：7份终稿hash与结果表一致；R6b没有事后并入R6准入；单provider失败没有冒充共同失败；7份有效稿中6份正文外包装的计数成立；状态台账无活动HOLD。

## Baseline diff 与轻量消融

- `git rev-list --count main..HEAD`：`5`。
- `git diff --quiet main...HEAD -- chinese-official-writing packages`：退出码0。
- `main:chinese-official-writing` 与 `HEAD:chinese-official-writing` tree 均为 `3ba4e9ead52d6234258d947157e1b41bab1e5403`。
- `main:packages` 与 `HEAD:packages` tree 均为 `f2bdd9a14ef75b21392d216e31e8f3d0556434d3`。
- 逐一重算7份有效终稿SHA-256，7/7与 `result.md` 一致；`wr020a2-ollama-baseline.final.txt` 不存在，符合两次技术失效且无终稿的记录。
- 包装机械观察加人工复核：R6 OpenCode为唯一无正文外包装样本，其余6份均有过程说明、自评、计数回执或Markdown横线；该观察不改变本轮原子准入。

这组消融确认维护证据的加入没有改变公开产品、普通包、Hook、adapter、付费候选或发布面。没有可供Grok、SOL、Kimi或Qwen评审的产品D1，因此未运行空昂贵冷审。

## 回归与结构检查

- `py -3.13 -B -m unittest maintenance.tests.test_status_ledger_consistency maintenance.tests.test_repository_reachability`：13项通过。
- `py -3.13 -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- `git diff --check main...HEAD`：通过。
- `git status --short --branch`：分支干净。

定向状态测试首跑曾因WR-020新状态把既有精确子串拆开而失败1项；已保留原 `B1_REJECTED / B2_DONE / WAIT_NEW_COUNTEREXAMPLE` 顺序并在其后追加a2结果，复跑7项通过，最终全组13项通过。该失败是台账兼容问题，不是写稿结果变化。

## 剩余风险

1. 无Hook直写的交付洁净度仍不稳定，7份有效稿中6份带正文外包装；现有CL-001是已验证的可选兜底，本轮没有重跑或修改。
2. `WR-020a2` 只有OpenCode有效长稿，Ollama两次技术失效，不能声称跨provider长稿稳定。
3. `WR-014-R6b` 只有Ollama出现证据未附外推；等待新材料的共同反例，不扩大成全局禁词或硬门。
4. 本分支只有维护证据和状态回填；是否合入main须另有明确授权，不在本复核中执行。

没有push、tag、上传或发布。
