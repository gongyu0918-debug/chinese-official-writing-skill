# 新闻消息与新闻评论叶组合验证

日期：2026-08-01

## 范围

- 基线：本地 `main` 的 `da8264c55d387683da42964214dcd7ee0d0e5e18`。
- 产品来源：新闻消息 `63aea451`、新闻评论 `b3aca673`。
- 只移植两份专项叶、入口别名与直达路由、provider 路由和必要测试；未移植负向收缩实验 `b9a24c5f`，未带入旧研究记录。
- 两份叶正文保持各自产品提交内容不变；版本号、发布链和现有入口减负三原子保持不变。

## 组合冲突

两个独立产品原有测试对“新闻消息 + 新闻评论”混合标签给出了相反优先级。组合后按体裁特异性处理：明确出现新闻评论、时评或评论员文章时读取评论叶；纯新闻稿、消息、快讯和活动报道读取消息叶。provider 先判断评论别名，再判断消息别名，并新增顺序无关的组合回归测试。未修改两份叶正文，也未新增第三套写作规则。

## 工程验证

- focused：`python -m unittest tests.test_promptfoo_eval.PromptfooProviderTests tests.test_skill_boundary.SkillBoundaryTests`，124/124 通过。
- 全量：`python -m unittest discover -s tests`，404/404 通过。
- Promptfoo smoke：`npm run eval:official-writing:smoke`，20/20 通过，0 failed，0 errors，judge consistency 1.0。
- 固定基线消融：`python tools/run_real_prompt_ablation.py --baseline-root F:\\Workspaces\\chinese-official-writing-skill\\output\\release-baselines\\v1.5.31-e8c077cb-news-message --baseline-label v1.5.31-e8c077cb --current-root . --out output\\news-leaves-integration-ablation-20260801`，基线 110/110、current 110/110。
- 快速校验：`python C:\\Users\\admin\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py chinese-official-writing`，`Skill is valid!`。
- 镜像：运行 `python tools/sync_adapters.py` 后无未暂存差异；canonical 与五个发行镜像同步。
- `git diff --check` 通过。

## 真实写作证据校准

- 新闻消息：两个 Candidate 专属运行均实际读取消息叶，事实、数字、主体分工、状态、体裁、输出范围、P0 和直接使用成本通过。
- 新闻评论：专项叶能够独立形成观点前置、事实支撑和评论推演。NCF01 同题三次首稿中两次保持“将调整/将增加”，一次写成“已调整/已增加”；该单稿有真实状态错误，但复现率为 1/3，未形成三个正常场景的共性风险，也没有证据表明由叶子 diff 诱发。按因果口径记为生成波动和已知风险，不据此否决新增功能或追加特例 Prompt。
- 篇幅偏短或偏长单独记录，不作为功能阻断；两类叶均已达到绝对可用门。

## 结论与风险

组合工程门通过，两类新增功能可进入 main 的合并候选。已知风险为新闻评论偶发状态强度漂移和篇幅偏长、新闻消息偶发低于目标篇幅；后续应在正常使用样本中继续观察，达到共性门后再做机制修复。本分支未推送、未发布、未改版本号、未合并 main。
