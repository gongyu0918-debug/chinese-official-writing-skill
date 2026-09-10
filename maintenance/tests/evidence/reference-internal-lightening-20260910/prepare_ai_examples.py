"""Prepare one structural atom; preserve all four examples verbatim."""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
E = Path(__file__).resolve().parent
p = ROOT / 'chinese-official-writing/references/ai-compute-docs.md'
text = p.read_text(encoding='utf-8')
examples = re.findall(r'^`[^\n]+`$', text, re.M)
assert len(examples) == 4
headings = ['需求表述', '成本与路径比较', 'SLA 与运维', '安全与合规']
example_page = '# 算力材料段落示例\n\n以下段落仅供结构和语气参考，示例中的场景、期限、安排和结论须有任务材料支持后才能用于正文。\n\n'
example_page += '\n\n'.join('## ' + title + '\n\n' + example for title, example in zip(headings, examples)) + '\n'
for example in examples:
    text = text.replace('\n' + example + '\n', '')
text = text.replace('优先从业务场景写需求，再落到资源指标。可采用：\n', '优先从业务场景写需求，再落到资源指标。\n')
text = text.replace('\n可采用：\n', '')
anchor = '术语只在非技术读者可能误解时解释。不要把正文写成 AI 科普、产品宣传或参数堆叠。'
text = text.replace(anchor, anchor + '\n\n需要参考完整段落写法时，选读 `ai-compute-examples.md` 中对应主题的示例；常规起草无需为此增加读取。')
text = re.sub(r'\n{3,}', '\n\n', text)
p.write_text(text, encoding='utf-8', newline='\n')
(p.parent / 'ai-compute-examples.md').write_text(example_page, encoding='utf-8', newline='\n')
old = json.loads((ROOT/'maintenance/tests/evidence/progressive-route-validation-20260910/combined-depth.json').read_text(encoding='utf-8'))
config = {
 'atom': 'ai-examples', 'baseline': '36653d768f8e9bf14bb615a642846e0db10b9f04', 'candidate': 'HEAD',
 'expected_diff': ['references/ai-compute-docs.md', 'references/ai-compute-examples.md'],
 'assignments': {'0':['technical_control'], '1':['cost_options'], '2':['example_requested'], '3':['technical_complete'], '4':['sparse_api']},
 'cases': {
  'technical_control': old['cases']['technical_control'],
  'cost_options': {'task':'请起草算力可研中的费用比较部分，直接输出正文，不列计算表或过程说明。已给材料：项目拟服务6个月；现阶段受控调用的API账单为每月2400元，扩展后的调用量尚未测定；GPU租赁报价每月8000元，报价仅包括GPU资源，存储、网络和运维费用未提供。现有材料未确定采用哪条路径。可以据上述数值做简单算术，说明费用能比较到什么程度，不能据此下定总费用或推荐结论，不补税费、合同条款、单位、期限或需求数据。'},
  'example_requested': {'task':'请参考 Skill 内算力材料的完整段落示例，为本单位起草一段可直接使用的“数据安全与服务管理”正文。只输出正文，不介绍或抄录样例。唯一材料：本次拟租用模型服务用于内部资料检索，拟处理的数据包括内部知识库和检索日志；现有方案要求两类数据均在本单位受控环境处理，项目管理员按现有权限表配置访问权限；数据导出条件尚未确定。示例仅供语气和结构参考，不补行业、跨区域限制、审计责任、合同义务或已完成结论。'},
  'technical_complete': {'task':'请把以下已确定条款整理为GPU租赁技术需求正文，分为资源、运维、验收三个自然段，不增加小标题或额外要求，只输出正文。材料：租期6个月，提供2张GPU，每张显存48GB，服务只用于模型推理；服务可用性不低于99.5%，故障响应时间不超过30分钟，恢复时间不超过4小时；验收由甲中心信息科负责，验收内容为资源规格核对、模型推理运行测试及运维文档交付。不得自行指定GPU品牌、训练或微调、并发压测、7×24值守、替代资源或安全配置条款。'},
  'sparse_api': {'task':'请将以下材料写成一段正式、简洁的模型API费用情况说明。只输出可直接使用的正文，不附说明，不列缺项清单。唯一事实：甲中心2026年8月试用模型API用于资料检索，当月实际支出2400元。试用范围和后续使用规模没有提供。不要扩写试用成效、费用增长、限额原因、预算、采购或后续安排，不把一个月的实际支出外推为月度标准或年度费用。'}
 }
}
(E/'ai-examples.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
runner = (ROOT/'maintenance/tests/evidence/progressive-route-validation-20260910/run_atom.py').read_text(encoding='utf-8')
runner = runner.replace("output/progressive-route-validation-20260910", "output/reference-internal-lightening-20260910")
(E/'run_atom.py').write_text(runner,encoding='utf-8',newline='\n')
print(json.dumps({'examples':len(examples),'examples_chars':sum(map(len,examples)),'ai_page_chars':len(text),'optional_page_chars':len(example_page)},ensure_ascii=False))
