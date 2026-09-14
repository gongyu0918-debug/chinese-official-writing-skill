"""Freeze the cold-review readability correction for final combination writing."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'output/common-layer-owners-r15-refined/AB2'
DEST = ROOT / 'output/common-layer-owners-r15-final/AB3'
assert not DEST.exists()
OLD = '按材料和主文种核对事实、状态、必要要素及改动；整体查全文，局部查改动及关联内容。跨段论证、多主体责任、表格和附件，核对对应的主体、结论、字段名称、数值及实测/测算/估算口径、顺序、状态、期限和指向。Word按模板查样式，保留要求的批注和修订痕迹。'
NEW = '按材料和主文种核对事实、状态、必要要素及本轮改动；整体查全文，局部查改动及关联内容。跨段论证和多主体事项核对主体、结论、期限及相互指向；正文、表格和附件核对对应要素的名称、数值、顺序和状态是否一致，分清实测、测算与估算。Word 稿按模板核对样式，保留要求的批注和修订痕迹。'
shutil.copytree(SOURCE, DEST, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
path = DEST / 'references/writing-rules.md'
raw = path.read_bytes()
assert raw.count(OLD.encode()) == 1
path.write_bytes(raw.replace(OLD.encode(), NEW.encode()))
files = {p.relative_to(DEST).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(DEST.rglob('*')) if p.is_file()}
record = {'source': SOURCE.relative_to(ROOT).as_posix(), 'old': OLD, 'new': NEW, 'files': files, 'fingerprint': hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()}
(DEST.parent / 'build.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(record['fingerprint'])
