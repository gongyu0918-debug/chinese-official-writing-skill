"""One exact-prompt repeat of the advisory unsupported-state expansion dispute; keep first results intact."""
import concurrent.futures
import hashlib
import importlib.util
import json
import subprocess
import time
from pathlib import Path

spec = importlib.util.spec_from_file_location('gaps', Path(__file__).with_name('run_trial.py'))
gaps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gaps)
OUT = gaps.ROOT / 'output/skill-lightening-merge-check/repeats'
TARGETS = [(2, 'advisory')]


def one(i, case, arm):
    source = gaps.OUT / 'runs' / str(i) / case / arm / 'max'
    # The original runner writes a CRLF file on Windows but sends the LF string.
    prompt = (source / 'prompt.txt').read_text(encoding='utf-8').encode('utf-8')
    original = json.loads((source / 'receipt.json').read_text(encoding='utf-8'))
    assert original['valid_final']
    assert hashlib.sha256(prompt).hexdigest() == original['prompt_sha256']
    d = OUT / str(i) / case / arm
    d.mkdir(parents=True, exist_ok=False)
    for sub in ['codex-home', 'work', 'temp', 'profile/AppData/Roaming', 'profile/AppData/Local']:
        (d / sub).mkdir(parents=True, exist_ok=True)
    (d / 'codex-home/config.toml').write_text('project_doc_max_bytes = 0\n', encoding='utf-8')
    (d / 'prompt.txt').write_bytes(prompt)
    model = gaps.matrix.MODELS[i]
    argv = [str(gaps.matrix.native.CLI), 'exec', '-m', model, '-c', 'model_reasoning_effort="max"', '-c', 'openai_base_url="http://127.0.0.1:10100/v1"', '-c', 'model_catalog_json="' + (gaps.OUT / f'catalog-{i}.json').as_posix() + '"', '--dangerously-bypass-approvals-and-sandbox', '--skip-git-repo-check', '--json', '--color', 'never', '-o', str(d / 'final.txt'), '-']
    start = time.monotonic()
    with (d / 'trace.jsonl').open('wb') as stdout, (d / 'stderr.txt').open('wb') as stderr:
        try:
            r = subprocess.run(argv, input=prompt, cwd=d / 'work', env=gaps.matrix.native.environment(d), stdout=stdout, stderr=stderr, timeout=300)
            code, error = r.returncode, None
        except subprocess.TimeoutExpired:
            code, error = None, 'timeout_300s'
    receipt = {'provider': i, 'model': model, 'case': case, 'arm': arm, 'effort': 'max', 'original': str(source), 'prompt_sha256': hashlib.sha256(prompt).hexdigest(), 'original_prompt_sha256': original['prompt_sha256'], 'exit_code': code, 'error': error, 'seconds': round(time.monotonic() - start, 2)}
    assert receipt['prompt_sha256'] == receipt['original_prompt_sha256']
    gaps.matrix.save(d / 'receipt.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False), flush=True)
    return receipt


def lane(target):
    i, case = target
    return [one(i, case, arm) for arm in ['candidate', 'baseline']]


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=False)
    gaps.matrix.save(OUT / 'preregister.json', {'targets': TARGETS, 'reason': ['Candidate adds current daily-operation claims and drops the explicitly undecided technical plan/person/time state; baseline retains the undecided state. Repeat both frozen prompts once without repairing writing rules.'], 'changes': 'none; same prompt bytes, frozen product, model and effort', 'limit': 'one repeated pair per selected signal, no fishing for a pass; repetition cannot prove causality'})
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        results = list(pool.map(lane, TARGETS))
    gaps.matrix.save(OUT / 'receipts.json', [r for lane_result in results for r in lane_result])
