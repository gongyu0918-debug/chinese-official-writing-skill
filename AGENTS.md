# AGENTS.md

本文件适用于整个仓库。后续 agent 接手本仓库时，优先遵守这里的发布、review 和测试约定；若与用户最新指令冲突，以用户最新指令为准，但不得伪造未运行的测试结果。

当前接手入口只保留本文件。当前 GitHub 发布状态为 `chinese-official-writing@1.5.2`，tag `v1.5.2` 指向发布提交 `70efc9ce74fe956497b5044ee14f60e2b94c5e55`，`origin/main` 已包含发布提交和后续发布状态记录，交接时以 `git ls-remote --heads origin main` 复核最新文档提交。SkillHub 目标项目 `https://skillhub.cn/skills/chinese-official-writing` 已公开切换到 `latestVersion.version=1.5.2`，`skillId=70149`、`versionId=129948`、`tags.latest=1.5.2`，`iconUrl` 仍为蓝底 Q 版图标。ClawHub 1.5.2 也已完成异步切换；内置浏览器页面显示 `当前版本：chinese-official-writing@1.5.2`，`clawhub inspect chinese-official-writing --json` 显示 `latestVersion.version=1.5.2`、`tags.latest=1.5.2`、moderation `clean`，`--versions --limit 5` 列表包含 `1.5.2`。版本级 `inspect --version 1.5.2` 显示包内 18 个文件、`proofreading-checklist.md` 已发布、VT `clean`、`hasWarnings=false`；深度 security 字段仍为异步 `pending`。下方 1.4.1 到 1.5.1 内容均为历史接手记录，不代表当前 live 版本。

## 基本工作纪律

1. 所有代码或文档修改必须通过 git commit 留痕。commit message 需说明修改目的、影响范围和验证方式。
2. 每次认为任务可交付前，必须运行 smoke test 或最小验证流程；无法运行时说明原因和人工验证步骤。
3. 每累计 5 次 commit，或修改范围明显扩大时，暂停开发，执行轻量 review、基线对比、轻量消融测试和回归检查。
4. 代码 review、大范围 diff、长文件阅读、第三方实现对比等可能污染主上下文的任务，优先交给 subagent 或独立上下文；subagent 结论必须经源码、diff、测试或日志交叉验证后再采纳。
5. 不允许伪造测试结果；未实际运行的命令不得写成已通过。

## 中文公文 Skill 发布验证

`tools/run_real_prompt_ablation.py` 是发布级确定性消融工具，但它不调用 LLM，只能证明 skill 包、reference、lint 和评估入口具备相应支撑。它不能替代真实写稿实测。

社区技能借鉴必须先设门禁。SkillHub、ClawHub、GitHub 或其他社区实现只作为思路、流程形态、检查维度和 prompt/markdown 写法参考，禁止直接誊抄代码、脚本、正则、模板库、大段 prompt、固定话术或模板正文。每个候选借鉴点都要满足本技能边界：不新增重排版引擎，不扩大默认联网，不默认强制确认，不破坏用户模板和字段式材料，不把社区技能的坏代码、坏 prompt、硬禁词或公众号式风格污染到本技能；落地前先归纳共性问题，落地后必须和上一基线做消融。

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

### ANTI-AI 对抗评测工作流

只有通过 AI 痕迹 judge / reference 复核的样稿，才允许在发布报告或 README 中称为 `ANTI-AI` 写作能力。这里的门槛只用于评测和发布命名，不进入默认起草流程，不得把检测器写成正文生成阶段的硬阻断。

对抗评测必须先检索 ClawHub、SkillHub、GitHub 或相关社区里的 AI 味检测、AIGC 痕迹判断、查重/重复度判断类 skill 或 reference。优先借鉴其判断维度和报告结构，例如句群同质化、连接词链、重复开头、模板化转折、二元包装句、空泛强评价、同义词循环、口号式结尾、查重式重复片段等；禁止复制其代码、API 调用、规避检测流程、口语化注入策略、固定替换表或大段 prompt。

ANTI-AI 真实写稿测试应采用对抗式 A/B：

1. 红队 writer subagent 只加载当前 `chinese-official-writing` skill 写稿或改稿，至少覆盖起草、改稿、只审不改、口语来源正式化、长文或限字场景；红队不得读取蓝队判分标准以外的结论，也不得修改仓库。
2. 蓝队 judge subagent 只加载 AI 痕迹检测、AIGC 判断、查重/重复度 reference 的判断维度，不加载改写器，不调用 API，不给代改稿。蓝队只看“原 prompt + 红队样稿”，按 AI 痕迹、查重式重复、模板化程度、事实边界、文种格式和用户指令遵循给出 PASS/WARN/FAIL。
3. 首轮至少跑 5 个真实用户式 prompt。先只记录命中问题，不在同一轮里修复；只有出现三次以上共性问题，才进入下一轮最小修复和基线消融。
4. 若 AI 味下降但事实边界变差，不能直接判定通过；必须记录为“降 AI 味与事实保真存在张力”，等三次以上共性问题再做最小修复。
5. 若样稿出现明显模板味、查重式重复片段、空泛强评价或机械三段式，且 judge 判为 FAIL，本轮不得对外宣称 `ANTI-AI` 能力通过。
6. 通过口径以独立 judge 结论为准；主上下文不得自行把普通 `lint`、确定性消融或单次自评包装成 AI 检测通过。

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

## 1.4.4 接手记录

1.4.4 的修改应从 1.4.3 发行基线 `77b56726efab8e2dcffbc8c1f3ae999249c28707` 出发做最小增强。前置证据包括：

- `tests/evidence/skillhub-1.4.4-research.md`：SkillHub “公文”81 个结果和 8 个代表技能核验；只允许借鉴流程思路、检查维度和 prompt/markdown 组织方式，不复制社区实现。
- `tests/evidence/real-writing-1.4.4-round1.md`：3 个 writer subagent、8 个真实 prompt、独立 verifier 评分；三次以上共性问题为缺项进正文、字段/事实边界变化、限字不稳、抽象套话、要点位置不准。
- `tests/evidence/real-writing-1.4.4-round2.md`：3 个 writer subagent、3 个真实 prompt、独立 verifier 复核；当前 1.4.4 规则未出现三次以上共性失败，未观察到缺项规则变成阻断，后续只需关注 Markdown 残留、正式落款日期完整度和字数精确度。

1.4.4 候选修复只应覆盖这些共性层面：

- 缺政策依据、截止时间、联系人、反馈渠道等事实时，列正文外待确认，不写“指定渠道”“截止时间前”等泛占位。
- 字段式申请、证明、采购明细和清单式材料只改用户指定字段；新增字段无值时留空或待确认，不推断票据、邮箱、日期等内容。
- 限字压缩必须先锁定不可丢要素，再真实压到用户限制；无法兼顾时说明取舍风险。
- 长篇限字稿件不能只追求低于字数上限；要检查篇幅预算、首中尾完整度、措施安排和结尾落点，避免模型为了限字头重脚轻或草草收尾。
- 抽象词和强评价必须有对象、动作、责任、时限、数据或制度载体。
- Word/docx 交付只做内容定稿后的要素核对和版式衔接，不补造正文事实。

## 1.4.5 接手记录

1.4.5 只收紧 1.4.4 中“事实充分性”的表达方式，不新增硬 lint、不新增联网、不新增排版脚本。

- 事实不足不作为默认中断理由。普通起草、顺稿和改稿必须先完成可用正文，再在正文后用“待确认事项”或当前版本的软性补足标题提示关键缺口。
- 缺口提示是软性写作建议，不做调查问卷式问题清单；只列影响文种功能或执行落地的关键事实，例如金额、日期、联系人、反馈渠道、政策依据、申请事项、审批对象。
- 增删论点、扩写细节、调整表达等写稿人可安排事项，不应列成用户义务。
- 事实不足时不能用强判断补空白。材料未给风险结论、整改结论、检查结论或影响范围时，不自行写“未发现重大隐患”“无异常”“已完成整改”“未影响核心业务”等结论；材料只给问题清单时，也不补写“总体较好”“能够正常开展”等概括性正向判断。
- 第二轮或后续修改中，用户没有补齐上一轮待确认事项，也必须继续执行本轮明确修改请求；不得把待确认事项升级为连续追问或修改阻断。
- 对应确定性用例为 P043-P046；真实写稿实测还要覆盖“材料不足但先成稿”“请示关键事实不足但不先问一串问题”“第二轮未补事实仍继续压缩/调序”“缺事实时不补强判断”。

## 1.4.6 接手记录

1.4.6 只调整事实补足提示语，不改变事实不足的非阻断规则。

- 正文后的软提示优先用“补充以下信息后，文章会更完整”，少用“关键事实”这种偏审查清单的标题。
- 提示项仍只列影响文种功能或执行落地的必要缺口，不做调查问卷式展开，不把增删论点、扩写细节等写稿人安排事项列成用户义务。

## 1.4.7 接手记录

1.4.7 只做社区技能最小借鉴，不引入代码、脚本、字体、模板库、硬禁词、硬阶段或硬阻断。本轮借鉴来源只作为流程形态和检查维度参考：

- `official-doc-writer` 的启发只保留“正式交付前要素核对卡”：用户要求 Word/docx/红头/文号/签发/版记时，正文后列缺项，不编造正式要素，也不因缺正式要素阻断正文。
- `govwriter-pro` 的启发只保留“创作/修改模式素材边界”：修改模式以最新版底稿为主线，旧稿、参考样文、过往材料和公开网页材料只作结构、语气、格式或检查维度参考，不把旧金额、旧主送、旧落款、旧政策口号或旧结论自动带回正文。
- `humanizer` 的启发只保留“成簇问题审稿”：去 AI 味和空话套话检查不因单个正式词、单个转折或一次排比硬清洗；公文自然度以克制、准确、可执行为准，不引入第一人称、口语化、情绪化表达或公众号式“人味化”。
- 真实对比测试曾提示单样本 WARN：模型可能为了更正式而补入未给出的部门、管理动作或后续处理进展，也可能把多个“位置”合并得过粗。对应软收紧为：正式化只压实原文事实；用户要求“位置”时先逐项引用原文短语或句子，再给整体归纳。
- 后续复测又提示核对卡可能过度展开。对应软收紧为：用户已点名缺少文号、签发人、版记等具体正式要素且要求简短核对时，优先只列点名缺项；其他正式要素只用一句按单位模板另行核对概括，不展开成长清单。

对应确定性用例为 P047-P051；发布或继续修改前还要做真实写稿对比，至少覆盖正式 Word 缺项但先成稿、最新版/旧版/参考样文防回流、只审空话套话不重写、正式化不补组织/管理事实，以及旧能力中的文种判断、结构锁定和第二轮未补事实仍继续修改。

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

## 1.4.8 接手记录

1.4.8 只做去 AI 味软性审稿和国产 Agent Skills 兼容入口的最小增强，不新增硬 lint、不新增检测器、不新增排版脚本、不新增默认记忆机制。

- 去 AI 味借鉴只落在 `references/anti-ai-patterns.md` 的“句群节奏和模板化痕迹”：检查句首重复、连接词链、句长同质化、口号式收束、清单堆叠替代论证。它只作审稿质量建议，不作为硬门禁，不把公文改成公众号口吻、第一人称、反问、口语插入或情绪化表达。
- 记忆机制本轮不并入发行包。后续如做，只能是用户明确同意后的本地可选层，短文件、分文种、只记录稳定偏好；当前用户指令、文种功能和事实边界始终优先。
- 国产 Agent 适配遵循最小镜像原则：Qwen Code 因官方目录为 `.qwen/skills/<skill-name>/SKILL.md`，保留独立 `.qwen/skills/chinese-official-writing/` 镜像；MiniMax Skills、GLM Skills（Z.ai/智谱）、AutoClaw、Kimi Code CLI、TRAE、Baidu Comate AI IDE 等共用 `skills/chinese-official-writing/` 或 `.agents/skills/chinese-official-writing/`，不为同一配方新增 `minimax/`、`glm/`、`kimi/` 等重复镜像。
- README 安装提示里的平台名要使用实际名称：Qwen Code、MiniMax Skills、GLM Skills（Z.ai/智谱）、AutoClaw、Kimi Code CLI、TRAE、Baidu Comate AI IDE。Kimi 只写兼容提示，不写成已稳定官方 Skill 目录。
- 对应确定性用例为 P052-P054；新增边界测试检查 `.qwen/skills` 镜像、README 平台名、共享目录策略和 frontmatter 兼容标识。

## 1.4.9 -> 1.4.12 接手记录

根目录只保留 `AGENTS.md` 作为 agent 接手入口；旧 `agent.md` 已删除。旧文件顶部仍记录 ClawHub live `1.4.8` 和 AI 味/查重 Round 1 过程，容易被后续 agent 误当成当前状态；保留必要结论如下，详细证据以 `tests/evidence/` 为准。

1.4.9 的主要结论：

- AI 味/查重循环只采纳三轮以上共性问题，不把单轮样稿同质化直接做成硬门禁。
- 最小修复仍限定在 prompt/reference 层，不新增检测器、不新增清洗脚本、不改变默认写作工作流。
- 发布前真实写稿、公开来源 5 轮测试和基线消融证据见 `tests/evidence/real-writing-1.4.9-release.md`、`tests/evidence/real-writing-1.4.9-public-source-5round.md`。

1.4.10 和 1.4.11 的主要结论：

- Hermes/GLM review 报告只作线索；每项 finding 必须先复现，再决定接受或拒绝。
- 已接受并修复的方向包括高频风险句式 lint 漏检、`--format` 代码围栏内格式漏扫、冗余 `core_compiled`、起草规则单 bullet 过密、日期/综述类边界漏测等。
- X-1 `name` 连字符问题继续拒绝：OpenClaw / ClawHub 兼容入口仍使用 `chinese_official_writing`；除非能复现实际加载断裂，否则不要改成连字符。
- 详细证据见 `tests/evidence/review-fix-release-1.4.10.md`、`tests/evidence/review-fix-1.4.10-followup.md`、`tests/evidence/review-fix-release-1.4.11.md`、`tests/evidence/review-fix-1.4.11-followup.md`。

Hermes 社区借鉴候选 `2713e27` 的处理结论：

- 不接受 `2713e27` 原提交形态，不把它当作可发布候选。该提交在 Hermes 仓库测试中出现镜像不同步、`## 函` 被误改为 `## 函数`、`format_docx.py` 风险和 lint 噪声问题。
- 拒绝 `format_docx.py`：候选脚本声称只做版式，实际会重建正文，存在默认同名 `.docx` 覆盖风险，并会把任意 `关于...` 行误判为标题。
- 拒绝段落同构 lint 和 AI 味固定替换表：前者噪声偏高，后者会把口语材料升级为未给出的强判断。
- 只最小借鉴思路：定稿前高风险先查、口语来源不等于事实授权、文种可参考顺序、低强度 AI 味提示。
- 详细证据见 `tests/evidence/review-community-borrowing-2713e27.md`、`tests/evidence/community-borrowing-minimal-db5607b.md`。

1.4.12 的发布结论：

- 官方发布 commit 为 `92f6d15cb8802d1e66d8fad6f8d775db6945d9c4`，tag 为 `v1.4.12`。
- GitHub `origin/main` 已对齐该 commit；ClawHub `latestVersion.version=1.4.12`，moderation `clean`。
- 1.4.12 只保留 prompt/reference 和测试层最小增强，不新增硬门禁、排版脚本或默认联网。
- 发布前验证包括 `python -m unittest discover -s tests -v`、`npm run eval:official-writing:smoke`、`git diff --check`、基线消融和真实 writer/verifier subagent 测试。
- 详细证据见 `tests/evidence/release-1.4.12.md`。

## 1.4.13 接手记录

1.4.13 的发布结论：

- 发布候选从 `cb7c8d3` 出发，只追加版本号同步和 `sync_adapters.py` 版本字段同步修复，不新增硬门禁、lint 规则、默认联网或写作工作流阶段。
- 1.4.12 基线消融：`baseline-1.4.12` 55/55 通过，`current` 55/55 通过。
- 发布前真实写稿 sanity：独立 verifier 判定 2 PASS、1 WARN；WARN 为“只审格式和语气”样本中格式项覆盖偏轻，不构成阻断、事实编造或格式破坏。
- 详细证据见 `tests/evidence/release-1.4.13.md`。

## 1.4.14 接手记录

1.4.14 只调整 skill 触发 description、OpenClaw 摘要说明和 description 专项回归用例，不新增硬门禁、lint 规则、默认联网、排版脚本或写作 workflow 阶段。

- description 明确覆盖“中文公文和机关企事业单位、学校等正式事务材料”，同时保留“写申请/请示/报告/通知/函”等短 prompt 的路由能力。
- `降 AI 味` 收束为“对这类材料”适用，并明确排除论文、个人求职、营销、社媒等，降低误触发风险。
- OpenClaw 市场页说明改为市场页只展示摘要，安装包内入口规则和 `references/` 为准，canonical 全文见 GitHub。
- 新增 P056-P064 description 专项消融用例；1.4.13 基线在新增专项中失败 3 项，current 64/64 通过。
- 发布前真实写稿 verifier 判定 2 PASS、2 WARN；WARN 均为用户未提供主送/发函单位/成文日期导致的正式完整性偏简，不构成文种错乱、事实编造或中断。
- 详细证据见 `tests/evidence/release-1.4.14.md`。

## 1.4.15 接手记录

1.4.15 是针对 1.4.14 交付 review 的最小修复候选；本轮发布目标为 GitHub、ClawHub 和 SkillHub。

- 接受并修复字段式材料 lint 误报：`project-card-summary` 不再作为 base medium 阻断项，只保留为 `--structure` 下 low 级质量提示，避免字段式申请、证明、采购明细被 `--strict --fail-on medium` 卡住。
- 接受并修复正文外待确认标题变体：`（待确认事项）`、`待补充事项`、`需确认事项`、`补充信息` 等标题后内容不再按正文占位扫描。
- 接受 description 补强：frontmatter 明确覆盖 `通告、意见、决定、决议、议案、公报、命令`，降低短 prompt 漏触发风险。
- 拒绝本轮改代码围栏扫描：历史测试要求 `--format` 不能让占位符和 Markdown 残留藏在代码块里，不能一刀切停扫。
- 延期 BMP 装饰符号和 `可以说。`：可复现但属于小 lint 漏检，暂不扩大 lint 面。
- 1.4.14 基线消融：baseline 65/71，current 71/71；baseline 只在新增 description 守卫上失败。
- 真实写作 A/B verifier 判定当前候选相对 1.4.14 无功能回退。
- 详细证据见 `tests/evidence/review-fix-release-1.4.15.md`。
## 1.5.0 接手记录

1.5.0 是在 1.4.15 稳定基线上的文种 playbook 架构整理和最小边界修复候选；本轮发布目标为 GitHub、ClawHub 和 SkillHub。

- 只做 prompt/reference 层架构优化：按文种 playbook 补齐请示、通知、函、会议纪要、报告、方案、讲话/致辞、采购/可研等路由提示，同时保留共性事实边界、去 AI 味和 lint 规则，不新增脚本硬门禁。
- 接受并修复 playbook 消融发现的“AI 算力/采购主题过拟合”和“审查/讲话类输出易补造事实”风险；AI/算力只在用户明确给出主题时进入正文，普通采购、审查、讲话和只审不改场景不得自动带入 AI 算力表达。
- 基线消融必须固定上一发行基线 `1.4.15`；新增用例只允许 1.4.15 baseline 失败，current 不得失败。
- 发布前仍需真实 writer/verifier subagent 测试，重点覆盖 AI 算力可研、普通采购、字段式审查、会议纪要、讲话、只审不改和旧文种能力。
- SkillHub 发布只能针对 slug `chinese-official-writing`；本轮已用 SkillHub CLI dry-run 确认 slug/version，并向该目标提交 `1.5.0`，提交结果 `skillId=70149`、`versionId=127481`、`tags.latest=1.5.0`。公开详情页在审核完成前仍可能显示 `latestVersion=1.4.15`。
- 详细证据见 `tests/evidence/release-1.5.0.md`。

## 1.5.1 接手记录

1.5.1 是 1.5.0 发布后的 review-found 最小修复发布，包含本地已验证的 `35385ee` 和 `1fa0858` 后续提交以及版本同步。

- 接受并修复上行文缺主送机关、申请单位、金额、成文日期时的软提示不足；仍不阻断成稿，不编造泛称主送、泛称落款或当前日期。
- 接受并修复长文压缩中落款单位、联系人和成文日期被压掉或截短的提示不足。
- 接受并修复正文和说明之间残留 `---` Markdown 横线的 lint 漏检；只提示风险，不自动清洗正文。
- 接受并修复两个 agent/eval 工具的超时异常处理，超时时返回 `124` 和可读错误，不再直接抛 traceback。
- 1.5.0 基线消融：baseline `81/84`，current `84/84`；baseline 只在新增 P082-P084 review 回归用例失败，current 无失败。
- 真实 writer/verifier subagent 复核为 `overall=WARN`、`publish_blocking=false`；非阻断 WARN 为会议通知样稿在缺发文单位时补入“办公室”和当前日期，后续观察，不在发布前扩大修复面。
- SkillHub 支持 skill 级 `iconUrl`；ClawHub `inspect` 未暴露 skill 头像字段。本轮只对 SkillHub 上传并发布蓝底 Q 版图标，不向 ClawHub 包加入头像字段。
- 详细证据见 `tests/evidence/release-1.5.1.md`。

## 1.5.2 接手记录

1.5.2 是 1.5.1 后的 prompt/reference 最小边界修复和测试证据补强版本。

- 接受并修复一处引用核验提示边界：`SKILL.md` 入口从“最终稿保留用户给定引用时”收窄为“需要提示未核验引用时”，避免用户明确要求只输出正文时被强制追加核实句。
- 同步 `tools/sync_adapters.py` 版本到 `1.5.2`，并同步 Codex、Qwen、Hermes、OpenClaw、Claude plugin 和 README 元数据。
- 发布前验证包括定向 unittest `78/78`、全量 unittest `105/105`、GitHub main/1.5.1 基线消融 current `85/85`、真实文章回归、promptfoo smoke `20/20`、`git diff --check`、真实 subagent writer/verifier 和 3000 字以上调研/可研/多附件合稿测试。
- GitHub 已发布：`origin/main` 和 tag `v1.5.2` 均为 `70efc9ce74fe956497b5044ee14f60e2b94c5e55`。
- ClawHub CLI `0.18.0` 与 `0.23.1` 发布命令曾因服务端响应不再包含 `skillId/versionId` 而报 schema 错误；官方文档仍推荐 `clawhub skill publish <path>` 和 `/api/v1/skills`，本机 CLI 源码也走该端点。当前环境默认代理变量指向 `127.0.0.1:9` 时会导致 CLI 网络失败；临时清空代理后 `whoami`、`inspect` 和 `dry-run` 正常。用同源 CLI 组包逻辑直接调用官方 `/api/v1/skills`、带完整 GitHub source 元数据重试、以及 legacy `/api/cli/publish` 均返回同一个 `status=pending`、`attemptId=zx7d8vv11327rpzzzg0gfgh24h8a345c`；后续用户完成内置浏览器登录后，ClawHub 页面和 CLI 均确认 1.5.2 已完成异步切换：`latestVersion.version=1.5.2`、`tags.latest=1.5.2`、moderation `clean`、`--versions` 列表包含 `1.5.2`。
- SkillHub 已公开切换精确项目 `chinese-official-writing`：`skillId=70149`、`versionId=129948`、`tags.latest=1.5.2`，公开 `latestVersion.version=1.5.2`。
- 详细证据见 `tests/evidence/release-1.5.2.md`。

## 1.5.2 后续弱模型测试记录

`be46036` 在 1.5.2 基线上补了报告/说明类、会议纪要、采购/可研等 playbook 边界。本轮随后按用户要求追加弱模型低思考真实写作测试，覆盖版慎通成本考察、版慎通使用报告、结构锁定改稿、只审不改和长篇限字汇报。详细证据见 `tests/evidence/weak-model-low-reasoning-20260707.md`。

累计口径下达到三次的共性问题只有两类：一是弱模型容易把“建议、拟测试、下一步设想”写成已定实施方案或执行要求；二是只审不改或正式稿中仍可能残留 Markdown `**` 加粗标签。本轮只做 prompt/reference 层软性最小修复：保持建议或待评估口径，不在未给正式决定、责任单位和期限时写“按以上方案执行”“一周内反馈”等强执行要求；用户指定“位置 + 风险层级 + 修改建议”时，用普通文本标签，不用 Markdown 加粗包装。未新增脚本清洗、lint 硬规则或默认阻断。

事实外扩、标题漂移和日期额外推断本轮未达到三次共性。后续如果这些问题再次出现，应先复查现有规则是否分散或表述冲突，再决定是否做最小收紧；不要单凭一个样本继续追加补丁。发布前仍需同时跑弱模型低思考和强模型真实写稿，防止优化弱模型后让强模型过度保守或把建议边界处理成新的过拟合。

## 1.5.3 发布前阻断记录

1.5.3 是 1.5.2 后的本地候选，尚未发布 GitHub、ClawHub、SkillHub，未创建 `v1.5.3` tag。候选只做 prompt/reference 层最小收紧和 P091-P093 确定性用例补充，不新增 lint 硬规则、脚本清洗、默认阻断或默认联网。

- 已核实最小借鉴链路存在：历史证据和 `AGENTS.md` 已设社区借鉴门禁，当前包内未发现 `format_docx.py`、`document_generator.py`、`install_fonts.py` 等社区重脚本进入 canonical。下一轮建议补 `minimal-borrowing-ledger` 和轻量防重脚本/社区 slug 守卫。
- 确定性验证通过：`python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary` 为 42 tests OK；1.5.2 基线消融 `baseline-1.5.2 84/93`、`current 93/93`。
- 真实弱模型低思考当前能力测试未通过：结构锁定改稿和版慎通成本考察短稿基本可用，但数据治理专项推进情况通报连续复测仍补写基础清单、工作组、问题清单、统一共识、治理流程、验收节点等未给事实。隔离 verifier 判定不可发布。
- 发布决定：不得把本地 1.5.3 候选推送或标记为发布版。下一轮优先解决“材料稀疏型通报/情况说明/报告在弱模型上自动补处置链条”的共性问题，修复后必须重新做 1.5.2/上一候选消融和真实 writer/verifier 测试。

详细证据见 `tests/evidence/preflight-1.5.3-blocked.md`。

- 2026-07-08 继续在 `446c08c` 基线上按“测试 -> 修复 -> 复测 -> 消融 -> 不行回退”跑了四轮弱模型低思考 prompt 候选，均已回退。候选包括稀疏材料短写、入口三项交付习惯、入口长句拆分、一次静默清理。真实 6 prompt writer/verifier 复核显示 Markdown 残留、稀疏材料补造执行链条、情况说明漂成审批尾巴仍未稳定解决。下一轮不要继续往 `SKILL.md` 堆类似 prompt 限制；优先考虑显式二次修改/交付检查工作流或工具辅助 final-draft inspection。详细证据见 `tests/evidence/weak-model-prompt-loop-20260708.md`。

- 1.4.15 发布后补跑 description 新路由真实写作和改写测试，覆盖通告、命令（令）、意见、公报、决议、议案以及报告改通告、意见稿去口语化。独立 verifier 判定 6 PASS、2 WARN、0 FAIL；主要残留风险是材料不足时容易补入惯常判断，以及公开发布短稿有轻微评价化倾向。详细证据见 `tests/evidence/real-writing-1.4.15-description-routes.md`。
- 下次发布前必须核查远端字段原始值。ClawHub 1.4.15 曾因 Windows `npx.cmd` 传参把 `--name "中文公文写作"` 和 `--tags "chinese,...,ai-compute"` 的引号写入远端 `displayName` 和 tag key；下一版本发布必须使用 `--name=中文公文写作`、`--tags=chinese,official-document,writing,gongwen,ai-compute`，并用 `clawhub inspect --json`、SkillHub API 和 GitHub tag/main 核对 displayName、tags、latestVersion、summary 和 canonical frontmatter。
