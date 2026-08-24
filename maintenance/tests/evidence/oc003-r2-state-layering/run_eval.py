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
OUTPUT_ROOT = REPO / "output" / "oc003-r2-state-layering"
UPSTREAM_PATH = REPO / "maintenance/tests/evidence/v1615-like-signal-short-writing-r1/run_eval.py"


def load_upstream():
    spec = importlib.util.spec_from_file_location("oc003_r2_upstream", UPSTREAM_PATH)
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


def prepare_arm(arm: str) -> dict:
    module = load_upstream()
    cases = load_cases()
    export = OUTPUT_ROOT / "exports" / arm
    if export.exists():
        raise RuntimeError(f"arm already prepared: {export}")
    export.parent.mkdir(parents=True, exist_ok=True)
    if arm == "baseline":
        staging = OUTPUT_ROOT / "staging-baseline"
        staging.mkdir(parents=True)
        archive = staging / "skill.zip"
        extracted = staging / "extracted"
        subprocess.run(
            ["git", "archive", "--format=zip", f"--output={archive}", cases["source_commit"], "chinese-official-writing"],
            cwd=REPO,
            check=True,
        )
        with zipfile.ZipFile(archive) as bundle:
            bundle.extractall(extracted)
        shutil.copytree(extracted / "chinese-official-writing", export)
        shutil.rmtree(staging)
    elif arm == "candidate":
        shutil.copytree(REPO / "chinese-official-writing", export)
    else:
        raise RuntimeError(f"unknown arm: {arm}")

    count, fingerprint = module.tree_fingerprint(export)
    for provider_id in cases["providers"]:
        root = OUTPUT_ROOT / "runtime" / provider_id / arm
        skill_root = root / ".agents/skills/chinese-official-writing"
        skill_root.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(export, skill_root)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
    fixture_path = OUTPUT_ROOT / "fixture.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8")) if fixture_path.is_file() else {"schema_version": 1, "arms": {}}
    fixture["arms"][arm] = {"file_count": count, "tree_fingerprint": fingerprint}
    fixture["providers"] = cases["providers"]
    fixture_path.write_text(json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return fixture["arms"][arm]


def run_provider(provider_id: str, arm: str) -> dict:
    module = load_upstream()
    cases = load_cases()
    result_path = OUTPUT_ROOT / "providers" / f"{provider_id}-{arm}.json"
    if result_path.exists():
        raise RuntimeError(f"provider result already exists: {result_path}")
    result_path.parent.mkdir(parents=True, exist_ok=True)
    records = [
        module.run_one(provider_id, cases["providers"][provider_id], arm, case, cases["reasoning_effort"])
        for case in cases["cases"]
    ]
    payload = {"provider_id": provider_id, "arm": arm, "records": records}
    result_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return payload


def summarize() -> dict:
    cases = load_cases()
    records = []
    for path in sorted((OUTPUT_ROOT / "providers").glob("*.json")):
        records.extend(json.loads(path.read_text(encoding="utf-8"))["records"])
    summary = {
        "schema_version": 1,
        "record_count": len(records),
        "technical_failure_count": sum(bool(item["technical_failures"]) for item in records),
        "hard_failure_count": sum(bool(item["hard_failures"]) for item in records),
        "records": records,
        "expected_providers": list(cases["providers"]),
    }
    (OUTPUT_ROOT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-arm", choices=("baseline", "candidate"))
    parser.add_argument("--provider", choices=tuple(load_cases()["providers"]))
    parser.add_argument("--arm", choices=("baseline", "candidate"))
    parser.add_argument("--summarize", action="store_true")
    args = parser.parse_args()
    if args.prepare_arm:
        result = prepare_arm(args.prepare_arm)
    elif args.provider and args.arm:
        result = run_provider(args.provider, args.arm)
    elif args.summarize:
        result = summarize()
    else:
        parser.error("use --prepare-arm, --provider with --arm, or --summarize")
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
