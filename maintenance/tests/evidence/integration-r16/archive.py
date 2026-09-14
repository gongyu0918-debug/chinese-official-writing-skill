"""Archive completed R16 originals and repairs without replacing prior evidence."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RUNS = {
    'common-layer-native-r16-A-minimax': 2,
    'common-layer-native-r16-B2-minimax': 2,
    'genre-router-native-r16': 24,
    'procurement-purpose-native-r16': 12,
    'correspondence-purpose-native-r16': 12,
    'editorial-note-native-r16': 12,
    'reference-integration-native-r16-medium': 16,
    'reference-integration-native-r16-max': 24,
    'reference-integration-native-r16-glm-recovery': 2,
    'reference-cold-fixes-native-r16': 16,
}
DIRS = list(RUNS) + [
    'genre-router-cleanup-r16', 'genre-purpose-r16', 'editorial-note-r16',
    'reference-integration-r16', 'reference-integration-r16-rule-refinement',
    'reference-integration-r16-final', 'reference-integration-r16-adopted',
    'prose-inline-r16', 'prose-business-conditional-r16', 'full-skill-cold-r16',
    'blind-r16',
]
EXTRA = ['r16-route-editorial-cold-review.md', 'r16-purpose-cold-review.md',
         'r16-route-execution-audit.md', 'low-frequency-coverage-r16.md']
TARGET = Path('F:/Workspaces/chinese-official-writing-skill-archives/experiments/reference-rewrite-20260913-common-layer/native-writing-batch-i.zip')
assert not TARGET.exists()
calls, paths = [], set()
for name, expected in RUNS.items():
    rows = json.loads((ROOT/'output'/name/'results.json').read_text(encoding='utf-8-sig'))
    assert len(rows) == expected, (name, len(rows))
    calls.extend({'run': name, **{k:v for k,v in row.items() if k != 'commands'}} for row in rows)
assert len(calls) == 122
for name in DIRS:
    paths.update(p for p in (ROOT/'output'/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
paths.update(ROOT/'output'/name for name in EXTRA)
for name in ['attribution','procurement','editorial','router','correspondence','correspondence-restored','integration-medium','integration-max','integration-recovery','cold-fixes']:
    assert (ROOT/'output/blind-r16'/name/'verdicts.json').is_file(), name
for p in paths:
    assert p.is_file() and p.resolve().is_relative_to((ROOT/'output').resolve()), p
    assert p.name.lower() not in {'auth.json','credentials.json','.env','config.toml'}
TARGET.parent.mkdir(parents=True, exist_ok=True)
manifest = []
with zipfile.ZipFile(TARGET,'x',compression=zipfile.ZIP_DEFLATED) as archive:
    for p in sorted(paths):
        data = p.read_bytes(); name = p.relative_to(ROOT).as_posix()
        archive.writestr(name,data)
        manifest.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    archive.writestr('MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2))
with zipfile.ZipFile(TARGET) as archive:
    assert archive.testzip() is None
    for row in manifest:
        assert hashlib.sha256(archive.read(row['path'])).hexdigest() == row['sha256']
    entries = len(archive.infolist())
record = {
    'archive':str(TARGET),'sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest(),
    'bytes':TARGET.stat().st_size,'entries':entries,'crc':'PASS','entry_hashes':'PASS',
    'calls':len(calls),'original_technical_valid':sum(not row['invalid'] for row in calls),
    'calibrated_technical_valid':sum(not row['invalid'] for row in calls)+1,
    'calibration':'output/blind-r16/correspondence-restored/calibration.json',
    'note':'One complete relative-path SKILL read restored; original receipt and exclusion preserved. Provider 502 and unfinished 100-character task remain invalid. Internal 2.0 observations do not certify 1.x nonregression.',
}
for name,value in [('archive-i',record),('calls-i',calls)]:
    (HERE/f'{name}.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
