"""Compare 1.x and current 2.0 using real persisted Codex conversations."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def snapshot(ref, destination):
    commit = subprocess.check_output(['git', 'rev-parse', ref], cwd=ROOT, text=True).strip()
    files = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', commit, '--', 'chinese-official-writing'], cwd=ROOT, text=True).splitlines()
    hashes = {}
    for name in files:
        relative = Path(name).relative_to('chinese-official-writing')
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        data = subprocess.check_output(['git', 'show', f'{commit}:{name}'], cwd=ROOT)
        target.write_bytes(data)
        hashes[relative.as_posix()] = hashlib.sha256(data).hexdigest()
    return {'commit': commit, 'files': hashes}


def run_turn(command, prompt, workspace, environment, prefix, timeout):
    started = time.monotonic()
    error = None
    try:
        result = subprocess.run(command, input=prompt, text=True, encoding='utf-8', errors='replace', capture_output=True, cwd=workspace, env=environment, timeout=timeout)
        code, stdout, stderr = result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as exc:
        code, error = None, 'timeout'
        stdout, stderr = exc.stdout or b'', exc.stderr or b''
        stdout = stdout.decode('utf-8', 'replace') if isinstance(stdout, bytes) else stdout
        stderr = stderr.decode('utf-8', 'replace') if isinstance(stderr, bytes) else stderr
    prefix.with_suffix('.trace.jsonl').write_text(stdout, encoding='utf-8')
    prefix.with_suffix('.stderr.txt').write_text(stderr, encoding='utf-8')
    events = []
    for line in stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return {'returncode': code, 'error': error, 'seconds': round(time.monotonic() - started, 2), 'events': events}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--model', default='alibaba-token-plan-2/deepseek-v4.1-flash')
    parser.add_argument('--effort', default='high')
    parser.add_argument('--timeout', type=int, default=360)
    args = parser.parse_args()
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=False)
    runtime = Path(tempfile.mkdtemp(prefix='cow-multiturn-'))
    binding = json.loads((ROOT/'output/scenario-atoms-native-20260918/a-qwen/binding.json').read_text(encoding='utf-8'))
    cases = json.loads((HERE/'multiturn-cases.json').read_text(encoding='utf-8'))
    refs = {'v1': 'legacy/1.x', 'v2': '21f3de03'}
    frozen = {arm: snapshot(ref, out/'snapshots'/arm) for arm, ref in refs.items()}
    save(out/'binding.json', {'model': args.model, 'effort': args.effort, 'cli': binding['cli'], 'snapshots': frozen, 'cases': cases, 'runtime': str(runtime), 'method': 'exec first turn; exec resume exact thread id; separate profile and workspace per arm and case'})
    options = ['--skip-git-repo-check', '-m', args.model, '-c', f'model_reasoning_effort="{args.effort}"', '-c', 'features.plugins=false', '-c', 'features.apps=false', '-c', 'features.memories=false', '-c', 'features.multi_agent=false', '-c', 'web_search="disabled"', '-c', 'openai_base_url="http://127.0.0.1:10100/v1"', '-c', f'model_catalog_json="{(Path.home()/".codex/opencodex-catalog.json").as_posix()}"', '--json']
    records = []
    for case, turns in cases.items():
        # Reverse arm order for the second sequence to reduce simple order effects.
        for arm in (['v1', 'v2'] if case == 'structure' else ['v2', 'v1']):
            run = runtime/f'{case}-{arm}'
            workspace = run/'workspace'
            profile = run/'profile'
            profile.mkdir(parents=True)
            (profile/'config.toml').write_text('approval_policy="never"\nsandbox_mode="danger-full-access"\nproject_doc_max_bytes=0\n[windows]\nsandbox="unelevated"\n', encoding='utf-8')
            shutil.copytree(out/'snapshots'/arm, workspace/'.agents/skills/chinese-official-writing')
            environment = {**os.environ, 'CODEX_HOME': str(profile), 'OPENAI_API_KEY': 'opencodex-loopback', 'CODEX_API_KEY': 'opencodex-loopback'}
            session = None
            for number, user_prompt in enumerate(turns, 1):
                prefix = out/f'{case}-{arm}-{number}'
                final = prefix.with_suffix('.final.txt')
                prompt = ('请使用当前目录下 .agents/skills/chinese-official-writing/SKILL.md 及按需引用的规则完成写作任务。读取文本使用UTF-8。\n\n' if number == 1 else '') + user_prompt
                prefix.with_suffix('.prompt.txt').write_text(prompt, encoding='utf-8')
                command = [binding['cli'], 'exec']
                command += ['-C', str(workspace)] if session is None else ['resume']
                command += options + ['--output-last-message', str(final)]
                if session:
                    command.append(session)
                command.append('-')
                print(f'START {case} {arm} turn{number}', flush=True)
                result = run_turn(command, prompt, workspace, environment, prefix, args.timeout)
                ids = [event['thread_id'] for event in result['events'] if event.get('type') == 'thread.started']
                observed = ids[0] if ids else None
                invalid = []
                if result['returncode'] != 0 or result['error']:
                    invalid.append(result['error'] or f'exit_{result["returncode"]}')
                if not final.exists() or not final.read_text(encoding='utf-8').strip():
                    invalid.append('missing_final')
                if not observed or (session and session != observed):
                    invalid.append('session_not_resumed')
                session = observed or session
                row = {k: result[k] for k in ('returncode', 'error', 'seconds')}
                row.update(case=case, arm=arm, turn=number, session_id=session, invalid=invalid, command=command, prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest())
                row['commands'] = [event['item'] for event in result['events'] if event.get('type') == 'item.completed' and event.get('item', {}).get('type') == 'command_execution']
                row['usage'] = [event.get('usage') for event in result['events'] if event.get('type') == 'turn.completed']
                row['final_sha256'] = hashlib.sha256(final.read_bytes()).hexdigest() if final.exists() else None
                records.append(row)
                save(out/'calls.json', records)
                print(f'END {case} {arm} turn{number} invalid={invalid} seconds={row["seconds"]}', flush=True)
                if invalid:
                    break


if __name__ == '__main__':
    main()
