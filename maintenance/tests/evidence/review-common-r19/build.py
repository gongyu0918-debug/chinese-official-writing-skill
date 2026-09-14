"""Freeze an audit-specific page reduction against the current common workflow."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--fix-grammar', action='store_true')
parser.add_argument('--explicit-calculation', action='store_true')
args = parser.parse_args()
if args.explicit_calculation and not args.fix_grammar:
    parser.error('--explicit-calculation requires --fix-grammar')
variant = 'calculated' if args.explicit_calculation else 'repaired' if args.fix_grammar else 'initial'
DEST = ROOT / ('output/review-common-r19' + ('' if variant == 'initial' else '-' + variant))
SOURCE = ROOT / 'chinese-official-writing'
proposal = ROOT / 'output/review-common-scope-r19/proposal.md'
raw = proposal.read_bytes()
candidate = proposal.read_text(encoding='utf-8-sig').split('```markdown\n', 1)[1].split('\n```', 1)[0] + '\n'
assert candidate.startswith('# 审稿检查\n')
if args.fix_grammar:
    anchor = '按当前主文种和 `writing-rules.md` 复核。'
    assert candidate.count(anchor) == 1
    candidate = candidate.replace(anchor, anchor + '结合上下文核对病句和搭配。', 1)
if args.explicit_calculation:
    anchor = '涉及算术校核时说明口径。'
    assert candidate.count(anchor) == 1
    candidate = candidate.replace(anchor, '可核算的数值用工具复算，并说明口径。', 1)
assert not DEST.exists()
assert not subprocess.check_output(['git', 'status', '--porcelain', '--', 'chinese-official-writing'], cwd=ROOT, text=True).strip()
for arm in ['baseline', 'candidate']:
    shutil.copytree(SOURCE, DEST / arm, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
relative = 'references/review-checklist.md'
(DEST / 'candidate' / relative).write_text(candidate, encoding='utf-8')
(HERE / ('candidate-review.md' if variant == 'initial' else 'candidate-review-' + variant + '.md')).write_text(candidate, encoding='utf-8')


def files(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}


maps = {arm: files(DEST / arm) for arm in ['baseline', 'candidate']}
assert maps['baseline'] == files(SOURCE)
assert set(maps['baseline']) == set(maps['candidate'])
assert {k for k in maps['baseline'] if maps['baseline'][k] != maps['candidate'][k]} == {relative}
sizes = {}
for arm in maps:
    text = (DEST / arm / relative).read_text(encoding='utf-8')
    sizes[arm] = {'chars': len(text), 'nonspace': len(re.sub(r'\s', '', text))}
record = {'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
          'variant': variant,
          'semantic_repair': 'restore grammar check; explicitly use tools to recalculate derivable values' if args.explicit_calculation else 'restore ordinary-review grammar and collocation check' if args.fix_grammar else None,
          'main': subprocess.check_output(['git', 'rev-parse', 'main'], cwd=ROOT, text=True).strip(),
          'changed': [relative], 'proposal_sha256': hashlib.sha256(raw).hexdigest(),
          'sizes': sizes, 'files': maps,
          'fingerprints': {arm: hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest() for arm, value in maps.items()}}
(DEST / 'build.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: record[k] for k in ['source_head', 'changed', 'sizes', 'fingerprints']}, ensure_ascii=False))
