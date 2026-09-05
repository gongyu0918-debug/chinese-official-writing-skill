from pathlib import Path
import importlib.util
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from maintenance.tests.hook_companion_support import ASSEMBLER

arm = sys.argv[1]
target = OUT / ('protocol-' + arm)
target.mkdir(exist_ok=False)
source = OUT / 'frozen-baseline/chinese-official-writing/hooks/adapters' if arm == 'baseline' else ROOT / 'chinese-official-writing/hooks/adapters'
hard_stop = json.loads((OUT / 'hard-stop.json').read_text(encoding='utf8'))
rows = []
for host, relative in [('workbuddy', 'host_gate_adapter.py'), ('kimi-code', 'kimi-code/gate_stop_hook.py')]:
    spec = importlib.util.spec_from_file_location(host.replace('-', '_'), source / relative)
    module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    output = module._host_response(host, hard_stop) if host == 'workbuddy' else module._host_response(hard_stop)
    rows.append({'host': host, 'scope': 'DIRECT_MAPPING_NOT_NATIVE', 'input': hard_stop, 'output': output})
for host, relative, destination, core in [
    ('deepseek-harness', 'deepseek-harness/index.mjs', 'index.mjs', 'skills/chinese-official-writing/hooks/gate_stop_hook.py'),
    ('opencode', 'opencode/opencode_gate_plugin.js', '.opencode/plugins/chinese-official-writing-gate.js', '.opencode/skills/chinese-official-writing/hooks/gate_stop_hook.py'),
]:
    companion = target / host
    ASSEMBLER.assemble(host, companion)
    (companion / destination).write_bytes((source / relative).read_bytes())
    # Only the subprocess boundary is stubbed; payload comes from real-D0 core replay.
    (companion / core).write_text('import json,sys\ne=json.load(sys.stdin)\nprint(json.dumps(' + repr(hard_stop) + ' if e["hook_event_name"]=="Stop" else {"continue":True},ensure_ascii=False))\n', encoding='utf8')
    command = ['node', str(OUT / 'protocol_probe.mjs'), host, str(companion), str(target / (host + '-data')), str(OUT / 'd0.txt')]
    result = subprocess.run(command, cwd=ROOT, env=os.environ.copy(), capture_output=True, text=True, encoding='utf8', timeout=30)
    rows.append({'host': host, 'argv': command, 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
    (target / (host + '.json')).write_text(result.stdout, encoding='utf8')
    assert result.returncode == 0, result.stderr
(target / 'result.json').write_text(json.dumps({'arm': arm, 'model_calls': 0, 'rows': rows}, ensure_ascii=False, indent=2), encoding='utf8')
print(json.dumps(rows, ensure_ascii=False))
