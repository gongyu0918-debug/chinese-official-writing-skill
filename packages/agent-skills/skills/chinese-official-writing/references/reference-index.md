# 参考资料索引

根据用户已经明确的稿件用途，在下表选读对应主文种；需要共性能力时按触发条件加读。

## 文种与场景首叶

### 文种专页

- 既有项目新增功能、服务或实施内容的增项申请：`genre-playbook-project-application.md`。
- 请示、普通采购或经费等申请：`genre-playbook-request.md`；文种专项复核用 `genre-checklist-request.md`。
- 报告、情况报告、周报、月报：`genre-playbook-report.md`；文种复核用 `genre-checklist-report.md`。
- 工作总结：`genre-playbook-work-summary.md`。
- 工作要点：`genre-playbook-work-priorities.md`。
- 通知：`genre-playbook-notice.md`；公告、公示、通告：`genre-playbook-publication.md`；情况、表扬或批评通报：`genre-playbook-bulletin.md`。
- 决定：`genre-playbook-decision.md`；决议：`genre-playbook-resolution.md`；议案：`genre-playbook-motion.md`。
- 公报：`genre-playbook-communique.md`；命令、令：`genre-playbook-order.md`；部署安排：`genre-playbook-deployment.md`。
- 批复：`genre-playbook-reply.md`；意见：`genre-playbook-opinion.md`；说明：`genre-playbook-explanation.md`。
- 函、复函、征求意见函：`genre-playbook-correspondence.md`。
- 会议纪要：`genre-playbook-minutes.md`。
- 讲话稿、致辞、演讲：`genre-playbook-speech-address.md`；开场人物顺序另加 `speech-person-order.md`。
- 会议主持词、主持串词：`genre-playbook-meeting-host.md`；开场人物顺序另加 `speech-person-order.md`。
- 书面述职、述职报告、履职情况报告、现场述职发言：`genre-playbook-duty-report.md`。单位工作报告或工作总结仍走各自主叶。
- 方案、实施方案、建设方案：`genre-playbook-plan-construction.md`。
- 制度、规定、办法、细则、操作规程：`genre-playbook-institution-rules.md`。
- 调研、研究：`genre-playbook-research.md`；可研：`genre-playbook-feasibility.md`；只审可研用 `genre-checklist-feasibility-review.md`。
- 采购审查、评审材料：`genre-playbook-procurement-review.md`；采购公告：`genre-playbook-procurement-announcement.md`。
- 新闻消息、活动报道、编者按：`genre-playbook-news-message.md`。
- 新闻评论、时评：`genre-playbook-news-commentary.md`。
- 意见建议、投诉反映、整改方案：先读 `compatibility-scene-routing.md`，再进入对应专页；法定“意见”直接进入意见主叶。
- 整改进展/整改情况报告：报告主叶 + `transaction-remediation-report.md`；反馈情况报告：报告主叶 + `transaction-feedback-report.md`。两者不改用整改方案或合作性意见建议骨架。

### 需先确定主文种的场景

其他未命中专页的事务文本，读 `genre-routing.md` 判定功能；命中专页后按该页写稿，仍未覆盖时用 `genre-checklist.md` 做最小核对。

## 共性能力页

| 能力 | 读取条件 | 作用 |
| --- | --- | --- |
| `information-selection.md` | 起草、改稿、压缩、合稿 | 区分事实、直接分析、状态和实质缺口 |
| `handling-elements.md` | 需要主体、对象、依据、时限、责任、附件、反馈或请批事项 | 核对办理要素，不补空项 |
| `argument-chains.md` | 需要原因、目标、方案比较、风险或执行链条 | 只组织已有依据支持的论证 |
| `official-style.md` | 需要正式、平实或去口语化 | 只做语言建议，不扩充事实 |
| `formal-addressing.md` | 需要行文关系、敬语或称谓 | 锁定称谓和关系 |
| `anti-ai-patterns.md` | 复核旁白、教学腔、包装句、模板腔 | 只删改稿件中的过程话和包装话 |
| `proofreading-checklist.md` | 定稿前轻量校对 | 查引用、数字、日期、术语和稿内一致性 |
| `final-review-layers.md` | 首页第二步事实与文种复核 | 核对事实、状态、文种、结构和文内完整性 |
| `prose-lint-usage.md` | 首页第四步脚本复核 | 给出脚本路径、参数和结果解释 |

## 专项资料

- 事务性固定用语和开端/承启/结尾核对：`formulaic-language.md`，仅在需要文种用语时叠加。
- 不熟悉的新文种、新材料类型、特殊事务场景，或需要核查通用做法、必备要素、正式格式、常用语及外部最新事实时：`external-research.md`；常规已知文种不自动扩展搜索。
- 短稿、只有上限、短正文自然度：`short-draft-naturalness.md`。
- 长文压缩和超限处置：`compression-details.md`。
- 字段拆行、增删和表单边界：`field-editing.md`。
- 结构增删、移动和标题重排：`structure-editing.md`。
- AI 算力场景：先选报告、方案、采购或技术材料等主文种，再在出现算力、GPU/服务器、模型推理/训练、智算中心、Token、并发或模型服务等信号时叠加 `ai-compute-docs.md`；单独出现安全、SLA 或验收不触发。该页是附加规则，不单独替代主文种。

## 停止规则

首叶覆盖文种功能后，直接进入成稿或审查；共性页按任务信号叠加。一个任务同时出现多个文种时，按用户指定的交付对象确定主文种，其余内容作为附件、引用或背景处理；文种仍有冲突时再读 `genre-routing.md`。关键词只触发对应页面，脚本调用保持在脚本页范围。
