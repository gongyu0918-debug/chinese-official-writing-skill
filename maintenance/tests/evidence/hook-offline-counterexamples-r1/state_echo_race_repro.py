import importlib.util
import json
import os
import sys
import tempfile
import threading
from pathlib import Path
from unittest import mock

ROOT = Path(sys.argv[1])
SPEC = importlib.util.spec_from_file_location('cow_audit_gate', ROOT / 'chinese-official-writing/hooks/core/gate_stop_hook.py')
HOOK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HOOK)
REQUEST = '请起草一份情况报告。材料：测试工作已完成。'
DRAFT = '情况报告\n\n测试工作已完成。'
WRONG = '错误回显：该项目已批准采购。'
with tempfile.TemporaryDirectory(prefix='cow-state-repro-') as tmp:
    os.environ.update(COW_GATE_HOOK_DATA=tmp, PLUGIN_ROOT=str(Path(tmp) / 'plugin'), COW_GATE_CAPABILITY='delivery_review')
    def event(name, turn, **kwargs):
        return dict(hook_event_name=name, session_id='audit-session', turn_id=turn, cwd=str(ROOT), **kwargs)
    def start(turn):
        HOOK.handle(event('UserPromptSubmit', turn, prompt=REQUEST))
        skill = Path(os.environ['PLUGIN_ROOT']) / 'skills/chinese-official-writing/SKILL.md'
        HOOK.handle(event('PostToolUse', turn, tool_input={'cmd': f'Get-Content "{skill}"'}, tool_response={'exit_code': 0}))
        response = HOOK.handle(event('Stop', turn, stop_hook_active=False, last_assistant_message=DRAFT))
        return response['reason'].split('不要加说明：\n', 1)[1]
    selected = start('wrong-echo')
    responses = []
    for attempt in range(1, 5):
        response = HOOK.handle(event('Stop', 'wrong-echo', stop_hook_active=True, last_assistant_message=WRONG))
        record = HOOK._read_json(HOOK._record_path(event('Stop', 'wrong-echo')))
        responses.append({'attempt': attempt, 'response': response.get('decision', 'allow'), 'phase': record.get('hook_phase'), 'verified': record.get('delivery_verified'), 'stop_attempts': record.get('stop_attempts'), 'raw_retained': 'txn' in record})
    print(json.dumps({'case': 'wrong_final_budget', 'request': REQUEST, 'selected_output': selected, 'last_assistant_message': WRONG, 'events': responses, 'final_response': response}, ensure_ascii=False))
    assert response == {'continue': True} and record['delivery_verified'] is False
    assert 'txn' not in record

    selected = start('late-tool-race')
    paused = threading.Event()
    resume = threading.Event()
    errors = []
    original_atomic = HOOK._atomic_write
    def delayed_atomic(path, value):
        if threading.current_thread().name == 'late-tool':
            paused.set()
            if not resume.wait(10):
                raise TimeoutError('audit coordination timeout')
        return original_atomic(path, value)
    def late_post_tool():
        try:
            HOOK.handle(event('PostToolUse', 'late-tool-race', tool_input={'cmd': 'Get-Content supporting-material.txt'}, tool_response={'exit_code': 0}))
        except Exception as error:
            errors.append(repr(error))
    with mock.patch.object(HOOK, '_atomic_write', side_effect=delayed_atomic):
        worker = threading.Thread(target=late_post_tool, name='late-tool')
        worker.start()
        assert paused.wait(10)
        response = HOOK.handle(event('Stop', 'late-tool-race', stop_hook_active=True, last_assistant_message=selected))
        before = HOOK._read_json(HOOK._record_path(event('Stop', 'late-tool-race')))
        resume.set()
        worker.join(10)
        assert not worker.is_alive() and not errors
    after_stop = HOOK.handle(event('Stop', 'late-tool-race', stop_hook_active=True, last_assistant_message=selected))
    after = HOOK._read_json(HOOK._record_path(event('Stop', 'late-tool-race')))
    print(json.dumps({'case': 'late_post_tool_overwrites_terminal', 'request': REQUEST, 'original_draft': DRAFT, 'terminal_before_late_write': before.get('data_retention_state'), 'request_before_late_write': 'request' in before, 'request_after_next_stop': after.get('request'), 'emitted_output_after_next_stop': after.get('emitted_output'), 'txn_directory_exists': Path(after['txn']).exists(), 'phase_after_next_stop': after.get('hook_phase'), 'redacted_state_after_next_stop': after.get('data_retention_state'), 'next_stop_response': after_stop}, ensure_ascii=False))
    assert 'request' not in before and after.get('request') == REQUEST
    assert after.get('emitted_output') == selected and after_stop == {'continue': True}
