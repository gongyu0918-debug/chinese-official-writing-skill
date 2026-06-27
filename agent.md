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
