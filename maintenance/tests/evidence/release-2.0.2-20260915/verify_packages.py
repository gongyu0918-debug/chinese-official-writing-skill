"""Verify release archives and execute the unpacked ordinary scripts."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile
import yaml

ROOT = Path(__file__).resolve().parents[4]
OUTPUT = ROOT / 'output/release-2.0.2'
EVIDENCE = Path(__file__).resolve().parent
source = OUTPUT / 'source'
workbuddy = json.loads((OUTPUT/'workbuddy-manifest.json').read_text(encoding='utf-8'))
github = json.loads((OUTPUT/'github/manifest.json').read_text(encoding='utf-8'))
result = {'product_commit':workbuddy['source_commit'],'checks':{}}
for manifest in (workbuddy, github):
    assert hashlib.sha256(Path(manifest['archive']).read_bytes()).hexdigest() == manifest['archive_sha256']
with zipfile.ZipFile(workbuddy['archive']) as bundle:
    names = bundle.namelist()
    assert bundle.testzip() is None
    assert len(names) == len(set(names)) == len(workbuddy['files']) == 73
    assert set(names) == set(workbuddy['files'])
    assert not any(PurePosixPath(n).is_absolute() or '..' in PurePosixPath(n).parts or 'hooks' in n.lower() or n.startswith('maintenance/') or n.endswith('review_gate.py') for n in names)
    for name in names:
        data = bundle.read(name)
        assert hashlib.sha256(data).hexdigest() == workbuddy['files'][name]
        if name != 'SKILL.md':
            assert data == (source/name).read_bytes()
    original = (source/'SKILL.md').read_text(encoding='utf-8')
    adapted = bundle.read('SKILL.md').decode('utf-8')
    assert original.split('---',2)[2] == adapted.split('---',2)[2]
    metadata = yaml.safe_load(adapted.split('---',2)[1])
    assert metadata['name'] == 'chinese-official-writing' and metadata['version'] == '2.0.2'
    assert {'display_name','display_name_en','description_zh','description_en'} <= metadata.keys()
    assert '当前版本为 2.0.2' in bundle.read('README.md').decode('utf-8')
    assert '你可以这样用' in bundle.read('README.md').decode('utf-8')
    unpacked = Path(tempfile.mkdtemp(prefix='workbuddy-check-', dir=OUTPUT))
    bundle.extractall(unpacked)
    result['workbuddy'] = {'archive':workbuddy['archive'],'sha256':workbuddy['archive_sha256'],'files':len(names),'references':sum(n.startswith('references/') for n in names),'scripts':sum(n.startswith('scripts/') for n in names),'canonical_body_equal':True,'canonical_other_files_equal':True,'metadata_fields':sorted(metadata),'crc_ok':True,'no_hooks_or_maintenance':True}
with zipfile.ZipFile(github['archive']) as bundle:
    names = bundle.namelist()
    assert bundle.testzip() is None
    assert set(names) == {'chinese-official-writing/'+n for n in github['files']} and len(names) == 72
    for name in names:
        assert bundle.read(name) == (source/PurePosixPath(name).relative_to('chinese-official-writing')).read_bytes()
    result['github'] = {'archive':github['archive'],'sha256':github['archive_sha256'],'files':len(names),'canonical_equal':True,'crc_ok':True,'optional_ui_metadata_omitted':['agents/openai.yaml']}
fixture = OUTPUT/'script-smoke.txt'
fixture.write_text('关于参加档案整理培训的通知\n\n业务科、资料室：\n\n档案整理培训定于2026年9月18日下午3时在二楼会议室举行，请准时参加。参会回执请于9月16日前报办公室，接收邮箱office@example.org，联系人王老师。\n',encoding='utf-8',newline='\n')
bad = OUTPUT/'format-smoke.txt'
bad.write_text('# 关于参加档案整理培训的通知\n\n请业务科参加培训。\n',encoding='utf-8',newline='\n')

def run(label, args, expected):
    command = ['python',*map(str,args)]
    completed = subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    result['checks'][label] = {'command':command,'returncode':completed.returncode,'stdout':completed.stdout,'stderr':completed.stderr}
    assert completed.returncode == expected,(label,completed.stdout,completed.stderr)

run('unpacked_word_count',[unpacked/'scripts/draft_length.py','--min-chars','80','--max-chars','220',fixture],0)
lint = [unpacked/'scripts/prose_lint.py','--delivery-mode','draft-body','--structure','--format','--strict']
run('unpacked_clean_lint',[*lint,fixture],0)
run('unpacked_markdown_detection',[*lint,bad],1)
run('requested_markdown_allowed',[*lint,'--allow-markdown',bad],0)
run('unpacked_paths',['maintenance/tools/audit_product_surface.py','--root',unpacked],0)
assert subprocess.check_output(['git','diff','651d5dec','HEAD','--name-only','--','chinese-official-writing'],cwd=ROOT).decode().splitlines() == ['chinese-official-writing/README.md']
result['checks']['approved_rules_unchanged'] = {'passed':True,'only_product_change':'README version 2.0.1 to 2.0.2'}
result['checks']['draft_length_unit_tests'] = {'command':'python -m unittest maintenance.tests.test_draft_length','passed':12}
result['scope'] = {'not_run':'WorkBuddy application import/native writing; no new semantic writing tests','deferred':['SkillHub','ClawHub','other adaptation packages','local Pro build/install']}
(EVIDENCE/'package-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
shutil.copy2(OUTPUT/'workbuddy-manifest.json',EVIDENCE/'workbuddy-manifest.json')
shutil.copy2(OUTPUT/'github/manifest.json',EVIDENCE/'github-manifest.json')
print(json.dumps({key:value for key,value in result.items() if key != 'checks'},ensure_ascii=False,indent=2))
print('Package and script checks passed')
