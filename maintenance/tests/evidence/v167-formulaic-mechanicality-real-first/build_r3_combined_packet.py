#!/usr/bin/env python3
"""Combine complete R3 pairs without choosing between duplicate drafts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import harness_r3 as r3


base = r3.base
ROOT = base.ROOT
RUN_ROOT = ROOT / "output/v167-formulaic-mechanicality-real-first"
PRIMARY = RUN_ROOT / "formal-r3"
SUPPLEMENT = RUN_ROOT / "formal-r3-supplement"


def load_manifest(run: Path) -> dict[str, Any]:
    value = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    if not isinstance(value.get("arms"), list):
        raise RuntimeError(f"invalid manifest: {run}")
    return value


def complete_pair(run: Path, case_id: str, by_arm: dict[str, dict[str, Any]]) -> bool:
    return all(
        bool(by_arm.get(f"{case_id}-{treatment}", {}).get("technical_valid"))
        for treatment in ("baseline", "candidate")
    )


def verified_final(run: Path, arm: dict[str, Any]) -> str:
    path = run / "raw" / arm["arm_id"] / "final.txt"
    text = path.read_text(encoding="utf-8")
    if base.sha256_text(text) != arm.get("final_sha256"):
        raise RuntimeError(f"final hash mismatch: {arm['arm_id']}")
    return text


def build(output: Path) -> None:
    if output.exists():
        raise RuntimeError(f"output must not exist: {output}")
    payload = r3.load_r3_payload()
    manifests = {"primary": load_manifest(PRIMARY), "supplement": load_manifest(SUPPLEMENT)}
    arms = {
        name: {item["arm_id"]: item for item in manifest["arms"]}
        for name, manifest in manifests.items()
    }
    output.mkdir(parents=True)
    packet = [
        "# WR-005 默认结构与条件用语查询匿名写稿包",
        "",
        "逐组检查事实、状态、篇幅、用户结构、文种功能、自然度和直接使用成本。单个正式连接词、用户指定尾语或有办理功能的文种用语不判机械化；只有无功能的固定开头、承启、总结、尾语或段落骨架成簇复现才计风险。不得推测处理身份。",
        "",
    ]
    mapping = []
    eligible = []
    for case in payload["cases"]:
        case_id = case["id"]
        available = [name for name in ("primary", "supplement") if complete_pair(
            PRIMARY if name == "primary" else SUPPLEMENT, case_id, arms[name]
        )]
        if not available:
            continue
        if len(available) > 1:
            raise RuntimeError(f"duplicate complete pair requires amendment: {case_id}")
        source_name = available[0]
        source_run = PRIMARY if source_name == "primary" else SUPPLEMENT
        first, second = base.blind_order(case_id)
        first_arm = arms[source_name][f"{case_id}-{first}"]
        second_arm = arms[source_name][f"{case_id}-{second}"]
        first_text = verified_final(source_run, first_arm)
        second_text = verified_final(source_run, second_arm)
        group = f"G{int(case_id[1:]):02d}"
        packet.extend([
            f"## {group} | {case['genre']}", "", "### 任务", "", str(case["request"]), "",
            "### 稿件甲", "", first_text.rstrip(), "", "### 稿件乙", "", second_text.rstrip(), "",
        ])
        mapping.append({
            "group": group,
            "case_id": case_id,
            "source_run": source_name,
            "稿件甲": first,
            "稿件乙": second,
        })
        eligible.append(group)
    packet_text = "\n".join(packet).rstrip() + "\n"
    base.atomic_text(output / "judge-export/blind-packet.md", packet_text)
    base.atomic_json(output / "restricted/mapping.json", {"schema_version": 1, "groups": mapping})
    template = {
        "schema_version": 1,
        "allowed_draft_verdicts": ["PASS", "WARN", "FAIL"],
        "allowed_winners": ["甲", "乙", "难分"],
        "groups": [
            {
                "group": group,
                "稿件甲": {"facts": "PASS|WARN|FAIL", "state": "PASS|WARN|FAIL", "length": "PASS|WARN|FAIL", "user_structure": "PASS|WARN|FAIL", "genre": "PASS|WARN|FAIL", "mechanicality": "PASS|WARN|FAIL", "direct_use_cost": "0|1|2|3|4"},
                "稿件乙": {"facts": "PASS|WARN|FAIL", "state": "PASS|WARN|FAIL", "length": "PASS|WARN|FAIL", "user_structure": "PASS|WARN|FAIL", "genre": "PASS|WARN|FAIL", "mechanicality": "PASS|WARN|FAIL", "direct_use_cost": "0|1|2|3|4"},
                "winner": "甲|乙|难分",
                "reason": "string",
            }
            for group in eligible
        ],
    }
    base.atomic_json(output / "judge-export/judge-template.json", template)
    freeze = {
        "schema_version": 1,
        "blind_packet_sha256": base.sha256_text(packet_text),
        "judge_template_sha256": base.sha256_bytes((output / "judge-export/judge-template.json").read_bytes()),
        "primary_manifest_sha256": base.sha256_bytes((PRIMARY / "manifest.json").read_bytes()),
        "supplement_manifest_sha256": base.sha256_bytes((SUPPLEMENT / "manifest.json").read_bytes()),
        "eligible_groups": eligible,
    }
    base.atomic_json(output / "judge-export/freeze.json", freeze)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    build(args.out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
