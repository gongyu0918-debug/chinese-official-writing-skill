from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
OUTPUT_ROOT = REPO / "output/mt004a-procurement-request-route-r1/baseline-probe"
SOURCE_SKILL = REPO / "chinese-official-writing"
CASES_PATH = HERE / "cases.json"
UPSTREAM = REPO / "maintenance/tests/evidence/v1615-like-signal-short-writing-r1/run_eval.py"
PROVIDER_ID = "alibaba1"
MODEL = "alibaba-token-plan/deepseek-v4-flash-0731"


def load_writer():
    spec = importlib.util.spec_from_file_location("mt004a_baseline_writer", UPSTREAM)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load writer: {UPSTREAM}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO = REPO
    module.OUTPUT_ROOT = OUTPUT_ROOT
    return module


def case() -> dict:
    data = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    return data["experiments"]["request-route"]["cases"][0]


def prepare() -> dict:
    if subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO, capture_output=True,
        text=True, encoding="utf-8", check=True,
    ).stdout.strip():
        raise RuntimeError("worktree must be clean")
    if OUTPUT_ROOT.exists():
        raise RuntimeError(f"output exists: {OUTPUT_ROOT}")
    runtime = OUTPUT_ROOT / "runtime" / PROVIDER_ID / "baseline"
    skill_root = runtime / ".agents/skills/chinese-official-writing"
    skill_root.parent.mkdir(parents=True)
    shutil.copytree(SOURCE_SKILL, skill_root)
    subprocess.run(["git", "init", "-q", str(runtime)], check=True)
    writer = load_writer()
    count, fingerprint = writer.tree_fingerprint(skill_root)
    result = {"file_count": count, "tree_fingerprint": fingerprint, "model": MODEL}
    (OUTPUT_ROOT / "fixture.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return result


def run() -> dict:
    if not (OUTPUT_ROOT / "fixture.json").is_file():
        raise RuntimeError("prepare first")
    writer = load_writer()
    record = writer.run_one(PROVIDER_ID, MODEL, "baseline", case(), "max")
    (OUTPUT_ROOT / "result.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--run", action="store_true")
    args = parser.parse_args()
    result = prepare() if args.prepare else run()
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
