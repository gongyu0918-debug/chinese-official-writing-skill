from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CASES_PATH = HERE / "cases.json"
OUTPUT_ROOT = REPO / "output/advisory-feedback-heading-evidence-r1/baseline"
BASE_RUNNER_PATH = REPO / "maintenance/tests/evidence/reference-slimming-r2/run_probe.py"


def load_config() -> dict:
    config = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    for case in config["cases"]:
        case["prompt"] = (HERE / case["prompt_file"]).read_text(encoding="utf-8")
    return config


def load_runner():
    spec = importlib.util.spec_from_file_location("wr025c_baseline", BASE_RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load runner: {BASE_RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO = REPO
    module.CASES_PATH = CASES_PATH
    module.OUTPUT_ROOT = OUTPUT_ROOT
    module.load_config = load_config
    return module


def main() -> int:
    config = load_config()
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--provider", choices=tuple(config["providers"]))
    action.add_argument("--summarize", action="store_true")
    args = parser.parse_args()
    runner = load_runner()
    if args.prepare:
        result = runner.prepare()
    elif args.provider:
        result = runner.run_provider(args.provider)
    else:
        result = runner.summarize()
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

