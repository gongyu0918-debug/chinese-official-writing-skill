#!/usr/bin/env python3
"""Run four candidate-only R6 drafts before any routing work."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import threading
from typing import Any

import harness_r4 as r4


base = r4.base
CASE_IDS = ("Q04", "Q05", "Q07", "Q08")
OLD_INTRO = "下表只提示文体功能和常用接引，不是固定模板。材料不足时不为补齐表中环节编造事实。"
NEW_INTRO = "下表用于核对文种功能，不是成稿提纲或逐项补齐清单。只采用本题有事实支撑、且完成文种任务确实需要的功能；没有事实支撑的结构轴直接省略，不用空泛目的、同义复述或固定开合补齐篇幅。"
OLD_HEADER = "| 文体 | 必须完成的功能 | 可按需使用的接引或收束 |"
NEW_HEADER = "| 文体 | 按材料选择的功能 | 可按需使用的接引或收束 |"


def load_r6_payload() -> dict[str, Any]:
    payload = r4.load_r4_payload()
    by_id = {item["id"]: item for item in payload["cases"]}
    cases = [by_id[case_id] for case_id in CASE_IDS]
    models = {
        key: value
        for key, value in payload["models"].items()
        if key in {"ollama", "alibaba2"}
    }
    return {"schema_version": 1, "models": models, "cases": cases}


def replace_once(text: str, before: str, after: str) -> str:
    if text.count(before) != 1:
        raise RuntimeError(f"R6 replacement mismatch: {before}")
    return text.replace(before, after, 1)


def prepare_skill_roots(runtime: Path) -> dict[str, Any]:
    roots = runtime / "skills"
    baseline = roots / "baseline/chinese-official-writing"
    candidate = roots / "candidate/chinese-official-writing"
    if roots.exists():
        shutil.rmtree(roots)
    base.export_baseline(baseline)
    shutil.copytree(baseline, candidate)
    target = candidate / "references/formulaic-language.md"
    text = target.read_text(encoding="utf-8").replace("\r\n", "\n")
    text = replace_once(text, OLD_INTRO, NEW_INTRO)
    text = replace_once(text, OLD_HEADER, NEW_HEADER)
    target.write_text(text, encoding="utf-8", newline="\n")
    baseline_manifest = base.tree_manifest(baseline)
    candidate_manifest = base.tree_manifest(candidate)
    baseline_by_path = {item["path"]: item["sha256"] for item in baseline_manifest}
    candidate_by_path = {item["path"]: item["sha256"] for item in candidate_manifest}
    differing = sorted(
        path
        for path in set(baseline_by_path) | set(candidate_by_path)
        if baseline_by_path.get(path) != candidate_by_path.get(path)
    )
    if differing != ["references/formulaic-language.md"]:
        raise RuntimeError(f"unexpected R6 prototype diff: {differing}")
    receipt = {
        "baseline_commit": base.BASELINE_COMMIT,
        "baseline_product_tree": base.BASELINE_PRODUCT_TREE,
        "baseline_root": str(baseline.resolve()),
        "candidate_root": str(candidate.resolve()),
        "differing_paths": differing,
        "baseline_manifest_sha256": base.sha256_text(
            json.dumps(baseline_manifest, sort_keys=True)
        ),
        "candidate_manifest_sha256": base.sha256_text(
            json.dumps(candidate_manifest, sort_keys=True)
        ),
    }
    base.atomic_json(runtime / "skill-roots.json", receipt)
    return receipt


def run_candidate_arm(
    claude: str,
    output: Path,
    runtime: Path,
    skill_roots: dict[str, Path],
    models: dict[str, str],
    case: dict[str, Any],
) -> dict[str, Any]:
    result = r4.ORIGINAL_RUN_ARM(
        claude, output, runtime, skill_roots, models, case, "candidate"
    )
    formulaic_read = any(
        Path(value).as_posix().endswith("/references/formulaic-language.md")
        for value in result["stream"]["reads"]
    )
    result["checks"]["formulaic_read"] = formulaic_read
    result["technical_valid"] = all(result["checks"].values())
    base.atomic_json(output / "raw" / result["arm_id"] / "meta.json", result)
    return result


def run_candidate_lane(
    claude: str,
    output: Path,
    runtime: Path,
    skill_roots: dict[str, Path],
    models: dict[str, str],
    cases: list[dict[str, Any]],
    progress: list[dict[str, Any]],
    lock: threading.Lock,
) -> list[dict[str, Any]]:
    results = []
    for case in cases:
        result = run_candidate_arm(
            claude, output, runtime, skill_roots, models, case
        )
        results.append(result)
        with lock:
            progress.append(
                {
                    "arm_id": result["arm_id"],
                    "technical_valid": result["technical_valid"],
                    "finished_utc": result["finished_utc"],
                }
            )
            base.atomic_json(
                output / "progress.json",
                {"completed": len(progress), "total": 4, "arms": progress},
            )
    return results


def build_candidate_packets(
    output: Path, cases: list[dict[str, Any]], results: list[dict[str, Any]]
) -> dict[str, Any]:
    expected = {f"{case['id']}-candidate" for case in cases}
    actual = {result["arm_id"] for result in results}
    if actual != expected:
        raise RuntimeError(f"candidate-only arm mismatch: {sorted(actual)}")
    receipt = {
        "schema_version": 1,
        "candidate_only": True,
        "arms": {
            result["arm_id"]: result["final_sha256"]
            for result in sorted(results, key=lambda item: item["arm_id"])
        },
        "eligible_groups": [],
    }
    base.atomic_json(output / "candidate-only-freeze.json", receipt)
    return receipt


def finalize_existing(output: Path) -> None:
    payload = load_r6_payload()
    results = []
    for case in payload["cases"]:
        arm_id = f"{case['id']}-candidate"
        meta_path = output / "raw" / arm_id / "meta.json"
        final_path = output / "raw" / arm_id / "final.txt"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        final = final_path.read_text(encoding="utf-8")
        if meta.get("arm_id") != arm_id or meta.get("final_sha256") != base.sha256_text(
            final
        ):
            raise RuntimeError(f"candidate-only output mismatch: {arm_id}")
        results.append(meta)
    freeze = build_candidate_packets(output, payload["cases"], results)
    manifest = {
        "schema_version": 1,
        "baseline_commit": base.BASELINE_COMMIT,
        "calls_planned": 4,
        "calls_completed": len(results),
        "technical_valid": sum(item["technical_valid"] for item in results),
        "pairs_eligible": len(freeze["eligible_groups"]),
        "candidate_only": True,
        "postprocess_recovered": True,
        "arms": sorted(results, key=lambda item: item["arm_id"]),
    }
    base.atomic_json(output / "manifest.json", manifest)


base.EXPECTED_CASES = 4
base.EXPECTED_PER_PROVIDER = 2
base.EXPECTED_CALLS = 4
base.MAX_PROVIDER_LANES = 2
base.AUTH_ENV = "V167_FORMULAIC_R6_AUTH"
base.AUTH_VALUE = "APPROVED_BY_USER_20260817"
base.load_payload = load_r6_payload
base.prepare_skill_roots = prepare_skill_roots
base.run_lane = run_candidate_lane
base.build_packets = build_candidate_packets


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--finalize-existing":
        finalize_existing(Path(sys.argv[2]).resolve())
        raise SystemExit(0)
    raise SystemExit(base.main())
