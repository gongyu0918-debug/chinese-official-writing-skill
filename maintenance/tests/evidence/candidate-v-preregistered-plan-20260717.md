# Candidate V：1.2.22 低密度内核提取与 U1 信息选择收口

日期：2026-07-17

## 候选身份与固定边界

- 候选名：Candidate V。现有分支和 worktree 中未发现同名候选，无需顺延。
- 固定基线：`cd0772fcd763eaa34bb32361c2f8d2cdee39a291`，tag `v1.5.15`。
- 历史参照：`1dad87ae6a54210daaf24af848198a3c1ae36d5d`，仓库历史 1.2.22。
- 分支：`codex/1.6-candidate-v-low-density-info-selection`。
- worktree：`output/research-worktrees/candidate-v-low-density-info-selection-1.6`。
- 性质：Prompt 层研究候选，不发布，不改版本号，不合并现有候选。
- 1.2.22 只提供低提示密度和规则单一归属的组织思路。文种路由、输出模式、用户模板、事实锚、长文提纲与篇幅预算、多轮改稿、Word 交付和三级复核继续以 1.5.15 为功能基线。
- 本候选不包含 `review_gate.py`、`delivery-review-gate.md`、FSM 入口、新正则或脚本清洗；不修改段内公式。Candidate H 继续作为后续独立变量，虚拟段落任务不恢复。

主工作树检查时位于 `4382b2edf23632e0e2060f23cae45bb05273f9ce`，仅有用户已有的 `README.md` 修改。Candidate V 在独立 worktree 中从固定基线建立，不触碰主工作树改动。Candidate H、Q、S/U1 仍在各自 worktree 中，互不合并。

## 历史密度校准

以下统计只描述文本体积，不直接代表写作质量：

| 版本 | SKILL.md | canonical Skill 与 references |
| --- | ---: | ---: |
| 1.2.22 `1dad87a` | 138 行，5,251 字符 | 13 文件，1,298 行，29,147 字符 |
| 1.5.15 `cd0772f` | 170 行，11,794 字符 | 16 文件，1,792 行，61,802 字符 |

1.2.22 可借鉴的是入口只保留不变量、reference 各自承担单一职责、加载条件集中维护。以下旧行为不进入 Candidate V：占位符交付、合理推断材料事实、先标缺项再写、泛称主体和整体回滚旧 reference。

## 唯一信息选择规则源

新增 `chinese-official-writing/references/information-selection.md`，预注册正文如下；实施时不追加同义 Prompt：

```markdown
# 信息选择

本文件是起草、改稿、压缩和合稿的唯一信息选择规则源。先服从用户指定的输出模式；事实映射和复核留在内部，交付只包含该模式需要的正文或提示。

1. 材料已给且与当前主旨相关的事实进入正文，保持主体、对象、数字、日期、状态和结论强度。
2. 材料明确记载未定状态且与当前主旨相关时，沿用原状态；材料已有调查、核查、研究等进行中动作时，用进行态承载。正文已经承载的状态不在文后重复。
3. 材料未谈到，或者材料虽有记载但与当前主旨无关，且不影响文种功能或办理落地的外围事项，直接省略。
4. 材料缺少但属于用户明确要求，或直接影响当前文种成立、请批事项或执行落地的信息，视为实质缺口。输出模式允许文后提示时，在正文后短列；只输出正文或改后稿时只交正文。

文后提示使用少量短项，只写缺口及其对当前交付的直接影响。上一轮未补齐的缺口不阻断后续修改。用户要求先确认时，再在正文前提出必要问题。
```

`SKILL.md` 只保留一句全局总纲：

> 先服从用户指定的输出模式，再按材料状态、事项关联性和办理必要性选择信息；起草、改稿、压缩或合稿时读取 `references/information-selection.md`，再进入轻量卡或文种叶子。

该 reference 在起草、改稿、压缩或合稿时先读一次。轻量卡、文种叶子和完整 workflow 的选择条件保持 1.5.15 原样；只增加全局信息选择的单一入口，不加载 Q/S 门禁或整套 reference。

## 精确 diff

### 运行时 Prompt 文件

| 文件 | 预定改动 | 明确保留 |
| --- | --- | --- |
| `chinese-official-writing/SKILL.md` | 将 L66、L72-L87、L89-L90、L101、L114、L117、L120、L129、L141 中重复的信息去向规则收回；在任务模式区写入唯一总纲；在 reference 表增加 `information-selection.md`；删除“未新增原文外事实”交付自证授权。 | 触发范围、事实不编造、四类输出模式、用户模板、轻卡和 playbook 路由、段内公式、长文篇幅预算、多轮修改、Word 入口、三级复核、联网边界、字段和占位清理。 |
| `chinese-official-writing/references/information-selection.md` | 新增上文预注册的四类信息处理规则，明确材料未谈到的外围事项和材料虽已给出但与主旨无关的外围事项均不进入正文。 | 只承担信息是否进入正文、保持状态、省略或短列缺口的决策，不承载文种模板、段内写法或 Word 格式知识。 |
| `references/task-route-cards.md` | L9-L18、L36 删除“缺什么就文后提示”的重复授权；保留轻量卡适用条件、升级条件和四类事实骨架，并注明本页不重新定义信息去向。 | 材料稀疏情况说明/通报/报告、未决纪要、短通知、二次局部修改四张卡及路由终止规则。 |
| `references/workflow.md` | L28、L30、L87、L91-L115、L125、L170 中的信息去向交由唯一 reference；删除“未新增原文外事实”自证；素材映射只保留最新版主线、已给事实、压实表达和未支持推断的内部区分。 | 四类模式、文种和行文判断、结构动作、字段边界、事实映射式二次修改、稀疏会议事实、异常对象保真、篇幅预算、数据冲突识别、网页稿、搜索流程、三级复核和急件处理。篇幅冲突说明、联网来源说明、审稿意见属于专项交付，不并入普通缺项授权。 |
| `references/handling-elements.md` | L21、L63-L71 不再决定所有缺项的展示位置；改为只发现候选办理要素，去向由唯一 reference 决定。 | 通用要素、文种要素表、AI 算力专项要素、正式要素不得编造和占位清理。 |
| `references/genre-playbooks.md` | L25、L31-L32、L39、L45-L47、L60-L61、L90、L97 删除全局“事实不足即文后”授权；各叶只提出本文种所需要素和事实骨架。 | 全部文种/专项叶子、会议决定状态、请示一文一事、报告/通报/可研/采购的文种功能和专项风险。审查材料正文中的“需补充事项”仍按文种功能保留。 |
| `references/genre-routing.md` | L68 保留重要数据和判断需要来源，信息去向改由唯一 reference 决定。 | 文种选择和行文关系。 |
| `references/review-checklist.md` | L10、L31-L40、L53-L54、L63、L72-L74、L77、L79-L81、L87 的重复生成规则收成一个 `information-selection.md` 执行检查；删除默认“未新增原文外事实”说明检查。 | 段落/小节/全文三级复核、事实数字、用户模板、字段、搜索、Word、格式、文种、结构和过程残留检查。检查器只验证信息选择，不创造新缺口。 |
| `references/anti-ai-patterns.md` | L81-L82、L175 保留强评价、无来源归因和算力空话识别，删除独立的“列为待确认”授权。 | ANTI-AI 判断维度、语言修改方法和事实强度保护。 |
| `references/official-style.md` | L47、L74 保留证据强度和正式化不补造原则，删除独立的正文外补充授权。 | 公文语体、行文关系、轻量语气替换和主体保护。 |
| `references/proofreading-checklist.md` | L33、L37 保留合计关系和来源可追溯检查，信息去向交由唯一 reference。 | 引用保真固定提示、语言校对、稿内一致性和轻量校对边界。 |

以下 reference 不改：`argument-chains.md`、`genre-checklist.md`、`final-review-layers.md`、`formal-addressing.md`、`format-gbt9704.md`、`ai-compute-docs.md`。其中审查材料“需补充事项”、Word 正式交付核对卡、引用核验固定短句、正文外审稿意见和占位清理都属于文种或输出模式专项，不是通用缺项授权。

### 生成镜像

完成 canonical 修改后运行现有 `tools/sync_adapters.py`，仅同步对应 Prompt 文件及新增 reference 到：

- `skills/chinese-official-writing/`
- `.agents/skills/chinese-official-writing/`
- `.qwen/skills/chinese-official-writing/`
- `hermes/skills/chinese-official-writing/`
- `openclaw/skills/chinese_official_writing/`

`tools/sync_adapters.py`、README、版本字段、发布元数据和 Red 历史归档不改。若同步命令产生与本候选无关的 README 或版本差异，恢复该差异后再继续。

### 验证文件

- `tests/test_skill_boundary.py`：新增唯一规则源、SKILL 单句总纲、其他 reference 不再重复授权、镜像含新增 reference、Q/S 门禁文件不存在的结构断言；调整只因规则迁移而失效的旧位置断言。
- `tools/run_real_prompt_ablation.py`：不改真实 prompt 和能力期望；只为发生规则归属迁移的既有用例登记 1.5.15 旧位置与 Candidate V 新位置两个等价证据组，保证固定基线仍按旧结构通过、Candidate V 按唯一规则源通过。
- `tests/test_real_prompt_ablation.py`：验证上述等价证据组；不新增写作结论或弱化原有能力检查。
- 本文件和后续结果证据：只记录实际命令、输出、稿件哈希、盲审和停止判断。

运行时产品变更仍只有 Markdown Prompt/reference；评测工具的等价证据组不进入 Skill 安装包，不改变写作链路。

## 工程验证预注册

统一使用：

`C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe`

不使用 Hermes 虚拟环境。临时目录设在 Candidate V worktree 的 `.tmp`。依次执行：

1. `python -B tools/sync_adapters.py`
2. `python -B tools/run_real_prompt_ablation.py --baseline-root F:\Workspaces\chinese-official-writing-skill\output\release-baselines\github-1.5.15-candidate-k --baseline-label baseline-1.5.15 --current-root . --out output/candidate-v-deterministic-vs-1.5.15-20260717`
3. `python -B -m unittest discover -s tests -v`
4. 设置 `PROMPTFOO_PYTHON` 为同一 Python 3.13 后运行 `npm.cmd run eval:official-writing:smoke`
5. `python -B C:\Users\admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\chinese-official-writing`
6. 单独复核 `SkillBoundaryTests.test_primary_adapter_mirrors_match_canonical_bytes` 与 `SkillBoundaryTests.test_packaged_resource_mirrors_match_canonical_bytes`
7. `git diff --check`
8. `git diff cd0772f --name-only` 和 `git status --short` 核对精确范围；确认版本仍为 1.5.15，且 Candidate Q/S 门禁、FSM、正则、段内公式均未进入 diff。

工程验收：Candidate V 通过全部当前用例；固定 1.5.15 通过全部旧能力用例。只允许 Candidate V 新增的“唯一规则源结构”断言在固定基线不存在，不允许用规则迁移掩盖旧能力失败。

## 真实 A/B 预注册

### 固定任务

只使用现有人工标注 P0 任务，不生成真正无 Skill 稿。预审发现 P-A2 与 P-CN 都主要覆盖“与主旨相关的进行态”，没有覆盖“材料已经给出但与主旨无关的外围未决事项”；为保持六稿上限，正式 A/B 用已有长稿 T01 替换 P-A2，P-A2 只保留为既有归档校准材料，不重新生成：

1. P-B1：老旧小区改造整改进展报告。用户明确要求说明情况、分析原因、提出下一步措施，但材料没有原因和下一步措施；检查第四类实质缺口能否避免编造和静默遗漏。
2. P-CN：政务服务系统故障报告。材料明确“故障原因正在组织排查”；检查正文进行态和材料未谈到的外围事项是否省略。
3. T01：市图书馆自助借还设备试运行阶段报告，要求 1600—1900 字。材料明确下一阶段记录事项，同时记载设备调整方案、责任分工和新增采购安排尚未确定；检查长稿篇幅与事实覆盖，并检查与阶段报告主旨无关的外围未决事项是否被机械展开或重复保护。

原始 prompt 从既有冻结盲包逐字复用。Candidate V 和固定 1.5.15 使用同一模型、同一 thinking、相同宿主条件和逐字一致输入。每个任务每个臂只取首个技术有效输出，共六稿；不因语言优劣重跑。技术有效只指：输出非空、任务未超时或中断、实际读取目标 worktree/commit 的 Skill、没有串入另一候选。无法核验模型、thinking 或 Skill 读取时，该稿只记探索性证据，不计正式 A/B。

写稿使用相互独立的 subagent；匿名盲审另用独立 subagent，只提供原始 prompt 与匿名稿件。盲审先检查事实、数字、主体、状态、文种、格式、篇幅和输出模式，再统计：

- 外围未决事项；
- 无锚定否定；
- 自证边界或材料读取旁白；
- 材料外程序；
- 为直接使用所需的最小删除、替换或补写数量。

原稿、请求哈希、输出哈希、模型/推理证据、实际读取文件、匿名映射和盲审结果归档到 Candidate V 的 ignored `output/` 与一份 tracked 证据记录。subagent 完成后结束，不建立用户可见新任务。

## 风险分层与停止条件

P0 优先于可局部修复的次级问题。事实、数字、主体、对象、状态强度、文种、用户模板和输出模式回退仍是硬停止项。

Candidate V 按原严格口径通过，需要同时满足：

1. 三题均无 Candidate 独有的事实、数字、主体、状态、文种、格式、篇幅或输出模式回退。
2. 至少两题的保护性外扩数量或直接修改成本明确低于 1.5.15。
3. 没有任何一题整体直接使用成本高于 1.5.15。

若 P0 明显下降，但只出现一处材料本身无法支持、可在一次二次改稿中精准补齐的次级遗漏，则不把该遗漏定性为共性风险，也不丢弃信息选择方向；Candidate V 仍不按严格口径通过，而是登记为 P0 方向保留，等待独立变量或二次链路验证。只有累计三次以上同机制遗漏，才进入共性修复。

纯失败时撤回 Candidate V 产品改动，保留证据。出现正向与硬回退时，先撤回混合改动，再按实际失败机制拆分；不追加同义 Prompt，不做一例一修。通过只代表 Candidate V 具备继续验证资格，不代表 Word、用户模板、多轮改稿或全部文种已经完成真实回归。T01 在本轮单独检查长稿篇幅与事实覆盖；其余未触及能力在结构测试中只证明规则仍在，任何合并或发布前仍须在 Candidate V 单变量上补对应的最小真实链路，不能等与 Candidate H 组合后再把回退归因混在一起。Candidate H 仍需独立测试；两者分别通过后，才允许组合并做完整文种与 Harness 回归。

Candidate U1 的 P-B1 首稿遗漏保持原始盲审记录，不改写成通过；但单次遗漏不等于共性风险。另用既有初稿补一轮最小二次改稿诊断，只回答该缺口能否低成本修复，不进入 Candidate V 六稿统计。
