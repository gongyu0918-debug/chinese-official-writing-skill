"""Freeze an independent editorial-note leaf and its sole directory entry."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
DEST = ROOT / 'output/editorial-note-r16'
SOURCE = ROOT / 'chinese-official-writing'
assert not DEST.exists()
assert not subprocess.check_output(['git', 'status', '--porcelain', '--', str(SOURCE)], cwd=ROOT, text=True).strip()
for arm in ['baseline', 'candidate']:
    shutil.copytree(SOURCE, DEST / arm, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
refs = DEST / 'candidate/references'
index = refs / 'reference-index.md'
old = '- 新闻消息、活动报道、编者按：`genre-playbook-news-message.md`。'
new = '- 新闻消息、活动报道：`genre-playbook-news-message.md`。\n- 编者按、编发按语：`genre-playbook-editorial-note.md`。'
raw = index.read_bytes()
assert raw.count(old.encode()) == 1
eol = b'\r\n' if b'\r\n' in raw else b'\n'
index.write_bytes(raw.replace(old.encode(), new.encode().replace(b'\n', eol)))
news = refs / 'genre-playbook-news-message.md'
lines = news.read_bytes().splitlines(keepends=True)
removed = [line for line in lines if line.startswith('- 用户要求编者按时'.encode())]
assert len(removed) == 1
news.write_bytes(b''.join(line for line in lines if line not in removed))
(refs / 'genre-playbook-editorial-note.md').write_text('''# 编者按

以编辑或编发者身份，说明编发什么、为何编发，以及读者可关注什么。

## 成稿

- 结合选题背景、材料主题和编发目的，概括本组内容的关系及阅读重点；有据的评价、分析和期望可融入其中。
- 按材料和篇幅组织简短自然段。采用用户已有栏目或版面模板；通常以“编者按”为标题，或用“编者按：”起笔，任选一种清楚标示即可，署名按实际需要处理。
- 叙述站在编发者的位置；引用作者经历、报道事实或被编发者观点时，保留其归属。具体栏目沿革、编发安排和评价依据取自材料。
- 本轮只要按语时，写完按语即可；同时需要被编发正文时，分别组织两部分，保留原文的任务按要求照录。

## 核对

编发对象、背景、目的与阅读方向相互对应，按语和被编发正文的身份与内容分清。按语以编辑说明成立，通常无需另套消息标题、导语和事件报道结构。
''', encoding='utf-8')
files = {}
for arm in ['baseline', 'candidate']:
    directory = DEST / arm
    files[arm] = {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(directory.rglob('*')) if p.is_file()}
changed = sorted(k for k in files['baseline'].keys() | files['candidate'].keys() if files['baseline'].get(k) != files['candidate'].get(k))
assert changed == ['references/genre-playbook-editorial-note.md', 'references/genre-playbook-news-message.md', 'references/reference-index.md']
assert not any('scripts/' in p for p in changed)
record = {'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'changed': changed, 'files': files, 'fingerprints': {k: hashlib.sha256(json.dumps(v, sort_keys=True).encode()).hexdigest() for k, v in files.items()}, 'new_leaf_characters': len((refs / 'genre-playbook-editorial-note.md').read_text(encoding='utf-8'))}
(DEST / 'build.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: record[k] for k in ['changed', 'fingerprints', 'new_leaf_characters']}, ensure_ascii=False))
