# 参考资料索引

本页只做两件事：为任务选出首个专页，规定允许叠加的共性页和停止点。不要把索引当成写作规则，也不要一次加载整套 references。

## 选路顺序

1. 先确定交付模式：起草、改稿、压缩、只审、格式交付。
2. 再确定文种或场景：优先使用用户标题、模板、最新版底稿和明确场景；文种冲突时进入 `genre-routing.md`。
3. 只读取首个文种页，再按下表叠加必要的共性页。
4. 完成首稿或审查范围后停止加载。脚本和 Hook 是执行工具，不改变文种路由。

## 交付模式页

| 任务信号 | 首页 | 可叠加 | 停止点 |
| --- | --- | --- | --- |
| 起草、整体改写、合稿 | 命中文种页 | `information-selection.md`；必要时 `handling-elements.md`、`argument-chains.md` | 文种页骨架和用户要求已覆盖 |
| 二次修改、压缩、重排 | `structure-editing.md` 或 `field-editing.md` | `information-selection.md`；长文压缩再加 `compression-details.md` | 点名动作已完成并复核 |
| 只审不改 | `review-direct-checklist.md` 或点名文种审查页 | 用户点名的质量页；不自动叠加总审页 | 已输出位置、风险和建议 |
| 全文综合复核 | `review-checklist.md` | `anti-ai-patterns.md`、`proofreading-checklist.md` | 三级清单完成 |
| Word、docx、GB/T 9704、红头 | `format-gbt9704.md` | 对应文种页；需要脚本时加 `prose-lint-usage.md` | 版式和正文均已交付 |

## 文种与场景首叶

### 已验证的专页

- 请示、申请、增项申请：`genre-playbook-request.md`、`genre-playbook-project-application.md`；只审请示或申请用 `genre-checklist-request.md`。
- 报告、情况说明、工作总结、工作要点：`genre-checklist-report.md`、`genre-playbook-work-summary.md`。
- 通知、公告、公示、通告、通报：`genre-playbook-notice-publication.md`。
- 函、复函、征求意见函：`genre-playbook-correspondence.md`。
- 会议纪要：`genre-playbook-minutes.md`。
- 讲话稿、致辞、演讲：`genre-playbook-speech-address.md`；开场人物顺序另加 `speech-person-order.md`。
- 方案、实施方案、建设方案：`genre-playbook-plan-construction.md`。
- 制度、规定、办法、细则、操作规程：`genre-playbook-institution-rules.md`。
- 调研、研究、可研：`genre-playbook-research-feasibility.md`；只审可研用 `genre-checklist-feasibility-review.md`。
- 采购审查、采购公告、评审材料：`genre-playbook-procurement-review.md` 或 `genre-playbook-notice-publication.md`。
- 新闻消息、活动报道、编者按：`genre-playbook-news-message.md`。
- 新闻评论、时评：`genre-playbook-news-commentary.md`。
- 意见建议、投诉反映、整改方案、部署安排：先读 `compatibility-scene-routing.md`，再进入对应专页。

### 仍需总路由判定的文种

命令、公报、决议、议案、决定、批复、通报等未命中专页时，读 `genre-routing.md` 判定功能，再用 `genre-checklist.md` 做最小核对。清单页只保留功能核对，不承载完整骨架。

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
| `final-review-layers.md` | 全文交付前综合总审 | 先硬边界，再质量建议，再场景参考 |
| `prose-lint-usage.md` | 用户要求或明确需要脚本扫描 | 给出脚本路径、参数和结果解释 |
| `delivery-review-gate.md` | 用户明确要求交付门禁 Hook | 只处理门禁，不进入普通写稿路径 |

## 专项资料

- 旧入口兼容目录：`genre-playbooks.md`；新任务优先按本页主叶表选路。
- 事务性固定用语和开端/承启/结尾核对：`formulaic-language.md`，仅在需要文种用语时叠加。
- 外部最新事实、公开政策或用户明确要求搜索：`external-research.md`。
- 短稿、只有上限、短正文自然度：`short-draft-naturalness.md`。
- 长文压缩和超限处置：`compression-details.md`。
- 字段拆行、增删和表单边界：`field-editing.md`。
- 结构增删、移动和标题重排：`structure-editing.md`。
- AI 算力专项：可研/比较、采购/租赁、技术需求/SLA/验收分别直达各自专项叶；只有类型不明时读取 `ai-compute-docs.md` 分流。

## 停止规则

首叶已覆盖文种功能后，直接进入成稿或审查；共性页只在任务信号明确时叠加。一个任务同时出现多个文种时，按用户指定的交付对象确定主文种，其余内容作为附件、引用或背景处理；无法判定时再读 `genre-routing.md`。不因看到关键词就加载整套 playbook，也不因使用脚本就加载总审页。
