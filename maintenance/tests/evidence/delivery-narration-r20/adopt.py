"""Adopt the exact native-tested R20 entry and delivery pages locally."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
EXPERIMENT = ROOT / 'output/delivery-narration-r20-final'
FROZEN = ROOT / 'output/delivery-narration-r20-adopted'
build = json.loads((EXPERIMENT / 'build.json').read_text(encoding='utf-8'))
decision = json.loads((HERE / 'decision.json').read_text(encoding='utf-8'))
assert decision['status'] == 'adopt-development-only'
assert decision['candidate_fingerprint'] == build['fingerprints']['candidate']
assert not FROZEN.exists()
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip() == 'codex/reference-rewrite-20260912'

def files(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}

canonical = ROOT / 'chinese-official-writing'
assert files(canonical) == build['files']['baseline']
assert files(EXPERIMENT / 'candidate') == build['files']['candidate']
relatives = decision['changed']
targets = [canonical] + [ROOT/'packages'/pkg/'skills'/name for pkg,name in [
    ('agent-skills','chinese-official-writing'),('hermes','chinese-official-writing'),
    ('qwen-code','chinese-official-writing'),('qwenwork','chinese-official-writing'),
    ('openclaw','chinese_official_writing')]]
before = {str(r.relative_to(ROOT)):files(r) for r in targets}
for root in targets:
    assert root.resolve().is_relative_to(ROOT.resolve())
    for relative in relatives:
        path = root/relative
        assert not subprocess.check_output(['git','status','--porcelain','--',path.relative_to(ROOT).as_posix()],cwd=ROOT,text=True).strip()
        if relative=='SKILL.md' and root.name=='chinese_official_writing':
            assert path.read_text(encoding='utf-8').split('---',2)[2] == (canonical/relative).read_text(encoding='utf-8').split('---',2)[2]
        else:
            assert hashlib.sha256(path.read_bytes()).hexdigest() == build['files']['baseline'][relative]
for root in targets:
    for relative in relatives:
        (root/relative).write_bytes((EXPERIMENT/'candidate'/relative).read_bytes())
spec = importlib.util.spec_from_file_location('sync_adapters', ROOT/'maintenance/tools/sync_adapters.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.patch_openclaw_frontmatter(targets[-1])
after = {str(r.relative_to(ROOT)):files(r) for r in targets}
for key in before:
    assert set(before[key]) == set(after[key])
    assert {p for p in before[key] if before[key][p] != after[key][p]} == set(relatives)
assert files(canonical) == build['files']['candidate']
for root in targets:
    assert (root/'references/writing-rules.md').read_bytes() == (canonical/'references/writing-rules.md').read_bytes()
    assert (root/'SKILL.md').read_text(encoding='utf-8').split('---',2)[2] == (canonical/'SKILL.md').read_text(encoding='utf-8').split('---',2)[2]
shutil.copytree(canonical,FROZEN/'candidate',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
record = {'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          'main_unchanged':subprocess.check_output(['git','rev-parse','main'],cwd=ROOT,text=True).strip(),
          'fingerprint':build['fingerprints']['candidate'],'files':files(canonical),
          'changed':relatives,'mirror_count':5,'mirror_changed_files':{k:{p:after[k][p] for p in relatives} for k in after},
          'decision_sha256':hashlib.sha256((HERE/'decision.json').read_bytes()).hexdigest(),
          'scope':decision['scope']}
(FROZEN/'adoption.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:record[k] for k in ['fingerprint','changed','mirror_count','scope']},ensure_ascii=False))
