# Reference 逐页架构归属表（2026-09-12）

基线：`main@1ce71123`。本表覆盖该基线的全部 50 个 reference；候选新增页另列，数量随职责拆合变化。`rewrite` 表示本批已按新职责重写，`retain` 表示保留既有稳定语义并重新接入路由；两种状态都必须在后续组合实写中验证，不能把文件状态当成功能等价。

| # | 基线 reference | 新架构分区 | 新页/归属 | 处置 | 归属与保留理由 |
|---:|---|---|---|---|---|
| 1 | `ai-compute-docs.md` | transaction/overlay | 算力场景附加页 | rewrite | 统一算力字段、技术、成本、SLA、安全和验收；不承载报告/方案/采购骨架。 |
| 2 | `ai-compute-examples.md` | transaction/overlay | 算力示例资料 | retain | 仅用户明确要求示例时读取，避免普通算力稿件伴读。 |
| 3 | `anti-ai-patterns.md` | language/review | 抗 AI 味与语言风险 | rewrite | 保留旁白、过程泄露、模板化表达、论断强度和段落节奏等语言风险；写稿与审核均经过检查。 |
| 4 | `argument-chains.md` | workflow | 依据与段落关系能力页 | rewrite | 保留判断与依据、合理分析、必要性与措施区分、实测/测算/估算/假设口径；移除跨文种骨架表，文种功能顺序由各自主叶承载。 |
| 5 | `compatibility-scene-routing.md` | transaction/router | 兼容场景分流页 | retain | 为新闻、意见建议、投诉反映、整改等已有场景选专页。 |
| 6 | `compression-details.md` | workflow/tool | 篇幅检查与调整页 | rewrite | 用独立 scripts/draft_length.py 扫描正文篇幅，再按材料调整；保留压缩取舍与超限/不足处理，后续文稿复核由 prose_lint.py 兜底。 |
| 7 | `delivery-review-gate.md` | pro/archive | 独立 Pro Hook 保存分支 | delete | MIT 候选移除本页及 Hook 门禁；原资产保存在 codex/pro-hooks-preserved-20260912@3b6f273b，许可与验证边界见 pro-hooks-next.md；不是删除普通脚本能力。 |
| 8 | `external-research.md` | workflow/tool | 通用写法与来源核查页 | rewrite | 用户要求搜索、时效事实、尚不熟悉的文种/材料类型或通用写法核查时定向研究；具体业务事实仍以用户材料为准。 |
| 9 | `field-editing.md` | workflow | 字段编辑页 | retain | 处理字段拆行、增删和表单边界，不带入完整文种规则。 |
| 10 | `final-review-layers.md` | review | 事实与文种复核页 | rewrite | 按事实与状态、文种与结构、模板与文内完整性三项核对本轮范围；删除跨文种骨架和提前交付动作，采用当前主文种要素。 |
| 11 | `formal-addressing.md` | language | 称谓与行文关系页 | rewrite | 统一上下行、平行关系、人物称谓和收束语。 |
| 12 | `format-gbt9704.md` | workflow/tool | Word/GB/T 9704 格式页 | retain | 仅格式交付模式加载，不混入正文事实规则。 |
| 13 | `formulaic-language.md` | language | 固定用语能力页 | rewrite | 保留开端、承启、引叙和收束能力，不重复文种骨架。 |
| 14 | `genre-checklist-feasibility-review.md` | review/genre | 可研专项复核页 | retain | 用户点名可研摘要核对时直达，避免无关总审。 |
| 15 | `genre-checklist-report.md` | genre/review | 报告文种核对页 | retain | 报告功能和要素核对，配合报告主叶使用。 |
| 16 | `genre-checklist-request.md` | genre/review | 请示/申请核对页 | retain | 请示、申请的请批和办理要素核对。 |
| 17 | `genre-checklist.md` | router/review | 未覆盖文种功能反查页 | rewrite | 只做功能反查，不再集中承载多个文种骨架。 |
| 18 | `genre-playbook-advisory-feedback.md` | genre/transaction | 意见建议主叶 | retain | 已有稳定意见建议语义，接入兼容场景分流。 |
| 19 | `genre-playbook-complaint-reflection.md` | genre/transaction | 投诉/情况反映主叶 | retain | 保留问题、对象、请求和事实状态边界。 |
| 20 | `genre-playbook-correspondence.md` | genre | 函/复函主叶 | retain | 负责函件目的、对象、事项和收束。 |
| 21 | `genre-playbook-deliberation-deployment.md` | router | 旧决定/部署混合页 | delete | 决定、决议、议案、公报、命令各由独立主叶承载，部署另归 genre-playbook-deployment.md；中间共享页 genre-playbook-deliberation.md 同步退役。 |
| 22 | `genre-playbook-institution-rules.md` | genre | 制度规章主叶 | retain | 制度、规定、办法、细则和规程的规范结构。 |
| 23 | `genre-playbook-minutes.md` | genre | 会议纪要主叶 | retain | 保留会议事实和议定事项状态，不补讨论过程。 |
| 24 | `genre-playbook-news-commentary.md` | genre | 新闻评论主叶 | retain | 新闻评论独立成文种，不通过兼容页稀释。 |
| 25 | `genre-playbook-news-message.md` | genre | 新闻消息主叶 | retain | 新闻消息、活动报道和编者按的事实结构。 |
| 26 | `genre-playbook-notice-publication.md` | router | 旧通知/公开发布混合页 | delete | 通知与公开发布已拆为 `genre-playbook-notice.md`、`genre-playbook-publication.md`，旧页继续存在会把两个主文种重新混读。 |
| 27 | `genre-playbook-plan-construction.md` | genre | 方案主叶 | retain | 方案目标、任务、步骤、保障和状态边界。 |
| 28 | `genre-playbook-procurement-review.md` | genre/transaction | 采购审查主叶 | retain | 采购审查和评审材料，不承载算力三套骨架。 |
| 29 | `genre-playbook-project-application.md` | genre | 项目申请主叶 | retain | 项目申请的依据、目标、内容和请批事项。 |
| 30 | `genre-playbook-remediation-plan.md` | genre/transaction | 整改方案主叶 | retain | 整改问题、措施、责任和状态保持原强度。 |
| 31 | `genre-playbook-request.md` | genre | 请示/申请主叶 | retain | 请批、依据、事项和结语的完整骨架。 |
| 32 | `genre-playbook-research-feasibility.md` | router | 旧调研/可研混合页 | delete | 调研/研究与可研的决策功能已拆为 `genre-playbook-research.md`、`genre-playbook-feasibility.md`。 |
| 33 | `genre-playbook-speech-address.md` | genre | 讲话/致辞/演讲主叶 | rewrite | 保留场合、身份、听众、主题、事实与收束；完整主持会序和职责述职分别迁入新主叶。 |
| 34 | `genre-playbook-work-summary.md` | genre | 工作总结主叶；工作要点独立；周期汇报归报告 | rewrite | 回顾、经验和有据展望留在总结；未来任务归 work-priorities；周报/月报复用报告并按需字段处理。旧语义和来源见 summary-priorities-separation-r1。 |
| 35 | `genre-playbooks.md` | router | 旧文种混合总页 | delete | 原功能由独立文种页及必要场景附加页承接；通知/公开发布、调研/可研、决定/决议/议案/公报/命令等分别落页，genre-routing.md 与 genre-checklist.md 仅处理选路或未覆盖功能。 |
| 36 | `genre-routing.md` | router | 主文种与行文关系路由 | rewrite | 只判定文种、对象关系和冲突，输出首叶。 |
| 37 | `handling-elements.md` | workflow | 办理要素能力页 | rewrite | 按主体对象、事项依据、动作状态、条件期限、支撑反馈和文内字段核对；删除多文种要素表，必要项由当前主文种判断，缺项按信息选择与定向研究规则处理。 |
| 38 | `information-selection.md` | workflow | 事实选择与状态页 | rewrite | 区分事实、直接分析、待定状态和实质缺项。 |
| 39 | `official-style.md` | language | 正式表达能力页 | rewrite | 处理语体、句式、证据强度和去口语，不增加事实。 |
| 40 | `proofreading-checklist.md` | review | 轻量校对页 | rewrite | 校验数字、日期、术语、引用和稿内一致性。 |
| 41 | `prose-lint-usage.md` | tool | 脚本调用契约页 | rewrite | 规定路径、参数、结果回流和失败解释，不替代文种判断。 |
| 42 | `reference-index.md` | router | 主文种与条件加读索引 | rewrite | 按稿件用途选唯一主叶，列明必要附加页；移除与首页重复的交付模式表，机器路由 manifest 留在维护区。 |
| 43 | `review-checklist.md` | review | 统一审稿检查页 | rewrite | 自然语言审核默认检查全文，含事实、文种、结构、语言与抗 AI 味、格式；吸收原直接审核页的合理推断、防过严、风险分层、主体与仅审边界，交付形态统一归 delivery.md。 |
| 44 | `review-direct-checklist.md` | review | 合并入 review-checklist.md | delete | 全文审核与范围限定共用统一审稿页；重要证据判断、合理推断、次级材料可选、仅审不改语义已蒸馏保留，取消重复首叶和跳过全面检查的支路。 |
| 45 | `short-draft-naturalness.md` | workflow | 短稿自然度页 | retain | 保留章节、小标题转自然段及一两句话承载事项的短格式能力；轻量卡只决定何时读取，不复制这些正文动作。 |
| 46 | `speech-person-order.md` | overlay | 讲话与主持人物顺序附加页 | retain | 仅讲话、致辞、演讲或主持开场出现具体人物排序需求时叠加。 |
| 47 | `structure-editing.md` | workflow | 结构编辑页 | retain | 处理增删、移动、标题和段落关系。 |
| 48 | `task-route-cards.md` | router | 轻量任务选择卡 | rewrite | 材料较少/短稿与局部修改作为两个独立成立的条件；保留唯一主文种，分别转短稿、结构或字段页，完成后衔接首页编号检查。 |
| 49 | `technical-terms.md` | transaction/overlay | 技术术语附加页 | retain | 算力或技术稿件明确需要术语核对时才加载。 |
| 50 | `workflow.md` | workflow | 拆入入口与共性页 | delete | 原起草、改写、压缩和合稿路由及编号检查由 `SKILL.md` 承接；事实与状态、结构动作、篇幅调整分别归 `information-selection.md`、`structure-editing.md`、`compression-details.md`，办理要素和论证关系按需归 `handling-elements.md`、`argument-chains.md`。本页已无独立职责，删除以免形成流程副本。 |

## 新构造页（不占用基线 50 行）

这些页面承接被删除或合并的旧页面功能。主文种由 `reference-index.md` 选取，事务页按明确场景叠加，交付页在检查完成后读取；机器路由 manifest 在维护区记录对应关系：

| 新页 | 用途 |
|---|---|
| `genre-playbook-notice.md` | 通知独立主文种 |
| `genre-playbook-publication.md` | 公告、公示、通告的公开发布功能 |
| `genre-playbook-bulletin.md` | 通报情况、表扬先进和批评问题的独立主文种 |
| `genre-playbook-research.md` | 调研/研究独立主文种 |
| `genre-playbook-feasibility.md` | 可行性研究独立主文种 |
| `genre-playbook-procurement-announcement.md` | 采购公告独立主文种 |
| `genre-playbook-decision.md` | 有权机关作出重要事项决定，明确对象、范围和执行要求 |
| `genre-playbook-resolution.md` | 会议讨论并通过的重大事项，保持集体议决与通过状态 |
| `genre-playbook-motion.md` | 人民政府向同级人大或其常委会提请审议，保留提请关系 |
| `genre-playbook-communique.md` | 公开发布已形成的重要事项或共识，保留发布范围与各方归属 |
| `genre-playbook-order.md` | 有权机关依法发令，核对权限、令号、公布事项与施行信息 |
| `genre-playbook-deployment.md` | 部署安排事务页 |
| `genre-playbook-reply.md` | 批复独立主文种 |
| `genre-playbook-opinion.md` | 意见独立主文种 |
| `genre-playbook-explanation.md` | 说明独立主文种 |
| `genre-playbook-report.md` | 报告、情况报告和情况说明独立主文种 |
| `genre-playbook-meeting-host.md` | 会议主持词、主持串词按既定会序组织环节、程序状态和转场 |
| `genre-playbook-duty-report.md` | 个人或班子书面与现场述职，围绕职责、履职事实、实绩归属、问题和改进方向 |
| `genre-playbook-work-priorities.md` | 年度、阶段或专项工作要点，组织未来任务、责任与节点，保留拟议状态 |
| `transaction-remediation-report.md` | 整改进展/整改情况报告事务附加页 |
| `transaction-feedback-report.md` | 反馈情况报告事务附加页 |
| `delivery.md` | 成稿/审稿意见交付，默认独立文后提示、未解决事项及明确省略提示的偏好 |

## 台账使用规则

- `rewrite`、`retain` 和 `delete` 都必须有证据；`retain` 不是免审，`delete` 必须说明替代页和功能闭合。
- 每个新页只能有一个主归属；同一条可执行语义不得在多个页重复成为硬规则。
- 后续填充时，为每行补充旧页语义摘录、候选页段落位置、允许读取集合、排除集合和真实写稿证据编号。
- 只有 50 行全部闭合，且组合 A/B 排除候选独有硬回退后，才可进入合并判断。
