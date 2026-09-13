"""Compose independently frozen rule changes into one complete writing Skill."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'chinese-official-writing'
DEST = ROOT / 'output/reference-integration-r16'
assert not DEST.exists()
assert not subprocess.check_output(['git', 'status', '--porcelain', '--', str(SOURCE)], cwd=ROOT, text=True).strip()
def files(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
def hashes(values):
    return {k: hashlib.sha256(v).hexdigest() for k, v in values.items()}
base = files(SOURCE)
for arm in ['baseline', 'candidate']:
    shutil.copytree(SOURCE, DEST / arm, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
candidate = DEST / 'candidate'
components = [
    ('common', 'common-layer-owners-r15/baseline', 'common-layer-owners-r15-final/AB3'),
    ('router', 'genre-router-cleanup-r16/baseline', 'genre-router-cleanup-r16/candidate'),
    ('procurement', 'genre-purpose-r16/baseline', 'genre-purpose-r16/procurement'),
    ('correspondence', 'genre-purpose-r16/baseline', 'genre-purpose-r16/correspondence-v2'),
    ('editorial', 'editorial-note-r16/baseline', 'editorial-note-r16/candidate'),
]
records = []
for name, baseline_path, incoming_path in components:
    assert files(ROOT / 'output' / baseline_path) == base, name
    incoming_root = ROOT / 'output' / incoming_path
    incoming = files(incoming_root)
    changed = sorted(k for k in base.keys() | incoming.keys() if base.get(k) != incoming.get(k))
    merged = []
    for relative in changed:
        target = candidate / relative
        assert target.resolve().is_relative_to(candidate.resolve())
        current = target.read_bytes() if target.exists() else None
        new = incoming.get(relative)
        if current == new:
            continue
        if current != base.get(relative):
            assert relative == 'references/reference-index.md', (name, relative)
            result = subprocess.run(['git', 'merge-file', '-p', str(target), str(SOURCE / relative), str(incoming_root / relative)], cwd=ROOT, capture_output=True)
            assert result.returncode == 0, (name, result.stderr.decode(errors='replace'))
            target.write_bytes(result.stdout)
            merged.append(relative)
        elif new is None:
            target.unlink()
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(new)
    records.append({'component': name, 'source': incoming_path, 'files': hashes(incoming), 'changed': changed, 'three_way_merged': merged})
refinements = {
    'references/genre-playbook-editorial-note.md': ('本组内容', '所编发内容'),
    'references/genre-playbook-procurement-announcement.md': ('采购公告公开采购项目的征集响应、结果或终止事项', '采购公告公开采购项目的征集响应、结果或终止等事项'),
}
for relative, (old, new) in refinements.items():
    path = candidate / relative
    raw = path.read_bytes()
    assert raw.count(old.encode()) == 1
    path.write_bytes(raw.replace(old.encode(), new.encode()))
actual = files(candidate)
changed = sorted(k for k in base.keys() | actual.keys() if base.get(k) != actual.get(k))
assert len(changed) == 17, changed
assert all(base[k] == v for k, v in actual.items() if k.startswith('scripts/'))
assert 'references/handling-elements.md' not in actual
assert 'references/official-style.md' not in actual
assert 'references/genre-playbook-editorial-note.md' in actual
index = actual['references/reference-index.md'].decode('utf-8-sig')
for term in ['genre-playbook-editorial-note.md', 'genre-playbook-correspondence.md', '请求批准', 'genre-checklist.md']:
    assert term in index, term
assert files(SOURCE) == base
record = {'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'components': records, 'editorial_refinements': refinements, 'changed': changed, 'files': {'baseline': hashes(base), 'candidate': hashes(actual)}, 'fingerprints': {k: hashlib.sha256(json.dumps(hashes(v), sort_keys=True).encode()).hexdigest() for k, v in [('baseline', base), ('candidate', actual)]}, 'canonical_unchanged': True, 'candidate_file_count': len(actual), 'candidate_reference_count': sum(k.startswith('references/') and k.endswith('.md') for k in actual)}
(DEST / 'build.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: record[k] for k in ['changed', 'fingerprints', 'candidate_file_count', 'candidate_reference_count']}, ensure_ascii=False))
