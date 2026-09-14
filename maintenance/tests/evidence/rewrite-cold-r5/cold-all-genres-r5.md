# combined-candidate-r5 全文种独立冷审

审计对象：`F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/combined-candidate-r5/skill`。

审计方式：只读候选，逐页阅读实文并定向跟读链接目标；未读取其他审计、匿名映射、比较结果或旧版本，未运行写稿，未修改产品。下列触发请求是静态指令链分析用例，不是已运行的写稿测试。行号均为本次候选现行行号；除特别说明外，文件名相对于候选 `references/`。

## 结论

主文种职责总体成立：40 个 `genre-playbook-*.md` 中，39 个承担主文种或同功能变体，`genre-playbook-procurement-review.md` 明确承担采购附加核对；整改报告、反馈报告和算力页没有取代主文种。未发现需要重新选路才能结束的强制循环或死锁，未发现主叶不可达，也未发现写作路径混入构建、回归、打包或发布命令。

确认 3 项需要修正的规则问题：算力触发条件在叶页中扩大；意见建议页的一处来意写法无条件指定了未给来源；普通 Word 交付被要求列完整正式发文缺项。前两项影响读页或事实边界，第三项影响交付范围。另列 4 项表达和维护建议，不按硬问题计，不增加新门槛。

本审计不评价旧功能留存、运行效果或版本优劣；未运行真实写稿，不能据此报告实测 PASS。

## 硬问题

### H1 · P2：叶页重新扩大算力触发，普通服务器与非 AI GPU 内容会进入无关附加页

**现行位置**：`genre-playbook-procurement-announcement.md:9`，`genre-playbook-feasibility.md:13`，`anti-ai-patterns.md:54`。对照入口 `SKILL.md:49`、`reference-index.md:65` 和 `genre-playbook-technical-requirements.md:19`。

**触发自然请求**：“根据以下材料写一份普通文件服务器租赁采购公告，服务器只用于文件存储和共享。采购数量、期限和提交渠道如下……”另一可触发任务是“写一份用于视频渲染工作站 GPU 更新的可研”，材料没有 AI 模型、训练或推理用途。

**实际指令链**：

1. `SKILL.md:35` → `reference-index.md:32` → 采购公告主叶。
2. `SKILL.md:49` 和索引 `:65` 明确要求结合实际业务判断，并排除普通服务器等词单独触发。
3. 采购公告 `:9` 又规定“出现 GPU、服务器、模型服务或算力部署等明确场景时，另叠加”算力页；其中普通服务器已经命中其列举条件。
4. 即使在第 3 步依首页避免加读，首页 `:91` 的必经语言检查进入 `anti-ai-patterns.md` 后，`:54` 又把“GPU/服务器租赁”列入专项需求、指标、SLA、安全和验收读算力页的范围。
5. 可研路线中，`genre-playbook-feasibility.md:13` 的“涉及算力、GPU、模型服务或算力租赁时，叠加”同样单独触发非 AI GPU 任务。

**风险**：同一任务得到相反的加读决定，普通采购或可研加载 Token、模型训推、统一调度等无关维度。已确认的是不必要伴读和路由条件冲突；未把潜在 AI 内容混入正文说成已经发生。

**最小结构修正**：将这 3 处触发条件统一引用首页的 AI 业务条件，或删去其本地扩大的关键词判断，保留算力页链接作为明确 AI 场景下的附加。无需新增路由页，也无需禁止普通 GPU 技术分析。

### H2 · P2：没有第一方经历时，意见建议页指令直接指定了调研、征集或会员反馈作为来意

**现行位置**：`genre-playbook-advisory-feedback.md:17`；相关上下文 `:15-18`。对照 `information-selection.md:7-8,25`、`SKILL.md:64,69`。

**触发自然请求**：“下面是某平台公开的申报说明。不同栏目对附件格式的说法不一致，请以企业名义写一封建议统一口径的建议信。”用户没有提供实际申报经历、调研、征集或会员反馈。

**实际指令链**：

1. `SKILL.md:33` → `compatibility-scene-routing.md:9,11` → 意见建议主叶。
2. 主叶 `:17` 在处理开头来意时要求“没有第一方经历时用调研、征集或会员反馈说明来意”。这是明确条件后的动作指令，没有“材料已给上述来源时”的限制。
3. 该任务满足没有第一方经历的条件，但只有公开说明。若照此动作起草，“经调研”“征集意见发现”或“根据会员反馈”中的任一个都会新增具体来源事实。
4. 信息选择页要求来源事实采用材料信息；后续复核若纠正该新增，又须撤销叶页要求的来意表达。两条规则不能在这类材料上同时按字面执行。

**风险**：虚构建议来源或调查活动，提高问题依据的表面强度。此处不是限制材料和常识支持的因果、必要性或建议；“曾有调研/征集/会员反馈”属于具体来源事实，不能由公开说明的内容推得。

**最小结构修正**：将 `:17` 的后半句改为按已有来源说明来意；材料给了调研、征集或会员反馈时再使用对应表述。没有经历类来源时，直接基于给定文件、规则或待讨论问题提出建议。可与 `:18` 的礼貌说明来意合并，不增设先询问、先调查或必须补证的步骤。

### H3 · P2：普通 Word 文稿也被强制列出整套正式发文要素缺项

**现行位置**：`format-gbt9704.md:20-22`；入口 `SKILL.md:49`，同页范围原则 `:3,29,107`，交付规则 `delivery.md:13-20`。

**触发自然请求**：“把下面已定稿的内部工作总结整理成普通 Word，保留标题和落款，排版清楚即可。”材料完整满足内部总结用途，没有要求红头、正式发文或套用国标。

**实际指令链**：

1. Word 请求由 `SKILL.md:49` 必须进入格式页，这一步合理。
2. 格式页 `:20` 把“Word、docx”与红头、签发、版记等并列为正式交付前要素核对卡的触发条件，并要求缺项清单输出。
3. `:22` 要求“至少核对”发文字号、签发人、密级或紧急程度、版记、印章等整套项目；未提供的要素标“待确认”。普通 Word 请求已经满足其触发条件。
4. 同页 `:3,29,107` 又要求内部材料优先保留模板、不强套党政机关格式；交付页只列影响当前使用的缺项。该任务并不需要上述签发字段，但局部必做清单仍要求把它们列成待确认。

**风险**：将不适用要素误报为缺项，给普通文档交付附上不必要的发文检查和追问。文本未规定这些缺项必然阻止文件生成，因此不将其升级成已证实的阻断或死锁。

**最小结构修正**：保留所有 Word 请求加读格式页；核对卡按实际交付用途和用户模板选项，完整发文要素卡仅用于正式发文、红头或相应明确要求。普通 Word 只核对其内容、样式及实际使用的标题、落款、附件等，不把不适用项标成“待确认”。无需增加授权确认步骤。

## 表达与维护建议（不计硬问题）

### E1：专页内仍有少量共性规则复制，后续容易分叉

位置：`genre-playbook-plan-construction.md:10` 与 `field-editing.md:3`；`genre-playbook-advisory-feedback.md:34` 与 `format-gbt9704.md:39`；`SKILL.md:63,67`。

触发请求分别为字段式方案改稿、意见建议 Word 排版、含拟议状态的普通文稿。实际链是在首页已经命中字段、格式或状态规则后，又在主叶读到同类细则。现行内容基本一致，不构成重复选路，也没有必要强行删去所有就地提醒。维护时可让精确格式细则归共性页，主叶保留与该文种相关的简短提醒；首页相邻状态条目可以合并。风险是修改一处后其他副本失同步，当前未证明输出错误。

### E2：两张事务页及报告细查页的“情况说明”称呼可统一为按用途分流后的范围

位置：`transaction-feedback-report.md:3,7`、`transaction-remediation-report.md:3,9`、`genre-checklist-report.md:3,11`；对照 `genre-routing.md:67` 与 `genre-playbook-explanation.md:3-11`。

触发请求：“写一份情况说明，解释为什么本次反馈数字与前稿不一致。”现行正常链先按实际用途进入说明主叶；报告主叶 `:25` 才触发报告事务页，因此不能仅凭事务页也写了“情况说明”，就认定该请求必然误路由。建议在这些附加/细查页把范围写成“已按报告功能选路的情况说明”，返回时称“已选主叶”，消除页内名词与返回目标之间的歧义，不新设名称硬门。

### E3：制度层级的压缩表述不够可直接操作

位置：`genre-playbook-institution-rules.md:9`。

触发请求：“按章、条、款、项整理这份管理办法。”实际链为首页制度入口 → 制度主叶 → 该层级说明。六个层级与后面四种写法通过“依次”对应，映射不够清楚；常规语义及已有模板通常能解决，故不列为功能缺失或硬错误。可直接写清章、节、条用何种标题，款是自然段，项、目分别用什么序号；维持模板优先即可。

### E4：部分页的长句尾部否定较密，适合压缩指令文字

位置：`genre-playbook-news-message.md:12,17`、`genre-playbook-complaint-reflection.md:15-18`、`genre-checklist-feasibility-review.md:7`、`field-editing.md:3`。

触发请求为普通活动消息、亲历问题反映、只审可研摘要和字段修改。实际链都能完成写稿/审稿后进入统一检查；这些否定中有不少承担真实事实或范围边界，不能因否定密度高机械删除。建议把同一对象的约束聚成“保留什么、按什么范围分析、哪些具体值取自材料”的直接动作，长例举放在紧随的短句；保留用户限制和未定状态。新闻 `:12` 同句承载推断对象、持续时长、统计形成状态和抽象内容具体化四类边界，尤其值得拆成易读规则。这是指令自然度建议，未证明必然产生句尾否定正文。

## 结构判断与未判问题

| 审核维度 | 判断及依据 |
| --- | --- |
| 一文种功能一主叶 | 总体成立。法定意见与合作性建议分开；报告、总结、工作要点分开；述职以个人/班子履职为轴；主持以会序为轴；技术需求以能力条件为轴；采购审查主题作为附加，不替代方案、公告、申请或独立审查意见。 |
| 合理变体共页 | 申请/请示、函/复函/征求意见函、情况/表扬/批评通报、讲话/致辞/演讲、书面/现场述职、方案/建设方案、宣传手册/同用途宣传材料均有共同功能且有变体说明。公开发布页分别写公告、公示、通告的差异，未发现被迫套同一缺项或执行骨架的确定错误。 |
| 混合材料 | `genre-routing.md:13,73,82-87` 分开通知壳和附件，技术内容服从原文种；技术需求附件另行处理。多份独立稿件由首页 `:27` 逐份选路。没有把“唯一首叶”误解成整个多稿任务只能有一份主文种。 |
| 增项申请与普通申请 | 索引 `:9-10` 已区分既有项目增项和常规申请；增项页 `:3,7-19` 有独立的已有基础—新增需求—申请关系。未因都含“申请”就判重复主叶。 |
| 必经检查 | 首页 `:77-99` 明确篇幅条件、事实复核、语言检查、脚本复核和交付。部分短叶没有逐一重写检查链，并不构成漏读；它们仍受入口契约约束。 |
| 只审与审后改稿 | `review-checklist.md:5,24-30` 决定交付模式；`prose-lint-usage.md:17-21` 区分被审稿件与审稿意见并保留原文件。没有据首页“检查并处理”的简写断言审核必然偷偷改原稿。 |
| 回接首页 | 主叶写明接回“成稿后的检查顺序”，没有要求重新执行选择文种。`anti-ai-patterns.md:3` 的职责转介也没有无条件重新选路动作，不能证明死锁。 |
| 事务页返回 | 报告 `:25` 加读事务页，事务页 `:7` 或 `:9` 明确停止本页后完成正文。它是有限附加过程；不能把静态链接 A→B→A 直接当强制循环。 |
| 脚本复扫 | `prose-lint-usage.md:25-27` 仅对改动文本复扫，已核对保留的提示允许结束；没有“警告必须归零”的无限修正门。 |
| 首叶可达性 | 39 个主叶均在首页直达、索引或兼容场景路由中有入口；采购附加在索引、技术需求和审查意见中有条件入口；两事务页从报告进入；算力二级例句和术语页有明确条件链接。未发现主叶孤岛。 |
| 构建维护命令 | 已读 SKILL、README 和全部参考页未发现 git/worktree、构建、测试回归、打包、发布命令。`compression-details.md:10` 与 `prose-lint-usage.md:10` 是用户稿件检查命令，属于产品能力，不按维护泄露判。脚本实现未审。 |
| 推断边界 | 首页 `:64`、信息选择 `:23-27` 与多个叶页允许事实和常识支持的原因、意义、影响、合理建议。整改方案 `:10-13` 还允许用户授权下的未来措施。未把这些正常分析当成新增事实错误，也未建议加审批、补证或禁止推断门。 |

## 全覆盖清单

以下均逐页看过实文，范围从第 1 行至表内末行；不是仅搜索文件名。入口和说明 3 页，参考页 72 页，共 75 个文档。全部 40 个 `genre-playbook-*`、2 个事务页及 2 个算力页均覆盖。

### 入口、路由与索引

| 文件 | 实读末行 | 说明 |
| --- | ---: | --- |
| `SKILL.md` | 99 | 主入口、选路、任务模式、统一检查 |
| `README.md` | 46 | 能力问答与面向用户的说明 |
| `agents/openai.yaml` | 4 | Agent 展示与默认入口 |
| `references/reference-index.md` | 69 | 全部首叶与共性/专项入口 |
| `references/genre-routing.md` | 91 | 功能树、混合文种及边界 |
| `references/compatibility-scene-routing.md` | 21 | 全部兼容场景入口 |
| `references/genre-checklist.md` | 27 | 未覆盖文种反查边界 |

### 全部文种页（以下相对于 references/）

| 文件 | 实读末行 | 主功能/附加作用 |
| --- | ---: | --- |
| `genre-playbook-advisory-feedback.md` | 42 | 合作性建议、建议信 |
| `genre-playbook-bulletin.md` | 16 | 情况、表扬、批评通报 |
| `genre-playbook-communique.md` | 5 | 公报 |
| `genre-playbook-complaint-reflection.md` | 38 | 亲历投诉与问题反映 |
| `genre-playbook-correspondence.md` | 18 | 函、复函、征求意见函 |
| `genre-playbook-decision.md` | 5 | 决定 |
| `genre-playbook-deployment.md` | 11 | 事务部署安排 |
| `genre-playbook-duty-report.md` | 16 | 书面与现场述职 |
| `genre-playbook-explanation.md` | 13 | 解释性说明 |
| `genre-playbook-feasibility.md` | 19 | 可研 |
| `genre-playbook-information-materials.md` | 17 | 正式事项宣传手册/材料 |
| `genre-playbook-initiative.md` | 16 | 倡议书 |
| `genre-playbook-institution-rules.md` | 44 | 制度、办法、细则、规程 |
| `genre-playbook-meeting-host.md` | 15 | 会议主持、串词 |
| `genre-playbook-minutes.md` | 18 | 会议纪要 |
| `genre-playbook-motion.md` | 5 | 议案 |
| `genre-playbook-narration.md` | 17 | 讲解稿 |
| `genre-playbook-news-commentary.md` | 13 | 新闻评论 |
| `genre-playbook-news-message.md` | 17 | 新闻消息、编者按 |
| `genre-playbook-notice.md` | 17 | 通知、内部告知 |
| `genre-playbook-open-letter.md` | 16 | 公开信 |
| `genre-playbook-opinion.md` | 13 | 正式意见 |
| `genre-playbook-order.md` | 5 | 命令、令 |
| `genre-playbook-plan-construction.md` | 19 | 方案、实施/建设方案 |
| `genre-playbook-procurement-announcement.md` | 11 | 采购公告、征集公告 |
| `genre-playbook-procurement-review.md` | 11 | 采购专项附加核对 |
| `genre-playbook-project-application.md` | 35 | 既有项目增项申请 |
| `genre-playbook-publication.md` | 13 | 公告、公示、通告 |
| `genre-playbook-remediation-plan.md` | 20 | 本单位整改方案 |
| `genre-playbook-reply.md` | 17 | 批复 |
| `genre-playbook-report.md` | 25 | 报告、情况综合、周/月报 |
| `genre-playbook-request.md` | 23 | 请示、常规申请 |
| `genre-playbook-research.md` | 13 | 调研/研究报告 |
| `genre-playbook-resolution.md` | 5 | 决议 |
| `genre-playbook-responsibility-letter.md` | 16 | 责任书 |
| `genre-playbook-review-opinion.md` | 15 | 独立审查/评审意见 |
| `genre-playbook-speech-address.md` | 15 | 讲话、致辞、演讲 |
| `genre-playbook-technical-requirements.md` | 21 | 技术需求及附件 |
| `genre-playbook-work-priorities.md` | 15 | 工作要点 |
| `genre-playbook-work-summary.md` | 16 | 工作总结 |

### 全部事务、算力及定向跟读页（以下相对于 references/）

| 文件 | 实读末行 | 跟读理由 |
| --- | ---: | --- |
| `transaction-feedback-report.md` | 7 | 报告附加与返回链 |
| `transaction-remediation-report.md` | 9 | 整改事实及返回链 |
| `ai-compute-docs.md` | 34 | 算力附加职责与二级链接 |
| `ai-compute-examples.md` | 19 | 例句隔离与事实前提 |
| `information-selection.md` | 35 | 必经事实、分析、状态契约 |
| `task-route-cards.md` | 12 | 短路径能否省掉主叶/检查 |
| `short-draft-naturalness.md` | 10 | 短稿与文种成立边界 |
| `review-checklist.md` | 34 | 只审、审后改稿及回接 |
| `genre-checklist-request.md` | 23 | 申请/请示专项细查 |
| `genre-checklist-report.md` | 11 | 报告细查及输出模式 |
| `genre-checklist-feasibility-review.md` | 10 | 可研摘要与范围边界 |
| `final-review-layers.md` | 25 | 必经事实/文种检查 |
| `delivery.md` | 24 | 正文与提示、只要正文 |
| `handling-elements.md` | 22 | 办理要素与缺项转介 |
| `argument-chains.md` | 18 | 论证、比较与推断 |
| `field-editing.md` | 3 | 字段精确修改、重复规则 |
| `structure-editing.md` | 9 | 结构修改与最新版边界 |
| `compression-details.md` | 23 | 篇幅条件、测量、复测退出 |
| `anti-ai-patterns.md` | 56 | 必经语言复核与算力旁路 |
| `prose-lint-usage.md` | 29 | 命令归属、复扫及停止 |
| `proofreading-checklist.md` | 9 | 条件校对与范围 |
| `official-style.md` | 30 | 语言建议是否侵入事实 |
| `formal-addressing.md` | 30 | 称谓、行文关系 |
| `speech-person-order.md` | 10 | 讲话/主持人物顺序附加 |
| `format-gbt9704.md` | 107 | Word/正式发文分界及检查卡 |
| `external-research.md` | 16 | 研究触发、停止和来源边界 |
| `formulaic-language.md` | 36 | 固定用语、历史模板 |
| `technical-terms.md` | 10 | 算力术语二级资料 |

## 未读及未运行范围

候选内未读取 `LICENSE`、`scripts/draft_length.py`、`scripts/prose_lint.py` 的实现。脚本使用说明已全文读过；没有执行脚本、写稿、外部检索或链接页面核验。未读取候选目录之外的旧版、产品源码、其他报告、映射、评分、Git 历史或审计材料。

唯一新增文件为本审计报告。未修改产品、未提交或合并代码；报告交由主任务按其已有授权整合。
