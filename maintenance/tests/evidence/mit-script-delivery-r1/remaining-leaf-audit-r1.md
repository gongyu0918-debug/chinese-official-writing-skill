# 剩余主叶审核与局部修复记录（R1）

## 一、范围与判断口径

本轮审核对象为 `output/route-worktrees/reference-rewrite-20260912/chinese-official-writing` 下的主文种页及其为确认冲突而直接指向的必要叶子。审核遵循“一项任务读取一个必要主叶，再按明确触发条件叠加共性页或场景页”的目标；不以文件数量越少或拆分越细为优化目标。同一功能家族内的变体可以共用主叶，只有正文目的、主体关系或核心骨架不同，才视为多个文种混杂。

本轮未修改 `SKILL.md`、`reference-index.md`、manifest、测试或其他未授权文件，未联网、未读取历史证据、未运行测试，也未提交或同步。初审后按根任务授权，仅修改七个 reference 文件；本报告记录审前证据、已执行修复和仍待处理项。

## 二、审前主要发现与处置

### 1. 请示/申请页存在回到选路起点的循环（已修复）

审前 `references/genre-playbook-request.md:19` 规定，多品类、分项核算、比价验收、技术附件或长篇任务“转读 `workflow.md`、`handling-elements.md` 和 `argument-chains.md`”。当时 `workflow.md:5` 又要求选择唯一首叶，会让已经确定为请示/申请的任务重新选叶，形成“申请主叶 → 共用工作流 → 选择申请主叶”的循环，也会让一项任务无必要地重跑入口流程。

已将 `genre-playbook-request.md` 改为：复杂申请仍以本页为主文种；需要核对主体、金额、期限、附件或反馈时加读 `handling-elements.md`，需要解释必要性或比较方案时加读 `argument-chains.md`。这样保留一个主叶，只按信号附加共性能力。`workflow.md` 现已由根任务或另一 agent 移除，本轮未修改该文件。

### 2. 采购公告在通用公开发布与采购公告专页之间存在双主叶（已修复局部路由）

审前 `references/genre-routing.md:34` 将所有“公告、公示、通告”指向 `genre-playbook-publication.md`，但同页审前第 57 行又单独提到采购公告；`references/reference-index.md:21` 则明确将采购公告指向 `genre-playbook-procurement-announcement.md`。这会让“采购公告”因先命中“公告”而进入通用发布页，或同时读取两个主叶。

已在 `genre-routing.md` 中把“公开采购、征集供应商响应或发布采购事项告知”优先指向 `genre-playbook-procurement-announcement.md`，其他公告、公示、通告再进入 `genre-playbook-publication.md`；边界段也改为采购公告、征集公告和采购事项告知优先进入采购公告专页。`reference-index.md` 的全局映射由根任务处理，本轮未修改。

### 3. 情况说明被报告页与说明页同时宣称覆盖（已修复局部边界）

审前 `references/genre-playbook-report.md:3` 无条件宣称处理“情况说明”，而 `references/genre-playbook-explanation.md:3-11` 将说明定义为解释事实、原因、过程、做法或事项边界的独立主叶，并明确“需要汇报工作和问题时转报告”。同时，`reference-index.md:10,14` 分别列出报告和说明。这会让标题相同但用途不同的材料落入两个主叶。

已从报告页去掉对“情况说明”的无条件覆盖，并在报告页和 `genre-routing.md` 写明按实际用途判断：解释具体事实、原因或回应疑问时进入说明主叶；汇报工作进展、问题或处置时进入报告主叶。判断依据是正文功能，不机械按标题选路。

### 4. 会议纪要被固定列为下行文，主体方向可能被误判（已修复）

审前 `references/genre-routing.md:18` 把会议纪要列入下行关系，而 `references/genre-playbook-minutes.md:7,13-18` 的核心是记录会议形成的事项、责任、期限及未决状态。纪要的功能来自会议记录和议定事项，分发对象并不当然赋予下行命令语气。

已从下行文举例中移除会议纪要，并增加“会议记录”判断：纪要按会议讨论和形成的事项选路，不预设为上行或下行；分发对象、责任主体和期限沿用材料。

### 5. 局部主叶可能提前进入交付或把全局必查项写成可选（已修复）

审前存在三类冲突：

- `references/genre-playbook-project-application.md:3,31,33-35` 自称本页完成成稿检查，正文形成后直接按交付页处理；这可能绕过 `SKILL.md:77-99` 的统一五步检查。
- `references/genre-playbook-institution-rules.md:37-43` 另设“交付前检查”，重复承载 anti-AI、事实和 Word 终检，容易形成第二套终稿出口。
- `references/genre-playbook-speech-address.md:12` 把 `anti-ai-patterns.md` 与语言复核一起写成“需要时”才读取，而主页要求所有成稿、改后稿和审核任务均读取该页。

已将增项申请页的本地清单改为“增项申请专项核对”，删除直达 delivery 的语句，末尾接回 `SKILL.md` 的“成稿后的检查顺序”；制度页的“交付前检查”改为“制度专项核对”，只保留制度专属核对点，并接回统一检查；讲话页仅把 `official-style.md` 保留为按需语言附加页，专项核对后接回主页统一检查，不再把 anti-AI 检查写成可选。

### 6. 请示/申请审核清单会把条件性栏目误当必备事实（已修复）

审前 `references/genre-checklist-request.md:12,18-19,23` 将经费或资源需求、拟实施安排、使用计划、承诺、绩效目标和真实性承诺列为固定内容，与 `genre-playbook-request.md:18-21` 的材料边界相冲突。对普通申请或材料稀疏的经费申请，这种写法可能反向要求补造计划、承诺或绩效事实。

已保留“一文一事、明确请批事项、请批结尾、申请主体和申请事项”等文种成立要素；其他栏目改为由用户模板、材料或具体申请事项触发。绩效目标、真实性承诺只有模板要求或材料明确时才保留，不能为了栏目完整而新增。

## 三、同文种变体与真正混杂的区分

### 无需机械拆分的主叶

- `references/genre-playbook-publication.md:1-13` 中的公告、公示、通告都承担面向社会或一定范围公开发布的功能，差异集中在公开事项、期限、异议渠道和应知应遵要求，属于同一公开发布功能家族。采购公告因核心是供应商公开响应规则而进入采购公告专页；这不意味着普通公告、公示、通告还需继续拆成三页。
- `references/genre-playbook-institution-rules.md:3-24` 中的制度、规定、办法、管理办法、实施细则和操作规程都属于规范性文稿，正文共同围绕适用范围、职责、规则、程序和附则展开。细则和规程的操作密度不同，但仍可在同一主叶内按形态分流。
- `references/genre-playbook-minutes.md:1-18` 保持单一的会议记录骨架，议题、议定事项、责任、期限和未决状态一致，不存在必须拆页的多文种结构。

### 仍存在的真正多骨架混杂（未处理）

`references/genre-playbook-speech-address.md:1,7-8` 同时覆盖讲话稿、致辞、演讲、会议主持开场和述职报告，并只给出“场合身份 → 主题态度 → 事实或工作基础 → 重点任务/体会 → 责任或目标”的统一骨架。其中：

- 讲话、致辞、演讲都是特定身份面向听众表达主题和态度，可继续作为同一主叶内的变体。
- 书面述职的主要任务是汇报职责履行、工作结果、问题和下一步，主体方向及证据组织更接近报告或工作总结。
- 完整主持词的主要任务是连接议程、介绍环节、控制会序和完成转场，不能用讲话骨架替代。`speech-person-order.md:1-10` 只解决开场人物排序，明确不覆盖全文写作，不能充当主持词主叶。

本轮按授权未新增主持或述职页面，也未改变讲话页覆盖范围。最小合理去向建议是：讲话、致辞、演讲保留在现页；书面述职根据交付用途归报告或工作总结路线；完整主持词需要独立的程序性骨架，人物排序页仅作条件附加页。应由根任务结合全局映射决定文件和入口改动。

## 四、增项申请页角色评估（未处理）

`references/reference-index.md:9` 审前把“请示、申请、增项申请”同时列到 `genre-playbook-request.md` 与 `genre-playbook-project-application.md`。后者 `genre-playbook-project-application.md:1-35` 仍包含完整的申请组织、请批收束和专项核对，因此在“既有项目增项申请”任务中可能与普通申请主叶形成双主叶。

从一任务一个必要主叶的目标看，最小合理方案是让 `genre-playbook-request.md` 承担请示/申请的通用主骨架，把 `genre-playbook-project-application.md` 定位为“既有项目增项”条件场景页，只保留原项目基础与本次增项的区分、需求来源、阶段费用和已有/未决状态等增项特有规则。另一可行方案是明确让增项申请独占专页，并在索引中规定命中增项后不再读取普通申请主叶。两种方案不能并存；建议根任务结合全映射和现有调用证据选择其一。

本轮未改变增项页角色，只消除了它自行完成终稿检查和直达交付的出口，使其无论最终作为主叶还是场景页，都接回统一成稿检查。

## 五、其他路由与维护结论

- 审前 `reference-index.md:29` 对未覆盖文本要求同时读取 `genre-routing.md` 和 `genre-checklist.md`，而路由页确定用途后转专页、清单页又要求选择最近主叶，存在重复 fallback 的可能。最小规则应是：先由 routing 判定，命中即进入唯一主叶；确实未覆盖时，才让 checklist 作为一次性兜底。该项涉及未授权文件，本轮未修改。
- 所审范围未发现把仓库构建、版本、发布、回归测试或内部维护命令写进产品写作规则的明显泄露。
- 七页修复没有引入新的否定堆叠；事实和主体边界仍允许材料事实与常识直接支持的一层、低强度合理分析，未把“不得编造”扩大成“不得分析”。

## 六、已修改文件清单

1. `references/genre-playbook-request.md`
2. `references/genre-checklist-request.md`
3. `references/genre-playbook-speech-address.md`
4. `references/genre-playbook-project-application.md`
5. `references/genre-playbook-institution-rules.md`
6. `references/genre-playbook-report.md`
7. `references/genre-routing.md`

当前未处理项只有需全局映射决策的讲话页主持/述职混杂、增项申请页角色，以及根任务范围内的 `reference-index.md` 映射和 fallback 收束。
