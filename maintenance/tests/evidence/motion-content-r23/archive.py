"""Keep the finite R23 native comparison and completion audit recoverable."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
names = ['motion-content-r23', 'motion-content-r23-adopted', 'motion-content-native-r23-qwen',
         'motion-content-native-r23-deepseek', 'blind-r16/motion-content-r23-qwen',
         'blind-r16/motion-content-r23-deepseek', 'completion-audit-r23']
target = Path('F:/Workspaces/chinese-official-writing-skill-archives/experiments/reference-rewrite-20260913-common-layer/native-writing-batch-o.zip')
assert not target.exists()
paths = set()
for directory in [*(ROOT / 'output' / n for n in names), HERE, ROOT / 'maintenance/tests/evidence/completion-audit-r23']:
    assert directory.is_dir(), directory
    paths.update(p for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
manifest = []
with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(paths):
        assert path.resolve().is_relative_to(ROOT.resolve())
        assert path.name.lower() not in {'auth.json', 'credentials.json', 'config.toml', '.env'}
        data = path.read_bytes(); name = path.relative_to(ROOT).as_posix()
        archive.writestr(name, data)
        manifest.append({'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    archive.writestr('MANIFEST.json', json.dumps(manifest, ensure_ascii=False, indent=2))
with zipfile.ZipFile(target) as archive:
    assert archive.testzip() is None
    for row in manifest:
        assert hashlib.sha256(archive.read(row['path'])).hexdigest() == row['sha256']
record = {'archive': str(target), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
          'bytes': target.stat().st_size, 'entries': len(manifest) + 1, 'native_calls': 12,
          'crc': 'PASS', 'entry_hashes': 'PASS',
          'note': 'Motion-only native prototype and final development pack with the separate user scope correction remain distinct. Includes both cold audits of 21 historical primary leaves and 2 transaction overlays. No new trial queued, no main merge, installation or release.'}
(HERE / 'archive-o.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(record, ensure_ascii=False))
