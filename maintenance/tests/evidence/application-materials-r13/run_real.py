"""Natural application prompts in isolated cheap-model Claude sessions; no Hook."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import time
import uuid

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'output/application-materials-r13'
BASELINE = 'bb3eae9d69216f149737a00fd1126813cc7ef724'
MODELS = {'alibaba2':'alibaba-token-plan-2/deepseek-v4-flash-0731', 'minimax':'minimax-cn/MiniMax-M3'}
HELPER = ROOT / 'maintenance/tests/evidence/v167-formulaic-mechanicality-real-first/harness.py'
spec = importlib.util.spec_from_file_location('application_env', HELPER)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def freeze(arm):
    plugin=OUT/'plugins'/arm
    plugin.mkdir(parents=True,exist_ok=False)
    save(plugin/'.claude-plugin/plugin.json',{'name':'official-writing-eval','version':'1.0.0','description':'中文公文写作测试副本'})
    target=plugin/'skills/chinese-official-writing'
    paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASELINE,'--','chinese-official-writing'],cwd=ROOT,text=True).splitlines()
    manifest=[]
    for name in paths:
        rel=Path(name).relative_to('chinese-official-writing')
        if 'hooks' in rel.parts:continue
        data=(subprocess.check_output(['git','show',BASELINE+':'+name],cwd=ROOT) if arm=='baseline' else (ROOT/name).read_bytes().replace(b'\r\n',b'\n'))
        p=target/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        manifest.append({'path':rel.as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    save(OUT/(arm+'-manifest.json'),manifest)
    print(json.dumps({'frozen':arm,'files':len(manifest)}),flush=True)

def run(arm,provider,case,client_tools='Read,Skill,Write,Edit,Bash',explicit_entry=True):
    lane=OUT/'runs'/case/provider/arm
    lane.mkdir(parents=True,exist_ok=False)
    prompt=(OUT/'prompts'/(case+'.txt')).read_text(encoding='utf-8')
    plugin=OUT/'plugins'/arm
    assert plugin.exists()
    expected=json.loads((OUT/(arm+'-manifest.json')).read_text(encoding='utf-8'))
    assert all(hashlib.sha256((plugin/'skills/chinese-official-writing'/x['path']).read_bytes()).hexdigest()==x['sha256'] for x in expected)
    model=MODELS[provider];runtime=lane/'runtime'
    env=base.build_environment(model,runtime)
    session=str(uuid.uuid4())
    cmd=[shutil.which('claude'),'--setting-sources','','--no-session-persistence','--tools',client_tools,'--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--permission-mode','dontAsk','--print','--verbose','--output-format','stream-json','--model',model,'--effort','max','--plugin-dir',str(plugin),'--add-dir',str(plugin),'--session-id',session]
    context = []
    if client_tools != 'Read,Skill':
        cmd += ['--allowedTools',client_tools]
        context.append('这是隔离写稿会话。只读本次插件目录及当前工作目录；临时稿件和检查结果只写当前工作目录。不联网，不读取其他Skill或用户文件。')
    if explicit_entry:
        entry = plugin/'skills/chinese-official-writing/SKILL.md'
        context.append(f'本次可用公文写作Skill的入口为：{entry}。用户要求使用该Skill时，请先读取此入口，再按入口自行选择所需资料。')
    if context:
        cmd += ['--append-system-prompt','\n'.join(context)]
    save(lane/'invocation.json',{'argv':cmd,'prompt':prompt,'session':session,'helper_sha256':hashlib.sha256(HELPER.read_bytes()).hexdigest(),'hook_enabled':False})
    started=time.monotonic();code=None;failure=None
    with (lane/'stream.jsonl').open('w',encoding='utf-8') as stdout,(lane/'stderr.txt').open('w',encoding='utf-8') as stderr:
        try:code=subprocess.run(cmd,input=prompt,cwd=runtime/'work',env=env,text=True,encoding='utf-8',stdout=stdout,stderr=stderr,timeout=480).returncode
        except (subprocess.TimeoutExpired,OSError) as exc:failure=type(exc).__name__
    parsed=base.parse_stream(lane/'stream.jsonl');final=parsed.pop('final');events=[]
    for line in (lane/'stream.jsonl').read_text(encoding='utf-8').splitlines():
        try:events.append(json.loads(line))
        except json.JSONDecodeError:pass
    uses=[b for e in events for b in (e.get('message') or {}).get('content',[]) if isinstance(b,dict) and b.get('type')=='tool_use']
    reads=[b.get('input',{}).get('file_path') for b in uses if b.get('name')=='Read']
    frozen_unchanged=all((plugin/'skills/chinese-official-writing'/x['path']).is_file() and hashlib.sha256((plugin/'skills/chinese-official-writing'/x['path']).read_bytes()).hexdigest()==x['sha256'] for x in expected)
    valid=(code==0 and bool(final.strip()) and frozen_unchanged and parsed['result_count']==1 and parsed['result_subtypes']==['success'] and parsed['result_errors']==[False] and not parsed['invalid_json_lines'] and all(parsed[k]==[model] for k in ['init_models','assistant_models','usage_models']))
    record={'arm':arm,'provider':provider,'model':model,'case':case,'session':session,'technical_valid':valid,'return_code':code,'failure':failure,'seconds':round(time.monotonic()-started,2),'reads':reads,'tool_uses':uses,'client_tools':client_tools,'explicit_entry':explicit_entry,'frozen_unchanged':frozen_unchanged,'final_sha256':hashlib.sha256(final.encode()).hexdigest(),'final_chars':len(final),**parsed}
    (lane/'final.txt').write_text(final,encoding='utf-8');save(lane/'receipt.json',record)
    print(json.dumps({k:record[k] for k in ['arm','provider','case','technical_valid','failure','seconds','final_chars','reads']},ensure_ascii=False),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','run']);p.add_argument('arm',choices=['baseline','candidate','candidate-r14','candidate-r15','candidate-r16']);p.add_argument('--provider',choices=MODELS);p.add_argument('--case',default='first-draft');a=p.parse_args()
    freeze(a.arm) if a.action=='freeze' else run(a.arm,a.provider,a.case)
