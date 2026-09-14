"""Freeze complete paired messages; keep identities and raw hashes outside the packet."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[4]
parser = argparse.ArgumentParser()
parser.add_argument('atom', choices=['A', 'B', 'AB'])
parser.add_argument('--revision', default='')
args = parser.parse_args()
run = ROOT / f'output/common-layer-native-r14-{args.atom}'
binding = json.loads((run / 'binding.json').read_text(encoding='utf-8-sig'))
results = json.loads((run / 'results.json').read_text(encoding='utf-8-sig'))
groups = {}
for record in results:
    groups.setdefault((record['model'], record['case']), {})[record['arm']] = record
pairs, mappings, excluded = [], [], []
for i, ((model, case), records) in enumerate(sorted(groups.items()), 1):
    if len(records) != 2 or any(r['invalid'] for r in records.values()):
        excluded.append({'model': model, 'case': case, 'invalid': {k: v['invalid'] for k, v in records.items()}})
        continue
    identifier = f'P{i:02}'
    pair = {'id': identifier, 'request': binding['cases'][case]}
    mapping = {'id': identifier, 'model': model, 'case': case}
    for letter, arm in zip('AB', ('candidate', 'baseline') if i % 2 else ('baseline', 'candidate')):
        receipts = [p for p in run.glob(f'*-{case}-{arm}.result.json') if json.loads(p.read_text(encoding='utf-8-sig'))['model'] == model]
        assert len(receipts) == 1
        path = receipts[0].with_name(receipts[0].name.replace('.result.json', '.final.txt'))
        raw = path.read_bytes()
        pair[letter] = re.sub(r'(?:/)?C:[\\/]+Users[\\/]+admin[\\/]+AppData[\\/]+Local[\\/]+Temp[\\/]+[^\s)>]+', '/<临时工作路径>', raw.decode('utf-8-sig'), flags=re.I)
        mapping[letter] = {'arm': arm, 'file': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(raw).hexdigest()}
    pairs.append(pair)
    mappings.append(mapping)
dest = ROOT / 'output/common-layer-blind-r14' / (args.atom + args.revision)
dest.mkdir(parents=True, exist_ok=True)
packet = {
    'scope': 'Judge manuscript and full delivery separately. Allow grounded purpose/impact inference, ordinary proposals, and confirmed current date for a missing draft signature. Distinguish unsupported concrete facts or upgraded decisions from normal style variation. Assess ordinary complete drafts against an 80 nonspace-character floor, separately from factual/language quality. Optional postscript suggestions are not body commitments. Do not infer actual tools from self-report or penalize masked paths. Identify severity and quote concrete evidence; ties are allowed.',
    'pairs': pairs,
}
for name, value in [('packet', packet), ('mapping', mappings), ('excluded', excluded)]:
    path = dest / f'{name}.json'
    assert not path.exists(), path
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'atom': args.atom, 'pairs': len(pairs), 'excluded': len(excluded), 'packet_sha256': hashlib.sha256((dest / 'packet.json').read_bytes()).hexdigest()}))
