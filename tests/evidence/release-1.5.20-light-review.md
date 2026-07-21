# 1.5.20 发布分支轻量 Diff Review

## 结论

**WARN**

BB、BC 两项产品改动总体保持单变量边界，规则正文未见丢失，五套发行镜像与 canonical 对应内容一致，OpenClaw 的三项运行时排除边界未变化。当前有两处路由/测试同步不完全，建议发布前最小修正并补定向测试；它们尚未构成已证实的写稿回退，因此本次不判 FAIL。

## 审核对象

- 工作树：`F:\Workspaces\chinese-official-writing-skill\output\release-worktrees\release-1.5.20`
- 基线产品提交：`e22b0150666974f38c4ce9c3b75cf6757091e646`
- 审核 HEAD：`1d8f72fabd39928996662ee9f699857ab22834aa`
- 产品提交：
  - BB：`e06dbea1817b4d866b45c5ff4992f0844d3eae50`
  - BC：`b9a0d171d8b889542eae3583fe2c247d37867f75`

## 发现项

### [WARN-1] 报告检查叶拆出后，SKILL 脚本段仍只指向公共 `genre-checklist.md`

证据：

- `chinese-official-writing/SKILL.md` 的渐进加载表已正确增加 `genre-checklist-report.md`，并把 `genre-checklist.md` 的适用范围改为其他文种。
- `genre-playbooks.md` 的“报告/情况说明”也已正确补充读取 `genre-checklist-report.md`。
- 但 `SKILL.md` 的“脚本”段仍写“文种和办理要素仍按 `handling-elements.md`、`genre-checklist.md` 与人工/LLM 复核判断”。报告规则已经从后一个文件移走，该句在“使用 prose_lint 后做文种复核”的路径上可能把报告复核指向不含报告规则的公共文件。

影响：主路由仍能到达新报告叶，三题真实 A/B 也未显示硬回退，因此不是确定性功能失败；但这是一个可直接定位的交叉引用不一致，会削弱 BC 的路由完整性。

建议：只把该句改为“对应文种检查叶”或同时列出 `genre-checklist-report.md`，不调整任何规则正文；增加一条测试，确认报告复核路径不会只落到公共 checklist。

### [WARN-2] Promptfoo 测试适配器的外部检索触发词窄于产品加载条件

证据：

- 产品入口与 `external-research.md` 的条件包括：用户明确要求搜索/核验公开来源，或任务包含“最新”“当前”“今日”“现行政策”“近期数据”等时效事实。
- `evals/official-writing/providers/agent_writer.py` 新增的触发词覆盖了“联网搜索、联网核验、搜索公开来源、核验公开来源、现行政策、近期数据、最新政策、最新数据、今日数据”，但没有覆盖一般形式的“搜索……”以及独立出现的“最新”“当前”“今日”。
- 新增单测只验证“核验现行政策和公开来源”这一条命中，以及普通报告不命中，尚未验证入口列出的全部触发族。

影响：这不改变随 Skill 分发的产品规则，但可能使部分 Promptfoo 任务没有加载 `external-research.md`，造成测试上下文与真实产品路由不对称。

建议：把适配器判定与产品加载条件共用同一组最小语义触发口径，并增加正反例；避免只按裸词“当前”误触发时，可用“当前/今日/最新 + 政策、数据、规定、标准、情况”等组合，而不是直接扩大到任意文本。

## 单变量边界核对

### Candidate BB

产品侧只做了以下变化：

1. 从 `workflow.md` 的“联网搜索使用边界”抽出详细规则；
2. 新增 `external-research.md`；
3. 在 `SKILL.md` 加入按需加载行；
4. 同步镜像及评测适配器/测试。

旧规则的实质内容仍可在入口、workflow 短路由和新叶中找到：默认不外搜、搜索用途、来源字段、冲突/无法核验处理、单位名称不触发样文搜索均未丢失。未发现扩大默认联网或改变普通写稿输出模式。

### Candidate BC

产品侧只做了以下变化：

1. 将 `genre-checklist.md` 中原有的报告4条规则移入新文件 `genre-checklist-report.md`；
2. 在 `SKILL.md` 加入报告叶加载条件，并把公共 checklist 的适用文种改为非报告文种；
3. 在 `genre-playbooks.md` 报告路由中增加新叶；
4. 同步镜像和定向测试。

新叶中的4条报告规则与基线原文一致。公共 checklist 除删除报告小节外未见其他文种规则变化，因此通知、请示、命令、公报、决议、议案、函、批复、公告、通告、公示、通报、纪要、讲话稿、述职等内容未被改写。

## 镜像与 OpenClaw

逐文件 SHA-256/正文比对结果：

- `skills/chinese-official-writing`：0 mismatch
- `.agents/skills/chinese-official-writing`：0 mismatch
- `.qwen/skills/chinese-official-writing`：0 mismatch
- `hermes/skills/chinese-official-writing`：0 mismatch（SKILL frontmatter 按适配器处理，正文一致）
- `openclaw/skills/chinese_official_writing`：0 mismatch（SKILL frontmatter 按适配器处理，正文一致）

OpenClaw 继续排除：

- `references/delivery-review-gate.md`
- `scripts/gate_stop_hook.py`
- `scripts/review_gate.py`

三项在 OpenClaw 包中均不存在，`scripts/prose_lint.py` 仍保留。未发现 BB/BC 改动改变排除列表、引入 Codex gate runtime 或制造镜像语义分叉。

## 实际检查

执行：

```text
python -B -m unittest \
  tests.test_skill_boundary.SkillBoundaryTests.test_primary_adapter_mirrors_match_canonical_bytes \
  tests.test_skill_boundary.SkillBoundaryTests.test_packaged_resource_mirrors_match_canonical_bytes \
  tests.test_skill_boundary.SkillBoundaryTests.test_openclaw_skill_excludes_codex_gate_runtime \
  tests.test_skill_boundary.SkillBoundaryTests.test_v141_search_boundary_stays_lightweight_and_opt_in \
  tests.test_skill_boundary.SkillBoundaryTests.test_report_checklist_is_routed_as_an_atomic_leaf \
  tests.test_promptfoo_eval.PromptfooProviderTests.test_external_research_leaf_is_loaded_only_for_explicit_research_tasks
```

结果：6项通过，`Ran 6 tests ... OK`。

另做只读检查：

- `git diff --stat`、两项产品提交的 `git show --name-status`；
- canonical 与五套发行镜像逐文件比对；
- OpenClaw 三项排除文件存在性检查；
- 基线报告小节与新报告叶逐条内容核对；
- 基线联网规则与入口、workflow、新 external leaf 的语义覆盖核对。

## 发布判断

当前 diff **没有越过 BB/BC 的产品机制边界，没有发现规则实质丢失、其他文种正文规则改写、OpenClaw 排除变化或镜像漂移**。两处 WARN 都能用单一交叉引用/测试适配器修正处理，不需要改写 Prompt 或扩大候选。修正后应重跑上述6项、全量 unittest、Promptfoo smoke、镜像一致性和 `git diff --check`。
