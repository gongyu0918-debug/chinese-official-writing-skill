"""Archive all R21/R22 variants and native evidence without profile credentials."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RUNS = {
    'independent-review-native-r21-qwen': 4,
    'independent-review-native-r21-deepseek': 4,
    'independent-review-native-r21-complete-qwen': 2,
    'independent-review-native-r21-complete-deepseek': 2,
    'independent-review-native-r21-routed-deepseek': 2,
    'independent-review-native-r21-routed-glm': 2,
    'independent-review-native-r21-explicit-deepseek': 2,
    'delivery-cleanup-native-r22-deepseek': 4,
    'delivery-cleanup-native-r22-qwen': 4,
}
DIRECTORIES = [*RUNS, 'independent-review-r21', 'independent-review-r21-complete',
               'independent-review-r21-routed', 'delivery-cleanup-r22', 'delivery-cleanup-r22-final',
               'blind-r16/independent-review-r21-deepseek', 'blind-r16/independent-review-r21-all',
               'blind-r16/independent-review-r21-routed', 'blind-r16/delivery-cleanup-r22-deepseek',
               'blind-r16/delivery-cleanup-r22-qwen']
TARGET = Path('F:/Workspaces/chinese-official-writing-skill-archives/experiments/reference-rewrite-20260913-common-layer/native-writing-batch-n.zip')
assert not TARGET.exists()
paths, calls = set(), []
for name, count in RUNS.items():
    rows = json.loads((ROOT / 'output' / name / 'results.json').read_text(encoding='utf-8'))
    assert len(rows) == count
    calls.extend({'run': name, **{k: v for k, v in row.items() if k not in {'commands', 'collaboration_items'}}} for row in rows)
for name in DIRECTORIES:
    directory = ROOT / 'output' / name
    assert directory.is_dir(), name
    paths.update(p for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
for directory in [HERE, ROOT / 'maintenance/tests/evidence/independent-review-r21', ROOT / 'maintenance/tests/evidence/sol-cold-r20']:
    paths.update(p for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
assert len(calls) == 26
manifest = []
TARGET.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(TARGET, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(paths):
        assert path.resolve().is_relative_to(ROOT.resolve())
        assert path.name.lower() not in {'auth.json', 'credentials.json', '.env', 'config.toml'}
        assert 'codex-profile' not in path.parts
        data = path.read_bytes()
        name = path.relative_to(ROOT).as_posix()
        archive.writestr(name, data)
        manifest.append({'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    archive.writestr('MANIFEST.json', json.dumps(manifest, ensure_ascii=False, indent=2))
with zipfile.ZipFile(TARGET) as archive:
    assert archive.testzip() is None
    for row in manifest:
        assert hashlib.sha256(archive.read(row['path'])).hexdigest() == row['sha256']
record = {'archive': str(TARGET), 'sha256': hashlib.sha256(TARGET.read_bytes()).hexdigest(),
          'bytes': TARGET.stat().st_size, 'entries': len(manifest) + 1,
          'root_calls': len(calls), 'technical_valid': sum(not r['invalid'] for r in calls),
          'crc': 'PASS', 'entry_hashes': 'PASS',
          'note': 'R21 broad review superseded; R22 narrow cleanup remains a prototype. All variants, failures, blind judgments and sanitized native provenance retained. No product adoption, main merge, installation or release. Host profile histories and credentials are excluded.'}
for name, value in [('archive-n', record), ('all-calls-n', calls)]:
    (HERE / (name + '.json')).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(record, ensure_ascii=False))
