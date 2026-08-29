from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BASE_CASES_PATH = HERE / "cases.json"
AB_CONFIG_PATH = HERE / "ab_config.json"
BASE_RUNNER_PATH = REPO / "maintenance/tests/evidence/reference-slimming-r1/run_eval.py"
OUTPUT_BASE_ROOT = REPO / "output/reference-slimming-r2/ai-basic-ab"
RUN_ROUND = "r1"


def current_output_base() -> Path:
    return OUTPUT_BASE_ROOT if RUN_ROUND == "r1" else OUTPUT_BASE_ROOT.with_name(f"ai-basic-ab-{RUN_ROUND}")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalized_config() -> dict:
    base = json.loads(BASE_CASES_PATH.read_text(encoding="utf-8"))
    ab = json.loads(AB_CONFIG_PATH.read_text(encoding="utf-8"))
    existing = {case["id"]: case for case in base["cases"]}
    cases = []
    for plan in ab["case_plan"]:
        arms = plan.get(f"arms_{RUN_ROUND}", plan["arms"])
        if not arms:
            continue
        if plan["id"] in existing:
            case = copy.deepcopy(existing[plan["id"]])
            case.update({key: value for key, value in plan.items() if key not in {"id"}})
        else:
            case = copy.deepcopy(plan)
        case["arms"] = arms
        cases.append(case)
    return {
        "schema_version": 1,
        "reasoning_effort": base["reasoning_effort"],
        "providers": base["providers"],
        "experiments": {
            ab["experiment_id"]: {
                "allowed_product_diff": ab["allowed_product_diff"],
                "tracked_files": ab["tracked_files"],
                "cases": cases,
            }
        },
    }


def load_runner():
    runner = load_module("reference_slimming_r2_base", BASE_RUNNER_PATH)
    runner.REPO = REPO
    runner.CASES_PATH = AB_CONFIG_PATH
    runner.OUTPUT_BASE = current_output_base()
    runner.load_config = normalized_config
    runner.experiment_config = lambda experiment_id: normalized_config()["experiments"][experiment_id]
    return runner


def run_provider(experiment_id: str, provider_id: str) -> dict:
    runner = load_runner()
    config = normalized_config()
    experiment = config["experiments"][experiment_id]
    if provider_id not in config["providers"]:
        raise RuntimeError(f"unknown provider: {provider_id}")
    root = runner.output_root(experiment_id)
    if not (root / "fixture.json").is_file():
        raise RuntimeError("run --prepare first")
    result_path = root / "providers" / f"{provider_id}.json"
    if result_path.exists():
        raise RuntimeError(f"provider result already exists: {result_path}")
    result_path.parent.mkdir(parents=True, exist_ok=True)
    writer = runner.load_writer(experiment_id)
    provider_index = list(config["providers"]).index(provider_id)
    preferred = ["baseline", "candidate"] if provider_index % 2 == 0 else ["candidate", "baseline"]
    records = []
    for case in experiment["cases"]:
        arms = [arm for arm in preferred if arm in case["arms"]]
        for arm in arms:
            record = writer.run_one(
                provider_id,
                config["providers"][provider_id],
                arm,
                case,
                config["reasoning_effort"],
            )
            trace_path = root / record["trace_file"]
            trace = trace_path.read_text(encoding="utf-8", errors="replace")
            files, loaded_bytes = runner.read_files_from_trace(trace, writer.runtime_root(provider_id, arm))
            record["experiment_id"] = experiment_id
            record["case_kind"] = case["kind"]
            record["skill_files_read"] = files
            record["tracked_loaded_bytes"] = loaded_bytes
            final_path = root / record["final_file"]
            final = final_path.read_text(encoding="utf-8", errors="replace") if final_path.is_file() else ""
            record["output_shape_failures"] = runner.missing_groups(case.get("output_shape_groups", []), final)
            records.append(record)
            result_path.write_text(
                json.dumps({"provider_id": provider_id, "records": records}, ensure_ascii=False, indent=2),
                encoding="utf-8",
                newline="\n",
            )
    return {"provider_id": provider_id, "record_count": len(records)}


def summarize(experiment_id: str) -> dict:
    runner = load_runner()
    config = normalized_config()
    experiment = config["experiments"][experiment_id]
    records = []
    missing = []
    for provider_id in config["providers"]:
        path = runner.output_root(experiment_id) / "providers" / f"{provider_id}.json"
        if path.is_file():
            records.extend(json.loads(path.read_text(encoding="utf-8"))["records"])
        else:
            missing.append(provider_id)
    indexed = {(item["provider_id"], item["case_id"], item["arm"]): item for item in records}
    pairs = []
    for provider_id in config["providers"]:
        for case in experiment["cases"]:
            if set(case["arms"]) != {"baseline", "candidate"}:
                continue
            baseline = indexed.get((provider_id, case["id"], "baseline"))
            candidate = indexed.get((provider_id, case["id"], "candidate"))
            if baseline is None or candidate is None:
                continue
            pairs.append(
                {
                    "provider_id": provider_id,
                    "case_id": case["id"],
                    "technical_ok": not baseline["technical_failures"] and not candidate["technical_failures"],
                    "baseline_files": baseline["skill_files_read"],
                    "candidate_files": candidate["skill_files_read"],
                    "baseline_loaded_bytes": baseline["tracked_loaded_bytes"],
                    "candidate_loaded_bytes": candidate["tracked_loaded_bytes"],
                    "loaded_bytes_delta": candidate["tracked_loaded_bytes"] - baseline["tracked_loaded_bytes"],
                    "baseline_hard_failures": baseline["hard_failures"],
                    "candidate_hard_failures": candidate["hard_failures"],
                    "baseline_chars": baseline["final_chars_nonspace"],
                    "candidate_chars": candidate["final_chars_nonspace"],
                }
            )
    summary = {
        "schema_version": 1,
        "experiment_id": experiment_id,
        "missing_providers": missing,
        "record_count": len(records),
        "technical_failure_count": sum(bool(item["technical_failures"]) for item in records),
        "hard_failure_count_observation_only": sum(bool(item["hard_failures"]) for item in records),
        "pairs": pairs,
        "records": records,
    }
    root = runner.output_root(experiment_id)
    (root / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return summary


def main() -> int:
    global RUN_ROUND
    config = normalized_config()
    experiment_id = next(iter(config["experiments"]))
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", choices=("r1", "r2"), default="r1")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", nargs=2, metavar=("BASELINE", "CANDIDATE"))
    action.add_argument("--provider", choices=tuple(config["providers"]))
    action.add_argument("--summarize", action="store_true")
    args = parser.parse_args()
    RUN_ROUND = args.round
    if args.prepare:
        result = load_runner().prepare(experiment_id, args.prepare[0], args.prepare[1])
    elif args.provider:
        result = run_provider(experiment_id, args.provider)
    else:
        result = summarize(experiment_id)
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
