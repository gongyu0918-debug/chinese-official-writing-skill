#!/usr/bin/env python3
"""Run one isolated gpt-5.6-sol max blind review for the combined R3 packet."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from typing import Any

import harness as base


MODEL = "gpt-5.6-sol"
EFFORT = "max"
TIMEOUT_SECONDS = 1200
AUTH_ENV = "V167_FORMULAIC_R3_SOL_AUTH"
AUTH_VALUE = "APPROVED_BY_USER_20260817"
ALLOWED = {"PASS", "WARN", "FAIL"}
FIELDS = ("facts", "state", "length", "user_structure", "genre", "mechanicality")


def validate_verdict(value: Any, template: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise RuntimeError("invalid verdict root")
    expected = [item["group"] for item in template["groups"]]
    groups = value.get("groups")
    if not isinstance(groups, list) or [item.get("group") for item in groups] != expected:
        raise RuntimeError("verdict groups mismatch")
    for item in groups:
        if item.get("winner") not in {"甲", "乙", "难分"} or not isinstance(item.get("reason"), str):
            raise RuntimeError(f"invalid comparison: {item.get('group')}")
        for label in ("稿件甲", "稿件乙"):
            draft = item.get(label)
            if not isinstance(draft, dict):
                raise RuntimeError(f"missing draft verdict: {item.get('group')} {label}")
            if any(draft.get(field) not in ALLOWED for field in FIELDS):
                raise RuntimeError(f"invalid draft axis: {item.get('group')} {label}")
            if str(draft.get("direct_use_cost")) not in {"0", "1", "2", "3", "4"}:
                raise RuntimeError(f"invalid direct use cost: {item.get('group')} {label}")
    return value


def judge_prompt(packet: str, template: str) -> str:
    return (
        "你是独立的中文正式材料盲审员。只根据下面的匿名任务、稿件和JSON模板裁决；"
        "不得猜测A/B身份，不得联网，不得调用工具。先分别检查事实、未决状态、篇幅、用户结构、文种功能、机械化和直接使用成本，再比较。"
        "单个正式连接词、用户指定尾语或有办理功能的文种用语不算机械化；只有无功能的固定开头、承启、总结、尾语或段落骨架成簇复现才计风险。"
        "输出一个JSON对象，字段和组顺序严格符合模板；可以额外给overall和concise_summary，但不要输出Markdown或解释。\n\n"
        "<judge-template>\n" + template + "\n</judge-template>\n\n"
        "<blind-packet>\n" + packet + "\n</blind-packet>\n"
    )


def execute(packet_path: Path, template_path: Path, output: Path) -> None:
    if os.environ.get(AUTH_ENV) != AUTH_VALUE:
        raise RuntimeError(f"missing exact authorization marker {AUTH_ENV}")
    if output.exists():
        raise RuntimeError(f"output must not exist: {output}")
    packet = packet_path.read_text(encoding="utf-8")
    template_text = template_path.read_text(encoding="utf-8")
    template = json.loads(template_text)
    output.mkdir(parents=True)
    runtime = output / "runtime"
    runtime.mkdir()
    environment = base.build_environment(MODEL, runtime)
    prompt = judge_prompt(packet, template_text)
    claude = shutil.which("claude")
    if not claude:
        raise RuntimeError("claude executable not found")
    stream = output / "stream.jsonl"
    stderr = output / "stderr.txt"
    command = [
        claude, "--setting-sources", "", "--no-session-persistence", "--tools", "",
        "--append-system-prompt", "只执行匿名盲审并输出严格JSON。",
        "--print", "--verbose", "--output-format", "stream-json",
        "--model", MODEL, "--effort", EFFORT,
    ]
    before = time.monotonic()
    with stream.open("w", encoding="utf-8", newline="\n") as stdout_handle, stderr.open("w", encoding="utf-8", newline="\n") as stderr_handle:
        completed = subprocess.run(
            command, cwd=runtime, env=environment, input=prompt,
            stdout=stdout_handle, stderr=stderr_handle, text=True,
            encoding="utf-8", errors="replace", timeout=TIMEOUT_SECONDS, check=False,
        )
    parsed = base.parse_stream(stream)
    if completed.returncode != 0 or parsed["result_count"] != 1 or parsed["result_errors"] != [False]:
        raise RuntimeError("SOL judge did not return one successful result")
    try:
        verdict = json.loads(parsed["final"])
    except json.JSONDecodeError as exc:
        raise RuntimeError("SOL result is not JSON") from exc
    verdict = validate_verdict(verdict, template)
    base.atomic_json(output / "sol-verdict.json", verdict)
    receipt = {
        "schema_version": 1,
        "model": MODEL,
        "effort": EFFORT,
        "duration_seconds": round(time.monotonic() - before, 3),
        "packet_sha256": base.sha256_bytes(packet_path.read_bytes()),
        "template_sha256": base.sha256_bytes(template_path.read_bytes()),
        "verdict_sha256": base.sha256_bytes((output / "sol-verdict.json").read_bytes()),
        "mapping_read": False,
        "network_used": False,
        "retry_count": 0,
        "group_count": len(verdict["groups"]),
    }
    base.atomic_json(output / "sol-receipt.json", receipt)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--show-plan", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.show_plan:
        template = json.loads(args.template.read_text(encoding="utf-8"))
        print(json.dumps({"model": MODEL, "effort": EFFORT, "groups": len(template["groups"]), "retry": 0}, ensure_ascii=False, indent=2))
        return 0
    if not args.execute:
        parser.error("choose --show-plan or --execute")
    execute(args.packet.resolve(), args.template.resolve(), args.out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
