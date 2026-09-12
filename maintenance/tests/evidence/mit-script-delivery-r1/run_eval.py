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
    parser.add_argument('--baseline-ref', default='main', help='Git baseline; a non-main ref is named baseline in artifacts.')
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
    commit = subprocess.check_output(['git','rev-parse',args.baseline_ref], cwd=ROOT, text=True).strip()
    baseline_arm = 'main' if args.baseline_ref == 'main' else 'baseline'
    base = out/'snapshots/main'; base.mkdir(parents=True)
    for name in subprocess.check_output(['git','ls-tree','-r','--name-only',commit,'chinese-official-writing'], cwd=ROOT, text=True).splitlines():
        target = base/Path(name).relative_to('chinese-official-writing'); target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(subprocess.check_output(['git','show',f'{commit}:{name}'],cwd=ROOT))
    candidate = out/'snapshots/candidate'
    candidate_source = Path(args.candidate_dir).resolve() if args.candidate_dir else ROOT/'chinese-official-writing'
    shutil.copytree(candidate_source,candidate,ignore=shutil.ignore_patterns('__pycache__','*.pyc','hooks'))
    snapshots = {baseline_arm:base,'candidate':candidate}
    binding = {'main_commit':commit,'candidate_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(), 'fingerprints':{arm:fingerprint(path) for arm,path in snapshots.items()},'models':[MODELS[i] for i in args.models], 'cases':{k:CASES[k] for k in args.cases}, 'cli':str(cli),'cli_version':subprocess.check_output([str(cli),'--version'],text=True).strip(),'effort':args.effort,'runtime':str(runtime),'permissions':'inherited-host-config','timeout':args.timeout}
    binding['agent_documents'] = 'inherited' if args.inherit_agent_docs else 'project_doc_max_bytes=0'
    binding['baseline_ref'] = args.baseline_ref
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
