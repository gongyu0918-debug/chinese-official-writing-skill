"""Adopt the native-tested motion page, then apply the user's review scope correction."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PACK = ROOT / 'output/motion-content-r23'
OUT = ROOT / 'output/motion-content-r23-adopted'
build = json.loads((PACK / 'build.json').read_text(encoding='utf-8'))


def files(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}


def fp(rows):
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()


assert not OUT.exists()
assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'codex/reference-rewrite-20260912'
canonical = ROOT / 'chinese-official-writing'
assert files(canonical) == build['files']['baseline']
assert files(PACK / 'candidate') == build['files']['candidate']
for name in ['motion-content-native-r23-qwen', 'motion-content-native-r23-deepseek']:
    run = ROOT / 'output' / name
    rows = json.loads((run / 'results.json').read_text(encoding='utf-8'))
    assert len(rows) == 6 and all(not r['invalid'] for r in rows)
    for arm, folder in [('baseline', 'main'), ('candidate', 'candidate')]:
        assert files(run / 'snapshots' / folder) == build['files'][arm]
targets = [canonical] + [ROOT / 'packages' / pkg / 'skills' / name for pkg, name in [
    ('agent-skills', 'chinese-official-writing'), ('hermes', 'chinese-official-writing'),
    ('qwen-code', 'chinese-official-writing'), ('qwenwork', 'chinese-official-writing'),
    ('openclaw', 'chinese_official_writing')]]
changed = ['references/genre-playbook-motion.md', 'references/review-checklist.md']
before = {str(t.relative_to(ROOT)): files(t) for t in targets}
old = '确需独立复核时，提供稿件、判断所需材料、范围及来源，依据证据处理分歧。'
new = '确需独立复核时，交接完整待交付消息，仅清理旁白、工程或工具自述、可见思考和写稿过程泄露；保留业务内容、合理分析及有效审核意见，交付清理后的同一消息。'
review = (canonical / changed[1]).read_text(encoding='utf-8')
assert review.count(old) == 1
for target in targets:
    for relative in changed:
        assert hashlib.sha256((target / relative).read_bytes()).hexdigest() == build['files']['baseline'][relative]
        assert not subprocess.check_output(['git', 'status', '--porcelain', '--', (target / relative).relative_to(ROOT).as_posix()], cwd=ROOT, text=True).strip()
for target in targets:
    shutil.copyfile(PACK / 'candidate' / changed[0], target / changed[0])
    (target / changed[1]).write_text(review.replace(old, new), encoding='utf-8', newline='\n')
after = {str(t.relative_to(ROOT)): files(t) for t in targets}
for name in before:
    assert {p for p, h in after[name].items() if h != before[name][p]} == set(changed)
for target in targets:
    for relative in changed:
        assert (target / relative).read_bytes() == (canonical / relative).read_bytes()
shutil.copytree(canonical, OUT / 'candidate', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
record = {'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
          'main': subprocess.check_output(['git', 'rev-parse', 'main'], cwd=ROOT, text=True).strip(),
          'changed': changed, 'files': files(canonical), 'fingerprint': fp(files(canonical)),
          'native_tested_motion_pack': build['fingerprints']['candidate'], 'mirrors': 5,
          'review_scope_correction': {'old': old, 'new': new, 'basis': 'User explicitly limited independent review to narration and visible thought/drafting-process leakage; no new default call or companion check added.',
                                     'native_scope': 'Twelve motion calls did not return review-checklist. R22 native child executions support feasibility but do not establish this exact wording as newly behavior-tested. No new model run is claimed.'},
          'scope': 'Development adoption only; no merge, installation or publication.'}
(OUT / 'adoption.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: record[k] for k in ['fingerprint', 'changed', 'mirrors', 'scope']}, ensure_ascii=False))
