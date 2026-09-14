"""Build a standard versioned Skill snapshot without overwriting prior artifacts."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SLUG = 'chinese-official-writing'

def build(source: Path, output: Path, version: str = '2.0.0-beta.2') -> dict:
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?', version):
        raise ValueError('Invalid version')
    source, output = source.resolve(), output.resolve()
    if 'name: '+SLUG+'\n' not in (source/'SKILL.md').read_text(encoding='utf-8-sig'):
        raise ValueError('Source must use the existing Skill identity')
    output.mkdir(parents=True, exist_ok=False)
    product = output/SLUG
    paths = [source/'SKILL.md', source/'README.md', source/'LICENSE',
             *sorted((source/'references').glob('*.md')), *sorted((source/'scripts').glob('*.py'))]
    for path in paths:
        if not path.is_file() or path.is_symlink():
            raise ValueError('Missing or unsafe source file')
        target = product/path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    files = {p.relative_to(product).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(product.rglob('*')) if p.is_file()}
    archive = output/f'{SLUG}-{version}.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(product.rglob('*')):
            if p.is_file(): z.write(p,(Path(SLUG)/p.relative_to(product)).as_posix())
    result = {'name':'中文公文写作','slug':SLUG,'version':version,'status':'unpublished-preview',
              'source':str(source),'files':files,'archive':str(archive),
              'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
    (output/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=ROOT/'chinese-official-writing')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--version',default='2.0.0-beta.2')
    args=parser.parse_args()
    result=build(args.source,args.output,args.version)
    print(json.dumps({k:v for k,v in result.items() if k!='files'},ensure_ascii=False,indent=2))
