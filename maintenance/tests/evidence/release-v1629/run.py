import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PY = 'C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe'

def run(name, command, timeout=600):
    started = time.time()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, encoding='utf-8', errors='replace', timeout=timeout)
    record = dict(command=command, exit_code=result.returncode, seconds=round(time.time()-started,3), stdout=result.stdout, stderr=result.stderr)
    (OUT / (name+'.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(name=name,exit_code=result.returncode,seconds=record['seconds'],tail=(result.stdout+result.stderr)[-2200:]),ensure_ascii=False))
    return result.returncode

def version():
    files = subprocess.check_output(['git','show','--format=','--name-only','1d705aea','--',':!maintenance/tests/evidence'],cwd=ROOT,text=True).splitlines()
    for name in filter(None,files):
        path=ROOT/name
        text=path.read_text(encoding='utf-8')
        assert '1.6.28' in text,name
        path.write_text(text.replace('1.6.28','1.6.29'),encoding='utf-8')
    spec=importlib.util.spec_from_file_location('release_sync',ROOT/'maintenance/tools/sync_adapters.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    checked=[]
    for path in module.TARGETS.values():
        resolved=path.resolve()
        assert resolved.is_relative_to((ROOT/'packages').resolve())
        assert not path.is_symlink() and not any(p.is_symlink() for p in path.rglob('*'))
        untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard','--',str(path)],cwd=ROOT,text=True)
        assert not untracked.strip(),untracked
        checked.append(str(resolved))
    (OUT/'sync-target-preflight.json').write_text(json.dumps(checked,indent=2)+'\n',encoding='utf-8')
    module.main()

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='version':version()
    elif mode=='full':sys.exit(run('full-tests',[PY,'-B','-X','utf8','-m','unittest','discover','-s','maintenance/tests','-p','test_*.py']))
    elif mode=='quick':
        dirs=['chinese-official-writing']+[f'packages/{x}/skills/chinese-official-writing' for x in ['agent-skills','qwen-code','qwenwork','hermes']]
        sys.exit(max(run('quick-'+str(i),[PY,'-B','-X','utf8','C:/Users/admin/.codex/skills/.system/skill-creator/scripts/quick_validate.py',p]) for i,p in enumerate(dirs)))
    elif mode=='command':sys.exit(run(sys.argv[2],sys.argv[3:]))
