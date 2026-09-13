"""Native isolated Codex drafting pairs: main versus a frozen working candidate."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[4]
MODELS = ["alibaba-token-plan/qwen3.8-flash", "alibaba-token-plan-2/qwen3.8-flash", "command-code/deepseek-deepseek-v4.1-flash", "minimax-cn/MiniMax-M3", "ollama-cloud/glm-5.3-flash"]
CASES = {
    'motion_with_supplied_details': '以下均为虚拟写作练习材料。请以海岚市人民政府名义向海岚市人大常委会拟一份提请审议《海岚市公共服务设施管理条例（草案）》的议案。草案已经2026年9月10日市政府常务会议讨论通过，拟明确管理单位承担日常维护、使用单位及时报告损坏，并由管理单位在设施入口公示服务内容、开放时间和咨询方式。请在议案中简要说明这三方面已给定的主要内容及便于维护和查询的目的。附件为该草案；落款2026年9月12日。',
    'complete_under_100': '请写一份完整的会议通知，控制在100字以内。资料中心定于2026年9月18日下午3点，在二楼会议室召开目录核对会，综合岗和各档案室负责人参加。请带本室待核对目录，会上集中确认编号和保管期限，不能参会的请在会前联系综合岗说明。通知由资料中心发出，写得简洁自然。',
    'explicit_under_40': '请把这条内部提醒写得简洁自然，最多40个字：今天下午3点在二楼会议室核对目录，请综合岗同事带上待核对清单。',
    'commentary_review_rewrite': '帮我审核并优化这篇新闻评论，修正错字、病句和空泛重复，保持事实与观点的意思，给我改好稿。事实材料：街道两个服务点的窗口位置已经调整，一个同步更新了入口指引，另一个仍使用旧指引；没有投诉数量或效率数据。原稿：指引要跟着实际办理条件更新。两个服务点已经调正窗口位置，一个服务点同步更新了入口指引，另一个服务点仍使用旧指引。`本文将从信息更新、服务衔接两个方面进行分析。`群众是否少走弯路，取决于指引是否准确。问题并不是有无设置指引，而是旧指引与实际窗口位置不一致。更新线上信息也不能代替现场指引，两者服务于不同的查询情境。信息更新应与窗口变动相衔接，避免已经变更的服务信息继续误导查询。避免信息没有更新，因为信息没有更新就不能正确指引。',
    'commentary_review_only': '帮我审核这篇新闻评论，给出问题位置和修改建议。事实材料：街道两个服务点的窗口位置已经调整，一个同步更新了入口指引，另一个仍使用旧指引；没有投诉数量或效率数据。原稿：指引要跟着实际办理条件更新。两个服务点已经调正窗口位置，一个服务点同步更新了入口指引，另一个服务点仍使用旧指引。`本文将从信息更新、服务衔接两个方面进行分析。`群众是否少走弯路，取决于指引是否准确。问题并不是有无设置指引，而是旧指引与实际窗口位置不一致。更新线上信息也不能代替现场指引，两者服务于不同的查询情境。信息更新应与窗口变动相衔接，避免已经变更的服务信息继续误导查询。避免信息没有更新，因为信息没有更新就不能正确指引。',
    'procurement_result_notice': '请为海川资料服务中心起草一份采购成交结果公告。项目为文件共享服务器租赁，编号HC-2026-07；成交供应商为云杉技术服务有限公司，成交金额23200元，租赁1台服务器，服务期12个月，成交结果已于2026年9月11日确定。原预算上限为24000元。联系人王老师，咨询邮箱procurement@example.org。请准确公告本次已经形成的结果，正文简洁完整。',
    'procurement_termination_notice': '请为海川资料服务中心起草采购终止公告。文件共享服务器租赁项目编号HC-2026-08，本次采购因需求范围调整而终止；是否重新采购尚未决定。采购人是海川资料服务中心，联系人王老师，咨询邮箱procurement@example.org，公告日期为2026年9月13日。请清楚说明终止对象、原因和当前状态。',
    'approval_request_letter': '请以青川市图书馆名义给市机关事务管理局起草一份请求批准临时使用会议厅的函。双方不存在隶属关系，机关事务管理局负责该会议厅的使用审批。图书馆拟于2026年10月18日14时至17时在该会议厅举办阅读交流会，预计参加人员60人，申请尚未批准；联系人陈老师，邮箱library@example.org。请把使用需要、时间、用途及请求批准的事项写清楚，沿用函的形式，简短完整。',
    'approval_response_letter': '请以青川市机关事务管理局名义，给与本局没有隶属关系的市图书馆起草《关于同意临时使用会议厅的函》。市图书馆已提交《关于申请临时使用会议厅的函》，文号青图函〔2026〕8号；本局有该厅使用审批权限，已同意图书馆于2026年10月18日14时至17时在此举办阅读交流会，参加人员限60人，使用结束后恢复原有桌椅摆放。以上为已确定的审批意见。请准确写成复函，称谓和语气与双方关系相符。',
    'fixed_title_application': '请为综合办公室起草一份报单位负责人审批的采购申请。单位模板题名固定为“设备情况说明”，题名和“现有情况”“申请事项”“金额”三个栏目请保留。材料：办公室两把座椅破旧，拟申请更换办公椅2把，每把估算400元，用于日常办公；采购时间和供应商尚未确定。请把申请原因、具体事项和金额写清楚，并明确请负责人审批。',
    'unlisted_authorization': '资料中心拟给档案馆出具一份领取材料授权书，委托周宁于9月18日代领资料中心送存的目录核对件，授权仅限本次领取，有效期至9月20日。请按照“委托单位、受托人、授权事项、有效期、单位盖章”这些栏目起草，盖章位置保留，内容简明完整。',
    'editorial_note_only': '便民服务中心内刊拟刊登两篇岗位记录，分别介绍更新办事材料清单、按现有窗口位置调整指引。这些改动仍在试用，使用反馈尚未汇总。编辑部希望同事关注服务指引怎样随办理条件同步调整、哪些问题还需核对。请以编发者身份为这组材料写一段简短完整的编者按，以“编者按”为标题。岗位记录原文不用重写。',
    'editorial_and_news': '请为中心内刊准备一段编者按，并写出其后刊登的一则活动消息，二者分清。编者按由编辑部说明编发意图：供同事交流材料清单如何随实际办理条件更新，提醒关注仍需核对的问题。消息材料：2026年9月10日下午，青川便民服务中心举办材料清单使用说明会，综合岗介绍了两份更新后的清单，并演示怎样查询有效版本；各窗口工作人员参加并就清单字段提出问题，部分问题仍待综合岗核对。两份都简短完整即可。',
    'review_estimate_table': '请根据记录写一份终端更新申请的审查意见，并附简明核对表。申请主体为资料中心，信息科提供性能测试记录，综合办公室提供费用估算。测试实测：旧终端处理一批目录用时18分钟，新终端样机用时12分钟；不代表所有任务的处理时间。费用估算：拟购终端3台，每台4800元，安装服务估算1200元；原申请总额误写为15000元，请复算并指出。供应商尚未确定，这些价格没有实际支付。信息科负责补充测试条件，综合办公室负责补正费用表，完成时间均未确定。审查结论是补正材料后再次复核，尚未通过。正文与表格写清各自责任、实测与估算的区别及当前结论。',
    'plain_speech_style': '资料中心负责人要在内部交流会上发言，请把这段口语整理成自然、正式的发言稿：我们和同事试了一个资料查询工具，10个测试问题里7个结果和原始资料一致，3个还有遗漏。查到出处之后，我们还得拿原文核一遍。办公室会先把遗漏类型整理出来，然后再安排下一轮小范围试用，是否扩大使用还没决定。我的想法是，如果准确性后面能稳下来，大家查材料可能更稳、更省事，但现在不能说实际办公时间已经减少了。希望大家把真实使用情况记下来，一起看看这个工具到底能帮上什么忙。',
    'procurement_application_and_speech': '综合办公室需要两份材料：一份报单位负责人审批的设备采购申请，附采购明细表；一份由综合办公室负责人在内部协调会上说明同一需求的简短发言稿。下面是同事口头整理的材料，请写得正式自然：三个会议室要同时用的时候，现有设备不够用。想补投影仪2台，每台3500元，再补幕布2套，每套600元，都用来补充会议室设备。这些是估算价格，还没选供应商，也没定采购时间和预算科目。请核算金额，申请正文和附件要对得上。发言时讲清楚为什么需要补设备、准备申请哪些东西，先核对预算科目，再报负责人审批。两份材料分别给完整稿件，采购事项还是申请阶段。',
    'formulaic_application_attachment': '请以综合办公室名义给单位负责人写一份设备采购申请，采用自然的申请开头和常用请批结尾，把申请正文和采购明细附件一并给出。现有会议室设备已不能满足三间会议室同时使用的需要；拟购投影仪2台，每台3500元，幕布2套，每套600元，用途均为补充会议室设备。请核对分项金额、合计金额及正文与附件的对应关系。供应商和采购时间尚未确定，预算科目和落款日期未提供。缘由和必要性写清即可，适当分段。',
    'formulaic_reply': '请以青川县图书馆名义给县文化馆写一份正式复函，注意选择函件常用的来文引叙和结尾用语，行文自然得体。文化馆来函询问能否于2026年10月18日下午借用图书馆报告厅开展阅读交流，图书馆已确认该时段可以借用；请文化馆于10月12日前告知预计人数和联系人，以便安排场地。双方是平行单位，来函文号和成文日期未提供，先给完整稿件。',
    'formulaic_report': '现在整理的是2026年度材料。请以资料中心名义向主管部门写一份情况报告，采用自然的公文开头、承接和结尾用语。9月10日完成两批目录核对，另外一批仍在核对；现有查询设备能够继续使用，是否购置新设备尚未研究。本稿用于汇报进展，没有申请审批事项，也没有收到主管部门来函。正文写清已经完成和仍在进行的情况，简短完整即可。',
    "material_based_analysis": "只按这些材料写一份办公椅采购申请，给单位负责人审批：综合办公室有24个固定工位，24把现有办公椅中6把已损坏且无法修复；对应6个工位临时借用会议室座椅，会议室使用时需要归还。拟购办公椅6把，每把420元，供应商和采购日期尚未确定。请把采购缘由和必要性讲清楚，再写明数量金额和请求。",
    "existing_field_form": "帮我把这份采购申请文字改得正式些。当前底稿：申请部门：综合办公室；采购品目：办公椅；数量：4把；参考单价：420元；申请理由：旧的4把办公椅坏了，想买4把替换用；供应商：尚未确定；采购日期：尚未确定。",
    "usage_value_report": "只按以下试用记录写一份工具使用体验报告，约250至400字。信息中心试用了一个资料查询工具：10个测试问题中7个返回内容与原始资料一致，另外3个有遗漏；7个准确结果可以帮助工作人员定位原文出处，但仍要对照原始资料复核。工具可作为资料查找辅助，尚未用于正式业务；建议继续小范围试用、观察遗漏类型，是否扩大使用尚未决定。把使用价值、问题和后续建议写清楚。",
    "feasibility_conditional_advice": "只按这些材料完善一段可研分析：资料中心拟试点电子目录查询，现有电脑可用，预计有8人使用；需求是按目录编号查找已确认档案。自建还是租用服务尚未决定，预算和建设周期仍待论证。请结合现有需求说明可以比较和验证哪些方面，形成供决策参考的分析，保持设想状态。",
    "news_supported_analysis": "根据材料写一篇简短活动新闻：9月10日，市企业服务中心组织企业交流会，8家企业代表参加；代表介绍各自产品，交流合作需求。中心负责人表示，交流的目的在于让企业了解彼此需求。可以结合这些动作概括一次交流的直接作用，其他按材料写。",
    "feasibility_procurement_content": "帮资料中心整理一份简短可研报告，供决定是否实施电子目录检索试点。需求是让工作人员查询已确认档案目录；现有电脑可使用，拟购买扫描仪1台，参考价6000元，正式报价和预算来源待核。试点范围及验收指标尚待论证，当前没有可行性通过结论。采购部分是报告中的条件分析，保留可研用途。",
    "procurement_plan": "帮综合办公室写设备采购方案，报单位负责人审批。拟购买投影仪2台，每台3500元，幕布2套，每套600元，用于补充会议室设备；先核对两类设备数量和金额，再按批准范围办理采购，供应商和采购时间尚未确定。预算科目暂未提供。把采购内容、金额和已给步骤写清楚。",
    "procurement_review_opinion": "根据这份评审记录写一份设备采购方案审查意见：方案拟购投影仪2台，每台3500元，幕布2套，每套600元；记录指出总额应为8200元，原方案误写8000元；两类设备用途均为补充会议室设备；供应商和采购时间尚未确定，预算科目材料尚未提供。评审结论为补正金额、补充预算材料后复核，未作通过结论。只按记录形成审查意见。",
    "design_review_opinion": "根据记录整理一份初步设计审查意见。审查对象是资料中心一层空间改造初步设计，审查记录指出平面图与设备清单中的档案柜数量不一致，需核对一致后提交复核；本轮没有提出新增房间或调整面积，也未作通过结论。这是设计审查记录整理，材料没有涉及设备采购。",
    "work_priorities": "帮综合办公室把明年打算写成工作要点：拟完善会议室预约登记，拟优化物资台账核对；计划每季度梳理一次预约冲突和登记差错。具体人员分工、预算和起始时间尚未决定。先把重点任务和思路写清楚。",
    "work_summary": "帮综合办公室写上半年工作总结。完成45场会议室预约协调、30批物资登记，办公室共同完成6次会议保障，会上桌椅布置由林舟负责；发现有3次预约时间冲突，均经沟通调整。下半年拟完善预约登记，是否采用线上表单尚未决定。写清工作、问题和改进思路，简短完整即可。",
    "weekly_report": "帮我把本周情况整理成周报，保留四个字段各占一行。已完成：接口A测试30次；推进中：核对其中2次超时的日志；问题：超时原因尚未查明；下周：张工建议追加测试，是否采用尚未决定。只整理这些内容。",
    "public_notice": "帮海岚市公共服务中心起草关于报送服务点名单的通知，将公开发布在中心网站。请各业务科于9月25日前把所负责服务点的名称和地址报综合办公室汇总，联系人周老师，联系方式暂未提供。标题保留通知，写清报送安排即可。",
    "research_comparison": "帮我写一份报领导参考的服务窗口调研报告。调研组走访了甲乙两个服务点，甲点使用现有窗口、无需新增投资，乙点提出增设窗口的设想，投资金额尚待测算；受访人员各5人，甲点3人建议增加周末服务，乙点2人建议延长下午开放时间。请比较两点观察结果并概括可供进一步研究的方向，这次稿件用途是汇报调研发现。",
    "sparse_plan": "帮资料室起草档案目录整理实施方案。目标是完成2025年度已确认档案目录整理和资料录入；分为目录核对、资料录入、复核三步，试点至9月30日，验收指标尚待确定。负责人和预算材料暂未提供。按现有材料写成简短但完整的方案。",
    "platform_review": "帮我审核并改好这段活动报道。有效材料：9月10日，市企业服务中心组织企业交流会，8家企业代表参加，代表介绍各自产品并交流合作需求。现稿：9月10日，市企业服务中心组织企业交流会，8家企业代表参加，代表介绍各自产品并交流合作需求。这次活动为企业交流搭建了强大平台，满足未来发展需要。请给自然简洁的改好稿件。",
    "official_marks": "帮我校改这份内部工作提示，清除起草旁白，给改好全文。材料要求保留文件首页的‘内部资料 注意保密’和‘第二版（2026年9月修订）’。现稿：内部资料 注意保密。第二版（2026年9月修订）。会议室使用提示。本文由AI整理，以下为最终版本。会议室使用完毕后，请关闭设备并恢复桌椅，设备故障反馈综合办公室。仅供参考，以实际审核结果为准。我只要改后稿件。",
    "quote_proofread": "请校改下面的纯文本讲话材料，改好后给我全文，不用Markdown。有效材料明确全年组织3场培训；负责人原话由我提供，但出处和日期还没核验。现稿第一行主标题是‘凝心聚力推进服务改进。’，下一行是小标题‘一、工作要求。’，下面接正文：会上，负责人原话是：‘要久久为功，把群众的事办实。’ 1.各部门要快速的回应诉求，全年组织3台培训。",
    "notice_receiver": "根据材料起草简短通知：请各业务科于9月20日前把培训报名表发送到市培训中心邮箱pxzx@example.org，接收联系人王老师。发文单位和成文日期还没有给，先把稿子写好。",
    "compute_units": "改写一段算力费用说明：试用期共调用模型1200次，输入和输出合计800万Token；按Token计费，单价及总额尚待核实。请把需求与费用口径写清，保持数字和待核状态，不新增GPU、并发或SLA数据。",
    "minutes_local": "帮我改这份会议纪要：把末句‘会议要求张工下周完成追加测试’改为‘张工建议追加测试，会议尚未决定是否采用’，其余保持。现稿：接口测试讨论纪要。9月10日，信息中心讨论接口测试情况。接口A已测试30次，其中2次返回超时，原因仍在核对。会议要求保留测试记录。会议要求张工下周完成追加测试。请给改好后的纪要。",
    "hosting_agenda": "帮信息中心主任周宁写一份简短的会议主持词，会上直接使用。会议为9月18日接口联调交流会，参会人员是信息中心全体同事。议程依次为：赵明介绍联调进展；刘青说明日志核对中发现的问题；参会同事交流意见；主持人宣布会议结束。按这些议程串联完整。",
    "duty_short": "帮林舟写一份提交部门考核的上半年述职报告，简短完整即可。林舟是综合办公室工作人员，职责为会议室预约协调和物资登记；上半年协调45场会议室预约，完成30批物资登记。办公室共同完成6次会议保障，林舟负责其中的桌椅布置，其他事项由同事承担。材料没有提供问题不足和下一步计划。",
    "duty_oral": "把这些内容写成林舟在部门考核会上直接读的一段述职发言：担任综合办公室工作人员，负责会议室预约协调与物资登记；上半年协调45场会议室预约、完成30批物资登记；参与办公室6次会议保障，负责桌椅布置。整体会议保障由办公室共同完成。简短自然即可。",
    "speech_control": "周宁是接口联调交流会主持人，请帮他写会议结束前的一段总结讲话。听众是信息中心同事，主题是加强联调中的沟通。材料：赵明和刘青分别交流了进展与日志核对问题，大家提出了意见；周宁希望今后沟通时把已核实情况和待核问题区分清楚。围绕这一主题讲清楚，不需要主持串词。",
    "chair_reason": "帮综合办公室写一份完整的办公椅采购申请，报单位负责人审批。材料：办公室现有4把办公椅较为破旧，拟购置4把办公椅用于更新，每把420元；供应商和采购日期尚未确定，预算科目材料暂未提供。",
    "request_reason_missing": "帮综合办公室写一份资料核对延期申请，报单位负责人审批。资料核对原定9月20日完成，现拟申请延至9月27日；延期原因还没有提供。",
    "request_reason_revision": "帮综合办公室审核并改好这份延期申请，报单位负责人审批。有效材料：资料核对原定9月20日完成，现拟申请延至9月27日；延期原因尚未提供。现稿：关于资料核对工作延期的申请。单位负责人：资料核对工作原定9月20日完成，因＿＿＿＿＿＿＿＿，申请将完成时间延至9月27日。妥否，请批示。综合办公室。请给改好稿件。",
    "request_full": "帮综合办公室写一份完整采购申请，报单位负责人审批，正文250至400个非空白字符。材料：本单位设有24个固定工位，现有办公椅24把，其中6把已损坏且无法修复，只有18把能够正常使用；受损座椅对应的6个工位目前临时借用会议室座椅，会议室使用时需要归还。现拟购置办公椅6把，用于替换损坏的6把，参考单价420元，合计请计算。本次不新增工位。报批时供应商和采购日期都还没有确定。预算科目暂未提供。请把购置理由、具体申请事项和金额写清楚。",
    "procurement_announcement": "以下为虚拟写作材料。请拟采购公告：海岚市档案服务中心拟采购扫描仪3台，最高限价合计1.8万元；采用公开询价，报名截止2026年9月25日17时，材料交市档案服务中心综合科，联系人李工，电话020-81234567。公告只发布这些已明确事项，不增加资质、评审标准或履约要求。",
    "explanation": "请帮信息中心写一份给业务部门的情况说明：9月10日10时至10时08分，统一查询接口出现访问延迟，随后恢复；原因正在核查。此稿用于解释这一次访问延迟，向使用部门说明情况。不要新增影响范围、处置过程和预防安排，简短成稿。",
    "complex_application": "帮综合办公室写一份设备采购申请，给单位负责人审批。现有会议室设备已不能满足三间会议室同时使用的需要，拟购投影仪2台，每台3500元；幕布2套，每套600元，合计请计算；两类设备用途都是补充会议室设备，明细表作为附件，供应商和采购时间还未确定。预算科目材料未提供。请给申请正文和对应明细，适当分段，金额核对清楚。",
    "institution": "把这份明确的现行安排整理成简短的会议室使用细则：适用于本单位三间会议室；使用部门在单位内部预约表登记使用时间、会议室和联系人；同一时段冲突时，由综合办公室联系相关部门协调；使用完毕后关闭设备并恢复桌椅；设备故障反馈综合办公室。写成可执行条款，仅整理这些规定。",
    "decision": "以下均为虚拟写作练习材料。请拟一份决定：海岚市人民政府已决定将便民服务大厅开放时间延长为工作日8:30至18:00，自2026年10月1日起实行；市政务服务中心负责落实。沿用已给信息，简短成稿。",
    "resolution": "以下均为虚拟写作练习材料。请拟一份决议：海岚市第六届人民代表大会第三次会议于2026年9月12日审议了市人民政府工作报告，会议决定批准该报告，要求市人民政府做好本年度已确定的重点民生项目。不要增添表决人数和未给评价。",
    "motion": "以下均为虚拟写作练习材料。请拟一份议案：海岚市人民政府向海岚市人大常委会提请审议《海岚市公共服务设施管理条例（草案）》；草案已经市政府常务会议讨论通过，主要是明确设施维护责任和服务信息公示要求，现提请审议。附件名称就是该草案。落款2026年9月12日。",
    "communique": "以下均为虚拟写作练习材料。请拟一份会议公报：海岚市城市更新工作会议于2026年9月12日召开；会议审议通过《2027年公共空间改造计划》，计划涉及12处公共空间，要求市住建局继续核对实施条件；具体开工时间尚未确定。只发布这些已形成事项。",
    "order": "以下均为虚拟写作练习材料。请拟一份公布规章的市人民政府令：海岚市人民政府令第18号；《海岚市公共服务设施维护办法》已经2026年9月10日市政府常务会议审议通过，现予公布，自2026年11月1日起施行。签署人：市长林岳；签署日期2026年9月12日。只写令的正文，不展开办法。",
    "review": "帮我审核这篇稿件，给出修改建议。材料事实是：信息中心完成接口A的30次测试，其中2次返回超时，原因仍在核对；张工建议追加测试，是否采用尚未决定。现有稿件：接口测试工作报告。本文将从测试情况、问题分析、后续安排三个方面展开说明。信息中心已完成30次测试，发现2次超时，目前已实现系统稳定运行。张工提出追加测试的建议，中心已决定下周组织全面测试。本报告只根据所给材料起草，不新增事实、不扩大结论、不作未经核实的推断。",
    "review_rewrite": "帮我审核这份采购申请并优化好，成稿控制在120至220个非空白字符。有效材料：申请部门为综合办公室，报单位负责人审批；4把现有办公椅已损坏，申请购置4把替换，每把420元，供应商和采购日期尚未确定；预算科目缺失，上轮已经提出但还没有回复。当前底稿：关于购置办公椅的申请。单位负责人：本申请将从购买原因、购买数量和购买金额三个方面展开。办公室拟购买4把办公椅替换4把已损坏的旧椅，每把420元，合计1800元。已确定供应商，下周采购。我室将以此次采购为契机，构建协同高效的办公保障新格局。综合办公室。",
    "minutes": "帮我把材料写成会议纪要，稿件控制在180至260个非空白字符。9月10日，信息中心组织接口测试讨论。接口A累计测试30次，其中2次返回超时；原因仍在核对。张工建议下周追加测试，会议尚未决定是否采用，也没有明确责任人和完成日期。王工认为应先核对超时日志，未形成结论。会议要求保留当前测试记录供核对。此前审稿曾提示‘会议地点缺失’和‘测试次数缺失’，本次补充了测试次数，地点仍未提供。记录已发生的事实和明确状态，帮我写完整稿子。",
    "application": "帮办公室写一份采购申请，申请部门为综合办公室，向单位负责人申请购买4把办公椅替换已损坏的4把旧椅。拟购产品每把420元，合计金额请据此计算；暂未确定供应商和采购日期。全文200至300个非空白字符。这一轮可以修改正文中的合计金额，其余缺失事实保留原状态。上轮审稿已指出旧稿把合计写成1800元，这项错误还没处理；预算科目也一直没有确认。不要落款日期。我只要正文，不附说明。",
    'responsibility_letter': '请为新桥服务中心写一份设备日常维护责任书草稿。涉及综合科和运维组，两方共同做好中心服务设备的日常维护。综合科登记各窗口报来的故障并告知运维组；运维组负责排查和处理设备故障，处理后把情况反馈综合科；综合科保管维修记录。适用范围是中心一楼的自助终端和排队叫号设备。以上分工是拟议安排，目前还没有签订。内容简洁些，各方责任要容易查找。',
    'initiative': '帮青禾图书馆写一份给读者的文明阅览倡议书，准备贴在阅览区。这里有成人阅览区和少儿阅读区，周末来馆读者较多。希望大家交谈时放低音量，手机调为静音，用完座位随手带走个人物品，爱护借阅书籍；家长陪同孩子时协助维护少儿区秩序。语气亲切自然，说清这样做的意义，约300字。',
    'open_letter': '请以榆园社区居委会名义给居民写一封公开信。社区活动室将在2026年10月12日至16日维修照明，这段时间活动室暂停开放，室外健身区正常使用。施工由景明维修公司负责，社区负责登记居民反映的情况。希望居民在维修期间从活动室东侧通道绕行，不进入施工区域；有关问题可到社区一楼服务台反映。信里把事项、理由和配合要求讲明白，不用太长。',
    'narration': '我们准备带新员工参观公司的产品展示区，请把这些介绍写成一段自然的讲解稿。路线依次是老产品展示台、工艺样品墙、试用区。老产品展示台陈列2008年至2015年的三代产品；工艺样品墙展示同一部件的四种加工样品，旁边有对应工序说明；试用区有两台现款设备，供参观人员查看操作界面。这次由培训专员带领参观，听众大多没有生产经验。不安排提问和现场演示，讲解顺序和转场清楚即可。',
    'information_materials': '请为澄溪街道便民服务点整理一份居民办事宣传手册正文，便于折页印刷。服务点办理居住信息登记、老年卡材料接收和公共就业咨询；地点在街道综合服务楼一楼，工作日上午9点至12点、下午2点至5点开放。居住信息登记需带身份证和居住证明；老年卡材料接收需带身份证复印件和一张近期一寸照片；就业咨询可直接到3号窗口。服务咨询电话为010-55501234。请按居民查阅和办理的顺序组织，标题简短，内容清楚。',
    'synthesis_advisory': '请根据两处服务站的记录，先写一份给青川街道办事处的《周末服务情况综合》，再以街道社区观察员的身份给便民服务中心写一封简短建议信。东站记录：9月7日接待咨询32人次，其中办理材料准备问题18人次，不少来访者希望先看到材料清单；西站记录：9月7日接待咨询25人次，其中11人次询问办理窗口位置，工作人员正在整理常见问题。两站记录口径一致，但没有登记访客身份，可能有同一人在两站咨询。建议在服务中心入口放置材料清单和窗口指引，这是观察员提出的想法，中心尚未决定采用。综合稿把共性、差异和当前状态讲清；信的语气诚恳、建议具体。',
    'server_technical_requirements': '请将下列材料整理成一份简短完整的《档案检索服务器租赁技术需求》，作为采购附件：租赁2台通用服务器，服务期12个月，用于现有档案检索系统；在本单位机房安装，与现有存储连接；需统一查看运行状态，故障设备由服务方替换；CPU、内存和连接接口规格尚待确认；验收核对设备数量、安装情况、存储连接和运行状态查看功能，提交设备清单及安装记录。写得自然、清楚，保持未定事项的状态。',
    'interface_technical_requirements': '请据以下材料起草《申报系统与进度查询页面接口需求说明》，供开发方确认：申报系统向查询页面提供申请编号、办理状态和更新时间，查询页面只读展示这些信息，不回写业务数据；沿用现有账号权限；双方接口协议和字段格式尚未确定；项目尚处于需求确认阶段。希望交付接口说明和联调记录，验收时核对字段对应、权限控制及显示内容与申报系统的一致性。篇幅不必长，给出可直接讨论的完整需求说明。',
    'formal_reply': '请以青川县教育局名义给县实验学校起草批复。县实验学校报来《关于调整图书室开放时间的请示》，文号实校〔2026〕12号，拟将开放时间调整为工作日12:00至13:30及16:30至18:00。教育局已同意按上述时间试行，试行期限为2026年10月至12月；试行后请学校报告使用情况。请写成简短完整的批复，落款日期没有提供。',
    'formal_opinion': '请以青川县教育局名义向各中小学拟一份《关于改进图书室服务的意见》。已明确的指导要求是：结合学生课余时间安排开放；保留借阅登记；学校根据藏书和借阅情况研究图书更新；发现损坏书籍及时整理登记。目的是方便学生使用现有阅读资源。各校具体开放时段由本校结合情况确定，未安排全县统一购书，也没有考核排名。语气体现上级指导，条理清楚即可。',
    'publication': '请为青川县文化馆写一份展厅暂停开放公告：文化馆二楼展厅将在2026年10月12日至14日更换照明，期间暂停开放；一楼阅览区和三楼活动室照常开放。咨询电话010-55501236。请把公众需要知道的事项写清楚，语气得体。',
    'bulletin': '请以青川街道办事处名义给各社区起草一份近期窗口服务情况通报。9月上旬抽查了4个社区的咨询记录，其中2个社区的办事材料清单已更新，另2个社区仍在核对内容；清单完成更新是此次检查发现的进展，未作排名或评优。街道要求各社区保留清单更新记录，具体完成日期未统一确定。简短成稿，准确区分进展和要求。',
    'project_addition': '请为资料中心写一份现有查询系统新增功能申请，报主管部门审批。原系统已能按档案编号查询目录；业务科提出希望按形成年度筛选结果，因此拟申请增加年度筛选功能。当前只申请确认新增功能范围，开发方案、费用和工期均待进一步评估。请把既有基础、新增需求和本次请批事项写清楚，适当说明作用，不把评估事项写成已定安排。',
    'remediation_plan': '请为青川街道便民服务中心写一份整改方案。检查发现两项问题：材料清单更新日期标注不清；窗口指引与现有窗口位置有两处不一致。中心拟由综合岗核对材料清单并补清更新日期，由服务岗核对窗口位置后更新指引，整改完成时间拟为9月30日。工作尚未启动，检查方没有提出销号或复查程序。围绕这些问题和拟议分工组织，原因可作审慎分析，简短但完整。',
    'remediation_report': '请以青川街道便民服务中心名义向街道办事处写一份整改进展报告：原先材料清单未注明更新日期、两处窗口指引与实际位置不一致。综合岗已为清单补充更新日期；服务岗已核对两处窗口位置，指引内容仍在修改，尚未张贴。相关问题暂未复核，也未确认整改完成。汇报截至9月18日的进展，保持各事项状态。',
    'feedback_report': '请为资料中心向主管部门写一份试用反馈情况报告。两组人员试用检索功能，第一组反馈编号查询结果准确，第二组反馈部分目录名称较长时页面显示不完整；这一显示问题仍在核对。有人建议增加按年度筛选，中心还没有决定是否增加。请归并已经收到的反馈、当前处理状态和未定建议，稿件简短完整。',
    'complaint': '请帮林宁给榆园社区物业服务中心写一份情况反映。林宁住3栋，9月16日和17日晚上回家时发现3栋一楼走廊两盏灯未亮，白天没有查看过，也不清楚原因。希望物业核查照明并反馈处理情况。语气客观礼貌，把亲历时间、位置和诉求说清楚，不扩大为全小区问题。',
    'parallel_reply': '请以青川县图书馆名义给县文化馆写一份复函。文化馆来函询问能否借用图书馆报告厅开展阅读交流，拟使用日期为10月18日下午。图书馆已确认该时段可以借用，请文化馆于10月12日前告知预计人数和联系人，以便场地安排。双方是平行单位；来函文号和落款日期未提供。',
    'deployment': '请把以下已经确定的安排写成青川街道周末服务准备工作部署，发给综合岗与各社区。各社区于9月20日前提交本周末服务人员名单；综合岗汇总名单并核对窗口安排，9月22日前发回各社区核对；各社区发现姓名或窗口对应有误时反馈综合岗。名单只用于此次周末服务安排，未增加考核和统计报表。内容清楚、便于执行即可。',
    'news_commentary': '请根据这些材料写一篇约400字的新闻评论，重点谈公共服务信息为什么需要跟着实际办理条件更新。材料：某街道两个服务点的窗口位置已经调整，其中一个服务点同步更新了入口指引，另一个服务点的指引仍是旧位置；材料没有提供投诉数量或效率数据。可以就这一现象作有据分析并提出建议，语气平实，评论须有明确观点，不写成工作部署。',
    'ordinary_server_announcement': '请根据以下材料起草一份采购公告。采购人是海川资料服务中心，项目名称是文件共享服务器租赁，租赁 1 台服务器，供中心内部存储、共享日常文档，服务期 12 个月，预算上限 24000 元。供应商应于 2026 年 9 月 25 日 17 时前，将报价和服务说明发送至采购材料中给定的邮箱 procurement@example.org，联系人为王老师。正文简洁，保留以上采购要素。',
    'public_rule_suggestion': '请以晨星信息服务有限公司的名义，给平台运营方写一封建议信。我们手头只有平台公开的申报说明：页面的“附件要求”栏目写应上传 PDF 文件，“常见问题”栏目却写应上传 Word 文件。请建议统一两处格式口径，并说明这样便于申报方准备材料。写得礼貌、具体，正文简短。',
    'ordinary_word_summary': '请把下面已经定稿的内部工作总结整理成普通 Word 文档，保留文字、标题和落款，排版清楚即可。\n\n资料室阶段工作总结\n\n本阶段，资料室整理纸质档案 120 盒，完成目录录入 860 条。另有 15 盒档案的分类信息正在核对。\n\n资料室',
    'guards_plain_titles': '请把下面这份采购申请整理成可以提交的正式正文，内容不增不减，按现有层次整理后直接以纯文本给我。\n\n关于购置扫描仪的申请。\n\n一、申请事由。\n资料室现有扫描仪已损坏，纸质档案仍需扫描归档。\n二、申请事项。\n拟购置扫描仪 1 台，预算 3000 元。\n三、有关事项。\n（一）设备用途。\n用于纸质档案扫描归档。\n（二）请财务室复核预算金额。\n妥否，请批示。\n资料室',
    'guards_business_marks': '下面是业务组准备讨论的资料借阅流程说明，请改得平实清楚，直接给我改后全文。\n\n资料借阅流程说明\n内部讨论稿 V0.3\n\n使用范围声明：本稿用于资料室与档案室讨论室内借阅流程，适用对象为两室工作人员；对外借阅仍按现行规定办理。\n\n资料室登记借阅申请后，将申请表交档案室核对档案编号。编号暂时无法核对时，申请保持待核状态。\n\n本文将从办理环节角度对有关工作进行说明。',
    'guards_notice_receiver': '请根据这些安排写一则简短通知：业务科、资料室于 9 月 18 日下午 3 时在二楼会议室参加档案整理培训。参会回执请于 9 月 16 日前报办公室，接收邮箱为 office@example.org，联系人是王老师。',
    'guards_compute_units': '请把这份智能问答服务试用记录整理成一段供负责人阅读的情况汇报：本周共调用 2400 次，消耗 180 万 Token，有 36 名用户参与试用，峰值并发为 8。费用记录为 120 元。当前调用量受试用额度限制，下阶段开放范围尚未确定。',
    'guards_grammar_quote': '请校对并润色下面这段工作总结，改好后给我完整段落：\n\n本周，工作人员认真得核对了三份登记表，整理出两台问题清单，形成了完整地记录。大家做得很仔细，坚持防微杜渐，及时发现细小差错。负责人在会上说：“工作贵在持之以恒。”',
    'scope_state_not_started': '本周收到 12 条设备报修登记，设备管理员负责维修联系，目前尚无处理结果，维修联系尚未启动。请据此写一段简短情况报告。',
    'scope_state_started': '本周收到 12 条设备报修登记，设备管理员负责维修联系，现已开始联系维修，目前尚无处理结果。请据此写一段简短情况报告。',
    'scope_word_complete_signoff': '学校旧打印机经常卡纸，教务处拟申请购置一台新打印机，预算 1800 元，报学校审批。请写一份完整申请稿，落款完整，并排成 Word。',
    'scope_word_today': '学校旧打印机在 8 月 20 日维修后仍经常卡纸，教务处拟申请购置一台新打印机，预算 1800 元，报学校审批。请写完整申请稿并排成 Word，落款写教务处，日期用今天。',
    'scope_word_format_only': '下面是尚未定稿的申请，我现在只要排成 Word，所有文字、数字、标点和空字段均原样保留，之后再改内容。\n\n购置打印机申请\n学校：\n教务处旧打印机经常卡纸，拟购置一台新打印机，预算1800元。请予批准。\n申请单位：教务处\n日期：____年__月__日',
    'scope_analysis_dedupe': '请改写下面的建议段，合并重复内容，把原因和可能影响讲清楚，可以结合常识展开分析。底稿：目前群众只能到现场交件，材料有误需要再次往返。建议先做线上预审，现场核验保留。线上预审有利于提前发现材料问题，减少补正往返。提前发现材料问题，可以减少群众反复到现场补材料。以上仅为建议。',
    'scope_state_unspecified': '本周收到12条设备报修登记，设备管理员负责维修联系，目前尚无处理结果。请据此写一段简短情况报告。',
    'grammar_correct_control': '请校对下面这段工作记录，给我校对后的全文：本月完成三项服务事项，形成两份报告，三台设备已检修。工作人员认真地核对了登记信息，材料整理得较为齐全。会议记录保留原话：“细节决定成败。”',
    'draft_date_missing': '学校旧打印机经常卡纸，教务处拟申请购置一台新打印机，预算1800元，报学校审批。请写完整申请稿，落款写教务处，成文日期尚待确定，先保持缺失。',
    'classified_internal_report': '请整理成一段供本部门内部流转的情况说明，并保留原有标识。标识：秘密。材料：工作组已完成两批资料目录整理，另有一批目录正在核对，调整方案尚未报批。',
    'ordinary_internal_report': '请整理成一段供本部门内部流转的情况说明。材料：工作组已完成两批资料目录整理，另有一批目录正在核对，调整方案尚未报批。',
}


def fingerprint(path: Path) -> str:
    rows = [f"{p.relative_to(path).as_posix()}:{hashlib.sha256(p.read_bytes()).hexdigest()}" for p in sorted(path.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
    return hashlib.sha256('\n'.join(rows).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    baseline = parser.add_mutually_exclusive_group()
    baseline.add_argument('--baseline-ref', default='main', help='Git baseline; a non-main ref is named baseline in artifacts.')
    baseline.add_argument('--baseline-dir', help='Explicit frozen Skill baseline; no Git commit is claimed for its contents.')
    parser.add_argument('--candidate-dir', help='Explicit frozen Skill directory for an attributable subset comparison.')
    parser.add_argument('--models', nargs='+', type=int, default=[0, 1])
    parser.add_argument('--cases', nargs='+', choices=list(CASES), default=list(CASES))
    parser.add_argument('--timeout', type=int, default=240)
    parser.add_argument('--effort', choices=['max','xhigh','high','medium'], default='max')
    parser.add_argument('--inherit-agent-docs', action='store_true', help='Retain host AGENTS.md context for an explicit harness comparison.')
    parser.add_argument('--isolated-profile', action='store_true', help='Use a temporary Codex profile with the same execution policy and the local provider proxy.')
    args = parser.parse_args()
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=False)
    runtime = Path(tempfile.mkdtemp(prefix='cow-native-'+out.name+'-'))
    eval_environment = os.environ.copy()
    if args.isolated_profile:
        eval_profile = runtime / 'codex-profile'
        eval_profile.mkdir()
        (eval_profile / 'config.toml').write_text('approval_policy = "never"\nsandbox_mode = "danger-full-access"\nproject_doc_max_bytes = 0\n[windows]\nsandbox = "unelevated"\n', encoding='utf-8')
        # Child-process profile only; use the existing local proxy's non-secret
        # placeholder key. No account credentials or global files are copied.
        eval_environment.update(CODEX_HOME=str(eval_profile), OPENAI_API_KEY='opencodex-loopback', CODEX_API_KEY='opencodex-loopback')
    binaries = Path(os.environ['LOCALAPPDATA'])/'OpenAI/Codex/bin'
    candidates = [binaries/'codex.exe', *binaries.glob('*/codex.exe')]
    cli = max(candidates, key=lambda p: tuple(int(x) for x in re.search(r'(\d+)\.(\d+)\.(\d+)', subprocess.check_output([str(p),'--version'],text=True)).groups()))
    catalog = Path.home()/'.codex/opencodex-catalog.json'
    snapshots = {}
    commit = None if args.baseline_dir else subprocess.check_output(['git','rev-parse',args.baseline_ref], cwd=ROOT, text=True).strip()
    baseline_arm = 'main' if not args.baseline_dir and args.baseline_ref == 'main' else 'baseline'
    base = out/'snapshots/main'; base.mkdir(parents=True)
    if args.baseline_dir:
        shutil.copytree(Path(args.baseline_dir).resolve(),base,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    else:
        for name in subprocess.check_output(['git','ls-tree','-r','--name-only',commit,'chinese-official-writing'], cwd=ROOT, text=True).splitlines():
            target = base/Path(name).relative_to('chinese-official-writing'); target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(subprocess.check_output(['git','show',f'{commit}:{name}'],cwd=ROOT))
    candidate = out/'snapshots/candidate'
    candidate_source = Path(args.candidate_dir).resolve() if args.candidate_dir else ROOT/'chinese-official-writing'
    shutil.copytree(candidate_source,candidate,ignore=shutil.ignore_patterns('__pycache__','*.pyc','hooks'))
    snapshots = {baseline_arm:base,'candidate':candidate}
    binding = {'main_commit':commit,'candidate_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(), 'fingerprints':{arm:fingerprint(path) for arm,path in snapshots.items()},'models':[MODELS[i] for i in args.models], 'cases':{k:CASES[k] for k in args.cases}, 'cli':str(cli),'cli_version':subprocess.check_output([str(cli),'--version'],text=True).strip(),'effort':args.effort,'runtime':str(runtime),'permissions':'inherited-host-config','timeout':args.timeout}
    binding['agent_documents'] = 'inherited' if args.inherit_agent_docs else 'project_doc_max_bytes=0'
    binding['baseline_ref'] = 'snapshot' if args.baseline_dir else args.baseline_ref
    binding['baseline_source'] = str(Path(args.baseline_dir).resolve()) if args.baseline_dir else None
    binding['candidate_source'] = str(candidate_source)
    binding['baseline_commit'] = commit
    binding['main_commit'] = subprocess.check_output(['git','rev-parse','main'],cwd=ROOT,text=True).strip()
    binding['profile'] = 'temporary-no-user-documents-or-credentials' if args.isolated_profile else 'host-profile'
    binding['runner_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    binding['prompt_prefix'] = '使用本目录 .agents/skills/chinese-official-writing/SKILL.md。\n\n'
    binding['runtime_layout'] = 'each call has a separate parent, workspace and temporary directory'
    (out/'binding.json').write_text(json.dumps(binding,ensure_ascii=False,indent=2),encoding='utf-8')

    def run_pair(index: int, case_id: str):
        results=[]
        for arm in ([baseline_arm,'candidate'] if index%2==0 else ['candidate',baseline_arm]):
            run_root=runtime/f'm{index}-{case_id}-{arm}'
            work=run_root/'workspace'; skill=work/'.agents/skills/chinese-official-writing'
            shutil.copytree(snapshots[arm],skill)
            scratch=run_root/'tmp'; scratch.mkdir()
            call_environment={**eval_environment, 'TEMP':str(scratch), 'TMP':str(scratch), 'TMPDIR':str(scratch)}
            prefix=out/f'm{index}-{case_id}-{arm}'
            final=Path(str(prefix)+'.final.txt')
            prompt='使用本目录 .agents/skills/chinese-official-writing/SKILL.md。\n\n'+CASES[case_id]
            command=[str(cli),'exec','--ephemeral','--skip-git-repo-check','-C',str(work),'-m',MODELS[index],'-c','approval_policy="never"','-c','features.plugins=false','-c','features.apps=false','-c','features.memories=false','-c','openai_base_url="http://127.0.0.1:10100/v1"','-c',f'model_catalog_json="{catalog.as_posix()}"','--json','--output-last-message',str(final),'-']
            if index != 2:
                command[-1:-1]=['-c',f'model_reasoning_effort="{args.effort}"']
            if not args.inherit_agent_docs:
                command[-1:-1]=['-c','project_doc_max_bytes=0']
            started=time.monotonic(); error=None
            print(f'START {index} {case_id} {arm}',flush=True)
            try:
                done=subprocess.run(command,input=prompt,text=True,encoding='utf-8',errors='replace',capture_output=True,timeout=args.timeout,env=call_environment,cwd=work)
                code=done.returncode;stdout=done.stdout;stderr=done.stderr
            except subprocess.TimeoutExpired as exc:
                code=None; error='timeout'
                stdout=exc.stdout or '';stderr=exc.stderr or ''
                if isinstance(stdout,bytes): stdout=stdout.decode('utf-8','replace')
                if isinstance(stderr,bytes): stderr=stderr.decode('utf-8','replace')
            Path(str(prefix)+'.trace.jsonl').write_text(stdout,encoding='utf-8')
            Path(str(prefix)+'.stderr.txt').write_text(stderr,encoding='utf-8')
            events=[]
            for line in stdout.splitlines():
                try: events.append(json.loads(line))
                except json.JSONDecodeError: pass
            calls=[x['item'] for x in events if isinstance(x.get('item'),dict) and x['item'].get('type')=='command_execution' and x.get('type')=='item.completed']
            commands=re.sub(r'/+', '/', '\n'.join(x.get('command','') for x in calls).replace('\\','/').lower())
            text=final.read_text(encoding='utf-8') if final.exists() else ''
            invalid=[]
            if code!=0 or error: invalid.append(error or f'exit_{code}')
            if not text.strip(): invalid.append('missing_final')
            bound_entry = (skill / 'SKILL.md').read_text(encoding='utf-8-sig').replace('\r\n', '\n').strip()
            entry_returned = any(
                x.get('exit_code') == 0 and bound_entry in x.get('aggregated_output', '').replace('\r\n', '\n')
                for x in calls
            )
            if 'chinese-official-writing/skill.md' not in commands and not entry_returned:
                invalid.append('missing_skill_read_trace')
            foreign=[x for x in calls if ('/.codex/skills/' in x.get('command','').replace('\\','/').lower() or '/plugins/cache/' in x.get('command','').replace('\\','/').lower())]
            if foreign: invalid.append('foreign_skill_read')
            if '开发与验证' in stdout or '所有代码和文档改动提交' in stdout or '仅保留完整 Pro 安装' in stdout:
                invalid.append('maintenance_instructions_contamination')
            result={'model':MODELS[index],'effort':args.effort if index!=2 else 'provider-default','case':case_id,'arm':arm,'returncode':code,'seconds':round(time.monotonic()-started,2),'invalid':invalid,'draft_sha256':hashlib.sha256(text.encode()).hexdigest(),'commands':calls,'usage':[x.get('usage') for x in events if x.get('type')=='turn.completed']}
            Path(str(prefix)+'.result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
            print(f'END {index} {case_id} {arm} invalid={invalid} seconds={result["seconds"]}',flush=True)
            results.append(result)
        return results

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(run_pair,i,c) for i in args.models for c in args.cases]
        results=[row for future in futures for row in future.result()]
    (out/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':
    main()
