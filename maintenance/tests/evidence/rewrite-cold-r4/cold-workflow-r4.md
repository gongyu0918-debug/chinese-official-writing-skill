# 共性工作流与普通脚本冷审 R4

## 实际读取清单与边界

冻结源：`output/speech-host-duty-native-r1/snapshots/candidate`，已确认存在，未回退 canonical。未读取已有冷审结论、A/B 胜负、历史映射或候选身份解释。未启用 Hook，未修改产品/测试，未写 main、合并或推送。只读审查与临时 CLI 输入不触发安装同步。

适用工作约束读取：父仓库 `AGENTS.md`、当前独立 worktree `AGENTS.md`、当前 `maintenance/docs/development-workflow.md`；只用于授权、只读范围和验证方式，不作为产品写作规则。报告放在默认忽略的 output，由主代理管理，不独立提交共享工作树的其他改动。

全文读过（按实际范围列出）：

- `SKILL.md`
- `README.md`
- `references/task-route-cards.md`
- `references/reference-index.md`
- `references/final-review-layers.md`
- `references/delivery.md`
- `references/information-selection.md`
- `references/handling-elements.md`
- `references/argument-chains.md`
- `references/official-style.md`
- `references/formal-addressing.md`
- `references/anti-ai-patterns.md`
- `references/proofreading-checklist.md`
- `references/review-checklist.md`
- `references/prose-lint-usage.md`
- `references/compression-details.md`
- `references/short-draft-naturalness.md`
- `references/structure-editing.md`
- `references/field-editing.md`
- `references/external-research.md`
- `references/format-gbt9704.md`
- `references/formulaic-language.md`
- `references/technical-terms.md`
- `references/genre-checklist.md`
- `references/genre-checklist-request.md`
- `references/genre-checklist-report.md`
- `references/genre-checklist-feasibility-review.md`
- `references/genre-routing.md`
- `references/compatibility-scene-routing.md`
- `references/speech-person-order.md`
- `references/ai-compute-docs.md`
- `references/ai-compute-examples.md`
- `scripts/draft_length.py`

定向读过：

- `scripts/prose_lint.py`：函数/参数/退出码导航；1—180（部分工具展示截断，未见片段不据此下结论）、355—610、898—950、1436—1552。重点是输入读取、正文/提示分区、建议词条、CLI 和失败语义；没有逐行审完全部 1552 行。
- 六个主叶的读页/专项复核/退出路径：`genre-playbook-report.md`、`genre-playbook-request.md`、`genre-playbook-feasibility.md`、`genre-playbook-speech-address.md`、`genre-playbook-meeting-host.md`、`genre-playbook-duty-report.md`。
- 对全部 `references/*.md` 和入口做维护/构建/Hook/测试语汇检索；命中仅作为定位线索。没有把业务中的维护、发布、验收当成开发指令。

冻结源文件清单指纹（按相对路径排序，将每行 `path<TAB>sha256` 以 LF 连接后再 SHA-256）：`bd9560544ba4b1b52a1b02786eb65f2d04f0322bf34ddf83fad55b6eacc3b4ad`。核心文件哈希见末尾。

## 结论

确认 2 项 P2 问题：DOCX 篇幅统计包含正文外部件；通用复核脚本向非技术稿件给出技术能力补写建议。另有 1 项可选 P3 重复整理。未确认维护指令泄露、不可达主叶、无条件执行回环、死锁或必经检查绕过。此结论是冻结规则与有限真实 CLI 的冷审，不代表真实写稿全量通过。

### R4-01 / P2：DOCX 正文计数把页眉、页脚和批注计入

- 位置：`references/compression-details.md:7-15`、`scripts/draft_length.py:11,23-25,55-60`；共享读取实现 `scripts/prose_lint.py:364-389,399-406`。入口 `SKILL.md:83` 要求有篇幅约束就实测。
- 自然触发：用户提供带页眉、页码和审阅批注的 Word，“请将报告正文压到 800 字以内，保留原样式和批注”。实际路径为报告主叶 → 压缩 → 编号第一步 → 按 usage 直接将 DOCX 传给 draft_length。用户指定的是正文，页眉/页码/批注不是其篇幅。
- 复现：正文 `工作已完成。` 为 6 个非空白字符。只加页眉 `办公室` 得 9；只加页脚 `第1页` 得 9；只加批注 `按你的要求，此处只改标点。` 得 19。上限 10 时批注样本报告 `above, above_by=9`；页眉和批注合并样本得 22、超 12。所有样本进程退出 0，符合脚本的报告型退出语义，问题在 count。
- 后果：正文未超限也会被要求继续压缩；若设下限，批注等还可能掩盖正文不足。这不是只有标题/落款计不计的约定差异：批注与页码不属于拟交付正文字符。usage 的“排除标题、落款或附件时单独传正文”没有揭示 DOCX 默认还会吸收批注和页眉页脚。
- 最小改法：为 draft_length 明确正文提取范围，DOCX 默认只取正文部件或先抽取用户指定正文；同时说明脚注/尾注是否按需求计入。不要简单修改共享 read_docx 使所有调用一律忽略页眉/批注，因为 prose_lint 的格式/残留检查可以有不同范围。
- 置信度：高；实际 CLI 可复现。完整 Word 渲染不是本次验证对象。

### R4-02 / P2：非技术文稿也收到补技术能力的操作建议

- 位置：`scripts/prose_lint.py:102-105`，尤其 103；这些词条通过 `prepare_pattern_sets:925-929` 无场景筛选进入普通扫描。对照 `SKILL.md:49`、`references/anti-ai-patterns.md:13,54`、`references/prose-lint-usage.md:25-27`。
- 自然触发：用户提供企业交流活动新闻稿，要求润色并保留材料事实；原稿含“这次活动为企业交流搭建了强大平台。”任务没有算力、服务器或模型服务信号，正确路径是新闻主叶 → 通用抗 AI 味复核 → 普通脚本。
- 真实输出：`--delivery-mode draft-body --structure --format --json -` 对上述单句返回 `ai-compute-vague`，建议为“补充调度、监控、隔离、计量、运维等具体平台能力。”退出 0。
- 后果：空泛语言风险本身可以成立，但具体改法跨越了活动新闻的语义领域，要求新增技术能力。即使真正算力稿件缺少这些材料，“应补充 GPU/服务器/Token/并发/SLA 等可验收指标”也与抗 AI 味页“回到材料事实，不补型号/数量/条款或成本结论”的方向不一致。usage 要求模型结合材料判断，因此不能据此声称必然新增事实；确认的是最后一道工具建议与写稿语义冲突。
- 最小改法：将词条建议改为先核对语境和已给材料，通常收回空泛评价或换成材料已有的具体动作；有相应技术语境且材料已有依据时再使用已有能力或指标。无需为此新增强制场景读页，也不应将所有“平台”都路由到 AI 场景。
- 置信度：高（建议错域实测）；错误正文出现率未测。

### R4-03 / P3 可选整理：入口自身重复陈述状态保真

- 位置：`SKILL.md:63` 与 `67`；两条都要求“拟、建议、评估、下一步设想”等维持原级别。
- 触发：每次加载入口都读到两段同义规则；第 67 行没有建立新的任务条件或状态层级。
- 后果：增加主入口规则正文体积与维护点，未证明造成误写、读页循环或检查绕过。
- 最小改法：第 67 行独有的“考察、拟测试、考虑尝试”等例子并入第 63 行或信息选择页，保留一个权威表述。按需链接及文种专有状态规则不要据此全删。
- 置信度：高（重复）；收益有限，不作为阻断项。

## 已核对但不升级为缺陷

1. DOCX 的 prose_lint 范围与计数分开判断。页眉 `办公室` 和页脚 `第1页` 样本均无风险；保留批注被标 `thought-leak`，但扫描元信息本身可以帮助清除真正的成品残留。当前输出只保留拼接行号、不显示 `word/comments.xml`，存在误认正文的解释限制；`format-gbt9704.md:10,104` 要求保留批注，usage 又要求结合修改范围人工处理，故不主张为 lint 一律排除页眉页脚或批注。若改进，优先在输出中标明部件来源，再按任务判断。
2. 入口有五步顺序；短稿与局部修改页明确回到编号检查，compatibility 场景也继承首页。事实/文种、抗 AI 味、普通脚本、交付没有被短路径取消。
3. review-checklist 的“审查并改稿”末尾回到检查步骤是对已改稿的必要复核；最终复核页不再跳回“审查并改稿”入口，未构成无条件循环。脚本 usage 允许经核实保留的提示直接完成判断，不要求直到零警告，未见零警告死锁。
4. `reference-index.md` 给唯一主叶，共性页按条件叠加；图/页中的返回链接不能自动当作重新选路和重读。已读未变规则可直接应用（task-route-cards:10）；未证明必须重复加载同页。
5. 新闻、主持、述职、讲话及 AI 附加页的入口信号与主叶职责可区分。AI 场景页只按需再读术语或示例，不要求全读；speech-person-order 只处理多人排序，未替代主持或讲话主叶。
6. `SKILL.md` 和写作 references 检索未见 git、commit、worktree、pytest、构建门或 Hook 执行动作混入正文规则。README 的维护和 Pro 说明属于允许的产品能力说明。脚本中的“删除门禁状态”检测词是清除稿件残留，不是要求启用门禁。
7. 有范围外问题时文后提示承接；只要正文时 delivery:24 明确省略提示。工具运行日志和规则自证留在内部，不要求在正文公布测试/构建结果。
8. 词表有“不是……而是……”等提示，但 anti-ai 要看上下文和成簇问题，usage 允许合理表达保留；因此没有把单个否定词或单条告警直接判作写作缺陷。
9. `draft_length` 非空白计数/CJK 计数、文后提示截断与 usage 一致；`prose_lint` 三种任务模式都存在，标准输入示例可运行。退出 0 不代表零告警，usage 要读取风险内容，目前没有要求以退出码宣称成稿通过。

## 实际验证与复现方式

运行环境为本机 Python，通过 `sys.executable -B` 调用冻结脚本；子进程环境设置 `PYTHONUTF8=1`、`PYTHONDONTWRITEBYTECODE=1`。没有加载 Hook，临时输入位于系统临时目录并由 TemporaryDirectory 清理。

实际命令族（S 是冻结源绝对目录）：

```text
python -B S/scripts/draft_length.py --help
python -B S/scripts/prose_lint.py --help
python -B S/scripts/draft_length.py --json --min-chars 7 --max-chars 7 -
python -B S/scripts/draft_length.py --json --count-mode cjk -
python -B S/scripts/prose_lint.py --delivery-mode draft-body --structure --format --json -
python -B S/scripts/prose_lint.py --delivery-mode gap-note-allowed --structure --format --json -
python -B S/scripts/prose_lint.py --delivery-mode review-only --structure --format --json -
python -B S/scripts/draft_length.py --json --max-chars 10 <temporary.docx>
python -B S/scripts/prose_lint.py --delivery-mode draft-body --structure --format --json <temporary.docx>
```

所有 CLI 调用退出 0，无 stderr。两份 help 参数与 usage 相符。标准输入：`工作已完成。` + 标准文后提示统计 6（min7 时 below1）；`工作已完成。ABC12` 的 cjk=5；纯正文、正文加文后提示均无 lint 风险；review-only 的 `原句：“作为 AI，我会按你的要求起草。”建议删除过程话。` 无告警，引用保护可用。

DOCX 小样本是为 reader 构造的最小 ZIP/XML，正文部分为：

```xml
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>工作已完成。</w:t></w:r></w:p></w:body></w:document>
```

其余部件分别保存 `word/header1.xml`、`word/footer1.xml`、`word/comments.xml`，以相同 w 命名空间的根元素包裹 `<w:p><w:r><w:t>测试文字</w:t></w:r></w:p>`。合并样本的页眉用 w:hdr、批注用 w:comments/w:comment。测试直接验证脚本读取行为，不宣称这些最小 ZIP 已作为完整 Office 文件打开或渲染。

| DOCX 组成 | 计数 | max10 状态 | lint |
| --- | ---: | --- | --- |
| 正文 6 | 6 | within | [] |
| 正文 + 页眉“办公室” | 9 | within | [] |
| 正文 + 页脚“第1页” | 9 | within | [] |
| 正文 + 批注“按你的要求，此处只改标点。” | 19 | above9 | thought-leak，line3，match=按你的要求 |
| 正文 + 页眉 + 同批注 | 22 | above12 | thought-leak，line4，match=按你的要求 |

## 未覆盖

- 未逐字审查其余所有文种主叶，不替代其他审查者对文种骨架和主体归属的冷审。
- 未运行真实模型起草/A-B 对照，未推断哪项问题为本轮独有回归，也未使用已有胜负证据。
- 未运行全量单元测试、构建、镜像同步、安装、联网、发布或 Word 渲染；本次是产品规则只读审查与 bounded CLI 小样本。
- 未穷尽全部 lint 正则与跨段算法；XML 注释之外的修订态、域代码、表格和多节特殊页眉解析未测。

## 关键冻结文件 SHA-256

- `SKILL.md`: `da45793d376905d6075853697660dd886fea4fd05a9956239c897ca273ffa182`
- `references/prose-lint-usage.md`: `efbb99dbb72599e5b9614b18ad901abc5284812aacd0bc9e92177f2139d70525`
- `references/compression-details.md`: `e46ae4b3c68f962eae9aa7dc5520d2fcd6e6f1725fa89b281fa8e15fa72e9d1d`
- `references/anti-ai-patterns.md`: `b075d7394091fc5b54f07d70bfbf68dce0048f0b74aa59cff8578ad3f4bf48eb`
- `scripts/draft_length.py`: `5b126b391dd65db4c395e0d5883c84403094c3447191bbf7803579226e6384ca`
- `scripts/prose_lint.py`: `8931a7a82a1563e5838a137f9496dc92dc7c48451b0fbf443d32afc27dc8e7c7`
