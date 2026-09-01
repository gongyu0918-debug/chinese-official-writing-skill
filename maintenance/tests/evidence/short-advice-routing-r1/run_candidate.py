from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BASE_RUNNER_PATH = REPO / "maintenance/tests/evidence/advisory-feedback-tone-r1/run_candidate.py"
ARMS = {
    "advisory-r3": {
        "config": HERE / "advisory-r3-config.json",
        "output": REPO / "output/short-advice-routing-r1/advisory-leaf-r3",
    },
    "advisory-r2": {
        "config": HERE / "advisory-r2-config.json",
        "output": REPO / "output/short-advice-routing-r1/advisory-leaf-r2",
    },
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
BASELINE_OUTPUT = Path(
    os.environ.get(
        "WR026_BASELINE_OUTPUT",
        REPO / "output/short-advice-routing-r1/baseline",
    )
)


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


def summarize(module) -> dict:
    cases_config, config, cases = module.load_inputs()
    pairs = []
    missing_providers = []
    missing_case_pairs = []
    for provider_id in cases_config["providers"]:
        baseline_path = module.BASELINE_OUTPUT / "providers" / f"{provider_id}.json"
        candidate_path = module.OUTPUT_ROOT / "providers" / f"{provider_id}.json"
        if not baseline_path.is_file() or not candidate_path.is_file():
            missing_providers.append(provider_id)
            continue
        baseline_records = {
            item["case_id"]: item
            for item in json.loads(baseline_path.read_text(encoding="utf-8"))["records"]
        }
        candidate_records = {
            item["case_id"]: item
            for item in json.loads(candidate_path.read_text(encoding="utf-8"))["records"]
        }
        for case in cases:
            baseline = baseline_records.get(case["id"])
            candidate = candidate_records.get(case["id"])
            if baseline is None or candidate is None:
                missing_case_pairs.append({"provider_id": provider_id, "case_id": case["id"]})
                continue
            pairs.append(
                {
                    "provider_id": provider_id,
                    "case_id": case["id"],
                    "technical_ok": not baseline["technical_failures"]
                    and not candidate["technical_failures"],
                    "baseline_files": baseline["skill_files_read"],
                    "candidate_files": candidate["skill_files_read"],
                    "baseline_loaded_bytes": baseline["loaded_bytes"],
                    "candidate_loaded_bytes": candidate["loaded_bytes"],
                    "baseline_hard_failures": baseline["hard_failures"],
                    "candidate_hard_failures": candidate["hard_failures"],
                    "baseline_chars": baseline["final_chars_nonspace"],
                    "candidate_chars": candidate["final_chars_nonspace"],
                    "baseline_file": baseline["final_file"],
                    "candidate_file": candidate["final_file"],
                }
            )
    read_counts = {}
    for case in cases:
        counter = Counter()
        for pair in pairs:
            if pair["case_id"] == case["id"] and pair["technical_ok"]:
                counter.update(pair["candidate_files"])
        read_counts[case["id"]] = dict(sorted(counter.items()))
    summary = {
        "schema_version": 1,
        "baseline_commit": config["baseline_commit"],
        "candidate_commit": config["candidate_commit"],
        "missing_providers": missing_providers,
        "missing_case_pairs": missing_case_pairs,
        "pair_count": len(pairs),
        "technical_pair_count": sum(pair["technical_ok"] for pair in pairs),
        "candidate_read_counts_valid_pairs": read_counts,
        "pairs": pairs,
    }
    (module.OUTPUT_ROOT / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return summary


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
        result = summarize(module)
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
