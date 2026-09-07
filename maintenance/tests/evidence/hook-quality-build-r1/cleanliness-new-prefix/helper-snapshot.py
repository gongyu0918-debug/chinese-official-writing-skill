"""Five frozen same-D0 cleanliness chains, existing no-tool cheap Claude CLI."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
REAL_PATH=ROOT/'maintenance/tests/evidence/date-source-real-r1/run.py'
RUNTIME_PATH=ROOT/'chinese-official-writing/hooks/capabilities/delivery_cleanliness/runtime.py'
MODELS={'alibaba2':'alibaba-token-plan-2/deepseek-v4-flash-0731','minimax':'minimax-cn/MiniMax-M3'}
PACKETS={'P6':('report-fourth-packet.json','3127a9501441b66a585be4f3ddcb811a61ea3de1f5f6357dd8baa813be4c4124'),
         'M6':('minutes-third-packet.json','e203b8981e83ed9e7f81236ed9b3c3a2f4f9a89d62abbe426f3c6dd82e4b5178')}

def sha(value):return hashlib.sha256(value).hexdigest()
def text_sha(value):return sha(value.encode('utf-8'))
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def save(path,value):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def prepare():
 if (HERE/'fixture.json').exists():raise RuntimeError('Preserve existing preregistration')
 sources={};cases=[]
 for name,(filename,expected) in PACKETS.items():
  path=ROOT/'maintenance/tests/evidence/natural-writing-stability-r1/raw/r2'/filename
  assert sha(path.read_bytes())==expected
  chain=read(path)['chains'][0];row=chain['rounds'][-1]
  assert chain['id']==name and row['round']==5 and text_sha(row['text'])==row['sha256']
  pieces=row['text'].split('\n\n---\n\n');assert len(pieces)==3
  cases.append({'id':name,'provider':'alibaba2' if name=='P6' else 'minimax','kind':'original_real_request_and_reply_pair_hook_off_source',
   'source':str(path.relative_to(ROOT)),'source_sha256':expected,'request':row['prompt'],'d0':row['text'],
   'expected':pieces[1],'body':pieces[1],'expected_method':'Observed middle body, test oracle only; never injected as model candidate/verdict.'})
 controls_path=ROOT/'maintenance/tests/evidence/delivery-cleanliness-real-first/cases.json'
 controls={c['id']:c for c in read(controls_path)['cases']}
 for name in ['C4','C5']:
  c=controls[name];draft='\n'.join(c['draft_lines'])
  cases.append({'id':name,'provider':'alibaba2','kind':'historical_frozen_clean_or_requested_markdown_control',
   'source':str(controls_path.relative_to(ROOT)),'source_sha256':sha(controls_path.read_bytes()),
   'request':c['request'],'d0':draft,'expected':draft,'body':draft,'expected_method':'Existing fixed preservation control, not fresh natural generation.'})
 original=cases[0]
 cases.append({'id':'C6','provider':'minimax','kind':'explicit_explanation_request_variant_on_real_P6_D0',
  'source':original['source'],'source_sha256':original['source_sha256'],
  'request':'请原样保留这份完整报告，包括前导语、横线分隔和末尾的字数统计、改动说明。正文及说明都不修改，直接返回全文。',
  'original_source_request':original['request'],'d0':original['d0'],'expected':original['d0'],'body':original['body'],
  'expected_method':'Request variant explicitly preserves all wrappers; not original natural request/reply pairing.'})
 for c in cases:
  for field in ['request','d0','expected','body']:c[field+'_sha256']=text_sha(c[field])
 for path in [Path(__file__),REAL_PATH,ROOT/'maintenance/tests/evidence/hook-audit-quality-r1/replay_real_d0.py',ROOT/'maintenance/tests/evidence/v167-formulaic-mechanicality-real-first/harness.py',RUNTIME_PATH]:
  sources[str(path.relative_to(ROOT))]=sha(path.read_bytes())
 snapshot=HERE/'runtime-baseline.py';snapshot.write_bytes(RUNTIME_PATH.read_bytes())
 fixture={'schema_version':1,'base_commit':'b77f6381438c8fa01f8576c205d13af4b8a987fd','models':MODELS,'effort':'max','model_retry_budget':0,
  'call_timeout_seconds':180,'max_continuations_per_case':4,'snapshot_sha256':sha(snapshot.read_bytes()),'source_sha256':sources,'cases':cases,
  'plan':'Run baseline existing runtime first. Feed runtime reason verbatim to a new real Claude CLI session for each revision/verdict/echo. No synthetic D1/PASS, no automatic retries or provider substitution. Five chains independent; phase sessions are fresh and isolated, not a persisted host conversation. Do not install/enable Hook or change core. Existing source D0 controls remain exact.',
  'acceptance':'P6/M6 final must equal expected body exactly; all3 controls final equal D0. Model,empty tool/skill/plugin/MCP inventories,one result,selection/hash/final delivery verified separately. Existing body errors not claimed fixed.',
  'engineering_gate':'Only after real target risk is reduced without control regression, consider a minimal runtime helper/prompt change or advise root on default integration. No added host matrix.'}
 save(HERE/'fixture.json',fixture)
 return {'fixture_sha256':sha((HERE/'fixture.json').read_bytes()),'cases':[c['id'] for c in cases],'max_normal_calls':12}

def run_case(case,fixture,real,claude):
 out=HERE/'r1'/case['id'];out.mkdir(parents=True,exist_ok=False)
 runtime=load('clean_runtime_'+case['id'],HERE/'runtime-baseline.py')
 record={'request':case['request']};save(out/'input.json',case)
 response=runtime.start({'last_assistant_message':case['d0']},record)
 events=[{'index':0,'actual_model_reply':False,'response':response,'state':copy.deepcopy(record)}];calls=[];current=case['d0'];status='pending'
 print(json.dumps({'case':case['id'],'provider':case['provider'],'status':'START'}),flush=True)
 for index in range(1,fixture['max_continuations_per_case']+1):
  if response is None or response.get('decision')!='block':break
  phase=record.get('delivery_cleanliness',{}).get('phase')
  callout=out/'calls'/str(index)
  command=real.command(claude,fixture['models'][case['provider']])
  save(out/f'invocation-{index}.json',{'argv':command,'phase':phase,'cwd':str(callout/'runtime/work'),
   'prompt_sha256':text_sha(response['reason']),'model':fixture['models'][case['provider']],'effort':'max',
   'isolation':'existing per-call isolated HOME/USERPROFILE/CLAUDE_CONFIG_DIR; no tools,Skills,plugins,MCP; dummy local gateway auth only; environment values omitted'})
  try:
   current,receipt=real.restricted_reply(fixture['models'][case['provider']],response['reason'],callout,claude)
  except Exception as exc:
   status='technical_failure_no_retry';save(out/'failure.json',{'exception_type':type(exc).__name__,'index':index,'phase':phase});break
  stream=[json.loads(s) for s in (callout/'stream.jsonl').read_text(encoding='utf-8').splitlines()]
  ids=sorted({e['session_id'] for e in stream if isinstance(e.get('session_id'),str)})
  calls.append({'index':index,'phase':phase,'session_ids':ids,'reply_sha256':text_sha(current),'receipt':receipt})
  response=runtime.advance({'last_assistant_message':current},record)
  events.append({'index':index,'actual_model_reply':True,'model_reply_sha256':text_sha(current),'response':response,'state':copy.deepcopy(record)})
  save(out/'events.json',events);save(out/'calls.json',calls)
  print(json.dumps({'case':case['id'],'call':index,'phase':phase,'next_phase':record['delivery_cleanliness'].get('phase'),'selection':record['delivery_cleanliness'].get('audit',{}).get('selection'),'technical_valid':receipt['technical_valid']}),flush=True)
 if status=='pending':status='finished' if response and response.get('decision')!='block' else 'wrapper_ceiling_no_retry'
 state=record.get('delivery_cleanliness',{});audit=state.get('audit',{})
 visible=current if status=='finished' else None
 result={'id':case['id'],'kind':case['kind'],'provider':case['provider'],'status':status,'source_request_sha256':case['request_sha256'],
  'original_sha256':case['d0_sha256'],'expected_sha256':case['expected_sha256'],'selected_sha256':record.get('delivery_cleanliness_selected_sha256'),
  'final_visible_sha256':text_sha(visible) if visible is not None else None,'selected_matches_visible':visible is not None and text_sha(visible)==record.get('delivery_cleanliness_selected_sha256'),
  'body_exactly_retained':visible is not None and case['body'] in visible,'expected_exact':visible==case['expected'],'original_unchanged':visible==case['d0'],
  'counts_nonspace':{k:len(''.join(v.split())) for k,v in [('original',case['d0']),('expected',case['expected']),('visible',visible or '')]},
  'audit':audit,'phase':state.get('phase'),'last_response':response,'calls':calls,'call_count':len(calls),'actual_native_hook_run':False,
  'result_kind':'real model revision/verdict/echo through exact existing runtime; no core/native event lifecycle',
  'functional_pass':status=='finished' and visible==case['expected'] and audit.get('delivery_verified') is True}
 save(out/'result.json',result);save(out/'events.json',events)
 (out/'last-assistant.txt').write_text(current,encoding='utf-8',newline='\n')
 if visible is not None:(out/'final-visible.txt').write_text(visible,encoding='utf-8',newline='\n')
 print(json.dumps({'case':case['id'],'status':status,'functional_pass':result['functional_pass'],'calls':len(calls)}),flush=True)
 return result

def run():
 fixture=read(HERE/'fixture.json');assert sha((HERE/'runtime-baseline.py').read_bytes())==fixture['snapshot_sha256']
 for path,expected in fixture['source_sha256'].items():
  if path.endswith('/runtime.py'):continue
  assert sha((ROOT/path).read_bytes())==expected,path
 if (HERE/'r1').exists():raise RuntimeError('Use a new preregistered run, never overwrite r1')
 claude=shutil.which('claude');assert claude
 real=load('clean_real_cli',REAL_PATH)
 save(HERE/'preflight.json',{'fixture_sha256':sha((HERE/'fixture.json').read_bytes()),'claude_version':subprocess.check_output([claude,'--version'],text=True).strip(),'cli':claude,'models':fixture['models'],'no_install':True})
 def lane(provider):return [run_case(c,fixture,real,claude) for c in fixture['cases'] if c['provider']==provider]
 with ThreadPoolExecutor(max_workers=2) as pool:results=[r for lane_results in pool.map(lane,fixture['models']) for r in lane_results]
 summary={'schema_version':1,'cases':results,'all_functional_pass':all(r['functional_pass'] for r in results),'model_calls':sum(r['call_count'] for r in results),'fixture_sha256':sha((HERE/'fixture.json').read_bytes()),'runtime_sha256':fixture['snapshot_sha256']}
 save(HERE/'r1/summary.json',summary)
 return {'all_functional_pass':summary['all_functional_pass'],'model_calls':summary['model_calls'],'cases':[{k:r[k] for k in ['id','functional_pass','call_count','final_visible_sha256']} for r in results]}

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);actions=parser.add_mutually_exclusive_group(required=True);actions.add_argument('--prepare',action='store_true');actions.add_argument('--run',action='store_true');args=parser.parse_args()
 print(json.dumps(prepare() if args.prepare else run(),ensure_ascii=False,indent=2),flush=True)
