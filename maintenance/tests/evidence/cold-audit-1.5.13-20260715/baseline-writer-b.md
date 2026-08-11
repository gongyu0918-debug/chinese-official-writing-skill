# 固定基线说明

独立 writer B，只做只读真实链路测试，不读取 tests/evidence、外部冷审报告或其他 agent 输出。固定使用 `F:/Workspaces/chinese-official-writing-skill/output/release-baselines/github-1.5.13-cold-audit/chinese-official-writing/SKILL.md`；先完整读取该入口，再完全按入口自己的渐进规则决定是否读取 reference，不预先假定应读哪些文件。除非题面依照 Skill 触发联网，否则不得联网。

# T1-T12 任务原文

T1 未决纪要：主题是模型费用观察，时间7月15日10时，地点二号会议室，参会为技术部和财务部；只形成“先试用低思考档位两周，下次会议听取结果”的建议，未形成采购决定、责任分工和完成期限，写一份简短纪要。

T2 完整纪要：项目协调会已议定数据组7月20日前完成字段核验，应用组7月25日前完成联调，办公室7月28日前汇总问题；写完整正式纪要。

T3 普通非AI服务器租赁申请：档案室拟租用一台普通备份服务器12个月，预算24000元，只用于电子档案备份，明确不涉及AI、模型、GPU或推理；写内部申请。

T4 AI算力租赁请示：业务预计每月8000万Token，峰值并发40，拟租赁GPU推理服务12个月，预算60万元，要求写SLA、数据安全和验收；写请示。

T5 非AI车辆租赁可研：后勤拟租赁2辆通勤车一年，预算18万元，比较购买与租赁，材料没有AI或信息化内容；写300字以内可研摘要。

T6 只审不改：原通知写“各部门要马上搞起来，月底前把结果发过来，大家务必高度重视。”只检查格式、语气和办理要素，按位置、风险层级、修改建议输出，不重写全文。

T7 只输出正文：把一份申请顺成正式稿；已知申请事项是采购3台办公电脑、预算15000元、经费来源年度信息化预算；主送机关、申请单位、成文日期未提供。只输出改后正文，不作说明，不附待确认。

T8 文种自判：本单位拟向直属上级申请新增2个专业技术岗位编制，请求批准；写合适文种，标题由你判断，金额和日期均无需补。

T9 文种自判：本单位请同级数据中心协助提供接口文档，并于7月22日前反馈联系人；写合适文种。

T10 完整正式公告：图书馆因消防检修于7月18日闭馆一天，7月19日恢复开放，咨询电话010-12345678，发布单位市图书馆，成文日期2026年7月15日；要求完整正式格式。

T11 文种自判：某内部处室想用“命令”部署普通月度资产盘点，但发布主体没有发布命令的法定权限；请改用合适文种成稿，已知各部门7月31日前报盘点表至资产科，联系人李明，电话010-87654321。

T12 文种自判：现对拟推荐的3名年度先进个人进行公开监督，公示期7月16日至22日，异议书面反馈至人事处，电话010-66668888，发布单位某市教育局，日期2026年7月15日；选择公告/公示/通告中合适文种并成稿。

# 上一轮原样输出

T1

模型费用观察专题会议纪要

时间：7月15日10时
地点：二号会议室
参会单位：技术部、财务部

会议围绕模型费用观察事项进行了讨论，形成如下建议：先试用低思考档位两周，下次会议听取试用结果。会议未就采购事项、责任分工和完成期限形成决定。

ROUTE T1: SKILL.md#任务模式路由与交付模式、核心流程、硬边界；references/task-route-cards.md#未决事项会议纪要；references/genre-playbooks.md#会议纪要；references/genre-checklist.md#会议纪要；references/proofreading-checklist.md#语言和格式自检、稿内一致性；未联网

T2

项目协调会纪要

会议议定以下事项：

一、数据组于7月20日前完成字段核验。

二、应用组于7月25日前完成联调。

三、办公室于7月28日前汇总问题。

补充以下信息后，文章会更完整：会议时间、地点、主持人及参会单位或人员。

ROUTE T2: SKILL.md#任务模式路由与交付模式、核心流程、硬边界；references/task-route-cards.md#使用口径；references/genre-playbooks.md#会议纪要；references/genre-checklist.md#会议纪要；references/handling-elements.md#通用要素、文种要素表、缺项处理；references/proofreading-checklist.md#语言和格式自检、稿内一致性；未联网

T3

关于租用电子档案备份服务器的申请

为满足电子档案备份需要，档案室拟租用1台普通备份服务器，租期12个月，预算24000元。该服务器仅用于电子档案备份，不涉及人工智能、模型、GPU或推理业务。

以上申请，恳请批准。

档案室

影响正式报送：请补充审批对象和成文日期。

ROUTE T3: SKILL.md#任务模式路由与交付模式、核心流程、硬边界；references/task-route-cards.md#使用口径；references/genre-playbooks.md#请示/申请；references/genre-checklist.md#申请；references/handling-elements.md#通用要素、文种要素表、缺项处理；references/formal-addressing.md#上行文、常见结尾；references/proofreading-checklist.md#语言和格式自检、稿内一致性；未联网

T4

关于租赁GPU推理服务的请示

为满足业务推理需求，拟租赁GPU推理服务12个月，预算60万元，现请予批准。

一、需求情况

业务预计每月使用8000万Token，峰值并发40。拟租赁的服务应与上述需求规模相匹配，并具备相应的推理服务承载能力。

二、服务级别和数据安全要求

合同中应明确服务级别协议（SLA），包括服务可用性、峰值并发保障、故障响应和恢复时限、监控告警及运维支持等内容。业务数据应在约定环境和范围内处理，明确数据权属、访问权限、传输和存储保护、日志审计、运维访问及服务终止后的数据处置要求；未经授权，不得留存、转移或用于约定范围外的用途。

三、验收要求

验收应核对服务方案对每月8000万Token需求的支撑能力，并测试峰值并发40情况下的服务表现。验收内容还应包括推理服务可用性、SLA响应机制、安全配置、日志审计和运维文档，具体测试方法及通过标准在合同和技术文件中明确。

妥否，请批示。

影响正式报送：请补充主送机关、发文单位和成文日期；明确SLA可用率、故障响应和恢复时限、数据处理环境以及验收测试方法和通过标准。

ROUTE T4: SKILL.md#任务模式路由与交付模式、核心流程、硬边界；references/task-route-cards.md#使用口径；references/genre-playbooks.md#请示/申请、AI算力与技术服务；references/genre-checklist.md#请示；references/argument-chains.md#请示和请批附件、AI算力和技术服务；references/handling-elements.md#通用要素、文种要素表、AI算力和技术服务要素、缺项处理；references/formal-addressing.md#上行文、常见结尾；references/ai-compute-docs.md#写作定位、算力资源采购或租赁方案、GPU/服务器租赁技术需求、SLA与运维、安全与合规、复核要点；references/proofreading-checklist.md#语言和格式自检、稿内一致性；未联网

T5

通勤车辆租赁可行性研究摘要

为满足后勤通勤需求，拟租赁2辆通勤车，期限1年，预算18万元。购买方式可形成自有车辆，但需一次性投入购置资金；租赁方式可按一年期需求配置车辆，支出边界与本次预算相对应。综合需求期限和资金安排，租赁可作为初步可行方案。最终选择应在统一使用周期和成本口径后确定。

补充以下信息后，文章会更完整：2辆同类车辆购置价格、租赁报价明细及一年期使用管理成本。

ROUTE T5: SKILL.md#任务模式路由与交付模式、核心流程、硬边界；references/task-route-cards.md#使用口径；references/genre-playbooks.md#调研报告/研究报告/可研报告/建设方案；references/argument-chains.md#可研、调研和审查；references/handling-elements.md#通用要素、文种要素表、缺项处理；references/proofreading-checklist.md#语言和格式自检、稿内一致性；未联网

T6

1. 位置：“马上搞起来”
风险层级：中高
修改建议：表述口语化，且未说明具体办理事项。“马上”还缺少明确起始时点，建议改为可核对的办理动作和时间要求。

2. 位置：“月底前把结果发过来”
风险层级：中高
修改建议：明确具体截止日期、报送材料名称或内容、接收单位及报送方式，避免“结果”“发过来”等含义不清的表达。

3. 位置：“大家务必高度重视”
风险层级：中
修改建议：属于空泛强调，未形成可执行要求。建议改为与事项直接相关的办理要求；没有新增要求时可删除。

4. 位置：全文（如作为完整通知）
风险层级：中
修改建议：补充标题，核对主送范围、通知事项、发文主体和成文日期；如并非所有部门均需办理，应进一步明确实际对象。

ROUTE T6: SKILL.md#任务模式路由与交付模式（审稿或复核）、硬边界；references/review-checklist.md#定稿前高风险先查、段落复核、全文复核；references/genre-checklist.md#通知；references/handling-elements.md#通用要素、文种要素表；references/official-style.md#行文语气、轻量语气替换建议、应避免的写法；references/proofreading-checklist.md#语言和格式自检；未联网

T7

关于采购办公电脑的申请

现申请采购办公电脑3台，预算15000元，经费来源为年度信息化预算。

以上申请，恳请批准。

ROUTE T7: SKILL.md#任务模式路由与交付模式、只输出正文规则、硬边界；references/task-route-cards.md#使用口径；references/genre-playbooks.md#请示/申请；references/genre-checklist.md#申请；references/handling-elements.md#通用要素、文种要素表、缺项处理；references/formal-addressing.md#上行文、常见结尾；references/proofreading-checklist.md#语言和格式自检、稿内一致性；未联网

T8

关于新增2个专业技术岗位编制的请示

本单位拟新增2个专业技术岗位编制，现就该事项报请审批。

妥否，请批示。

影响正式报送：请补充主送机关和发文单位。

ROUTE T8: SKILL.md#任务模式路由与交付模式、核心流程、硬边界；references/task-route-cards.md#使用口径；references/genre-routing.md#文稿类别、上行文、文种边界、路由提示；references/genre-playbooks.md#请示/申请；references/genre-checklist.md#请示；references/argument-chains.md#请示和请批附件；references/handling-elements.md#通用要素、文种要素表、缺项处理；references/formal-addressing.md#上行文、常见结尾；references/proofreading-checklist.md#语言和格式自检、稿内一致性；未联网

T9

关于商请提供接口文档的函

数据中心：

现商请贵中心协助提供接口文档，并于7月22日前反馈联系人信息。

请予支持为盼。

补充以下信息后，文章会更完整：反馈方式、发函单位和成文日期。

ROUTE T9: SKILL.md#任务模式路由与交付模式、核心流程、硬边界；references/task-route-cards.md#使用口径；references/genre-routing.md#文稿类别、平行文、文种边界、路由提示；references/genre-playbooks.md#函/复函/征求意见函；references/genre-checklist.md#函；references/handling-elements.md#通用要素、文种要素表、缺项处理；references/formal-addressing.md#平行文、常见结尾；references/proofreading-checklist.md#语言和格式自检、稿内一致性；未联网

T10

市图书馆关于消防检修期间闭馆的公告

因消防检修，市图书馆将于7月18日闭馆一天，7月19日恢复开放。如需咨询，请拨打010-12345678。

特此公告。

市图书馆
2026年7月15日

ROUTE T10: SKILL.md#任务模式路由与交付模式、核心流程、硬边界；references/task-route-cards.md#使用口径；references/genre-playbooks.md#通知/通告/公告/公示/通报；references/genre-checklist.md#公告；references/handling-elements.md#通用要素、文种要素表；references/proofreading-checklist.md#语言和格式自检、稿内一致性；未联网

T11

关于开展月度资产盘点工作的通知

各部门：

请开展月度资产盘点，并于7月31日前将盘点表报送资产科。

联系人：李明，联系电话：010-87654321。

特此通知。

ROUTE T11: SKILL.md#任务模式路由与交付模式、核心流程、硬边界；references/task-route-cards.md#使用口径；references/genre-routing.md#法定公文、下行文、文种边界、路由提示；references/genre-playbooks.md#通知/通告/公告/公示/通报、意见/决定/决议/议案/公报/命令；references/genre-checklist.md#通知、命令（令）；references/handling-elements.md#通用要素、文种要素表；references/proofreading-checklist.md#语言和格式自检、稿内一致性；未联网

T12

关于年度先进个人拟推荐人选的公示

现对3名年度先进个人拟推荐人选进行公示。公示期为7月16日至7月22日。公示期间，如有异议，请以书面形式向人事处反映。联系电话：010-66668888。

某市教育局
2026年7月15日

补充以下信息后，文章会更完整：3名拟推荐人选姓名。

ROUTE T12: SKILL.md#任务模式路由与交付模式、核心流程、硬边界；references/task-route-cards.md#使用口径；references/genre-routing.md#常用事务文书、文种边界；references/genre-playbooks.md#通知/通告/公告/公示/通报；references/genre-checklist.md#公示、公告、通告；references/handling-elements.md#通用要素、文种要素表、缺项处理；references/formal-addressing.md#常见结尾；references/proofreading-checklist.md#语言和格式自检、稿内一致性；未联网
