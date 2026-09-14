"""Preserve R31 original outputs and compact evidence; never score or edit drafts."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / 'output/v2-readiness-r31'
BATCHES = ('core', 'parent', 'script-delta', 'qwen2', 'deepseek', 'glmflash', 'word', 'minutes-retry')
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
inventory = []
for batch in BATCHES:
    folder = OUT / batch
    destination = HERE / 'runs' / batch
    destination.mkdir(parents=True, exist_ok=True)
    keep = [*folder.glob('*.final.txt'), folder / 'binding.json', folder / 'observations.json']
    keep += [p for p in (folder / 'artifact-links.json', folder / 'word-inspection.json') if p.is_file()]
    keep += list((folder / 'artifacts').glob('*'))
    for source in sorted(keep):
        target = destination / source.relative_to(folder)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        inventory.append({'file': target.relative_to(HERE).as_posix(), 'sha256': sha(target)})
for name in ('aggregate.json', 'verification.json'):
    shutil.copyfile(OUT / name, HERE / name)

archive = OUT / 'r31-native-evidence.zip'
with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as z:
    for batch in BATCHES:
        for source in sorted((OUT / batch).rglob('*')):
            if source.is_file():
                z.write(source, source.relative_to(OUT).as_posix())
    for source in sorted(OUT.glob('blind-*-mapping.private.json')):
        z.write(source, source.relative_to(OUT).as_posix())

rules = {}
for arm, folder in (('v1', OUT / 'frozen/baseline'), ('v2', ROOT / 'chinese-official-writing')):
    paths = [folder / 'SKILL.md', *sorted((folder / 'references').glob('*.md'))]
    rules[arm] = {'pages': len(paths), 'chars': sum(len(p.read_text(encoding='utf-8-sig')) for p in paths),
                  'entry_chars': len(paths[0].read_text(encoding='utf-8-sig'))}

preview = OUT / 'preview-final/chinese-official-writing-v2-2.0.0-beta.1.zip'
manifest = {'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'raw_archive': {'path': str(archive), 'sha256': sha(archive), 'bytes': archive.stat().st_size},
            'preview': {'path': str(preview), 'sha256': sha(preview), 'published': False},
            'static_rules': rules, 'files': inventory}
(HERE / 'archive.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in manifest.items() if k != 'files'}, ensure_ascii=False, indent=2))
print('Preserved compact files:', len(inventory))
