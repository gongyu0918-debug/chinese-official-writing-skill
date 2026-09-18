## SKILL.md

---
name: chinese-official-writing
description: 用于中文公文、事务性材料和新闻稿件的起草、改写、压缩、润色、审校、文种核对、去口语化、降 AI 味及 Word 格式处理，适用于机关、企事业单位、学校和新闻机构。涵盖申请、请示、报告、通知、通告、意见、决定、决议、议案、公报、命令、函、复函、批复、说明、方案、纪要、公告、公示、通报、制度、规定、办法、细则、操作规程、工作要点、总结、调研、讲话、致辞、主持词、述职、可研、审查材料、技术需求、新闻消息、编者按、新闻评论，以及采购、整改、反馈和 AI 算力等场景。
metadata:
  tags: chinese, official-document, writing, gongwen, ai-compute
---

# 中文公文写作

## 适用范围

处理中文公文、事务性材料、正式工作材料、新闻消息、新闻评论，以及这些文本的起草、改写、压缩、润色、文种核对、事实边界复核和 Word 正文整理。英文、文学、营销软文、社交媒体文案、个人求职信和代码说明走其他路径。

查询 Skill 能力时读取 `README.md`。

## 入口契约

### 第一步：理解用户需求

从请求中识别以下信息：

- **任务与交付件**：起草、改写、压缩、审核或格式处理；需要一份稿件、多份稿件、审稿意见，还是审核后的改好稿件。
- **稿件用途**：谁以什么身份写给谁，是请求批准、汇报情况、告知安排、记录会议，还是表达意见；结合用户给出的文种或模板判断。
- **材料与修改范围**：使用哪份最新版底稿，本轮改哪些内容，哪些事实、状态、标题和字段需要保留。
- **篇幅与形式**：字数要求、短稿或长稿、文件格式，以及用户明确提出的交付偏好。

主送和落款按材料或用户模板填写。材料只给回执接收方、联系人或承办部门时，不据此补发文单位；未给的主送、落款不填“上级单位”“申请单位”等泛称。

信息足以判断时继续处理；稿件用途尚无法确定时，集中询问影响选路的信息。独立稿件及具有独立用途的附件分别选路；文内背景和引用按主文本用途处理。

### 第二步：选择文种

需要处理正文内容时，以用户模板、最新版底稿、明确标题和用途选路。用户限定仅排版、保留文字时，直接按格式任务处理。

按 `references/reference-index.md` 为每份稿件选定一个主叶；标题、模板、正文用途或行文关系有冲突时，先读 `references/genre-routing.md` 判定，再选主叶。

### 第三步：按任务加读

选定主文种后，根据本轮任务加读：

- **起草**：按主文种组织必要要素和合理分析。
- **改写**：以最新版底稿为基础，按实际的结构、字段或语言调整加读相应页。
- **局部修改、重排或字段处理**：结构动作读 `references/structure-editing.md`，字段动作读 `references/field-editing.md`；以最新版底稿为唯一主线。
- **压缩或限字**：先按文种成稿，再按需读 `references/compression-details.md`；压缩始终保留文种硬要素、事实状态和用户点名字段。
- **审核、复核、审校或把关**：读取对应主文种/事务叶和 `references/review-checklist.md`，按该页确定审稿意见或改后稿件。
- **格式交付**：内容和办理要素核对完成后，再按用户要求读取 Word、GB/T 9704 或格式工具页。

需要 Word、docx、GB/T 9704、红头或正式版式时叠加 `references/format-gbt9704.md`。主文种已确定且稿件明确涉及 AI 算力、模型推理/训练、智算中心或模型服务资源时，在主文种叶上叠加 `references/ai-compute-docs.md`；服务器、GPU、Token、并发等词结合实际业务判断，普通服务器、接口、安全、SLA 或验收内容单独出现时沿用主文种规则。

用户已有提纲、模板、标题顺序或字段表时优先保留。

## 材料与通用写法核查

遇到尚不熟悉的新文种、新材料类型、特殊事务场景，或需要核查通用写法、必备要素、正式格式和常用语时，读取 `references/external-research.md` 并进行定向联网核查；用户明确要求搜索，或任务涉及“最新数据、今日情况、当前政策、现行规定、近期数据”等时效事实时同样启用。检索补充写作规则和来源背景，网络材料作为背景依据，用户事实仍以用户材料为准；记录来源、日期和检索口径，冲突或无法核验列为待确认。常规已知文种沿用已有路线。

## 正文形态

正式正文直接呈现事实、办理事项和有据分析。

- AI 身份自述、提示词披露严禁出现。
- 思考过程、隐藏推理严禁出现。
- 起草步骤、脚本结果、制作说明严禁出现。
- 起草免责话术、连续追问及“正文如下”等引导语严禁出现。

普通文字稿不得用井号标题、Markdown 加粗、整稿代码围栏或横线包装。用户明确要求 Markdown、代码或固定模板时按要求处理。

纯文本主标题独立成行，行末省略句号，标题后空一行；层级标题省略行末句号，与其统领的正文分段。编号内容本身是完整正文句时，保留正常句末标点。用户模板优先。Word 小标题是否独立成段按模板和实际统领关系判断。网页复制稿先剥离来源、栏目路径、责任编辑、字号和打印元信息；“关于印发”的通知壳、被印发文件正文和附件关系分开处理。

## 写作与交付步骤

按 `references/writing-rules.md` 完成以下四步，具体命令与处理要求见该页：

1. 材料与分析：核对本轮材料、修改范围及分析依据。
2. 成稿与篇幅：按文种成稿，有篇幅要求时运行 `scripts/draft_length.py`。
3. 复核：核对事实、文种与语言，完成抗 AI 味检查；按 `references/prose-lint-usage.md` 运行 `scripts/prose_lint.py` 并处理风险。
4. 交付：给出稿件、审核意见或文件，按交付要求单列文后提示。


## references/reference-index.md

# 参考资料索引

根据用户已经明确的稿件用途，在下表选读对应主文种；需要共性能力时按触发条件加读。

## 文种与场景首叶

### 文种专页

- 既有项目新增功能、服务或实施内容的增项申请：`genre-playbook-project-application.md`。
- 请示、普通采购或经费等申请：`genre-playbook-request.md`；审核、复核、审后改稿，或细查请批事项和办理要素时，读取 `genre-checklist-request.md`。
- 报告、情况报告、情况综合、周报、月报：`genre-playbook-report.md`；报告功能或状态表达拿不准时用 `genre-checklist-report.md`。
- 工作总结：`genre-playbook-work-summary.md`。
- 工作要点：`genre-playbook-work-priorities.md`。
- 通知：`genre-playbook-notice.md`；情况、表扬或批评通报：`genre-playbook-bulletin.md`。
- 公开采购、征集供应商响应或发布采购事项告知的采购公告：`genre-playbook-procurement-announcement.md`。采购方案仍走方案主叶，独立采购清单按 `field-editing.md` 保留字段形态。
- 其他公告、公示、通告：`genre-playbook-publication.md`。
- 决定：`genre-playbook-decision.md`；决议：`genre-playbook-resolution.md`；议案：`genre-playbook-motion.md`。
- 公报：`genre-playbook-communique.md`；命令、令：`genre-playbook-order.md`；部署安排：`genre-playbook-deployment.md`。
- 上级对下级请示的批复：`genre-playbook-reply.md`。
- 不相隶属单位之间商洽、询答、请求批准或答复审批事项的函、复函、征求意见函，以及代表建议、委员提案的办理答复：`genre-playbook-correspondence.md`。
- 意见：`genre-playbook-opinion.md`；解释事实、既有流程或回应疑问的说明：`genre-playbook-explanation.md`。
- 会议纪要：`genre-playbook-minutes.md`。
- 讲话稿、致辞、演讲：`genre-playbook-speech-address.md`；开场人物顺序另加 `speech-person-order.md`。
- 会议主持词、主持串词：`genre-playbook-meeting-host.md`；开场人物顺序另加 `speech-person-order.md`。
- 书面述职、述职报告、履职情况报告、现场述职发言：`genre-playbook-duty-report.md`。单位工作报告或工作总结仍走各自主叶。
- 方案、实施方案、建设方案：`genre-playbook-plan-construction.md`。
- 技术需求书、软件需求说明、接口需求和技术需求附件：`genre-playbook-technical-requirements.md`；按所需能力和条件组织，技术主题不改变方案或可研的主文种。
- 作为执行规则交付的制度、规定、办法、细则、操作规程：`genre-playbook-institution-rules.md`。
- 责任书：`genre-playbook-responsibility-letter.md`。
- 倡议书：`genre-playbook-initiative.md`；公开信：`genre-playbook-open-letter.md`。
- 讲解稿：`genre-playbook-narration.md`。
- 正式事项说明用途的宣传手册、宣传材料：`genre-playbook-information-materials.md`。
- 调研、研究：`genre-playbook-research.md`；可研：`genre-playbook-feasibility.md`；只审可研用 `genre-checklist-feasibility-review.md`。
- 独立审查意见、评审意见（包括采购、初步设计或项目材料）：`genre-playbook-review-opinion.md`；只审核既有稿件时保留原主文种，按首页审稿模式处理。
- 新闻消息、活动报道：`genre-playbook-news-message.md`。
- 编者按、编发按语：`genre-playbook-editorial-note.md`。
- 新闻评论、时评：`genre-playbook-news-commentary.md`。
- 意见建议、建议信、投诉反映、整改方案：先读 `compatibility-scene-routing.md`，再进入对应专页；建议信按面向有权方提出合作性建议的用途进入意见建议页，法定“意见”直接进入意见主叶。
- 整改进展、整改情况：按报告、说明或情况通报的用途选主叶，并加读 `transaction-remediation-report.md`；反馈情况报告：报告主叶 + `transaction-feedback-report.md`。

### 目录未命中时

事务名称未列出时，按实际用途匹配上述专页。用途已明确且没有适用专页时，读取 `genre-checklist.md`。

## 共性能力页

| 能力 | 读取条件 | 作用 |
| --- | --- | --- |
| `argument-chains.md` | 需要展开方案比较、跨段论证或执行链条 | 只组织已有依据支持的论证 |
| `formal-addressing.md` | 行文关系、敬语或称谓拿不准 | 锁定称谓和关系 |

## 专项资料

- 固定用语或衔接选用拿不准时，读取 `formulaic-language.md`。
- 不熟悉的新文种、新材料类型、特殊事务场景，或需要核查通用做法、必备要素、正式格式、常用语及外部最新事实时：`external-research.md`；常规已知文种不自动扩展搜索。
- 长文压缩和超限处置：`compression-details.md`。
- 字段拆行、增删和表单边界：`field-editing.md`。
- 结构增删、移动和标题重排：`structure-editing.md`。
- 材料报送、征集需区分填报主体、统计口径、分层汇总或多项材料要求时：`material-submission.md`。简单单项提交按主文种写清材料、期限和渠道。
- 采购需求、规格报价、响应规则或履约条件需要专项核对时：在已选主文种上叠加 `genre-playbook-procurement-review.md`；只做语言或格式审校时不因此加读。
- 编制预算、说明多项费用构成、核对年度或分期资金及申请额度时：`funding-budget.md`。简单单项费用直接按主文种写清用途和金额。
- 组织信息系统新建、改造、整合或运维的需求、范围和实施安排时：`information-system-projects.md`。普通设备购买、活动消息或仅改语言格式时，按主文种和本次任务处理。
- AI 算力场景：按首页的场景条件叠加 `ai-compute-docs.md`。独立技术需求进入 `genre-playbook-technical-requirements.md`。


## references/genre-playbook-correspondence.md

# 函、复函与征求意见函

函用于不相隶属单位间商洽、询问答复、征求意见、请求批准和答复审批事项，按实际用途与收发双方职权确定写法。上级答复下级请示用批复，转 `genre-playbook-reply.md`。

向代表、委员等个人答复建议、提案时，按函组织答复，称谓对应实际接收人。

## 成稿骨架

来文或事项背景 → 本次商洽、答复、征求意见或请批事项 → 办理意见与必要反馈信息。

- 商洽、询问或征求意见：写明具体事项，用平等沟通语气；需要对方反馈时写清反馈路径。
- 请求批准：说明理由和具体请求，使用请批语，保留尚待批准的状态。
- 回复来文方对建议、提案或转办事项的诉求时，加读 `handling-response.md`，对应各项诉求说明办理情况。
- 审批答复：承接来函，在有权范围内按材料已有结论明确同意、不同意及条件和范围；缺少授权或结论依据时不代作批准。

称谓服从用户模板和已给主体；对不相隶属单位可用“贵单位”等中性称谓。商洽可用“商请”“请予支持”，请批可用“请予批准”，复函对应来文作出答复，结语随本次用途确定。

材料已给或办理确有需要时，保留反馈期限、方式、联系人和附件；材料未给且不影响办理时不把这些内容补成固定要素。


## references/material-submission.md

# 材料报送与征集

多项材料、分层汇总或不同统计口径的报送与征集，按以下关系组织要求。

- 分清谁填报、统计谁、由谁汇总。把本次确定的填报主体落实到主送和办理要求；改稿时同步修正旧稿中范围不符的称呼。
- 每项材料对应填报内容、统计期间或时点、提交期限和渠道。基层提交与汇总报出分别写清；意见征集对应具体事项、版本或问题。
- 对照正文和附件核准名称、序号、填报单元及数值口径。电子版、纸质版和签字盖章等要求依本次安排分别落实到相应材料。
- 零值、无此事项和待核实分别表达，零报送依本次要求处理。已明确的更正落实到正文；仍影响提交的缺项或矛盾集中列入文后提示。


## references/handling-response.md

# 事项办理答复

围绕来文方提出的诉求组织答复，把已经办到的程度与还需解决的部分说清楚。

- 逐项回应处理意见和覆盖范围。关联诉求可合并说明，逐项核对哪些已解决、哪些只解决了一部分，哪些仍需处理。
- 用已采取的措施和实际结果说明办理进展。研究、协调、列入计划各按当前环节表达，并交代落实诉求还需要完成的工作或条件。
- 重点说明尚待解决事项的制约原因、可行方向及所需配合。材料和常识支持的原因、影响与拟议做法可展开；涉及多个主体时，分别交代本单位行动和需要其他主体决定、配合的部分。


## references/genre-playbook-procurement-announcement.md

# 采购公告

采购公告公开采购项目的征集响应、结果、更正或终止等事项，按本次发布目的选择要素；内部采购申请或审查按实际交付件处理。

## 成稿骨架

先交代采购主体、项目及适用包次，再按发布目的展开：

- 征集响应：采购内容、数量、预算或上限 → 已给的资格或响应条件 → 文件获取、响应期限和提交方式。
- 结果告知：已形成的中标或成交结果 → 对应供应商、结果金额及主要标的信息。
- 更正事项：标明原项目、包次及原公告，再交代更正内容、理由和处理结论。更正前内容依据原公告填写；材料只有原公告名称或日期时，可据此指回原文。后续签约、供货、整改和解约事实放在本次更正理由中；处理安排按本次决定的范围与状态表述。
- 终止事项：终止的项目或包次、范围 → 当前状态和已给原因 → 材料已有的后续安排。

联系方式、公告期限、附件以及评审或后续安排，按本次材料、模板及适用发布要求保留。只提示影响当前发布目的的缺项，不把响应条件、递交期限等征集要素强加给结果或终止公告。

保持客观告知语气，核对项目或包次与公开事项相符；预算或上限、估算价与中标或成交金额不互换。结果未定不写成既定，终止不自行改为重新采购或项目永久取消。

AI 算力场景按首页条件叠加 `ai-compute-docs.md`。


## references/writing-rules.md

# 共性写作与交付

## 第一步：材料与分析

以本轮有效材料、最新版底稿和用户模板为准，落实补充、更正及修改范围。主体、对象、数字、金额、业务日期、引语、来源和事实状态照实保留；引用旧稿、样文或模型先前补写内容时重新核对依据。

材料与常识支持的原因、目的、影响、合理下一步、自然延续和结论可展开，主体、范围和强度与依据相称，多种解释保留不确定性。具体经历、数值、期限、程序、责任、决定和成效须有依据；只有主题或方向时可写功能和拟议做法，授权拟方案时可提出措施，现状与建议分清。

拟、建议、可选、进行中、待核和未决定保持原程度。分清信息未给与业务未定、暂无结果与是否启动；可核算合计差额；其余分项是否正常仍分别核对。

业务日期沿用材料，年份可继承明确语境。需要落款且未给日期时，用系统或工具确认的当天日期作为草稿日期；指定留空、待确认或模板空位的按要求保留。

先完成可用正文，实质缺项集中在文后提示。仅排版、逐字保留或不作分析的限制照办。

## 第二步：成稿与篇幅

按主文种写全要素、缘由、用途和合理衔接。普通完整短稿至少80字；局部替换、字段处理或明确要求更短时按实际范围处理。

围绕事项组织自然段，一两句话可直接承接章节功能；标题和编号用于区分事项、方便查阅。保留用户的标题、顺序、模板、字段、表格及指定空位，清理无用途占位。完成文种动作即可收束，指定尾语照录；上限无需填满，保留事实和有作用的分析。

有篇幅要求（含上述下限）时，将稿件保存为临时文件，以已读SKILL.md所在目录定位脚本，按实际上下限运行：

```text
python "<Skill目录>/scripts/draft_length.py" --min-chars 80 "<草稿绝对路径>"
```

默认计非空白字符，含正文及所需标题、落款、附件，文后提示单列；用户另定范围或口径时按要求。复杂计数、长文分配或压缩读取 `compression-details.md`。不足时补全材料和合理分析，仍不足则在文后提示说明实测差额与所需材料。

## 第三步：复核

按材料和主文种核对事实、状态、要素及本轮改动；整体查全文，局部查改动与关联内容。跨段、多主体及正文、表格、附件核对主体、名称、数值、顺序、期限、结论、状态与指向，分清实测、测算和估算。Word按模板核样式，保留要求的批注和修订。

所有成稿、改后稿和审核任务读取 `anti-ai-patterns.md` 检查语言；用户要求校对，或引语、成语、专门术语需核准时，读取 `proofreading-checklist.md`。

读取 `prose-lint-usage.md`，运行文稿扫描并处理风险。交付前修正范围内已确认的问题；实质修改后核对关联内容并复扫，影响篇幅时另测字数。运行受限时完成可做的检查，如实记录未完成项。

含保密标识、内部数据或个人信息时，按接收对象及发布范围核对保留、脱敏或需确认内容；明确标为绝密、机密或秘密时，提示正式使用前人工保密审查。

## 第四步：交付

起草及审后改稿交付完整稿件；审核给出位置、问题和建议改法，AI味问题列原句及可用替代表达；用户同时要求两项时一并交付。

按用户要求整理底稿样式，最终回复中的稿件也遵守本轮格式要求。

交付消息从稿件、审核意见或文件链接开始。给用户的是所需成果，自己怎样读规则、想问题、调用工具、写稿和检查的过程留在内部。

交付前核对整条消息，删去这类过程说明。例如：
- “我先读取该技能的说明文件，再按其中规范审核改写。”这是讲自己的操作过程。
- “成稿123个非空白字符（脚本校验在120—220内，文稿扫描无风险项）。”这是汇报自检结果。

这些话放在开头、文后提示或结束语中同样要删除，正文形态中的旁白禁令适用于整条交付消息。审核时说明原句哪里有问题、依据是什么、怎样改，属于应交付的意见；影响稿件使用的缺项、风险及未完成检查如实写入文后提示。

影响文种成立、请批、执行或用户明示要求的缺项、矛盾，以及影响使用的风险、修改建议、上轮未解决事项和已发现未处理错误，默认在完整稿件后空一行，以无编号“文后提示”单列。遗留错误注明位置、未处理原因和下一步；移除已解决、已给定及无关事项，无实质事项时可给简短提示。

正文编号、落款和附件在提示前结束；文件交付时提示留在消息中。明确只要稿件或省略说明时省略提示，“写完整稿子”仍按通常形式交付。


## 本次差异

diff --git a/chinese-official-writing/references/genre-playbook-correspondence.md b/chinese-official-writing/references/genre-playbook-correspondence.md
index 477c8568..b10d31e6 100644
--- a/chinese-official-writing/references/genre-playbook-correspondence.md
+++ b/chinese-official-writing/references/genre-playbook-correspondence.md
@@ -2,12 +2,15 @@
 
 函用于不相隶属单位间商洽、询问答复、征求意见、请求批准和答复审批事项，按实际用途与收发双方职权确定写法。上级答复下级请示用批复，转 `genre-playbook-reply.md`。
 
+向代表、委员等个人答复建议、提案时，按函组织答复，称谓对应实际接收人。
+
 ## 成稿骨架
 
 来文或事项背景 → 本次商洽、答复、征求意见或请批事项 → 办理意见与必要反馈信息。
 
 - 商洽、询问或征求意见：写明具体事项，用平等沟通语气；需要对方反馈时写清反馈路径。
 - 请求批准：说明理由和具体请求，使用请批语，保留尚待批准的状态。
+- 回复来文方对建议、提案或转办事项的诉求时，加读 `handling-response.md`，对应各项诉求说明办理情况。
 - 审批答复：承接来函，在有权范围内按材料已有结论明确同意、不同意及条件和范围；缺少授权或结论依据时不代作批准。
 
 称谓服从用户模板和已给主体；对不相隶属单位可用“贵单位”等中性称谓。商洽可用“商请”“请予支持”，请批可用“请予批准”，复函对应来文作出答复，结语随本次用途确定。
diff --git a/chinese-official-writing/references/genre-playbook-procurement-announcement.md b/chinese-official-writing/references/genre-playbook-procurement-announcement.md
index 9be2410f..3f4653cb 100644
--- a/chinese-official-writing/references/genre-playbook-procurement-announcement.md
+++ b/chinese-official-writing/references/genre-playbook-procurement-announcement.md
@@ -1,6 +1,6 @@
 # 采购公告
 
-采购公告公开采购项目的征集响应、结果或终止等事项，按本次发布目的选择要素；内部采购申请或审查按实际交付件处理。
+采购公告公开采购项目的征集响应、结果、更正或终止等事项，按本次发布目的选择要素；内部采购申请或审查按实际交付件处理。
 
 ## 成稿骨架
 
@@ -8,6 +8,7 @@
 
 - 征集响应：采购内容、数量、预算或上限 → 已给的资格或响应条件 → 文件获取、响应期限和提交方式。
 - 结果告知：已形成的中标或成交结果 → 对应供应商、结果金额及主要标的信息。
+- 更正事项：标明原项目、包次及原公告，再交代更正内容、理由和处理结论。更正前内容依据原公告填写；材料只有原公告名称或日期时，可据此指回原文。后续签约、供货、整改和解约事实放在本次更正理由中；处理安排按本次决定的范围与状态表述。
 - 终止事项：终止的项目或包次、范围 → 当前状态和已给原因 → 材料已有的后续安排。
 
 联系方式、公告期限、附件以及评审或后续安排，按本次材料、模板及适用发布要求保留。只提示影响当前发布目的的缺项，不把响应条件、递交期限等征集要素强加给结果或终止公告。
diff --git a/chinese-official-writing/references/handling-response.md b/chinese-official-writing/references/handling-response.md
new file mode 100644
index 00000000..9644b824
--- /dev/null
+++ b/chinese-official-writing/references/handling-response.md
@@ -0,0 +1,7 @@
+# 事项办理答复
+
+围绕来文方提出的诉求组织答复，把已经办到的程度与还需解决的部分说清楚。
+
+- 逐项回应处理意见和覆盖范围。关联诉求可合并说明，逐项核对哪些已解决、哪些只解决了一部分，哪些仍需处理。
+- 用已采取的措施和实际结果说明办理进展。研究、协调、列入计划各按当前环节表达，并交代落实诉求还需要完成的工作或条件。
+- 重点说明尚待解决事项的制约原因、可行方向及所需配合。材料和常识支持的原因、影响与拟议做法可展开；涉及多个主体时，分别交代本单位行动和需要其他主体决定、配合的部分。
diff --git a/chinese-official-writing/references/material-submission.md b/chinese-official-writing/references/material-submission.md
new file mode 100644
index 00000000..4d9b1f66
--- /dev/null
+++ b/chinese-official-writing/references/material-submission.md
@@ -0,0 +1,8 @@
+# 材料报送与征集
+
+多项材料、分层汇总或不同统计口径的报送与征集，按以下关系组织要求。
+
+- 分清谁填报、统计谁、由谁汇总。把本次确定的填报主体落实到主送和办理要求；改稿时同步修正旧稿中范围不符的称呼。
+- 每项材料对应填报内容、统计期间或时点、提交期限和渠道。基层提交与汇总报出分别写清；意见征集对应具体事项、版本或问题。
+- 对照正文和附件核准名称、序号、填报单元及数值口径。电子版、纸质版和签字盖章等要求依本次安排分别落实到相应材料。
+- 零值、无此事项和待核实分别表达，零报送依本次要求处理。已明确的更正落实到正文；仍影响提交的缺项或矛盾集中列入文后提示。
diff --git a/chinese-official-writing/references/reference-index.md b/chinese-official-writing/references/reference-index.md
index c06612b1..7f2ba47c 100644
--- a/chinese-official-writing/references/reference-index.md
+++ b/chinese-official-writing/references/reference-index.md
@@ -17,7 +17,7 @@
 - 决定：`genre-playbook-decision.md`；决议：`genre-playbook-resolution.md`；议案：`genre-playbook-motion.md`。
 - 公报：`genre-playbook-communique.md`；命令、令：`genre-playbook-order.md`；部署安排：`genre-playbook-deployment.md`。
 - 上级对下级请示的批复：`genre-playbook-reply.md`。
-- 不相隶属单位之间商洽、询答、请求批准或答复审批事项的函、复函、征求意见函：`genre-playbook-correspondence.md`。
+- 不相隶属单位之间商洽、询答、请求批准或答复审批事项的函、复函、征求意见函，以及代表建议、委员提案的办理答复：`genre-playbook-correspondence.md`。
 - 意见：`genre-playbook-opinion.md`；解释事实、既有流程或回应疑问的说明：`genre-playbook-explanation.md`。
 - 会议纪要：`genre-playbook-minutes.md`。
 - 讲话稿、致辞、演讲：`genre-playbook-speech-address.md`；开场人物顺序另加 `speech-person-order.md`。
@@ -56,6 +56,7 @@
 - 长文压缩和超限处置：`compression-details.md`。
 - 字段拆行、增删和表单边界：`field-editing.md`。
 - 结构增删、移动和标题重排：`structure-editing.md`。
+- 材料报送、征集需区分填报主体、统计口径、分层汇总或多项材料要求时：`material-submission.md`。简单单项提交按主文种写清材料、期限和渠道。
 - 采购需求、规格报价、响应规则或履约条件需要专项核对时：在已选主文种上叠加 `genre-playbook-procurement-review.md`；只做语言或格式审校时不因此加读。
 - 编制预算、说明多项费用构成、核对年度或分期资金及申请额度时：`funding-budget.md`。简单单项费用直接按主文种写清用途和金额。
 - 组织信息系统新建、改造、整合或运维的需求、范围和实施安排时：`information-system-projects.md`。普通设备购买、活动消息或仅改语言格式时，按主文种和本次任务处理。
