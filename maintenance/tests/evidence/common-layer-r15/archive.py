"""Archive completed R15 originals; never overwrite an archive or alter raw drafts."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RUNS = {
    'common-layer-native-r15-A': 8,
    'common-layer-native-r15-B': 8,
    'common-layer-native-r15-B-repeat': 2,
    'common-layer-native-r15-B2': 8,
    'common-layer-native-r15-AB3-core': 4,
    'common-layer-native-r15-AB3-more': 6,
    'common-layer-native-r15-AB3-qwen0-repeat': 2,
    'common-layer-native-r15-AB3-qwen1-repeat': 2,
    'common-layer-native-r15-AB3-minimax-repeat': 2,
}
DIRS = list(RUNS) + ['common-layer-owners-r15', 'common-layer-owners-r15-refined', 'common-layer-owners-r15-final', 'common-layer-blind-r15']
EXTRA = ['common-layer-r15-owner-cold-review.md', 'rewrite-remaining-coverage-r15.md', 'genre-router-cleanup-r16-plan.md']
TARGET = Path('F:/Workspaces/chinese-official-writing-skill-archives/experiments/reference-rewrite-20260913-common-layer/native-writing-batch-h.zip')
assert not TARGET.exists()
calls, paths = [], set()
for name, expected in RUNS.items():
    rows = json.loads((ROOT / 'output' / name / 'results.json').read_text(encoding='utf-8-sig'))
    assert len(rows) == expected, (name, len(rows))
    calls.extend({'run': name, **{k: v for k, v in row.items() if k != 'commands'}} for row in rows)
for name in DIRS:
    paths.update(p for p in (ROOT / 'output' / name).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
paths.update(ROOT / 'output' / name for name in EXTRA)
for group in ['A', 'B', 'B2', 'AB3', 'AB3-repeat']:
    assert (ROOT / 'output/common-layer-blind-r15' / group / 'verdicts.json').is_file()
for path in paths:
    assert path.is_file(), path
    assert path.name.lower() not in {'auth.json', 'credentials.json', '.env', 'config.toml'}
TARGET.parent.mkdir(parents=True, exist_ok=True)
manifest = []
with zipfile.ZipFile(TARGET, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(paths):
        data = path.read_bytes()
        name = path.relative_to(ROOT).as_posix()
        archive.writestr(name, data)
        manifest.append({'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    archive.writestr('MANIFEST.json', json.dumps(manifest, ensure_ascii=False, indent=2))
with zipfile.ZipFile(TARGET) as archive:
    assert archive.testzip() is None
    for row in manifest:
        assert hashlib.sha256(archive.read(row['path'])).hexdigest() == row['sha256']
    entries = len(archive.infolist())
record = {
    'archive': str(TARGET), 'sha256': hashlib.sha256(TARGET.read_bytes()).hexdigest(),
    'bytes': TARGET.stat().st_size, 'entries': entries, 'crc': 'PASS',
    'calls': len(calls), 'technical_valid': sum(not row['invalid'] for row in calls),
    'runs': list(RUNS),
    'note': 'Original B, diagnostic repeat and refined B2 retained separately. Internal 2.0 comparisons; technical completion and preferences do not certify final 1.x nonregression.',
}
for name, value in [('archive-h', record), ('calls-h', calls)]:
    (HERE / f'{name}.json').write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(record, ensure_ascii=False))
