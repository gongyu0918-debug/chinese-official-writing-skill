#!/usr/bin/env python3
"""Two real-D0 cancellation schedules; actual core/detect processes, no model."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def load(root: Path):
    path = root / "chinese-official-writing/hooks/core/gate_stop_hook.py"
    spec = importlib.util.spec_from_file_location("cleanup_core", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--sample", type=Path)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--barrier", type=Path)
    args = parser.parse_args()
    args.source_root = args.source_root.resolve()
    core = load(args.source_root)
    if args.worker:
        original = core._atomic_write_text
        paused = False

        def first_write(path, text):
            nonlocal paused
            if not paused:
                paused = True
                args.barrier.mkdir(parents=True, exist_ok=True)
                (args.barrier / "ready").write_text("before_first_raw_input_write", encoding="utf-8")
                deadline = time.monotonic() + 15
                while not (args.barrier / "resume").is_file():
                    if time.monotonic() >= deadline:
                        raise RuntimeError("fault scheduler did not resume")
                    time.sleep(0.01)
            return original(path, text)

        core._atomic_write_text = first_write
        return core.main()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    sample_raw = args.sample.read_bytes()
    sample = json.loads(sample_raw)
    request, d0 = sample["request"], sample["d0"]
    assert digest(d0.encode("utf-8")) == sample["receipt"]["final_sha256"]
    (args.output / "sample.json").write_bytes(sample_raw)
    source = args.source_root / "chinese-official-writing/hooks/core/gate_stop_hook.py"
    common_env = {k: v for k, v in os.environ.items() if not k.startswith("COW_GATE_") and k not in {"PLUGIN_ROOT", "PLUGIN_DATA"}}
    common_env.update(COW_GATE_CAPABILITY="delivery_review", PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    cases = []
    for scenario in ("bootstrap_abort", "abort_lock_recovery"):
        case_dir = args.output / scenario
        case_dir.mkdir()
        data = case_dir / "data"
        env = dict(common_env, COW_GATE_HOOK_DATA=str(data))
        events = []
        record_path = data / "candidate-ai-gate-hook/cleanup" / f"{scenario}.json"

        def event(name, **fields):
            return {"hook_event_name": name, "session_id": "cleanup", "turn_id": scenario, "cwd": str(args.source_root), **fields}

        def observation():
            record = json.loads(record_path.read_bytes()) if record_path.is_file() else None
            raw_files = []
            for path in data.rglob("*"):
                if path.is_file() and path.suffix not in {".state-lock", ".bootstrap-lock"}:
                    content = path.read_bytes()
                    if "中心举办读书交流活动".encode("utf-8") in content or request.encode("utf-8") in content:
                        raw_files.append({"path":path.relative_to(data).as_posix(), "sha256":digest(content)})
            return {"record": record, "raw_files": raw_files}

        def call(name, **fields):
            payload = event(name, **fields)
            completed = subprocess.run([sys.executable, "-B", "-X", "utf8", str(source)], input=json.dumps(payload, ensure_ascii=False).encode("utf-8"), capture_output=True, env=env, cwd=args.source_root, timeout=35)
            result = {"event": payload, "exit_code": completed.returncode, "stdout": completed.stdout.decode("utf-8"), "stderr": completed.stderr.decode("utf-8"), "response":json.loads(completed.stdout), "after":observation()}
            events.append(result)
            return result

        call("UserPromptSubmit", prompt=request)
        skill = args.source_root / "chinese-official-writing/SKILL.md"
        skill_bytes = skill.read_bytes()
        call("PostToolUse", tool_input={"cmd":f'Get-Content "{skill}"'}, tool_response={"exit_code":0,"output":skill_bytes.decode("utf-8")})
        if scenario == "bootstrap_abort":
            barrier = case_dir / "barrier"
            payload = event("Stop", last_assistant_message=d0, stop_hook_active=False)
            process = subprocess.Popen([sys.executable, "-B", "-X", "utf8", str(Path(__file__).resolve()), "--worker", "--source-root", str(args.source_root), "--barrier", str(barrier)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, cwd=args.source_root)
            process.stdin.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            process.stdin.close()
            process.stdin = None
            deadline = time.monotonic() + 10
            while not (barrier / "ready").is_file():
                if time.monotonic() >= deadline or process.poll() is not None:
                    raise RuntimeError("bootstrap worker never reached scheduling barrier")
                time.sleep(0.01)
            before_abort = observation()
            abort = call("HostAbort", abort_reason="turn_changed")
            (barrier / "resume").write_text("resume", encoding="utf-8")
            stdout, stderr = process.communicate(timeout=30)
            events.append({"event":payload,"fault_schedule":"pause before first actual input write, HostAbort completes, then resume original write/detect", "exit_code":process.returncode,"stdout":stdout.decode("utf-8"),"stderr":stderr.decode("utf-8"),"response":json.loads(stdout),"after":observation()})
            after_worker = observation()
        else:
            lock = core._acquire_file_lock(record_path.with_suffix(".state-lock"))
            assert lock is not None
            try:
                before_abort = observation()
                abort = call("HostAbort", abort_reason="turn_changed")
            finally:
                core._release_bootstrap_lock(*lock)
            after_worker = observation()
        recovered = call("Stop", last_assistant_message=d0, stop_hook_active=False)
        result = {"scenario":scenario,"before_abort":before_abort,"after_abort":abort["after"],"after_producer_or_lock_release":after_worker,"after_followup_stop":recovered["after"],"followup_response":recovered["response"],"events":events}
        write(case_dir / "result.json", result)
        cases.append(result)
    result = {"baseline_or_candidate_core_sha256":digest(source.read_bytes()),"sample_sha256":digest(sample_raw),"d0_sha256":digest(d0.encode("utf-8")),"model_calls":0,"detect_stubbed":False,"script_sha256":digest(Path(__file__).read_bytes()),"cases":cases}
    write(args.output / "result.json", result)
    print(json.dumps({"core_sha256":result["baseline_or_candidate_core_sha256"],"cases":[{"scenario":c["scenario"],"raw_after_producer_or_release":len(c["after_producer_or_lock_release"]["raw_files"]),"raw_after_followup_stop":len(c["after_followup_stop"]["raw_files"]),"followup_response":c["followup_response"]} for c in cases]},ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
