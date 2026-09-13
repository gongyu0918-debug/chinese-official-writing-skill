"""Freeze the three concrete cold-review fixes as a complete Skill."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'output/reference-integration-r16-rule-refinement/candidate'
SCRIPT = ROOT / 'output/prose-inline-r16/candidate/scripts/prose_lint.py'
DEST = ROOT / 'output/reference-integration-r16-final/candidate'
assert not DEST.exists()
assert hashlib.sha256(SCRIPT.read_bytes()).hexdigest() == '513934d60e145087d992b2383dc92a522ecd9497446194ce1885e937800486fc'
shutil.copytree(SOURCE, DEST, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
(DEST / 'scripts/prose_lint.py').write_bytes(SCRIPT.read_bytes())
def files(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
base = files(ROOT / 'output/reference-integration-r16/candidate')
after = files(DEST)
changed = sorted(k for k in base if base[k] != after[k])
assert changed == ['references/compression-details.md', 'references/genre-playbook-news-commentary.md', 'scripts/prose_lint.py']
record = {'changed_from_cold_snapshot': changed, 'files': after, 'fingerprint': hashlib.sha256(json.dumps(after, sort_keys=True).encode()).hexdigest(), 'script_source': str(SCRIPT)}
(DEST.parent/'build.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({k:record[k] for k in ['changed_from_cold_snapshot','fingerprint']}))
