from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CASES_PATH = HERE / "cases.json"
CONFIG_PATH = HERE / "config.json"
BASE_RUNNER_PATH = REPO / "maintenance/tests/evidence/reference-slimming-r2/run_probe.py"
OUTPUTS = {
    "baseline": REPO / "output/short-route-semantic-r1/baseline",
    "candidate": REPO / "output/short-route-semantic-r1/candidate",
    "candidate-r2": REPO / "output/short-route-semantic-r1/candidate-r2b",
    "candidate-r3": REPO / "output/short-route-semantic-r1/candidate-r3",
}
MODE_COMMITS = {
    "baseline": "baseline_commit",
    "candidate": "candidate_commit",
    "candidate-r2": "candidate_r2_commit",
    "candidate-r3": "candidate_r3_commit",
}
R2_CASE_IDS = {
    "SEMANTIC-COMPACT-PURCHASE",
    "UPPER-480-SITUATION",
    "AROUND-360-NOTICE",
    "FACT-DENSE-COMPACT-REPORT",
    "UPPER-1500-FULL-SPEECH",
}
R3_CASE_IDS = {
    "SEMANTIC-COMPACT-PURCHASE",
    "UPPER-480-SITUATION",
    "UPPER-1500-FULL-SPEECH",
}


def git_text(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()


def load_static() -> tuple[dict, dict]:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return cases, config


def load_cases(mode: str) -> dict:
    cases, config = load_static()
    cases["baseline_commit"] = config[MODE_COMMITS[mode]]
    if mode == "candidate-r2":
        cases["cases"] = [case for case in cases["cases"] if case["id"] in R2_CASE_IDS]
    elif mode == "candidate-r3":
        cases["cases"] = [case for case in cases["cases"] if case["id"] in R3_CASE_IDS]
    for case in cases["cases"]:
        case["prompt"] = (HERE / case["prompt_file"]).read_text(encoding="utf-8")
    return cases


def load_runner(mode: str):
    spec = importlib.util.spec_from_file_location(f"short_route_{mode}", BASE_RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load runner: {BASE_RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO = REPO
    module.CASES_PATH = CASES_PATH
    module.OUTPUT_ROOT = OUTPUTS[mode]
    module.load_config = lambda: load_cases(mode)
    return module


def validate_candidate_diff(mode: str) -> None:
    _, config = load_static()
    baseline = git_text("rev-parse", f"{config['baseline_commit']}^{{commit}}")
    candidate_key = MODE_COMMITS[mode]
    candidate = git_text("rev-parse", f"{config[candidate_key]}^{{commit}}")
    changed = set(
        filter(
            None,
            git_text(
                "diff",
                "--name-only",
                baseline,
                candidate,
                "--",
                "chinese-official-writing",
            ).splitlines(),
        )
    )
    expected = set(config["allowed_product_diff"])
    if changed != expected:
        raise RuntimeError(
            f"unexpected product diff: actual={sorted(changed)} expected={sorted(expected)}"
        )


def compare(candidate_mode: str) -> dict:
    cases = load_cases(candidate_mode)
    _, config = load_static()
    pairs = []
    missing = []
    for provider_id in cases["providers"]:
        baseline_path = OUTPUTS["baseline"] / "providers" / f"{provider_id}.json"
        candidate_path = OUTPUTS[candidate_mode] / "providers" / f"{provider_id}.json"
        if not baseline_path.is_file() or not candidate_path.is_file():
            missing.append(provider_id)
            continue
        baseline_records = {
            item["case_id"]: item
            for item in json.loads(baseline_path.read_text(encoding="utf-8"))["records"]
        }
        candidate_records = {
            item["case_id"]: item
            for item in json.loads(candidate_path.read_text(encoding="utf-8"))["records"]
        }
        for case in cases["cases"]:
            baseline = baseline_records.get(case["id"])
            candidate = candidate_records.get(case["id"])
            if baseline is None or candidate is None:
                missing.append(f"{provider_id}:{case['id']}")
                continue
            pairs.append(
                {
                    "provider_id": provider_id,
                    "case_id": case["id"],
                    "technical_ok": not baseline["technical_failures"]
                    and not candidate["technical_failures"],
                    "baseline_files": baseline["skill_files_read"],
                    "candidate_files": candidate["skill_files_read"],
                    "baseline_hard_failures": baseline["hard_failures"],
                    "candidate_hard_failures": candidate["hard_failures"],
                    "baseline_chars": baseline["final_chars_nonspace"],
                    "candidate_chars": candidate["final_chars_nonspace"],
                    "baseline_file": baseline["final_file"],
                    "candidate_file": candidate["final_file"],
                }
            )
    read_counts = {}
    for case in cases["cases"]:
        counter = Counter()
        for pair in pairs:
            if pair["case_id"] == case["id"] and pair["technical_ok"]:
                counter.update(pair["candidate_files"])
        read_counts[case["id"]] = dict(sorted(counter.items()))
    result = {
        "schema_version": 1,
        "baseline_commit": config["baseline_commit"],
        "candidate_commit": config[MODE_COMMITS[candidate_mode]],
        "candidate_mode": candidate_mode,
        "missing": missing,
        "pair_count": len(pairs),
        "technical_pair_count": sum(item["technical_ok"] for item in pairs),
        "candidate_read_counts_valid_pairs": read_counts,
        "pairs": pairs,
    }
    suffixes = {"candidate": "", "candidate-r2": "-r2", "candidate-r3": "-r3"}
    suffix = suffixes[candidate_mode]
    output = REPO / f"output/short-route-semantic-r1/comparison{suffix}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return result


def main() -> int:
    cases, _ = load_static()
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=tuple(OUTPUTS))
    parser.add_argument(
        "--compare-mode",
        choices=("candidate", "candidate-r2", "candidate-r3"),
        default="candidate",
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--provider", choices=tuple(cases["providers"]))
    action.add_argument("--summarize", action="store_true")
    action.add_argument("--compare", action="store_true")
    args = parser.parse_args()
    if args.compare:
        result = compare(args.compare_mode)
    else:
        if args.mode is None:
            parser.error("--mode is required except with --compare")
        if args.mode != "baseline" and args.prepare:
            validate_candidate_diff(args.mode)
        runner = load_runner(args.mode)
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
