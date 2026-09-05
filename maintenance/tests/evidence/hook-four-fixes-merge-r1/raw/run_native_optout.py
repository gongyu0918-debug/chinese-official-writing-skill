"""Native opt-out control with a labeled cleanup-lock failure; no source rewrite."""
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "maintenance/tests/evidence/hook-four-fixes-r1/run_native_claude.py"
spec = importlib.util.spec_from_file_location("native_optout_base", SOURCE)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
read_json = runner.REAL.read_json

def optout_config(path):
    value = read_json(path)
    if Path(path).name == "case.json":
        value["prompt"] = "本次关闭Hook。" + value["prompt"]
    return value

runner.REAL.read_json = optout_config
fault = """if event.get('hook_event_name') == 'Stop':
    original_load = m._load_core_bridge
    def load_fault_bridge():
        core = original_load()
        def unavailable(*args):
            raise core.RecordLockUnavailable('injected cleanup-lock failure')
        core._redact_turn_data = unavailable
        return core
    m._load_core_bridge = load_fault_bridge
    injected = True
"""
runner.WRAPPER = runner.WRAPPER.replace("response=m.handle(event)", fault + "response=m.handle(event)")
sys.argv = [str(SOURCE), "--output", str(ROOT / "output/hook-four-fixes-r1/merge-check-r1/native-optout")]
runner.main()
