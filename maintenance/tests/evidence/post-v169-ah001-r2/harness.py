#!/usr/bin/env python3
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
CASES = HERE / "cases.json"
OUTPUT = ROOT / "output/post-v169-ah001-r2/formal-r1"
TIMEOUT_SECONDS = 1200
AUTH_ENV = "POST_V169_AH001_R2_AUTH"
AUTH_VALUE = "APPROVED_BY_USER_20260818"
BASELINE_COMMIT = "17de0712fd09a409fc56135e4929caf8bc4c0fce"
BASE_HARNESS = HERE.parent / "v167-formulaic-mechanicality-real-first/harness.py"
CONTRACT_PATH = HERE / "prototype_anchor_contract.py"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("v167_real_runner", BASE_HARNESS)
CONTRACT = load_module("ah001_contract", CONTRACT_PATH)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="strict", timeout=60, check=True,
    ).stdout.strip()


def load_cases() -> dict[str, Any]:
    payload = json.loads(CASES.read_text(encoding="utf-8"))
    if len(payload.get("cases") or []) != 4:
        raise RuntimeError("expected four cases")
    return payload


def preflight() -> dict[str, Any]:
    if git("merge-base", "--is-ancestor", BASELINE_COMMIT, "HEAD"):
        pass
    if git("status", "--porcelain", "--", "chinese-official-writing"):
        raise RuntimeError("product tree dirty")
    changed = git("diff", "--name-only", BASELINE_COMMIT, "--", "chinese-official-writing")
    if changed:
        raise RuntimeError(f"prototype must not change product: {changed}")
    return {
        "baseline_commit": BASELINE_COMMIT,
        "experiment_commit": git("rev-parse", "HEAD"),
        "cases_sha256": hashlib.sha256(CASES.read_bytes()).hexdigest(),
        "contract_sha256": hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest(),
        "self_test": CONTRACT.self_test(),
    }


def system_prompt(skill_root: Path) -> str:
    return (
        "你是独立的中文正式材料修订 Agent。先用 Read 工具读取唯一入口："
        f"{(skill_root / 'SKILL.md').resolve()}。只读取同一 Skill 根内本题必要的 references，"
        "不得读取维护记录、测试证据或用户目录，不得联网、创建文件或运行命令。"
        "修订时保留底稿明确给出的标题、主体、名称、数字、日期、金额、文号、引语、字段、"
        "否定与未决状态，并保持值与主体、对象、事项之间的归属关系；允许删除同一锚点的无用重复，"
        "不要求出现次数完全相等。严格按用户要求只输出改后正文，不解释过程。"
    )


def run_arm(claude: str, provider: str, model: str, case: dict[str, Any]) -> dict[str, Any]:
    arm_id = f"{provider}-{case['id']}"
    out = OUTPUT / "raw" / arm_id
    runtime = OUTPUT / "runtime" / arm_id
    out.mkdir(parents=True, exist_ok=False)
    runtime.mkdir(parents=True, exist_ok=False)
    skill_root = ROOT / "chinese-official-writing"
    prompt = system_prompt(skill_root)
    user_input = f"{case['request']}\n\n【底稿】\n{case['draft']}"
    environment = BASE.build_environment(model, runtime)
    work = runtime / "work"
    stream = runtime / "stream.jsonl"
    stderr = runtime / "stderr.txt"
    started = time.monotonic()
    return_code = -1
    timed_out = False
    error = None
    with stream.open("w", encoding="utf-8", newline="\n") as stdout, stderr.open(
        "w", encoding="utf-8", newline="\n"
    ) as errors:
        try:
            completed = subprocess.run(
                BASE.command(claude, model, skill_root, prompt),
                cwd=work,
                env=environment,
                input=user_input,
                stdout=stdout,
                stderr=errors,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=TIMEOUT_SECONDS,
                check=False,
            )
            return_code = completed.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            error = repr(exc)
    parsed = BASE.parse_stream(stream)
    final = parsed.pop("final")
    scope = BASE.read_scope(parsed["reads"], skill_root, work)
    checks = {
        "return_code_zero": return_code == 0,
        "not_timed_out": not timed_out,
        "single_success": parsed["result_count"] == 1
        and parsed["result_subtypes"] == ["success"]
        and parsed["result_errors"] == [False],
        "final_nonempty": bool(final.strip()),
        "model_bound": parsed["init_models"] == [model]
        and parsed["assistant_models"] == [model]
        and parsed["usage_models"] == [model],
        "entry_read": scope["entry_read"],
        "read_scope": not scope["outside"],
        "no_plugins": not parsed["plugins"],
        "valid_stream": not parsed["invalid_json_lines"],
    }
    contract = CONTRACT.compare(str(case["draft"]), final)
    (out / "final.txt").write_text(final, encoding="utf-8", newline="\n")
    shutil.copyfile(stderr, out / "stderr.txt")
    write_json(out / "contract.json", contract)
    meta = {
        "arm_id": arm_id,
        "provider": provider,
        "model": model,
        "case_id": case["id"],
        "duration_seconds": round(time.monotonic() - started, 3),
        "return_code": return_code,
        "timed_out": timed_out,
        "error": error,
        "checks": checks,
        "technical_valid": all(checks.values()),
        "mechanical_ok": contract["mechanical_ok"],
        "contract_status": contract["status"],
        "final_sha256": sha256_text(final),
        "reads": parsed["reads"],
    }
    write_json(out / "meta.json", meta)
    return meta


def run_lane(claude: str, provider: str, model: str, cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [run_arm(claude, provider, model, case) for case in cases]


def execute() -> None:
    if os.environ.get(AUTH_ENV) != AUTH_VALUE:
        raise RuntimeError(f"missing {AUTH_ENV}")
    if OUTPUT.exists():
        raise RuntimeError(f"output exists: {OUTPUT}")
    claude = shutil.which("claude")
    if not claude:
        raise RuntimeError("claude executable unavailable")
    payload = load_cases()
    OUTPUT.mkdir(parents=True)
    write_json(OUTPUT / "preflight.json", preflight())
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(run_lane, claude, provider, model, payload["cases"])
            for provider, model in payload["models"].items()
        ]
        for future in futures:
            results.extend(future.result())
    results.sort(key=lambda item: item["arm_id"])
    write_json(
        OUTPUT / "manifest.json",
        {
            "calls_planned": 8,
            "calls_completed": len(results),
            "technical_valid": sum(bool(item["technical_valid"]) for item in results),
            "mechanical_ok": sum(bool(item["mechanical_ok"]) for item in results),
            "arms": results,
        },
    )


if __name__ == "__main__":
    execute()
