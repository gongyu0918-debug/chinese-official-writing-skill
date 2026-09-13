"""Reproduce business-condition false positives and test the bounded regex change."""

from __future__ import annotations

import argparse
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
OUT = ROOT / "output/prose-business-conditional-r16"
BASELINE = ROOT / "output/reference-integration-r16-final/candidate/scripts/prose_lint.py"
CANDIDATE = OUT / "candidate/scripts/prose_lint.py"
BASELINE_SHA256 = "513934d60e145087d992b2383dc92a522ecd9497446194ce1885e937800486fc"
LABEL = "protective-negative-inference"
MODES = ("draft-body", "gap-note-allowed")
BUSINESS_CONDITIONS = (
    "不能参会的会前向综合岗说明",
    "不能参会的，请会前向综合岗说明。",
    "无法到场的人员，应提前提交书面说明。",
    "不能按时提交材料的，请说明原因。",
    "不能当天办结的事项，窗口应说明办理进度。",
    "不能提交原件时，应提供其他证明。",
    "无法在线办理的，可由受理人员说明线下流程。",
    "不宜参加现场测试的设备，应另行确定检测时间。",
    "不能完成核验的，需另行确定补验时间。",
    "资金不足以支付全款的，出纳应说明支付安排。",
)
DIRECT_INFERENCES = (
    "设备已经恢复，但尚不能据此认定问题已经彻底消除。",
    "该记录不足以证明页面在这一时段始终正常。",
    "现有数据不能形成新增设备采购结论。",
    "本次抽查结果不宜作为确定长期改造方案的依据。",
    "仅凭统计尚无法推定变动原因。",
    "现有样本不能直接认定整体有效。",
    "现有记录不足以充分说明系统运行状况。",
    "现阶段无法据此准确判断长期趋势。",
    "暂时不能由此得出全面结论。",
    "记录不宜直接作为年度判断依据。",
    "现有证据不能证明预算已经落实。",
    "不同统计口径不能比较年度成本。",
    "本次结果仍不能说明项目已经完成。",
    "现有数据不宜据此确定资源规模。",
)
LONG_DISTANCE_INFERENCES = (
    "不能仅凭本次抽查结果认定问题已经彻底消除。",
    "不足以在缺少连续监测记录时证明系统始终正常。",
    "无法对不同统计周期的数据直接比较。",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def selected_findings(lint, text: str, mode: str) -> list:
    return [hit for hit in lint.scan("<business-condition>", text, include_format=True,
                                     include_structure=True, delivery_mode=mode) if hit.label == LABEL]


def cli_record(script: Path, text: str, mode: str) -> dict:
    command = [sys.executable, "-B", str(script), "--json", "--structure", "--format",
               "--delivery-mode", mode, "--strict", "--fail-on", "medium", "-"]
    result = subprocess.run(command, input=text, text=True, encoding="utf-8", capture_output=True)
    return {"command": command, "input": text, "mode": mode, "returncode": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr}


def protective_suite(script: Path) -> unittest.TestSuite:
    path = ROOT / "maintenance/tests/test_protective_negative_tail_lint.py"
    source = path.read_text(encoding="utf-8-sig")
    original_path = 'ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py"'
    assert source.count(original_path) == 2
    # Bind both the import and CLI path; retain every existing assertion and test method.
    bound = source.replace(original_path, "Path(SCRIPT_UNDER_TEST)")
    namespace = {"__file__": str(path), "__name__": "bound_protective_tests",
                 "SCRIPT_UNDER_TEST": str(script)}
    exec(compile(bound, str(path), "exec"), namespace)
    return unittest.defaultTestLoader.loadTestsFromTestCase(namespace["ProtectiveNegativeTailLintTests"])


def f03_suite(lint, script: Path, records: list, cli_records: list) -> unittest.TestSuite:
    path = ROOT / "maintenance/tests/evidence/prose-inline-r16/test_inline_residue.py"
    module = load_module("business_conditional_f03_tests", path)
    module.CANDIDATE = script
    return module.candidate_suite(lint, records, cli_records)


def new_suite(lint, script: Path, candidate: bool, cli_records: list) -> unittest.TestSuite:
    class BusinessConditionalTests(unittest.TestCase):
        def test_business_conditions_are_not_inference_tails(self):
            for text in BUSINESS_CONDITIONS:
                for mode in MODES:
                    with self.subTest(text=text, mode=mode):
                        hits = selected_findings(lint, text, mode)
                        self.assertEqual(bool(hits), not candidate)

        def test_direct_inference_family_and_severity_are_preserved(self):
            for text in DIRECT_INFERENCES:
                for mode in MODES:
                    with self.subTest(text=text, mode=mode):
                        hits = selected_findings(lint, text, mode)
                        self.assertEqual(len(hits), 1)
                        self.assertEqual(hits[0].severity, "medium")

        def test_long_distance_detection_tradeoff_is_explicit(self):
            for text in LONG_DISTANCE_INFERENCES:
                for mode in MODES:
                    with self.subTest(text=text, mode=mode):
                        self.assertEqual(bool(selected_findings(lint, text, mode)), not candidate)

        def test_business_condition_does_not_hide_a_later_real_inference(self):
            text = "不能参会的会前向综合岗说明。材料不足以证明问题已解决。"
            for mode in MODES:
                with self.subTest(mode=mode):
                    hits = selected_findings(lint, text, mode)
                    self.assertEqual(len(hits), 1 if candidate else 2)
                    self.assertTrue(any(hit.match == "不足以证明" for hit in hits))

        def test_modes_and_postscript_scope_stay_unchanged(self):
            text = DIRECT_INFERENCES[0]
            for mode in ("generic", "review-only"):
                self.assertEqual(selected_findings(lint, text, mode), [])
            note = "资料已核对。\n\n文后提示\n" + text
            self.assertEqual(selected_findings(lint, note, "gap-note-allowed"), [])

        def test_cli_keeps_business_condition_and_reports_real_inference(self):
            for mode in MODES:
                for text, expected in ((BUSINESS_CONDITIONS[0], 0 if candidate else 1),
                                       (DIRECT_INFERENCES[0], 1)):
                    with self.subTest(text=text, mode=mode):
                        result = cli_record(script, text, mode)
                        cli_records.append(result)
                        self.assertEqual(result["stderr"], "")
                        self.assertEqual(result["returncode"], expected)
                        hits = [hit for hit in json.loads(result["stdout"]) if hit["label"] == LABEL]
                        self.assertEqual(bool(hits), expected == 1)

    return unittest.defaultTestLoader.loadTestsFromTestCase(BusinessConditionalTests)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("baseline", "candidate"), required=True)
    args = parser.parse_args()
    assert sha256(BASELINE) == BASELINE_SHA256, "Final frozen script changed"
    script = CANDIDATE if args.phase == "candidate" else BASELINE
    lint = load_module("business_conditional_lint", script)
    records = []
    for family, texts in (("business_conditions", BUSINESS_CONDITIONS), ("direct_inferences", DIRECT_INFERENCES),
                          ("long_distance_tradeoff", LONG_DISTANCE_INFERENCES)):
        for text in texts:
            for mode in MODES:
                hits = selected_findings(lint, text, mode)
                records.append({"family": family, "text": text, "mode": mode,
                                "findings": [asdict(hit) for hit in hits]})
    remaining_ambiguity = "不能说明原因的，暂缓受理。"
    ambiguity_hits = selected_findings(lint, remaining_ambiguity, "draft-body")
    f03_records, f03_cli, cli_records = [], [], []
    full_protective = protective_suite(script)
    full_protective_count = full_protective.countTestCases()
    affected_f03 = f03_suite(lint, script, f03_records, f03_cli)
    f03_count = affected_f03.countTestCases()
    suite = new_suite(lint, script, args.phase == "candidate", cli_records)
    suite.addTests(full_protective)
    suite.addTests(affected_f03)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    assert sha256(BASELINE) == BASELINE_SHA256, "Final frozen script was modified"
    payload = {
        "phase": args.phase, "status": "PASS" if result.wasSuccessful() else "FAIL",
        "script": str(script), "script_sha256": sha256(script), "baseline_unchanged": True,
        "counts": {"tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
                   "new_methods": 6, "all_protective_methods": full_protective_count, "affected_f03_methods": f03_count},
        "matrix": records, "cli_records": cli_records, "f03_records": f03_records, "f03_cli": f03_cli,
        "remaining_ambiguity": {"text": remaining_ambiguity, "findings": [asdict(hit) for hit in ambiguity_hits]},
        "unittest_output": stream.getvalue(),
        "reused_tests": {name: sha256(ROOT / name) for name in (
            "maintenance/tests/test_protective_negative_tail_lint.py",
            "maintenance/tests/evidence/prose-inline-r16/test_inline_residue.py")},
    }
    OUT.mkdir(parents=True, exist_ok=True)
    attempt = len(list(OUT.glob(args.phase + "-*.json"))) + 1
    destination = OUT / f"{args.phase}-{attempt:03d}.json"
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "phase": args.phase, "counts": payload["counts"],
                      "output": str(destination)}, ensure_ascii=False))
    if not result.wasSuccessful():
        print(stream.getvalue())
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
