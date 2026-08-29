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
CONFIG_PATH = HERE / "cases.json"
OUTPUT_ROOT = REPO / "output/short-inference-r1"
UPSTREAM_PATH = REPO / "maintenance/tests/evidence/v1615-like-signal-short-writing-r1/run_eval.py"


def load_upstream():
    spec = importlib.util.spec_from_file_location("short_inference_writer", UPSTREAM_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load writer: {UPSTREAM_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO = REPO
    module.CASES_PATH = CONFIG_PATH
    module.OUTPUT_ROOT = OUTPUT_ROOT
    return module


def config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def git_text(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True,
        encoding="utf-8", check=True,
    ).stdout.strip()


def runtime_root(provider_id: str, arm: str) -> Path:
    return OUTPUT_ROOT / "runtime" / provider_id / arm


def prepare_arm(arm: str) -> dict:
    data = config()
    if arm not in data["arms"]:
        raise RuntimeError(f"unknown arm: {arm}")
    if git_text("status", "--porcelain"):
        raise RuntimeError("worktree must be clean before fixture preparation")
    destination = OUTPUT_ROOT / "exports" / arm
    if destination.exists():
        raise RuntimeError(f"arm already prepared: {destination}")
    commit = git_text("rev-parse", f"{data['arms'][arm]['commit']}^{{commit}}")
    if commit != data["arms"][arm]["commit"]:
        raise RuntimeError(f"commit mismatch for {arm}: {commit}")
    staging = OUTPUT_ROOT / "staging" / arm
    archive = staging / f"{arm}.zip"
    extracted = staging / "extracted"
    staging.mkdir(parents=True)
    subprocess.run(
        ["git", "archive", "--format=zip", f"--output={archive}", commit, "chinese-official-writing"],
        cwd=REPO, check=True,
    )
    with zipfile.ZipFile(archive) as bundle:
        bundle.extractall(extracted)
    shutil.copytree(extracted / "chinese-official-writing", destination)
    writer = load_upstream()
    count, fingerprint = writer.tree_fingerprint(destination)
    for provider_id in data["providers"]:
        root = runtime_root(provider_id, arm)
        skill_root = root / ".agents/skills/chinese-official-writing"
        skill_root.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(destination, skill_root)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
    shutil.rmtree(staging)
    fixture = {
        "schema_version": 1, "arm": arm, "commit": commit,
        "file_count": count, "tree_fingerprint": fingerprint,
    }
    fixture_path = OUTPUT_ROOT / "fixtures" / f"{arm}.json"
    fixture_path.parent.mkdir(parents=True, exist_ok=True)
    fixture_path.write_text(json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return fixture


def run_provider(arm: str, provider_id: str) -> dict:
    data = config()
    if provider_id not in data["providers"]:
        raise RuntimeError(f"unknown provider: {provider_id}")
    if not (OUTPUT_ROOT / "fixtures" / f"{arm}.json").is_file():
        raise RuntimeError(f"prepare {arm} first")
    result_path = OUTPUT_ROOT / "providers" / f"{provider_id}-{arm}.json"
    if result_path.exists():
        raise RuntimeError(f"result exists: {result_path}")
    result_path.parent.mkdir(parents=True, exist_ok=True)
    writer = load_upstream()
    records = []
    for case in data["cases"]:
        records.append(writer.run_one(provider_id, data["providers"][provider_id], arm, case, data["reasoning_effort"]))
        result_path.write_text(
            json.dumps({"provider_id": provider_id, "arm": arm, "records": records}, ensure_ascii=False, indent=2),
            encoding="utf-8", newline="\n",
        )
    return {"provider_id": provider_id, "arm": arm, "record_count": len(records)}


def summarize() -> dict:
    data = config()
    records = []
    missing = []
    for arm in data["arms"]:
        for provider_id in data["providers"]:
            path = OUTPUT_ROOT / "providers" / f"{provider_id}-{arm}.json"
            if path.is_file():
                records.extend(json.loads(path.read_text(encoding="utf-8"))["records"])
            else:
                missing.append(f"{provider_id}:{arm}")
    result = {
        "schema_version": 1,
        "missing": missing,
        "record_count": len(records),
        "technical_failure_count": sum(bool(item["technical_failures"]) for item in records),
        "hard_failure_count_observation_only": sum(bool(item["hard_failures"]) for item in records),
        "records": records,
    }
    (OUTPUT_ROOT / "summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n",
    )
    return result


def main() -> int:
    data = config()
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=tuple(data["arms"]))
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--provider", choices=tuple(data["providers"]))
    action.add_argument("--summarize", action="store_true")
    args = parser.parse_args()
    if args.summarize:
        result = summarize()
    elif not args.arm:
        parser.error("--arm is required for --prepare and --provider")
    elif args.prepare:
        result = prepare_arm(args.arm)
    else:
        result = run_provider(args.arm, args.provider)
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
