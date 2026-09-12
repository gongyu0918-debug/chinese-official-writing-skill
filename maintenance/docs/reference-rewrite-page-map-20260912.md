# Reference 逐页架构归属表（2026-09-12）

基线：`main@1ce71123`。本表覆盖当前 Skill 的全部 50 个 reference。`rewrite` 表示本批已按新职责重写，`retain` 表示保留既有稳定语义并重新接入路由；两种状态都必须在后续组合实写中验证，不能把文件状态当成功能等价。

| # | 基线 reference | 新架构分区 | 新页/归属 | 处置 | 归属与保留理由 |
|---:|---|---|---|---|---|
| 1 | `ai-compute-docs.md` | transaction/overlay | 算力场景附加页 | rewrite | 统一算力字段、技术、成本、SLA、安全和验收；不承载报告/方案/采购骨架。 |
| 2 | `ai-compute-examples.md` | transaction/overlay | 算力示例资料 | retain | 仅用户明确要求示例时读取，避免普通算力稿件伴读。 |
| 3 | `anti-ai-patterns.md` | language/review | 反旁白与过程泄露 | rewrite | 只处理正文表面和交付包装，不决定文种。 |
| 4 | `argument-chains.md` | workflow | 论证关系能力页 | rewrite | 组织事实、判断、原因、目标和风险关系，不补具体事实。 |
| 5 | `compatibility-scene-routing.md` | transaction/router | 兼容场景分流页 | retain | 为新闻、意见建议、投诉反映、整改等已有场景选专页。 |
| 6 | `compression-details.md` | workflow | 压缩流程页 | retain | 负责篇幅取舍和超限处置，不重写文种骨架。 |
| 7 | `delivery-review-gate.md` | tool/hook | 交付门禁说明 | retain | 绑定冻结 Hook，仅用户明确要求门禁时读取。 |
| 8 | `external-research.md` | workflow/tool | 外部事实研究页 | retain | 仅用户要求检索或需要最新公开事实时启用。 |
| 9 | `field-editing.md` | workflow | 字段编辑页 | retain | 处理字段拆行、增删和表单边界，不带入完整文种规则。 |
| 10 | `final-review-layers.md` | review | 终稿分层复核页 | rewrite | 规定硬边界、质量复核和场景交付顺序，避免反向启动总路由。 |
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
| 21 | `genre-playbook-deliberation-deployment.md` | genre/transaction | 部署安排主叶 | retain | 作为事务型稿件专页，不混入通知或报告骨架。 |
| 22 | `genre-playbook-institution-rules.md` | genre | 制度规章主叶 | retain | 制度、规定、办法、细则和规程的规范结构。 |
| 23 | `genre-playbook-minutes.md` | genre | 会议纪要主叶 | retain | 保留会议事实和议定事项状态，不补讨论过程。 |
| 24 | `genre-playbook-news-commentary.md` | genre | 新闻评论主叶 | retain | 新闻评论独立成文种，不通过兼容页稀释。 |
| 25 | `genre-playbook-news-message.md` | genre | 新闻消息主叶 | retain | 新闻消息、活动报道和编者按的事实结构。 |
| 26 | `genre-playbook-notice-publication.md` | genre | 通知/公告/公示主叶 | retain | 负责发布对象、事项、时间和执行要求。 |
| 27 | `genre-playbook-plan-construction.md` | genre | 方案主叶 | retain | 方案目标、任务、步骤、保障和状态边界。 |
| 28 | `genre-playbook-procurement-review.md` | genre/transaction | 采购审查主叶 | retain | 采购审查和评审材料，不承载算力三套骨架。 |
| 29 | `genre-playbook-project-application.md` | genre | 项目申请主叶 | retain | 项目申请的依据、目标、内容和请批事项。 |
| 30 | `genre-playbook-remediation-plan.md` | genre/transaction | 整改方案主叶 | retain | 整改问题、措施、责任和状态保持原强度。 |
| 31 | `genre-playbook-request.md` | genre | 请示/申请主叶 | retain | 请批、依据、事项和结语的完整骨架。 |
| 32 | `genre-playbook-research-feasibility.md` | genre | 调研/研究/可研主叶 | retain | 研究对象、方法、分析和结论状态。 |
| 33 | `genre-playbook-speech-address.md` | genre | 讲话/致辞主叶 | retain | 讲话、致辞和演讲的对象、主题、层次和收束。 |
| 34 | `genre-playbook-work-summary.md` | genre | 工作总结/要点主叶 | retain | 总结、要点的事实归纳和安排状态。 |
| 35 | `genre-playbooks.md` | router | 旧入口兼容目录 | delete | 仅剩跳转和重复目录功能；已由专页、`genre-routing.md` 与 `genre-checklist.md` 替代，删除以避免旧混合入口继续被误读。 |
| 36 | `genre-routing.md` | router | 主文种与行文关系路由 | rewrite | 只判定文种、对象关系和冲突，输出首叶。 |
| 37 | `handling-elements.md` | workflow | 办理要素能力页 | rewrite | 统一主体、对象、依据、时限、责任、附件和请批字段。 |
| 38 | `information-selection.md` | workflow | 事实选择与状态页 | rewrite | 区分事实、直接分析、待定状态和实质缺项。 |
| 39 | `official-style.md` | language | 正式表达能力页 | rewrite | 处理语体、句式、证据强度和去口语，不增加事实。 |
| 40 | `proofreading-checklist.md` | review | 轻量校对页 | rewrite | 校验数字、日期、术语、引用和稿内一致性。 |
| 41 | `prose-lint-usage.md` | tool | 脚本调用契约页 | rewrite | 规定路径、参数、结果回流和失败解释，不替代文种判断。 |
| 42 | `reference-index.md` | router | 平面读取 manifest 生成页 | rewrite | 按模式、主文种、场景和停止点选最小集合。 |
| 43 | `review-checklist.md` | review | 全文综合复核页 | rewrite | 段落、小节、全文、事实、文种和格式分层复核。 |
| 44 | `review-direct-checklist.md` | review | 只审不改页 | retain | 只输出位置、风险和建议，不重写全文。 |
| 45 | `short-draft-naturalness.md` | workflow | 短稿自然度页 | retain | 用户要求短正文或材料稀疏时按需加载。 |
| 46 | `speech-person-order.md` | overlay | 讲话人物顺序附加页 | retain | 仅讲话开场出现人物排序需求时叠加。 |
| 47 | `structure-editing.md` | workflow | 结构编辑页 | retain | 处理增删、移动、标题和段落关系。 |
| 48 | `task-route-cards.md` | router | 轻量任务路由卡 | rewrite | 只判定是否可走短路，不带入会议、通知或报告细则。 |
| 49 | `technical-terms.md` | transaction/overlay | 技术术语附加页 | retain | 算力或技术稿件明确需要术语核对时才加载。 |
| 50 | `workflow.md` | workflow | 写作流程总契约 | rewrite | 规定模式动作、阶段顺序和停止点，不写具体文种骨架。 |

## 台账使用规则

- `rewrite`、`retain` 和 `delete` 都必须有证据；`retain` 不是免审，`delete` 必须说明替代页和功能闭合。
- 每个新页只能有一个主归属；同一条可执行语义不得在多个页重复成为硬规则。
- 后续填充时，为每行补充旧页语义摘录、候选页段落位置、允许读取集合、排除集合和真实写稿证据编号。
- 只有 50 行全部闭合，且组合 A/B 排除候选独有硬回退后，才可进入合并判断。
