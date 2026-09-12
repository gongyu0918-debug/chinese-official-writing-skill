"""Preserve the completed R7/R8 exploratory calls, not later combined runs."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RUNS = [
    'legacy-common-guards-native-r7', 'common-guard-controls-repeat-r7',
    'three-leaf-refine-native-r7', 'route-overlap-native-r7-qwen-deep',
    'route-overlap-native-r7-minimax', 'common-state-scope-native-r7-glm',
    'common-grammar-refine-native-r8', 'common-state-stress-native-r7',
]
DIRECTORIES = RUNS + [
    'legacy-common-guards-r7', 'common-guards-refine-r8', 'three-leaf-refine-r7',
    'technical-requirements-refine-r7', 'narration-letter-refine-r7',
    'route-overlap-refine-r7', 'common-state-scope-refine-r7',
    'legacy-common-guards-blind-r7', 'r7-complete-output-blind', 'route-overlap-blind-r7',
]
EXTRA = [
    'inference-calibration-r7.md', 'route-overlap-audit-r7.md',
    'common-scope-conflicts-r7.md', 'r7-last-batches-execution.md',
    'r7-last-batches-execution.json', 'r7-last-batches-execution.sha256',
]
target = Path('F:/Workspaces/chinese-official-writing-skill-archives/experiments/reference-rewrite-20260913-r7/native-writing-batch-d.zip')
assert not target.exists(), 'Refuse to replace an existing archive'
paths = set()
for name in DIRECTORIES:
    folder = ROOT / 'output' / name
    assert folder.is_dir(), folder
    paths.update(p for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
for name in EXTRA:
    p = ROOT / 'output' / name
    assert p.is_file(), p
    paths.add(p)
calls = []
for name in RUNS:
    folder = ROOT / 'output' / name
    for row in json.loads((folder / 'results.json').read_text(encoding='utf-8')):
        calls.append({'run': name, **{k:v for k,v in row.items() if k != 'commands'}})
assert len(calls) == 86
assert sum(not r['invalid'] for r in calls) == 83
for p in paths:
    assert p.name.lower() not in {'auth.json', 'credentials.json', '.env', 'config.toml'}
target.parent.mkdir(parents=True, exist_ok=True)
manifest = []
with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED) as z:
    for p in sorted(paths):
        raw = p.read_bytes()
        rel = p.relative_to(ROOT).as_posix()
        z.writestr(rel, raw)
        manifest.append({'path': rel, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    z.writestr('MANIFEST.json', json.dumps(manifest, ensure_ascii=False, indent=2))
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    entries = len(z.infolist())
record = {'archive': str(target), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
          'bytes': target.stat().st_size, 'entries': entries, 'crc': 'PASS',
          'calls': len(calls), 'technical_valid': 83, 'runs': RUNS,
          'note': 'Hash after ZIP close. Full per-entry hashes are in MANIFEST.json. Technical validity is not writing acceptance.'}
(HERE / 'archive.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
(HERE / 'calls.json').write_text(json.dumps(calls, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(record, ensure_ascii=False))
