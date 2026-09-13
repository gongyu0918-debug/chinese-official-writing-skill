"""Freeze one actionable narration-page repair without changing other genres."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / 'output/final-main-r24/candidate'
OUT = ROOT / 'output/narration-grounding-r25'


def files(path):
    return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(path.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}


before = files(SOURCE)
assert hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest() == '345271e65f29f3f055026102f8ef29fbb26bee2bca6fcce57ca524f6a448909d'
assert not OUT.exists()
shutil.copytree(SOURCE, OUT / 'candidate', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
shutil.copyfile(HERE / 'candidate-narration.md', OUT / 'candidate/references/genre-playbook-narration.md')
after = files(OUT / 'candidate')
changed = [p for p, h in after.items() if h != before[p]]
assert changed == ['references/genre-playbook-narration.md']
record = {'baseline_commit': '1ce7112303172478faa2392667a2de1098eb912c', 'before': before, 'candidate': after,
          'changed_from_r24': changed, 'fingerprint': hashlib.sha256(json.dumps(after, sort_keys=True).encode()).hexdigest()}
(OUT / 'build.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'fingerprint': record['fingerprint'], 'changed': changed}, ensure_ascii=False))
