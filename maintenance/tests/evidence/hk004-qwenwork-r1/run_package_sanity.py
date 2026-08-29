from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
OUTPUT_ROOT = REPO / "output/hk004-qwenwork-r1"
SOURCE_SKILL = REPO / "packages/qwenwork/skills/chinese-official-writing"
CASE_PATH = HERE / "package-sanity-case.json"
UPSTREAM_PATH = REPO / "maintenance/tests/evidence/v1615-like-signal-short-writing-r1/run_eval.py"
PROVIDER_ID = "alibaba-token-plan-2"
MODEL = "alibaba-token-plan-2/deepseek-v4-flash-0731"


def load_writer():
    spec = importlib.util.spec_from_file_location("qwenwork_package_writer", UPSTREAM_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load writer: {UPSTREAM_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO = REPO
    module.OUTPUT_ROOT = OUTPUT_ROOT
    return module


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
    if git_text("status", "--porcelain"):
        raise RuntimeError("worktree must be clean before fixture preparation")
    if OUTPUT_ROOT.exists():
        raise RuntimeError(f"output already exists: {OUTPUT_ROOT}")
    runtime = OUTPUT_ROOT / "runtime" / PROVIDER_ID / "qwenwork"
    skill_root = runtime / ".agents/skills/chinese-official-writing"
    skill_root.parent.mkdir(parents=True)
    shutil.copytree(SOURCE_SKILL, skill_root)
    subprocess.run(["git", "init", "-q", str(runtime)], check=True)
    writer = load_writer()
    count, fingerprint = writer.tree_fingerprint(skill_root)
    fixture = {
        "schema_version": 1,
        "commit": git_text("rev-parse", "HEAD"),
        "provider_id": PROVIDER_ID,
        "model": MODEL,
        "reasoning_effort": "max",
        "source": SOURCE_SKILL.relative_to(REPO).as_posix(),
        "runtime_skill": skill_root.relative_to(REPO).as_posix(),
        "file_count": count,
        "tree_fingerprint": fingerprint,
    }
    (OUTPUT_ROOT / "fixture.json").write_text(
        json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return fixture


def run() -> dict:
    fixture = OUTPUT_ROOT / "fixture.json"
    if not fixture.is_file():
        raise RuntimeError("prepare the fixture first")
    result_path = OUTPUT_ROOT / "result.json"
    if result_path.exists():
        raise RuntimeError(f"result already exists: {result_path}")
    writer = load_writer()
    case = json.loads(CASE_PATH.read_text(encoding="utf-8"))
    record = writer.run_one(PROVIDER_ID, MODEL, "qwenwork", case, "max")
    result_path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--run", action="store_true")
    args = parser.parse_args()
    result = prepare() if args.prepare else run()
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
