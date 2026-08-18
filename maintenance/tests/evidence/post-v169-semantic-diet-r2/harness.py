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
BASELINE_ROOT = Path(r"F:\Workspaces\chinese-official-writing-skill")
BASELINE_COMMIT = "17de0712fd09a409fc56135e4929caf8bc4c0fce"
OUTPUT = ROOT / "output/post-v169-semantic-diet-r2/formal-r1"
TIMEOUT_SECONDS = 1200
AUTH_ENV = "POST_V169_SEMANTIC_R2_AUTH"
AUTH_VALUE = "APPROVED_BY_USER_20260818"
BASE_HARNESS = HERE.parent / "v167-formulaic-mechanicality-real-first/harness.py"


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location("v167_real_runner", BASE_HARNESS)
    if spec is None or spec.loader is None:
        raise RuntimeError("base runner unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_base()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def git(path: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(path), *args], capture_output=True, text=True,
        encoding="utf-8", errors="strict", timeout=60, check=True,
    ).stdout.strip()


def load_cases() -> dict[str, Any]:
    payload = json.loads(CASES.read_text(encoding="utf-8"))
    cases = payload.get("cases")
    if not isinstance(cases, list) or len(cases) != 3:
        raise RuntimeError("expected exactly three cases")
    if len({item.get("id") for item in cases}) != 3:
        raise RuntimeError("duplicate case id")
    return payload


def preflight() -> dict[str, Any]:
    if git(BASELINE_ROOT, "rev-parse", "HEAD") != BASELINE_COMMIT:
        raise RuntimeError("baseline HEAD drifted")
    if git(ROOT, "merge-base", "--is-ancestor", BASELINE_COMMIT, "HEAD"):
        pass
    baseline_dirty = git(BASELINE_ROOT, "status", "--porcelain", "--", "chinese-official-writing")
    candidate_dirty = git(ROOT, "status", "--porcelain", "--", "chinese-official-writing")
    if baseline_dirty or candidate_dirty:
        raise RuntimeError("product worktree dirty")
    changed = git(ROOT, "diff", "--name-only", BASELINE_COMMIT, "--", "chinese-official-writing").splitlines()
    expected = ["chinese-official-writing/references/anti-ai-patterns.md"]
    if changed != expected:
        raise RuntimeError(f"unexpected product diff: {changed}")
    return {
        "baseline_commit": BASELINE_COMMIT,
        "candidate_commit": git(ROOT, "rev-parse", "HEAD"),
        "changed_paths": changed,
        "cases_sha256": hashlib.sha256(CASES.read_bytes()).hexdigest(),
    }


def prompt(skill_root: Path) -> str:
    entry = skill_root / "SKILL.md"
    anti_ai = skill_root / "references/anti-ai-patterns.md"
    return (
        "你是独立的中文正式材料写稿 Agent。先用 Read 工具读取以下两个文件：\n"
        f"- {entry.resolve()}\n- {anti_ai.resolve()}\n"
        "再按 SKILL 入口只读取本题必要的同一 Skill 根内 references。不得读取其他 Skill、"
        "维护记录、测试证据或用户目录；不得联网、创建文件或运行命令。"
        "严格按用户题面输出可直接使用的正文，不解释过程。"
    )


def run_arm(
    claude: str,
    provider: str,
    model: str,
    case: dict[str, Any],
    treatment: str,
) -> dict[str, Any]:
    arm_id = f"{provider}-{case['id']}-{treatment}"
    out = OUTPUT / "raw" / arm_id
    runtime = OUTPUT / "runtime" / arm_id
    out.mkdir(parents=True, exist_ok=False)
    runtime.mkdir(parents=True, exist_ok=False)
    skill_root = (BASELINE_ROOT if treatment == "baseline" else ROOT) / "chinese-official-writing"
    system_prompt = prompt(skill_root)
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
                BASE.command(claude, model, skill_root, system_prompt),
                cwd=work,
                env=environment,
                input=str(case["request"]),
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
    anti_ai_read = (skill_root / "references/anti-ai-patterns.md").resolve() in {
        BASE.resolve_read(item, work) for item in parsed["reads"]
    }
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
        "anti_ai_read": anti_ai_read,
        "read_scope": not scope["outside"],
        "no_plugins": not parsed["plugins"],
        "valid_stream": not parsed["invalid_json_lines"],
    }
    (out / "final.txt").write_text(final, encoding="utf-8", newline="\n")
    shutil.copyfile(stderr, out / "stderr.txt")
    meta = {
        "arm_id": arm_id,
        "provider": provider,
        "model": model,
        "case_id": case["id"],
        "treatment": treatment,
        "duration_seconds": round(time.monotonic() - started, 3),
        "return_code": return_code,
        "timed_out": timed_out,
        "error": error,
        "checks": checks,
        "technical_valid": all(checks.values()),
        "final_sha256": sha256_text(final),
        "reads": parsed["reads"],
    }
    write_json(out / "meta.json", meta)
    return meta


def run_lane(claude: str, provider: str, model: str, cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for index, case in enumerate(cases):
        order = ("baseline", "candidate") if index % 2 == 0 else ("candidate", "baseline")
        for treatment in order:
            results.append(run_arm(claude, provider, model, case, treatment))
    return results


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
            "calls_planned": 12,
            "calls_completed": len(results),
            "technical_valid": sum(bool(item["technical_valid"]) for item in results),
            "arms": results,
        },
    )


if __name__ == "__main__":
    execute()
