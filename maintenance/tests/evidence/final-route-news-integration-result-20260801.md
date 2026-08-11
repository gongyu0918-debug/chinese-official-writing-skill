# 核心路由去重与新闻两叶最终组合验证

日期：2026-08-01

## 组合范围

- 起点：本地 `main` 的 `da8264c55d387683da42964214dcd7ee0d0e5e18`。
- 新闻消息、新闻评论组合产品：`48ad823eb70033bb729a3d3e115721ebd05f935f`。
- 核心路由去重组合产品：`e66ff437b21fca59191e248a72a467425832c151`。
- 核心路由部分只移植 `dcfe62b4` 的产品 diff：六个 `SKILL.md` 镜像及对应 boundary tests；未带入预注册、旧工程记录或其他 Prompt 调整。
- 保留新闻评论优先于混合消息标签的组合规则、两份新闻叶正文和本地 main 已验证的入口减负三原子；未改版本号、发布链或叶正文。

## 路由与信息完整性

- 核心流程不再逐项枚举会议纪要、报告、请示、函、通用 playbook 和 AI 算力等旧叶名，改为轻量卡早停或按 reference 表实际命中项加载。
- 当前 canonical `SKILL.md` 为 10518 字符；相对 `da8264c5` 减少 286 字符，相对发布产品 `v1.5.31=e8c077cb` 减少 767 字符。新闻两叶新增入口与表项抵消了部分核心段减载，因此相对 `da8264c5` 的净减载小于核心路由原子本身。
- 核心流程区块为 1257 字符，七个旧叶文件名命中数为 0。
- reference 表核验的 11 项主要文种/专项叶全部存在，缺失数为 0；其中包含新闻消息、新闻评论、会议纪要、报告、请示、请示审核、普通函、通用文种、制度、通用检查和 AI 算力叶。

## 核心路由真实 A/B 摘要

- CRD01：Candidate 与 Baseline 都读取 `SKILL.md`、`information-selection.md`、`task-route-cards.md`，路由集合对称。
- CRD02：两臂都读取入口、信息选择、轻量卡和会议纪要叶，路由集合对称。
- CRD03：两臂均命中 AI 算力叶和请示叶；Candidate 还读取办理要素、终稿复核与校对等完整流程叶，Baseline 未记录这三项，因此该题不具备完全对称的 reference 集合。
- 六份成稿均未发现事实、数字、日期、主体、状态、文种、输出范围或保护性外扩方面的硬边界缺失。
- CRD03 Candidate 的篇幅记录为 710；Baseline 在既有记录中出现 905 与 932 两种统计口径，932 为回执口径。计量口径不完全一致，加之每臂仅一次输出，该差异只作为一次篇幅观察。
- 结论：技术路由证据为 `ROUTE MIXED`，原因是 CRD03 两臂加载集合不完全对称；因果判定为 `CAUSAL PASS / MERGEABLE`。没有证据显示核心路由去重漏掉应命中叶，CRD03 的单次篇幅差异不能归因于产品 diff。

## 最终组合工程验证

- focused：`python -m unittest tests.test_promptfoo_eval.PromptfooProviderTests tests.test_skill_boundary.SkillBoundaryTests`，124/124 通过。
- 全量：`python -m unittest discover -s tests`，404/404 通过。
- Promptfoo smoke：`npm run eval:official-writing:smoke`，20/20 通过，0 failed，0 errors，judge consistency 1.0。
- 固定基线消融：`python tools/run_real_prompt_ablation.py --baseline-root F:\\Workspaces\\chinese-official-writing-skill\\output\\release-baselines\\v1.5.31-e8c077cb-news-message --baseline-label v1.5.31-e8c077cb --current-root . --out output\\final-news-route-integration-ablation-20260801`，baseline 110/110、current 110/110。
- `python tools/sync_adapters.py` 后无内容漂移；CRLF 状态经重新暂存后工作树干净。
- `python C:\\Users\\admin\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py chinese-official-writing`：`Skill is valid!`。
- `git diff --check` 通过。

## 结论与剩余风险

最终组合达到本地合并候选条件：既有公文路由和工程回归无回退，新闻两项新增功能保留，核心入口获得可验证净减载。剩余风险仍为新闻评论偶发状态强度漂移、新闻消息或评论的篇幅波动，以及 CRD03 单次篇幅未达目标；这些均未建立与本次 diff 的稳定因果关系，继续按正常样本共性门观察。本分支未合并 main、未推送、未发布。
