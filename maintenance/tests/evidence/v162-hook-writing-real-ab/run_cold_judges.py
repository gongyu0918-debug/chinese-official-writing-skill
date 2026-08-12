#!/usr/bin/env python3
"""Run Kimi K3, Qwen3.8-max and Grok4.5 against frozen writing and DIFF packets."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from typing import Any
from urllib import request as urllib_request


ROOT = Path(__file__).resolve().parents[4]
RUN_ROOT = ROOT / "output/v162-hook-writing-real-ab/run-20260812-r2"
WRITING_PACKET = RUN_ROOT / "blind-packet.md"
WRITING_TEMPLATE = RUN_ROOT / "blind-verdict-template.json"
MAPPING_PATH = RUN_ROOT / "mapping.json"
DIFF_PACKET = ROOT / "output/v162-hook-writing-real-ab/v162-diff-cold-packet.md"
JUDGE_ROOT = RUN_ROOT / "judges"
RUNTIME_ROOT = ROOT / "output/v162-hook-writing-real-ab/judge-runtime"
WRITING_PACKET_SHA256 = "2171a88fda22e81c9523a075d733bdf3ddd158451f956aa43dcf7d1872196dbc"
GATEWAY = "http://127.0.0.1:10100"
TIMEOUT_SECONDS = 1200
AUTH_ENV = "V162_COLD_JUDGE_AUTH"
AUTH_VALUE = "APPROVED_BY_USER_20260812"
JUDGES = {
    "kimi": "kimi/k3",
    "qwen": "alibaba-token-plan-2/qwen3.8-max",
    "grok": "xai/grok-4.5",
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def count_tokens_probe(model: str) -> dict[str, Any]:
    payload = json.dumps({"model": model, "messages": [{"role": "user", "content": "cold audit probe"}]}).encode("utf-8")
    request = urllib_request.Request(
        GATEWAY + "/v1/messages/count_tokens", data=payload, method="POST",
        headers={"anthropic-version": "2023-06-01", "content-type": "application/json", "x-api-key": "local-cold-judge-dummy"},
    )
    try:
        with urllib_request.urlopen(request, timeout=30) as response:
            parsed = json.loads(response.read().decode("utf-8"))
            return {"ok": response.status == 200 and isinstance(parsed.get("input_tokens"), int), "status": response.status, "input_tokens": parsed.get("input_tokens")}
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__}


def build_prompt() -> str:
    writing = WRITING_PACKET.read_text(encoding="utf-8")
    template = WRITING_TEMPLATE.read_text(encoding="utf-8")
    diff = DIFF_PACKET.read_text(encoding="utf-8")
    return (
        "你是独立冷审裁判。不得调用工具、读取文件、猜测匿名稿件身份，严格只用下列两个冻结 packet。"
        "先完成匿名写稿盲审，再完成非匿名 v1.6.0->v1.6.2 产品 DIFF 审计。"
        "写稿部分必须完整填写9组模板；DIFF部分只报告可复现P0/P1/P2。"
        "只输出一个JSON对象，不要Markdown或额外文字，根对象键必须为writing_review和diff_review。"
        f"写稿盲包SHA256={WRITING_PACKET_SHA256}。\n\n"
        f"写稿JSON模板：\n{template}\n\n匿名写稿盲包：\n{writing}\n\n产品DIFF冷审包：\n{diff}"
    )


def run_environment(model: str, config_root: Path, tmp_root: Path) -> dict[str, str]:
    environment = {
        key: value for key, value in os.environ.items()
        if not key.startswith("ANTHROPIC_") and key not in {"CLAUDE_CODE_OAUTH_TOKEN", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"}
    }
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        environment[key] = ""
    environment.update(
        {
            "NO_PROXY": "127.0.0.1,localhost", "no_proxy": "127.0.0.1,localhost",
            "ANTHROPIC_BASE_URL": GATEWAY, "ANTHROPIC_AUTH_TOKEN": "local-cold-judge-dummy",
            "ANTHROPIC_MODEL": model, "ANTHROPIC_DEFAULT_OPUS_MODEL": model,
            "ANTHROPIC_DEFAULT_SONNET_MODEL": model, "ANTHROPIC_DEFAULT_HAIKU_MODEL": model,
            "ANTHROPIC_CUSTOM_MODEL_OPTION": model, "ANTHROPIC_CUSTOM_MODEL_OPTION_NAME": model,
            "ANTHROPIC_CUSTOM_MODEL_OPTION_SUPPORTED_CAPABILITIES": "effort,xhigh_effort,max_effort,thinking,adaptive_thinking,interleaved_thinking",
            "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1", "CLAUDE_CODE_ATTRIBUTION_HEADER": "0",
            "CLAUDE_CONFIG_DIR": str(config_root), "CLAUDE_CODE_TMPDIR": str(tmp_root),
        }
    )
    return environment


def parse_stream(value: str) -> dict[str, Any]:
    records, invalid = [], []
    for number, line in enumerate(value.splitlines(), 1):
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            invalid.append(number)
            continue
        if isinstance(item, dict):
            records.append(item)
    inits = [item for item in records if item.get("type") == "system" and item.get("subtype") == "init"]
    results = [item for item in records if item.get("type") == "result"]
    assistant_models = set()
    for item in records:
        message = item.get("message")
        if isinstance(message, dict) and isinstance(message.get("model"), str):
            assistant_models.add(message["model"])
    usage_models = set()
    for item in results:
        usage = item.get("modelUsage")
        if isinstance(usage, dict):
            usage_models.update(str(key) for key in usage)
    final = results[-1].get("result", "") if results else ""
    return {
        "invalid_json_lines": invalid,
        "init_models": sorted(str(item.get("model")) for item in inits if item.get("model")),
        "assistant_models": sorted(assistant_models),
        "model_usage": sorted(usage_models),
        "api_key_sources": sorted(str(item.get("apiKeySource")) for item in inits if item.get("apiKeySource") is not None),
        "result_count": len(results), "result_subtypes": [item.get("subtype") for item in results],
        "result_is_error": [item.get("is_error") for item in results], "final": final if isinstance(final, str) else "",
    }


def validate_final(final: str) -> dict[str, Any]:
    try:
        value = json.loads(final)
    except json.JSONDecodeError as exc:
        return {"valid": False, "error": f"json:{exc.pos}"}
    if not isinstance(value, dict):
        return {"valid": False, "error": "root_not_object"}
    writing, diff = value.get("writing_review"), value.get("diff_review")
    groups = writing.get("groups") if isinstance(writing, dict) else None
    ids = [item.get("group") for item in groups if isinstance(item, dict)] if isinstance(groups, list) else []
    valid = ids == [f"G{number:02d}" for number in range(1, 10)] and isinstance(diff, dict) and isinstance(diff.get("findings"), list)
    return {"valid": valid, "error": None if valid else "schema", "parsed": value if valid else None}


def run_judge(label: str, model: str, prompt: str) -> dict[str, Any]:
    output = JUDGE_ROOT / label
    runtime = RUNTIME_ROOT / label
    config, tmp = runtime / "config", runtime / "tmp"
    if output.exists() or runtime.exists():
        raise RuntimeError(f"judge output exists: {label}")
    output.mkdir(parents=True)
    config.mkdir(parents=True)
    tmp.mkdir(parents=True)
    command = [shutil.which("claude") or "claude", "--setting-sources", "", "--no-session-persistence", "--tools", "", "--print", "--verbose", "--output-format", "stream-json", "--model", model, "--effort", "max"]
    started, monotonic = utc_now(), time.monotonic()
    return_code, timeout, exception, stdout, stderr = -1, False, None, "", ""
    try:
        completed = subprocess.run(command, cwd=runtime, env=run_environment(model, config, tmp), input=prompt, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=TIMEOUT_SECONDS, check=False)
        return_code, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
    except subprocess.TimeoutExpired as exc:
        timeout, exception, return_code = True, repr(exc), -9
        stdout = (exc.stdout or b"").decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = (exc.stderr or b"").decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    duration = round(time.monotonic() - monotonic, 3)
    parsed = parse_stream(stdout)
    validation = validate_final(parsed["final"])
    write_text(output / "stream.jsonl", stdout)
    write_text(output / "stderr.txt", stderr)
    write_text(output / "final.txt", parsed["final"])
    if validation.get("valid"):
        write_json(output / "final.parsed.json", validation["parsed"])
    receipt = {
        "label": label, "model": model, "effort": "max", "writing_packet_sha256": WRITING_PACKET_SHA256,
        "diff_packet_sha256": sha256_bytes(DIFF_PACKET.read_bytes()), "prompt_sha256": sha256_bytes(prompt.encode("utf-8")),
        "started_utc": started, "finished_utc": utc_now(), "duration_seconds": duration, "return_code": return_code,
        "timeout": timeout, "exception": exception, "outer_retry_count": 0,
        "stream_sha256": sha256_bytes(stdout.encode("utf-8")), "stderr_sha256": sha256_bytes(stderr.encode("utf-8")),
        "final_sha256": sha256_bytes(parsed["final"].encode("utf-8")), "final_chars": len(parsed["final"]),
        "stream_summary": {key: value for key, value in parsed.items() if key != "final"},
        "final_validation": {key: value for key, value in validation.items() if key != "parsed"},
    }
    receipt["technical_valid"] = (
        return_code == 0 and not timeout and parsed["result_count"] == 1 and parsed["result_subtypes"] == ["success"]
        and parsed["result_is_error"] == [False] and not parsed["invalid_json_lines"]
        and parsed["init_models"] == [model] and parsed["assistant_models"] == [model] and parsed["model_usage"] == [model]
        and validation.get("valid") is True
    )
    write_json(output / "receipt.json", receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if os.environ.get(AUTH_ENV) != AUTH_VALUE:
        raise SystemExit(f"missing {AUTH_ENV}={AUTH_VALUE}")
    if sha256_bytes(WRITING_PACKET.read_bytes()) != WRITING_PACKET_SHA256:
        raise SystemExit("writing packet hash mismatch")
    if not MAPPING_PATH.is_file() or not DIFF_PACKET.is_file():
        raise SystemExit("sealed mapping or diff packet missing")
    probes = {label: {"model": model, **count_tokens_probe(model)} for label, model in JUDGES.items()}
    if not all(item["ok"] for item in probes.values()):
        raise SystemExit("judge path probe failed")
    if not args.execute:
        print(json.dumps({"writing_packet_sha256": WRITING_PACKET_SHA256, "diff_packet_sha256": sha256_bytes(DIFF_PACKET.read_bytes()), "mapping_opened": False, "probes": probes}, ensure_ascii=False, indent=2))
        return 0
    if JUDGE_ROOT.exists() or RUNTIME_ROOT.exists():
        raise SystemExit("judge output already exists")
    JUDGE_ROOT.mkdir(parents=True)
    write_json(JUDGE_ROOT / "preflight.json", {"mapping_opened": False, "writing_packet_sha256": WRITING_PACKET_SHA256, "diff_packet_sha256": sha256_bytes(DIFF_PACKET.read_bytes()), "probes": probes})
    prompt = build_prompt()
    receipts = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(run_judge, label, model, prompt): label for label, model in JUDGES.items()}
        for future in as_completed(futures):
            receipt = future.result()
            receipts.append(receipt)
            print(json.dumps({"label": receipt["label"], "technical_valid": receipt["technical_valid"], "timeout": receipt["timeout"]}, ensure_ascii=False), flush=True)
    receipts.sort(key=lambda item: item["label"])
    write_json(JUDGE_ROOT / "receipts.json", {"mapping_opened": False, "receipts": receipts})
    hashes = {
        path.relative_to(JUDGE_ROOT).as_posix(): sha256_bytes(path.read_bytes())
        for path in sorted((item for item in JUDGE_ROOT.rglob("*") if item.is_file()), key=lambda item: item.as_posix().lower())
    }
    write_json(JUDGE_ROOT / "hashes.json", hashes)
    print(json.dumps({"complete": True, "valid": sum(item["technical_valid"] for item in receipts), "receipts": receipts}, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
