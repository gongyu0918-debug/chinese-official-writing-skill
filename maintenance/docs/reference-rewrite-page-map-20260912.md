# Reference 逐页架构归属表（2026-09-13，2.0 开发候选）

固定基线为 `main@1ce7112303172478faa2392667a2de1098eb912c`；本表活动状态为在R20基础上采用R23议案修复及用户独立复核范围纠正的开发候选，完整指纹为 `9fade115eae2892cf4ac2af3d9587f784d2b476c200ef32ab9eca128d50ec18a`，见[R23采用记录](../../output/motion-content-r23-adopted/adoption.json)。50 个旧页全部列名：37 个同名路径仍在、13 个退役或迁出；另新增 30 页，共 67 页，其中 40 个具名主叶、43 条路线（40 个主叶加 3 条事务叠加路线）。这是 2.0 开发候选的工程映射，不是 1.x 对照验收或发布结论。
当前有限收口见[R23状态](../tests/evidence/completion-audit-r23/status.md)；历史阶段结果与未完成项见[共性层进度](rewrite-common-layer-progress-20260913.md)及[R19整体完成度审计](../tests/evidence/completion-audit-r19/report.md)（[JSON](../tests/evidence/completion-audit-r19/report.json)）。下表保留50行旧页归属、30个新增页及原链接；来源性审计备注须结合后续证据判读，逐页归属不代表逐条语义、真实稿件或整体1.x等价已经闭合。

“同名承接”表示职责仍落同名文件，不表示内容未改；“拆分承接”表示职责分到多个现存页；“退役/迁出”说明替代或保存位置。旧表的 rewrite/retain 是阶段性文件处理标签，本次按当前职责更新，均不等于逐条语义或真实写稿通过。表内产品链接指向已应用的 canonical。各行映射以旧 Git 对象、冻结候选及下列审计共同定位，允许读取与排除集合见[路由 manifest](../specs/reference-route-manifest.json)；它们是静态契约，实际读页另见原生证据。

| # | 基线 reference | 新架构分区 | 当前页/归属 | 处置 | 归属与保留理由 |
|---:|---|---|---|---|---|
| 1 | `ai-compute-docs.md` | transaction/overlay | [ai-compute-docs.md](../../chinese-official-writing/references/ai-compute-docs.md)、[genre-playbook-feasibility.md](../../chinese-official-writing/references/genre-playbook-feasibility.md)、[genre-playbook-plan-construction.md](../../chinese-official-writing/references/genre-playbook-plan-construction.md)、[genre-playbook-technical-requirements.md](../../chinese-official-writing/references/genre-playbook-technical-requirements.md) | 拆分承接 | 算力需求、资源/Token、成本、SLA、安全与验收留在同名附加页；旧可研/方案骨架归各自主叶，独立技术需求归新技术需求主叶。普通服务器或接口不因关键词单独触发算力。 |
| 2 | `ai-compute-examples.md` | transaction/overlay | [ai-compute-examples.md](../../chinese-official-writing/references/ai-compute-examples.md) | 同名承接 | 仅用户明确要求示例时读取，避免普通算力稿件伴读。 |
| 3 | `anti-ai-patterns.md` | language/review | [anti-ai-patterns.md](../../chinese-official-writing/references/anti-ai-patterns.md) | 同名承接 | 必经语言检查保留旁白、过程泄露、必要否定、判断强度、有效排比、业务声明和原意；原生质量及 1.x 专项等价须按对应证据判断。 |
| 4 | `argument-chains.md` | workflow | [argument-chains.md](../../chinese-official-writing/references/argument-chains.md) | 同名承接 | 保留判断与依据、合理分析、必要性与措施区分、实测/测算/估算/假设口径；移除跨文种骨架表，文种功能顺序由各自主叶承载。 |
| 5 | `compatibility-scene-routing.md` | transaction/router | [compatibility-scene-routing.md](../../chinese-official-writing/references/compatibility-scene-routing.md) | 同名承接 | 为新闻、意见建议、投诉反映、整改等已有场景选专页。 |
| 6 | `compression-details.md` | workflow/tool | [compression-details.md](../../chinese-official-writing/references/compression-details.md) | 同名承接 | 用独立 scripts/draft_length.py 扫描正文篇幅，再按材料调整；保留压缩取舍与超限/不足处理，后续文稿复核由 prose_lint.py 兜底。 |
| 7 | `delivery-review-gate.md` | pro/archive | [Pro 保存分支与许可边界](pro-hooks-next.md) | 退役/迁出 | MIT 候选移除本页及 Hook 门禁；原资产保存在 codex/pro-hooks-preserved-20260912@3b6f273b，许可与验证边界见 pro-hooks-next.md；不是删除普通脚本能力。 |
| 8 | `external-research.md` | workflow/tool | [external-research.md](../../chinese-official-writing/references/external-research.md) | 同名承接 | 用户要求搜索、时效事实、尚不熟悉的文种/材料类型或通用写法核查时定向研究；具体业务事实仍以用户材料为准。 |
| 9 | `field-editing.md` | workflow | [field-editing.md](../../chinese-official-writing/references/field-editing.md) | 同名承接 | 处理字段拆行、增删和表单边界，不带入完整文种规则。 |
| 10 | `final-review-layers.md` | workflow/review | [writing-rules.md](../../chinese-official-writing/references/writing-rules.md)、[anti-ai-patterns.md](../../chinese-official-writing/references/anti-ai-patterns.md) | 退役/迁出 | 事实、状态、主文种要素、关联内容及条件性敏感信息核对归 writing-rules；无用重复的语义检查归 anti-ai，独立旧复核页撤下。 |
| 11 | `formal-addressing.md` | language | [formal-addressing.md](../../chinese-official-writing/references/formal-addressing.md) | 同名承接 | 统一上下行、平行关系、人物称谓和收束语。 |
| 12 | `format-gbt9704.md` | workflow/tool | [format-gbt9704.md](../../chinese-official-writing/references/format-gbt9704.md) | 同名承接 | 仅格式交付模式加载，不混入正文事实规则。 |
| 13 | `formulaic-language.md` | language | [formulaic-language.md](../../chinese-official-writing/references/formulaic-language.md)、[genre-playbook-responsibility-letter.md](../../chinese-official-writing/references/genre-playbook-responsibility-letter.md)、[genre-playbook-initiative.md](../../chinese-official-writing/references/genre-playbook-initiative.md)、[genre-playbook-open-letter.md](../../chinese-official-writing/references/genre-playbook-open-letter.md)、[genre-playbook-narration.md](../../chinese-official-writing/references/genre-playbook-narration.md)、[genre-playbook-information-materials.md](../../chinese-official-writing/references/genre-playbook-information-materials.md)、[genre-playbook-report.md](../../chinese-official-writing/references/genre-playbook-report.md)、[genre-playbook-advisory-feedback.md](../../chinese-official-writing/references/genre-playbook-advisory-feedback.md)、[genre-playbook-editorial-note.md](../../chinese-official-writing/references/genre-playbook-editorial-note.md) | 拆分承接 | 用语功能留在同名页；旧事务表的责任书、倡议书、公开信、讲解、宣传类分入独立主叶，情况综合归报告、建议信归合作性建议。旧直接叶不再跳过统一检查；其余旧事务入口见下表。 |
| 14 | `genre-checklist-feasibility-review.md` | review/genre | [genre-checklist-feasibility-review.md](../../chinese-official-writing/references/genre-checklist-feasibility-review.md) | 同名承接 | 用户点名可研摘要核对时直达，避免无关总审。 |
| 15 | `genre-checklist-report.md` | review + genre | [genre-checklist-report.md](../../chinese-official-writing/references/genre-checklist-report.md)、[genre-playbook-report.md](../../chinese-official-writing/references/genre-playbook-report.md)、[genre-playbook-explanation.md](../../chinese-official-writing/references/genre-playbook-explanation.md) | 拆分承接 | 复核留在同名页，起草归报告；使用/体验/评估报告兼顾已有价值、问题、影响与后续建议的组织提示已恢复。说明性材料按用途归说明，不能把情况说明一律改成报告。 |
| 16 | `genre-checklist-request.md` | genre/review | [genre-checklist-request.md](../../chinese-official-writing/references/genre-checklist-request.md) | 同名承接 | 请示、申请的请批和办理要素核对。 |
| 17 | `genre-checklist.md` | router/review | [genre-checklist.md](../../chinese-official-writing/references/genre-checklist.md) | 同名承接 | 用途明确而无适用专页时，按模板、材料及已确认的通用写法成稿，不再反向重选主叶；陌生写法仍按首页核查规则处理。 |
| 18 | `genre-playbook-advisory-feedback.md` | genre/transaction | [genre-playbook-advisory-feedback.md](../../chinese-official-writing/references/genre-playbook-advisory-feedback.md) | 同名承接 | 合作性意见建议和建议信共用同名主叶；保留亲历事实、代表证据、权责与建议状态。法定意见另有主叶，不因建议信外形强加函页或具体调研经历。 |
| 19 | `genre-playbook-complaint-reflection.md` | genre/transaction | [genre-playbook-complaint-reflection.md](../../chinese-official-writing/references/genre-playbook-complaint-reflection.md) | 同名承接 | 保留问题、对象、请求和事实状态边界。 |
| 20 | `genre-playbook-correspondence.md` | genre | [genre-playbook-correspondence.md](../../chinese-official-writing/references/genre-playbook-correspondence.md) | 同名承接 | 按不相隶属关系、收发权限和用途处理商洽、询答、请求批准及审批答复；与上级答复下级请示的批复区分，不因请批措辞机械跳页。 |
| 21 | `genre-playbook-deliberation-deployment.md` | router | [genre-playbook-opinion.md](../../chinese-official-writing/references/genre-playbook-opinion.md)、[genre-playbook-decision.md](../../chinese-official-writing/references/genre-playbook-decision.md)、[genre-playbook-resolution.md](../../chinese-official-writing/references/genre-playbook-resolution.md)、[genre-playbook-motion.md](../../chinese-official-writing/references/genre-playbook-motion.md)、[genre-playbook-communique.md](../../chinese-official-writing/references/genre-playbook-communique.md)、[genre-playbook-order.md](../../chinese-official-writing/references/genre-playbook-order.md)、[genre-playbook-deployment.md](../../chinese-official-writing/references/genre-playbook-deployment.md) | 退役/迁出 | 旧混合骨架按意见、决定权限、会议议决、法定提请、公开发布、依法发令及部署功能分入七页；旧混合页退役。中间页 genre-playbook-deliberation.md 亦退役，不属于固定基线 50 页。 |
| 22 | `genre-playbook-institution-rules.md` | genre | [genre-playbook-institution-rules.md](../../chinese-official-writing/references/genre-playbook-institution-rules.md) | 同名承接 | 制度、规定、办法、细则和规程的规范结构。 |
| 23 | `genre-playbook-minutes.md` | genre | [genre-playbook-minutes.md](../../chinese-official-writing/references/genre-playbook-minutes.md) | 同名承接 | 保留会议事实和议定事项状态，不补讨论过程。 |
| 24 | `genre-playbook-news-commentary.md` | genre | [genre-playbook-news-commentary.md](../../chinese-official-writing/references/genre-playbook-news-commentary.md) | 同名承接 | 新闻评论独立成文种，不通过兼容页稀释。 |
| 25 | `genre-playbook-news-message.md` | genre | [genre-playbook-news-message.md](../../chinese-official-writing/references/genre-playbook-news-message.md)、[genre-playbook-editorial-note.md](../../chinese-official-writing/references/genre-playbook-editorial-note.md) | 拆分承接 | 新闻消息和活动报道的事实结构留在同名页；编者按的编发身份、编发目的和阅读方向迁至独立编者按主叶；有来源观点及有据即时作用留在消息内。 |
| 26 | `genre-playbook-notice-publication.md` | router | [genre-playbook-notice.md](../../chinese-official-writing/references/genre-playbook-notice.md)、[genre-playbook-publication.md](../../chinese-official-writing/references/genre-playbook-publication.md)、[genre-playbook-bulletin.md](../../chinese-official-writing/references/genre-playbook-bulletin.md) | 退役/迁出 | 通知、公开发布、通报分别承接旧功能；通报不再与公告共叶。通知页渠道/邮箱/接收单位不反推发文主体的旧专项边界仍未闭合。 |
| 27 | `genre-playbook-plan-construction.md` | genre | [genre-playbook-plan-construction.md](../../chinese-official-writing/references/genre-playbook-plan-construction.md) | 同名承接 | 方案目标、任务、步骤、保障和状态边界。 |
| 28 | `genre-playbook-procurement-review.md` | transaction/overlay + genre | [genre-playbook-procurement-review.md](../../chinese-official-writing/references/genre-playbook-procurement-review.md)、[genre-playbook-procurement-announcement.md](../../chinese-official-writing/references/genre-playbook-procurement-announcement.md)、[genre-playbook-review-opinion.md](../../chinese-official-writing/references/genre-playbook-review-opinion.md) | 拆分承接 | 同名页改作采购专项附加：需求、规格报价、响应规则和履约条件按需核对；采购公告与独立审查意见分入两个主叶。一般项目审查不必预读采购，只审既有稿件保留原文种。 |
| 29 | `genre-playbook-project-application.md` | genre | [genre-playbook-project-application.md](../../chinese-official-writing/references/genre-playbook-project-application.md) | 同名承接 | 项目申请的依据、目标、内容和请批事项。 |
| 30 | `genre-playbook-remediation-plan.md` | genre/transaction | [genre-playbook-remediation-plan.md](../../chinese-official-writing/references/genre-playbook-remediation-plan.md) | 同名承接 | 整改问题、措施、责任和状态保持原强度。 |
| 31 | `genre-playbook-request.md` | genre | [genre-playbook-request.md](../../chinese-official-writing/references/genre-playbook-request.md) | 同名承接 | 请批、依据、事项和结语的完整骨架。 |
| 32 | `genre-playbook-research-feasibility.md` | router | [genre-playbook-research.md](../../chinese-official-writing/references/genre-playbook-research.md)、[genre-playbook-feasibility.md](../../chinese-official-writing/references/genre-playbook-feasibility.md) | 退役/迁出 | 调研保留样本来源、发现、分析及建议；可研保留比较论证、投资口径、条件结论与有据核实/验证建议。旧稀疏材料一概禁止下一步的收紧已改，但单段可研实写仍有范围反例。 |
| 33 | `genre-playbook-speech-address.md` | genre | [genre-playbook-speech-address.md](../../chinese-official-writing/references/genre-playbook-speech-address.md)、[genre-playbook-meeting-host.md](../../chinese-official-writing/references/genre-playbook-meeting-host.md)、[genre-playbook-duty-report.md](../../chinese-official-writing/references/genre-playbook-duty-report.md) | 拆分承接 | 讲话/致辞/演讲留在同名页；完整主持会序、转场与程序状态归主持词；书面及现场职责述职归述职页。人物排序按需附加，不再记为待拆页。 |
| 34 | `genre-playbook-work-summary.md` | genre | [genre-playbook-work-summary.md](../../chinese-official-writing/references/genre-playbook-work-summary.md)、[genre-playbook-work-priorities.md](../../chinese-official-writing/references/genre-playbook-work-priorities.md)、[genre-playbook-report.md](../../chinese-official-writing/references/genre-playbook-report.md) | 拆分承接 | 回顾、问题、经验和有据下一步留在总结；未来工作任务归工作要点；周报/月报归报告，字段处理按需附加。历史拆分来源见 [summary-priorities-separation-r1](../tests/evidence/rewrite-cold-r4/summary-priorities-separation-r1.md)，R5 另有旧文种逐页审计；不将拆页视为实写通过。 |
| 35 | `genre-playbooks.md` | router | [reference-index.md](../../chinese-official-writing/references/reference-index.md)、[genre-routing.md](../../chinese-official-writing/references/genre-routing.md)、[genre-checklist.md](../../chinese-official-writing/references/genre-checklist.md)、[genre-playbook-correspondence.md](../../chinese-official-writing/references/genre-playbook-correspondence.md) | 退役/迁出 | 旧混合总页的文种功能分入各自主叶；索引/路由只选路，checklist 只反查未知功能，旧函节骨架归函页。下列 30 个新增页及旧页同名主叶共同承接，不以索引存在证明全部语义闭合。 |
| 36 | `genre-routing.md` | router | [genre-routing.md](../../chinese-official-writing/references/genre-routing.md) | 同名承接 | 只判定文种、对象关系和冲突，输出首叶。 |
| 37 | `handling-elements.md` | workflow | [writing-rules.md](../../chinese-official-writing/references/writing-rules.md) | 退役/迁出 | 主体、对象、金额、日期、状态、用户字段和实质缺项归共性写作页；必要办理要素结合当前主文种判断，正文、表格、附件的对应关系在共同复核中核对，不保留额外伴读页。 |
| 38 | `information-selection.md` | workflow | [writing-rules.md](../../chinese-official-writing/references/writing-rules.md) | 退役/迁出 | 本轮材料、合理分析、业务状态、草稿日期及实质缺项归共性写作页；材料与常识支持的分析保留，未支持的具体事实与已定安排不得补入。 |
| 39 | `official-style.md` | language | [anti-ai-patterns.md](../../chinese-official-writing/references/anti-ai-patterns.md) | 退役/迁出 | 正式语体、叙述身份、句段关系、证据和论断强度、语义保真及中英文/标点处理归必经语言检查；行文关系和称谓继续由既有 formal-addressing 能力页处理。 |
| 40 | `proofreading-checklist.md` | review | [proofreading-checklist.md](../../chinese-official-writing/references/proofreading-checklist.md) | 同名承接 | 按实际校对任务核对引用、数字、日期、术语和稿内一致性；成语、原文、的地得及量词已有明确规则，历史专项结果不因文件更新自动变更。 |
| 41 | `prose-lint-usage.md` | tool | [prose-lint-usage.md](../../chinese-official-writing/references/prose-lint-usage.md) | 同名承接 | 规定路径、参数、结果回流和失败解释，不替代文种判断。 |
| 42 | `reference-index.md` | router | [reference-index.md](../../chinese-official-writing/references/reference-index.md) | 同名承接 | 按稿件用途选唯一主叶，列明必要附加页；移除与首页重复的交付模式表，机器路由 manifest 留在维护区。 |
| 43 | `review-checklist.md` | review | [review-checklist.md](../../chinese-official-writing/references/review-checklist.md)、[writing-rules.md](../../chinese-official-writing/references/writing-rules.md) | 同名承接 | 默认全文审核及范围限定、合理推断、风险分层、仅审和审后改留在审稿页；共同复核和完整交付、文后提示归 writing-rules。 |
| 44 | `review-direct-checklist.md` | review | [review-checklist.md](../../chinese-official-writing/references/review-checklist.md)、[writing-rules.md](../../chinese-official-writing/references/writing-rules.md) | 退役/迁出 | 全文审核与范围限定共用审稿页；证据判断、合理推断、次级材料可选、仅审不改语义保留，完整改后稿与独立提示归共性写作页。 |
| 45 | `short-draft-naturalness.md` | workflow/language | [writing-rules.md](../../chinese-official-writing/references/writing-rules.md)、[anti-ai-patterns.md](../../chinese-official-writing/references/anti-ai-patterns.md) | 退役/迁出 | 自然段承接章节、有效标题编号、上限无需填满和文种动作收束归共性写作页；重复和旁白归必经语言检查，不再设置短稿伴读入口。 |
| 46 | `speech-person-order.md` | overlay | [speech-person-order.md](../../chinese-official-writing/references/speech-person-order.md) | 同名承接 | 讲话、致辞、演讲及主持词涉及具体人物排序时加读；保留用户次序、主客关系和跨单位不猜级别，完成后返回原稿全文。 |
| 47 | `structure-editing.md` | workflow | [structure-editing.md](../../chinese-official-writing/references/structure-editing.md) | 同名承接 | 处理增删、移动、标题和段落关系。 |
| 48 | `task-route-cards.md` | router/workflow | [SKILL.md](../../chinese-official-writing/SKILL.md)、[writing-rules.md](../../chinese-official-writing/references/writing-rules.md)、[structure-editing.md](../../chinese-official-writing/references/structure-editing.md)、[field-editing.md](../../chinese-official-writing/references/field-editing.md) | 退役/迁出 | 首页按实际用途选文种，局部结构和字段动作沿用既有入口；所有稿件使用共同写作、复核与交付规则，旧轻量卡撤下。 |
| 49 | `technical-terms.md` | transaction/overlay | [technical-terms.md](../../chinese-official-writing/references/technical-terms.md) | 同名承接 | 算力或技术稿件明确需要术语核对时才加载。 |
| 50 | `workflow.md` | workflow | [SKILL.md](../../chinese-official-writing/SKILL.md)、[writing-rules.md](../../chinese-official-writing/references/writing-rules.md)、[structure-editing.md](../../chinese-official-writing/references/structure-editing.md)、[field-editing.md](../../chinese-official-writing/references/field-editing.md)、[compression-details.md](../../chinese-official-writing/references/compression-details.md)、[argument-chains.md](../../chinese-official-writing/references/argument-chains.md)、[format-gbt9704.md](../../chinese-official-writing/references/format-gbt9704.md) | 退役/迁出 | 首页负责任务和文种选择；取材、成稿、复核与交付归 writing-rules，复杂结构、字段、篇幅、办理、论证和格式按实际能力分工，旧流程副本撤下。 |

## 新构造页（30 页，不占基线 50 行）

27 个新增主叶、2 个报告事务附加页、1 个共性写作页；结合保留路径中的 13 个主叶，共 40 个主叶。采购专项同名页属于附加页，不能因文件名含 playbook 计入主叶。

| 新页 | 当前用途 | 旧来源/补建依据 |
|---|---|---|
| [genre-playbook-notice.md](../../chinese-official-writing/references/genre-playbook-notice.md) | 通知独立主文种 | 旧 notice-publication 通知部分 |
| [genre-playbook-publication.md](../../chinese-official-writing/references/genre-playbook-publication.md) | 公告、公示、通告的公开发布功能 | 旧 notice-publication 公开发布部分 |
| [genre-playbook-bulletin.md](../../chinese-official-writing/references/genre-playbook-bulletin.md) | 通报情况、表扬先进和批评问题的独立主文种 | 旧 notice-publication 通报部分 |
| [genre-playbook-research.md](../../chinese-official-writing/references/genre-playbook-research.md) | 调研/研究独立主文种 | 旧 research-feasibility 调研部分 |
| [genre-playbook-feasibility.md](../../chinese-official-writing/references/genre-playbook-feasibility.md) | 可行性研究独立主文种 | 旧 research-feasibility 及 ai-compute-docs 可研部分 |
| [genre-playbook-procurement-announcement.md](../../chinese-official-writing/references/genre-playbook-procurement-announcement.md) | 采购公告独立主文种，征集、结果及终止等按发布目的取要素 | 旧 procurement-review 采购公告部分 |
| [genre-playbook-decision.md](../../chinese-official-writing/references/genre-playbook-decision.md) | 有权机关作出重要事项决定，明确对象、范围和执行要求 | 旧 deliberation-deployment 与 genre-checklist 对应功能 |
| [genre-playbook-resolution.md](../../chinese-official-writing/references/genre-playbook-resolution.md) | 会议讨论并通过的重大事项，保持集体议决与通过状态 | 旧 deliberation-deployment 与 genre-checklist 对应功能 |
| [genre-playbook-motion.md](../../chinese-official-writing/references/genre-playbook-motion.md) | 人民政府向同级人大或其常委会提请审议，保留提请关系 | 旧 deliberation-deployment 与 genre-checklist 对应功能 |
| [genre-playbook-communique.md](../../chinese-official-writing/references/genre-playbook-communique.md) | 公开发布已形成的重要事项或共识，保留发布范围与各方归属 | 旧 deliberation-deployment 与 genre-checklist 对应功能 |
| [genre-playbook-order.md](../../chinese-official-writing/references/genre-playbook-order.md) | 有权机关依法发令，核对权限、令号、公布事项与施行信息 | 旧 deliberation-deployment 与 genre-checklist 对应功能 |
| [genre-playbook-deployment.md](../../chinese-official-writing/references/genre-playbook-deployment.md) | 部署安排独立主叶 | 旧 deliberation-deployment 与 genre-checklist 对应功能 |
| [genre-playbook-reply.md](../../chinese-official-writing/references/genre-playbook-reply.md) | 批复独立主文种 | 旧 genre-checklist 批复功能 |
| [genre-playbook-opinion.md](../../chinese-official-writing/references/genre-playbook-opinion.md) | 意见独立主文种 | 旧 deliberation-deployment 与 genre-checklist 意见功能 |
| [genre-playbook-explanation.md](../../chinese-official-writing/references/genre-playbook-explanation.md) | 独立说明性材料；情况说明按实际用途判定 | 旧 genre-checklist/genre-checklist-report 说明功能 |
| [genre-playbook-report.md](../../chinese-official-writing/references/genre-playbook-report.md) | 报告、情况报告、情况综合、周报/月报；使用评估兼顾正反价值 | 旧 genre-checklist-report 骨架、work-summary 周期汇报、formulaic-language 情况综合 |
| [genre-playbook-meeting-host.md](../../chinese-official-writing/references/genre-playbook-meeting-host.md) | 会议主持词、主持串词按既定会序组织环节、程序状态和转场 | 旧 speech-address 主持开场及 formulaic-language 接引；补足完整会序 |
| [genre-playbook-duty-report.md](../../chinese-official-writing/references/genre-playbook-duty-report.md) | 个人或班子书面与现场述职，围绕职责、履职事实、实绩归属、问题和改进方向 | 旧 speech-address 述职功能 |
| [genre-playbook-work-priorities.md](../../chinese-official-writing/references/genre-playbook-work-priorities.md) | 年度、阶段或专项工作要点，组织未来任务、责任与节点，保留拟议状态 | 旧 work-summary 工作要点功能 |
| [transaction-remediation-report.md](../../chinese-official-writing/references/transaction-remediation-report.md) | 整改进展/整改情况报告事务附加页 | 旧报告中的整改情况；明确与整改方案分工 |
| [transaction-feedback-report.md](../../chinese-official-writing/references/transaction-feedback-report.md) | 反馈情况报告事务附加页 | 旧报告中的意见办理/反馈情况；明确与合作性建议分工 |
| [writing-rules.md](../../chinese-official-writing/references/writing-rules.md) | 所有文种共用的取材、成稿、篇幅、复核与交付规则 | 归并 information-selection、handling-elements、final-review-layers、delivery、short-draft-naturalness、task-route-cards 的有效语义 |
| [genre-playbook-responsibility-letter.md](../../chinese-official-writing/references/genre-playbook-responsibility-letter.md) | 责任书：共同事项、各方责任与已有条件 | 旧 formulaic-language 责任书项 |
| [genre-playbook-initiative.md](../../chinese-official-writing/references/genre-playbook-initiative.md) | 倡议书：缘由、具体行动及自愿参与语气 | 旧 formulaic-language 倡议书项 |
| [genre-playbook-open-letter.md](../../chinese-official-writing/references/genre-playbook-open-letter.md) | 公开信：发信主体、明确受众、沟通事项与配合要求 | 旧 formulaic-language 公开信项 |
| [genre-playbook-narration.md](../../chinese-official-writing/references/genre-playbook-narration.md) | 讲解稿：受众、对象、路线/说明顺序与有据解释 | 旧 formulaic-language 讲解稿项 |
| [genre-playbook-information-materials.md](../../chinese-official-writing/references/genre-playbook-information-materials.md) | 正式宣传手册与宣传材料：查阅分项、要求方法、渠道与适用范围 | 旧 formulaic-language 宣传手册/宣传材料项 |
| [genre-playbook-review-opinion.md](../../chinese-official-writing/references/genre-playbook-review-opinion.md) | 独立审查/评审意见；一般项目、初步设计及采购审查按同一功能处理 | 旧 procurement-review 审查材料部分 |
| [genre-playbook-technical-requirements.md](../../chinese-official-writing/references/genre-playbook-technical-requirements.md) | 独立技术需求书、软件/接口需求或附件；算力与采购专项按条件叠加 | 旧 ai-compute-docs 独立技术需求及通用技术需求路由补建 |
| [genre-playbook-editorial-note.md](../../chinese-official-writing/references/genre-playbook-editorial-note.md) | 编者按与编发按语：编辑身份、编发目的、阅读方向及按语/原稿关系 | 旧 news-message 编者按要求与 formulaic-language 编者按入口 |

## 旧事务用语表的剩余入口

第 13 行列出了 R5 审计发现的缺口及其现有落点；旧表其余类型仍须按用途进入主叶，不能再把用语页当免检查直接叶。

| 旧 formulaic-language 类型 | 当前归属 |
|---|---|
| 计划 | 工作要点或部署；需要完整实施路径时为方案，以交付用途判定 |
| 汇报、情况综合 | 报告；情况综合保留来源、分类、共性差异与当前状态 |
| 调查报告 | 调研；侧重汇报办理情况时按报告功能判断 |
| 讲话稿、演讲词 | 讲话/致辞/演讲 |
| 答复 | 平行往来用函/复函；上级答复请示用批复；纯解释材料用说明 |
| 建议信、情况反映 | 合作性意见建议、投诉/情况反映；法定意见另行判定 |
| 新闻发布稿、新闻 | 新闻消息；公开告知材料按公告用途判定 |
| 编者按 | 独立编者按主叶，以编辑或编发者身份说明目的和阅读方向，不套事件消息骨架 |
| 总结、短评 | 工作总结、新闻评论 |

以上是功能选路映射，不是给任一标题硬定文种，也不证明这些组合已经全部实写。

## 历史证据与未闭合状态

以下证据保留各自快照的判断，不追改 R5/R6 或其他历史结果。历史“未闭合”按原快照理解；当前活动状态以本页摘要、R16—R20各自绑定的结果及整体完成度审计为准。

- [旧共性语义审计 R5](../tests/evidence/rewrite-cold-r5/legacy-common-parity-r5.md)覆盖 23 页；[旧文种语义审计 R5](../tests/evidence/rewrite-cold-r5/legacy-genre-parity-r5.md)覆盖 26 页。剩余 technical-terms 在共性报告中另记与旧页逐行相同。两份审计针对当时快照，原有 G1–G4/U1 不是当前未修清单，也不是当前通过证书。
- [R5 修复及证据汇总](../tests/evidence/rewrite-cold-r5/result.md)记录有据分析、字段默认形态、使用报告正反组织、消息内分析、可研建议、事务入口与技术需求的补建。当前页存在相应落点；敏感信息范围复核已补回，但不能据此宣布旧涉密人工复核专项等价。
- [R6 旧边界迁移](../tests/evidence/legacy-boundary-migration-r6/result.md)更新了早期“总体等价”的精度：81 个方法保留，75 通过、6 个方法仍有 12 个失败子断言。未闭合项是声明/业务版本明示保留（2）、纯文本标题与编号句标点（4）、渠道不推发文主体（1）、Token 不改调用次数（1）、成语同语境/的地得/量词（3）、引用原文同语境保护（1）。不能用泛称模板、单位或校对规则代替专项承接。
- [R6 真实写稿](../tests/evidence/rewrite-validation-r6/result.md)保留三组各自对照：冷审修复 2 较好/1 较弱/7 相当；剩余文种 7/3/2；已知反例可比项 1/6/1，另 1 项仅候选可评。没有逐页全部质量通过结论，不能把正反样本合并成普遍改善。
- 技术需求、公开信、讲解的事实/程序扩写，完整消息旁白、局部范围、偶发不交正文和额外主叶读取仍有反例。新增页不自动获得旧页历史成绩；主持/述职已有专页也不表示两类组合全部验收。
- R7 原型及 R5/R6 未闭合项保留为历史记录；R16完整开发候选、R17已采用的按语与脚本修正、R18共性同义压缩分别保留原绑定与结果，截至R19的canonical在R18基础上采用497字符审稿页；当前R23另有已记录的范围纠正，以上方活动摘要为准。静态映射只表示工程归属，实际读取仍以native轨迹为准，1.x整体等价与发布验收未闭合。

## R16—R20 已采用证据与当前未闭合项

- [完整候选构建记录](../../output/reference-integration-r16/build.json)及[组合预登记](../tests/evidence/integration-r16/preregister.md)保留共性归并、目录、采购公告目的、函用途和编者按五项冻结组件的来源；[R16采用记录](../../output/reference-integration-r16-adopted/adoption.json)及[完整结果](../tests/evidence/integration-r16/results.md)记录已完成的组合与开发候选应用。页集为67页，不以构建或应用成功代替整体真实写稿通过。
- [目录原型预登记](../tests/evidence/genre-router-r16/preregister.md)、[采购/函用途原型](../tests/evidence/genre-purpose-r16/preregister.md)及[编者按原型](../tests/evidence/editorial-note-r16/preregister.md)说明各自范围。索引清理后 manifest 按实际命名链接重建 allowed_reads/forbidden_reads；补回旧清单遗漏的通报路线，并新增编者按路线，不以固定路线总数代替路径核对。
- [完整候选冷审](../../output/full-skill-cold-r16/report.md)及[两规则局部修正构建](../../output/reference-integration-r16-rule-refinement/build.json)保留压缩单侧上限、评论修改范围和行内代码残留扫描问题的原始发现与修正范围；规则和脚本后续采用、复现及相关检查见[R16完整结果](../tests/evidence/integration-r16/results.md)，不回写原冻结包，也不作为整体最终验收。
- 共性撤页及来源/身份边界的[原型预登记](../tests/evidence/common-layer-r16-attribution/preregister.md)和原有反例继续保留；适配 agent_writer 只移除活动退役路径，不能用该预选上下文证明 native 选路。
- [R17验证汇总](../tests/evidence/verification-r17/results.md)记录1.x金线低频文种、审核/改稿/字段等模式、Word实物及两项内部原子的分组结果；已采用按语对象澄清和零字号检测，议案用途原型未采用。Word仍有不可读实物与链接未验证记录，正文和完整消息分别判读。
- [R18共性压缩结果](../tests/evidence/common-compression-r18/results.md)记录已采用的同义压缩、独立语义冷审、原生同题验证及相关维护检查。当前仍有旁白、误提示、伴读和实际执行问题，逐条旧责任与整体1.x等价未闭合，不能把局部通过累计成整体通过。
- [R19审稿页精炼](../tests/evidence/review-common-r19/results.md)完成并采用497字符版，前两版失败保留；[Word输入实稿](../tests/evidence/docx-input-native-r19/report.md)完成4份可读修复，保留未调用扫描及署名偏位等限制。二者规则快照不同，不合称组合通过。剩余最小工作按[R19整体审计](../tests/evidence/completion-audit-r19/report.md)与[当前进度](rewrite-common-layer-progress-20260913.md)收口；2.0未合main、安装、推送或发布。

- [R20入口与交付](../tests/evidence/delivery-narration-r20/results.md)采用两页，description事务范围、首页四步与两脚本路径、交付反旁白例子均已落实；索引和文种页未变。12次原生、6对完整交付为候选4/基线1/相当1，反例及漏读保留。另16次审核扩充未支持采用，不能混为已通过组合。50旧方法迁移见[R20旧责任](../tests/evidence/legacy-boundary-migration-r20/report.md)，原有工程缺口已收束，真实写作覆盖仍按对应题目判断。

## 台账使用规则

- 删除须能追溯替代页、授权迁出或明确废弃理由；同名保留也须核对具体语义。
- 每条可执行语义按实际职责定位；简短接引不等于重复骨架。旧页到现存页的文件覆盖与逐条功能验收分别记录。
- 真实稿件保留快照、请求、通道、最终消息、读取与无效原因；静态断言、原生运行技术有效和交付质量三个状态分开。
- 本表和聚焦测试用于确认 2.0 开发候选的文件归属、链接及语义承接，不能替代真实写稿、候选独有回退核对或 1.x 发布验收。
