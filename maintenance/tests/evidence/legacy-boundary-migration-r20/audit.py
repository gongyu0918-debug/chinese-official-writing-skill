"""Finalize R20 evidence without executing tests or changing product files."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess

E = Path(__file__).resolve().parent
ROOT = E.parents[3]
TARGET = ROOT / "maintenance/tests/test_skill_boundary.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def definitions(text):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(text))
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


baseline = (E / "baseline-test_skill_boundary.py").read_text("utf-8")
current = TARGET.read_text("utf-8")
catalog = json.loads((E / "migration-catalog.json").read_text("utf-8"))
full = json.loads((E / "module-run.json").read_text("utf-8"))
focused = json.loads((E / "heading-wrapper-focused.json").read_text("utf-8"))
before, after = definitions(baseline), definitions(current)
assert set(before) == set(after)
changed = sorted(k for k in before if before[k] != after[k])
assert set(changed) == {r["method"] for r in catalog} and len(changed) == 50
assert len([k for k in after if k.startswith("test_")]) == 81
for protected in ["read_routing_surfaces", "read_field_boundary", "assert_rules", "assert_route",
                  "test_sparse_length_rule_keeps_fact_boundary_without_short_first_priority",
                  "test_review_command_includes_interpreter_and_draft_path"]:
    assert before[protected] == after[protected], protected
assert re.findall(r'^(?:CURRENT|PUBLISHED)_VERSION = .*$', baseline, re.M) == re.findall(r'^(?:CURRENT|PUBLISHED)_VERSION = .*$', current, re.M)
wrapper_start = current.index("        # The retired short-draft page also protected whole-body wrappers.")
wrapper_end = current.index("\n    def test_plain_text_title_boundary_contract_is_explicit", wrapper_start)
tested = current[:wrapper_start] + current[wrapper_end:]
tested_bytes = tested.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")
assert hashlib.sha256(tested_bytes).hexdigest() == full["module_sha256"]
(E / "module-tested-before-wrappers.py").write_bytes(tested_bytes)
full_defs = definitions(tested)
assert [k for k in after if full_defs[k] != after[k]] == ["test_long_form_headings_warn_against_markdown_bold"]
assert sha(TARGET) == focused["module_sha256"]
assert full["returncode"] == focused["returncode"] == 0
assert sha(E / "module-python313.log") == full["log_sha256"]
assert sha(E / "heading-wrapper-focused.log") == focused["log_sha256"]
log = (E / "module-python313.log").read_text("utf-8")
assert "Ran 81 tests" in log and log.rstrip().endswith("OK")
assert "FAIL:" not in log and "ERROR:" not in log
product_diff = subprocess.run(["git", "diff", "--name-only", "HEAD", "--", "chinese-official-writing", "packages"],
                              cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
assert not product_diff
for row in catalog:
    if row["method"] == "test_long_form_headings_warn_against_markdown_bold" and "完整模块通过后补回" not in row["migration"]:
        row["migration"] += " 完整模块通过后补回整稿代码围栏/横线的3个真实CLI正反例，单独复验该方法通过。"
    node = next(n for n in ast.walk(ast.parse(current)) if isinstance(n, ast.FunctionDef) and n.name == row["method"])
    row["current_line"] = node.lineno
    row["explicit_owner_names"] = sorted({n.value for n in ast.walk(node) if isinstance(n, ast.Constant)
                                           and isinstance(n.value, str) and re.fullmatch(r"[a-z][a-z0-9-]+\.md", n.value)})
(E / "migration-catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", "utf-8")

pending = [
    {"id": "G01", "kind": "specific_native_behavior_unverified", "responsibility": "仅有报送邮箱/接收单位时不得推定发文主体",
     "current_support": "通知对象保留原称谓、落款采用已有信息；共性主体对象保真；审核分开发文主体与动作主体。",
     "limit": "本次没有此输入的真实改稿输出；静态断言证明明确约束存在，不能证明模型已执行，也未证明产品丢失。"},
    {"id": "G02", "kind": "specific_native_behavior_unverified", "responsibility": "Token数量、调用次数、单价及费用关系不互换",
     "current_support": "算力页分别列Token/调用次数且单位保持一致，Token主线承接费用；校对页核数字金额单位与材料一致。",
     "limit": "未新增具体Token/调用次数样稿或模型调用。不能将通用单位保护报告成该案例已通过。"},
    {"id": "G04-examples", "kind": "specific_formalization_examples_unverified", "responsibility": "老板关心/钱花得值/马上要搞等口语正式化不得增强身份、评价、程序或承诺",
     "current_support": "同义正式语体、叙述身份/条件/可能性/论断强度保真及具体责任程序成效需依据。",
     "limit": "不要求恢复旧例句；仅迁移明确语义。本模块不执行这些写稿样例，结果仍待既有或后续实稿核对。"},
    {"id": "G03/G04/G06/G08-native", "kind": "document_contract_is_not_generation_test", "responsibility": "标题/语法/多轮/专叶在真实生成中的执行",
     "current_support": "具体条件、例外、角色、状态和修改粒度已在对应方法中逐项断言；3个包装与5个既有CLI检查真实执行。",
     "limit": "其他文稿语义为文档契约测试，不是81个模型能力样本。没有未解静态失败不等于重构功能全部验收。"},
]
summary = {
    "baseline_head": "95e29838e7f8cf4ef54c7433870eb5d8ab214458",
    "baseline_module_sha256": sha(E / "baseline-test_skill_boundary.py"),
    "final_module_sha256": sha(TARGET), "methods_preserved": 81, "changed_methods": len(changed),
    "unchanged_methods": 31, "helpers_and_version_constants_preserved": True,
    "r18_cli_methods_unchanged": True, "product_and_mirror_diff_from_head": [],
    "full_module": {**full, "run_count": 1, "methods": 81, "passed": 81, "failure_events": 0, "error_events": 0, "skipped": 0},
    "final_delta": {**focused, "changed_methods_after_full_run": ["test_long_form_headings_warn_against_markdown_bold"],
                    "other_80_methods_identical_to_full_run": True, "focused_passed": 1, "new_cli_cases": 3},
    "final_supported_method_outcomes": {"passed": 81, "unresolved_failure_methods": 0,
        "basis": "one 81-method run, then 1 changed method rechecked; not a second full-module run"},
    "actual_cli_cases": {"preserved_length_modes": 2, "preserved_prose_modes": 3, "new_wrapper_cases": 3, "total": 8},
    "pending_responsibilities": pending, "new_models_run": 0, "whole_repository_suites_run": 0, "commit_created": False,
    "historical_r17_log_sha256": sha(ROOT / "output/legacy-boundary-current-r17/run-python313.log"),
    "evidence": {name: sha(E / name) for name in ["module-python313.log", "heading-wrapper-focused.log", "module-run.json",
                                                   "heading-wrapper-focused.json", "migration-catalog.json"]},
}
assert summary["historical_r17_log_sha256"] == "7833d5d508919da66dba978374db4dba25da58c6d8aba6892dea5c12cef624c8"
(E / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", "utf-8")
rows = ["| 方法 | 责任组 | 本轮迁移 | 当前明确页 |", "| --- | --- | --- | --- |"]
for row in sorted(catalog, key=lambda r: r["current_line"]):
    rows.append(f"| `{row['method']}` | {row['group']} | {row['migration']} | {', '.join(row['explicit_owner_names'])} |")
(E / "method-migration.md").write_text("# 50 个方法的责任迁移\n\n" + "\n".join(rows) + "\n", "utf-8")
print(json.dumps({"method_count": 81, "changed_methods": 50, "full_run_passed": 81,
                  "focused_passed": 1, "unresolved_static_failure_methods": 0,
                  "final_module_sha256": summary["final_module_sha256"]}))
