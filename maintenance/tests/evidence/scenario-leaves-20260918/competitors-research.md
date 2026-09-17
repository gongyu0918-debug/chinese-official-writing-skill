## 结论速览

这轮研究有一个先要说明的发现：**没有找到独立第三方专门覆盖"经费预算 + 信息化建设 + 采购 + 整改"四类写作规则的专项 Skill**。最接近的 `gongyu0918-debug/chinese-official-writing-skill` 与本工作区 `current-rules/` 属于同一规则谱系——我用文件级比对核过，工作区 4 个文件与该仓库 HEAD 版本逐字一致（仅换行差异）。其余可核查对象要么只覆盖相邻品类（投标侧、文件脱敏、行业信息化方案），要么许可证不可用、内容不可核查。下面的重合与差异按这个事实写。

另外要如实说明：本轮只做了规则文本与官方材料的核查，**没有跑任何写稿测试，不能声称已提高写稿质量**。

## 来源表

| # | 对象与链接 | 发布主体 | 正文日期 | 许可证 | 实际已读文件 | 解决什么写作问题 |
|---|---|---|---|---|---|---|
| 1 | [gongyu0918-debug/chinese-official-writing-skill](https://github.com/gongyu0918-debug/chinese-official-writing-skill) | GitHub 作者 `gongyu0918-debug`（README 自述 v2.0.4） | 采购专项核对/技术需求/可研：2026-09-13（db1761fa）；整改方案：2026-09-04（028a1174）；整改报告页：2026-09-12（82ade47a） | MIT（可见，LICENSE 在库根） | README.md；SKILL.md；`references/`：writing-rules.md、genre-playbook-procurement-review.md、genre-playbook-remediation-plan.md、genre-playbook-technical-requirements.md、genre-playbook-feasibility.md、genre-playbook-plan-construction.md、genre-playbook-procurement-announcement.md、genre-playbook-project-application.md、transaction-remediation-report.md、genre-routing.md | 中文公文/工作材料按文种选路起草与复核；采购、整改、技术需求、可研、建设方案各有专页处理要素、结构、事实状态与缺口 |
| 2 | [SunFangFei/gov-project-file-redaction](https://github.com/SunFangFei/gov-project-file-redaction) | GitHub 作者 `SunFangFei` | SKILL.md 2026-09-17（fe42d43）；redaction-policy.md 2026-09-17（60442c4） | 无（API `license=none`，未见 LICENSE 文件） | SKILL.md；references/redaction-policy.md | 政府信息化建设方案、可研、技术建议书、投资估算表及附件的本地脱敏，含金额策略与"数量×单价=合价、分项合计=总计"一致性验收 |
| 3 | [wangsanxing3210/medinfo-solution-expert](https://github.com/wangsanxing3210/medinfo-solution-expert) | GitHub 作者 `wangsanxing3210` | investment-estimation.md 2026-08-05（6b47f17，v1.6.6） | MIT（可见） | SKILL.md（关键词定位全文段落）；references/investment-estimation.md（全文）；references/bidding.md（关键词段落） | 医疗信息化解决方案编撰/审核，含投资量级区间库、构成占比、审核报告（问题清单+整改建议+优先级）、招投标应答矩阵 |
| 4 | [Get00/BiaoShu-SKILL](https://github.com/Get00/BiaoShu-SKILL) | GitHub 作者 `Get00` | BiaoShu-writer-pro/SKILL.md 2026-05-22（bf2b005） | Apache-2.0（可见） | README.md；BiaoShu-writer-pro/SKILL.md（内容规则与章节结构段落）；templates 目录清单 | 投标文件按评分标准生成；规定"禁止金额/预算描述，除非招标文件明确要求"、字数公式与章节骨架 |
| 5 | [jytpeterjiang/gov-bid-writer](https://github.com/jytpeterjiang/gov-bid-writer) | GitHub 作者 `jytpeterjiang` | references/procurement_analysis.md 2026-07-15（64bdf3c，init） | 无（API `license=none`） | SKILL.md（关键词段落）；references/procurement_analysis.md（全文） | 政府采购文件解读：预算金额=报价上限、资格要求、评分权重、需求逐条响应与关键词识别 |

补充核查（不作为规则证据）：[larashero3-dotcom/lieflat-gongwen](https://github.com/larashero3-dotcom/lieflat-gongwen) 许可证为 PolyForm Noncommercial 1.0.0（非商业），只看了 LICENSE 前几行与 README 片段，其整改类方案示例未作为依据使用；[munchengracedriver/awesome-requirements-writer](https://github.com/munchengracedriver/awesome-requirements-writer) 虽有"需求写作"定位，但仓库树 0 条目、README 为空，**列为不可核查**。

真实官方材料（用于 A/B 题材，非规则来源）：

- [湖南大学ZK-2026068货物及服务采购项目公开招标公告](http://www.ccgp.gov.cn/cggg/zygg/gkzb/202609/t20260917_27350152.htm)，中国政府采购网（财政部指定发布媒体），2026-09-17。
- [四川大学卓越创新群体计算集群二期更正公告](http://www.ccgp.gov.cn/cggg/zygg/gzgg/202609/t20260917_27350145.htm)，同上，2026-09-17。
- [国务院关于2024年度中央预算执行和其他财政收支审计查出问题整改情况的报告](https://www.audit.gov.cn/n5/n26/c10758168/content.html)，审计署网站，正文日期 2025-12-22（十四届全国人大常委会第十九次会议），正文为 22 页 PDF，我已用 PyMuPDF 抽取并核对关键段落。

## 跨样本稳定规律

**金额口径先于金额数字。** 五份样本里没有一份允许凭主题补金额。gongyu 的可研页要求投资估算、资金来源、建设周期分别标明"实际、测算、估算或假设"口径，材料缺失时"标为实质缺项或待核，不用地方模板补数字"；增项申请页更直接："不必为稿件完整造一个总预算"，且没给计算依据就不合计。medinfo 把这条做成反向硬约束：投资只给"量级区间 + 构成拆分"，并在反模式表里把"投资估算写精确数"列为 AP-05，把"编造厂商报价、合同金额"列为 AP-02。

**同一份稿子内部金额必须自洽。** redaction 的验收底线写明金额处理后"正文、总表、分表、数量、单价、合价、核增减额与总投资之间仍一致；无法重算时必须标为待人工复核"，并禁止"逐格随机修改"。gongyu 共性页对应的是"跨段、多主体及正文、表格、附件核对主体、名称、数值、顺序、期限、结论、状态与指向，分清实测、测算和估算"。

**采购文种里预算不等于结果。** gongyu 采购公告页要求"预算或上限、估算价与中标或成交金额不互换"，只提示影响当前发布目的的缺项；govbid 从投标侧给出同一事实的另一面——"预算金额：这是报价的上限，超过预算会废标"。

**需求类写作靠逐条可核对，而不是靠形容词。** govbid 的需求逐条分析法用"需求类型（必须满足/加分项）→ 对应章节 → 响应策略 → 证明材料"四栏，并要求区分"必须满足"和"建议满足"；medinfo 的应答矩阵是"招标要求→方案响应→无偏离/正偏离/负偏离→证据章节"；biaoshu 把"严格按评分标准编写"写成内容规则第一条。三者都不允许用泛化表述代替响应点。

**整改的状态分层必须保留，措施不等于完成。** gongyu 整改方案页要求问题概述先写"材料明示的已完成、正在整改、尚未启动或等待复核"，并明确"形成方案不等于完成整改，预期效果不写成已有成效"、"建立台账、召开会议、印发文件或开展培训本身不自动等于整改完成"。medinfo 的对应做法是审核只出"问题清单 + 高/中/低优先级 + 整改建议 + 重检触发方式，不判'废'"。

**缺口要么问、要么标，不静默补齐。** medinfo 的规则是信息不全先问关键字段，"不会瞎猜"，两轮仍模糊就输出带【假设】标注的版本；gongyu 是"信息未给与业务未定"分开，缺项进文后提示。

## 与当前规则的差异

`current-rules/` 只有 4 个文件，与上游同名文件逐字相同，属于同一谱系的**子集**。上游与同类对象里已覆盖、而当前 4 页没有的规则，主要在这些位置：

- 可研的资金与结论条件：`genre-playbook-feasibility.md` 要求投资、资金、周期、效益、风险分口径，结论按证据强度写"具备条件/有待补充论证/尚不能判断"，不把建议写成已批项目。
- 建设方案的预算取舍：`genre-playbook-plan-construction.md` 把"人员、设备、保障、预算和验收"列为按材料取舍项，并明确"行业通用做法可以用于分析建议，与已经确定的实施事项分开表达"。
- 采购公告的发布目的分流：`genre-playbook-procurement-announcement.md` 区分征集响应、结果告知、终止事项三类要素，结果或终止公告不套征集要素。
- 申请类经费写法：`genre-playbook-project-application.md` 的"费用按材料的单位和阶段写"整节（月费仍写月费、可选档位仍是可选、不设金额区间、不补"按实际用量结算"等财务规则）。
- 共性页的数值核对与口径区分：`writing-rules.md` 的"可核算合计差额"、"分清实测、测算和估算"。
- 外部独有：medinfo 的量级区间与构成占比库及 AP-02/AP-05 反模式；redaction 的金额四策略（保留/统一比例缩放/区间化/完全移除）与组合识别风险；biaoshu 的"招标文件未明确要求就不写金额/预算"；govbid 的"预算=报价上限，超预算废标"。

## 可借鉴而不宜通用化的条款

medinfo 的分场景投资量级（互联互通四级甲等 800–2000 万、电子病历 5 级 1000–3000 万等）和构成占比（软件许可 35–50%、硬件 15–25% 等）是行业经验值，可以借"给量级、给构成、注明以立项批复为准"的形式，**数值本身不能进用户稿件**——这与"不得凭空补齐金额"直接冲突。

biaoshu 的字数公式（目标字数 = 评分分值 ×（总页数 ÷ 总分）× 780）、"每小节 ≥ 3 个独立段落"、"每章节配表格"是投标排版经验，只适用于投标响应件，通用写稿借过去会把"按材料取舍结构"挤掉。

govbid 的价格策略（如"报价接近预算但略低于竞争者"）是投标方战术，站在响应人立场；采购方文种与整改文种都不能采用，借的应是"预算即报价上限"这层事实关系。

biaoshu 的"禁止金额/预算描述"仅适用于投标文本；在采购公告、采购需求、可研、投资估算场景中恰恰相反，预算与最高限价是核心要素。

redaction 的金额缩放系数、占位符替换、禁止残留词表都属脱敏流程，通用写稿只宜借"金额一致性核对"这一条思路，不能对用户材料里的真实金额做任何缩放或改写。

gongyu 上游 40 多个文种页加脚本的机制可以借（按用途选页、脚本只做字数与风险定位），但页数与覆盖面不必整体搬运。

## A/B 题材（从真实材料提炼）

**A 题：采购与预算口径。** 材料取自已核到原文的两则中央公告：湖南大学 ZK-2026068 公开招标公告（预算金额与最高限价均为 140.000000 万元、包号 1、数量 1 套、合同履行期限"详见招标文件第五章 采购需求"、开标时间 2026-10-09）与四川大学计算集群二期更正公告（品目为信息化设备下的服务器、交换设备、机柜，更正事项是需求文件"技术要求 服务器 参数要求"中平台兼容范围的修改，附件含需求.pdf）。任务设为：按这两则材料的字段写采购公告的征集响应段，或据技术参数与数量写技术需求附件。看点在于预算与限价同值、数量与包次绑定、"详见采购需求"这类指向性表述不得改写成具体期限。

**B 题：整改状态与金额。** 材料取自审计署公开的 2025-12-22 整改情况报告正文（22 页 PDF）。已核到的状态字段：要求立行立改的 2186 个问题中 98% 已完成整改，要求分阶段整改的 1299 个、持续整改的 753 个"制定了时间表和路线图"，共整改问题金额 1.04 万亿元，制定完善制度 1090 多项，处理处分 3420 多人；要求立行立改的问题还有 62 个（占 2%）尚未整改到位，报告结尾写"有关地方、部门和单位已作出后续安排"。任务设为：据这批字段写整改进展报告或整改方案的问题概述段。看点在于三类整改状态与"已整改问题涉及资金 3446.41 亿元"这类口径必须原样分层，不能把 98% 写成全部完成，也不能把后续安排写成已闭环。

两题的来源分别是 ccgp.gov.cn 与 audit.gov.cn 的公开页面；**可匿名化字段**：采购单位、代理机构与联系人电话、项目编号与项目名称、开标与更正日期、平台域名、具体金额（可换为量级）、涉及的地方与部门名称、具体资金/人数/制度数。真实材料的字段只作测试输入，不得把其中的事实补进用户稿件。

## 可提炼规则草案（简洁正向、按用途取舍）

金额按材料原口径保留，并标明是预算、最高限价、报价、成交、测算还是估算。只写材料给出的费用项；没有计算依据时不合计、不设周期、不设区间。采购文种保持预算/上限与结果金额各自独立。需求类写到可逐条响应、可核对的粒度，区分必须满足与建议满足。整改文种分层保留已完成、正在整改、尚未完成与后续安排，措施不写成完成。未给字段按缺口处理并说明缺口，不补财务规则与程序结论。这些规则是否有效，仍需后续真实写稿测试验证。

## 局限与失败记录

采购站内搜索页返回 JS 骨架（2919 字节）无法检索；DuckDuckGo HTML 端点返回 202 阻断页；Bing 返回 109 KB 但无可用结果链接；mojeek 返回 5575 字节无结果；`munchengracedriver/awesome-requirements-writer` 仓库为空；对 lieflat 某中文路径示例文件的 commit 查询失败（jq 解析错误）。许可证不可见或非商业的对象（redaction、govbid、lieflat）只提炼一般思路，未复制原文。审计整改报告仅用 PyMuPDF 抽取了关键段落与结构，未逐页全文引用。中间下载物保存在 [research-scratch](C:/Users/admin/AppData/Local/Temp/cow-scenario-research-_jbkw_fw/workspace/research-scratch) 下，可作为复核起点。