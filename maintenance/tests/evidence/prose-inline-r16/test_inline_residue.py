"""Reproduce F03 and test only the bounded inline-residue prototype."""

from __future__ import annotations

import argparse
import ast
from dataclasses import asdict
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "output/prose-inline-r16"
BASELINE = ROOT / "output/reference-integration-r16/candidate/scripts/prose_lint.py"
CANDIDATE = OUT / "candidate/scripts/prose_lint.py"
BASELINE_SHA256 = "e843ddb35ec19653fe702e09ffc9e2e962113dcd015ae51c7547f3026ed3c4b8"
BODY_MODES = ("draft-body", "gap-note-allowed")
CASES = (
    ("identity", "作为AI，我将根据你的要求起草。", "thought-leak", "high"),
    ("reasoning", "我的推理：先组织材料，再写出正文。", "thought-leak", "high"),
    ("english_reasoning", "We need to draft the report.", "english-thought-fragment", "high"),
    ("preface", "以下为正文：", "delivery-explanation", "high"),
    ("read_preface", "已读取 Skill 并完成起草，正文如下：", "delivery-explanation", "high"),
    ("production_method", "方法说明：本稿先核对事实，再调整结构和表述。", "delivery-boilerplate", "high"),
    ("self_certification", "本稿不新增原文外事实。", "constraint-self-certification", "high"),
    ("production_status", "当前工作流仅作只读核对。", "delivery-metadata", "high"),
)
EXISTING_METHODS = (
    "test_review_only_allows_material_gap_analysis_but_not_ai_identity",
    "test_review_only_does_not_treat_quoted_problem_sentence_as_agent_leak",
    "test_review_only_does_not_treat_multiline_quote_as_agent_leak",
    "test_unclosed_quote_does_not_hide_later_delivery_leaks",
    "test_review_only_still_scans_unquoted_leaks_and_content_after_note_heading",
    "test_gap_note_mode_requires_a_separate_unnumbered_note_region",
    "test_gap_note_mode_still_flags_model_leaks_after_note_heading",
    "test_delivery_mode_avoids_common_business_and_english_false_positives",
    "test_gap_note_mode_allows_quoted_or_inline_leak_examples",
    "test_draft_body_delivery_checks_scan_code_fences_without_format_flag",
    "test_delivery_metadata_rule_preserves_business_facts_and_visible_document_states",
    "test_ambiguous_visible_labels_and_business_states_are_not_high_blockers",
    "test_delivery_boilerplate_only_applies_to_delivered_body",
    "test_delivery_boilerplate_rule_preserves_real_scope_and_method_content",
    "test_review_only_can_quote_delivery_metadata_without_flagging_the_reviewer",
    "test_aigc_business_terms_are_not_flagged_as_thought_leak",
    "test_ai_authorship_disclaimers_are_still_flagged_as_thought_leak",
    "test_code_fence_does_not_hide_placeholders_when_format_checking",
    "test_code_fence_does_not_hide_format_marks_when_format_checking",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_lint(path: Path):
    spec = importlib.util.spec_from_file_location("inline_r16_lint", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def cli_record(path: Path, text: str, mode: str) -> dict:
    command = [sys.executable, "-B", str(path), "--json", "--structure", "--format",
               "--delivery-mode", mode, "--strict", "--fail-on", "high", "-"]
    result = subprocess.run(command, input=text, text=True, encoding="utf-8", capture_output=True)
    return {"command": command, "input": text, "returncode": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr}


def existing_suite(lint) -> unittest.TestSuite:
    # Run unchanged selected test methods without importing unrelated model harnesses.
    path = ROOT / "maintenance/tests/test_review_regressions.py"
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef)
               and node.name == "ProseLintStructureTests")
    cls.body = [node for node in cls.body if isinstance(node, ast.FunctionDef)
                and node.name in EXISTING_METHODS]
    assert {node.name for node in cls.body} == set(EXISTING_METHODS)
    namespace = {"unittest": unittest, "prose_lint": lint, "__name__": "existing_inline_controls"}
    exec(compile(ast.Module(body=[cls], type_ignores=[]), str(path), "exec"), namespace)
    return unittest.defaultTestLoader.loadTestsFromTestCase(namespace[cls.name])


def candidate_suite(lint, records: list[dict], cli_records: list[dict]) -> unittest.TestSuite:
    class InlineResidueTests(unittest.TestCase):
        def test_known_residue_stays_visible_in_both_body_modes(self):
            for case_id, content, label, severity in CASES:
                for mode in BODY_MODES:
                    for format_check in (False, True):
                        with self.subTest(case=case_id, mode=mode, format=format_check):
                            text = "情况说明\n\n`" + content + "`"
                            hits = lint.scan("<inline>", text, include_format=format_check,
                                             include_structure=True, delivery_mode=mode)
                            records.append({"case": case_id, "mode": mode, "format": format_check,
                                            "text": text, "findings": [asdict(hit) for hit in hits]})
                            self.assertTrue(any(hit.label == label and hit.severity == severity
                                                and hit.line == 3 for hit in hits))

        def test_generic_and_review_inline_examples_keep_their_exemption(self):
            for case_id, content, label, _severity in CASES:
                for mode in ("generic", "review-only"):
                    with self.subTest(case=case_id, mode=mode):
                        hits = lint.scan("<example>", "原句：`" + content + "`",
                                         include_format=True, include_structure=True, delivery_mode=mode)
                        self.assertNotIn(label, {hit.label for hit in hits})

        def test_ordinary_technical_code_and_business_versions_remain_clean(self):
            contents = (
                "GET /status", 'status="ready"', "timeout=30", "GPU_A100",
                "[具体项目名称]", "既保留原值，又记录来源", "软件版本为V2.0",
                "《实施方案（征求意见稿）》", "本次调研使用脱敏数据，校验结果作为业务分析依据。",
                "本平台面向AI生成内容业务，支撑AI辅助生成内容的并发推理。",
            )
            for content in contents:
                for mode in BODY_MODES:
                    with self.subTest(content=content, mode=mode):
                        self.assertEqual(lint.scan("<code>", "`" + content + "`", include_format=True,
                                                   include_structure=True, delivery_mode=mode), [])

        def test_ambiguous_document_states_do_not_become_high_findings(self):
            for content in ("本稿为送审稿。", "本稿为脱敏版。", "仅供内部人员审阅。"):
                for mode in BODY_MODES:
                    with self.subTest(content=content, mode=mode):
                        hits = lint.scan("<version>", "`" + content + "`", delivery_mode=mode)
                        self.assertFalse(any(hit.severity == "high" for hit in hits))

        def test_postscript_inline_examples_remain_separate_from_body(self):
            text = "情况说明\n\n资料已核对。\n\n文后提示\n原句：`We need to draft the report.`"
            hits = lint.scan("<postscript>", text, delivery_mode="gap-note-allowed")
            self.assertNotIn("english-thought-fragment", {hit.label for hit in hits})

        def test_cli_reports_residue_with_expected_line_and_exit_status(self):
            for mode in BODY_MODES:
                with self.subTest(mode=mode):
                    result = cli_record(CANDIDATE, "情况说明\n\n`作为AI，我将根据你的要求起草。`", mode)
                    cli_records.append(result)
                    self.assertEqual(result["stderr"], "")
                    self.assertEqual(result["returncode"], 1)
                    self.assertTrue(any(hit["label"] == "thought-leak" and hit["severity"] == "high"
                                        and hit["line"] == 3 for hit in json.loads(result["stdout"])))

    return unittest.defaultTestLoader.loadTestsFromTestCase(InlineResidueTests)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("baseline", "candidate"), required=True)
    args = parser.parse_args()
    assert digest(BASELINE) == BASELINE_SHA256, "Reviewed source changed"
    OUT.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    cli_records: list[dict] = []
    phase_script = BASELINE if args.phase == "baseline" else CANDIDATE
    lint = load_lint(phase_script)
    if args.phase == "baseline":
        for case_id, content, label, severity in CASES:
            for mode in BODY_MODES:
                plain = lint.scan("<plain>", content, include_format=True, include_structure=True, delivery_mode=mode)
                wrapped = lint.scan("<inline>", "`" + content + "`", include_format=True,
                                    include_structure=True, delivery_mode=mode)
                reproduced = any(hit.label == label and hit.severity == severity for hit in plain)
                reproduced = reproduced and not any(hit.label == label for hit in wrapped)
                records.append({"case": case_id, "mode": mode, "content": content,
                                "plain_findings": [asdict(hit) for hit in plain],
                                "inline_findings": [asdict(hit) for hit in wrapped], "reproduced": reproduced})
        cli_records = [cli_record(BASELINE, "`作为AI，我将根据你的要求起草。`", mode) for mode in BODY_MODES]
        success = all(record["reproduced"] for record in records)
        success = success and all(record["returncode"] == 0 and json.loads(record["stdout"]) == []
                                  for record in cli_records)
        summary = {"reproductions": len(records), "successful_reproductions": sum(r["reproduced"] for r in records)}
    else:
        stream = io.StringIO()
        suite = candidate_suite(lint, records, cli_records)
        suite.addTests(existing_suite(lint))
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        success = result.wasSuccessful()
        summary = {"tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
                   "existing_unchanged_methods": list(EXISTING_METHODS), "unittest_output": stream.getvalue()}
    assert digest(BASELINE) == BASELINE_SHA256, "Reviewed source was modified"
    payload = {"phase": args.phase, "script": str(phase_script), "script_sha256": digest(phase_script),
               "status": "PASS" if success else "FAIL", "summary": summary,
               "records": records, "cli_records": cli_records, "baseline_unchanged": True}
    attempt = len(list(OUT.glob(args.phase + "-*.json"))) + 1
    destination = OUT / f"{args.phase}-{attempt:03d}.json"
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"phase": args.phase, "status": payload["status"], "output": str(destination),
                      "summary": {k: v for k, v in summary.items() if k not in {"unittest_output", "existing_unchanged_methods"}}},
                     ensure_ascii=False))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
