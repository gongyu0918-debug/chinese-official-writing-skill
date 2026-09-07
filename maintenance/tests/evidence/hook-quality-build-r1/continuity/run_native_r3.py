"""Five ordinary requests in one persistent native Claude session."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('native_environment', ROOT / 'maintenance/tests/evidence/v167-formulaic-mechanicality-real-first/harness.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
model = 'alibaba-token-plan-2/deepseek-v4-flash-0731'
runtime = OUT / 'native-r3-production'
assert not runtime.exists()
environment = base.build_environment(model, runtime)
environment['COW_EXPERIMENT_EVENTS'] = str(runtime / 'events')
companion = OUT / 'companion-production'
cases = json.loads((ROOT / 'maintenance/tests/evidence/natural-writing-stability-r1/cases.json').read_text(encoding='utf-8'))['cases'][0]['rounds']
cases += [{'round':6,'prompt':'请再调整刚才报告的表达，删掉不必要的铺垫和重复，保留最新事实、职责及未决状态，700字以内，只输出完整正文。'}, {'round':7,'prompt':'以刚才这版为底稿，再把下一步考虑改得更简洁一些，不把建议写成已经作出的决定。其他部分保留，给我700字以内的完整正文。'}]
session = str(uuid.uuid4())
records = []
for case in cases:
    number = case['round']
    directory = runtime / f'round-{number}'
    directory.mkdir()
    cmd = [shutil.which('claude'), '--setting-sources', '', '--tools', 'Read,Skill', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
           '--permission-mode', 'dontAsk', '--include-hook-events', '--print', '--verbose', '--output-format', 'stream-json',
           '--model', model, '--effort', 'max', '--plugin-dir', str(companion), '--add-dir', str(companion),
           *( ['--session-id',session] if number == 1 else ['--resume',session])]
    (directory/'invocation.json').write_text(json.dumps({'argv':cmd,'prompt':case['prompt'],'session':session},ensure_ascii=False,indent=2),encoding='utf-8')
    started=time.monotonic()
    with (directory/'stream.jsonl').open('w',encoding='utf-8') as stdout, (directory/'stderr.txt').open('w',encoding='utf-8') as stderr:
        result=subprocess.run(cmd,input=case['prompt'],cwd=runtime/'work',env=environment,text=True,encoding='utf-8',stdout=stdout,stderr=stderr,timeout=900)
    events=[json.loads(l) for l in (directory/'stream.jsonl').read_text(encoding='utf-8').splitlines()]
    terminal=[e for e in events if e.get('type')=='result']
    final=terminal[-1].get('result','') if terminal else ''
    (directory/'final.txt').write_text(final,encoding='utf-8')
    record={'round':number,'exit_code':result.returncode,'seconds':round(time.monotonic()-started,2),'session':session,'result_subtype':terminal[-1].get('subtype') if terminal else None,'final_chars':len(final)}
    records.append(record)
    (runtime/'result.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    print(json.dumps(record),flush=True)
    if result.returncode or not final or any(e.get('subtype') == 'hook_response' and e.get('exit_code', 0) != 0 for e in events):break
