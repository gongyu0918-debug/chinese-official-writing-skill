import json
import sys
from run import OUT, PY, run

CHANGELOG = '改善Claude同稿连续修改的门禁接续和用户材料绑定；明确只发正文时，核验删除常见正文外说明后继续默认审查；修复完整JSON围栏误拒。Hook仍默认关闭，ClawHub保持无Hook包。自然字数解析及原稿事实纠错未准入。'
commands = {
    'github-release': ['gh','release','create','v1.6.29','--repo','gongyu0918-debug/chinese-official-writing-skill','--verify-tag','--title','v1.6.29','--notes-file',str(OUT/'release-notes.md')],
    'skillhub': [PY,'-B','-X','utf8','C:/Users/admin/.skillhub/skills_store_cli.py','--skip-self-upgrade','publish',str(OUT/'skillhub/chinese-official-writing'),'--version','1.6.29','--changelog',CHANGELOG,'--json'],
    'clawhub': ['C:/Program Files/nodejs/node.exe','C:/Users/admin/AppData/Roaming/npm/node_modules/clawhub/bin/clawdhub.js','publish','packages/openclaw/skills/chinese_official_writing','--slug','chinese-official-writing','--name','中文公文写作','--owner','gongyu0918-debug','--version','1.6.29','--tags','latest','--topics','chinese-writing,official-writing,office-productivity,content-creation','--source-repo','https://github.com/gongyu0918-debug/chinese-official-writing-skill','--source-commit','52d60597c3850d9922b8959a619be80e21e9af83','--source-ref','v1.6.29','--source-path','packages/openclaw/skills/chinese_official_writing','--changelog',CHANGELOG,'--json'],
}
if __name__=='__main__':
    key=sys.argv[1]
    attempt=OUT/(key+'-submission-attempt.json')
    assert not attempt.exists(), 'An attempt already exists; inspect receipt before any retry.'
    attempt.write_text(json.dumps({'formal_attempt':1,'command':commands[key]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    sys.exit(run(key+'-publish',commands[key]))
