"""Bounded isolated real-operation A/B runner for independent detail atoms."""
import concurrent.futures,hashlib,io,json,subprocess,sys,time,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
E=Path(__file__).resolve().parent
config=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
ATOM=config['atom'];OUT=ROOT/'output/detail-combined-20260910'/ATOM
legacy=Path('F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/skill-lightening-merge-check')
path='maintenance/tests/evidence/output-contract-matrix-r1/run_matrix.py'
source=subprocess.check_output(['git','show','c8058bdc:'+path],cwd=ROOT)
m=types.ModuleType('verified');m.__file__=str(legacy/path);exec(compile(source,m.__file__,'exec'),m.__dict__)
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare():
 OUT.mkdir(parents=True,exist_ok=False);hashes={}
 for arm in ['baseline','candidate']:
  rev=config[arm];names=subprocess.check_output(['git','ls-tree','-r','--name-only',rev,'--','chinese-official-writing'],cwd=ROOT).decode().splitlines()
  stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(rev+':'+n for n in names)+'\n').encode(),cwd=ROOT));hashes[arm]={}
  for name in names:
   h=stream.readline().split();data=stream.read(int(h[2]));assert stream.read(1)==b'\n';rel=Path(name).relative_to('chinese-official-writing');p=OUT/'frozen input'/arm/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);hashes[arm][rel.as_posix()]=hashlib.sha256(data).hexdigest()
 diff=sorted(n for n in hashes['baseline'].keys()|hashes['candidate'].keys() if hashes['baseline'].get(n)!=hashes['candidate'].get(n));assert diff==config['expected_diff'],diff
 catalog=json.loads(m.native.CATALOG.read_text(encoding='utf-8'))['models']
 for i,model in enumerate(m.MODELS):save(OUT/f'catalog-{i}.json',{'models':[x for x in catalog if x['slug']==model]})
 for case,c in config['cases'].items():
  if 'fixture' in c:
   p=OUT/'fixtures'/f'{case} 草稿.md';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(c['fixture'],encoding='utf-8')
 save(OUT/'freeze.json',{'config':config,'models':m.MODELS,'default_effort':'max','fallback':'high once on technical failure only','hashes':hashes,'runner_source_sha256':hashlib.sha256(source).hexdigest(),'limit':'One atom at a time; repeated outputs never replace first trials; no model calls are made for deterministic gate-only failures.'})
def one(i,case,arm,effort='max',repeat=False):
 d=OUT/'runs'/str(i)/case/arm/effort
 original=d
 if repeat:d=d/'repeat1'
 d.mkdir(parents=True,exist_ok=False)
 for sub in ['codex-home','work','temp','profile/AppData/Roaming','profile/AppData/Local']:(d/sub).mkdir(parents=True,exist_ok=True)
 (d/'codex-home/config.toml').write_text('project_doc_max_bytes = 0\n',encoding='utf-8')
 fixture=OUT/'fixtures'/f'{case} 草稿.md'
 task=config['cases'][case]['task'].replace('{fixture}',fixture.as_posix()).replace('{output_dir}',(d/'work').as_posix())
 permission='仅可读取所指Skill内的命中资料及任务给定文件；任务要求调用本Skill脚本时允许执行该脚本。不得联网，不启用Hook或插件，不修改原文件。'
 if config['cases'][case].get('docx'):
  permission+='本任务允许读取给定DOCX及所提供运行库，用该运行库编辑；仅可在本次结果目录内写脚本和新输出，不得覆盖输入。无需加载其他Skill。'
 prompt='请按以下Skill完成用户任务。先读取 '+(OUT/'frozen input'/arm/'SKILL.md').as_posix()+'。'+permission+'输出形态按用户要求。\n\n用户任务：\n'+task
 if repeat:
  assert not config['cases'][case].get('docx'), 'DOCX output directory must stay isolated; no automatic repeat'
  prompt=(original/'prompt.txt').read_bytes().decode('utf-8')
 (d/'prompt.txt').write_bytes(prompt.encode())
 cmd=[str(m.native.CLI),'exec','-m',m.MODELS[i],'-c','model_reasoning_effort="'+effort+'"','-c','openai_base_url="http://127.0.0.1:10100/v1"','-c','model_catalog_json="'+(OUT/f'catalog-{i}.json').as_posix()+'"','--dangerously-bypass-approvals-and-sandbox','--skip-git-repo-check','--json','--color','never','-o',str(d/'final.txt'),'-']
 t=time.monotonic();error=None
 with (d/'trace.jsonl').open('wb') as so,(d/'stderr.txt').open('wb') as se:
  try:r=subprocess.run(cmd,input=prompt.encode(),cwd=d/'work',env=m.native.environment(d),stdout=so,stderr=se,timeout=300);code=r.returncode
  except subprocess.TimeoutExpired:code=None;error='timeout300'
 valid=code==0 and (d/'final.txt').exists() and bool((d/'final.txt').read_text(encoding='utf-8').strip())
 rec={'provider':i,'model':m.MODELS[i],'case':case,'arm':arm,'effort':effort,'exit_code':code,'error':error,'valid_final':valid,'seconds':round(time.monotonic()-t,2),'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest()};save(d/'receipt.json',rec);print(json.dumps(rec,ensure_ascii=False),flush=True);return rec

def lane(i):
 out=[]
 for j,case in enumerate(config['assignments'][str(i)]):
  for arm in (['baseline','candidate'] if (i+j)%2==0 else ['candidate','baseline']):
   r=one(i,case,arm);out.append(r)
   if not r['valid_final']:out.append(one(i,case,arm,'high'))
 return out
if __name__=='__main__':
 prepare()
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(lane,range(5)))
 save(OUT/'receipts.json',[r for group in results for r in group])
