"""Keep language fidelity explicit for all edits while preserving the two page removals."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'output/common-layer-owners-r15'
DEST = ROOT / 'output/common-layer-owners-r15-refined'
assert not DEST.exists()
OLD = '口语或情绪化表达改为同义正式语体，保持叙述身份、原意、引用、主体、对象、否定范围、先后和论断强度。“更稳、更省”仍分别说明稳定性和成本。'
NEW = '语言调整保持原意、叙述身份、引用、主体、对象、条件、可能性、否定范围、先后和论断强度；口语或情绪化表达用同义正式语体表述。“更稳、更省”分别保留稳定性和成本两层意思。'
records = {}
for original, name in [('B', 'B2'), ('AB', 'AB2')]:
    target = DEST / name
    shutil.copytree(SOURCE / original, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    path = target / 'references/anti-ai-patterns.md'
    raw = path.read_bytes()
    assert raw.count(OLD.encode()) == 1
    path.write_bytes(raw.replace(OLD.encode(), NEW.encode()))
    files = {p.relative_to(target).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(target.rglob('*')) if p.is_file()}
    records[name] = {'source': original, 'files': files, 'fingerprint': hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()}
(DEST / 'build.json').write_text(json.dumps({'changed_from_previous': 'references/anti-ai-patterns.md: expression fidelity paragraph only', 'old': OLD, 'new': NEW, 'arms': records}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v['fingerprint'] for k, v in records.items()}))
