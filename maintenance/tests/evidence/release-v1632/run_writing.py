"""Combined router/index interaction comparison against retained scene-only product."""
import concurrent.futures
import hashlib
import io
import json
import subprocess
import types
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[4]
E = Path(__file__).resolve().parent
OUT = ROOT / 'output/release-v1632-writing'
REVISIONS = {'baseline': '77dfcfac', 'candidate': '0f088b82'}
RUNNER_PATH = 'maintenance/tests/evidence/output-contract-matrix-r1/run_matrix.py'
source = subprocess.check_output(['git', 'show', 'c8058bdc:' + RUNNER_PATH], cwd=ROOT)
matrix = types.ModuleType('verified_matrix')
matrix.__file__ = str(Path('F:/Workspaces/chinese-official-writing-skill/output/route-worktrees/skill-lightening-merge-check') / RUNNER_PATH)
exec(compile(source, matrix.__file__, 'exec'), matrix.__dict__)
CASES = {'news_edit': {'task': '请修改下列活动新闻稿，理顺段落和句子、去AI味，校对数字日期与文字格式。只输出改后正文，不增加新事实、目的或效果，不补标题落款日期。唯一底稿：2026年9月7日，青禾中心举办资料整理培训，18人参加。培训内容包括分类标记和归档顺序，现场演示了2份材料。18人参加了这次培训。活动为高质量发展注入强劲动能，取得了显著实效。培训反馈仍在汇总，尚未形成结论。', 'checks': ['日期18人2份不改', '重复参加信息自然合并', '删无据成效口号', '反馈汇总中不升级', '不加新目的效果', '正文无过程/校对说明']}, 'request': {'task': '请写简短采购申请：办公室现有打印机高峰时需等待20分钟，拟申请购置一台打印机，预算2000元。审批尚未决定，不补品牌、购买渠道或日期。', 'checks': ['未命中四类卡后继续选择申请叶并交付正文', '20分钟/1台/2000元与拟购未批状态', '不补日期品牌渠道', '不以执行说明代替成稿']}, 'commentary': {'task': '请写一篇简短新闻评论，围绕提示清楚与办理便利展开两个有区别的论点，理顺段落句子、去AI味并校对日期数字。直接给正文，不附写作说明。材料：2026年9月6日，青禾服务站试用了新的材料清单。12名办事人员中，7人反馈更容易找到所需材料，3人认为两处提示不清楚，2人未反馈。后续是否调整尚未决定。可以从材料出发作一层评论分析，不增加政策、机构行为、调查结果或已经取得的成效。', 'checks': ['完整日期与12/7/3/2主体状态', '是否调整未决', '两个论点有区别且有据', '无政策组织成效补造', '段落句子anti-ai校对衔接', '无执行旁白']}, 'advisory': {'task': '请以平台使用方身份给平台建设方写一份合作性优化建议，语言平实、有据分析，直接给成稿。材料：试用期间，5名填报人员反馈重复录入有所减少，但没有统计减少幅度。3张表对同一指标的统计范围提示不一致，分歧已随表记录。两次提交显示失败，重试后成功，原因未查明。我们建议先核对3张表的提示文字，再评估是否调整；技术方案、负责人和时间尚未决定。可说明提示一致对理解口径的意义，但不要补已取得效果或替对方承诺实施。', 'checks': ['5人/3表/两次主体不混', '无虚构减少幅度', '建议先核对及再评估保持未定', '不补技术原因或承诺', '建议非监督命令', '段落不重复', '无执行旁白']}, 'remediation': {'task': '请根据以下问题清单，为本单位拟一份简短整改方案，直接给正文。允许提出职责范围内的一般纠正措施和复核步骤，不指定材料没有的部门、人名、预算、期限或固定机制。请使问题与措施对应、句子自然，并校对数字和状态。材料：2026年9月5日内部检查发现，18份登记表中有4份缺少签名，其中2份已补签、仍待复核，另2份尚未补签。检查还发现同一事项在2张表中的提示文字不一致，原因尚未查明，目前正在核对。责任分工和完成时间尚未决定。', 'checks': ['18/4及2已补待复核与2未补准确绑定', '提示正在核对不写尚未启动或已统一', '允许一般未来措施且有可执行内容', '责任时间仍未决', '不补专班月报预算具体责任期限', '无执行旁白']}, 'complaint': {'task': '请以我本人身份，写给平台客服的“情况反映”正文，保留这个标题。只说明我遇到的问题、经过和当前状态，不提出解决建议，也不新增投诉请求。请合并真正重复的表达、去AI味，校对日期次数和文字格式。只给可直接提交的正文。材料：2026年9月7日，我在青禾平台提交材料时，两次页面提示“提交失败”。我重试后页面显示“提交成功”，但记录列表仍未显示该材料。2026年9月8日，客服表示“是否入库尚待核实”。我目前仍在查询，没有再次提交。记录列表仍未显示该材料。材料没有姓名、联系方式或成文日期，保持缺失。', 'checks': ['9月7日两次失败重试成功不混', '9月8日客服说法有归属且待核实', '列表未显示及仍在查询未再提交保留', '不加建议请求承诺和技术原因', '标题保留缺失要素不补', '自然合并重复且无旁白']}}
ASSIGNMENTS = {0: ['news_edit', 'request'], 1: ['commentary'], 2: ['advisory'], 3: ['remediation'], 4: ['complaint']}
matrix.OUT, matrix.E, matrix.CASES = OUT, E, CASES


def prepare():
    OUT.mkdir(parents=True, exist_ok=False)
    hashes = {}
    for arm, rev in REVISIONS.items():
        names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', rev, '--', 'chinese-official-writing'], cwd=ROOT).decode().splitlines()
        stream = io.BytesIO(subprocess.check_output(['git', 'cat-file', '--batch'], input=('\n'.join(rev + ':' + n for n in names) + '\n').encode(), cwd=ROOT))
        hashes[arm] = {}
        for name in names:
            header = stream.readline().split(); data = stream.read(int(header[2])); assert stream.read(1) == b'\n'
            rel = Path(name).relative_to('chinese-official-writing'); p = OUT / 'frozen' / arm / rel
            p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data)
            hashes[arm][rel.as_posix()] = hashlib.sha256(data).hexdigest()
    diff = sorted(n for n in hashes['baseline'].keys() | hashes['candidate'].keys() if hashes['baseline'].get(n) != hashes['candidate'].get(n))
    assert diff == ['SKILL.md', 'references/compatibility-scene-routing.md', 'references/reference-index.md'], diff
    catalog = json.loads(matrix.native.CATALOG.read_text(encoding='utf-8'))['models']
    for i, model in enumerate(matrix.MODELS):
        selected = [m for m in catalog if m['slug'] == model]; assert len(selected) == 1
        matrix.save(OUT / f'catalog-{i}.json', {'models': selected})
    matrix.save(E / 'cases.json', CASES)
    matrix.save(E / 'freeze.json', {'revisions': REVISIONS, 'models': matrix.MODELS, 'effort': 'max', 'technical_fallback': 'high once only if technical failure', 'assignments': ASSIGNMENTS, 'logical_pairs': 6, 'new_planned_writer_calls': 12, 'hashes': hashes, 'product_differences': diff, 'runner_sha256': hashlib.sha256(source).hexdigest(), 'limit': 'Release public-baseline transfer check: five scenes plus ordinary request; unchanged public writing leaves/hooks. Supplement established multi-route atom and combination evidence.'})


def lane(i):
    receipts = []
    for j, case in enumerate(ASSIGNMENTS[i]):
        for arm in (['baseline', 'candidate'] if (i + j) % 2 == 0 else ['candidate', 'baseline']):
            r = matrix.run_one(i, case, arm); receipts.append(r)
            if not r['valid_final']:
                receipts.append(matrix.run_one(i, case, arm, 'high'))
    return receipts


if __name__ == '__main__':
    prepare()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(lane, range(5)))
    matrix.save(E / 'receipts.json', [r for lane_result in results for r in lane_result])
