"""Thin natural-prompt wrapper over the repository's real persistent CLI runner."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess

ROOT = Path.cwd().resolve()
SOURCE = ROOT / 'maintenance/tests/evidence/revision-stability-audit-r1/run_chain.py'
spec = importlib.util.spec_from_file_location('natural_chain', SOURCE)
chain = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chain)


def save(path, value):
    chain.BASE.write_json(path, value)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(output, config_path, arm, commit):
    config = json.loads(config_path.read_text(encoding='utf-8'))
    for case in config['cases']:
        for turn in case['rounds']:
            assert not any(term in turn['prompt'] for term in ('Skill', 'skill', 'references/', 'SKILL.md', '使用当前'))
    target = output / f'fixture-{arm}.json'
    assert not target.exists(), target
    cli, version = chain.BASE.load_module('natural_desktop', chain.BASE.WRITER_PATH).desktop_codex()
    writer = chain.BASE.load_writer(output)
    export = output / 'exports' / arm
    staging = output / 'staging' / arm
    staging.mkdir(parents=True)
    writer.export_skill(commit, export, staging)
    count, fingerprint = writer.tree_fingerprint(export)
    for case in config['cases']:
        case_writer = chain.BASE.load_writer(output / case['id'])
        for provider in config['providers']:
            runtime = case_writer.runtime_root(provider, arm)
            skill = runtime / '.agents/skills/chinese-official-writing'
            skill.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(export, skill)
            subprocess.run(['git', 'init', '-q', str(runtime)], check=True)
    fixture = {'schema_version': 1, 'config': config, 'cli': str(cli), 'cli_version': version,
               'arms': {arm: {'commit': commit, 'file_count': count, 'tree_fingerprint': fingerprint}},
               'sources_sha256': {str(p): digest(p) for p in
                                  (config_path, Path(__file__), SOURCE, chain.BASE_PATH,
                                   chain.BASE.WRITER_PATH, chain.BASE.PROBE_PATH, Path(writer.__file__))},
               'context_method': 'Skill installed and discoverable; natural language only; real same-thread exec resume',
               'hook_mode': 'No Hook; plugins/apps/memories disabled; other installed Skills disabled',
               'activation_policy': 'Missing natural activation is an observed outcome, not discarded as technical failure.'}
    save(target, fixture)
    print(json.dumps({'prepared': arm, 'commit': commit, 'expected_turns': 20}), flush=True)


def run(output, arm, provider):
    fixture = json.loads((output / f'fixture-{arm}.json').read_text(encoding='utf-8'))
    for path, sha in fixture['sources_sha256'].items():
        assert digest(Path(path)) == sha, path
    for scenario in fixture['config']['cases']:
        case_output = output / scenario['id']
        writer = chain.BASE.load_writer(case_output)
        runtime = writer.runtime_root(provider, arm)
        assert writer.tree_fingerprint(runtime / '.agents/skills/chinese-official-writing')[1] == fixture['arms'][arm]['tree_fingerprint']
        receipt = case_output / 'sessions' / f'{provider}-{arm}.json'
        assert not receipt.exists(), receipt
        payload = {'provider_id': provider, 'arm': arm, 'scenario': scenario['id'], 'thread_id': None, 'records': []}
        for case in scenario['rounds']:
            record = chain.run_round(case_output, fixture, provider, arm, case, payload['thread_id'], writer)
            missing_activation = 'missing_initial_successful_skill_read'
            record['activation_observations'] = [missing_activation] if missing_activation in record['technical_failures'] else []
            record['technical_failures'] = [x for x in record['technical_failures'] if x != missing_activation]
            if record['technical_failures'] == ['missing_final']:
                record['technical_failures'] = []
                record['delivery_observations'] = ['completed_turn_without_final_body']
            payload['thread_id'] = payload['thread_id'] or record['thread_id']
            payload['records'].append(record)
            save(receipt, payload)
            print(json.dumps({'provider': provider, 'arm': arm, 'case': scenario['id'],
                              'round': case['round'], 'chars': record['final_chars_nonspace'],
                              'reads': record['skill_files_read'], 'technical': record['technical_failures'],
                              'activation': record['activation_observations']}, ensure_ascii=False), flush=True)
            if record['technical_failures']:
                break


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--arm', choices=('baseline', 'candidate'), required=True)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--prepare', action='store_true')
    actions.add_argument('--provider', choices=('alibaba2', 'minimax'))
    parser.add_argument('--config', type=Path)
    parser.add_argument('--commit')
    args = parser.parse_args()
    if args.prepare:
        assert args.config and args.commit
        prepare(args.output.resolve(), args.config.resolve(), args.arm, args.commit)
    else:
        run(args.output.resolve(), args.arm, args.provider)


if __name__ == '__main__':
    main()
