# R5 共性规则与普通脚本独立冷审

审计对象：`F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/reference-rewrite-20260912/output/combined-candidate-r5/skill`。

本报告先于任何修复保存，行号均来自这份冻结候选。只读候选内容、定向跟读其中的引用目标；没有读取其他审计、胜负、匿名映射或历史结果，没有修改候选，没有运行模型写稿。下述内存探针只检验脚本输入、读取和扫描行为，不属于真实写稿评测。

结论：发现 **4 项中风险问题、1 项低风险规则残留**。其中 2 项 DOCX 缺陷已经由只读内存探针复现，另外 2 项中风险为可直接定位的规则触发范围冲突。未发现必须反复重启路由的循环、必经页目标缺失或维护/构建/发布/测试命令混入写稿入口。不能据此声称模型能稳定执行全部流程。

## 发现

### F01｜中风险｜抗 AI 味必经页扩大了算力附加页的触发范围

- 位置：`references/anti-ai-patterns.md:54`；对照 `SKILL.md:49`、`references/reference-index.md:65`、`references/ai-compute-docs.md:7-10,22-28`。
- 自然触发：用户要求起草普通服务器租赁申请，或审核普通服务器、接口、安全与 SLA 技术材料，没有 AI 算力、模型训练/推理或模型服务资源内容。首页正确保留原主文种；成稿或审核仍必须按 `SKILL.md:91` 读取抗 AI 味页。
- 指令证据：首页明确说普通服务器、接口、安全、SLA 或验收内容单独出现时沿用主文种；抗 AI 味页却把“算力、GPU/服务器租赁、模型服务和 AI 平台材料”并列，并令“专项需求、指标、SLA、安全和验收读 `ai-compute-docs.md`”。普通服务器租赁因此有第二次进入算力页的文字入口。
- 影响：附加页包含 Token、模型推理/训练、模型服务和资源测算检查，可能增加与当前稿件无关的读页及检查项。这里确认的是触发范围不一致，没有把可能的无关加载声称为已经发生的模型行为，也不把有依据的合理推断判为事实回退。
- 最小修正：抗 AI 味页只负责语言核对；若需要引用算力页，直接复用首页“明确涉及 AI 算力、模型推理/训练、智算中心或模型服务资源”的条件，或写成“已按首页选入 AI 算力场景时”。不以一般 GPU/服务器租赁、SLA 和验收重新触发。

### F02｜中风险，已复现｜DOCX 只枚举前三个页眉页脚，漏扫多节文档的后续部件

- 位置：`scripts/prose_lint.py:364-405`，核心固定名单在 `371-381`；默认入口 `read_text` 为 `408-422`，普通 lint 调用在 `1494-1496`。
- 自然触发：用户交付含多个节的 Word 材料，待清理的模型身份或过程残留位于 `word/header4.xml`、`word/footer4.xml` 或后续页眉页脚。
- 代码证据：`scope="all"` 的 `xml_names` 明确只列 `header1.xml` 至 `header3.xml`、`footer1.xml` 至 `footer3.xml`；遍历只处理这些名单项，没有枚举其他页眉页脚。
- 只读内存探针：同样的主文档与同样的“作为AI，我的思路是”文本，放在 `header1.xml` 时 `leak_in_read=True` 且扫描得到两条 `thought-leak`；仅改为 `header4.xml` 时 `leak_in_read=False`、发现列表为空。
- 影响：后续页眉页脚完全没有进入被检查文本，违反“全部检查部件”的函数说明和最终文本兜底用途。人工复核可能发现它，但脚本本身不能声称已经覆盖。
- 最小修正：普通 lint 从 ZIP 部件名动态枚举所有实际页眉页脚，保留主文档、脚注、尾注及批注原有扫描顺序/行为。`main-document` 篇幅读取继续仅使用主文档，不把页眉页脚加入字数。增加含第四个页眉/页脚的读取及扫描回归。

### F03｜中风险，已复现｜普通 lint 对缺主文档的无效 DOCX 返回成功

- 位置：`scripts/prose_lint.py:385-391`，错误输出与退出逻辑在 `1494-1500,1524-1527,1538-1547`；对照 `scripts/draft_length.py:55-59`。
- 自然触发：用户传入损坏、打包遗漏或误改后缀的 DOCX；它仍是可打开的 ZIP，但不含 `word/document.xml`。
- 代码证据：只有 `scope == "main-document"` 才检查主文档是否存在。默认 `all` 模式跳过不存在的名单项，返回空字符串；其后没有读取错误且没有发现，普通命令可打印 `No prose risks found.` 并返回 0。
- 只读内存探针：仅含 `[Content_Types].xml` 的 ZIP，普通 `scan_input_files` 返回 `findings=0`、`read_error=False`，`determine_exit_code` 返回 `0`；同一包按 `main-document` 读取则抛出 `InputReadError`。
- 影响：同一不可用输入在字数脚本中被拒绝，在语言脚本中却被认作检查成功，容易把“未取得正文”误报为“没有风险”。
- 最小修正：两种 DOCX 范围都先要求 `word/document.xml` 存在；保持既有 `InputReadError`、stderr 和退出码 2 路线，勿把正常空正文和缺失部件混为一类。增加缺主文档的普通 lint 读取/退出回归。

### F04｜中风险｜普通 Word 整理也被强制加入正式发文全要素缺项卡

- 位置：`references/format-gbt9704.md:20-22`；对照同页 `3,8,14,16,29-30,104-107`、`references/information-selection.md:10,19-20`、`references/delivery.md:15,20`。
- 自然触发：用户提供已经定稿的内部工作总结、讲话或企业材料，只要求整理成普通 Word，并未要求国标发文、红头或机关正式签发。
- 指令证据：第 20 行把“Word、docx”与红头、签发等并列，触发正式交付核对卡；第 22 行又规定“至少核对”发文字号、签发人、密级、紧急程度、版记、印章等，未提供即标“待确认”。同页虽然要求尊重内部/企业模板，却没有在核对卡处按文种和模板排除不适用项。
- 影响：普通文件转换会平白生成一组不影响该稿使用的待确认事项，与只列实质缺项和“无关项目从提示移除”的交付规则发生冲突。可能打断排版交付，或制造需要用户补文号/印章的错误预期；没有观察到模型实际被阻断，故不报告为已发生死锁。
- 最小修正：按当前文种、用户模板与是否要求正式机关发文确定核对项；普通 Word 仅核对正文、标题、段落、表格、落款等实际适用项。将文号、签发、密级、版记和印章等限制在用户要求或模板适用时，不适用项不列为缺项。

### F05｜低风险规则残留｜报告细查页仍把情况说明统一引回报告主叶

- 位置：`references/genre-checklist-report.md:3,6,11`；对照 `references/genre-routing.md:67`、`references/genre-playbook-explanation.md:3,9,11`、`references/review-checklist.md:5,24-30`。
- 自然触发及前提：用户要求复核并修改“关于数字差异原因的情况说明”；若本轮因情况说明复核读取报告细查页，该页宣称自己覆盖“情况说明”，并要求起草、改写、压缩先读报告主叶，末尾也把用户要求改写导回报告主叶。
- 指令证据：主路由已经按实际用途把解释事实/原因、回应疑问的说明转到独立说明页；说明页明确“不自动变成报告”。旧细查页的覆盖声明和回程目标没有同步。
- 影响与限定：加载该页后存在错误换用报告功能的指令；但首页通常应先选择说明主叶，现有文字并不证明普通说明任务必然加载报告细查页，因此不升为主路由必现中风险。
- 最小修正：报告细查只承接以报告功能成文的情况说明；解释用途沿已选说明主叶处理。第 11 行保留只审交付意见、审后改稿交全文的区别，改后回到当前主文种及编号检查步骤，不统一换成报告。

## 工作流与脚本检查结论

1. **必经检查与出口**：`SKILL.md:79-99` 给出篇幅、事实文种、抗 AI 味、脚本和交付的顺序；篇幅不足且材料已穷尽时，`compression-details.md:21-23` 允许真实短稿并记录差额。`prose-lint-usage.md:25-27` 要求变动内容复扫、影响篇幅时复测，合理提示经判断后可以保留。没有把“所有命中必须清零”设为无限出口条件。
2. **复核与审后改稿**：`review-checklist.md:5,24-32` 明确区分审稿意见、改好全文和两者同时交付。其第 30 行返回首页编号检查，是检查改后稿，不是重新选择文种。`final-review-layers.md` 的三项是该次事实文种检查的内部层次；与首页五步有分工，没有发现必须相互重启的闭环。
3. **最终文本与默认提示**：脚本使用页区分被审原稿、改好稿、审稿意见及正文加提示；第 27 行要求最终发送使用已检查文本，临时开场和说明也纳入。交付页第 9、22、24 行分别约束文件外提示、篇幅分区和“只要正文”例外。默认提示的存在不是正文污染，不能把用户已经允许的提示当违规残留。
4. **局部修改**：首页第 79 行、事实文种页第 15 行、任务卡第 6、12 行共同限定改动与关联段落；不需要为一次标点修改重写全篇。抗 AI 味页第 3、7、13 行和使用页第 25 行保留上下文判断，未把单个否定词、正式词或固定句式当硬错误。
5. **推断边界**：`information-selection.md:8,21,25-29` 与 `review-checklist.md:18-22` 保留材料和常识支持的合理分析，区别已经发生、已定流程及具体责任承诺。本次不把合理推断能力本身列为风险；也没有仅凭句尾否定或词语偏生硬增加中风险条目。
6. **脚本提示**：常见强平台/成本/未来需求等提示指回材料或删除无据评价，未要求凭空补 GPU 数量、期限、合同与责任；结构类建议仍是复核提示，不等于必须添事实。低级提示如项目卡片、重复术语和三段式，仍须服从已有字段、引用与本轮范围。没有据代码证明存在强制新增无关事实的硬路径。
7. **脚本退出**：正常风险提示默认退出 0，是提示型工具设计；`--strict`、`--fail-on` 才改变风险退出码，不能把默认 0 当内容全部合格。缺文件、权限和常见 XML/ZIP 错误有 `InputReadError` 路线。F03 是缺主文档例外。损坏 XML、平台编码、极大文件等未全部动态覆盖。
8. **维护命令与页间引用**：入口及共性页无 Git、构建、发布、单测或审计执行命令回流。`draft_length.py`、`prose_lint.py` 的普通用户调用示例属于功能使用说明，不能误判为维护泄露。只读路径检查显示本次范围内所有反引号引用的 `.md/.py` 目标均存在。README 的能力说明包含 Pro/Hook 边界介绍，没有把 Hook 作为普通写稿必经执行路径。

## 逐页覆盖

下表每页均完整读取；“无新增发现”只表示本次静态冷审未形成可报告问题，不表示已证明模型稳定执行。

| 文件 | 已核对内容与结论 |
| --- | --- |
| `SKILL.md` | 完整入口、任务加读、事实边界、五步检查、交付；F01 的对照基线 |
| `references/ai-compute-docs.md` | 附加页职责、数据性质、成本、SLA、安全、验收、二级资料；自身需按主文种与材料触发 |
| `references/ai-compute-examples.md` | 四组完整示例与首段材料授权限制；无新增发现 |
| `references/anti-ai-patterns.md` | 语义、旁白、结构、节奏、英文、格式和附加路由；F01 |
| `references/argument-chains.md` | 单判断、多判断、依据不足出口；无新增发现 |
| `references/compatibility-scene-routing.md` | 五类场景、建议信、单页读取及检查回程；无新增发现 |
| `references/compression-details.md` | 调用参数、计数范围、上下限、材料不足与复测；无新增发现 |
| `references/delivery.md` | 完整稿/意见、消息/文件边界、默认提示、纯正文例外；F04 对照 |
| `references/external-research.md` | 两类触发、来源用途、一次定向补搜、停止与字段缺口；无新增发现 |
| `references/field-editing.md` | 字段分隔、留空、顺序、禁擅自表格化/散文化；无新增发现 |
| `references/final-review-layers.md` | 事实状态、文种结构、模板完整性、范围外问题；无新增发现 |
| `references/formal-addressing.md` | 称谓、上/下/平行、人员与尾语；无新增发现 |
| `references/format-gbt9704.md` | Word 交付、全部核对卡、字体页面、标题、主送、版头、附件、落款、版记、编号、DOCX保留；F04 |
| `references/formulaic-language.md` | 固定用语、历史模板、尾语和人物排序触发；无新增发现 |
| `references/genre-checklist-feasibility-review.md` | 摘要审核范围、完整性条件、未决状态、估算；无新增发现 |
| `references/genre-checklist-report.md` | 适用范围、情况说明、只审与改写回程；F05 |
| `references/genre-checklist-request.md` | 请示/申请细查、资金/下游否定、模板与尾语；无新增发现 |
| `references/genre-checklist.md` | 未覆盖功能、已有首叶排除、转入和停止；无新增发现 |
| `references/genre-routing.md` | 完整判定树、功能表、混合材料、停止；F05 对照 |
| `references/handling-elements.md` | 实际必要要素、来源和缺项；无新增发现 |
| `references/information-selection.md` | 四类信息、进展推断、时间锚、唯一底稿和材料不足；F04 对照 |
| `references/official-style.md` | 视角、判断、语气、正式化及复核范围；无新增发现 |
| `references/proofreading-checklist.md` | 引用、数字、主体、格式、直接修改/位置报告；无新增发现 |
| `references/prose-lint-usage.md` | 三种文本模式、必需参数、原稿保留、复扫、最终文本、失败处理；无新增发现 |
| `references/reference-index.md` | 全部首叶和专项读取条件、停止；F01/F05 对照 |
| `references/review-checklist.md` | 问题确定、不过审、只审/审后改稿、独立复核输入；F05 对照 |
| `references/short-draft-naturalness.md` | 短稿适用、段落、尾语、事实和压缩；无新增发现 |
| `references/speech-person-order.md` | 模板优先、具体与泛称、跨单位、主客与主持区分；无新增发现 |
| `references/structure-editing.md` | 最新版、增删调序、粒度、点名标签、主体联动；无新增发现 |
| `references/task-route-cards.md` | 两类轻量任务、首叶保留、接回检查；无新增发现 |
| `references/technical-terms.md` | 四项术语及非词典边界；无新增发现 |
| `scripts/draft_length.py`（1–71 行） | 全部计数、参数合法性、读取、状态与退出；主文档范围保持明确 |
| `scripts/prose_lint.py`（1–1568 行） | 全部词表、格式/交付规则、DOCX读取、引号和围栏、提示分区、重复检测、逐行/聚合扫描、CLI/输出/退出；F02/F03 |
| `README.md` | 完整能力说明、使用场景、普通脚本、Hook/Pro、来源；未打开外部链接 |
| `agents/openai.yaml` | 展示信息、默认技能触发范围；无新增发现 |

定向跟读：完整读取 `references/genre-playbook-report.md`、`references/genre-playbook-explanation.md`，只核对 F05 的首叶功能与回程；其他主文种、两个 transaction 文件由另一独立审查负责，本报告不代其作结论。`LICENSE` 仅在目录清单中看到，本次未进行许可证审查。

## 检查命令与保留结果

在内存中使用 `python -B -` 导入冻结候选的两个脚本；`-B` 禁止生成 `__pycache__`。DOCX 探针用 `io.BytesIO` 创建最小 ZIP/XML，并临时替换 `zipfile.ZipFile` 的打开对象，不生成任何 DOCX 文件。调用原函数 `read_docx`、`scan`、`scan_input_files`、`determine_exit_code`、`measure_draft`。

```text
word/header1.xml leak_in_read= True labels= ['thought-leak', 'thought-leak']
word/header4.xml leak_in_read= False labels= []
missing-main lint: findings= 0 read_error= False exit= 0
missing-main count: InputReadError
review heading: []
postscript count: 3
AST_OK draft_length.py
AST_OK prose_lint.py
COMMON_REFERENCE_LINKS_MISSING []
```

附加两项小探针：审稿意见中的引用“本方案重点说明”在 `review-only` 下未被当成意见自身旁白；`正文。` 加空行和标准“文后提示”后，字数只计 3 个非空白字符。两脚本 `ast.parse` 通过。静态引用校验逐一检查首页和 30 个共性 reference 中的 `.md/.py` 反引号目标；没有缺失路径。维护词检索只命中业务运维或业务日期语境。

未验证：实际模型路由/写稿轨迹、贵模型多次一致性、真实 Word 渲染与样式保真、所有合法 DOCX 关系/节组合、损坏包的全部异常类型、跨平台 Python/编码、超大文档性能、完整回归集及其他主文种/transaction 内容。F01/F04/F05 的运行影响需要定向任务轨迹确认；上述探针不能替代这些验证。
