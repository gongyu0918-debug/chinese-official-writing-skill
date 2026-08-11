# 论文专项叶隔离门禁

日期：2026-07-13

## v1.5.8 基线流程

当前 `SKILL.md` 同时展示公文和论文入口。Agent 读取整份以公文规则为主的 `SKILL.md` 后，才由一句路由转读 `references/academic-writing.md`；论文任务虽然被要求跳过公文文种、行文关系和办理要素，但完整公文 Prompt 已经进入上下文。OpenClaw 入口同样先展示论文规则，再连续附加公文规则。现有 Promptfoo writer 只加载公文卡片，没有论文 dispatch，因此不能证明论文上下文已经隔离。

`开题报告` 和独立 `文献综述` 只在入口、reference 和静态断言中出现；1.5.8 的真实路由 sanity 未覆盖这两类任务。门禁开始时不把它们记为已验证能力，先从基础论文叶范围中移出，待基础叶通过后分别验证。

## 候选流程与分阶段门禁

1. canonical `SKILL.md` 只保留短入口、最终交付物路由和两类任务共用的最小事实边界。
2. 公文或正式工作材料只读取 `references/official-writing.md`，不得读取论文叶子。
3. 用户明确要求中文本科、硕士学位论文或课程论文的提纲、据材料分节起草、改稿或审稿时，读取 `references/academic-writing.md`；这是按最终交付物命中的普通专项路由，不以“没有其他论文技能”为前提。不得读取公文叶子和公文专项 references。
4. 基础论文叶通过后，开题报告读取 `references/academic-proposal.md`，独立文献综述读取 `references/academic-literature-review.md`；普通论文页不追加两套流程。英文论文、期刊或会议投稿全流程、实验设计、统计分析、答辩、排版和查重/AIGC 规避继续排除。
5. 公文叶保留 1.5.8 的文种、办理要素、输出模式、三级复核、默认联网和 reference 渐进加载规则；论文叶自带由大至小写作和由小至大复核，不再借用公文复核清单。

## 修改原因

- 论文是按需专项叶，不应与公文形成同级产品展示入口。
- 软性“跳过公文规则”不能消除已经加载进上下文的公文 Prompt。
- 开题报告和独立文献综述在门禁开始时没有真实验证，不能未经独立测试直接写成稳定能力。
- 双叶按需加载仍保持重 Prompt、轻脚本；不新增生成器、检测器、默认联网、强制确认或硬清洗。

## 单句回退方式

若候选出现公文能力回退、双向交叉加载、论文事实边界变差或上下文预算超限，撤销候选产品提交，恢复 v1.5.8 入口；随后按用户授权把论文叶复制为工作区内独立 Git skill，并把本仓库恢复为纯公文入口。

## 保留叶子的门禁

只有同时满足以下条件才保留论文专项叶：

- 静态上下文证明公文路径不含任何论文专项 reference；普通论文、开题报告和独立文献综述各自只加载短路由和一个专项 reference，不含 `official-writing.md`、公文卡片、文种、办理要素、格式或专项 references。
- canonical 入口和各 Agent description 以公文为主，论文只出现为次要按需入口；基础叶验证前，开题报告和独立文献综述不作为正向触发。
- 1.5.8 基线消融中，现有公文确定性用例无回退，完整测试、Promptfoo smoke、快速校验、镜像一致性和上下文预算通过。
- 两次独立 writer 对未见公文、论文、混合路由和超范围任务产出后，两名独立 verifier 均未发现公文规则渗入论文、论文结构渗入公文、事实编造或输出模式回退。

任一项失败，先回滚候选；若失败来自同 skill 的入口或上下文耦合而不是可单句修复的实现错误，直接执行拆分。

## 真实测试说明

真实 writer/verifier 的精确模型 ID 如运行面不披露，必须记为 `unavailable`，只作为独立 sanity，不冒充指定模型矩阵或统计显著性证据。不得使用 MiniMax；deterministic stub 只作工程回归，不作写作质量证明。

## 用户纠正后的分阶段处理

论文不是“没有其他技能才启用”的默认兜底，而是明确论文任务按需命中的专项叶，运行形态类似按主题进入 AI 算力专项 reference；它只是在产品展示层不与公文主入口平级。基础论文叶先接受双向隔离和公文回归门禁；只有判定保留后，才分别增加开题报告和独立文献综述子链，并对两条子链单独测试。基础叶不稳时不叠加子链，直接执行拆分。

论文叶只写论文任务的正向路径。公文与论文的互斥只在短路由中各说一次；不得在论文叶中反复写“不要按公文处理”“不要使用主送、落款”等对照句，因为这些词本身会把模型注意力重新引向未选中的链路。

## 社区实现最小借鉴

2026-07-13 复核了以下公开实现，只提取流程形态和检查维度：

- ClawHub `chinese-academic-writing`：开题、文献综述、正文和修改分阶段路由；文献综述按主题、时间或学派组织；只基于用户材料归纳，不编造文献。<https://clawhub.ai/michealxie001/skills/chinese-academic-writing>
- GitHub `luwill/research-skills`：研究计划采用“需求 -> 文献核验 -> 提纲 -> 分节内容 -> 质量核对”；引用不可核验时标记风险，不补造。<https://github.com/luwill/research-skills>
- GitHub `WenyuChiou/ai-research-skills`：文献处理与正文修改拆成单一职责叶，强调 claim-evidence 对应、来源状态和可移植的 `SKILL.md + references`。<https://github.com/WenyuChiou/ai-research-skills>

本候选只借鉴三点：按最终交付物分子链、先形成由大至小结构再分节写、逐条保持来源与论点对应。拒绝引入固定章数和篇幅、最低文献数量、强制确认、占位符、默认联网、Zotero/多 Agent 依赖、模板正文、生成器和格式化脚本。

## 基础论文叶盲测结论

两次候选 writer 与两次 `v1.5.8` writer 使用同一组 O1/O2/A1/A2/M1/M2/X1/X2 未见 prompts；四名 writer 的精确模型 ID 均为 `unavailable`，因此只记独立 sanity，不宣称指定模型矩阵或统计显著性。原始稿、匿名包、映射密钥和两份 verifier 原始判定均保存在同目录。

- verifier 1：32 份无 FAIL。候选两次 A1、A2、M2 全部 PASS；候选 writer 1 的 O2 因未单列“10月31日”缺年份风险记 1 个 WARN。基线 writer 1 的 A1、基线 writer 2 的 A1 和 M2 分别出现结构重复、论文功能偏薄或“待编码后形成”式占位 WARN。
- verifier 2：31 PASS、1 WARN、0 FAIL；唯一 WARN 是基线 writer 2 的 M2 占位式重复。候选两次输出全部 PASS。
- 两名 verifier 均确认 O1、O2、M1 无路由错误、事实编造、跨叶硬污染或输出模式回退；“本科毕业论文抽检通知”稳定走通知，“研究公文语言的课程论文”稳定走论文。

判定：基础论文叶保留。候选已经做到短路由和双向延迟加载，公文能力相对 `v1.5.8` 无硬回退，论文提纲的结构稳定性不低于基线。非阻断 WARN 不满足回滚或拆分门槛，也不据此向产品 Prompt 追加一例一修。

## 基础阶段工程验证

- `python -m unittest tests.test_skill_boundary tests.test_promptfoo_eval`：72 项通过（启用子链前）。
- `python -m unittest discover -s tests -v`：149 项中 148 项通过；唯一失败为当时有意未启用的 P109 独立文献综述守卫，公文和基础论文用例均通过。
- `python tools/run_real_prompt_ablation.py ...academic-leaf-base`：`baseline-1.5.8 112/112`，`current 111/112`；唯一失败同为当时有意延期的 P109。
- `py -3 evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2`：20/20 通过，10 个 skill 侧样本均胜 baseline，judge consistency 1.0。
- `py -3 .../quick_validate.py chinese-official-writing`：`Skill is valid!`。

基础叶通过后，开题报告与独立文献综述不追加到 `academic-writing.md`，而是分别进入 `academic-proposal.md` 和 `academic-literature-review.md`；每个任务只加载一个论文专项 reference。两条子链仍需各自真实 writer/verifier 复核，任一失败只回滚该子链。

## 开题报告与独立综述子链验证

子链 A/B 使用两次候选开题 writer、两次候选综述 writer、一次 `v1.5.8` 基线 writer 和一次公文通知回归 writer。所有精确模型 ID 均为 `unavailable`；原始稿、匿名包、映射和 verifier 原始判定保存在同目录。

- 开题报告：P1 给定学校栏目、研究材料、拟采用方法和进度；P2 只有题目，要求先给能成立的短稿再给三类构造建议。两名 verifier 对候选和基线的 6 份匿名输出均判 PASS；没有补造文献、对象、方法、数据、进度或结果。开题报告专项链保留。
- 路由回归：包含“本科毕业论文开题报告”的 O1 稳定生成通知，未进入论文正文结构，未补抽检比例、处罚、联系人、落款日期或政策依据；两名 verifier 均判 PASS。
- 独立综述首轮：L2 无来源且禁联网的 3 份输出均保持事实边界。L1 有来源样本中，一份候选稿把“相关关系”和“访谈反映”概括成“平台带来的影响”；verifier 1 判 WARN，verifier 2 判 FAIL，因此不能直接保留首轮版本。
- 最小修复：只在 `academic-literature-review.md` 增加一句“相关、关联、反映、提及不得改写为影响、作用、导致或效果；来源未作因果识别时，不使用因果或效果表述”，未改路由、普通论文页、开题链或公文链。
- 修复复测：两名额外独立 writer 重新完成同一 L1，两名独立 verifier 对两份匿名输出全部判 PASS，确认相关性、访谈代表性、制度文本未评估效果和 `[1][2][3]` 对应均保真。独立文献综述专项链保留，未触发回滚。

最终冷审发现 OpenClaw 的旧同步器仍把整页公文市场介绍内联在 `SKILL.md` 路由之前，论文任务会先摄入公文示例、文种和办理要素。该项判为发布阻断并已修复：市场介绍只保留在 `README.md`，OpenClaw 可执行 `SKILL.md` 的正文与 canonical 短路由完全一致。新增回归直接比较两者正文，并禁止实际 OpenClaw 入口出现“适用场景、核心能力、快速试用、27+ 文种”和请示示例等市场文案；最终 OpenClaw 路由正文为 `686` 字符。

修复后另用实际 OpenClaw `SKILL.md + academic-proposal.md` 完成一次只有题目的开题报告 smoke；独立 verifier 判 PASS，未发现公文结构、办理要素、事实补造、规则自述或加载过程，三类构造建议与正文分开。

## 最终工程验证

- `py -3 -m unittest discover -s tests -v`：150/150 通过。
- `py -3 tools/run_real_prompt_ablation.py ...academic-subchains-final`：`baseline-1.5.8 111/113`，`current 113/113`；基线只在两个新增子链守卫失败。
- `py -3 evals/official-writing/run_eval.py --suite smoke --judge-batch-size 2`：20/20 通过，10 个 skill 侧样本均胜 baseline，judge consistency 1.0。
- `py -3 .../quick_validate.py chinese-official-writing`：`Skill is valid!`。
- 完整数据集分 27 批的最大上下文为 `24947`，低于 `<25000` 门槛；普通论文、开题报告、独立综述单路由上下文分别为 `4322`、`2802`、`2898` 字符。
- 完整单测同时覆盖 canonical、`.agents`、`skills`、`.qwen`、Hermes、OpenClaw 镜像字节一致性和按路由只加载一个叶子。

最终判断：保留合并形态，不拆分。论文能力是次要展示、明确触发、按最终交付物命中的专项叶；运行时形成公文、普通论文、开题报告、独立文献综述四条互斥路径，但每次只加载一条。普通论文页没有公文对照词，也没有塞入开题或综述流程。

本轮不升版本、不推送、不发布，也不原地改写已经发布的 1.5.8 包。canonical 和仓库镜像已同步；现有 SkillHub 1.5.8 临时包与 Red 1.5.8 副本仍是旧发布快照，未来新版本发布包尚未生成。
