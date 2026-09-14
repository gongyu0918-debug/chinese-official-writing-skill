"""Build the independent v2 preview; never overwrite a package or publish it."""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SLUG = 'chinese-official-writing-v2'


def build(source: Path, output: Path) -> dict:
    source = source.resolve()
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    product = output / SLUG
    product.mkdir()
    paths = [source / 'SKILL.md', source / 'README.md', source / 'LICENSE',
             *sorted((source / 'references').glob('*.md')),
             *sorted((source / 'scripts').glob('*.py'))]
    if any(not p.is_file() for p in paths):
        raise ValueError('Missing required source file')
    changes = []
    for path in paths:
        relative = path.relative_to(source)
        target = product / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        data = path.read_bytes()
        if relative.as_posix() == 'SKILL.md':
            text = data.decode('utf-8-sig').replace('\r\n', '\n')
            legacy_name = 'name: chinese-official-writing\n'
            current_name = f'name: {SLUG}\n'
            if text.count(legacy_name) + text.count(current_name) != 1:
                raise ValueError('Unexpected source skill name')
            text = text.replace(legacy_name, current_name, 1)
            text = text.replace('# 中文公文写作\n', '# 中文公文写作 2.0\n', 1)
            data = text.encode('utf-8')
            changes.append('SKILL.md: normalize independent product identity')
        elif relative.as_posix() == 'README.md':
            text = data.decode('utf-8-sig').replace('\r\n', '\n')
            text = text.replace('# 中文公文写作\n', '# 中文公文写作 2.0\n\n独立产品标识：`chinese-official-writing-v2`。此包为 2.0 测试版；1.x 已归档，既有 MIT 授权保持有效。\n', 1)
            text = text.replace('Hook 后续归 Pro 专属能力，普通版保留独立运行的检查脚本。', '2.0 包含写作规则和独立运行的篇幅、文稿检查脚本。1.x 已发布的 Hook 继续遵循其 MIT 许可；2.0 未包含 Hook。')
            text = '\n'.join(line for line in text.split('\n') if not line.startswith('欢迎到[中文公文写作页面]'))
            data = text.encode('utf-8')
            changes.append('README.md: independent identity, historical license boundary, remove 1.x feedback destination')
        target.write_bytes(data)
    files = {p.relative_to(product).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(product.rglob('*')) if p.is_file()}
    archive = output / f'{SLUG}-2.0.0-beta.1.zip'
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(product.rglob('*')):
            if p.is_file():
                z.write(p, (Path(SLUG) / p.relative_to(product)).as_posix())
    result = {'name':'中文公文写作 2.0','slug':SLUG,'version':'2.0.0-beta.1','status':'unpublished-preview',
              'source':str(source),'identity_only_changes':changes,'files':files,
              'archive':str(archive),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
    (output/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT/'chinese-official-writing')
    parser.add_argument('--output', type=Path, required=True)
    args=parser.parse_args()
    result=build(args.source,args.output)
    print(json.dumps({k:v for k,v in result.items() if k!='files'},ensure_ascii=False,indent=2))
