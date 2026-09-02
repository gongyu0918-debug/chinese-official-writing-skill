from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BASE_RUNNER_PATH = REPO / "maintenance/tests/evidence/advisory-feedback-tone-r1/run_candidate.py"
SUITES = {
    "main": {
        "cases": HERE / "cases.json",
        "config": HERE / "candidate-config.json",
        "output": REPO / "output/advisory-feedback-heading-evidence-r1/candidate",
        "baseline": REPO / "output/advisory-feedback-heading-evidence-r1/baseline",
    },
    "opening": {
        "cases": HERE / "opening-cases.json",
        "config": HERE / "opening-candidate-config.json",
        "output": REPO / "output/advisory-feedback-heading-evidence-r1/opening-candidate",
        "baseline": REPO / "output/advisory-feedback-heading-evidence-r1/opening-baseline",
    },
}


def load_module(suite: str):
    selected = SUITES[suite]
    spec = importlib.util.spec_from_file_location(f"wr025c_candidate_{suite}", BASE_RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load runner: {BASE_RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.HERE = HERE
    module.REPO = REPO
    module.CASES_PATH = selected["cases"]
    module.CONFIG_PATH = selected["config"]
    module.OUTPUT_ROOT = selected["output"]
    module.BASELINE_OUTPUT = selected["baseline"]

    def load_cases_config() -> dict:
        config = json.loads(selected["cases"].read_text(encoding="utf-8"))
        for case in config["cases"]:
            case["prompt"] = (HERE / case["prompt_file"]).read_text(encoding="utf-8")
        return config

    module.load_cases_config = load_cases_config
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", required=True, choices=tuple(SUITES))
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--provider")
    action.add_argument("--summarize", action="store_true")
    args = parser.parse_args()
    module = load_module(args.suite)
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
