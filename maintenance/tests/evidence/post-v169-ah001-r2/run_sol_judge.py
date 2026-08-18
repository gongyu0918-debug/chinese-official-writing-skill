#!/usr/bin/env python3
from __future__ import annotations

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
PACKET = HERE / "relation-blind-packet.md"
OUTPUT = ROOT / "output/post-v169-ah001-r2/sol-r1"
MODEL = "gpt-5.6-sol"
AUTH_ENV = "POST_V169_AH001_SOL_AUTH"
AUTH_VALUE = "APPROVED_BY_USER_20260818"
BASE_HARNESS = HERE.parent / "v167-formulaic-mechanicality-real-first/harness.py"
EXPECTED_GROUPS = [f"H{index:02d}" for index in range(1, 7)]


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location("v167_real_runner", BASE_HARNESS)
    if spec is None or spec.loader is None:
        raise RuntimeError("base runner unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_base()


def validate(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("overall") not in {"PASS", "FAIL"}:
        raise RuntimeError("invalid verdict root")
    if [key for key in value if key != "overall"] != EXPECTED_GROUPS:
        raise RuntimeError("group order mismatch")
    for group in EXPECTED_GROUPS:
        item = value.get(group)
        if not isinstance(item, dict) or item.get("verdict") not in {"PASS", "FAIL"}:
            raise RuntimeError(f"invalid verdict: {group}")
        if not isinstance(item.get("reason"), str) or not item["reason"].strip():
            raise RuntimeError(f"missing reason: {group}")
    return value


def execute() -> None:
    if os.environ.get(AUTH_ENV) != AUTH_VALUE:
        raise RuntimeError(f"missing {AUTH_ENV}")
    if OUTPUT.exists():
        raise RuntimeError(f"output exists: {OUTPUT}")
    claude = shutil.which("claude")
    if not claude:
        raise RuntimeError("claude executable unavailable")
    packet = PACKET.read_text(encoding="utf-8")
    prompt = (
        "你是独立的中文正式材料事实归属核验员。只读取下列匿名包，不联网、不调用工具。"
        "逐组只判断锚点值与主体、对象、事项和状态的关系，不评价整体文采。严格按包尾JSON格式输出，"
        "不得附加Markdown。\n\n" + packet
    )
    OUTPUT.mkdir(parents=True)
    runtime = OUTPUT / "runtime"
    runtime.mkdir()
    environment = BASE.build_environment(MODEL, runtime)
    stream = OUTPUT / "stream.jsonl"
    stderr = OUTPUT / "stderr.txt"
    command = [
        claude, "--setting-sources", "", "--no-session-persistence", "--tools", "",
        "--print", "--verbose", "--output-format", "stream-json",
        "--model", MODEL, "--effort", "max",
    ]
    started = time.monotonic()
    with stream.open("w", encoding="utf-8", newline="\n") as stdout, stderr.open(
        "w", encoding="utf-8", newline="\n"
    ) as errors:
        completed = subprocess.run(
            command, cwd=runtime, env=environment, input=prompt,
            stdout=stdout, stderr=errors, text=True, encoding="utf-8",
            errors="replace", timeout=1200, check=False,
        )
    parsed = BASE.parse_stream(stream)
    if completed.returncode != 0 or parsed["result_count"] != 1 or parsed["result_errors"] != [False]:
        raise RuntimeError("SOL did not return one successful result")
    verdict = validate(json.loads(parsed["final"]))
    BASE.atomic_json(OUTPUT / "verdict.json", verdict)
    receipt = {
        "model": MODEL,
        "effort": "max",
        "retry_count": 0,
        "duration_seconds": round(time.monotonic() - started, 3),
        "packet_sha256": hashlib.sha256(PACKET.read_bytes()).hexdigest(),
        "verdict_sha256": hashlib.sha256((OUTPUT / "verdict.json").read_bytes()).hexdigest(),
        "groups": len(EXPECTED_GROUPS),
    }
    BASE.atomic_json(OUTPUT / "receipt.json", receipt)


if __name__ == "__main__":
    execute()
