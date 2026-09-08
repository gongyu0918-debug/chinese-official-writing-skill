"""Reuse committed writing/extraction protocols; freeze the speech role/state refinement."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
OUT = ROOT / 'output/experience-report-r3'
BASELINE = '05c4465fe6aa6187f31f0879120cc616a6f31e63'
HARNESS_COMMIT = '7bde6c3e4bbd87a304d01d74be178673fe048f67'
HARNESS_ROOT = Path('F:/Workspaces/chinese-official-writing-skill-worktrees/application-rule-combine-r24')
RUNNER = 'maintenance/tests/evidence/application-route-rewrite-r20/run_real.py'
EXTRACTOR = 'maintenance/tests/evidence/application-rule-efficacy-r23/archive_actual.py'
MODELS = {'qwen': 'alibaba-token-plan/qwen3.8-max', 'sol': 'gpt-5.6-sol'}
CASES = ('experience', 'leader-report')
OVERLAYS = ('references/formulaic-language.md',)
ADDED = ''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def load(relative):
    path = HARNESS_ROOT / relative
    expected = subprocess.check_output(['git', 'show', HARNESS_COMMIT + ':' + relative], cwd=ROOT)
    assert path.read_bytes().replace(b'\r\n', b'\n') == expected
    spec = importlib.util.spec_from_file_location('r26_' + path.parent.name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prepare():
    OUT.mkdir(parents=True, exist_ok=False)
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASELINE, '--', 'chinese-official-writing'], cwd=ROOT, text=True).splitlines()
    for arm in ('baseline', 'candidate'):
        plugin = OUT / 'plugins' / arm
        save(plugin / '.claude-plugin/plugin.json', {'name': 'official-writing-eval', 'version': '1.0.0', 'description': '中文公文写作测试副本'})
        manifest = []
        for name in names + (['chinese-official-writing/' + ADDED] if arm == 'candidate' and ADDED else []):
            rel = Path(name).relative_to('chinese-official-writing')
            if 'hooks' in rel.parts:
                continue
            data = ((EVIDENCE / 'prototype' / rel).read_bytes().replace(b'\r\n', b'\n') if arm == 'candidate' and rel.as_posix() in OVERLAYS
                    else subprocess.check_output(['git', 'show', BASELINE + ':' + name], cwd=ROOT))
            path = plugin / 'skills/chinese-official-writing' / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            manifest.append({'path': rel.as_posix(), 'bytes': len(data), 'sha256': sha(data)})
        save(OUT / (arm + '-manifest.json'), manifest)
    for case in CASES:
        path = OUT / 'prompts' / (case + '.txt')
        path.parent.mkdir(exist_ok=True)
        path.write_bytes((EVIDENCE / 'prompts' / (case + '.txt')).read_bytes())
    base = json.loads((OUT / 'baseline-manifest.json').read_text())
    candidate = json.loads((OUT / 'candidate-manifest.json').read_text())
    before = {row['path']: row['sha256'] for row in base}
    after = {row['path']: row['sha256'] for row in candidate}
    assert {name for name in before.keys() | after.keys() if before.get(name) != after.get(name)} == set(OVERLAYS)
    save(OUT / 'freeze.json', {'baseline_commit': BASELINE, 'candidate_base_commit': BASELINE,
        'overlay_paths': OVERLAYS, 'models': MODELS, 'cases': CASES, 'new_calls': 4,
        'harness_commit': HARNESS_COMMIT, 'harness_source_hashes': {p: sha((HARNESS_ROOT / p).read_bytes()) for p in (RUNNER, EXTRACTOR)},
        'prompt_hashes': {c: sha((OUT / 'prompts' / (c + '.txt')).read_bytes()) for c in CASES},
        'preregister_sha256': sha((EVIDENCE / 'preregister.md').read_bytes()),
        'hook_enabled': False, 'automatic_retries': 0, 'timeout_seconds': 1200, 'effort': 'max'})
    print(json.dumps({'prepared': True, 'files_per_arm': len(base), 'changed_files': OVERLAYS}), flush=True)


def suite():
    runner = load(RUNNER)
    runner.OUT, runner.MODELS = OUT, MODELS
    def provider_lane(provider):
        for number, case in enumerate(CASES):
            arms = ('candidate',)
            for arm in arms:
                runner.run(arm, provider, case, client_tools='Read,Skill')
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(provider_lane, MODELS))


def archive():
    extractor = load(EXTRACTOR)
    extractor.SOURCE, extractor.DEST, extractor.MODELS = OUT, EVIDENCE / 'actual', MODELS
    rows = [extractor.archive_lane(p.parent) for p in sorted((OUT / 'runs').rglob('receipt.json'))]
    save(EVIDENCE / 'actual/summary.json', {'expected': 4, 'completed': len(rows), 'runs': rows})
    for name in ('freeze.json', 'baseline-manifest.json', 'candidate-manifest.json'):
        (EVIDENCE / 'actual' / name).write_bytes((OUT / name).read_bytes())
    for arm in ('baseline', 'candidate'):
        for relative in OVERLAYS:
            target = EVIDENCE / 'actual/snapshots' / arm / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((OUT / 'plugins' / arm / 'skills/chinese-official-writing' / relative).read_bytes())
    print(json.dumps({'archived': len(rows), 'technical_valid': sum(r['technical_valid'] for r in rows)}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('prepare', 'suite', 'archive'))
    globals()[parser.parse_args().action]()
