"""Preserve all completed R12/R13 calls, candidates, audits and anonymous reviews."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RUNS = ['common-layer-native-r12-unified', 'common-layer-native-r12-coverage', 'common-layer-native-r12-retry', 'common-layer-native-r13-index', 'common-layer-native-r13-quantifier-repeat']
DIRS = RUNS + ['common-layer-unified-r12', 'common-layer-index-r13', 'common-layer-blind-r12']
EXTRA = ['common-layer-companions-audit-r13.md', 'common-layer-index-stop-audit-r13.md']
TARGET = Path('F:/Workspaces/chinese-official-writing-skill-archives/experiments/reference-rewrite-20260913-common-layer/native-writing-batch-f.zip')
assert not TARGET.exists()
calls=[]
paths=set()
for name in RUNS:
    for row in json.loads((ROOT/'output'/name/'results.json').read_text(encoding='utf-8-sig')):
        calls.append({'run':name,**{k:v for k,v in row.items() if k!='commands'}})
for name in DIRS:
    paths.update(p for p in (ROOT/'output'/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
paths.update(ROOT/'output'/name for name in EXTRA)
assert len(calls)==40 and sum(not r['invalid'] for r in calls)==39
for p in paths:assert p.name.lower() not in {'auth.json','credentials.json','.env','config.toml'}
TARGET.parent.mkdir(parents=True,exist_ok=True)
manifest=[]
with zipfile.ZipFile(TARGET,'x',compression=zipfile.ZIP_DEFLATED) as z:
    for p in sorted(paths):
        data=p.read_bytes();name=p.relative_to(ROOT).as_posix()
        z.writestr(name,data)
        manifest.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    z.writestr('MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2))
with zipfile.ZipFile(TARGET) as z:
    assert z.testzip() is None
    entries=len(z.infolist())
record={'archive':str(TARGET),'sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest(),'bytes':TARGET.stat().st_size,'entries':entries,'crc':'PASS','calls':len(calls),'technical_valid':sum(not r['invalid'] for r in calls),'runs':RUNS,'note':'Technical completion is not quality acceptance. Original timeout and its unmatched candidate remain preserved; retry uses both newly generated arms. R13 repeated quantifier pair does not replace the first pair.'}
(HERE/'archive-f.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(HERE/'calls-f.json').write_text(json.dumps(calls,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
