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

## Round 3-10 生成-评审 loop

本轮目标是把前两轮结论延伸为 10 轮工程 loop：继续以 GitHub `origin/main` 的 skill 本体为基线，新增 8 轮，只读生成与评审，先统计三轮以上共性问题，再进入最小 md prompt 修复。

基线核对：

- `git fetch origin` 成功。
- `origin/main` 为 `874ed1d docs: remove chatbot prompt-only routing`。
- 当前分支仅多测试记录和工具提交；`git diff --stat origin/main -- chinese-official-writing skills openclaw hermes .qwen .agents` 在修复前无输出，说明测试基线仍是 GitHub main skill 本体。

生成方式：

- Round 3-10 共 8 轮，每轮 5 篇，新增 40 篇样稿。
- writer subagent 均加载 `.agents/skills/chinese-official-writing/SKILL.md`。
- 覆盖通知、报告、请示、函、批复、方案、会议材料、AI 算力需求、压缩、顺稿、网页清理、审稿和多材料合稿。
- 样稿保存于 `output/ai-dedupe-round3/` 至 `output/ai-dedupe-round10/`，`output/` 不提交。

反 AI 味评审方式：

- 两个 verifier subagent 加载本地 `talk-normal` skill。
- Verifier A 评审 R3-R6，Verifier B 评审 R7-R10。
- verifier 只看 prompt + output，不看主线程预设结论，不改稿。

### 本地软件扫描

本轮统一使用 `evals/ai-dedupe/local_scan.py`，该脚本调用本仓库 `prose_lint.py`，并用纯本地 char 3-gram SimHash、TF-IDF cosine、Jaccard 计算跨样稿相似度。脚本只记录风险，不作为硬门禁。

| 轮次 | 样本数 | lint 总数 | 单篇最高 lint | 最小 SimHash 距离 | 最高 TF-IDF | 最高 Jaccard |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| R3 | 5 | 9 | 4 | 27 | 0.0479 | 0.0475 |
| R4 | 5 | 7 | 4 | 26 | 0.0178 | 0.0167 |
| R5 | 5 | 4 | 4 | 21 | 0.0924 | 0.0582 |
| R6 | 5 | 0 | 0 | 25 | 0.0636 | 0.0495 |
| R7 | 5 | 5 | 3 | 25 | 0.0218 | 0.0219 |
| R8 | 5 | 0 | 0 | 26 | 0.0175 | 0.0146 |
| R9 | 5 | 24 | 11 | 28 | 0.0507 | 0.0512 |
| R10 | 5 | 14 | 9 | 28 | 0.0257 | 0.0238 |

本地扫描判断：

- 未发现跨样稿近重复。8 轮最高 TF-IDF 为 `0.0924`，最高 Jaccard 为 `0.0582`，SimHash 最小距离为 `21`。
- R9、R10 lint 总数高，主要来自审稿样本主动引用“AI 味”、模板词、编号结构和空话词，不直接等同正文生成失败。
- `local_scan.py` 试跑时发现 Windows `tmp` 临时目录权限问题，已改为直接导入 `prose_lint.py` 的 `scan()` 函数，不再写临时草稿文件。

### verifier 共性问题

| 问题类别 | 新增轮次证据 | 严重度 | 判断 |
| --- | --- | --- | --- |
| 事实或动作轻微外扩：为完整性补入未给出的具体场景、责任安排、处置过程、实施步骤、后续动作、影响或效果判断 | Verifier A count=6，证据 `R3-W1-03`、`R5-W1-02`、`R5-W1-03`、`R6-W1-02`、`R6-W1-03`、`R6-W1-05`；Verifier B count=10，证据 `R7-W1-01`、`R7-W1-02`、`R7-W1-05`、`R8-W1-01`、`R8-W1-05`、`R9-W1-01`、`R9-W1-02`、`R9-W1-03`、`R10-W1-01`、`R10-W1-04` | medium | 与 R1、R2 的事实边界问题同类，已超过三轮门槛，进入最小 md prompt 修复。 |
| 缺项提示或说明性尾巴近似重复 | Verifier A：固定缺项句式 count=4，自证式尾句 count=2；Verifier B：说明性尾巴/缺项提示 count=8 | low | 已超过三轮，适合做轻量软化；保留正文外缺项提示，不新增硬门禁。 |
| 审稿输出结构同质化 | R1 已观察到 T03 同质化；Verifier A count=3，证据 `R4-W1-01`、`R4-W1-02`、`R4-W1-05`；Verifier B count=3，证据 `R8-W1-04`、`R9-W1-05`、`R10-W1-05` | low | 已超过三轮，但多为审稿类可读结构相近；只做提示层软化，避免把审稿输出改散。 |
| 模板腔或口号式收束残留 | Verifier A count=4，Verifier B count=5 | low | 已超过三轮，纳入同一最小 prompt 修复，要求收束优先落到已给对象、动作和事实。 |
| 相对时间处理风险 | Verifier B count=2，证据 `R8-W1-03`、`R9-W1-01` | low | 未达到三轮门槛，不单独修复。 |
| 严格删除/清理任务过度改写 | Verifier A count=1，证据 `R6-W1-03` | fail but single case | 未达到三轮门槛，不单独修复；作为事实外扩的一个证据纳入主问题。 |

10 轮门槛判断：

- 进入修复：事实边界/完整性补写。修复范围限定为 md prompt，禁止硬门禁和脚本拦截。
- 伴随软化：缺项提示固定句式、自证式尾句、审稿固定框架和口号式收束。只改写作指令，不加禁词表。
- 暂不修复：相对时间处理、单次删除任务过度改写。继续观察。

### 修复与消融记录

修复原则：

- 只修复 10 轮中三轮以上复现的共性问题。
- 只改 `SKILL.md` prompt 文案，不新增硬门禁、脚本拦截或禁词表。
- 每次修复后用固定 A/B 样本做消融；若事实边界、文种功能、AI 味或查重风险明显退化，立即回滚该次修改。

Patch 1：

- 范围：尝试大幅收紧成稿补足边界，并调整起草、审稿、压缩多处提示。
- 消融样本：12 条，来自 R3-R10 中事实外扩、缺项尾巴和控制类 prompt。
- 本地扫描：A 组 lint 总数 18，B 组 lint 总数 13；B 组最高 TF-IDF `0.1547`。
- verifier 结论：`keep_patch=false`，`rollback_required=true`；4 条改善、3 条持平、5 条退化。
- 退化点：B 组新增或强化“申请单位”“说明单位”“上级单位”“报告单位”“2026年6月27日”等泛称主送、泛称落款或日期，控制样本也出现格式漂移。
- 处置：已回滚 Patch 1，不保留该修改。

Patch 2：

- 范围：改为更窄的 md prompt 修复，只补三处软约束：用户明确禁止编造时不补具体用途、效果、原因、处置、责任或后续动作；只输出正文时不附自证式尾句；未要求完整主送/落款/日期时不添加泛称主送、泛称落款或当前日期。
- 消融样本：沿用 Patch 1 的 12 条固定样本。
- 本地扫描：`python evals\ai-dedupe\local_scan.py output\ai-dedupe-ablation-patch2\patched_samples.json --repo-root . --out output\ai-dedupe-ablation-patch2\patched_local_scan.json`；结果为 sample_count 12，lint 总数 11，单篇最高 4，最小 SimHash 距离 24，最高 TF-IDF `0.1206`，最高 Jaccard `0.1218`。
- verifier 结论：`keep_patch=true`，`rollback_required=false`；8 条改善、2 条持平、2 条退化。
- 保留理由：事实外扩和说明性尾巴明显下降；退化集中在部分请示、函样本格式要素偏短，适合用更小 Patch 3 修正。

Patch 3：

- 范围：只在压缩、顺稿或去口语化提示中增加一句软约束，要求不得为变短或降 AI 味删除请示、函、通知、报告等文种已给的主送、落款、成文日期、请批事项或联系人等基本要素。
- 聚焦消融样本：3 条，覆盖 Patch 2 中暴露的请示、函格式回归，以及一个 180 字压缩控制样本。
- 本地扫描：`python evals\ai-dedupe\local_scan.py output\ai-dedupe-ablation-patch3\patched_samples.json --repo-root . --out output\ai-dedupe-ablation-patch3\patched_local_scan.json`；结果为 sample_count 3，lint 总数 4，单篇最高 4，最小 SimHash 距离 30，最高 TF-IDF `0.0037`，最高 Jaccard `0.0036`。lint 只来自 `P3-B1` 的数字列表样式。
- verifier 结论：`keep_patch3=true`，`rollback_patch3=false`。
- 保留理由：C 组较 Patch 2 补回请示/函的基本格式骨架，压缩稿保持 180 字以内，未见回滚级事实外扩、AI 味或查重风险。
- 剩余风险：Patch 3 只有 3 条聚焦样本，适合判断该最小补丁是否保留，但不能替代后续更宽样本回归；请示主送占位、函成文日期仍有轻微完整度差异，继续观察，不在本轮扩大修复。

## 测试反馈修复 loop

建议把后续工作固定为一个工程 loop：

1. **Test / 生成**：用当前 GitHub main 的 `chinese-official-writing` 生成 6-10 篇真实任务样稿，覆盖缺事实、改写、审稿、方案、讲话和技术材料。
2. **Review / 评审**：用反 AI 味或去重 skill 的独立 subagent 审核，只提供 prompt 和样稿，输出 PASS/WARN/FAIL、证据短语和共性统计。
3. **Record / 记录**：把样稿、评审 JSON、本地扫描结果放 `output/ai-dedupe-roundN/`，把摘要和共性问题写入 `agent.md`。
4. **Gate / 门禁**：只有同类问题跨三轮以上复现，才进入修复候选；单轮或两轮问题只观察。
5. **Fix / 修复**：对已达门槛的问题做最小 skill 改动，不扩大默认联网、不新增硬禁词、不改成聊天化风格。
6. **A/B 消融**：用上一轮样稿和新样稿比较“修复前 skill vs 修复后 skill”。必须验证事实边界、AI 味、查重/同质化指标没有退化。
7. **Rollback / 回滚**：消融、smoke 或最小验证失败，则撤销此次修复，只保留失败记录。

## 社区检测 skill 与工具补测记录

本轮目标是补足测试层，不修改写作 skill。优先找可作为独立 verifier 的 SkillHub/ClawHub 专用 skill；GitHub 工具只作为本地增强候选；DeepSeek API 暂不作为查重主工具。

ClawHub 检索与安装：

- `clawhub search "AI味" --limit 10`：命中 `humanize-zh`、`humanize-zh-pro`。
- `clawhub search "查重 相似度" --limit 10`：未命中。
- `clawhub search "tender similarity analyzer" --limit 10`：命中 `tender-similarity-analyzer`。
- `clawhub search "AIGC检测" --limit 10`、`"AI生成文本检测"`、`"机器生成文本检测"`：未命中。
- `clawhub search "AI detector" --limit 10`：命中 `ai-detector`、`detector-ai`、`zeelin-ai-detector`、`ai-article-detector` 等。
- 已隔离安装到 `output/ai-dedupe-community-skills/`：`humanize-zh-pro`、`tender-similarity-analyzer`、`zeelin-ai-detector`、`ai-detector`、`detector-ai`。该目录不提交，仅作测试器来源。

候选判断：

| 候选 | 类型 | 是否外发 | 本轮判断 |
| --- | --- | --- | --- |
| `zeelin-ai-detector` | 中文 AI 文本概率判断 skill | 否，纯 skill 评审 | 优先作为中文 AIGC/AI 味 verifier。 |
| `tender-similarity-analyzer` | 本地多文档段落查重工具 | 否，声明网络隔离 | 优先作为本地查重增强；当前 Python 环境缺依赖，需单独依赖环境后再跑正式样稿。 |
| `detector-ai` | 本地启发式 AI detector 脚本 | 否 | 可跑通，但指标偏英文；仅作低权重补充。 |
| `humanize-zh-pro` | 中文去 AI 味/评分 skill | 否，脚本本地 | 检测维度偏自媒体“人味”，不完全适合公文；只作低权重参考。 |
| `ai-detector` | GPTHumanizer API 检测 | 是，调用 `detect.gpthumanizer.ai` | 默认不纳入主流程，除非用户明确允许外发脱敏文本。 |
| `ai-article-detector` | 文章链接检测 | 可能依赖外部链接/网络 | 不优先，当前样稿是本地文本。 |

Smoke 结果：

- `python output\ai-dedupe-community-skills\detector-ai\scripts\detect_ai.py output\ai-dedupe-community-smoke\sample_a.txt --json`：可运行，输出 `overall_ai_probability=62.0`，`verdict=Likely AI-generated`，`confidence=Medium`。该结果只证明脚本可用，不作为正式质量结论。
- `python output\ai-dedupe-community-skills\tender-similarity-analyzer\scripts\main.py --files output\ai-dedupe-community-smoke\sample_a.txt output\ai-dedupe-community-smoke\sample_b.txt --output output\ai-dedupe-community-smoke\tender_report.html`：未跑通，当前环境缺 `docx`、`jieba`、`sklearn`、`lxml`、`bs4`、`jinja2` 等依赖；后续应建独立依赖环境或复用可用 Python 环境。
- `bash output/ai-dedupe-community-skills/humanize-zh-pro/scripts/detect-ai-taste.sh output/ai-dedupe-community-smoke/sample_a.txt`：未跑通，WSL bash 在当前沙箱报 `E_ACCESSDENIED`；后续可用 Git Bash 或改写为 PowerShell/Python 包装，但不作为第一优先级。

GitHub 工具候选：

- `Hello-SimpleAI/chatgpt-comparison-detection`：HC3 项目提供中英文检测器，含单文本检测和语言学特征检测，适合作为后续 AIGC 检测候选。
- `johnsonwangzs/MGT-Mini`：NLPCC 2025 机器生成文本检测 top-1 方案，中文相关性强；但需下载多套模型/微调权重，并要求两张 V100 级 GPU，当前只记录为重型候选，不强行接入。
- `HeraldofLight/C-ReD`：ACL 2026 Findings 中文 AI 生成文本检测 benchmark，适合作为后续评测集参考，不是直接检测工具。
- `shibing624/text2vec`：中文语义向量和相似度工具，适合补本地 embedding 查重层；优先级高于外部 embedding API。

下一轮补测建议：

1. 用 `zeelin-ai-detector` skill 作为主 AI 味/AIGC verifier，评审上一轮固定样稿。
2. 给 `tender-similarity-analyzer` 建独立依赖环境，跑同一批样稿的多文档交叉查重。
3. 用 `detector-ai` 脚本批量跑低权重辅助分。
4. 再接本地 `text2vec` 或 BGE embedding 做语义相似度；暂不使用 DeepSeek 或外部 embedding API。
5. 只有上述结果互相矛盾时，再考虑 DeepSeek API 作为大模型仲裁，不把它称为查重。

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

## SkillHub 增强排查 10 轮记录

日期：2026-06-28

本轮回应“不要放弃寻找 SkillHub skill”的要求，重新扩展检索并用 SkillHub 专用 skill 作为主要 verifier。只读测试，不修改 `chinese-official-writing`。

### 基线

- 当前分支：`codex/ai-dedupe-round1-20260627`
- 当前 HEAD：`31b4404 docs: record community AI detector candidates`
- 写作 skill 最近一次行为修改：`4e21b43 fix: tighten official writing fact-boundary prompt`
- 对照核验：`git diff --stat 4e21b43..HEAD -- chinese-official-writing skills openclaw hermes .qwen .agents` 无输出，说明 `4e21b43` 之后没有再改 skill 本体。
- 本轮样稿基线：最小事实边界修复后的本地版本，不再用未修复的 `origin/main` 旧基线。
- 样稿文件：`output/ai-dedupe-community-rounds-20260628/samples.json`，10 轮 x 每轮 2 篇，共 20 篇。

### SkillHub 扩展检索

使用 SkillHub API 关键词扩展检索：`AI味`、`去AI味`、`AIGC`、`AI检测`、`AIGC检测`、`机器生成文本检测`、`查重`、`论文查重`、`相似度`、`文本相似度`、`投标 AI味`、`公文 AI味`。候选摘要保存到 `output/ai-dedupe-community-skills/skillhub-search-expanded-fixed.json`。

代表候选：

| skill | 类型 | downloads / installs / stars | API | 本轮用途 |
| --- | --- | ---: | --- | --- |
| `unclecheng-reduce-ai-perception-v2` | 文章去 AI 味 | 17643 / 650 / 102 | false | 中文 AI 味 verifier 规则来源 |
| `unclecheng-reduce-ai-perception` | 去 AI 味 | 4844 / 502 / 15 | false | 候选记录 |
| `humanizer-academic-zh` | 中文学术去 AIGC | 3567 / 955 / 6 | false | 候选记录 |
| `humanize-ai` | AI pattern 脚本 | 3062 / 360 / 8 | false | 本地脚本扫描；中文覆盖不足 |
| `paperdown` | 论文降 AIGC | 3020 / 0 / 13 | false | 候选记录，偏改写 |
| `removeai` | 清除中文 AI 味 | 1609 / 391 / 1 | false | 中文 AI 味 verifier 规则来源 |
| `paper-checker` | 查重 + AI率 | 1356 / 0 / 3 | false | 本地脚本扫描 |
| `tencentcloud-aigc-recog-text` | 文本 AIGC 检测 | 970 / 103 / 0 | true | API 候选，未外发样稿 |
| `tender-similarity-analyzer` | 多文档查重 | 403 / 15 / 0 | false | 查重候选，当前环境缺依赖 |
| `humanizer-zh-enhanced` | 中文去痕 | 483 / 0 / 1 | false | 中文 AI 味 verifier 规则来源 |
| `boo-check-review` | 多 docx 查重 | 154 / 0 / 0 | false | 候选记录 |
| `stop-slop` | 去 AI 味 | 153 / 0 / 0 | false | 规则参考 |
| `cn-bid-deai-checker` | 投标文件去 AI 味 | 96 / 0 / 0 | false | 正式文档 verifier 规则来源 |
| `plagiarism-detection` | 查重监测系统 | 92 / 0 / 0 | false | 候选记录，偏前端系统 |
| `paper-ct-scan` | 论文 CT AI 痕迹 | 57 / 0 / 0 | false | 正式文档 verifier 规则来源 |
| `plagiarism-precheck` | 查重卫士 | 44 / 0 / 0 | false | 查重方法论 verifier 规则来源 |

本轮实际下载到 `output/ai-dedupe-community-skills/` 的 SkillHub 包包括：`unclecheng-reduce-ai-perception-v2`、`unclecheng-reduce-ai-perception`、`removeai`、`remove-ai-flavor`、`humanizer-zh-enhanced`、`humanize-ai`、`stop-slop`、`cn-bid-deai-checker`、`paper-checker`、`paper-ct-scan`、`wang-paper-ct`、`plagiarism-precheck`、`plagiarism-detection`、`boo-check-review`、`tender-similarity-analyzer`、`tencentcloud-aigc-recog-text`。

`tencentcloud-aigc-recog-text` 是企业 API 型检测，未用于本轮样稿，以避免外发测试数据。DeepSeek API 本轮未使用，因为未找到以 DeepSeek 为专用查重/AIGC 检测后端的成熟 SkillHub verifier；DeepSeek 可作为大模型仲裁，但不应冒充查重工具。

### 生成与评审流程

- Writer subagent 2 个，均加载 `.agents/skills/chinese-official-writing/SKILL.md`，生成 C01-C10 共 20 篇短样稿。
- Verifier A：加载 `removeai`、`humanizer-zh-enhanced`、`unclecheng-reduce-ai-perception-v2`，只评审 AI 味，不改稿。
- Verifier B：加载 `cn-bid-deai-checker`、`paper-ct-scan`，按正式/投标/论文文档的 AI 痕迹维度评审。
- Verifier C：加载 `paper-checker`、`plagiarism-precheck`、`tender-similarity-analyzer`，结合本地扫描结果评审查重、相似度和弱 AI 检测信号。
- 所有 verifier 均只读本地样稿，不上传外部服务。

### 本地扫描结果

| 工具 | 结果 |
| --- | --- |
| `evals/ai-dedupe/local_scan.py` | sample_count 20；prose_lint_total_findings 12；max_tfidf_cosine 0.0668；max_char_jaccard 0.0511；min_simhash_distance 22。未见跨样稿近重复。 |
| SkillHub `paper-checker` | max_ai_percentage 30；avg_ai_percentage 19.2；max_similarity_percentage 15；`samples_ai_over_30=[]`；`samples_similarity_over_40=[]`。 |
| SkillHub `humanize-ai` | total_issues 0。该脚本词库偏英文，对中文公文覆盖不足，只作“可运行但低权重”记录。 |
| ClawHub `detector-ai` | avg_overall_ai_probability 53.27；likely AI：`C02-02`、`C05-01`、`C07-01`、`C10-01`。该工具对短中文公文的低困惑度过敏，作为弱报警，不单独判失败。 |

### 只记录的三轮以上共性问题

1. **明示缺项未稳定列入待确认**
   - 轮次：C01、C03、C05、C07
   - 样稿：`C01-01`、`C03-01`、`C05-01`、`C07-01`
   - 证据：采购请示未列采购方式、资金来源、供应商；会议通知未列联系人、反馈渠道、附件；AI 算力需求未列价格、供应商、政策依据；会议纪要未列会议时间、主持人、参会人员。
   - 判断：medium。与前一轮事实边界修复方向一致，但表现为“未编造却也未提示缺项”。后续如修，只能软性补充“用户明示未提供且影响办理落地时，正文后短列待确认”，不得变成硬拦截或长问卷。

2. **三项/编号式脚手架和机械三项展开**
   - 轮次：C03、C04、C06、C07、C08、C09、C10
   - 样稿：`C03-02`、`C04-01`、`C06-01`、`C07-02`、`C08-01`、`C08-02`、`C09-01`、`C09-02`、`C10-01`
   - 证据：审稿和待确认项反复编号；三项任务默认等长铺开；“主要包括三项”“三个方面”“一是、二是、三是”等包装反复出现。
   - 判断：medium-low。公文可以编号，问题不在编号本身，而是没有必要时仍加三项包装，造成模板感。后续如修，应只提示“用户要求清单或文种确需逐项核对时编号；三项给定时避免额外套一层三项包装”。

3. **句群节奏偏齐、长句或并列链偏密**
   - 轮次：C02、C03、C04、C05、C06、C07、C08、C10
   - 样稿：`C02-02`、`C03-01`、`C04-01`、`C05-01`、`C06-01`、`C07-01`、`C08-01`、`C10-01`
   - 证据：`paper-checker` 高强度长句样稿包括 `C03-01`、`C05-01`、`C06-01`、`C08-01`、`C08-02`、`C10-01`；`detector-ai` likely AI 中有 `C05-01`、`C10-01`；verifier A/B 均指出句式同质和并列要求链。
   - 判断：low-medium。该问题影响 AI 检测弱信号和读感，但不能牺牲公文简洁。后续如修，应提示“按事项功能自然拆句，避免连续同长度并列句”，不引入口语化。

4. **泛化收束或重复性尾句**
   - 轮次：C04、C06、C10
   - 样稿：`C04-01`、`C06-01`、`C06-02`、`C10-01`
   - 证据：“做到情况清楚、进展可查”“后续将继续跟进督促”“上述工作覆盖窗口巡查、咨询处理和办事指南维护”等尾句未增加新事实。
   - 判断：low-medium。Verifier A 明确列为共性；Verifier B 只作为局部问题提示，交叉置信度低于前三项。后续可并入“句群节奏/收束只落已给事实”的最小提示，不单独扩大修复。

### 暂不进入修复的观察项

- `C09-01` 复函无标题和落款、`C10-02` “碰头沟通”偏口语、`C06-02` “多轮核看”生硬：均不足三轮，不修。
- 待确认事项编号尾部只覆盖 C07、C09 两个 round，且用于防止编造；不因降 AI 味删除。
- 查重/相似度风险低：local_scan、paper-checker 一致未见高相似度，不做查重方向修复。

### 本轮结论

本轮已按 SkillHub 专用 skill 优先原则补足测试层。结论是：当前最小修复基线没有明显跨样稿查重风险，也没有 HIGH AI 味样稿；但存在三类可进入后续修复候选的共性问题：明示缺项未稳定列待确认、机械三项/编号脚手架、句群节奏偏齐。第四类泛化尾句可作为合并修复点观察。

本轮不修改 skill。本轮记录提交后，若进入下一轮修复，应只做 md prompt 最小修复，并以 `4e21b43` 后当前基线和本轮 20 篇样稿做 A/B 消融。消融必须检查：缺项提示是否改善、是否新增编造、文种格式是否漂移、local_scan 相似度是否上升、verifier 是否出现新 HIGH。任何一项明显退化则回滚该次修改。

### 下一轮 goal 模式提示词

目标：基于当前最小修复后基线继续做“测试 -> 反馈 -> 最小修复 -> A/B 消融 -> 回滚或保留”的工程 loop。只修复 SkillHub 增强排查中跨三轮以上出现的共性问题，禁止硬门禁，优先改 `SKILL.md` prompt。

执行要求：

1. 先确认 `git diff --stat 4e21b43..HEAD -- chinese-official-writing skills openclaw hermes .qwen .agents`，明确当前 skill 本体是否仍等同上一修复基线。
2. 读取 `AGENTS.md` 和 `agent.md` 中 “SkillHub 增强排查 10 轮记录”。
3. 修复候选只允许覆盖三项：明示缺项短列待确认、避免无必要三项/编号脚手架、句群节奏自然拆分；“泛化收束尾句”只能并入第三项，不能单独扩写大规则。
4. 只做 `SKILL.md` / 对应镜像的最小 prompt 修复，不新增脚本、硬禁词、硬门禁、默认联网或外部 API。
5. 修复后立即用本轮 20 篇 prompt 做 A/B：旧基线输出 vs 新输出；writer subagent 生成，新 verifier subagent 加载 SkillHub `removeai`、`cn-bid-deai-checker`、`paper-checker` 等评审。
6. 消融指标必须包括：事实边界、明示缺项是否提示、文种格式是否保留、AI 味 HIGH/MEDIUM 数、local_scan 相似度、paper-checker AI率/重复率、detector-ai 弱报警变化。
7. 若出现新增编造、文种骨架漂移、查重相似度明显升高、AI 味 HIGH、或 verifier 判断净退化，则回滚此次修改，只保留失败记录并另拟更小方案。
8. 通过后再更新 `agent.md`，运行最小 smoke/回归验证，并按 AGENTS.md 要求 commit。不得把未运行的测试写成通过。

## AI 味/查重最小修复一轮记录

日期：2026-06-28

本轮目标是对 SkillHub 增强排查 10 轮中“三次以上共性问题”做一次最小 prompt 修复，并按用户要求做 A/B 消融；若出现回归风险，立即回滚该次方案。

### 本轮基线

- 修复前基线 commit：`b9e3872`。
- 对照样稿：`output/ai-dedupe-community-rounds-20260628/samples.json`，共 20 篇。
- 本轮坚持只改 `SKILL.md` prompt 和镜像摘要，不新增检测脚本、硬门禁、硬禁词或清洗器。

### 尝试过但回滚的方案

第一次方案同时覆盖三项：明示缺项短列待确认、避免机械三项包装、句群节奏和尾句收束。writer subagent 生成 20 篇 patched 样稿后，独立 verifier 给出回滚意见：

- `C08-01`：用户明确“不要新增原因、影响范围和整改举措”，patched 把三项问题扩写成“在线填报要求与窗口受理材料表述不完全对应”等未给解释。
- `C06-01`：用户只强调提高数据质量、压实填报责任、按时报送结果，patched 增加“名称、编码、地址、联系人”“具体经办人员和复核人员”等未给细节。
- 本轮判断：三项包装和句群节奏提示容易诱导模型为了“低 AI 味”补事实，按规则回滚该部分思路。

第二次方案补了“降 AI 味不得补造事实”的约束，但仍保留“三项/句群节奏”相关提示。writer subagent 复测后仍出现事实边界漂移：

- `C08-01` 继续把“口径不一致、更新不及时、操作不熟”扩写成“尚未统一、未能及时调整、掌握不稳定”。
- `C06-01`、`C10-01` 仍有新增流程和成效收束倾向。
- 本轮判断：继续回滚“三项美化/句群节奏”方向，不把它纳入当前修复。

### 最终保留的最小修复

最终只保留两个更窄的 prompt 边界：

1. 用户明示某些事项未提供且影响办理落地时，正文后短列用户点名缺项；不要漏列，也不要扩展成调查问卷。
2. 去 AI 味、变换句式、拆分长句或调整清单结构时，不得补写未给的解释、原因、影响范围、办理流程、责任人员、字段示例或整改动作。

同步范围：

- `chinese-official-writing/SKILL.md`
- `skills/chinese-official-writing/SKILL.md`
- `.agents/skills/chinese-official-writing/SKILL.md`
- `.qwen/skills/chinese-official-writing/SKILL.md`
- `hermes/skills/chinese-official-writing/SKILL.md`
- `openclaw/skills/chinese_official_writing/SKILL.md`
- `tools/sync_adapters.py`
- `tests/test_skill_boundary.py`

### 真实场景复测

writer subagent 使用当前 `.agents/skills/chinese-official-writing/SKILL.md` 生成 5 条真实样稿，覆盖购买数据脱敏工具请示、问题分析、方案正文、只审不改、字段式申请。

独立 verifier 结论：`NO_MATERIAL_REGRESSION`，不建议回滚。

逐项结果：

- `T01` PASS：资金来源、采购方式、供应商、验收指标均列入待确认；未扩展成问卷。
- `T02` PASS：只围绕三项既有问题正式化表达，未新增原因、影响范围、整改举措、责任人员或办理流程。
- `T03` PASS：三项任务边界基本保持，未新增牵头部门、考核办法、通报机制、责任人员。
- `T04` PASS：保持只审不改，按位置、风险层级和建议输出，未重写原文。
- `T05` PASS：只润色“申请事由”字段，保留字段顺序和空字段。

非阻断提醒：`T01` 有轻微重复，`T02/T03` 仍有少量公文判断腔和目的性补足，`T05` “我科室”正式度一般；这些不足未达到回滚条件。

### 对比与发布前检查

已运行命令：

- `python -m unittest tests.test_skill_boundary -q`
  - 结果：29 tests OK。
- `python -m unittest tests.test_real_prompt_ablation tests.test_review_regressions tests.test_revision_instruction_eval tests.test_promptfoo_eval -q`
  - 结果：57 tests OK。
  - 说明：因 Windows/sandbox 临时目录清理权限问题，使用提升权限运行；未改测试结果。
- `python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\b9e3872 --baseline-label baseline-b9e3872 --current-root . --out .\output\real-prompt-vs-b9e3872-conservative-ai-boundary`
  - 结果：baseline-b9e3872 54/54 通过，current 54/54 通过。
- `git diff --check`
  - 结果：通过。

未纳入提交的产物：

- `output/` 下 A/B 样稿、扫描结果和基线 worktree。
- `.clawhub/` 未跟踪目录。

### 结论

本轮保留的修复是“事实边界优先”的最小 prompt 修复，解决明示缺项未稳定提示的问题，同时用更明确的事实边界压住去 AI 味诱发的补造风险。机械三项、句群节奏和泛化尾句仍记录为后续观察项，本轮不修，因为两次 A/B 已证明直接修容易引发事实外扩。

## 1.4.9 发布前检查记录

日期：2026-06-28

本轮在 `619519a` 最小 prompt 修复基础上做 1.4.9 版本同步和发布前验证，不新增规则、不扩大测试硬门禁、不调整写作工作流。

真实 subagent 测试：

- writer subagent 生成 6 条真实场景样稿，覆盖缺项不阻断、问题分析不补事实、只审不改、字段式申请、商请函和限字压缩。
- verifier subagent 总结为 `WARN`、`publish_blocking=false`。
- 非阻断观察项：一处正文末句略像审稿口径提示；一处字段式申请将原分号单行改成分行字段。两项均未破坏事实边界、字段边界或文种功能，留作后续观察，不在发布前扩大修复。

发布前验证：

- `python -m unittest tests.test_skill_boundary -q`：29 tests OK。
- `python -m unittest tests.test_real_prompt_ablation tests.test_review_regressions tests.test_revision_instruction_eval tests.test_promptfoo_eval -q`：57 tests OK。
- `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\chinese-official-writing`：Skill is valid。
- `python -m unittest discover -s tests -q`：86 tests OK。
- `$env:PROMPTFOO_PYTHON = 'C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe'; npm run eval:official-writing:smoke`：20/20 passed，skill win rate 1.0，judge consistency rate 1.0。
- `python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\619519a --baseline-label baseline-619519a --current-root . --out .\output\real-prompt-vs-619519a-release-1.4.9`：baseline-619519a 54/54 通过，current 54/54 通过。
- `git diff --check`：通过。

详细证据见 `tests/evidence/real-writing-1.4.9-release.md`。结论：允许发布 GitHub main 和 ClawHub 1.4.9。

## 1.4.9 公开来源真实写稿/改稿 5 轮测试

日期：2026-06-28

本轮按用户要求随机覆盖政府网站和公司网站材料，做 5 轮真实写稿/改稿，只读 1.4.9 skill，不修改 skill 本体。最初 3 个候选 URL 返回 404，相关样稿作废；正式纳入样稿均先用 `Invoke-WebRequest -UseBasicParsing` 核验来源为 200。

正式样稿：

- `R149-5-01B`：中国政府网《国务院关于加强数字政府建设的指导意见》 -> 市数据资源局通知。
- `R149-5-02B`：中国政府网《“十四五”数字经济发展规划》 -> 政策学习情况报告。
- `R149-5-03`：国家发展改革委、生态环境部 2026 年节能宣传周通知 -> 园区活动方案。
- `R149-5-04B`：腾讯官网公司简介 -> 供应商基础情况调研摘编。
- `R149-5-05`：华为官网公司信息 -> 供应商基础情况调研摘编。

独立 verifier 结论：`WARN`，`publish_blocking=false`。

- 4 条 PASS：报告、方案、腾讯摘编、华为摘编均未发现事实编造、文种错位、采购推荐或禁止项新增。
- 1 条 WARN：`R149-5-01B` 通知把报送截止日期、报送渠道、联系人、附件模板等未给缺项写进正文“待正式明确后执行”，应移至正文后“待确认事项”。
- 共性判断：本轮未发现三轮以上共性失败；“通知类缺项进正文”作为单例观察项继续记录，不进入本轮 prompt 修复。

详细证据见 `tests/evidence/real-writing-1.4.9-public-source-5round.md`。

## 1.4.10 Hermes/GLM Review 复现修复记录

日期：2026-06-28

本轮目标是处理桌面 review 报告 `C:\Users\admin\Desktop\chinese-official-writing-Review-报告.md`。报告只作线索，不直接采信；每项 finding 经 1.4.9 基线和当前 HEAD 复现、源码检查、测试或 subagent 复核后再决定。

接受并修复：

- `R-1/S-3/A-1`：高频风险句式 lint 漏检。1.4.9 基线 13 条命中 `0/13`，当前 HEAD 命中 `13/13`。
- `S-1/S-2`：`--format` 代码围栏内格式漏扫和 `core_compiled` 冗余。1.4.9 基线围栏内无命中且源码含 `core_compiled`，当前 HEAD 围栏内命中 `halfwidth-punctuation`、`emoji-marker`、`markdown-bold`，源码不再含 `core_compiled`。
- `P-1`：起草规则 730 字单 bullet 过密。1.4.9 基线最长 730 字，当前 HEAD 拆为父 bullet + 6 个子 bullet，最长 181 字。

拒绝或延期：

- `X-1` 拒绝：OpenClaw 适配目录和 frontmatter 使用 `chinese_official_writing` 是 README 明示的兼容规则，ClawHub slug 仍为 `chinese-official-writing`，未复现加载断裂。
- `D-1/D-2/R-2/R-3/S-4/S-5/A-2/P-2/P-3/X-2` 延期：未复现明确失败，不扩大本轮修复。

发布前验证：

- `python .\tools\sync_adapters.py`：同步完成，无新增 diff。
- `python -m unittest tests.test_review_regressions tests.test_skill_boundary -v`：55 tests OK。
- `python -m unittest discover -s tests -v`：89 tests OK。
- `$env:PROMPTFOO_PYTHON = 'C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe'; npm run eval:official-writing:smoke`：20/20 passed，skill win rate 1.0，judge consistency rate 1.0。
- `git diff --check`：通过。
- `python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\github-1.4.9-review --baseline-label baseline-1.4.9 --current-root . --out .\output\real-prompt-vs-1.4.9-release-1.4.10`：baseline/current 均 54/54 通过。

真实 subagent 测试：

- 覆盖请示、通知、函起草，缺金额、日期、联系人、供应商、附件等不编造。
- 覆盖字段式材料改写，保持字段名、顺序和空字段，只润色指定字段。
- 覆盖只审不改，不重写全文，不打 0-100 分。
- 覆盖去 AI 味和 format lint，只提示风险，不自动清洗。
- 独立 verifier 结论：`PASS_WITH_WARNINGS`，`publish_blocking=false`。轻微观察项为通知中新增“暂未发生目录更新也请说明”等执行要求，后续继续观察。

详细证据见 `tests/evidence/review-fix-release-1.4.10.md`。

## 1.4.10 Follow-up Hermes/GLM Review 最小修复

日期：2026-06-28

本轮处理两份桌面 review 报告：

- `C:\Users\admin\Desktop\chinese-official-writing-Review-1.4.10.md`
- `C:\Users\admin\Desktop\chinese-official-writing-Review-1.4.10-扩大范围.md`

基线为 GitHub/main `d8d7ee0a96a0c0b822446bd70d1d417eef2a729e`。报告只作线索，结论经主上下文复现、源码检查、只读 subagent 复核和真实写稿/审稿测试交叉验证。

接受并最小修复：

- `N-1`：`可以说` 误命中 `不可以说`，收窄为 `(?<!不)可以说[，,]`。
- `N-2`：`综上所述` 误命中章节引用语境，收窄为 `综上所述[，,]`。
- `B3`：`经现场检查，未发现重大隐患` 有明确检查依据时误报；仅在同句前置 `经...检查/核查/评估/审查` 时跳过 `unsupported-conclusion`，无依据 `未发现重大隐患` 仍提示。
- `N-3`：长方案可能残留 Markdown `**加粗**` 小标题；在常见错误反例补软性提示，长稿正文用中文编号或普通小标题，不用 `**加粗**`、`###` 或代码块。

延期：

- `B1`：`高度重视` 维持 `low/empty-filler` 质量提示，不做复杂上下文白名单。
- `B2`：`有关方面认为` 维持 `medium/vague-attribution`，因为模糊归因仍需明确来源。

真实 subagent 测试：

- Writer A 覆盖节能宣传周/低碳日长方案和设备维保请示；长方案未残留 Markdown 加粗或 `###`，缺日期、经费、联系人、金额、采购方式、供应商、合同日期等均未编造。
- Writer B 覆盖字段式材料、只审不改和 lint 边界判断；字段顺序和空字段保留，审稿未重写全文、未打分，lint 判断与脚本复现一致。
- 独立 verifier 结论：`PASS`，`publish_blocking=false`。

验证：

- `python .\tools\sync_adapters.py`：同步成功。
- `python -m unittest tests.test_review_regressions tests.test_skill_boundary -v`：58 tests OK。
- `python -m unittest discover -s tests -v`：92 tests OK。
- `$env:PROMPTFOO_PYTHON='C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe'; npm run eval:official-writing:smoke`：20/20 passed，skill win rate 1.0，judge consistency rate 1.0。
- `python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\github-1.4.10-review-fix --baseline-label baseline-1.4.10 --current-root . --out .\output\real-prompt-vs-1.4.10-review-fix`：baseline 54/54，current 54/54。
- `git diff --check`：通过。
- `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\chinese-official-writing`：Skill is valid。

详细证据见 `tests/evidence/review-fix-1.4.10-followup.md`。本轮不做版本号 bump，不发布 ClawHub；这是 1.4.10 后续最小修复提交。

## 1.4.11 发布记录

日期：2026-06-28

本轮把 `273adb41ffd2400813376ce60b5582e6c06f6c89` 的 1.4.10 follow-up 最小修复作为 1.4.11 候选发布。行为层修复已经在上一节通过真实 subagent 测试；本节只做版本号同步、发布级验证和 GitHub/ClawHub 发布记录。

版本同步：

- `tools/sync_adapters.py` 版本号改为 `1.4.11`。
- canonical `chinese-official-writing/SKILL.md` metadata/openclaw/hermes 版本改为 `1.4.11`。
- 运行 `python .\tools\sync_adapters.py` 同步 `.agents`、`.qwen`、`skills`、`hermes`、`openclaw`、README、OpenClaw card 和 Claude plugin manifest。

发布前验证：

- `python -m unittest discover -s tests -v`：92 tests OK。
- `$env:PROMPTFOO_PYTHON='C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe'; npm run eval:official-writing:smoke`：20/20 passed，skill win rate 1.0，judge consistency rate 1.0。
- `python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\github-1.4.10-release-1.4.11 --baseline-label baseline-1.4.10 --current-root . --out .\output\real-prompt-vs-1.4.10-release-1.4.11`：baseline 54/54，current 54/54。
- `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\chinese-official-writing`：Skill is valid。
- 直接 lint 复现：N-1/N-2/B3 支持场景不再误报，无依据 `未发现重大隐患`、`可以说，`、`综上所述，`、Markdown 加粗和代码围栏格式仍正常提示。

详细证据见 `tests/evidence/review-fix-release-1.4.11.md`。

## 1.4.11 Follow-up Hermes/GLM Review 本地修复记录

日期：2026-06-29

本轮处理桌面报告 `C:\Users\admin\Desktop\chinese-official-writing-Review-1.4.11.md`。基线为 GitHub/main `89948800d9616cb207f7d263948db7f51bc2441c`，不做 `1.4.12` 版本号更新，不发布 GitHub 或 ClawHub，只做本地最小修复提交。

接受并修复：

- `B1`：`综上所述。/：/；` 在 1.4.11 clean HEAD 漏检。修复为只扩展终止标点 `，,。：:；;`，不匹配 `本文综上所述部分如下。`。
- `O1`：`（成文日期待确认）` 已被 lint 捕获，但 prompt 未明确；真实 writer 测试还暴露“用户明示成文日期缺失时仍把今天日期写进落款”的相邻问题。最终补成文日期边界：明示缺失、待确认或需另行确认时，不使用当前日期补落款，只在正文外列待确认；未明示缺失的完整草稿仍可使用当前日期作草稿日期。

拒绝或延期：

- `X-1` 拒绝：OpenClaw 适配 `name: chinese_official_writing` 是 README 明示兼容规则，未复现加载断裂。
- `B2` 延期：不把 `调查/检测/审计/评测/论证/了解` 整批列为安全结论依据，避免弱化 `未发现重大隐患` 的事实边界提示。
- `A-2/R-2/D-1` 等旧项延期：未复现明确失败。

为什么前几轮没看出：

- 前次测试只覆盖 `综上所述，` 和章节引用 false-positive，不覆盖句号、冒号、分号变体。
- `O1` 不是单纯 lint 漏洞；lint 已命中字面占位，但真实写稿验收没有隔离“成文日期明确缺失且不得用当前日期”的场景。
- `run_real_prompt_ablation.py` 不调用 LLM，只能证明 skill 包、reference、lint 和评估入口具备支撑，不能替代真实 writer 行为。

真实 subagent 测试：

- 只读 reviewer `019f0f46-08ca-7770-a049-d88e20a773d3` 独立确认 B1/O1 成立，B2/X-1 不应本轮扩改。
- 初始 writer/verifier 暴露 A1 失败：缺成文日期时写入 `2026年6月29日`。
- 最小补丁后 writer `019f0f4e-b7f7-7223-a621-ea7247e1f46e` 重测同一请示场景，未写今天日期，成文日期列入正文外待确认。
- verifier `019f0f4f-d79b-7aa2-baef-3413a05c389f` 结论 `PASS`，支持本地提交且不发布 1.4.12。

验证：

- `python .\tools\sync_adapters.py`：同步成功。
- `python -m unittest tests.test_review_regressions tests.test_skill_boundary -v`：59 tests OK。
- `python -m unittest discover -s tests -v`：93 tests OK。
- `python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\github-1.4.11-review-followup --baseline-label baseline-1.4.11 --current-root . --out .\output\real-prompt-vs-1.4.11-review-followup-after-date-fix`：baseline/current 均 54/54 通过。
- `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\chinese-official-writing`：Skill is valid。
- `npm run eval:official-writing:smoke`：最终提权重跑 20/20 passed，skill win rate 1.0，judge consistency rate 1.0；此前沙箱内失败是 promptfoo 无法调用配置 Python 和清理旧日志的环境权限问题。
- `git diff --check`：通过，仅有 Windows 行尾提示，无 whitespace 错误。

详细证据见 `tests/evidence/review-fix-1.4.11-followup.md`。

## Hermes 社区借鉴提交 2713e27 Review 记录

日期：2026-06-29

本轮只读 review Hermes 工作仓库 `C:\Users\admin\chinese-official-writing-review\repo` 的候选提交 `2713e275ea118e15ad3e0ce705bcc73f606b86c4`。当前交付工作区仍是 `F:\Workspaces\chinese-official-writing-skill`；未把 Hermes 提交应用到本工作区。

总体结论：不接受 `2713e27` 当前形态，不发布，不 bump 1.4.12。可保留部分社区借鉴思路，但必须在当前工作区重新做最小实现、同步镜像和测试。

复现证据：

- `python -m unittest tests.test_review_regressions tests.test_skill_boundary -v` 在 Hermes 仓库运行：58 tests，5 failures。
- `python -m unittest discover -s tests -v` 在 Hermes 仓库运行：92 tests，5 failures。
- 失败均为镜像一致性问题：canonical 新增 `format_docx.py` 和部分 reference 改动，但 `.agents`、`.qwen`、`skills`、`openclaw` 未同步。
- canonical `genre-checklist.md` 把 `## 函` 改成 `## 函数`，而镜像仍是 `## 函`，既破坏函文种章节，也证明提交内部不一致。

只读 subagent review：

- reviewer `019f126d-bf21-7310-bde2-eb64da7c169d` 结论：不建议接受。主要问题是 `format_docx.py` 可能覆盖同名 `.docx`、实际重建正文却声称只设置布局、会把任何 `关于...` 行当标题居中放大；段落同构规则噪声偏高且 match 不稳定；提交未补测试或证据。

真实场景补测：

- writer `019f126f-deac-7a63-ac71-6342d069f057` 用候选 canonical skill 跑 5 个场景：函、只审不改、Word/docx 边界、去 AI 味、字段式材料。
- verifier `019f1271-2ba3-7230-aa06-65a98988fd15` 结论 `overall=FAIL`。T1/T2/T3 PASS；T4/T5 FAIL，原因是把 `老板关心` 升级成 `领导高度关注/领导关注`，并补写 `资金使用具有必要性`、`推进较为紧迫`、`按程序推进` 等未给事实。

借鉴点取舍：

- AB1 段落同构检测：修改后再考虑。只能 low 提示，需要降低常见公文固定句误报、稳定 match、补正反测试。
- AB2 硬边界 checklist：思路可接受，但不得变成新阻断流程，必须同步镜像。
- AB3 AI 味替换表：当前实现拒绝。必须明确“只有原文有证据时可替换”，否则会诱发事实升级。
- AB4 `format_docx.py`：当前实现拒绝。Word/docx 工具需另行设计，不能覆盖模板、不能误排正文、不能声称只设置布局却重建全文。
- AB5 文种结构骨架：修改后再考虑。先修 `## 函数`，并说明骨架不是可见标签，不覆盖用户模板、字段式材料和既有标题顺序。

详细证据见 `tests/evidence/review-community-borrowing-2713e27.md`。

## 社区借鉴最小实现记录

日期：2026-06-29

本轮以 Codex 工作区 `F:\Workspaces\chinese-official-writing-skill` 为准，不修改 Hermes 工作仓库。基线为本地提交 `db5607b`，不 bump 1.4.12，不发布 GitHub 或 ClawHub。

接受的最小借鉴：

- `review-checklist.md` 增加 `定稿前高风险先查`，只作为定稿前快速分层，不变成阻断流程。
- `official-style.md` 增加 `口语来源不等于事实授权`，防止 `老板关心`、`钱花得值`、`马上要搞` 被升级成 `领导高度关注`、`投入产出清晰`、`推进较为紧迫`、`按程序推进`。
- `genre-checklist.md` 给通知、请示、报告、方案、申请、函补 `可参考顺序`，并明示不写成正文标签，不覆盖用户模板、字段式材料、网页复制稿或既有标题顺序。
- `anti-ai-patterns.md` 和 `prose_lint.py` 把既有口语替换提示改为低强度、保依据边界的建议。

拒绝或未引入：

- 不新增 `format_docx.py`。
- 不新增段落同构 lint。
- 不新增硬门禁、自动清洗脚本或默认确认流程。

真实 subagent 测试：

- Writer `019f1289-e637-7821-9994-d0bc63280cf1` 覆盖口语去正式化、字段式申请、只审不改、商请函缺项、模板优先通知 5 个场景。
- Verifier `019f128b-9977-7351-ba33-508958022f91` 判定 T1-T5 全部 PASS，`overall=PASS`，`publish_blocking=false`。

基线消融：

- `python .\tools\run_real_prompt_ablation.py --baseline-root .\output\release-baselines\db5607b-before-community-borrowing --baseline-label baseline-db5607b --current-root . --out .\output\real-prompt-vs-db5607b-community-borrowing`
- `baseline-db5607b`：55 用例，54 通过，1 失败；唯一失败是新增 P055。
- `current`：55 用例，55 通过，0 失败。

验证：

- `python .\tools\sync_adapters.py`：同步成功；首次沙箱内运行因 `.agents` 权限拒绝失败，提权重跑成功。
- `python -m unittest tests.test_skill_boundary tests.test_real_prompt_ablation -v`：39 tests OK。
- `python -m unittest tests.test_review_regressions tests.test_skill_boundary -v`：59 tests OK。
- `python -m unittest discover -s tests -v`：93 tests OK。
- `$env:PROMPTFOO_PYTHON='C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe'; npm run eval:official-writing:smoke`：20/20 passed，skill win rate 1.0，judge consistency rate 1.0。
- `python C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\chinese-official-writing`：Skill is valid。
- `git diff --check`：通过。
- 发布目录未发现 `format_docx.py`、`document_generator.py`、`generate_official_doc.py` 或 `install_fonts.py`。

详细证据见 `tests/evidence/community-borrowing-minimal-db5607b.md`。
