"""Freeze the motion-only prototype against the adopted R20 package."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'output/motion-content-r23'
SOURCE = ROOT / 'output/delivery-narration-r20-adopted/candidate'


def files(path):
    return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(path.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}


before = files(SOURCE)
assert hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest() == 'a8f2f4694450e790bcc7129447f0ccac32cf5ef2bf227e7852604d714dfcddb5'
assert not OUT.exists()
for arm in ['baseline', 'candidate']:
    shutil.copytree(SOURCE, OUT / arm)
shutil.copyfile(HERE / 'candidate-motion.md', OUT / 'candidate/references/genre-playbook-motion.md')
after = files(OUT / 'candidate')
changed = [p for p, h in after.items() if h != before[p]]
assert changed == ['references/genre-playbook-motion.md']
record = {'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
          'changed': changed, 'files': {'baseline': before, 'candidate': after},
          'fingerprints': {a: hashlib.sha256(json.dumps(v, sort_keys=True).encode()).hexdigest()
                           for a, v in [('baseline', before), ('candidate', after)]}}
(OUT / 'build.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in record.items() if k != 'files'}, ensure_ascii=False))
