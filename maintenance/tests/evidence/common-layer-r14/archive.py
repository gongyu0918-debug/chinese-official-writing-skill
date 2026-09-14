"""Archive the three completed R14 comparisons without rewriting any raw output."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RUNS = [f'common-layer-native-r14-{atom}' for atom in ['A', 'B', 'AB']]
DIRS = RUNS + ['common-layer-companions-r14', 'common-layer-blind-r14', 'canonical-adoption-r14']
EXTRA = ['canonical-adoption-audit-r14.md', 'genre-purity-audit-r14.md', 'genre-source-check-r14.md']
TARGET = Path('F:/Workspaces/chinese-official-writing-skill-archives/experiments/reference-rewrite-20260913-common-layer/native-writing-batch-g.zip')
assert not TARGET.exists()
calls, paths = [], set()
for name in RUNS:
    rows = json.loads((ROOT / 'output' / name / 'results.json').read_text(encoding='utf-8-sig'))
    assert len(rows) == 8, (name, len(rows))
    calls.extend({'run': name, **{k: v for k, v in row.items() if k != 'commands'}} for row in rows)
for name in DIRS:
    paths.update(p for p in (ROOT / 'output' / name).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
paths.update(ROOT / 'output' / name for name in EXTRA)
for group in ['A-sanitized', 'B', 'AB']:
    assert (ROOT / 'output/common-layer-blind-r14' / group / 'verdicts.json').is_file()
for p in paths:
    assert p.name.lower() not in {'auth.json', 'credentials.json', '.env', 'config.toml'}
TARGET.parent.mkdir(parents=True, exist_ok=True)
manifest = []
with zipfile.ZipFile(TARGET, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
    for p in sorted(paths):
        data = p.read_bytes()
        name = p.relative_to(ROOT).as_posix()
        archive.writestr(name, data)
        manifest.append({'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    archive.writestr('MANIFEST.json', json.dumps(manifest, ensure_ascii=False, indent=2))
with zipfile.ZipFile(TARGET) as archive:
    assert archive.testzip() is None
    entries = len(archive.infolist())
record = {
    'archive': str(TARGET), 'sha256': hashlib.sha256(TARGET.read_bytes()).hexdigest(),
    'bytes': TARGET.stat().st_size, 'entries': entries, 'crc': 'PASS',
    'calls': len(calls), 'technical_valid': sum(not r['invalid'] for r in calls), 'runs': RUNS,
    'note': 'All original outputs retained. A original packet leaked a technical path; A-sanitized was independently reviewed by a reader who had not seen the original. Technical validity and small-sample preference are not final 1.x quality acceptance.',
}
for name, value in [('archive-g', record), ('calls-g', calls)]:
    (HERE / f'{name}.json').write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(record, ensure_ascii=False))
