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
OUTPUT_ROOT = REPO / "output/remediation-plan-r1/baseline"
BASE_RUNNER_PATH = REPO / "maintenance/tests/evidence/reference-slimming-r2/run_probe.py"
DESKTOP_WRITER_PATH = REPO / "maintenance/tests/evidence/complaint-reflection-r1/desktop_writer.py"


def load_cases() -> dict:
    config = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    for case in config["cases"]:
        case["prompt"] = (HERE / case["prompt_file"]).read_text(encoding="utf-8")
    return config


def load_base_runner():
    spec = importlib.util.spec_from_file_location("wr028_baseline", BASE_RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load runner: {BASE_RUNNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO = REPO
    module.CASES_PATH = CASES_PATH
    module.OUTPUT_ROOT = OUTPUT_ROOT
    module.load_config = load_cases

    writer_spec = importlib.util.spec_from_file_location("wr028_desktop_writer", DESKTOP_WRITER_PATH)
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


def prepare() -> dict:
    if OUTPUT_ROOT.exists():
        raise RuntimeError(f"output already exists: {OUTPUT_ROOT}")
    if git_text("status", "--porcelain"):
        raise RuntimeError("worktree must be clean before fixture preparation")
    config = load_cases()
    baseline = git_text("rev-parse", f"{config['baseline_commit']}^{{commit}}")
    if baseline != config["baseline_commit"]:
        raise RuntimeError(f"baseline mismatch: {baseline}")

    base = load_base_runner()
    writer = base.load_writer()
    staging = OUTPUT_ROOT / "staging"
    exported = OUTPUT_ROOT / "exports/baseline"
    staging.mkdir(parents=True)
    exported.parent.mkdir(parents=True, exist_ok=True)
    writer.export_skill(baseline, exported, staging)
    count, fingerprint = writer.tree_fingerprint(exported)
    for provider_id in config["providers"]:
        runtime = writer.runtime_root(provider_id, "baseline")
        skill_root = runtime / ".agents/skills/chinese-official-writing"
        skill_root.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(exported, skill_root)
        subprocess.run(["git", "init", "-q", str(runtime)], check=True)
    shutil.rmtree(staging)
    fixture = {
        "schema_version": 1,
        "baseline_commit": baseline,
        "file_count": count,
        "tree_fingerprint": fingerprint,
        "providers": config["providers"],
        "case_ids": [case["id"] for case in config["cases"]],
    }
    (OUTPUT_ROOT / "fixture.json").write_text(
        json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return fixture


def run_provider(provider_id: str) -> dict:
    config = load_cases()
    if provider_id not in config["providers"]:
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
    for case in config["cases"]:
        record = writer.run_one(
            provider_id, config["providers"][provider_id], "baseline", case, config["reasoning_effort"]
        )
        trace = (OUTPUT_ROOT / record["trace_file"]).read_text(encoding="utf-8", errors="replace")
        files, loaded_bytes = base.skill_reads(trace, writer.runtime_root(provider_id, "baseline"))
        record["atoms"] = case["atoms"]
        record["skill_files_read"] = files
        record["loaded_bytes"] = loaded_bytes
        records.append(record)
        result_path.write_text(
            json.dumps({"provider_id": provider_id, "records": records}, ensure_ascii=False, indent=2),
            encoding="utf-8",
            newline="\n",
        )
    return {"provider_id": provider_id, "record_count": len(records)}


def summarize() -> dict:
    config = load_cases()
    records = []
    missing = []
    for provider_id in config["providers"]:
        path = OUTPUT_ROOT / "providers" / f"{provider_id}.json"
        if path.is_file():
            records.extend(json.loads(path.read_text(encoding="utf-8"))["records"])
        else:
            missing.append(provider_id)
    read_counts: dict[str, Counter] = {}
    for record in records:
        read_counts.setdefault(record["case_id"], Counter()).update(record["skill_files_read"])
    summary = {
        "schema_version": 1,
        "baseline_commit": config["baseline_commit"],
        "missing_providers": missing,
        "record_count": len(records),
        "technical_failure_count": sum(bool(item["technical_failures"]) for item in records),
        "hard_failure_count_observation_only": sum(bool(item["hard_failures"]) for item in records),
        "cases": {
            case["id"]: {
                "valid_records": sum(
                    item["case_id"] == case["id"] and not item["technical_failures"] for item in records
                ),
                "read_counts": dict(sorted(read_counts.get(case["id"], Counter()).items())),
                "records": [
                    {
                        "provider_id": item["provider_id"],
                        "technical_failures": item["technical_failures"],
                        "hard_failures": item["hard_failures"],
                        "final_chars_nonspace": item["final_chars_nonspace"],
                        "skill_files_read": item["skill_files_read"],
                        "loaded_bytes": item["loaded_bytes"],
                        "usage": item["usage"],
                        "final_file": item["final_file"],
                        "trace_file": item["trace_file"],
                    }
                    for item in records
                    if item["case_id"] == case["id"]
                ],
            }
            for case in config["cases"]
        },
    }
    (OUTPUT_ROOT / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return summary


def main() -> int:
    providers = tuple(load_cases()["providers"])
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
