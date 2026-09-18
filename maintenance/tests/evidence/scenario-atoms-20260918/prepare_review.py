"""Prepare anonymous native draft pairs; this script makes no quality verdict."""
from pathlib import Path
import argparse
import hashlib
import json
import random
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RUNS = ROOT / 'output/scenario-atoms-native-20260918'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cases', nargs='+', required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--runs', nargs='+', default=['qwen', 'deepseek'])
    parser.add_argument('--skip-reviewed', action='store_true')
    args = parser.parse_args()
    seen = set()
    if args.skip_reviewed:
        for mapping_path in HERE.glob('blind-*-mapping.json'):
            seen.update(item['source'] for item in load(mapping_path))
    pairs = []
    for route in args.runs:
        run = RUNS / route
        binding = load(run / 'binding.json')
        for case in args.cases:
            if case not in binding['cases']:
                continue
            records = {}
            for arm in ('baseline', 'candidate'):
                paths = list(run.glob(f'm*-{case}-{arm}.result.json'))
                if len(paths) != 1:
                    raise ValueError(f'Incomplete or duplicate result: {route}/{case}/{arm}')
                record = load(paths[0])
                if record['invalid']:
                    raise ValueError(f'Technically invalid result: {paths[0]}')
                final = paths[0].with_name(paths[0].name.replace('.result.json', '.final.txt'))
                records[arm] = (record, final)
            if all(str(final) in seen for _, final in records.values()):
                continue
            pairs.append((binding['cases'][case], records))
    rng = random.Random('scenario-20260918-' + args.name)
    rng.shuffle(pairs)
    mapping, sections = [], []
    for number, (prompt, records) in enumerate(pairs, 1):
        sections.append(f'## 第{number}对\n\n任务：\n{prompt}\n')
        arms = list(records)
        rng.shuffle(arms)
        for label, arm in zip(('A', 'B'), arms):
            record, final = records[arm]
            draft = final.read_text(encoding='utf-8')
            draft = re.sub(r'\[([^\]]+)\]\([^\n]*?\)', r'[\1](本地稿件文件)', draft)
            draft = re.sub(r'[A-Za-z]:[^\n]*?\.(?:txt|md|docx)(?=[>),，\s]|$)', '本地稿件文件', draft)
            sections.append(f'### {label}\n\n{draft}\n')
            mapping.append({'pair': number, 'label': label, 'arm': arm,
                            'case': record['case'], 'model': record['model'],
                            'source': str(final), 'sha256': hashlib.sha256(final.read_bytes()).hexdigest()})
    packet = '\n'.join(sections)
    if '-baseline' in packet or '-candidate' in packet:
        raise ValueError('Identity remains in anonymous packet')
    work = RUNS / f'{args.name}-input'
    work.mkdir(exist_ok=True)
    (work / 'drafts.md').write_text(packet, encoding='utf-8')
    (HERE / f'{args.name}-packet.md').write_text(packet, encoding='utf-8')
    save(HERE / f'{args.name}-mapping.json', mapping)
    instructions = '''你是独立中文正式材料审阅者。本轮只读取工作目录中的 drafts.md（UTF-8），不查看目录外文件、模型、版本或映射，不调用其他 Skill，不改写原稿。
每对是同题独立真实写稿，A/B身份随机。逐对比较是否准确、自然、完整、能直接使用，注意主文种用途、执行主体与统计范围、事项前后时间关系及篇幅形式。写得更长、更多标题或更多检查不自动等于更好。
可以判相当。材料和常识支持的原因、目的、影响及拟议建议允许，不要求逐字来自材料；只有具体事实矛盾、无依据具体断言或把未定写成已定才据实指出。不要用法定模板缺省字段强迫短事务稿补齐未知事项。当前日期是2026年9月18日，正常落款允许沿用系统日期。
正文、文后提示、正文外文件链接分别判断。提示冗余可以指出，但不当作正文污染。审稿后改稿任务可以在正文外说明修改。不要因为句式相似或出现某个词就扣分。主送可以统称，正文已准确限定执行者时，不因称谓不同判错；有效材料已经明确的修正，应看是否落实到了改后正文，不能用文后提示中的可选修改冒充已完成。
每对写：正文 A较好/B较好/相当/无法判断；文后提示的差异；引用真实句子说明依据；如有严重问题说明是双方都有还是一方特有。不要猜匿名身份，不把审稿偏好冒充错误，不强凑胜负。最后简述共同风险，不宣称任何版本全面胜出。控制在2600汉字以内。
'''
    (HERE / f'{args.name}-prompt.txt').write_text(instructions, encoding='utf-8')
    print(json.dumps({'pairs': len(pairs), 'packet_sha256': hashlib.sha256(packet.encode()).hexdigest(), 'work': str(work)}))
