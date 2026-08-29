from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CASES_PATH = HERE / "cases.json"
OUTPUT_ROOT = REPO / "output" / "ah002-news-date-completeness-r1" / "baseline"
UPSTREAM_PATH = REPO / "maintenance/tests/evidence/v1615-like-signal-short-writing-r1/run_eval.py"


def load_upstream():
    spec = importlib.util.spec_from_file_location("ah002_upstream", UPSTREAM_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load upstream runner: {UPSTREAM_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO = REPO
    module.CASES_PATH = CASES_PATH
    module.OUTPUT_ROOT = OUTPUT_ROOT
    return module


def load_cases() -> dict:
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def git_text(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()


def prepare() -> dict:
    if OUTPUT_ROOT.exists():
        raise RuntimeError(f"output already exists: {OUTPUT_ROOT}")
    cases = load_cases()
    source_commit = git_text("rev-parse", f"{cases['source_commit']}^{{commit}}")
    if source_commit != cases["source_commit"]:
        raise RuntimeError(f"source commit mismatch: {source_commit}")

    staging = OUTPUT_ROOT / "staging"
    staging.mkdir(parents=True)
    archive = staging / "skill.zip"
    extracted = staging / "extracted"
    subprocess.run(
        ["git", "archive", "--format=zip", f"--output={archive}", source_commit, "chinese-official-writing"],
        cwd=REPO,
        check=True,
    )
    with zipfile.ZipFile(archive) as bundle:
        bundle.extractall(extracted)
    export = OUTPUT_ROOT / "export"
    shutil.copytree(extracted / "chinese-official-writing", export)
    shutil.rmtree(staging)

    engine = load_upstream()
    for provider_id in cases["providers"]:
        root = engine.runtime_root(provider_id, "baseline")
        skill_root = root / ".agents" / "skills" / "chinese-official-writing"
        skill_root.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(export, skill_root)
        subprocess.run(["git", "init", "-q", str(root)], check=True)

    count, fingerprint = engine.tree_fingerprint(export)
    fixture = {
        "schema_version": 1,
        "source_commit": source_commit,
        "file_count": count,
        "tree_fingerprint": fingerprint,
        "providers": cases["providers"],
        "initial_providers": cases["initial_providers"],
    }
    (OUTPUT_ROOT / "fixture.json").write_text(
        json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return fixture


def run_provider(provider_id: str) -> dict:
    cases = load_cases()
    if provider_id not in cases["providers"]:
        raise RuntimeError(f"unknown provider: {provider_id}")
    if not (OUTPUT_ROOT / "fixture.json").is_file():
        raise RuntimeError("run --prepare first")
    result_path = OUTPUT_ROOT / "providers" / f"{provider_id}.json"
    if result_path.exists():
        raise RuntimeError(f"provider result already exists: {result_path}")
    result_path.parent.mkdir(parents=True, exist_ok=True)
    engine = load_upstream()
    records = []
    for case in cases["cases"]:
        record = engine.run_one(
            provider_id,
            cases["providers"][provider_id],
            "baseline",
            case,
            cases["reasoning_effort"],
        )
        records.append(record)
        result_path.write_text(
            json.dumps({"provider_id": provider_id, "records": records}, ensure_ascii=False, indent=2),
            encoding="utf-8",
            newline="\n",
        )
    return {"provider_id": provider_id, "records": records}


def summarize() -> dict:
    cases = load_cases()
    records = []
    missing = []
    for provider_id in cases["providers"]:
        path = OUTPUT_ROOT / "providers" / f"{provider_id}.json"
        if path.is_file():
            records.extend(json.loads(path.read_text(encoding="utf-8"))["records"])
        else:
            missing.append(provider_id)

    case_by_id = {case["id"]: case for case in cases["cases"]}
    for record in records:
        case = case_by_id[record["case_id"]]
        final_path = OUTPUT_ROOT / record["final_file"]
        final = final_path.read_text(encoding="utf-8", errors="replace") if final_path.is_file() else ""
        record["full_date_present"] = case["full_date"] in final
        record["short_date_count"] = final.count(case["short_date"])
        record["natural_repair_target"] = (
            not record["technical_failures"]
            and not record["full_date_present"]
            and record["short_date_count"] == 1
        )

    summary = {
        "schema_version": 1,
        "missing_providers": missing,
        "record_count": len(records),
        "technical_failure_count": sum(bool(item["technical_failures"]) for item in records),
        "full_date_present_count": sum(bool(item["full_date_present"]) for item in records),
        "natural_repair_target_count": sum(bool(item["natural_repair_target"]) for item in records),
        "records": records,
    }
    (OUTPUT_ROOT / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--provider", choices=tuple(load_cases()["providers"]))
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
