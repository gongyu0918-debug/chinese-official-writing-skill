"""Bind a genuine unreadable DOCX and an isolated existing detector comparison."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[4]
DEST = ROOT / 'output/docx-input-native-r19'
assert not DEST.exists()
inventory = json.loads((ROOT / 'output/final-word-qa-r17/artifact-inventory.json').read_text(encoding='utf-8'))
entry = next(r for r in inventory if r['id'] == 'm4-scope_word_complete_signoff-candidate')
source = Path(entry['recovered'])
raw = source.read_bytes()
expected = '0989cecd96b1e85a5bc7eccdb7b0e4ca16260ecb23ae61161a5fd5fe19a6e068'
assert hashlib.sha256(raw).hexdigest() == entry['docx_sha256'] == expected
old_script = ROOT / 'output/editorial-object-r17-adopted/candidate/scripts/prose_lint.py'
old = old_script.read_bytes()
assert hashlib.sha256(old).hexdigest() == 'd69f2a2f02972f1ed832f1f34af2f8ccd140033c6422f95d3637e920c42b46dc'
for arm in ['baseline', 'candidate']:
    shutil.copytree(ROOT / 'chinese-official-writing', DEST / arm, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
(DEST / 'baseline/scripts/prose_lint.py').write_bytes(old)
(DEST / 'received-application.docx').write_bytes(raw)


def files(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}


maps = {arm: files(DEST / arm) for arm in ['baseline', 'candidate']}
assert set(maps['baseline']) == set(maps['candidate'])
assert {k for k in maps['baseline'] if maps['baseline'][k] != maps['candidate'][k]} == {'scripts/prose_lint.py'}
assert maps['candidate']['scripts/prose_lint.py'] == '96d79b02e0a23d7ea9eb7427b2b5b21c09cb2e03cd0f7243fdc3ab0fb1a9f460'
record = {'document': {'source': str(source), 'staged': str(DEST / 'received-application.docx'), 'sha256': expected},
          'files': maps, 'fingerprints': {arm: hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest() for arm, value in maps.items()},
          'scope': 'Both arms use current common rules; only the already-adopted explicit DOCX zero-font detector differs. Not an old full-package baseline.'}
(DEST / 'build.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'document_sha256': expected, 'fingerprints': record['fingerprints']}, ensure_ascii=False))
