"""Minimal sequential prototype: existing default gate after real cleaned body."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


core = load('after_clean_core', ROOT / 'chinese-official-writing/hooks/core/gate_stop_hook.py')
real = load('after_clean_real', ROOT / 'maintenance/tests/evidence/date-source-real-r1/run.py')
fixture = json.loads((OUT / 'fixture.json').read_text(encoding='utf-8'))
target = OUT / 'integrated-default'
target.mkdir(exist_ok=False)
(target / 'preregister.json').write_text(json.dumps({
    'plan': 'Actual full D0 -> integrated default prepass -> ordinary gate. Reuse three genuine cleanliness replies only after byte-exact prompt comparison; new independent real model replies for default repair/echo. No retries or native host claim.',
    'cases': ['P6', 'M6'], 'maximum_calls_per_case': 3,
}), encoding='utf-8')
for name, folder in [('P6', 'r1/P6'), ('M6', 'r2-full/M6')]:
    case = next(c for c in fixture['cases'] if c['id'] == name)
    d0 = (OUT / folder / 'final-visible.txt').read_text(encoding='utf-8')
    assert d0 == case['expected']
    directory = target / name
    directory.mkdir()
    events = []
    current = case['d0']
    with tempfile.TemporaryDirectory() as data:
        os.environ['COW_GATE_HOOK_DATA'] = data
        os.environ['COW_GATE_CAPABILITY'] = 'delivery_review'
        common = {'session_id': name, 'turn_id': 'after-clean', 'cwd': str(ROOT)}
        core.handle(dict(common, hook_event_name='UserPromptSubmit', prompt=case['request']))
        core.handle(dict(common, hook_event_name='PostToolUse', tool_input={'command': str(core.SKILL_ROOT / 'SKILL.md')}, tool_response={'exit_code': 0}))
        status = 'ceiling'
        for index in range(7):
            response = core.handle(dict(common, hook_event_name='Stop', last_assistant_message=current, stop_hook_active=index > 0))
            events.append({'index': index, 'response': response, 'record': copy.deepcopy(core._read_json(core._record_path(common)))})
            (directory / 'events.json').write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding='utf-8')
            if response.get('decision') != 'block':
                status = 'complete'
                break
            if index == 6:
                break
            if index < 3:
                saved = OUT / folder / 'calls' / str(index + 1)
                assert response['reason'] == (saved / 'prompt.txt').read_text(encoding='utf-8')
                current = (saved / 'reply.txt').read_text(encoding='utf-8')
                continue
            try:
                current, receipt = real.restricted_reply(fixture['models'][case['provider']], response['reason'], directory / 'calls' / str(index + 1), shutil.which('claude'))
            except Exception as exc:
                status = type(exc).__name__
                break
        result = {'status': status, 'original_clean_body_unchanged': current == d0, 'record': core._read_json(core._record_path(common))}
        (directory / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        (directory / 'last-response.txt').write_text(current, encoding='utf-8')
        print(json.dumps({'case': name, 'status': status, 'body_unchanged': current == d0}), flush=True)
