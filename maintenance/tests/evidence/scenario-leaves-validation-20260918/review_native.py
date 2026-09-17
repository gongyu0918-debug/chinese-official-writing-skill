"""Run a bounded independent review through plaintext native Codex CLI."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', required=True)
    parser.add_argument('--prompt', required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--effort', default='max')
    parser.add_argument('--timeout', type=int, default=360)
    args = parser.parse_args()
    work = Path(args.work).resolve()
    prompt = Path(args.prompt).read_text(encoding='utf-8')
    binding = json.loads((ROOT / 'output/scenario-native-20260918/qwen/binding.json').read_text(encoding='utf-8'))
    runtime = Path(tempfile.mkdtemp(prefix='cow-scenario-review-'))
    (runtime / 'config.toml').write_text('approval_policy="never"\nsandbox_mode="danger-full-access"\nproject_doc_max_bytes=0\n[windows]\nsandbox="unelevated"\n', encoding='utf-8')
    final = HERE / f'{args.name}.md'
    command = [binding['cli'], 'exec', '--ephemeral', '--skip-git-repo-check', '-C', str(work),
               '-m', 'alibaba-token-plan-2/deepseek-v4.1-flash', '-c', f'model_reasoning_effort="{args.effort}"',
               '-c', 'features.plugins=false', '-c', 'features.apps=false', '-c', 'features.memories=false',
               '-c', 'features.multi_agent=false', '-c', 'web_search="disabled"',
               '-c', 'openai_base_url="http://127.0.0.1:10100/v1"', '-c', f'model_catalog_json="{(Path.home()/".codex/opencodex-catalog.json").as_posix()}"',
               '--json', '--output-last-message', str(final), '-']
    started = time.monotonic()
    error = None
    try:
        done = subprocess.run(command, input=prompt, text=True, encoding='utf-8', errors='replace',
                              capture_output=True, cwd=work, timeout=args.timeout,
                              env={**os.environ, 'CODEX_HOME': str(runtime), 'OPENAI_API_KEY': 'opencodex-loopback', 'CODEX_API_KEY': 'opencodex-loopback'})
        code, stdout, stderr = done.returncode, done.stdout, done.stderr
    except subprocess.TimeoutExpired as exc:
        code, error = None, 'timeout'
        stdout, stderr = exc.stdout or b'', exc.stderr or b''
        stdout = stdout.decode('utf-8', 'replace') if isinstance(stdout, bytes) else stdout
        stderr = stderr.decode('utf-8', 'replace') if isinstance(stderr, bytes) else stderr
    logs = ROOT / 'output/scenario-native-20260918/reviews'
    logs.mkdir(exist_ok=True)
    (logs / f'{args.name}.trace.jsonl').write_text(stdout, encoding='utf-8')
    (logs / f'{args.name}.stderr.txt').write_text(stderr, encoding='utf-8')
    receipt = {'model': 'alibaba-token-plan-2/deepseek-v4.1-flash', 'effort': args.effort,
               'seconds': round(time.monotonic()-started, 2), 'exit_code': code, 'error': error,
               'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(), 'command': command,
               'final_sha256': hashlib.sha256(final.read_bytes()).hexdigest() if final.exists() else None}
    (HERE / f'{args.name}-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k!='command'}, ensure_ascii=False))
