# Anonymous AGENTS.md review packet

Review two alternative repository engineering control files for a Skill project. Judge only:

1. engineering executability and clarity;
2. duplicated or conflicting rules;
3. stale release state or historical log leakage;
4. accidental product-writing rules in the engineering control plane;
5. Git, testing, anonymous review, DIFF attribution, release and security boundaries;
6. Hook packaging distinctions across SkillHub and ClawHub.

Do not rewrite either file. For each arm, return PASS/WARN/FAIL, concrete line-level issues, and a final preference A/B/tie. A shorter file is not automatically better. Do not infer identity, history or expected outcome.

## Arm A

# AGENTS.md

## 作用范围

本文件只规定本仓库的开发、Git、测试、评分、匿名盲审、DIFF 归因、发行和安全纪律。

**产品写稿规则不得进入 `AGENTS.md`。** 文种、写作行为、生成要求和运行时约束只写入 canonical Skill 及其 references；候选结论、评测题面和发布流水进入相应 evidence，不在这里复述。

发布事实和维护历史见 [`docs/evidence/README.md`](docs/evidence/README.md)。历史文件不是当前指令。

## 仓库与发行表面

- `chinese-official-writing/` 是 canonical 产品包；`skills/`、`.agents/`、`.qwen/`、`hermes/`、`openclaw/` 是适配或镜像表面。同步后验证字节和路由一致。
- `tools/`、`evals/`、`tests/` 是工程与评测工具；`tests/evidence/` 保存预注册、消融、盲审和真实执行证据；`docs/evidence/` 保存维护历史和索引；`output/` 默认不提交。
- SkillHub 可携带可选 Codex Hook 伴随物，Hook 资产放在专属 `hooks/` 目录；ClawHub 包排除 Hook 和交付门禁资产。包内存在、插件安装、功能启用、信任确认和真实执行是五项独立事实，必须分别验证。

## 修改与 Git

1. 修改前确认仓库根、分支、HEAD、工作树、固定基线和用户授权。保留用户改动；来源不明的修改先审计。
2. 发布、候选复现和基线比较使用独立 worktree；固定基线记录解引用 commit，不用浮动分支名替代。
3. 所有代码和文档修改均提交到 Git。commit message 说明目的、范围和实际验证。
4. 外部仓库或平台状态变更须取得当次明确授权。未经授权不得合并 `main`、推送、移动 tag、创建 Release 或上传平台。
5. 禁止破坏性重置和无边界批量清理。删除、覆盖、force push 或改动发行 tag 前精确核对目标并取得授权。
6. 每累计 5 次 commit，或修改范围明显扩大时，暂停并执行轻量 review、基线对比、轻量消融和回归检查。

## 研究、review 与归因

1. 先用源码、实际调用链、日志或可重复命令确认问题。外部报告和候选实现只作线索。
2. 只修复至少三份真实样本共同指向的机制，或可确定证明的等义重复；保持原子化，避免一例一修和无关重构。
3. 实质改变产品默认行为、核心工具链或发行链路前，先与固定发行基线比较并向用户说明方案、原因和回退风险。
4. 新构想先检索官方文档、GitHub、ClawHub、SkillHub 和相关社区。禁止直接誊抄第三方代码、脚本、正则、模板库、大段 prompt、固定话术或模板正文；候选不新增重排版引擎，不扩大默认联网，不默认强制确认，不破坏用户模板和字段式材料，落地后必须和上一基线做消融。
5. 大范围 diff、长文件和第三方实现优先交给独立上下文；主线程以源码、diff、测试或日志交叉验证结论。
6. 分开记录静态发现、真实执行、独立验证、可复现修复和消融结果。DIFF 只评价候选相对固定基线造成的变化；基线共有问题、抽样波动、环境失败和候选独有回退分别报告。

## 测试与评分

1. 可交付前运行与风险相称的 smoke 或最小验证；无法运行时记录原始错误和人工核验方法。
2. 文档和工程元数据改动至少运行直接相关测试、链接或标题检查及 `git diff --check`。产品、脚本或评测逻辑改动按影响面增加 unit、Promptfoo smoke、quick validate、镜像一致性、编译和固定基线消融。
3. `tools/run_real_prompt_ablation.py` 是不调用 LLM 的确定性工程门，不能替代真实链路执行或独立质量评分。
4. canonical Skill、references 或默认行为实质变化时，对固定发行基线运行真实链路 A/B，并由独立 verifier 复核；样本量随风险升级。
5. A/B 与多候选评分预先固定基线、输入、环境和判分口径。裁判材料先匿名并打乱，解盲前不泄露候选身份。
6. 保留裁判原始记录，分别报告硬边界、质量、胜负或难分、无效样本和理由。模型票数不能覆盖确定性失败；真实执行、verifier 和人工 review 冲突时保留分歧并说明最终依据。
7. 不伪造测试结果。未运行的命令不得写成通过；首次环境失败和后续有效复跑同时保留。

## 发行与回执

1. 授权只覆盖用户点名的平台和版本，不延伸到其他平台或后续版本。
2. 发布前固定上一发行 tag 的解引用 commit，核对 ancestry、精确 diff、版本面、镜像、工作树、测试、清洁包 allowlist、文件数、禁入文件和 fingerprint。
3. 分别核验 annotated tag object、tag 解引用 commit、发布提交、远端分支和 GitHub Release。发布后的证据提交可以推进 `main`，不得移动已发布 tag。
4. dry-run、上传回执、公开 `latest` 或 tag、审核与安全状态、来源证明和搜索索引传播分别记录；公开索引滞后不构成重复提交理由。
5. 常规发布范围为 GitHub、ClawHub 和 skillhub.cn。小红书 Red SkillHub 默认排除，只有用户逐次明确恢复授权才可触碰。
6. 发布报告记录提交、tag、测试、包哈希或 fingerprint、平台回执、未闭环项和剩余风险，不把候选基线称为已发布版本。

## 安全与交付

- 不提交密钥、令牌、Cookie、登录态、私有地址或未脱敏外部数据；日志和证据先检查敏感信息。
- 外部命令、上传和删除采用最小权限与精确目标；平台状态检查优先只读。
- 不改任务范围外的 Skill、服务、平台或工作树，不把临时输出、外部 checkout、缓存和未跟踪目录带入候选。
- 交付时用通俗语言报告修改摘要、branch、commit、实际测试结果、量化变化和剩余风险。

## Arm B

# AGENTS.md

## 工程控制面

本文件是本仓库制造、维护和发布 Skill 的工程控制面，只规定开发环境、Git、worktree、提交、测试、回归、评分、匿名盲审、DIFF 归因、发布回执和安全边界。

**产品写稿规则不得进入 `AGENTS.md`。** 写作行为、文种规则、生成要求和运行时约束只允许存在于 canonical Skill 及其 references；不得在本文件复制、改写、概括或追加，也不得把候选的具体写作结论或长篇发布流水写回根文件。

当前正式发行版为 `v1.6.0`。发布事实和历史入口见 [`docs/evidence/README.md`](docs/evidence/README.md)；历史材料不是当前指令。

## 仓库结构

- `chinese-official-writing/`：canonical 产品包。
- `skills/`、`.agents/`、`.qwen/`、`hermes/`、`openclaw/`：适配或镜像表面；需要同步时必须用既有工具并验证字节一致性。
- `tools/`、`evals/`、`tests/`：工程工具、评测入口和回归测试。
- `tests/evidence/`：逐版发布、预注册、消融、盲审和真实执行证据。
- `docs/evidence/`：不应在每次 run 注入的维护历史和索引。
- `output/`：临时或生成证据；除非任务明确要求，不得把生成物混入产品包或提交。

## Git、worktree 与提交

1. 开始修改前确认仓库根、当前分支、HEAD、工作树状态和任务授权边界。用户已有改动必须保留；不明来源的修改先审计，不得覆盖。
2. 发布、候选复现和基线比较优先使用独立 worktree。固定基线必须记录解引用 commit，不得用浮动分支名代替。
3. 所有代码或文档修改必须通过 git commit 留痕。commit message 必须说明修改目的、影响范围和实际验证方式。
4. 未经用户明确授权，不得合并 `main`、移动 tag、推送、创建 Release 或向任何平台提交。
5. 禁止破坏性重置和无边界批量清理。删除、覆盖、force push 或改动发布 tag 前必须精确核对目标并取得明确授权。
6. 每累计 5 次 commit，或修改范围明显扩大时，暂停开发，执行轻量 review、基线对比、轻量消融和回归检查。

## 修改与 review

1. 先用源码、实际调用链、日志或可重复命令确认问题，再改动；外部报告和候选实现只能作为线索。
2. 只修复已归纳的共性机制，保持改动小而可复用；避免一例一修、上帝函数、魔法数字和无关重构。
3. 拟实质改变产品默认行为、核心工具链或发布链路时，实施前必须与固定发行基线比较，向用户说明现状、方案、原因和回退风险；只有取得明确同意后才可继续。
4. 涉及产品行为、核心工具链或发布链路的新构想，必须先检索官方文档、GitHub、ClawHub、SkillHub 和相关社区，确认成熟方案或可复用组件；只采用可由源码、diff、测试或日志验证的结论。禁止直接誊抄第三方代码、脚本、正则、模板库、大段 prompt、固定话术或模板正文；候选不新增重排版引擎，不扩大默认联网，不默认强制确认，不破坏用户模板和字段式材料，落地后必须和上一基线做消融。
5. 大范围 diff、长文件、第三方实现和复杂 review 优先交给 subagent 或独立上下文；结论必须由主上下文以源码、diff、测试或日志交叉验证。
6. Review 必须区分：静态发现、真实执行、独立验证、可复现修复和消融结果。不得用其中一类证据替代另一类。
7. DIFF 归因只评价候选相对固定基线造成的变化。基线共有问题、抽样波动、环境失败和候选独有回退必须分别记录。

## 测试、回归与评分

1. 每次认为任务可交付前，必须运行与风险相称的 smoke test 或最小验证；无法运行时说明原因、原始错误和人工验证步骤。
2. 文档或工程元数据改动至少运行直接相关测试、链接/标题检查和 `git diff --check`。产品、脚本或评测逻辑改动按影响面增加 unit、Promptfoo smoke、quick validate、镜像一致性、编译和固定基线消融。
3. `tools/run_real_prompt_ablation.py` 是确定性工程门，不调用 LLM；它不能替代真实链路执行或独立质量评分。
4. canonical Skill、references 或默认行为发生实质变化时，必须对固定发行基线运行真实链路 A/B，并由独立 verifier 复核；样本量和矩阵按风险升级，不能用确定性工程门替代。
5. A/B 或多候选评分必须预先固定基线、输入、环境和判分口径。交给裁判的材料先匿名并打乱顺序；解盲前不得泄露候选身份。
6. 裁判输出必须保留原始记录，并分别报告硬边界、质量评分、胜负/难分、无效样本和理由。不能凭模型票数覆盖确定性失败。
7. 真实执行、独立 verifier 和人工 review 的结论冲突时不得择优汇报；应保留分歧、复现原样本并说明最终裁决依据。
8. 不允许伪造测试结果。未实际运行的命令不得写成已通过；首次环境失败和后续有效复跑必须同时记录。

## 发布与回执纪律

1. 发布动作必须有当次明确授权。授权只覆盖点名的平台和版本，不自动延伸到其他平台或后续版本。
2. 发布前固定上一发行 tag 的解引用 commit，核对候选 ancestry、精确 diff、版本号、镜像、工作树、测试结果、清洁包 allowlist、文件数、禁入文件和 fingerprint。
3. annotated tag object、tag 解引用 commit、发布提交、远端分支和 GitHub Release 分别核验。发布后的维护提交可以推进 `main`，不得移动已发布 tag。
4. dry-run、上传回执、公开 `latest`/tag、审核与安全状态、来源证明和搜索索引传播是不同事实，不得互相推断。来源证明缺失时记 `unavailable`。
5. 已取得正式提交回执后，公开索引滞后或审核 pending 不构成重复提交理由。
6. 常规发布范围为 GitHub、ClawHub 和 skillhub.cn。小红书 Red SkillHub 默认排除，只有用户逐次明确恢复授权才可触碰。
7. 发布报告必须记录提交、tag、测试、包哈希或 fingerprint、平台回执、尚未闭环项和剩余风险；不得把候选基线称为已发布版本。

## 安全与交付

- 不提交密钥、令牌、Cookie、登录态、私有地址或未脱敏的外部数据；日志和证据先检查敏感信息。
- 外部命令、上传和删除操作遵循最小权限与精确目标原则。平台状态检查优先只读。
- 不修改任务范围外的 Skill、服务、平台或工作树；不把临时输出、外部 checkout、缓存和未跟踪目录带入候选。
- 交付时用通俗语言报告修改摘要、branch、commit hash、实际测试命令与结果、量化变化和剩余风险。

