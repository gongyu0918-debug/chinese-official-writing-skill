"""Freeze separate companion-trigger and formulaic-content atoms, plus their combination."""
from pathlib import Path
import difflib
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'output/common-layer-index-r13/skill'
DEST = ROOT / 'output/common-layer-companions-r14'
assert not DEST.exists()
DEST.mkdir()
changes = {
    'A': {'references/genre-playbook-request.md': [
        ('需要核对主体、金额、期限、附件或反馈时加读 `handling-elements.md`',
         '需要核对多主体责任、分项金额或正文与附件的对应关系时加读 `handling-elements.md`')]},
    'B': {'references/formulaic-language.md': [
        ('- 材料只有月份、月日或时间段时保留原时间锚，不补“今年”、具体年份或材料外日期。\n', ''),
        ('- 固定尾语按事项需要使用。一篇稿只保留一个有效收束；纪要、汇报提纲、调查报告等已自然结束时不强加尾语。\n', ''),
        ('“综上所述”“总之”“为此”“据此”只在形成真实归纳或承接时使用；上一段已经完成作用时不重复添加。',
         '“综上所述”“总之”“为此”“据此”用于真实归纳或承接。'),
        ('\n## 复核\n\n检查用语是否符合文种、主送对象和正文功能；引叙的文件、文号、日期及研究/批准动作是否有材料依据；固定尾语是否必要并与落款衔接；是否重复收束、堆叠敬辞或用旧式词掩盖事项不清。\n', '')]}
}
records = {}
for arm, atoms in [('A', ['A']), ('B', ['B']), ('AB', ['A','B'])]:
    target = DEST / arm
    shutil.copytree(SOURCE, target, ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    changed=set()
    for atom in atoms:
        for name, replacements in changes[atom].items():
            p=target/name;text=p.read_text(encoding='utf-8-sig')
            for old,new in replacements:
                assert text.count(old)==1,(name,old)
                text=text.replace(old,new)
            p.write_text(text,encoding='utf-8',newline='\n');changed.add(name)
    patch=[]
    for name in sorted(changed):
        a=(SOURCE/name).read_text(encoding='utf-8-sig');b=(target/name).read_text(encoding='utf-8-sig')
        patch.extend(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='r13/'+name,tofile=arm+'/'+name))
    (DEST/f'{arm}.diff').write_text(''.join(patch),encoding='utf-8')
    manifest={p.relative_to(target).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(target.rglob('*')) if p.is_file()}
    records[arm]={'changed_paths':sorted(changed),'files':manifest,'fingerprint':hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()}
(DEST/'build.json').write_text(json.dumps({'source':SOURCE.relative_to(ROOT).as_posix(),'arms':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({a:{'fingerprint':v['fingerprint'],'changed':v['changed_paths']} for a,v in records.items()},ensure_ascii=False))
