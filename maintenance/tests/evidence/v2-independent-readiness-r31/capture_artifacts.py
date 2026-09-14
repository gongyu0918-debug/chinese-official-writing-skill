"""Preserve linked local deliverables and their availability; never alter drafts."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import sys

run=Path(sys.argv[1]).resolve()
dest=run/'artifacts'
dest.mkdir(exist_ok=True)
rows=[]
for final in sorted(run.glob('*.final.txt')):
    text=final.read_text(encoding='utf-8-sig')
    for n,match in enumerate(re.finditer(r'\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+))\)',text)):
        raw=match.group(1) or match.group(2)
        if raw.startswith(('http:','https:','codex:')):
            continue
        target=raw
        if re.match(r'^/[A-Za-z]:[/\\]',target): target=target[1:]
        path=Path(target)
        row={'final':final.name,'link':raw,'resolved':str(path),'exists':path.is_file()}
        if path.is_file():
            copy=dest/f'{final.stem}-{n}{path.suffix}'
            shutil.copyfile(path,copy)
            row.update(copy=copy.relative_to(run).as_posix(),sha256=hashlib.sha256(copy.read_bytes()).hexdigest())
        rows.append(row)
(run/'artifact-links.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rows,ensure_ascii=False))
