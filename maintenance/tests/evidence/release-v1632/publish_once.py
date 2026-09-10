"""One formal submission per target; inspect receipts before any recovery."""
import hashlib,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
E=Path(__file__).resolve().parent
OUT=ROOT/'output/release-v1632'
mode=sys.argv[1]
freeze=json.loads((OUT/'release-freeze.json').read_text(encoding='utf-8'))
commit=freeze['release_commit']
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==commit
notes=(E/'release-notes.md').read_text(encoding='utf-8')
assert not any(term in notes for term in ['拆分','拆出','拆了一','拆出来'])
for label,manifest in json.loads((E/'package-manifests.json').read_text(encoding='utf-8')).items():
 path=Path(manifest['path'])
 actual={p.relative_to(path).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in path.rglob('*') if p.is_file()}
 assert actual==manifest['files'],label
commands={
 'github-push':['git','push','--atomic','origin','HEAD:refs/heads/main','refs/tags/v1.6.32'],
 'github-release':['C:/Program Files/GitHub CLI/gh.exe','release','create','v1.6.32','--repo','gongyu0918-debug/chinese-official-writing-skill','--verify-tag','--title','v1.6.32','--notes-file',str(E/'release-notes.md')],
 'skillhub':['C:/Users/admin/AppData/Local/Programs/Python/Python313/python.exe','C:/Users/admin/.skillhub/skills_store_cli.py','--skip-self-upgrade','publish',str(OUT/'skillhub/chinese-official-writing'),'--version','1.6.32','--changelog',notes,'--json'],
 'clawhub':['C:/Program Files/nodejs/node.exe','C:/Users/admin/AppData/Roaming/npm/node_modules/clawhub/bin/clawdhub.js','publish',str(OUT/'packages/openclaw/skills/chinese_official_writing'),'--slug','chinese-official-writing','--name','中文公文写作','--owner','gongyu0918-debug','--version','1.6.32','--tags','latest','--topics','chinese-writing,official-writing,office-productivity,content-creation','--source-repo','https://github.com/gongyu0918-debug/chinese-official-writing-skill','--source-commit',commit,'--source-ref','v1.6.32','--source-path','chinese-official-writing','--changelog',notes,'--json']}
command=commands[mode]
attempt=OUT/(mode+'-attempt.json')
with attempt.open('x',encoding='utf-8') as f:json.dump({'formal_attempt':1,'command':command,'release_commit':commit},f,ensure_ascii=False,indent=2)
t=time.monotonic()
r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=300)
receipt={'command':command,'exit_code':r.returncode,'seconds':round(time.monotonic()-t,2),'stdout':r.stdout,'stderr':r.stderr}
(OUT/(mode+'-receipt.json')).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'target':mode,'exit_code':r.returncode,'stdout':r.stdout[-1800:],'stderr':r.stderr[-800:]},ensure_ascii=False))
sys.exit(r.returncode)
