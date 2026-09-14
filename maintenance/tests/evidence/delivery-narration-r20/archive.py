"""Preserve all R20 variants, native calls, cold reviews and migration evidence."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RUNS = {'review-boundaries-native-r20-qwen': 8, 'review-boundaries-native-r20-deepseek': 8,
        'delivery-narration-native-r20-qwen': 6, 'delivery-narration-native-r20-deepseek': 6}
DIRECTORIES = [*RUNS, 'review-boundaries-r20', 'delivery-narration-r20',
               'delivery-narration-r20-examples', 'delivery-narration-r20-navigation',
               'delivery-narration-r20-complete-entry', 'delivery-narration-r20-final',
               'delivery-narration-r20-final-rebuild', 'delivery-narration-r20-adopted',
               'sol-cold-r20', 'request-capability-r20', 'motion-purpose-r20',
               'blind-r16/review-boundaries-r20',
               'blind-r16/delivery-narration-r20-qwen', 'blind-r16/delivery-narration-r20-deepseek']
TARGET = Path('F:/Workspaces/chinese-official-writing-skill-archives/experiments/reference-rewrite-20260913-common-layer/native-writing-batch-m.zip')
assert not TARGET.exists()
paths, calls = set(), []
for name, expected in RUNS.items():
    rows = json.loads((ROOT / 'output' / name / 'results.json').read_text(encoding='utf-8'))
    assert len(rows) == expected
    calls.extend({'run': name, **{k: v for k, v in r.items() if k != 'commands'}} for r in rows)
for name in DIRECTORIES:
    directory = ROOT / 'output' / name
    assert directory.is_dir(), name
    paths.update(p for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
for directory in [HERE, ROOT / 'maintenance/tests/evidence/review-boundaries-r20', ROOT / 'maintenance/tests/evidence/legacy-boundary-migration-r20']:
    paths.update(p for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
assert len(calls) == 28
manifest = []
TARGET.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(TARGET, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(paths):
        assert path.resolve().is_relative_to(ROOT.resolve())
        assert path.name.lower() not in {'auth.json', 'credentials.json', '.env', 'config.toml'}
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
          'bytes': TARGET.stat().st_size, 'entries': len(manifest) + 1, 'calls': len(calls),
          'technical_valid': sum(not r['invalid'] for r in calls), 'crc': 'PASS', 'entry_hashes': 'PASS',
          'note': 'Keep the rejected review-page restoration and all unrun intermediate entry variants distinct. The user-corrected index edit was withdrawn. Twelve tested entry/delivery calls support development adoption with adverse state, narration and missing anti-AI examples retained; sixteen restoration calls do not support adoption. Full Sol cold review binds R19, with R20 changes evaluated separately. No main merge, installation or release.'}
for name, value in [('archive-m', record), ('calls-m', calls)]:
    (HERE / (name + '.json')).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(record, ensure_ascii=False))
