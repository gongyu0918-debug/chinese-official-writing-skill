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
OUTPUT_ROOT = REPO / "output/post-v1623-cold-review-fixes-r1"
WRITER_PATH = REPO / "maintenance/tests/evidence/v1615-like-signal-short-writing-r1/run_eval.py"
PROBE_PATH = REPO / "maintenance/tests/evidence/reference-slimming-r2/run_probe.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


WRITER = load_module("cold_review_writer", WRITER_PATH)
PROBE = load_module("cold_review_probe", PROBE_PATH)
WRITER.REPO = REPO
WRITER.OUTPUT_ROOT = OUTPUT_ROOT


def git_text(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()


def load_cases() -> dict:
    config = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    for case in config["cases"]:
        case["prompt"] = (HERE / case["prompt_file"]).read_text(encoding="utf-8")
    return config


def prepare(baseline: str, candidate: str) -> dict:
    if OUTPUT_ROOT.exists():
        raise RuntimeError(f"output already exists: {OUTPUT_ROOT}")
    if git_text("status", "--porcelain"):
        raise RuntimeError("worktree must be clean before fixture preparation")
    baseline_commit = git_text("rev-parse", f"{baseline}^{{commit}}")
    candidate_commit = git_text("rev-parse", f"{candidate}^{{commit}}")
    changed = set(
        filter(
            None,
            git_text(
                "diff",
                "--name-only",
                baseline_commit,
                candidate_commit,
                "--",
                "chinese-official-writing",
            ).splitlines(),
        )
    )
    expected = {"chinese-official-writing/SKILL.md"}
    if changed != expected:
        raise RuntimeError(f"unexpected product diff: {sorted(changed)}")

    config = load_cases()
    staging = OUTPUT_ROOT / "staging"
    staging.mkdir(parents=True)
    fixture = {
        "schema_version": 1,
        "baseline_commit": baseline_commit,
        "candidate_commit": candidate_commit,
        "product_diff": sorted(changed),
        "providers": config["providers"],
        "case_ids": [case["id"] for case in config["cases"]],
        "arms_by_case": {case["id"]: case["arms"] for case in config["cases"]},
    }
    exports: dict[str, Path] = {}
    for arm, commit in (("baseline", baseline_commit), ("candidate", candidate_commit)):
        exported = OUTPUT_ROOT / "exports" / arm
        exported.parent.mkdir(parents=True, exist_ok=True)
        WRITER.export_skill(commit, exported, staging)
        count, fingerprint = WRITER.tree_fingerprint(exported)
        fixture[f"{arm}_file_count"] = count
        fixture[f"{arm}_fingerprint"] = fingerprint
        exports[arm] = exported

    for provider_id in config["providers"]:
        for arm, exported in exports.items():
            runtime = WRITER.runtime_root(provider_id, arm)
            skill_root = runtime / ".agents/skills/chinese-official-writing"
            skill_root.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(exported, skill_root)
            subprocess.run(["git", "init", "-q", str(runtime)], check=True)
    shutil.rmtree(staging)
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
    records = []
    provider_index = list(config["providers"]).index(provider_id)
    for case in config["cases"]:
        arms = list(case["arms"])
        if len(arms) == 2 and provider_index % 2:
            arms.reverse()
        for arm in arms:
            record = WRITER.run_one(
                provider_id,
                config["providers"][provider_id],
                arm,
                case,
                config["reasoning_effort"],
            )
            trace_path = OUTPUT_ROOT / record["trace_file"]
            trace = trace_path.read_text(encoding="utf-8", errors="replace")
            files, loaded_bytes = PROBE.skill_reads(trace, WRITER.runtime_root(provider_id, arm))
            record["atom"] = case["atom"]
            record["skill_files_read"] = files
            record["loaded_bytes"] = loaded_bytes
            records.append(record)
            result_path.write_text(
                json.dumps(
                    {"provider_id": provider_id, "records": records},
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
                newline="\n",
            )
    return {"provider_id": provider_id, "record_count": len(records)}


def summarize() -> dict:
    config = load_cases()
    all_records = []
    missing = []
    for provider_id in config["providers"]:
        path = OUTPUT_ROOT / "providers" / f"{provider_id}.json"
        if path.is_file():
            all_records.extend(json.loads(path.read_text(encoding="utf-8"))["records"])
        else:
            missing.append(provider_id)
    cases = {}
    for case in config["cases"]:
        records = [item for item in all_records if item["case_id"] == case["id"]]
        read_counts: dict[str, Counter] = {}
        for arm in case["arms"]:
            counter = Counter()
            for record in records:
                if record["arm"] == arm and not record["technical_failures"]:
                    counter.update(record["skill_files_read"])
            read_counts[arm] = counter
        cases[case["id"]] = {
            "atom": case["atom"],
            "arms": case["arms"],
            "valid_records": sum(not item["technical_failures"] for item in records),
            "technical_failures": sum(bool(item["technical_failures"]) for item in records),
            "hard_failures": sum(bool(item["hard_failures"]) for item in records),
            "read_counts": {
                arm: dict(sorted(counter.items())) for arm, counter in read_counts.items()
            },
            "records": [
                {
                    "provider_id": item["provider_id"],
                    "arm": item["arm"],
                    "technical_failures": item["technical_failures"],
                    "hard_failures": item["hard_failures"],
                    "final_chars_nonspace": item["final_chars_nonspace"],
                    "skill_files_read": item["skill_files_read"],
                    "loaded_bytes": item["loaded_bytes"],
                    "final_file": item["final_file"],
                    "trace_file": item["trace_file"],
                    "usage": item["usage"],
                }
                for item in records
            ],
        }
    summary = {
        "schema_version": 1,
        "fixture": json.loads((OUTPUT_ROOT / "fixture.json").read_text(encoding="utf-8")),
        "missing_providers": missing,
        "record_count": len(all_records),
        "technical_failure_count": sum(bool(item["technical_failures"]) for item in all_records),
        "hard_failure_count": sum(bool(item["hard_failures"]) for item in all_records),
        "cases": cases,
    }
    (OUTPUT_ROOT / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return summary


def main() -> int:
    config = load_cases()
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--provider", choices=tuple(config["providers"]))
    action.add_argument("--summarize", action="store_true")
    parser.add_argument("--baseline-commit")
    parser.add_argument("--candidate-commit")
    args = parser.parse_args()
    if args.prepare:
        if not args.baseline_commit or not args.candidate_commit:
            parser.error("--prepare requires --baseline-commit and --candidate-commit")
        result = prepare(args.baseline_commit, args.candidate_commit)
    elif args.provider:
        result = run_provider(args.provider)
    else:
        result = summarize()
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

