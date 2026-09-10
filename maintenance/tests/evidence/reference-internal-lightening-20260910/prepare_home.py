"""Freeze independent homepage-only experiment against the same main."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];E=Path(__file__).resolve().parent
old=json.loads((ROOT/'maintenance/tests/evidence/progressive-route-validation-20260910/combined-depth.json').read_text(encoding='utf-8'))
config={'atom':'home-route-dedup','baseline':'36653d768f8e9bf14bb615a642846e0db10b9f04','candidate':'c412a49dbe3784697d88d36b946fdda6ca78af75','expected_diff':['SKILL.md'],
 'assignments':{'0':['pending_minutes'],'1':['project_addition'],'2':['opinion_rewrite'],'3':['public_statement'],'4':['limited_commitment']},
 'cases':{k:old['cases'][k] for k in ['opinion_rewrite','public_statement','limited_commitment']}}
config['cases']['pending_minutes']={'task':'请仅根据以下记录整理简短会议纪要正文，不加标题、参会人或落款。2026年9月9日办公室召开资料核对协调会，讨论了12份登记记录的核对问题；会上提出由资料室汇总差异的建议，但尚未作决定，完成期限也未确定。直接输出可用正文，不把建议写成分工、议定安排或执行要求，不补会议共识、原因、反馈渠道、复核节奏或后续动作。'}
config['cases']['project_addition']={'task':'请按以下唯一材料起草一份向甲中心领导班子提交的增项申请，直接输出完整可用稿件，语言平实，不新增数据、用途、测试或后续安排。落款甲中心信息科，成文日期保持缺失。材料：现有资料登记系统已在使用，信息科建议在该系统增加按登记日期检索功能；需求来自本次登记资料查询，现有材料未统计查询次数或耗时。供应方报价为一次性开发费用3000元，报价仅覆盖日期检索功能；申请是否批准、实施时间和验收主体均未确定。请清楚提出批准增加该功能及3000元开发费用的申请，不把申请写成已获批或已安排实施。'}
(E/'home-route-dedup.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for arm in ['baseline','candidate']:
 text=subprocess.check_output(['git','show',config[arm]+':chinese-official-writing/SKILL.md'],cwd=ROOT).decode()
 print(arm,len(text))
