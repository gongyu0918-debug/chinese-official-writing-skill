"""Archive native drafts and compact provenance; never grade writing by code."""
from pathlib import Path
import hashlib
import json
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RUNS = ROOT / 'output/scenario-atoms-native-20260918'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == '__main__':
    counts = {}
    for run in RUNS.iterdir():
        if not (run / 'binding.json').exists():
            continue
        target = HERE / 'native' / run.name
        target.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(run / 'binding.json', target / 'binding.json')
        rows, artifacts = [], []
        for result in sorted(run.glob('*.result.json')):
            item = json.loads(result.read_text(encoding='utf-8'))
            stem = result.name.removesuffix('.result.json')
            row = {key: value for key, value in item.items() if key != 'commands'}
            row['run'] = stem
            row['commands'] = [
                {'command': c['command'], 'exit_code': c['exit_code'],
                 'output_chars': len(c['aggregated_output']),
                 'output_sha256': hashlib.sha256(c['aggregated_output'].encode()).hexdigest()}
                for c in item['commands']
            ]
            rows.append(row)
            for suffix in ('result.json', 'trace.jsonl', 'stderr.txt', 'final.txt'):
                path = run / f'{stem}.{suffix}'
                if path.exists():
                    artifacts.append({'path': str(path), 'sha256': digest(path), 'bytes': path.stat().st_size})
                    if suffix == 'final.txt':
                        shutil.copyfile(path, target / path.name)
        save(target / 'calls.json', rows)
        save(target / 'artifacts.json', artifacts)
        counts[run.name] = len(rows)
    print(json.dumps(counts))
