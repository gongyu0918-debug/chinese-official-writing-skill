# Candidate：请示/申请细查叶预注册

## 固定基线

- 当前 main：`8e4721b031422b691e8c9780a9f821a944e68526`
- 1.5.25 产品提交：`776a32e60f7bb0afe37f439b2710b6d0b43d40e8`
- 候选分支：`codex/1.5.26-candidate-request-review-leaf-v1525`
- 候选 worktree：`output/research-worktrees/candidate-request-review-leaf-v1525`

## 单一变量

将 `references/genre-checklist.md` 中现有的“请示”和“申请”细查小节原样迁入新的 review-only 叶。请示、申请起草仍只走已经验证的 `genre-playbook-request.md`；只有用户要求审稿、复核、文种细查或同时要求审后改写时，才读取新叶。

本候选不新增写作规则，不改请示、申请的起草骨架，不改变信息选择、事实边界、文种判断、用户模板、篇幅预算、三级复核、修改次数、回退方式、Word 交付或发布链。

## 精确 diff 计划

1. 新建 `references/genre-checklist-request.md`，承载 `genre-checklist.md` 现有“请示”和“申请”小节。
2. 从 `genre-checklist.md` 删除上述两个小节，其他文种原文和顺序保持不变。
3. 在 `SKILL.md` 的文种细查路由、reference 表和脚本后人工复核说明中增加请示/申请细查叶指针；请示、申请起草继续指向 `genre-playbook-request.md`。
4. 更新确定性测试和 Promptfoo provider，使 review-only 的请示/申请测试能够加载新叶；不借此调整其他起草路由。
5. 使用 `tools/sync_adapters.py` 同步发行镜像，不手工制造平台差异。

## 加载对照

| 任务 | 1.5.25 | Candidate |
| --- | --- | --- |
| 请示/申请起草 | `SKILL.md` + `genre-playbook-request.md` | 不变 |
| 请示/申请文种细查 | `SKILL.md` + `review-checklist.md` + 全量 `genre-checklist.md` | `SKILL.md` + `review-checklist.md` + `genre-checklist-request.md` |
| 其他文种细查 | 全量 `genre-checklist.md` | 删除请示、申请小节后的 `genre-checklist.md` |

## 不修改的文件和能力

- 不修改 `genre-playbook-request.md`、`information-selection.md`、`workflow.md`、`handling-elements.md`、`argument-chains.md`、`anti-ai-patterns.md`、`final-review-layers.md`、`proofreading-checklist.md`。
- 不修改检测脚本、正则、Hook、FSM、标记协议和终稿回退逻辑。
- 不修改版本号、README、发布说明、平台适配策略或线上包。
- 不修改通知、函、复函、纪要、报告、制度等其他文种规则。

## 工程验证

依次运行：

1. `python -m unittest discover -s tests`
2. `npm run eval:official-writing:smoke`
3. `python tools/run_real_prompt_ablation.py --baseline-root <1.5.25-product> --baseline-label 1.5.25 --current-root . --out <candidate-output>`
4. `python tools/sync_adapters.py` 后核对 canonical 与各镜像一致
5. `python <skill-creator>/scripts/quick_validate.py chinese-official-writing`
6. `git diff --check`

工程验证失败时停止真实测试。

## 真实 A/B 预注册

固定 Candidate 与 1.5.25 产品提交，使用同一模型、同一 thinking、逐字一致的自然语言原始任务，各取首个技术有效输出，不补写目标答案或候选机制。

1. R01：内部费用申请审稿，只列位置、风险层级和修改建议，保留用户两行标题、称呼和落款习惯。
2. R02：正式请示审稿，检查一文一事、请批事项、依据、金额和请批语，不改写全文。
3. R03：请示审后直接改稿，完整保留数字、主体、请批事项和成文日期，输出可直接使用正文。

writer、硬边界 verifier 和匿名 judge 相互独立。三题均不得出现 Candidate 独有的事实、数字、日期、主体、状态、文种、格式、输出模式或 P0 回退；至少一题 Candidate 明确胜出，其余不败，才保留产品提交。

若仅有一题出现软性观感负项且没有硬回退，可对同题按原条件预注册补一对噪声复验；复验仍负则冻结候选，不追加 Prompt、不修改测试题。

## 后续边界

本候选通过只证明请示/申请细查叶具备保留资格。AI 专项迁移、工作总结叶和其他 reference 拆分必须各自建立独立 worktree、预注册和真实 A/B，不与本候选组合归因。
