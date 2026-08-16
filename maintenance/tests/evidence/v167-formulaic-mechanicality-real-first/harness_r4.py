#!/usr/bin/env python3
"""Run R4: ordinary tasks skip formulaic language; explicit phrase requests load it."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
from typing import Any

import harness as base


EVIDENCE_ROOT = Path(__file__).resolve().parent
R4_CASES = EVIDENCE_ROOT / "cases-r4.json"
R3_CASES = EVIDENCE_ROOT / "cases-r3.json"
R1_CASES = EVIDENCE_ROOT / "cases.json"
PHRASE_PROTOTYPE = EVIDENCE_ROOT / "prototype-phrases-explicit-only-r4.md"
R4_CASES_SHA256 = "d08ebf5d81ac8060e8ac5294723bff46a68c0c590531528f27a318251a3606dc"
R3_CASES_SHA256 = "af459dd49b38daa86bd0f41d792f202723c2b877bdc62dcc91ca7ef7a9f5adc9"
R1_CASES_SHA256 = "0bab8696cd2bc82cb6a8e40244cb41fcef717385bf684f7b5df541e3b5780ba9"
PHRASE_PROTOTYPE_SHA256 = "b1540c40bc64b64ce9151770e425c79924f94cc9317957319ddd10385b0dd3ce"
ORIGINAL_RUN_ARM = base.run_arm


FORMULAIC_ROW = "| `references/formulaic-language.md` | 起草中/定稿前 | 起草或复核计划、汇报、调查报告、讲话稿、演讲词、答复、责任书、公开信、倡议书、建议信、新闻发布稿、总结、情况反映、情况综合、编者按、新闻、短评、讲解稿、宣传手册或宣传材料，且需要核对文种功能、开端、承启、综合或结尾用语时。文种明确、材料单一且该页功能表足以覆盖时，由该页直接结束文种路由；复杂任务再补对应长 reference。 |"
FORMULAIC_ROW_R4 = "| `references/formulaic-language.md` | 按需查询 | 仅当用户明确要求选择、核对或解释公文开端、引叙、承启、综合、期请或结尾用语时读取；普通起草、改写、压缩和复核不读取。 |"
TASK_ROUTE_ROW = "| `references/task-route-cards.md` | 起草前/改稿前 | 未被 `formulaic-language.md` 直接叶覆盖，且材料稀疏、短稿、低上下文局部修改，或用户明确要求不新增事实、只按已给材料写时，先判断是否完整命中材料稀疏的情况说明/通报/报告、未决事项会议纪要、短通知/限字通知、二次局部修改四类卡片之一；卡片不能覆盖或任务转为复杂时，再读 `workflow.md`、`genre-playbooks.md` 等长 reference。 |"
TASK_ROUTE_ROW_R4 = "| `references/task-route-cards.md` | 起草前/改稿前 | 材料稀疏、短稿、低上下文局部修改，或用户明确要求不新增事实、只按已给材料写时，先判断是否完整命中材料稀疏的情况说明/通报/报告、未决事项会议纪要、短通知/限字通知、二次局部修改四类卡片之一；卡片不能覆盖或任务转为复杂时，再读 `workflow.md`、`genre-playbooks.md` 等长 reference。 |"
NEWS_ROW = "| `references/genre-playbook-news-message.md` | 按文种选读 | 用户明确要求编者按、新闻稿、新闻消息、快讯、活动报道、活动新闻稿或新闻通稿时直接读取；材料单一的编者按已由 `formulaic-language.md` 完整覆盖时不重复加载。 |"
NEWS_ROW_R4 = "| `references/genre-playbook-news-message.md` | 按文种选读 | 用户明确要求编者按、新闻稿、新闻消息、快讯、活动报道、活动新闻稿或新闻通稿时直接读取。 |"
TASK_CARD_SENTENCE = "文种明确、材料单一且已经由 `formulaic-language.md` 的20类事务文体表完整覆盖时，不再读取本页。"


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")).hexdigest()


def replace_once(text: str, before: str, after: str, label: str) -> str:
    if text.count(before) != 1:
        raise RuntimeError(f"expected one {label} occurrence")
    return text.replace(before, after, 1)


def load_r4_payload() -> dict[str, Any]:
    for path, expected in (
        (R4_CASES, R4_CASES_SHA256), (R3_CASES, R3_CASES_SHA256),
        (R1_CASES, R1_CASES_SHA256), (PHRASE_PROTOTYPE, PHRASE_PROTOTYPE_SHA256),
    ):
        if normalized_sha256(path) != expected:
            raise RuntimeError(f"hash mismatch: {path.name}")
    plan = json.loads(R4_CASES.read_text(encoding="utf-8"))
    r1 = {item["id"]: item for item in json.loads(R1_CASES.read_text(encoding="utf-8"))["cases"]}
    r3 = {item["id"]: item for item in json.loads(R3_CASES.read_text(encoding="utf-8"))["cases"]}
    cases = []
    for item in plan["cases"]:
        source = r1[item["source_case_id"]] if "source_case_id" in item else r3[item["source_r3_id"]]
        cases.append({
            "id": item["id"], "provider": item["provider"], "genre": source["genre"],
            "request": source["request"], "phrase_lookup": bool(item["phrase_lookup"]),
        })
    return {"schema_version": 1, "models": plan["models"], "cases": cases}


def prepare_skill_roots(runtime: Path) -> dict[str, Any]:
    roots = runtime / "skills"
    baseline = roots / "baseline/chinese-official-writing"
    candidate = roots / "candidate/chinese-official-writing"
    if roots.exists():
        shutil.rmtree(roots)
    base.export_baseline(baseline)
    shutil.copytree(baseline, candidate)

    skill = (candidate / "SKILL.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    skill = replace_once(skill, FORMULAIC_ROW, FORMULAIC_ROW_R4, "formulaic route")
    skill = replace_once(skill, TASK_ROUTE_ROW, TASK_ROUTE_ROW_R4, "task-card route")
    skill = replace_once(skill, NEWS_ROW, NEWS_ROW_R4, "news route")
    (candidate / "SKILL.md").write_text(skill, encoding="utf-8", newline="\n")

    (candidate / "references/formulaic-language.md").write_text(
        PHRASE_PROTOTYPE.read_text(encoding="utf-8").replace("\r\n", "\n"),
        encoding="utf-8", newline="\n",
    )
    cards_path = candidate / "references/task-route-cards.md"
    cards = cards_path.read_text(encoding="utf-8").replace("\r\n", "\n")
    cards = replace_once(cards, TASK_CARD_SENTENCE, "", "task-card formulaic dependency")
    cards_path.write_text(cards, encoding="utf-8", newline="\n")

    baseline_manifest = base.tree_manifest(baseline)
    candidate_manifest = base.tree_manifest(candidate)
    baseline_by_path = {item["path"]: item["sha256"] for item in baseline_manifest}
    candidate_by_path = {item["path"]: item["sha256"] for item in candidate_manifest}
    differing = sorted(
        path for path in set(baseline_by_path) | set(candidate_by_path)
        if baseline_by_path.get(path) != candidate_by_path.get(path)
    )
    expected = ["SKILL.md", "references/formulaic-language.md", "references/task-route-cards.md"]
    if differing != expected:
        raise RuntimeError(f"unexpected prototype diff: {differing}")
    receipt = {
        "baseline_commit": base.BASELINE_COMMIT,
        "baseline_product_tree": base.BASELINE_PRODUCT_TREE,
        "baseline_root": str(baseline.resolve()), "candidate_root": str(candidate.resolve()),
        "baseline_file_count": len(baseline_manifest), "candidate_file_count": len(candidate_manifest),
        "differing_paths": differing,
        "baseline_manifest_sha256": base.sha256_text(json.dumps(baseline_manifest, sort_keys=True)),
        "candidate_manifest_sha256": base.sha256_text(json.dumps(candidate_manifest, sort_keys=True)),
    }
    base.atomic_json(runtime / "skill-roots.json", receipt)
    return receipt


def run_arm(
    claude: str, output: Path, runtime: Path, skill_roots: dict[str, Path], models: dict[str, str],
    case: dict[str, Any], treatment: str,
) -> dict[str, Any]:
    result = ORIGINAL_RUN_ARM(claude, output, runtime, skill_roots, models, case, treatment)
    formulaic_reads = [
        value for value in result["stream"]["reads"]
        if Path(value).as_posix().endswith("/references/formulaic-language.md")
    ]
    route_ok = True
    if treatment == "candidate":
        route_ok = bool(formulaic_reads) is bool(case["phrase_lookup"])
    result["checks"]["explicit_phrase_route"] = route_ok
    result["phrase_lookup"] = {
        "expected": bool(case["phrase_lookup"]) if treatment == "candidate" else None,
        "read": bool(formulaic_reads),
    }
    result["technical_valid"] = all(result["checks"].values())
    base.atomic_json(output / "raw" / result["arm_id"] / "meta.json", result)
    return result


base.PROTOTYPE_PATH = PHRASE_PROTOTYPE
base.PROTOTYPE_SHA256 = PHRASE_PROTOTYPE_SHA256
base.EXPECTED_CASES = 9
base.EXPECTED_PER_PROVIDER = 3
base.EXPECTED_CALLS = 18
base.AUTH_ENV = "V167_FORMULAIC_R4_AUTH"
base.AUTH_VALUE = "APPROVED_BY_USER_20260817"
base.load_payload = load_r4_payload
base.prepare_skill_roots = prepare_skill_roots
base.run_arm = run_arm


if __name__ == "__main__":
    raise SystemExit(base.main())
