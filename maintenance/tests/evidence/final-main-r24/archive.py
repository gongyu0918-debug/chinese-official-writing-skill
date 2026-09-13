"""Preserve the final ordinary comparison, negatives and encoding recovery together."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
runs = [f'final-main-native-r24-m{i}' for i in range(5)] + [f'final-main-repeat-r24-m{i}' for i in [0, 2, 3]] + ['final-main-utf8-r24-m3'] + [f'narration-grounding-native-r25-m{i}' for i in [0, 3]]
names = ['final-main-r24', 'narration-grounding-r25', *runs,
         *['blind-r16/' + n.replace('final-main-native-', 'final-main-') for n in runs]]
if (ROOT / 'output/narration-grounding-r25-adopted').is_dir():
    names.append('narration-grounding-r25-adopted')
target = Path('F:/Workspaces/chinese-official-writing-skill-archives/experiments/reference-rewrite-20260913-common-layer/native-writing-batch-p.zip')
assert not target.exists()
paths = set()
for directory in [*(ROOT / 'output' / n for n in names), HERE, HERE.parent / 'narration-grounding-r25']:
    assert directory.is_dir(), directory
    paths.update(p for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
manifest = []
with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(paths):
        assert path.resolve().is_relative_to(ROOT.resolve())
        assert path.name.lower() not in {'auth.json', 'credentials.json', 'config.toml', '.env'}
        data = path.read_bytes()
        name = path.relative_to(ROOT).as_posix()
        archive.writestr(name, data)
        manifest.append({'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    archive.writestr('MANIFEST.json', json.dumps(manifest, ensure_ascii=False, indent=2))
with zipfile.ZipFile(target) as archive:
    assert archive.testzip() is None
    for row in manifest:
        assert hashlib.sha256(archive.read(row['path'])).hexdigest() == row['sha256']
record = {'archive': str(target), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
          'bytes': target.stat().st_size, 'entries': len(manifest) + 1, 'native_calls': 34,
          'comparable_calls': 32, 'encoding_damaged_calls': 2, 'crc': 'PASS', 'entry_hashes': 'PASS',
          'note': 'All first-pass negatives and the excluded encoding-damaged pair remain intact. Recovery is separate and changes only both-arm UTF-8 file-reading instruction. No merge, installation or release.'}
(HERE / 'archive-p.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(record, ensure_ascii=False))
