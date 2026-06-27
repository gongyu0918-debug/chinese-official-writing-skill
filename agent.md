# AI 味与查重 Round 1 记录

日期：2026-06-27

## 基线

- GitHub 仓库：`gongyu0918-debug/chinese-official-writing-skill`
- 测试基线：`origin/main`
- 本地测试分支：`codex/ai-dedupe-round1-20260627`
- 基线 commit：`874ed1d docs: remove chatbot prompt-only routing`
- 对齐验证：`git rev-list --left-right --count origin/main...HEAD` 输出 `0 0`
- 旧本地 main 已保存：`codex/local-main-backup-20260627`
- ClawHub live：`clawhub inspect chinese-official-writing --json` 显示 latestVersion `1.4.8`，moderation `clean`，downloads `1796`

本轮不修改 skill 规则，只做第一轮基线测试和流程记录。

## 执行约束

1. 所有测试以 GitHub `origin/main` 最新 commit 为主，不以本地旧分支、ClawHub 缓存页或未同步副本为准。
2. 测试样稿由 subagent 生成或复核；主线程只汇总、交叉验证和记录。
3. 修复门槛按“三轮以上共性问题”执行：同一问题只在一轮内出现三份样稿，不足以直接修复；需在后续 Round 2、Round 3 中继续复现，或累计三轮明确同类问题后才进入最小修复。
4. 每次修复前固定上一轮为基线，修复后跑消融；消融、smoke 或最小验证不通过则回滚该次修改。
5. 测试工具集中到 `evals/ai-dedupe/` 管理；临时样稿、依赖、模型和输出放在 `output/ai-dedupe-roundN/`，不提交。
6. 工具优先级：agent skill > 不用 API 的本地开源工具 > 需要 API 的外部工具。
7. 使用外部 API 前必须记录样稿是否外发、脱敏方式、接口名称和失败处理；默认不把未脱敏测试数据发给第三方。

## 轻量 review 结论

独立 explorer 和本地主线程交叉验证后，发现 GitHub main 当前存在以下既有问题：

- `.qwen/skills/chinese-official-writing/agents/openai.yaml` 工作区行尾为 CRLF，canonical `chinese-official-writing/agents/openai.yaml` 为 LF；`tests.test_skill_boundary` 的字节级镜像测试因此失败。
- `tests/evidence/real-writing-1.4.8.md` 的回归摘要粒度偏粗，没有保留 prompt、样稿和逐项 verifier 细节。
- `tests/evidence/real-writing-1.4.8.md` 写“完整单测：84 项通过”，当前 `rg "^    def test_" tests` 统计为 `85`。
- 旧证据中 `expanded-ablation-summary.md` 和 `agent-public-ablation-summary.md` 对 C 轮评估 `7/9` 与 `9/9` 的口径不一致。

这些是基线记录，不属于本轮 AI 味/查重修复对象。

## 工具候选

### Agent skill / 平台候选

- SkillHub `AI味` 搜索：`total=82`。高下载候选包括 `unclecheng-reduce-ai-perception-v2`，downloads `17392`，stars `100`；`unclecheng-reduce-ai-perception`，downloads `4799`，stars `15`。
- SkillHub `查重` 搜索：`total=33`。候选包括 `paper-checker`，downloads `1340`；`tender-similarity-analyzer`，downloads `400`；`boo-check-review`，downloads `153`。
- SkillHub `AIGC` 搜索：`total=49`。企业候选包括 `tencentcloud-aigc-recog-text`，downloads `967`，requires_api_key `true`。

平台 skill 候选只作为测试器或检查维度来源，不复制实现。

### 不用 API 的开源候选

- `fxsjy/jieba`：GitHub stars `35034`，Python，pushed `2024-08-21`，用于中文分词。
- `shibing624/text2vec`：GitHub stars `4971`，Python，pushed `2026-02-14`；Hugging Face `shibing624/text2vec-base-chinese` downloads `1625149`，中文 sentence-similarity。
- `Hello-SimpleAI/chatgpt-comparison-detection`：GitHub stars `1391`，Python；Hugging Face `Hello-SimpleAI/chatgpt-detector-roberta-chinese` downloads `2190`，中文 text-classification。
- `1e0ng/simhash`：GitHub stars `1037`，Python，用于近重复检测。

本轮实际运行：`jieba`、`simhash`、`scikit-learn` TF-IDF/cosine 和仓库自带 `prose_lint.py`。`text2vec` 依赖已安装到 `output/ai-dedupe-round1/deps`，但未下载模型权重，未把它当作已运行语义模型结果。

## Round 1 样稿测试

样稿来源：3 个 writer subagent，各自只读 GitHub main 版本 skill，生成 T01/T02/T03 三类输出，共 9 份。临时样稿保存在 `output/ai-dedupe-round1/samples.json`。

任务覆盖：

- T01：政务数据共享情况自查通知，要求对象、时限、反馈邮箱、联系人，缺政策依据不得编造。
- T02：把“我们检查了系统，发现日志备份不及时，后面继续盯。”改成正式报告语气，不得新增事实。
- T03：只审 AI 味和空话套话，不重写全文。

独立 verifier 结论：

- T01：`R1-C-01` 编造具体截止日期、邮箱、联系人和科室，判为 FAIL；`R1-A-01` 自行设置“5个工作日内”，判为 WARN；`R1-B-01` 没有编造，但正文未写明三项，只在补充信息里提示，判为 WARN。事实边界问题本轮未达到三份共性，但风险高，进入后续观察。
- T02：三份均 PASS，未见明显新增事实。
- T03：三份均 PASS，但 verifier 认为审稿维度和措辞组织高度相近，存在同质化风险。该问题本轮 count=3，只作为 Round 1 观察项，不能直接修复；需后续两轮继续验证。

本地软件扫描：

- `prose_lint.py --format --structure`：仅发现 low 级 western-bullet 和 `闭环` 术语重复；无 medium/high AI 味风险。
- `jieba + simhash`：T03 三对距离为 `17 / 25 / 24`，未达到逐字近重复级别。
- `jieba + TF-IDF cosine`：T03 三对相似度为 `0.6227 / 0.3619 / 0.3579`；T01 最高为 `0.7370`，T02 A/C 为 `0.7597`。这些说明固定短任务会有词面重合，但不等同抄袭。

Round 1 判断：不修复。继续 Round 2、Round 3，用不同 prompt 和独立 verifier 观察 T03 审稿同质化、T01 缺事实时补造日期/联系人风险是否稳定复现。

## Round 2 生成-评审测试

本轮按“写作 skill 生成 -> 反 AI 味 skill 评审”的闭环做，只读测试，不修改 skill。严格说，这不是完整 A/B 测试；完整 A/B 应比较“当前 skill 与上一轮/修复前 skill”或“skill 与 no-skill baseline”。本轮目标是发现当前写作 skill 生成稿中的 AI 味、模板化和事实边界顽疾。

基线核对：

- `git fetch origin` 成功。
- `origin/main` 仍为 `874ed1d docs: remove chatbot prompt-only routing`。
- 当前分支相对 `origin/main` ahead 1，仅多本记录文件；`git diff --stat origin/main -- chinese-official-writing skills openclaw hermes .qwen .agents` 无输出，说明 skill 内容仍等同 GitHub main。

生成方式：

- writer subagent 加载 `F:\Workspaces\chinese-official-writing-skill\chinese-official-writing`。
- 生成 6 篇样稿，覆盖通知、情况报告、内部申请、方案正文、AI 算力服务租赁需求说明、会议讲话稿开头。
- 样稿临时保存：`output/ai-dedupe-round2/samples.json`。

反 AI 味评审方式：

- verifier subagent 加载本地 `talk-normal` skill 作为反 LLM 腔规则参考。
- verifier 只看“原 prompt + 样稿”，不看主线程预设结论，不改稿。
- 输出 PASS/WARN/FAIL、AI 味分、查重/模板风险、事实边界和证据短语。

### verifier 结果

| 样稿 | 结论 | AI 味 | 同质化/模板风险 | 事实边界 | 主要问题 |
| --- | --- | ---: | ---: | --- | --- |
| R2-W1-01 通知 | PASS | 1 | 1 | PASS | 缺项已放正文后提示，未编日期、邮箱、联系人；少量常规通知语可接受。 |
| R2-W1-02 情况报告 | WARN | 0 | 0 | WARN | 末段补入“后续将结合系统运行情况”“继续关注……”等未给出的后续安排。 |
| R2-W1-03 内部申请 | PASS | 1 | 1 | PASS | 未编供应商、审批人、财务科目；采购用途轻度概括但可接受。 |
| R2-W1-04 方案正文 | PASS | 0 | 1 | PASS | 无口号式结尾；末句用途收束轻微但未明显新增事实。 |
| R2-W1-05 算力租赁需求 | PASS | 1 | 1 | PASS | SLA、并发、安全、验收覆盖完整；表达偏清单化但信息密度足够。 |
| R2-W1-06 讲话稿开头 | WARN | 1 | 1 | WARN | “近期从办文、审稿和流转情况看”等观察来源未给，事实边界略不稳。 |

共性问题：

- medium：为增强完整性补入未给出的后续动作、近期观察或背景判断，count=2，样稿 `R2-W1-02`、`R2-W1-06`。
- low：个别文本仍有公文常用收束句和清单化表达，count=3，样稿 `R2-W1-01`、`R2-W1-04`、`R2-W1-05`；未达到明显 AI 腔或不可交付程度。

### 本地软件扫描

- `prose_lint.py --format --structure`：仅 `R2-W1-01` 有 4 个 low 级 `western-bullet`；其余样稿 0 finding。无 medium/high AI 味风险。
- `jieba + simhash`：跨 6 篇样稿两两距离最低为 `23`，未见近重复。
- `jieba + TF-IDF cosine`：跨样稿最高为 `0.1726`，未见跨文种查重风险。
- `char_jaccard`：最高为 `0.3418`，主要来自同一政务数据主题词，不构成抄袭或高同质化。

Round 2 判断：不修复。R2 未复现 R1 的“审稿输出同质化”场景，因为本轮主要生成正文；但 R2 与 R1 共同指向事实边界问题：模型为了成稿完整度，容易补入未给出的时限、联系人、后续安排或近期观察。该问题已出现两轮，但尚未满足“三轮以上共性问题”修复门槛，进入 Round 3 重点观察。

## 测试反馈修复 loop

建议把后续工作固定为一个工程 loop：

1. **Test / 生成**：用当前 GitHub main 的 `chinese-official-writing` 生成 6-10 篇真实任务样稿，覆盖缺事实、改写、审稿、方案、讲话和技术材料。
2. **Review / 评审**：用反 AI 味或去重 skill 的独立 subagent 审核，只提供 prompt 和样稿，输出 PASS/WARN/FAIL、证据短语和共性统计。
3. **Record / 记录**：把样稿、评审 JSON、本地扫描结果放 `output/ai-dedupe-roundN/`，把摘要和共性问题写入 `agent.md`。
4. **Gate / 门禁**：只有同类问题跨三轮以上复现，才进入修复候选；单轮或两轮问题只观察。
5. **Fix / 修复**：对已达门槛的问题做最小 skill 改动，不扩大默认联网、不新增硬禁词、不改成聊天化风格。
6. **A/B 消融**：用上一轮样稿和新样稿比较“修复前 skill vs 修复后 skill”。必须验证事实边界、AI 味、查重/同质化指标没有退化。
7. **Rollback / 回滚**：消融、smoke 或最小验证失败，则撤销此次修复，只保留失败记录。

## Round 3 goal 模式提示词

目标：继续对 GitHub `origin/main` 版本 `chinese-official-writing` 做 Round 3 生成-评审测试，重点验证事实边界顽疾是否跨三轮成立，并补足真正的 A/B 消融设计。先只读测试，不修 skill。

执行要求：

1. 先 `git fetch origin`，确认 skill 目录相对 `origin/main` 无差异；如果当前分支有记录提交，只要 `git diff --stat origin/main -- chinese-official-writing skills openclaw hermes .qwen .agents` 为空，即可视为 GitHub main skill 基线。
2. 读取 `AGENTS.md`、`agent.md`、`evals/ai-dedupe/README.md`，遵守“生成 -> 评审 -> 记录 -> 累计 -> 修复 -> 消融 -> 回滚”的 loop。
3. 创建 `output/ai-dedupe-round3/` 存放临时样稿、verifier 结果和本地扫描结果；不提交 output。
4. 让 writer subagent 加载 `chinese-official-writing` skill 生成 6-10 篇样稿，prompt 必须重点覆盖：
   - 缺截止时间、邮箱、联系人、政策依据；
   - 原文只给问题但未给后续安排；
   - 讲话稿或报告未给“近期观察来源”；
   - 用户明确要求不要补事实；
   - 去 AI 味但保持公文正式语气。
5. 让 verifier subagent 加载反 AI 味/去模板化 skill 审核，只给原 prompt 和样稿，输出 PASS/WARN/FAIL、AI 味分、事实边界、查重/模板风险和证据短语。
6. 本地扫描至少跑 `prose_lint.py --format --structure`、`jieba+simhash`、`jieba+TF-IDF cosine`；如使用模型或 API，记录是否本地运行、是否下载权重、是否外发文本。
7. 统计 R1/R2/R3 三轮共性问题。若“为完整度补入未给事实/后续安排/近期观察”第三轮仍复现，才拟定最小修复方案。
8. 本轮仍不修 skill。若用户明确要求进入修复阶段，先固定 R2/R3 样稿为 A/B 消融集，再做最小改动。
9. 交付报告必须包含：生成样本数、verifier 结论表、共性问题、是否达到三轮门槛、本地扫描结果、未运行项、下一步修复/消融计划。

## 已运行验证

- `git fetch origin`：成功，`origin/main` 更新到 `874ed1d`。
- `git rev-list --left-right --count origin/main...HEAD`：`0 0`。
- `python -m unittest tests.test_skill_boundary -q`：失败 1 项，原因是 `.qwen/.../agents/openai.yaml` CRLF/LF 字节不一致。
- `npm run eval:official-writing:smoke`：失败，promptfoo provider 报 `Python 3 not found`，属于环境路径问题，非样稿质量结论。
- `C:\Users\admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe evals\official-writing\run_eval.py --suite smoke --judge-batch-size 2`：同样失败在 promptfoo provider 的 Python 路径识别。
- 提权并把 `TEMP/TMP` 指到 repo 内后运行：`python -m unittest tests.test_review_regressions tests.test_real_prompt_ablation tests.test_revision_instruction_eval tests.test_promptfoo_eval -q`，57 项通过。

## 下轮 goal 模式提示词

目标：基于 GitHub `origin/main` 最新 commit 对 `chinese-official-writing` 做 Round 2 AI 味和查重基线测试，不修改 skill 规则，继续观察 Round 1 中的 T03 审稿同质化和 T01 事实边界风险。

执行要求：

1. 先 `git fetch origin`，确认 `HEAD` 与 `origin/main` 对齐；若本地分支分叉，先保护本地 HEAD，再基于 `origin/main` 建测试分支。
2. 读取 `AGENTS.md`、`agent.md` 和 `evals/ai-dedupe/README.md`，按本轮约束执行。
3. 测试工具集中使用 `evals/ai-dedupe/`，临时样稿和依赖只放 `output/ai-dedupe-round2/`。
4. 工具优先级：先用 agent skill 或 subagent 审查；再用不用 API 的本地工具；最后才考虑需要 API 的工具。不得把未脱敏样稿发给外部 API。
5. 让至少 3 个 writer subagent 基于 GitHub main skill 生成新样稿，prompt 不得与 Round 1 完全相同，但必须覆盖：
   - 缺时限、邮箱、联系人、政策依据时是否编造；
   - 只审 AI 味/空话套话时是否输出同质化审稿模板；
   - 正式化改写是否新增原文外事实。
6. 再让独立 verifier subagent 只看“原 prompt + 样稿”，输出 PASS/WARN/FAIL 和三轮共性问题统计；不要泄露主线程预设结论。
7. 软件扫描至少跑 `prose_lint.py`、`jieba+simhash` 和 `jieba+TF-IDF cosine`；如使用 `text2vec` 或 Hello-SimpleAI 模型，必须记录模型是否本地运行、是否下载权重、是否外发文本。
8. 只记录问题，不修复。除非某个问题已经跨三轮累计复现并达到修复门槛，否则不得改 skill。
9. 若后续进入修复阶段，每次只做最小改动；修复后必须与上一轮输出做消融，消融不通过立即回滚此次修改。
10. 交付时报告：基线 commit、样本数、工具、测试结果、三轮共性状态、未运行/失败原因、剩余风险。
