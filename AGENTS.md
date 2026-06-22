# AGENTS.md

本文件适用于整个仓库。后续 agent 接手本仓库时，优先遵守这里的发布、review 和测试约定；若与用户最新指令冲突，以用户最新指令为准，但不得伪造未运行的测试结果。

## 基本工作纪律

1. 所有代码或文档修改必须通过 git commit 留痕。commit message 需说明修改目的、影响范围和验证方式。
2. 每次认为任务可交付前，必须运行 smoke test 或最小验证流程；无法运行时说明原因和人工验证步骤。
3. 每累计 5 次 commit，或修改范围明显扩大时，暂停开发，执行轻量 review、基线对比、轻量消融测试和回归检查。
4. 代码 review、大范围 diff、长文件阅读、第三方实现对比等可能污染主上下文的任务，优先交给 subagent 或独立上下文；subagent 结论必须经源码、diff、测试或日志交叉验证后再采纳。
5. 不允许伪造测试结果；未实际运行的命令不得写成已通过。

## 中文公文 Skill 发布验证

`tools/run_real_prompt_ablation.py` 是发布级确定性消融工具，但它不调用 LLM，只能证明 skill 包、reference、lint 和评估入口具备相应支撑。它不能替代真实写稿实测。

涉及 `chinese-official-writing` 的版本 review、发布或回归判断时，必须同时做两类验证：

1. **基线消融**：用 detached worktree 固定上一发行基线，只和上一基线比，不和 no-skill 混比。示例：
   - `git worktree add --detach output\release-baselines\github-1.4.1 74dc5be8e1c9dfa30b0ef3f484c3eb5edc8a7fed`
   - `python .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.4.1 --baseline-label baseline-1.4.1 --current-root . --out output\real-prompt-vs-1.4.1-release-1.4.3`
   - 判断口径：current 失败才是发布阻断；baseline 只允许在新补充用例上失败。
2. **真实写稿实测**：用真实用户式 prompt 让写作 agent 产出短稿或改稿，再让独立 verifier 只看“原 prompt + 成稿”判断，不由主上下文自行判定。稿件可以不长，但必须检验指令遵循、要点置入、文种格式、禁止事项、事实边界和是否把格式改坏。

真实写稿实测至少覆盖：

- 本轮新增或修改的边界，例如网页复制稿、套嵌文件、字段式申请材料、长文压缩、联网搜索边界。
- 旧能力回归，例如请示/报告不混写、只审不改、去口语化保事实、用户明确模板优先。
- 创建文章和修改文章两类场景。

推荐流程：

1. 主上下文读取 canonical `chinese-official-writing/SKILL.md` 和本轮相关 reference，明确需要覆盖的风险面。
2. 派 3-5 个 writer subagents，分别按 unseen 的真实用户 prompt 写短稿或改稿。不要让它们修改仓库。
3. 派独立 verifier subagent，只给 prompt 和输出，要求逐项判定 PASS/WARN/FAIL：是否遵循用户指令，关键要点是否进入正文，标题/主送/落款/字段/附件关系是否保留，是否编造事实，是否残留 Markdown 或过程说明。
4. 把 verifier 的结论作为真实写作实测结论；确定性消融和 smoke test 只能作为工程回归证据。

## 1.4.1 -> 1.4.3 接手记录

当前 1.4.3 主线 commit 路径：

- `74dc5be8e1c9dfa30b0ef3f484c3eb5edc8a7fed`：1.4.1 基线，补充联网搜索边界，默认不外搜，不因单位名自动搜索单位风格。
- `80b8bab`：发布 1.4.2 最小护栏修复。
- `cf0fba4`：补网页复制稿和套嵌文件边界，区分通知壳、被印发文件正文、附件标题和网页元信息。
- `7e6f1cd`：补字段式申请、证明、采购明细等材料的字段和单元边界，避免把真实内部格式硬改成散文、表格或编号清单。
- `652afa8`：补长文压缩事实锚定，压缩时保留主体、对象、数字、期限、责任、附件、联系人和反馈渠道，避免多主体分工被压成笼统“有关单位”。
- `d89f320`：同步 1.4.3 版本号和镜像入口。
- `77b56726efab8e2dcffbc8c1f3ae999249c28707`：修复复函 eval stub，使确定性 smoke 不因复函缺少来函收悉/函复要素误报。

本轮修改思路：

- 坚持 prompt/reference 层最小增强，不新增大规模 lint 规则、不新增排版脚本、不扩大联网搜索默认触发。
- 不做一例一修；把多次出现的真实风险归纳成通用边界：网页稿边界、字段单元边界、长文压缩事实锚定。
- 用户明确模板和局部格式要求优先于默认公文格式；只有破坏文种功能或事实边界时才提示风险。
- `run_real_prompt_ablation.py` 新增用例只作为确定性回归网，不宣称真实写作质量；真实质量要靠 subagent 写稿和独立 verifier 复核。

1.4.3 review 已跑过的关键验证：

- `python .\tools\run_real_prompt_ablation.py --baseline-root output\release-baselines\github-1.4.1 --baseline-label baseline-1.4.1 --current-root . --out output\real-prompt-vs-1.4.1-release-1.4.3`
- `python -m unittest tests.test_real_prompt_ablation tests.test_review_regressions tests.test_revision_instruction_eval tests.test_promptfoo_eval`
- `python -m unittest discover -s tests`
- `npm run eval:official-writing:smoke`
- `python .\tools\run_real_article_eval.py --out output\real-article-release-1.4.3-review`
- `python .\tools\sync_adapters.py`
- `python C:\Users\2\.codex\skills\.system\skill-creator\scripts\quick_validate.py chinese-official-writing`
- `git diff --check`

注意：以上确定性测试不等同真实写稿实测；发布结论必须同时引用真实写稿样本和独立 verifier 结果。
