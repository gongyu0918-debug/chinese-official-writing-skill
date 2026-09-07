"""Read-only, isolated real-model checks for the two README routes."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'output/skill-package-readme-delivery'
HELPER = ROOT / 'maintenance/tests/evidence/v167-formulaic-mechanicality-real-first/harness.py'
spec = importlib.util.spec_from_file_location('readme_route_base', HELPER)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
base.TIMEOUT_SECONDS = 480
MODELS = {'alibaba2': 'alibaba-token-plan-2/deepseek-v4-flash-0731', 'minimax': 'minimax-cn/MiniMax-M3'}
CASES = {
    'capabilities': '这个中文公文写作 Skill 能帮我做什么？我只有一些零散想法，应该怎么请它帮我写稿？能写小说吗？',
    'hook-help': '这个中文公文写作 Skill 里的 Hook 主要做什么？安装 Skill 会自动启用吗？先只解释，不安装。',
    'draft-instead-of-faq': '我该怎么写这份申请？请直接替我写好，我只想要正文。资料室周内多场培训共用现有1块白板，需要往返搬运，现拟购移动白板2块，单价900元，费用拟从年度培训经费列支，采购尚未批准。',
}


def system_prompt(skill_root):
    return (f'本次只使用以下公文写作Skill，先用Read读取入口：{skill_root / "SKILL.md"}。'
            '根据用户实际问题，按入口自行选择需要的资料并答复。'
            '只读取该Skill目录；不联网，不读取其他Skill、用户文件、记忆或维护资料，不创建或修改文件、不运行命令。')


base.system_prompt = system_prompt


def freeze():
    shutil.copytree(ROOT / 'chinese-official-writing', OUT / 'skill', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    manifest = base.tree_manifest(OUT / 'skill')
    base.atomic_json(OUT / 'manifest.json', manifest)
    base.atomic_json(OUT / 'prompts.json', CASES)
    base.atomic_json(OUT / 'protocol.json', {'helper': str(HELPER.relative_to(ROOT)), 'helper_sha256': hashlib.sha256(HELPER.read_bytes()).hexdigest(), 'models': MODELS, 'tools': ['Read'], 'hook_execution': False, 'plugins': False, 'entry_explicit': True, 'timeout': 480, 'automatic_retries': 0})
    print(json.dumps({'frozen_files': len(manifest)}))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['freeze', 'run'])
    p.add_argument('--case', choices=CASES)
    p.add_argument('--treatment', choices=['candidate', 'baseline'], default='candidate')
    p.add_argument('--provider', choices=MODELS)
    args = p.parse_args()
    if args.action == 'freeze':
        freeze()
    else:
        case = {'id': args.case + '-' + args.provider, 'request': CASES[args.case], 'provider': args.provider, 'genre': 'skill-help' if args.case != 'draft-instead-of-faq' else 'application'}
        result = base.run_arm(shutil.which('claude'), OUT, OUT / 'runtime', {args.treatment: OUT / ('skill' if args.treatment == 'candidate' else 'baseline-skill')}, MODELS, case, args.treatment)
        assert base.tree_manifest(OUT / 'skill') == json.loads((OUT / 'manifest.json').read_text(encoding='utf-8'))
        print(json.dumps({k: result[k] for k in ['case_id', 'model', 'technical_valid', 'duration_seconds', 'checks']}, ensure_ascii=False))
