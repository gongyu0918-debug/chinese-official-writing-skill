"""Preserve anonymous complete-message comparisons, including independent repeats."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import secrets

ROOT = Path(__file__).resolve().parents[4]
parser = argparse.ArgumentParser()
parser.add_argument('name')
parser.add_argument('--runs', nargs='+', required=True)
args = parser.parse_args()
assert re.fullmatch(r'[a-zA-Z0-9_-]+', args.name)
destination = ROOT / 'output/blind-r16' / args.name
assert not destination.exists()
destination.mkdir(parents=True)
pairs, mappings, excluded = [], [], []
for run_name in args.runs:
    run = ROOT / 'output' / run_name
    binding = json.loads((run / 'binding.json').read_text(encoding='utf-8-sig'))
    groups = {}
    for receipt in sorted(run.glob('*.result.json')):
        row = json.loads(receipt.read_text(encoding='utf-8-sig'))
        group = groups.setdefault((row['model'], row['case']), {})
        assert row['arm'] not in group
        group[row['arm']] = (row, receipt)
    for (model, case), group in sorted(groups.items()):
        if set(group) != {'baseline', 'candidate'} or any(v[0]['invalid'] for v in group.values()):
            excluded.append({'run': run_name, 'model': model, 'case': case, 'invalid': {arm: v[0]['invalid'] for arm, v in group.items()}})
            continue
        identifier = f'P{len(pairs)+1:02}'
        pair = {'id': identifier, 'request': binding['cases'][case]}
        mapping = {'id': identifier, 'run': run_name, 'model': model, 'case': case}
        arms = ['baseline', 'candidate']
        if secrets.randbits(1):
            arms.reverse()
        for label, arm in zip('AB', arms):
            _, receipt = group[arm]
            path = receipt.with_name(receipt.name.replace('.result.json', '.final.txt'))
            raw = path.read_bytes()
            pair[label] = re.sub(r'(?:/)?C:[\\/]+Users[\\/]+admin[\\/]+AppData[\\/]+Local[\\/]+Temp[\\/]+[^\s)>]+', '/<临时工作路径>', raw.decode('utf-8-sig'), flags=re.I)
            mapping[label] = {'arm': arm, 'file': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(raw).hexdigest()}
        pairs.append(pair)
        mappings.append(mapping)
packet = {'scope': 'Compare bodies and complete delivery separately against the user request. Allow grounded reasons, purposes, direct effects, normal proposed arrangements and current draft signature dates. Preserve actual fact/state, roles, data nature and required document acts. Ordinary complete manuscripts have an 80 nonspace character floor unless scope or an explicit shorter requirement overrides it; assess independent manuscripts separately. Distinguish material errors from stylistic preferences and process narration. Do not infer tool execution from self-reports or penalize masked file paths. Ties are allowed.', 'pairs': pairs}
for name, value in [('packet', packet), ('mapping', mappings), ('excluded', excluded)]:
    (destination / f'{name}.json').write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'packet': str(destination / 'packet.json'), 'pairs': len(pairs), 'excluded': len(excluded), 'sha256': hashlib.sha256((destination / 'packet.json').read_bytes()).hexdigest()}))
