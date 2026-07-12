# AGENTS.md

本文件适用于整个仓库。后续 agent 接手本仓库时，优先遵守这里的发布、review 和测试约定；若与用户最新指令冲突，以用户最新指令为准，但不得伪造未运行的测试结果。

当前接手入口只保留本文件。GitHub tag `v1.5.7` 指向发布提交 `d3755df7deb2456150c61ccb1944aa3982f7edf1`，release 为 `https://github.com/gongyu0918-debug/chinese-official-writing-skill/releases/tag/v1.5.7`；`origin/main` 在发布后可能继续包含状态记录等文档提交，不再把 tag 和分支头写成必然相同，接手时以 `git ls-remote --heads origin main` 和 `git rev-parse 'v1.5.7^{commit}'` 分别复核。ClawHub 已公开切换到 `latestVersion.version=1.5.7`、`tags.latest=1.5.7`、`displayName=中文公文写作`，moderation 为 `clean`，发布 `versionId=k97ftrws1kttyemqrn1jmb13mx8aazy8`、19 个文件；`chinese`、`official-document`、`writing`、`gongwen`、`ai-compute` 五个正确 tag 均指向 1.5.7。1.4.15 和 1.5.6 形成的带引号或合并历史 tag key 仍保留，但不影响 `latest`、正确 tags、安装包或 moderation；后续发布继续把整个参数写成单一 token：`'--tags=chinese,official-document,writing,gongwen,ai-compute'`。

SkillHub 精确目标仍为 `https://skillhub.cn/skills/chinese-official-writing`，`skillId=70149`。1.5.7 已提交，返回 `versionId=134824`、19 个文件、`tags.latest=1.5.7`，`reviewStatus/securityScanStatus/contentAuditStatus=pending`；公开搜索索引暂仍为 1.5.6，需等待异步审核后复查。图标仍为蓝底 Q 版图标。发布前后必须用 `git ls-remote --heads origin main`、`clawhub inspect chinese-official-writing --json`、SkillHub API 或 CLI 和 GitHub tag/main 核对 displayName、tags、latestVersion、summary、source commit 和 canonical frontmatter。下方旧版本内容均为历史接手记录，不代表当前 live 版本。

## 小红书 Red SkillHub（与 SkillHub 分开维护）

小红书 Red SkillHub 是独立发布面，不等同于 `skillhub.cn` 的 SkillHub。两边的登录、标签、审核状态、skill ID、版本回执和安装包不得互相代替，也不能因为一边发布成功就把另一边记为已发布。

- Red SkillHub 官方上传说明：`https://redskill.xiaohongshu.net/uploader.md`。
- Red SkillHub 专用维护路径：`redskill/skills/chinese-official-writing/`。
- `skillhub.cn` SkillHub 的发布包仍在 `output/skillhub-release-<version>/publish-package/` 临时生成，不把该临时目录写成 Red SkillHub 的维护路径。
- Red 专用副本以同版本 SkillHub 已发布包为源，当前 1.5.7 只允许一项内容差异：删除 Red CLI 不支持的 `agents/openai.yaml`。其余共享文件须逐文件校验相对路径和 SHA-256；不得顺手删改 `_meta.json`、`SKILL.md`、references 或脚本。
- 后续版本先完成 canonical、GitHub、ClawHub、SkillHub 的既定验证，再同步 Red 专用副本；同步后运行小红书 CLI dry-run，确认版本、描述、Skill ID、标签和包哈希，不能沿用上一版本回执。
- 当前 Red 发布参数：`source=原创`，标签为 `内容创作、职场办公`。标签仍须在每次发布前由 CLI 实时拉取，不把本记录当成平台永久标签清单。
- 小红书 Red SkillHub 1.5.7 已真实提交：`skill_identifier=chinese-official-writing`、`name=中文公文写作`、`version=1.5.7`、`original=true`、`content_tag_ids=[1002,1004]`，回执为 `skill_id=8494`、`version_id=100041`、`first_version=true`、`display_status=1`、`audit_request_id=8494_100041_17833860685024`。首次用英文名称 `chinese-official-writing` 提交时服务端返回“名称长度不符合要求”，该次未发布；改用中文短名并重跑 dry-run 后提交成功。

Red 上传工具按官方包安装：

```powershell
npm install -g "https://fe-video-qc.xhscdn.com/fe-platform-file/104101b83221qt9bu7k0653u0hejenq0004pf88k9rpr6a.tgz"
```

官方 agent skill 注册在当前用户的 `~/.agents/skills/skillhub-upload/SKILL.md`。上传固定顺序为：`whoami`；未登录时 `login --agent`；实时取标签；对 `redskill/skills/chinese-official-writing/` 执行带完整 `--source`、`--tag` 的 `publish --dry-run --agent`；把 dry-run 的 `RESULT_JSON.payload` 展示给用户；只有用户明确回复“提交 / 确认 / submit”后才向 CLI confirm 阶段输入 `submit`；最后保存真实 `RESULT_JSON` 回执。

当前用户另有个人自动化 skill：`C:\Users\admin\.codex\skills\red-skillhub-upload\SKILL.md`。它触发“上传小红书 SkillHub / Red Skill / 上传小红书”等请求，采用渐进式披露：主文件只保留默认授权、自动标签和成功判据，详细 CLI 流程按需读取 `references/workflow.md`。该个人 skill 把上传请求本身视为真实上传授权；用户未指定标签时根据 skill 语义从实时标签中自主选择 1—2 个，用户明确指定时直接采用；仍须保留 dry-run、设备授权、永久 Skill ID 歧义和服务端错误等必要门禁。此个人偏好不得反向改变上方官方 `skillhub-upload` 的原始文件。

当前官方 CLI `0.1.1` 的 Windows shim 会因 `import.meta.url` 与 `process.argv[1]` 路径格式不一致而静默退出。在该版本修复前，可调用同一已安装模块的 `main()`，不修改打包、上传或提交逻辑：

```powershell
node -e "import('file:///C:/Users/admin/AppData/Roaming/npm/node_modules/@xhs/skillhub-upload/cli/index.mjs').then(m=>m.main(process.argv.slice(1)))" whoami
```

升级 CLI 后先重测普通 `skillhub-upload whoami`；若已恢复输出，应回到官方命令，不长期固化上述兼容入口。任何 Red 发布结果都在本节另记 Red 的 `skill_identifier`、版本、标签、回执和审核状态，不覆盖上方 SkillHub 的 `skillId=70149`、`versionId` 或公开索引状态。

当前 0.1.1 还有一项 frontmatter 兼容问题：SkillHub 包使用 `version: "1.5.7"` 时，Red CLI 会把引号保留进 payload，形成错误的字面版本 `"1.5.7"`。在 CLI 修复前，dry-run 和真实提交都必须显式传 `--version <无引号版本>`，并以 dry-run 的 `RESULT_JSON.payload.version` 为准；不得提交带引号版本，也不为此改写 SkillHub 包的 `SKILL.md`。

## 基本工作纪律

1. 所有代码或文档修改必须通过 git commit 留痕。commit message 需说明修改目的、影响范围和验证方式。
2. 每次认为任务可交付前，必须运行 smoke test 或最小验证流程；无法运行时说明原因和人工验证步骤。
3. 每累计 5 次 commit，或修改范围明显扩大时，暂停开发，执行轻量 review、基线对比、轻量消融测试和回归检查。
4. 代码 review、大范围 diff、长文件阅读、第三方实现对比等可能污染主上下文的任务，优先交给 subagent 或独立上下文；subagent 结论必须经源码、diff、测试或日志交叉验证后再采纳。
5. 不允许伪造测试结果；未实际运行的命令不得写成已通过。
6. 不得自行修改本 skill 的核心工作流。核心工作流包括任务路由、reference 加载条件、段落/小节/全文复核顺序、输出模式、修改次数、回滚方式和发布链路。拟修改这些内容前，必须先与上一发行版和相关早期稳定基线对比，向用户明确说明现有流程、拟改流程、改变原因和可能回退；只有用户明确同意后才可实施。发现措辞优化实际改变了流程时，应立即停止扩改并单独报告，不得把核心变更混入普通 Markdown 精简、测试修订或发布提交。

## 中文公文 Skill 发布验证

### 真实写稿测试分级

真实写稿测试按风险升级，不再作为每次小改的固定动作：

1. 普通脚本、测试、文档、发布元数据或默认不启用的检查器改动，优先运行 unit、clean corpus、确定性消融和静态回归；只有行为边界无法由这些证据确认时，才补 2-4 个短样本。
2. 修改 `SKILL.md`、写稿 reference、文种路由、事实边界或默认 workflow 时，先用 2-4 个与改动直接相关的短稿做 A/B，并由独立 verifier 复核；短测出现新回退、结论分歧或长文特有风险后，再扩大样本和模型数量。
3. 3000 字以上长文、多附件合稿、多轮/compact、跨模型大矩阵和完整文种覆盖，只在发布候选、重大架构调整、已复现的长文风险、用户明确要求或短测不能回答问题时运行。
4. 旁白、思考泄露和约束自述出现一次即可触发针对该样本的复现与最小修复判断，但不因此自动启动整套长稿批量测试。
5. 测试报告必须区分确定性证据、短样本 sanity 和发布级真实写稿；未运行长稿矩阵时直接说明，不用低价值批量生成填充测试数量。

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
5. A/B 出现近义词、情态词或固定搭配差异，且人工与 verifier 无法确定哪一种更符合公文习惯时，不靠模型票数直接裁决。先检索政府网站、公开政策文件和专业公文资料，记录检索词、来源类型、实际用例及上下文；优先采用更常见且与文种、责任强度和原材料决策状态一致的表达。搜索结果数量只作方向性证据，不能脱离语境把高频词机械替换进正文。本规则只用于 review/评测取证，不扩大 skill 默认联网范围。

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

## 1.5.4 重新发布候选记录

当前 `1.5.4` 发布候选不是上方被阻断候选的直接发布。后续复核发现远端 GitHub 已存在 `v1.5.3` tag，指向 `b4535b9 fix: close final 1.5.3 fact-boundary blockers`；该远端版本相对 `1.5.2` 已修复一组事实边界问题并新增 P086-P095。当前候选先恢复并保留远端 `v1.5.3` 的事实边界修复，再合入本地轻量 `references/task-route-cards.md` 和 `SKILL.md` 参考资料表按需读取提示。因远端已有 `v1.5.3` tag，本次候选上移为 `1.5.4`，不覆盖旧 tag。该候选不新增硬 lint、默认联网、强阻断或重排版脚本；弱模型验收口径明确为格式噪点记 WARN，优先判断 prompt 遵循、要点置入、事实边界、禁止事项和二次修改可交付性。

发布前验证已通过：1.5.2 基线消融 baseline `84/95`、current `95/95`；远端 1.5.3 基线消融 baseline/current 均为 `95/95`；全量 unittest `107/107`；promptfoo smoke `20/20`、judge 一致率 `1.0`；quick_validate 通过；真实样文回归 skill 路径 10 样本要素覆盖 `61/61`。合并后另跑弱模型 `gpt-5.3-codex-spark` 低思考和强模型 `gpt-5.5` 低思考真实写稿，独立 verifier 结论为强模型 3 PASS，弱模型 3 WARN、0 FAIL，主要风险为 Markdown 标题和一处轻微事实扩展，无三次以上共性功能失败。详细证据见 `tests/evidence/release-1.5.4.md`。

发布状态：GitHub main/tag 已推送；ClawHub `1.5.4` 已发布且 inspect 显示 clean；SkillHub `1.5.4` 已提交到精确项目 `chinese-official-writing`，返回 `skillId=70149`、`versionId=132166` 和 `tags.latest=1.5.4`，但搜索索引提交后仍显示 `1.5.3`，需等待审核/索引完成后复查公开页。

- 2026-07-09 针对“弱模型可能因入口规则过密导致注意力崩溃”的假设做过一次小步实验。候选只压缩 `SKILL.md` 的“任务模式路由与交付模式”入口段，并同步 Codex、Qwen、Hermes、OpenClaw 等镜像；未改 reference、脚本、lint 或版本号。入口段从 2013 字符压到 1463 字符，减少 550 字符，并把高密度长句拆成更短的扫描项。确定性验证通过：`python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary` 为 41 tests OK；与 1.5.2 的确定性消融为 baseline 85/85、current 85/85。但真实写稿 A/B 不支持保留：弱模型 `gpt-5.3-codex-spark` low 在当前压缩入口下没有优于 1.5.2 基线，TestAgent 通知把“通过钉钉发给技术应用部”写成“通过钉钉下发至技术应用部”，并把排查主体错误转给技术应用部；C1-C4 仍连续残留 Markdown 加粗。强模型 `gpt-5.5` low 未明显退化，但不能证明弱模型改善。结论：本次入口压缩候选已撤回，不得作为发布候选继续推进。后续如继续做注意力优化，不要在这版失败候选上叠补丁；应先只读审查信息熵和重复表达，每次只压缩一个小块，并固定使用弱/强模型真实 A/B，重点覆盖“时间点不得改成截止时间”“报送至/下发至/由谁执行的动作关系”“正式正文不使用 Markdown 加粗”。详细证据见 `tests/evidence/attention-compression-ab-20260709.md`。
- 2026-07-09 继续测试一个更窄的“入口长句拆行”候选：不删任何规则，只把 `SKILL.md` 中“起草或改写”下 4 条高密度长句拆成 8 条短句，同步各镜像；未改 reference、脚本、lint 或版本号。确定性验证通过：`python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary` 为 41 tests OK；与 1.5.2 的确定性消融为 baseline 85/85、current 85/85；入口片段最大单行长度 181 -> 132。但真实弱/强模型 A/B 不支持保留：独立 verifier 判定 current weak 在 260 字压缩通知中把“清查结果通过 OA 反馈至信息技术部”改成“由联系人李明通过电话12345678确认反馈”，遗漏 OA 渠道并改错联系人/反馈关系；current weak 还在 5090 说明和世界杯通知中补入未给判断，current strong 在 5090 说明中也有细节外扩。结论：该拆行候选已撤回，不得作为发布候选推进。后续压缩应先处理重复和信息熵，不要仅凭“更短/更分行”判断改善；必须继续用弱/强模型真实 A/B 证明不损害事实关系。详细证据见 `tests/evidence/split-drafting-rules-ab-20260709.md`。
- 2026-07-09 按“信息熵/重复表达先审查、三次以上回退后查社区路径”的要求，补做只读密度审查、独立 subagent 审查和 SkillHub 社区检索。可验证参考包括 `official-document-skill`、`plan-proofread`、`unclecheng-reduce-ai-perception-v2`；结论是只借鉴 `plan-proofread` 的“入口索引 + reference 细则 + 审稿清单化”思路，不借鉴单文件大入口、硬评分、重脚本、硬禁词、口语化和“活人感”。随后尝试“短原则 + 转读 reference”的入口瘦身候选，但 `python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary` 在 41 tests 中失败 6 项，说明入口不能移走 `用户明示某些事项未提供`、`不要做调查问卷式问题清单`、`材料未给风险结论`、`未发现重大隐患`、`总体较好`、`不得为显得完整而补造未提供的牵头部门...` 等历史回归锚点；补回这些锚点会退回上一轮已被真实 A/B 否掉的“拆行/换行”形态。候选已撤回，本轮不产生发布候选。后续不要继续压缩 `SKILL.md` 事实边界入口；若还要做注意力优化，优先只读审查并拆分按需 reference 的超长段落，或转向二次修改链路测试。详细证据见 `tests/evidence/prompt-density-community-review-20260709.md`。
- 2026-07-09 继续按用户放宽口径测试“弱模型首稿基本可用，用户自然语言指出问题后二次修改可用”。4 个真实场景覆盖 TestAgent 通知、OpenClaw 报告、世界杯通知和 260 字压缩通知；弱模型 `gpt-5.3-codex-spark low` 首稿为 1 FAIL、3 WARN，强模型 `gpt-5.5 low` 首稿为 2 PASS、2 WARN。用户式二次修改后，独立 verifier 判定弱模型二稿 4/4 PASS、强模型二稿 4/4 PASS。二稿阶段没有三次以上共性失败，因此本轮不修改 skill，不继续堆 `SKILL.md` 入口 prompt。首稿阶段仍需关注“时间点被改成截止时间”“弱模型漏落款/日期/反馈渠道或补管理动作”，但本轮证据显示可通过二次修改修正。详细证据见 `tests/evidence/second-revision-usable-20260709.md`。
- 2026-07-09 继续按“原始文档信息熵和压缩后信息熵”思路测试 reference 层最小拆段。只读定位和独立 explorer 均认为 `workflow.md` 的“事实充分性软处理”长段是可疑高密度片段；临时候选只把该段拆成“缺项处理、上行文结构缺口、正文缺项表达、强判断边界、事实外扩、playbook 边界、后续轮次”7 个短块，未删语义、未改 `SKILL.md` 入口。确定性验证 `python -m unittest tests.test_real_prompt_ablation tests.test_skill_boundary` 为 41 tests OK，但真实弱/强模型 A/B 不支持保留：weak candidate 三篇标题均残留 Markdown `**...**`，并在版慎通成本说明中补入近三个月调用结构、预算监测报表、按月复盘等未给管理动作；strong candidate 也在微博说明中轻度补具体选题方向。独立 verifier 判定 weak baseline PASS、weak candidate FAIL、strong baseline PASS、strong candidate WARN。候选已撤回，不得作为发布候选推进。后续不要把“更短、更分块、更像清单”直接等同于更好；若继续注意力优化，优先做加载路径 A/B（入口、入口+workflow、入口+workflow+playbook），或继续二次修改/只读 final-draft inspection 路线。详细证据见 `tests/evidence/reference-density-ab-rollback-20260709.md`。
- 2026-07-09 继续澄清并测试“深渐进式披露”。第一阶段测试 A=只读入口、B=入口+整份 workflow、C=入口+整份 workflow+整份 genre-playbooks；结论是“多读 reference”没有单调改善，weak A/WARN、weak B/FAIL、weak C/FAIL，strong A/WARN、strong B/WARN、strong C/PASS，不应强制或鼓励整份 reference 深加载。用户随后澄清深渐进式披露应理解为更细颗粒的按需路由，避免加载无关内容；第二阶段追加微型路由卡，只给稀疏情况说明、会议纪要、限字通知所需 5 条短规则。独立 verifier 在放宽弱模型格式噪点口径后判定 weak micro PASS、strong micro WARN。结论：微型路由卡值得作为后续设计方向，但本轮不直接并入正式 skill；弱模型不要再死磕一次成稿，重点看内容是否符合 prompt、事实边界和禁止项，Markdown 等格式噪点只记 WARN，交付口径转为首稿基本可用、二次/三次局部修改后可交付。详细证据见 `tests/evidence/deep-progressive-disclosure-ab-20260709.md`。
- 2026-07-09 在 `f0ae58f` 后将微型路由卡按最小原则并入正式 skill：新增 `references/task-route-cards.md`，`SKILL.md` 只在参考资料表增加一行路由提示，OpenClaw 精简入口同步同一提示；不新增 lint 硬规则、默认联网、强阻断或主入口长段落。轻卡只覆盖材料稀疏、未决会议纪要、短通知/限字通知和二次局部修改。真实 writer/verifier 复测显示弱模型 `gpt-5.3-codex-spark low` 三项均为 WARN、无硬 FAIL，强模型 `gpt-5.5 low` 三项 PASS；弱模型格式噪点继续只记 WARN，判断重点是 prompt 遵循、事实边界和禁止项。详细证据见 `tests/evidence/task-route-cards-real-ab-20260709.md`。
- 2026-07-09 继续在 `be140b9` 上测试轻卡并入后的真实二次修改链路。3 个真实场景覆盖 OpenClaw 安装情况排查报告、版慎通低成本模型测试会议纪要和 230 字以内账号权限自查通知；弱模型 `gpt-5.3-codex-spark low` 首稿为 2 WARN、1 PASS，强模型 `gpt-5.5 low` 首稿为 3 WARN，WARN 均集中在 Markdown/标题包装、`排查范围` 栏目或口径略硬。用户自然语言指出问题后二稿两组均为 3/3 PASS。独立 verifier 判定不存在三次以上共性失败，因此本轮只记录证据，不再修改 prompt，避免无意义膨胀。详细证据见 `tests/evidence/second-revision-after-route-cards-20260709.md`。
- 2026-07-09 继续做发布前旧能力真实回归，覆盖电脑采购内部申请、结构锁定改稿、只审不改、800 字以内模型成本治理建议。弱模型 `gpt-5.3-codex-spark low` 为 1 WARN、3 PASS，强模型 `gpt-5.5 low` 为 2 WARN、2 PASS；独立 verifier 判定 0 FAIL、无三次以上共性失败。WARN 主要是轻度格式包装、个别表达偏请示化、局部扩写超出指定范围，未达到修复门槛。本轮不修改 prompt，不新增规则，不做一例一修。详细证据见 `tests/evidence/release-readiness-regression-20260709.md`。
- 2026-07-09 按用户最新口径补做当前候选发布前综合预检：弱模型写作中的 Markdown 残留、标题加粗等格式噪点只记 WARN，不作为内容失败；判断重点转向 prompt 遵循、要点置入、事实边界、禁止事项和二次修改可交付性。`sync_adapters.py` 后零 drift；1.5.2 基线确定性消融 baseline/current 均为 85/85；全量 unittest 106/106；promptfoo smoke 20/20、judge 一致率 1.0；quick_validate 通过；真实样文回归 skill 路径 10 样本要素覆盖 61/61，但“主送单位、发文字号”等待确认项仍被工具计为占位风险，作为人工提示记录。当前候选未发现发布阻断。详细证据见 `tests/evidence/preflight-current-20260709.md`。
- 2026-07-08 继续在 `446c08c`、`59923bf` 和 `cc3776d` 基线上按“测试 -> 修复 -> 复测 -> 消融 -> 不行回退”跑了六轮弱模型低思考 prompt 候选，均已回退。候选包括稀疏材料短写、入口三项交付习惯、入口长句拆分、一次静默清理、显式交付前检查/smoke text 工具提示、纯文本交付和稀疏提醒/排查类短写前置。真实 6 prompt writer/verifier 复核显示 Markdown 残留、稀疏材料补造执行链条、情况说明漂成审批尾巴仍未稳定解决；单 prompt 隔离复测排除了“六篇合集”伪影，但仍有两次 verifier 判定不适合发布。下一轮不要继续往 `SKILL.md` 堆类似 prompt 限制；优先考虑真正的二次修订交互或外部工具辅助 final-draft inspection，并用真实 writer/verifier A/B 证明。详细证据见 `tests/evidence/weak-model-prompt-loop-20260708.md`。
- 2026-07-08 继续测试真实二次修改链路。六个真实首稿 prompt 的独立 verifier 结论仍是 6 WARN、`usable but not publish-ready`；自然语言二次修改能删除大块未给事实和明显 Markdown 包装，但仍残留行尾 Markdown 换行、小型事实外扩和日期沿用。随后只保留三条窄修复：二次修改中 `已排查/已核查/已检查` 不展开成未给范围/载体/流程/结果；正式正文不使用行尾两个空格控制换行；用户二轮要求不要补日期/删日期时同步删除上一稿日期。聚焦复测显示这些规则改善显式二次修改，但尚不能证明弱模型首稿可发布。下一步若继续发布准备，必须再跑上一基线消融、强弱模型真实写稿 A/B 和 verifier 复核。详细证据见 `tests/evidence/weak-model-second-round-repair-20260708.md`。
- 2026-07-08 在 `0caf2db` 上补跑用户指定 6 个真实 prompt 的强弱模型首稿 A/B。strong (`gpt-5.5 low`) 为 4 PASS、2 WARN，整体可进入二次修改；weak (`gpt-5.3-codex-spark low`) 为 4 WARN、2 FAIL，Markdown 残留、事实/措施外扩和正式格式完整性不稳均达到三次以上。独立 verifier 判定当前版本“可辅助起草，但不宜作为稳定版发布口径”。本轮只记录证据，不继续堆 prompt 补丁。详细证据见 `tests/evidence/weak-strong-first-draft-ab-20260708.md`。
- 2026-07-08 随后尝试把共性外扩归纳为“风险提示/排查/核查类短稿”最小候选，并通过确定性单测和 `3a6eba3` 消融；但真实 weak 复测仍在 Claude Code 通知、暴雨通勤提醒、世界杯通知和 OpenClaw 报告中出现 Markdown 残留、执行链条外扩和排查范围/方法补造，独立 verifier 判定不应保留。该候选已回退，只保留失败证据。后续不要重复追加同类“场景名称 + 禁止项”短稿边界。详细证据见 `tests/evidence/failed-risk-shortdraft-candidate-20260708.md`。
- 2026-07-08 又诊断了 URL-only 与来源摘录的区别：当 Claude Code 和气象网页关键事实直接放入 prompt 时，弱模型能基本保留版本号、预警时间、预报时段和地区范围；但 OpenClaw 稀疏报告仍补入“按照有关要求”“相关终端设备”和当前日期。后续不要把“URL 是否被读取”与“公文写作能力”混成同一个回归结论；测试公文改写能力时应给来源摘录或确认 writer 具备联网读取能力。真正需要继续处理的是稀疏报告/情况说明自动补依据、范围、日期和后续管理动作。详细证据见 `tests/evidence/source-excerpt-vs-url-diagnostic-20260708.md`。
- 2026-07-08 在不再堆默认起草 prompt 的前提下，保留了一处 review-only 最小修复：`references/review-checklist.md` 增加稀疏 `已排查/已核查/已检查` 类报告和通知短稿的 final-draft inspection 风险提示，把 `按照有关要求`、`相关终端设备`、当前日期、后续管理、记录留痕等未给依据/范围/动作至少按中风险提示。确定性消融对比 `d5c2c61` 为 baseline `101/102`、current `102/102`；真实低思考审稿复测和独立 verifier 判定 PASS。该修复只改善“只审不改/外部检查”安全网，不证明弱模型首稿已可发布。详细证据见 `tests/evidence/final-draft-inspection-20260708.md`。
- 2026-07-08 继续测试“交付修订模式”作为非默认二次修订能力。默认首稿“交付前三项短检”候选在真实 6 prompt 复测中仍未解决事实外扩和格式残留，已回退；当前只保留用户把坏稿发回并要求“修干净、能发、删掉没说的东西、去掉格式痕迹、按已给材料重改”时触发的 `references/review-checklist.md` 交付修订模式。二次修订真实测试为 2 PASS、2 WARN，能明显删除补造链条，但仍有行尾空格、少量制度化表达和落款位置不稳风险。本候选不是发布充分条件，不要宣称首稿质量已稳定。详细证据见 `tests/evidence/delivery-repair-loop-20260708.md`。

- 1.4.15 发布后补跑 description 新路由真实写作和改写测试，覆盖通告、命令（令）、意见、公报、决议、议案以及报告改通告、意见稿去口语化。独立 verifier 判定 6 PASS、2 WARN、0 FAIL；主要残留风险是材料不足时容易补入惯常判断，以及公开发布短稿有轻微评价化倾向。详细证据见 `tests/evidence/real-writing-1.4.15-description-routes.md`。
- 下次发布前必须核查远端字段原始值。ClawHub 1.4.15 曾因 Windows `npx.cmd` 传参把 `--name "中文公文写作"` 和 `--tags "chinese,...,ai-compute"` 的引号写入远端 `displayName` 和 tag key；下一版本发布必须使用 `--name=中文公文写作`、`--tags=chinese,official-document,writing,gongwen,ai-compute`，并用 `clawhub inspect --json`、SkillHub API 和 GitHub tag/main 核对 displayName、tags、latestVersion、summary 和 canonical frontmatter。

## 1.5.4 交付 review 后续记录

2026-07-09 复核 `C:\Users\2\Desktop\中文公文写作skill-1.5.4-交付Review报告.md`。该报告结论为 1.5.4 可交付，但提示架构膨胀和重复规则风险。本轮只接受两项最小修复：一是在 `task-route-cards.md` 增加“完整文种骨架、800 字以上长文、多材料合稿、会议纪要/可研/采购/AI 算力专项论证、GB/T 9704 或 Word 正式交付”等必须转读长 reference 的条件；二是将 `genre-playbooks.md` 通报小节中的事实映射式二次修改细则改为指向 `workflow.md`，降低 single source of truth 漂移风险。Codex、`.agents`、`.qwen`、Hermes、OpenClaw 等镜像已通过 `tools/sync_adapters.py` 同步。

本轮拒绝继续压缩 `SKILL.md` 硬边界入口、拆分 `workflow.md` 事实充分性长段，原因是此前 `attention-compression-ab-20260709.md`、`split-drafting-rules-ab-20260709.md`、`prompt-density-community-review-20260709.md` 和 `reference-density-ab-rollback-20260709.md` 均记录过弱模型真实 A/B 回退。后续不要在这些入口和事实充分性长段上叠补丁；如要继续优化，应优先做加载路径或二次修改链路实验。

验证：定向 unittest `43/43` 通过；与当前 1.5.4 基线 `48f3190b704e0486f09e5b44f4c6a1e3efc91bcd` 的确定性消融为 baseline `95/95`、current `95/95`；真实写稿 A/B 使用 subagent，baseline writer `019f44de-05a4-7661-a39b-6ee51015ae86`、current writer `019f44de-4f23-7ea0-90af-389fdadd3afd`、verifier `019f44df-77c1-7f31-886c-ed97e5c7fb58`，两项任务均 PASS，verifier 判定 current 无功能性回退。详细证据见 `tests/evidence/review-fix-1.5.4-delivery.md`。

## 1.5.4 深度 review 进行中记录

2026-07-09 按用户新目标进入深度 review 轮。本轮规则：使用隔离 subagent 冷审，不复用旧 review 结论；未经复现不采信单次 finding；只有三次以上共性问题才进入最小修复；禁止脚本硬清洗、一例一修和默认阻断；每次实质 prompt/reference/script 修改后必须与 1.5.4 基线做确定性消融和真实写稿 A/B。当前基线固定为 `output\release-baselines\local-1.5.4-48f3190`，当前工作树起点为 `42e7b08`。

当前已启动三条只读隔离任务：冷审 reviewer `019f44f2-c729-7ec2-9962-3343180d5f9d` 只看当前源文件、不读历史证据；baseline writer `019f44f3-5ed3-7591-903c-405227879a94` 读取 1.5.4 基线 skill；current writer `019f44f3-d46a-7ad1-b47e-1703ec9acd0b` 读取当前候选 skill。写稿 A/B 覆盖 description 中声明的 30 类文种/正式材料，每类 1 个真实用户式短 prompt。后续必须由独立 verifier 只看 prompt 和两组输出判定回退风险，不能由主上下文自行判定。

本轮冷审只接受一项最小修复：将 `references/workflow.md` 中“事实充分性软处理”超长单段拆成短 bullet，保持原语义，不新增硬阻断、脚本清洗、lint 规则或默认联网。首轮真实 A/B 达到三次以上共性问题，允许尝试该最小修复；post-fix 继续用 30 类 prompt 做 1.5.4 baseline/current 写稿 A/B，verifier `019f4500-f7ae-7462-a43d-ad38f4c4ac34` 判定总体 `WARN`，但未出现 current 独有且达到三次以上的同类功能性回退，建议保留拆分、不回滚、不继续补丁式追加规则。

验证：定向 unittest `43/43` 通过；全量 unittest `107/107` 通过；与 1.5.4 基线的确定性消融为 baseline `95/95`、current `95/95`；promptfoo smoke `20/20` 通过；真实样文回归 skill 差异率 `0.00%`、关键词命中率 `100.00%`，但仍有占位词风险样本需人工复核；quick_validate 通过；`git diff --check` 通过且仅有 Windows 换行提示。详细证据见 `tests/evidence/deep-review-1.5.4-workflow-split.md`。

## 1.5.6 前置阻断、finalizer 回滚和发布裁决

2026-07-10 以 GitHub `v1.5.5` 为固定发行基线补做 reference 路由、评测 provider、只输出正文边界和真实长文测试。已保留的本地候选改动通过全量 unittest `121/121`、确定性消融 current `101/101`、Promptfoo smoke `20/20` 和 quick_validate；但真实 `gpt-5.6-luna` 写稿在 600—800 字、900—1100 字及 3000—3500 字多附件合稿中可复现“现有材料没有/未说明”等材料读取旁白，独立 verifier 按当时“一次出现即阻断”的口径判定 `FAIL`。该问题在 `v1.5.5` 基线也存在，不是本轮候选独有，因此该段只记录阶段性暂停发布的历史判断。

先后尝试的明示禁令、业务对象状态改写、静默纯净检查和单次静默净稿四种 prompt-only 候选均未在长文中稳定解决，已全部回滚；不要在这些失败候选上继续叠同义 prompt。该阶段版本仍为 `1.5.5`，没有创建 `v1.5.6` tag，也没有调用 ClawHub 或 SkillHub 发布。详细证据见 `tests/evidence/review-reference-routing-1.5.5-followup-blocked.md`。

2026-07-10 继续固定 `v1.5.2`、`v1.5.3`、`v1.5.4`、`v1.5.5` 和本轮起点做版本追溯、真实 Luna 写稿 A/B、`workflow.md` 拆分因果消融及独立净稿实验。`v1.5.2` 已可复现材料旁白，canonical Markdown 此后没有缩短；受控交换 workflow 的结果不支持“拆段导致旁白”的因果结论。父级显式编排第二个 cleaner agent 时 6 篇清稿均由独立 verifier 判定通过，但把按需 cleaner 路由写入 canonical skill 后，真实 writer 未调用子代理，候选旁白密度由本轮起点的每千字 `1.79` 升至 `2.16`，并发生一次 `拟先` 到 `考虑先` 的语气漂移。两名 blind verifier 都判候选和基线为发布阻断，因此产品改动、临时 reference、测试和 P102 已全部回滚，只保留证据。回滚后定向 unittest `86/86`、全量 `121/121`、本轮起点消融双方 `101/101`、`v1.5.5` 对比 current `101/101`、Promptfoo smoke `20/20` 通过。该段同样是 finalizer 实验前的阶段性暂停记录，详细证据见 `tests/evidence/material-narration-version-ab-and-cleaner-rollback-20260710.md`。

后续按“确定性检测 + 独立二次修订 + 不变量消融”又隔离测试三种 finalizer 实现。主 Luna A/B/C 中 C 可把确定性旁白命中降为 0，并达到 10/10 场景通过；但两轮 GPT-5.5 强模型复测和独立 cold review 均发现 C 会新增未提供的培训、身份、采购或审批事实，且发生因果与状态外扩，违反“不新增事实”和不变量 100% 的验收条件。因此三种 finalizer、临时 validator、约束包、修订编排和相关测试均完整排除，不进入 canonical skill、reference、正式测试或三平台发行包；pre-finalizer 基线固定为 `a444c51b70c168a0f3c8e6e360d403316630e2d3`。

最终发布裁决：保留 `a444c51` 之前已验证的字面引用边界、只输出正文优先级、渐进式 reference 路由、评测 provider 和发布链修复；长文偶发材料读取旁白作为继承自 `v1.5.5` 的剩余风险记录，不宣称已解决。finalizer 连续三种实现未达到语义不变量门槛后，不再继续向 prompt 堆同义禁令，也不再阻断这些独立正向修复进入 `1.5.6`；发布仍须通过版本同步、双基线消融、真实 writer/verifier、全量测试和三平台实况核验。

发布前又用 5 个独立 Luna writer 对真实 pre-finalizer 稿件测试用户自然语言二次提醒，覆盖 600—800 字阶段报告、900—1100 字调研报告、3000—3300 字多附件可研、300—450 字培训简报和引语/拟办状态保护；另用 GPT-5.5 与 GPT-5.6 Sol 独立盲审。二次提醒可清除大部分可见旁白，但不能视为稳定解决：S1 两版分别 412、538 字，均低于下限，后一版还出现异常残片“屾讯”；S3 普通版 2663 字不足，明确篇幅版 3190 字但有程序性泛化和语义空转；S5 以近义重复凑到 300 字；只有 S7 稳定通过，S2 为 PASS/WARN 分歧。因此二次自然语言提醒只作为用户可尝试的修订方式，不作为默认兜底、发布能力承诺或“旁白已解决”证据；不再为此追加 prompt。详细证据见 `tests/evidence/release-1.5.6.md`。

最终 cold review `019f4bbd-a09f-7cf0-add1-01e405de5c92` 发现并复现 OpenClaw 压缩入口没有同步“只输出正文优先”，规则 5 和规则 13 仍可能无条件追加正文外缺项。已只在 `tools/sync_adapters.py` 的 OpenClaw 摘要模板补齐交付优先级，并增加 unit 断言和 P103 消融守卫；canonical prompt 未改。修复后 `v1.5.5` 为 95/102、pre-finalizer 为 101/102、current 为 102/102，复核代理确认 `resolved=true`、`publish_blocking=false`。

发布完成：发布 commit/tag 为 `7e485700a49a924abf973656d2bb0e9630054890`。GitHub main、tag 和 release 已公开；ClawHub 1.5.6 已公开且 moderation `clean`；SkillHub 已向精确项目提交 1.5.6，返回 `skillId=70149`、`versionId=133850` 和 `tags.latest=1.5.6`，但公开 latest/search 仍为 1.5.5，三项审核 pending。详细命令、测试矩阵、finalizer 拒绝证据、自然语言二次修改结论和平台字段见 `tests/evidence/release-1.5.6.md`。

## 1.5.6 后续 span-only finalizer 实验

2026-07-11 在被忽略的 `output/finalizer-experiments/attempt4/` 实现“结构化约束包 -> 模式感知检测 -> 独立 claim verifier -> 一次精确 span patch -> 不变量复核 -> 快照回滚”原型。实际 `v1.5.6` tag 为 `7e485700a49a924abf973656d2bb0e9630054890`，pre-experiment HEAD 为 `8a0144d1f359e3f77e1c1618f87a06b79e5d7f4d`；不要沿用计划中已失真的 `d6414a3` tag SHA。

20 篇审校标注只用于校准线索；Luna A/B 各 24 篇、GPT-5.5 16 篇及 GPT-5.5/GPT-5.6 Sol 双盲复核均未证明 C 稳定优于 B。两项共识安全 patch 在全量复核后仍失败，故接受数为 0，C 的 24 篇正文全部字节级回退为 B。H09 多轮和 H10 compact 后快照恢复均精确通过，说明宿主快照可用，但不能把它表述为模型记忆能力。该 finalizer 不进入 canonical skill、reference、正式测试或发行包；不要在此结果上追加全文重写、通用 cleaner 或同义 prompt。详细证据见 `tests/evidence/finalizer-span-patch-experiment-20260711.md`。

## 1.5.6 后续二次修改风险收敛实验

2026-07-11 又在 ignored `output/finalizer-experiments/attempt5/` 测试用户触发二修和宿主检测/repair 双层方案。12 类新 holdout 覆盖稀疏/长文、未决纪要、字段材料、引语、只审不改、只输出正文、定点时间、范围情态、事实外扩和精确回滚；Luna 低/中思考两轮各 36 篇。

三种最小 prompt 候选均在第一轮回退：完整边界会反向泄露，静默局部规则和纯回滚规则都会改坏标题、换行、标点或字段格式，R12 从当前 A 的 3/3 PASS 退为 0/3。达到三次停止条件后未修改 canonical。宿主 C1 不通过；C2 fail-closed 第一轮将 FAIL 从 12 降到 9，但第二轮 Sol 判 A/C 均为 27 PASS、9 FAIL，GPT-5.5 只减少 1 个 WARN，未达到连续三轮稳定优于 B，因此停止第三轮且不下沉。精确回滚继续依赖宿主 SHA/base64 快照，不靠 prompt 或模型记忆。详细证据见 `tests/evidence/second-revision-risk-convergence-20260711.md`。

## 1.5.7 窄修复发布候选

1.5.7 只发布 `8a0144d` 已验证的最小修复：删除容易诱发材料旁白的“从已给材料看，问题集中于……”，改为直接列明已确认问题的对象、数量和状态，无法支持的结论继续放正文外待确认。未加入 finalizer、detector、repair、embedding、外部依赖、二次修改候选 prompt 或新写稿工作流。

干净分支 `codex/release-1.5.7` 从 `afc85dc` 创建，并保留最新实验结论记录；误跟踪实验输出提交不是该分支祖先，`output/` 不进入 Git 发行内容。发布前验证为定向/全量 unittest 均 123/123，`v1.5.6` 消融 baseline 101/102、current 102/102，Promptfoo smoke 20/20，真实文章关键要素 61/61，quick_validate 和 `git diff --check` 通过。4 个 Luna writer 真实 sanity 经独立 GPT-5.5 verifier 判 3 PASS、1 WARN、无发布阻断；WARN 为稀疏问题清单稿篇幅不足和一句边界性概括，不追加 prompt。cold review 另发现 ClawHub PowerShell tags 示例未整体引用和 canonical 下 ignored pyc 不能直接递归打包；前者已用文档加测试最小修复，后者改用 19 文件干净市场目录，不删除本地缓存。修复后 cold re-review 为 `resolved=true`、`publish_blocking=false`；仍须完成三平台实况核验，详细证据见 `tests/evidence/release-1.5.7.md`。

## 1.5.7 后续旁白交付检测实验

2026-07-12 已撤销修改全局硬边界的稀疏扩写候选。当前实验只给 `prose_lint.py` 增加默认关闭的 `draft-body`、`review-only`、`gap-note-allowed` 交付模式，检测材料读取旁白、约束自证、交付说明、AI 身份和英文思考残片；不自动改写，不改变 canonical 写稿 prompt 或默认 workflow。独立 cold review 的五类漏扫/误报及镜像漂移均已修复，最终 `publish_blocking=false`。

三名不同档位 agent 均证明现有 Markdown 会把“现有材料仅反映……”和“本报告仅反映已给事实……”误读为可留正文；一条按来源区分业务事实与模型输入判断的候选说明可将三者全部纠正，同时不误伤正式报告过渡语。该候选本轮只记录，不进入 prompt；必须按本文件的真实写稿测试分级规则完成短稿 A/B 后才能决定是否采用。详细证据见 `tests/evidence/narration-delivery-mode-and-prompt-comprehension-20260712.md`。

## 1.5.7 后续稀疏压力与核心 workflow 复核

2026-07-12 对 1.4.10、1.4.12、1.5.2 和 1.5.7 做历史追溯，并用同一 Luna 低思考 writer 对“仅三项事实但强制 650-800 字”和正常短稿做版本对比。早期 1.4.10、1.5.2 在冲突长稿中已出现重复、材料旁白和事实动作外扩；1.5.7 选择短写且不补造。该压力组合只用于诊断，不能把未达字数单独判为正常写作功能退化。

短审核 workflow 和 13 个 Markdown 文件的广泛清晰化候选均未通过真实 A/B：低思考候选出现一次用户指令遗漏、旁白误判和无关外文残片。两名 blind verifier 未证明候选稳定优于 1.5.7，故全部撤回。canonical 继续保留“小段写完先审、小节写完再审、全文合并后做总审”，不得把“小节不审、全文仅审一次、最多修订一次”等候选重新混入文字精简。

本轮只保留默认关闭、只检测不改写的 delivery lint 精度调整，材料范围句按 medium 人工判断，明确自证、英文思考和交付说明仍按 high；另增加核心 workflow 测试守卫。详细取证和验证见 `tests/evidence/sparse-stress-and-core-workflow-forensics-20260712.md`。
