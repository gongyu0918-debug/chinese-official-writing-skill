"""Keep complete R12 messages anonymous; invalid or incomplete pairs stay outside preference counts."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[4]
parser = argparse.ArgumentParser()
parser.add_argument('group', choices=['unified', 'coverage', 'retry', 'index'])
args = parser.parse_args()
name = {'unified': 'common-layer-native-r12-unified', 'coverage': 'common-layer-native-r12-coverage', 'retry': 'common-layer-native-r12-retry', 'index': 'common-layer-native-r13-index'}[args.group]
run = ROOT / 'output' / name
binding = json.loads((run / 'binding.json').read_text(encoding='utf-8-sig'))
results = json.loads((run / 'results.json').read_text(encoding='utf-8-sig'))
grouped = {}
for r in results:
    grouped.setdefault((r['model'], r['case']), {})[r['arm']] = r
pairs, mappings, excluded = [], [], []
for i, ((model, case), records) in enumerate(sorted(grouped.items()), 1):
    if len(records) != 2 or any(r['invalid'] for r in records.values()):
        excluded.append({'model': model, 'case': case, 'invalid': {k: v['invalid'] for k,v in records.items()}})
        continue
    ident = args.group[0].upper() + f'{i:02}'
    pair = {'id': ident, 'request': binding['cases'][case]}
    mapping = {'id': ident, 'run': name, 'case': case, 'model': model}
    for letter, arm in zip('AB', ('candidate','baseline') if i % 2 else ('baseline','candidate')):
        r = records[arm]
        receipts = [p for p in run.glob(f'*-{case}-{arm}.result.json') if json.loads(p.read_text(encoding='utf-8-sig'))['model'] == model]
        assert len(receipts) == 1
        path = receipts[0].with_name(receipts[0].name.replace('.result.json','.final.txt'))
        raw = path.read_bytes()
        message = re.sub(r'(?:/)?C:/Users/admin/AppData/Local/Temp/[^\s)]+', '/<临时工作路径>', raw.decode('utf-8-sig'), flags=re.I)
        pair[letter] = message
        mapping[letter] = {'arm': arm, 'file': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(raw).hexdigest()}
    pairs.append(pair)
    mappings.append(mapping)
dest = ROOT / 'output/common-layer-blind-r12'
dest.mkdir(exist_ok=True)
packet = {'scope': 'Judge body and complete delivery separately. Ordinary complete drafts have an 80 nonspace character minimum; supplied explicit ranges and local/proofreading task scope take precedence. Allow grounded purpose/impact analysis, ordinary future intentions and today as a missing draft signature date. Distinguish unsupported concrete facts, explicit user scope limits, normal style variation and optional postscript suggestions. Do not infer actual tools from self-report or penalize masked paths.', 'pairs': pairs}
if args.group == 'index':
    packet['scope'] += ' For this preregistered follow-up, full-paragraph polishing is assessed against the 80-character minimum; the precise local replacement case preserves the unchanged text. Report minor length compliance separately from factual and language quality.'
for stem, value in [('packet',packet),('mapping',mappings),('excluded',excluded)]:
    path = dest / f'{stem}-{args.group}.json'
    assert not path.exists(),path
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pairs':len(pairs),'excluded':len(excluded),'sha256':hashlib.sha256((dest/f'packet-{args.group}.json').read_bytes()).hexdigest()}))
