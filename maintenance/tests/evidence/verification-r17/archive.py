"""Archive R17 originals, failed experiments and read-only Word evidence."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RUNS = {'final-genres-native-r17-low-frequency': 10, 'final-word-native-r17': 12, 'editorial-object-native-r17-qwen': 4, 'editorial-object-native-r17-minimax': 4, 'motion-purpose-native-r17': 8, 'final-modes-native-r17': 8}
DIRS = [*RUNS, 'editorial-object-r17', 'editorial-object-r17-adopted', 'motion-purpose-r17', 'final-word-qa-r17', 'legacy-boundary-current-r17', 'prose-docx-zero-r17', 'reference-verification-r17-adopted']
REVIEWS = ['final-genres-r17', 'editorial-object-r17', 'motion-purpose-r17', 'final-modes-r17']
TARGET = Path('F:/Workspaces/chinese-official-writing-skill-archives/experiments/reference-rewrite-20260913-common-layer/native-writing-batch-j.zip')
assert not TARGET.exists()
calls = []
paths = set()
for name, count in RUNS.items():
    rows = json.loads((ROOT / 'output' / name / 'results.json').read_text(encoding='utf-8-sig'))
    assert len(rows) == count, (name, len(rows))
    calls.extend({'run': name, **{k: v for k, v in row.items() if k != 'commands'}} for row in rows)
for name in DIRS + ['blind-r16/' + n for n in REVIEWS]:
    directory = ROOT / 'output' / name
    assert directory.is_dir(), name
    paths.update(p for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
paths.add(ROOT / 'output/editorial-combination-attribution-r17.md')
for name in REVIEWS:
    assert (ROOT / 'output/blind-r16' / name / 'verdicts.json').is_file()
assert len(calls) == 46
for path in paths:
    assert path.is_file() and path.resolve().is_relative_to((ROOT / 'output').resolve()), path
    assert path.name.lower() not in {'auth.json', 'credentials.json', '.env', 'config.toml'}, path
manifest = []
TARGET.parent.mkdir(parents=True, exist_ok=True)
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
record = {'archive': str(TARGET), 'sha256': hashlib.sha256(TARGET.read_bytes()).hexdigest(), 'bytes': TARGET.stat().st_size, 'entries': entries, 'crc': 'PASS', 'entry_hashes': 'PASS', 'calls': len(calls), 'technical_valid': sum(not r['invalid'] for r in calls), 'note': 'Original failures preserved. Word files, text, links and visual pages assessed separately. Prototype detector replays are not new native writing calls. No main merge, installation or release.'}
for name, value in [('archive-j', record), ('calls-j', calls)]:
    (HERE / (name + '.json')).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(record, ensure_ascii=False))
