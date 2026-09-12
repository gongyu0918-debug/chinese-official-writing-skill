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
    (out/'binding.json').write_text(json.dumps(binding,ensure_ascii=False,indent=2),encoding='utf-8')

    def run_pair(index: int, case_id: str):
        results=[]
        for arm in ([baseline_arm,'candidate'] if index%2==0 else ['candidate',baseline_arm]):
            work=runtime/f'm{index}-{case_id}-{arm}'; skill=work/'.agents/skills/chinese-official-writing'
            shutil.copytree(snapshots[arm],skill)
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
                done=subprocess.run(command,input=prompt,text=True,encoding='utf-8',errors='replace',capture_output=True,timeout=args.timeout,env=eval_environment)
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
            if 'chinese-official-writing/skill.md' not in commands: invalid.append('missing_skill_read_trace')
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
