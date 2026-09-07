"""Experimental native Claude relay; no production files edited."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import uuid

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from revision_context import recover

event = json.load(sys.stdin)
root = Path(os.environ['CLAUDE_PLUGIN_ROOT'])
spec = importlib.util.spec_from_file_location('prototype_adapter', root / 'scripts/gate_stop_hook.py')
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
original_load = adapter._load_core_bridge
observation = {'event': event, 'prototype_context': None}


def load():
    core = original_load()
    original_handle = core.handle
    run = core._run_review_gate_subprocess

    def handle(mapped):
        record_path = core._record_path(mapped)
        record = core._read_json(record_path) or {} if record_path else {}
        if (mapped.get('hook_event_name') == 'Stop' and not record.get('txn')
                and not record.get('bypass') and not core._record_is_terminal(record)
                and record.get('request') and event.get('transcript_path')):
            context = recover(event['transcript_path'], event['session_id'], record['request'], core.SKILL_ROOT)
            if context:
                observation['prototype_context'] = {'turn_count': context['turn_count'], 'sha256': context['sha256']}
                record.update(skill_seen=True, source_text=context['source_text'], revision_context=observation['prototype_context'])
                core._write_record(record_path, record)

                def with_source(command, *args, **kwargs):
                    if 'detect' in command:
                        path = Path(command[command.index('--request') + 1]).with_name('source.txt')
                        path.write_text(context['source_text'], encoding='utf-8')
                        command = [*command, '--source', str(path)]
                    return run(command, *args, **kwargs)
                core._run_review_gate_subprocess = with_source
        result = original_handle(mapped)
        observation['mapped'] = mapped
        observation['record_after'] = core._read_json(record_path) if record_path else None
        return result
    core.handle = handle
    return core


adapter._load_core_bridge = load
result = adapter.handle(event)
observation['response'] = result
directory = Path(os.environ['COW_EXPERIMENT_EVENTS'])
directory.mkdir(parents=True, exist_ok=True)
(directory / (uuid.uuid4().hex + '.json')).write_text(json.dumps(observation, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
