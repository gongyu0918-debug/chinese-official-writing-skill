# Candidate Direct Fact State 预注册

日期：2026-07-29

## 研究对象

- 固定基线：`v1.5.28=f7570d4df5064582946732d283d30e86063ef142`。
- 研究分支：`codex/candidate-direct-fact-state-v1528`。
- 性质：纯 Prompt 单变量研究候选，不改版本号，不合并，不发布。
- 目标：降低已选事实后继续追加材料充分性评价、无锚定否定、自证边界和外围未决回卷的概率；目标是把 P0 风险控制在可发现、可局部修改的范围，不要求消除全部风险。

## 因果假设

现有 `information-selection.md` 已规定信息是否进入正文及其去向，但始终加载的正向规则没有明确选入信息的直接表达方式。模型可能在事实或状态之后继续评价材料是否充分、结论是否成立或事项是否意味着其他结果。

本候选只补一个正向表达原子：

> 已选入正文的事项，直接陈述该事项已给的业务事实和当前状态。

该句只约束同一事项的落笔方式，不授权跨章节复用事实，不授权补原因、措施、程序、关系、承诺或篇幅。

## 精确 diff 计划

1. 只修改 canonical `chinese-official-writing/references/information-selection.md` 第 1 条，在“事实之间的时间、因果和归属关系以材料明确关系为准”之后追加上述一句。
2. 运行 `tools/sync_adapters.py`，仅把同一内容同步到发行镜像。
3. 不修改 `SKILL.md`、文种叶、`anti-ai-patterns.md`、`final-review-layers.md`、篇幅规则、段内公式、脚本、正则、FSM、回退逻辑、输出模式、版本号或发布文件。

## 工程验证

- `python -m unittest discover -s tests`
- `npm run eval:official-writing:smoke`
- `python tools/run_real_prompt_ablation.py --baseline-root <v1.5.28固定工作树> --baseline-label v1.5.28 --current-root . --out <隔离输出目录>`
- `python <skill-creator>/scripts/quick_validate.py chinese-official-writing`
- canonical 与发行镜像哈希一致性检查
- `git diff --check`

工程门失败即停止，不进入真实写稿。

## 真实 A/B 预注册

只使用自然任务，不在 Prompt 中写入 P0 风险词、候选机制、目标答案或诱导性禁令。Candidate 与固定 v1.5.28 使用同模型、同 thinking、逐字一致原始输入，各取首个技术有效输出；writer 与匿名 verifier/judge 分离。

### S15：长篇工作总结

- 复用既有 S15 原始任务。
- 检查：材料充分性评价、无锚定否定、自证边界、外围未决回卷、跨事项关系、事实和篇幅。

### C01：进行态控制题

- 复用 1.5.19 的日常供餐异常通报任务；材料明确“正在核查原因”和“核查完成后通报结果”。
- 检查：必要进行态和既有后续动作是否完整保留，是否被压掉、弱化或改成额外边界说明。

## 验收

两题都必须满足：

1. 无 Candidate 独有的事实、数字、日期、主体、状态、文种、格式、篇幅或输出模式硬回退。
2. S15 的 P0 簇数或直接修改成本低于基线，C01 不得丢失材料明确的进行态和后续动作。
3. 不因该句明显加重短写、提纲化、同义复述、统计工程化或跨事项关系联想。

结果：

- `PASS`：两题均无硬回退，S15 有明确正向，保留候选等待扩大验证。
- `MIXED`：有正向也有回退；保持隔离，不追加同义规则。
- `FAIL`：无可见正向或出现事实、状态、关系、篇幅硬回退；冻结候选。
