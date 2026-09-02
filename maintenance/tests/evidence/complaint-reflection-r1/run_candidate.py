from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CASES_PATH = HERE / "cases.json"
CONFIG_PATH = HERE / "candidate-config.json"
OUTPUT_ROOT = REPO / "output/complaint-reflection-r1/candidate-r2"
BASELINE_OUTPUT = REPO / "output/complaint-reflection-r1/baseline-r2"
BASE_RUNNER_PATH = REPO / "maintenance/tests/evidence/reference-slimming-r2/run_probe.py"
DESKTOP_WRITER_PATH = HERE / "desktop_writer.py"


def load_cases_config() -> dict:
    config = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    for case in config["cases"]:
        case["prompt"] = (HERE / case["prompt_file"]).read_text(encoding="utf-8")
    return config


def load_base_runner():
    spec = importlib.util.spec_from_file_location("wr027_candidate", BASE_RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load runner: {BASE_RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO = REPO
    module.CASES_PATH = CASES_PATH
    module.OUTPUT_ROOT = OUTPUT_ROOT
    module.load_config = load_cases_config
    writer_spec = importlib.util.spec_from_file_location("wr027_desktop_writer_candidate", DESKTOP_WRITER_PATH)
    if writer_spec is None or writer_spec.loader is None:
        raise RuntimeError(f"cannot load writer adapter: {DESKTOP_WRITER_PATH}")
    writer_adapter = importlib.util.module_from_spec(writer_spec)
    writer_spec.loader.exec_module(writer_adapter)
    module.load_writer = lambda: writer_adapter.load_writer(REPO, CASES_PATH, OUTPUT_ROOT)
    return module


def git_text(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True, encoding="utf-8", check=True
    ).stdout.strip()


def load_inputs() -> tuple[dict, dict]:
    return load_cases_config(), json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def prepare() -> dict:
    if OUTPUT_ROOT.exists():
        raise RuntimeError(f"output already exists: {OUTPUT_ROOT}")
    if git_text("status", "--porcelain"):
        raise RuntimeError("worktree must be clean before fixture preparation")
    cases, config = load_inputs()
    baseline = git_text("rev-parse", f"{config['baseline_commit']}^{{commit}}")
    candidate = git_text("rev-parse", f"{config['candidate_commit']}^{{commit}}")
    changed = set(filter(None, git_text("diff", "--name-only", baseline, candidate, "--", "chinese-official-writing").splitlines()))
    expected = set(config["allowed_product_diff"])
    if changed != expected:
        raise RuntimeError(f"unexpected product diff: actual={sorted(changed)} expected={sorted(expected)}")

    base = load_base_runner()
    writer = base.load_writer()
    staging = OUTPUT_ROOT / "staging"
    exported = OUTPUT_ROOT / "exports/candidate"
    staging.mkdir(parents=True)
    exported.parent.mkdir(parents=True, exist_ok=True)
    writer.export_skill(candidate, exported, staging)
    count, fingerprint = writer.tree_fingerprint(exported)
    for provider_id in cases["providers"]:
        runtime = writer.runtime_root(provider_id, "candidate")
        skill_root = runtime / ".agents/skills/chinese-official-writing"
        skill_root.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(exported, skill_root)
        subprocess.run(["git", "init", "-q", str(runtime)], check=True)
    shutil.rmtree(staging)
    fixture = {
        "schema_version": 1,
        "baseline_commit": baseline,
        "candidate_commit": candidate,
        "changed_product": sorted(changed),
        "file_count": count,
        "tree_fingerprint": fingerprint,
        "providers": cases["providers"],
        "case_ids": [case["id"] for case in cases["cases"]],
    }
    (OUTPUT_ROOT / "fixture.json").write_text(json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return fixture


def run_provider(provider_id: str) -> dict:
    cases, _ = load_inputs()
    if provider_id not in cases["providers"]:
        raise RuntimeError(f"unknown provider: {provider_id}")
    if not (OUTPUT_ROOT / "fixture.json").is_file():
        raise RuntimeError("run --prepare first")
    result_path = OUTPUT_ROOT / "providers" / f"{provider_id}.json"
    if result_path.exists():
        raise RuntimeError(f"provider result already exists: {result_path}")
    result_path.parent.mkdir(parents=True, exist_ok=True)
    base = load_base_runner()
    writer = base.load_writer()
    records = []
    for case in cases["cases"]:
        record = writer.run_one(provider_id, cases["providers"][provider_id], "candidate", case, cases["reasoning_effort"])
        trace = (OUTPUT_ROOT / record["trace_file"]).read_text(encoding="utf-8", errors="replace")
        files, loaded_bytes = base.skill_reads(trace, writer.runtime_root(provider_id, "candidate"))
        record["atoms"] = case["atoms"]
        record["skill_files_read"] = files
        record["loaded_bytes"] = loaded_bytes
        records.append(record)
        result_path.write_text(json.dumps({"provider_id": provider_id, "records": records}, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return {"provider_id": provider_id, "record_count": len(records)}


def summarize() -> dict:
    cases, config = load_inputs()
    pairs = []
    missing = []
    for provider_id in cases["providers"]:
        baseline_path = BASELINE_OUTPUT / "providers" / f"{provider_id}.json"
        candidate_path = OUTPUT_ROOT / "providers" / f"{provider_id}.json"
        if not baseline_path.is_file() or not candidate_path.is_file():
            missing.append(provider_id)
            continue
        baseline_records = {item["case_id"]: item for item in json.loads(baseline_path.read_text(encoding="utf-8"))["records"]}
        candidate_records = {item["case_id"]: item for item in json.loads(candidate_path.read_text(encoding="utf-8"))["records"]}
        for case in cases["cases"]:
            baseline = baseline_records[case["id"]]
            candidate = candidate_records[case["id"]]
            pairs.append({
                "provider_id": provider_id,
                "case_id": case["id"],
                "technical_ok": not baseline["technical_failures"] and not candidate["technical_failures"],
                "baseline_files": baseline["skill_files_read"],
                "candidate_files": candidate["skill_files_read"],
                "baseline_hard_failures": baseline["hard_failures"],
                "candidate_hard_failures": candidate["hard_failures"],
                "baseline_chars": baseline["final_chars_nonspace"],
                "candidate_chars": candidate["final_chars_nonspace"],
                "baseline_file": baseline["final_file"],
                "candidate_file": candidate["final_file"],
            })
    read_counts = {}
    for case in cases["cases"]:
        counter = Counter()
        for pair in pairs:
            if pair["case_id"] == case["id"] and pair["technical_ok"]:
                counter.update(pair["candidate_files"])
        read_counts[case["id"]] = dict(sorted(counter.items()))
    summary = {
        "schema_version": 1,
        "baseline_commit": config["baseline_commit"],
        "candidate_commit": config["candidate_commit"],
        "missing_providers": missing,
        "pair_count": len(pairs),
        "technical_pair_count": sum(pair["technical_ok"] for pair in pairs),
        "candidate_read_counts_valid_pairs": read_counts,
        "pairs": pairs,
    }
    (OUTPUT_ROOT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return summary


def main() -> int:
    providers = tuple(load_inputs()[0]["providers"])
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--provider", choices=providers)
    action.add_argument("--summarize", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        result = prepare()
    elif args.provider:
        result = run_provider(args.provider)
    else:
        result = summarize()
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
