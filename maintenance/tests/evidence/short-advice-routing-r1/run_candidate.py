from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BASE_RUNNER_PATH = REPO / "maintenance/tests/evidence/advisory-feedback-tone-r1/run_candidate.py"
ARMS = {
    "advisory": {
        "config": HERE / "advisory-config.json",
        "output": REPO / "output/short-advice-routing-r1/advisory-leaf",
    },
    "short": {
        "config": HERE / "short-config.json",
        "output": REPO / "output/short-advice-routing-r1/short-leaf",
    },
}
CASES_PATH = HERE / "cases.json"
BASELINE_OUTPUT = REPO / "output/short-advice-routing-r1/baseline"


def load_module(arm: str):
    selected = ARMS[arm]
    spec = importlib.util.spec_from_file_location(f"wr026_candidate_{arm}", BASE_RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load runner: {BASE_RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.HERE = HERE
    module.REPO = REPO
    module.CASES_PATH = CASES_PATH
    module.CONFIG_PATH = selected["config"]
    module.OUTPUT_ROOT = selected["output"]
    module.BASELINE_OUTPUT = BASELINE_OUTPUT

    def load_cases_config() -> dict:
        config = json.loads(CASES_PATH.read_text(encoding="utf-8"))
        for case in config["cases"]:
            case["prompt"] = (HERE / case["prompt_file"]).read_text(encoding="utf-8")
        return config

    module.load_cases_config = load_cases_config
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", required=True, choices=tuple(ARMS))
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--provider")
    action.add_argument("--summarize", action="store_true")
    args = parser.parse_args()
    module = load_module(args.arm)
    providers = tuple(module.load_inputs()[0]["providers"])
    if args.provider is not None and args.provider not in providers:
        parser.error(f"unknown provider {args.provider!r}; choose from {', '.join(providers)}")
    if args.prepare:
        result = module.prepare()
    elif args.provider:
        result = module.run_provider(args.provider)
    else:
        result = module.summarize()
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
