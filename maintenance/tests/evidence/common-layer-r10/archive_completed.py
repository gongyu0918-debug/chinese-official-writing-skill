"""Archive frozen earlier experiments and completed R10/R11 writing without touching live runs."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RUNS = ['combined-native-r8-text', 'combined-native-r8-word', 'combined-native-r8-boundaries', 'common-layer-native-r10', 'common-layer-native-r11-length']
DIRS = RUNS + ['combined-candidate-r8', 'combined-text-blind-r8', 'common-layer-experiment-r10', 'common-layer-refine-r11', 'common-layer-blind-r10', 'common-layer-blind-r11', 'short-companion-candidate-r9', 'short-companion-candidate-r9b', 'short-companion-experiment-r9']
EXTRA = ['common-layer-ownership-r10.md']
TARGET = Path('F:/Workspaces/chinese-official-writing-skill-archives/experiments/reference-rewrite-20260913-common-layer/native-writing-batch-e.zip')
assert not TARGET.exists(), 'Refuse to replace existing evidence'
calls = []
for name in RUNS:
    for row in json.loads((ROOT / 'output' / name / 'results.json').read_text(encoding='utf-8-sig')):
        calls.append({'run': name, **{k: v for k, v in row.items() if k != 'commands'}})
paths = set()
for name in DIRS:
    path = ROOT / 'output' / name
    assert path.is_dir(), path
    paths.update(p for p in path.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
paths.update(ROOT / 'output' / name for name in EXTRA)
for path in paths:
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
    entries = len(archive.infolist())
report = {'archive': str(TARGET), 'sha256': hashlib.sha256(TARGET.read_bytes()).hexdigest(), 'bytes': TARGET.stat().st_size, 'entries': entries, 'crc': 'PASS',
          'calls': len(calls), 'technical_valid': sum(not r['invalid'] for r in calls), 'runs': RUNS,
          'note': 'Technical completion is not writing acceptance. R9 ran no writing. R8 Word includes failures; captured traces/messages are preserved, but this archive does not establish artifact recovery or visual validation. Live R12 is excluded.'}
(HERE / 'archive-e.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(HERE / 'calls-e.json').write_text(json.dumps(calls, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, ensure_ascii=False))
