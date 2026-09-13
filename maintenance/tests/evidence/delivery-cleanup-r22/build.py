"""Freeze the two-page delivery cleanup prototype against the adopted R20 pack."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASELINE = 'a8f2f4694450e790bcc7129447f0ccac32cf5ef2bf227e7852604d714dfcddb5'


def manifest(path):
    return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(path.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}


def fingerprint(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = ROOT / args.output
    out.mkdir(parents=True, exist_ok=False)
    source = ROOT / 'output/delivery-narration-r20-adopted/candidate'
    assert fingerprint(manifest(source)) == BASELINE
    for arm in ['baseline', 'candidate']:
        shutil.copytree(source, out / arm)
    for name in ['writing-rules', 'anti-ai-patterns']:
        shutil.copyfile(HERE / f'candidate-{name}.md', out / f'candidate/references/{name}.md')
    files = {arm: manifest(out / arm) for arm in ['baseline', 'candidate']}
    changed = [p for p, h in files['candidate'].items() if h != files['baseline'][p]]
    assert changed == ['references/anti-ai-patterns.md', 'references/writing-rules.md']
    record = {'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'changed': changed, 'files': files,
              'fingerprints': {arm: fingerprint(rows) for arm, rows in files.items()}}
    (out / 'build.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in record.items() if k != 'files'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
