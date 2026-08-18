#!/usr/bin/env python3
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
OUTPUT = ROOT / "output/post-integration-wr-ah-cold-review/hard-anchor-fix-r1"
BASE_HARNESS = Path(__file__).resolve().parent.parent / "v167-formulaic-mechanicality-real-first/harness.py"
UNDER_PATH = ROOT / "chinese-official-writing/hooks/capabilities/under_length/runtime.py"
OVER_PATH = ROOT / "chinese-official-writing/hooks/capabilities/over_length/runtime.py"
TIMEOUT_SECONDS = 1200
MODELS = {
    "opencode": "opencode-go/deepseek-v4-flash",
    "ollama": "ollama-cloud/deepseek-v4-flash:0731",
    "alibaba": "alibaba-token-plan-2/deepseek-v4-flash-0731",
}


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module("hard_anchor_fix_base", BASE_HARNESS)
UNDER = load_module("hard_anchor_fix_under", UNDER_PATH)
OVER = load_module("hard_anchor_fix_over", OVER_PATH)


UNDER_REQUEST = (
    "请起草220—280字的采购请示，标题为关于申请购置应急通信设备的请示，"
    "字段包括项目名称、设备型号、覆盖范围、申请数量。材料：拟购置H100型应急通信设备，"
    "覆盖两个小区，共6台；现有预算能够承担本次支出，供应商尚未确定。只输出完整正文。"
)
UNDER_D0 = (
    "关于申请购置应急通信设备的请示\n\n"
    "为保障两个小区应急通信需要，拟购置H100型应急通信设备6台。"
    "本次购置可由现有预算承担，供应商尚未确定。现提出申请，请予审批。"
)
UNDER_SPEC = {"minimum": 220, "maximum": 280, "scope": "full"}

OVER_REQUEST = "请将全文压缩至不超过220字，只输出完整正文。"
OVER_D0 = (
    "关于申请购置应急通信设备的请示\n\n"
    "姓名：李明；部门：运行管理科\n"
    "现将有关情况说明如下：\n"
    "为保障两个小区的应急通信工作，拟购置H100型应急通信设备6台。当前两个小区均有应急通信需要，"
    "购置相关设备能够用于现有应急通信工作，因此提出本次购置申请。\n"
    "本次购置资金可由现有预算承担，预算已经作出相应安排。现有预算能够满足本次购置支出需要，"
    "本次购置不需要另行追加预算。\n"
    "供应商尚未确定。待履行审批程序后，将根据批准结果办理相关事项。"
    "综上，为做好两个小区应急通信工作，现申请购置H100型应急通信设备6台，请予审批。"
)
OVER_SPEC = {"minimum": 0, "maximum": 220, "scope": "full"}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def prompt_for(case_id: str) -> str:
    if case_id == "under":
        return UNDER._revision_instruction(UNDER_REQUEST, UNDER_D0, UNDER_SPEC)
    return OVER._revision_instruction(OVER_REQUEST, OVER_D0, OVER_D0, OVER_SPEC, 1)


def evaluate(case_id: str, final: str) -> dict[str, Any]:
    if case_id == "under":
        mechanical = UNDER.mechanical_reason(UNDER_D0, final, UNDER_SPEC, UNDER_REQUEST)
        increments = UNDER._increment_items(UNDER_D0, final)
        semantic = UNDER._unsupported_added_process(UNDER_REQUEST, UNDER_D0, increments)
        return {
            "mechanical_reason": mechanical,
            "added_process_reason": semantic,
            "count": UNDER.count_text(final, "full"),
            "required_labels_present": all(
                label in final for label in UNDER._required_labels(UNDER_REQUEST)
            ),
            "functional_pass": mechanical is None and semantic is None,
        }
    mechanical = OVER.mechanical_reason(OVER_D0, final, OVER_SPEC, OVER_REQUEST)
    return {
        "mechanical_reason": mechanical,
        "count": OVER.count_text(final, "full"),
        "intro_glue_removed": "现将有关情况说明如下" not in final,
        "functional_pass": mechanical is None,
    }


def run_arm(claude: str, provider: str, model: str, case_id: str) -> dict[str, Any]:
    arm_id = f"{provider}-{case_id}"
    out = OUTPUT / "raw" / arm_id
    runtime = OUTPUT / "runtime" / arm_id
    out.mkdir(parents=True, exist_ok=False)
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
    with stream.open("w", encoding="utf-8", newline="\n") as stdout, stderr.open(
        "w", encoding="utf-8", newline="\n"
    ) as errors:
        completed = subprocess.run(
            command,
            cwd=runtime / "work",
            env=environment,
            input=prompt_for(case_id),
            stdout=stdout,
            stderr=errors,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    parsed = BASE.parse_stream(stream)
    final = parsed.pop("final")
    technical_valid = (
        completed.returncode == 0
        and parsed["result_count"] == 1
        and parsed["result_subtypes"] == ["success"]
        and parsed["result_errors"] == [False]
        and parsed["init_models"] == [model]
        and parsed["assistant_models"] == [model]
        and parsed["usage_models"] == [model]
        and not parsed["invalid_json_lines"]
    )
    assessment = evaluate(case_id, final) if technical_valid else {"functional_pass": False}
    (out / "final.txt").write_text(final, encoding="utf-8", newline="\n")
    receipt = {
        "arm_id": arm_id,
        "provider": provider,
        "model": model,
        "effort": "max",
        "retry_count": 0,
        "duration_seconds": round(time.monotonic() - started, 3),
        "return_code": completed.returncode,
        "technical_valid": technical_valid,
        "final_sha256": sha256_text(final),
        **assessment,
    }
    write_json(out / "receipt.json", receipt)
    return receipt


def run_lane(claude: str, provider: str, model: str) -> list[dict[str, Any]]:
    return [run_arm(claude, provider, model, case_id) for case_id in ("under", "over")]


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError(f"output exists: {OUTPUT}")
    if subprocess.run(
        ["git", "status", "--porcelain", "--", "chinese-official-writing"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip():
        raise RuntimeError("product worktree must be committed and clean")
    claude = shutil.which("claude")
    if not claude:
        raise RuntimeError("claude executable unavailable")
    OUTPUT.mkdir(parents=True)
    receipts: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [
            pool.submit(run_lane, claude, provider, model)
            for provider, model in MODELS.items()
        ]
        for future in futures:
            receipts.extend(future.result())
    write_json(
        OUTPUT / "manifest.json",
        {
            "calls": len(receipts),
            "technical_valid": sum(item["technical_valid"] for item in receipts),
            "functional_pass": sum(item["functional_pass"] for item in receipts),
            "receipts": receipts,
        },
    )


if __name__ == "__main__":
    main()
