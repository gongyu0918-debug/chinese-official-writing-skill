import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(sys.argv[1])
SPEC = importlib.util.spec_from_file_location('cow_audit_gate', ROOT / 'chinese-official-writing/hooks/core/gate_stop_hook.py')
HOOK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HOOK)
REQUEST = '请写一则新闻稿。活动事实：中心在2026-09-05举办读书交流活动，共20人参加。日期格式示例（不属于活动事实）：2020年9月5日。'
DRAFT = '中心举办读书交流活动\n\n9月5日，中心举办读书交流活动，共20人参加。'
with tempfile.TemporaryDirectory(prefix='cow-date-repro-') as tmp:
    os.environ.update(COW_GATE_HOOK_DATA=tmp, PLUGIN_ROOT=str(Path(tmp) / 'plugin'), COW_GATE_CAPABILITY='delivery_review')
    def event(name, **kwargs):
        return dict(hook_event_name=name, session_id='audit-session', turn_id='date-turn', cwd=str(ROOT), **kwargs)
    HOOK.handle(event('UserPromptSubmit', prompt=REQUEST))
    skill = Path(os.environ['PLUGIN_ROOT']) / 'skills/chinese-official-writing/SKILL.md'
    HOOK.handle(event('PostToolUse', tool_input={'cmd': f'Get-Content "{skill}"'}, tool_response={'exit_code': 0}))
    response = HOOK.handle(event('Stop', stop_hook_active=False, last_assistant_message=DRAFT))
    record = HOOK._read_json(HOOK._record_path(event('Stop')))
    state = HOOK._read_json(Path(record['txn']) / 'state.json')
    selected = response['reason'].split('不要加说明：\n', 1)[1]
    print(json.dumps({'request': REQUEST, 'original_d0': DRAFT, 'selected_output': selected, 'snapshot_state': state['state'], 'selected_label': state.get('selected'), 'date_audit': record.get('source_bound_date'), 'bug_reproduced': '2020年9月5日' in selected}, ensure_ascii=False, indent=2))
    assert '2020年9月5日' in selected
    assert state['state'] == 'TERMINAL_D0'
