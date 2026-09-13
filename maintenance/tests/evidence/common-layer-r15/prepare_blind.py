"""Prepare immutable anonymous messages from disjoint native runs, preserving originals."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[4]
parser = argparse.ArgumentParser()
parser.add_argument('atom', choices=['A', 'B', 'AB', 'B2', 'AB2', 'AB3', 'AB3-repeat'])
parser.add_argument('--runs', nargs='+', required=True)
args = parser.parse_args()
groups = {}
for name in args.runs:
    run = ROOT / 'output' / name
    binding = json.loads((run / 'binding.json').read_text(encoding='utf-8-sig'))
    results = json.loads((run / 'results.json').read_text(encoding='utf-8-sig'))
    for r in results:
        pair = groups.setdefault((r['model'], r['case']), {})
        assert r['arm'] not in pair, (name, r['model'], r['case'], r['arm'])
        pair[r['arm']] = (run, binding['cases'][r['case']], r)

pairs, mappings, excluded = [], [], []
for number, ((model, case), records) in enumerate(sorted(groups.items()), 1):
    if len(records) != 2 or any(r[2]['invalid'] for r in records.values()):
        excluded.append({'model': model, 'case': case, 'invalid': {k: v[2]['invalid'] for k, v in records.items()}})
        continue
    assert records['baseline'][1] == records['candidate'][1]
    identifier = f'P{number:02}'
    pair = {'id': identifier, 'request': records['baseline'][1]}
    mapping = {'id': identifier, 'model': model, 'case': case}
    # Order balances within each small packet; mapping remains outside it.
    for letter, arm in zip('AB', ('candidate', 'baseline') if number % 2 else ('baseline', 'candidate')):
        run, _, r = records[arm]
        receipts = [p for p in run.glob(f'*-{case}-{arm}.result.json') if json.loads(p.read_text(encoding='utf-8-sig'))['model'] == model]
        assert len(receipts) == 1
        path = receipts[0].with_name(receipts[0].name.replace('.result.json', '.final.txt'))
        raw = path.read_bytes()
        pair[letter] = re.sub(r'(?:/)?C:[\\/]+Users[\\/]+admin[\\/]+AppData[\\/]+Local[\\/]+Temp[\\/]+[^\s)>]+', '/<临时工作路径>', raw.decode('utf-8-sig'), flags=re.I)
        mapping[letter] = {'arm': arm, 'run': run.name, 'file': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(raw).hexdigest()}
    pairs.append(pair)
    mappings.append(mapping)
dest = ROOT / 'output/common-layer-blind-r15' / args.atom
dest.mkdir(parents=True, exist_ok=True)
packet = {
    'scope': 'Compare each manuscript and complete delivery separately. Preserve grounded purposes, impacts, ordinary proposals and confirmed current draft signature dates. Check required genre acts, speaker and recipient roles, data nature, arithmetic, temporal order, uncertainty and attachment consistency. Ordinary complete manuscripts have an 80 nonspace character floor unless user scope says otherwise; for two manuscripts assess each separately. Do not treat every usual preparation or analytical sentence as invented fact. Distinguish substantive errors from stylistic preferences and process narration. Do not infer actual tool execution from self-reports or penalize masked file paths. Ties are allowed.',
    'pairs': pairs,
}
for name, value in [('packet', packet), ('mapping', mappings), ('excluded', excluded)]:
    path = dest / f'{name}.json'
    assert not path.exists(), path
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'atom': args.atom, 'pairs': len(pairs), 'excluded': len(excluded), 'sha256': hashlib.sha256((dest / 'packet.json').read_bytes()).hexdigest()}))
