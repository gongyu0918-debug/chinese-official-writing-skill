"""Reuse the native isolated Codex runner with a bounded release-comparison case set."""
from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'maintenance/tests/evidence/mit-script-delivery-r1/run_eval.py'
spec = importlib.util.spec_from_file_location('r31_native_runner', SOURCE)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
runner.CASES.update(json.loads(Path(__file__).with_name('format-cases.json').read_text(encoding='utf-8')))

if __name__ == '__main__':
    runner.main()
