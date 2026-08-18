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
OUTPUT = ROOT / "output/post-integration-wr-ah-cold-review/judges-r1"
WRITING_PACKET = HERE / "writing-blind-packet.md"
DIFF_PACKET = HERE / "diff-cold-review-packet.md"
ENTROPY_PACKET = HERE / "entropy-review-packet.md"
FREEZE = HERE / "packet-freeze.json"
AUTH_ENV = "POST_INTEGRATION_COLD_REVIEW_AUTH"
AUTH_VALUE = "APPROVED_BY_USER_20260818"
TIMEOUT_SECONDS = 1200
MODELS = {
    "sol": "gpt-5.6-sol",
    "grok": "xai/grok-4.6",
    "qwen": "alibaba-token-plan-2/qwen3.8-max",
}
BASE_HARNESS = HERE.parent / "v167-formulaic-mechanicality-real-first/harness.py"
PAIR_IDS = [f"P{index:02d}" for index in range(1, 13)]
GRADE_VALUES = {"PASS", "WARN", "FAIL"}


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location("post_integration_judge_base", BASE_HARNESS)
    if spec is None or spec.loader is None:
        raise RuntimeError("base harness unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_base()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_draft(value: Any, pair_id: str, label: str) -> None:
    if not isinstance(value, dict):
        raise RuntimeError(f"invalid draft verdict: {pair_id}-{label}")
    for field in ("facts", "state", "genre", "length", "naturalness", "repetition"):
        if value.get(field) not in GRADE_VALUES:
            raise RuntimeError(f"invalid {field}: {pair_id}-{label}")
    if not isinstance(value.get("direct_use_cost"), int) or not 0 <= value["direct_use_cost"] <= 5:
        raise RuntimeError(f"invalid cost: {pair_id}-{label}")
    if not isinstance(value.get("reason"), str) or not value["reason"].strip():
        raise RuntimeError(f"missing reason: {pair_id}-{label}")


def validate_verdict(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or list((value.get("pairs") or {}).keys()) != PAIR_IDS:
        raise RuntimeError("invalid pair set")
    for pair_id, item in value["pairs"].items():
        if not isinstance(item, dict) or item.get("winner") not in {"甲", "乙", "难分"}:
            raise RuntimeError(f"invalid pair verdict: {pair_id}")
        validate_draft(item.get("甲"), pair_id, "甲")
        validate_draft(item.get("乙"), pair_id, "乙")
        if not isinstance(item.get("reason"), str) or not item["reason"].strip():
            raise RuntimeError(f"missing pair reason: {pair_id}")
    for field in ("diff_findings", "entropy_findings"):
        if not isinstance(value.get(field), list):
            raise RuntimeError(f"invalid {field}")
    if not isinstance(value.get("overall"), dict):
        raise RuntimeError("invalid overall")
    return value


def prompt() -> str:
    writing = WRITING_PACKET.read_text(encoding="utf-8")
    diff = DIFF_PACKET.read_text(encoding="utf-8")
    entropy = ENTROPY_PACKET.read_text(encoding="utf-8")
    schema = {
        "pairs": {
            pair_id: {
                "甲": {
                    "facts": "PASS|WARN|FAIL",
                    "state": "PASS|WARN|FAIL",
                    "genre": "PASS|WARN|FAIL",
                    "length": "PASS|WARN|FAIL",
                    "naturalness": "PASS|WARN|FAIL",
                    "repetition": "PASS|WARN|FAIL",
                    "direct_use_cost": 0,
                    "reason": "具体理由",
                },
                "乙": {
                    "facts": "PASS|WARN|FAIL",
                    "state": "PASS|WARN|FAIL",
                    "genre": "PASS|WARN|FAIL",
                    "length": "PASS|WARN|FAIL",
                    "naturalness": "PASS|WARN|FAIL",
                    "repetition": "PASS|WARN|FAIL",
                    "direct_use_cost": 0,
                    "reason": "具体理由",
                },
                "winner": "甲|乙|难分",
                "reason": "比较理由",
            }
            for pair_id in PAIR_IDS
        },
        "diff_findings": [
            {"severity": "P0|P1|P2", "path": "路径", "issue": "问题", "evidence": "证据"}
        ],
        "entropy_findings": [
            {
                "severity": "P1|P2|OBSERVE",
                "location": "路径与行或候选编号",
                "issue": "重复、冲突或过载",
                "recommendation": "保留、合并、删除或继续观察",
            }
        ],
        "overall": {
            "writing": "PASS|WARN|FAIL",
            "diff": "PASS|WARN|FAIL",
            "entropy": "PASS|WARN|FAIL",
            "summary": "不超过五句",
        },
    }
    return (
        "你是独立中文正式写作与 Skill 工程冷审员。只读下列三份冻结包，不调用工具、不联网，"
        "不知道稿件版本映射，也不得根据措辞猜版本。先逐稿做硬边界，再比较自然度；DIFF 审核只评价"
        "固定代码变化；信息熵审核必须结合真实读取量和重复候选，不因静态相似就建议删除。"
        "保护性安全边界与合理概括要区分，不能把常识性自然衔接一律判外扩。"
        "只输出一个严格 JSON 对象，不加 Markdown。字段必须与下列骨架一致：\n"
        + json.dumps(schema, ensure_ascii=False)
        + "\n\n===== 写稿匿名包 =====\n"
        + writing
        + "\n\n===== 产品 DIFF 包 =====\n"
        + diff
        + "\n\n===== 信息熵包 =====\n"
        + entropy
    )


def run_judge(claude: str, name: str, model: str, review_prompt: str) -> dict[str, Any]:
    out = OUTPUT / name
    runtime = out / "runtime"
    out.mkdir(parents=True, exist_ok=False)
    runtime.mkdir()
    environment = BASE.build_environment(model, runtime)
    stream = out / "stream.jsonl"
    stderr = out / "stderr.txt"
    command = [
        claude,
        "--setting-sources",
        "",
        "--no-session-persistence",
        "--tools",
        "",
        "--print",
        "--verbose",
        "--output-format",
        "stream-json",
        "--model",
        model,
        "--effort",
        "max",
    ]
    started = time.monotonic()
    return_code = -1
    timed_out = False
    error = None
    with stream.open("w", encoding="utf-8", newline="\n") as stdout, stderr.open(
        "w", encoding="utf-8", newline="\n"
    ) as errors:
        try:
            completed = subprocess.run(
                command,
                cwd=runtime,
                env=environment,
                input=review_prompt,
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
    valid_stream = (
        return_code == 0
        and not timed_out
        and parsed["result_count"] == 1
        and parsed["result_subtypes"] == ["success"]
        and parsed["result_errors"] == [False]
        and parsed["init_models"] == [model]
        and parsed["assistant_models"] == [model]
        and parsed["usage_models"] == [model]
        and not parsed["invalid_json_lines"]
    )
    verdict = None
    validation_error = None
    if valid_stream:
        try:
            verdict = validate_verdict(json.loads(final))
        except (json.JSONDecodeError, RuntimeError) as exc:
            validation_error = repr(exc)
    if verdict is not None:
        write_json(out / "verdict.json", verdict)
    receipt = {
        "judge": name,
        "model": model,
        "effort": "max",
        "retry_count": 0,
        "duration_seconds": round(time.monotonic() - started, 3),
        "return_code": return_code,
        "timed_out": timed_out,
        "error": error,
        "validation_error": validation_error,
        "technical_valid": verdict is not None,
        "writing_packet_sha256": sha256_file(WRITING_PACKET),
        "diff_packet_sha256": sha256_file(DIFF_PACKET),
        "entropy_packet_sha256": sha256_file(ENTROPY_PACKET),
        "verdict_sha256": sha256_file(out / "verdict.json") if verdict is not None else None,
    }
    write_json(out / "receipt.json", receipt)
    return receipt


def execute() -> None:
    if os.environ.get(AUTH_ENV) != AUTH_VALUE:
        raise RuntimeError(f"missing {AUTH_ENV}")
    if OUTPUT.exists():
        raise RuntimeError(f"output exists: {OUTPUT}")
    frozen = json.loads(FREEZE.read_text(encoding="utf-8"))
    for key, path in (
        ("writing_packet_sha256", WRITING_PACKET),
        ("diff_packet_sha256", DIFF_PACKET),
        ("entropy_packet_sha256", ENTROPY_PACKET),
    ):
        if frozen.get(key) != sha256_file(path):
            raise RuntimeError(f"packet hash mismatch: {path}")
    claude = shutil.which("claude")
    if not claude:
        raise RuntimeError("claude executable unavailable")
    OUTPUT.mkdir(parents=True)
    review_prompt = prompt()
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [
            pool.submit(run_judge, claude, name, model, review_prompt)
            for name, model in MODELS.items()
        ]
        receipts = [future.result() for future in futures]
    receipts.sort(key=lambda item: item["judge"])
    write_json(
        OUTPUT / "manifest.json",
        {
            "judges_planned": len(MODELS),
            "judges_completed": len(receipts),
            "technical_valid": sum(bool(item["technical_valid"]) for item in receipts),
            "receipts": receipts,
        },
    )


if __name__ == "__main__":
    execute()
