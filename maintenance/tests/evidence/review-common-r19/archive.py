"""Preserve all R19 variants, native calls and read-only Word evidence."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RUNS = {'review-common-native-r19-qwen': 8, 'review-common-native-r19-deepseek': 8,
        'review-common-native-r19-repaired': 8, 'review-common-native-r19-calculated': 8,
        'docx-input-native-r19-deepseek': 2, 'docx-input-native-r19-glm': 2}
DIRECTORIES = [*RUNS, 'review-common-r19', 'review-common-r19-repaired', 'review-common-r19-calculated',
               'review-common-scope-r19', 'review-common-r19-checks', 'docx-input-native-r19', 'docx-input-qa-r19', 'completion-audit-r19',
               *['blind-r16/review-common-r19-' + s for s in ['qwen', 'deepseek', 'repaired', 'calculated-valid']]]
if (ROOT / 'output/review-common-r19-adopted').is_dir():
    DIRECTORIES.append('review-common-r19-adopted')
TARGET = Path('F:/Workspaces/chinese-official-writing-skill-archives/experiments/reference-rewrite-20260913-common-layer/native-writing-batch-l.zip')
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
for directory in [HERE, ROOT / 'maintenance/tests/evidence/docx-input-native-r19', ROOT / 'maintenance/tests/evidence/completion-audit-r19']:
    paths.update(p for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
assert len(calls) == 36
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
          'note': 'Three review-page variants remain separate; rejected prototypes and adverse drafts retained. Word detector comparison uses R18 rules, not the R19 review-page combination. First three review batches have explicitly limited raw runner provenance. No main merge, installation or release.'}
for name, value in [('archive-l', record), ('calls-l', calls)]:
    (HERE / (name + '.json')).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(record, ensure_ascii=False))
