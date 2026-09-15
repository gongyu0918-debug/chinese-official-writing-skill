from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LABELS = {
    "protective-negative-inference",
    "unresolved-conclusion-tail",
    "negative-boundary-tail",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


prose_lint = load_module(
    "protective_negative_tail_prose_lint",
    ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py",
)


def protective_findings(text: str, *, delivery_mode: str = "draft-body"):
    return [
        item
        for item in prose_lint.scan("<protective-tail>", text, delivery_mode=delivery_mode)
        if item.label in LABELS
    ]


class ProtectiveNegativeTailLintTests(unittest.TestCase):
    def test_locates_preregistered_protective_tail_families(self) -> None:
        samples = {
            "设备已经恢复，但尚不能据此认定问题已经彻底消除。": "protective-negative-inference",
            "该记录不足以证明页面在这一时段始终正常。": "protective-negative-inference",
            "现有数据不能形成新增设备采购结论。": "protective-negative-inference",
            "本次抽查结果不宜作为确定长期改造方案的依据。": "protective-negative-inference",
            "异常原因尚未形成正式结论。": "unresolved-conclusion-tail",
            "会议还讨论了接入范围，但尚未形成决定。": "unresolved-conclusion-tail",
            "会议尚未形成具体安排。": "unresolved-conclusion-tail",
            "页面已恢复，这不代表异常已经根本解决。": "negative-boundary-tail",
            "本阶段支出已经核定，但不构成扩大设备数量后的预算依据。": "negative-boundary-tail",
            "本阶段支出可供参考，但不直接等同于扩大设备数量后的预算需求。": "negative-boundary-tail",
            "法律顾问书面意见载明：相关事实已经查明，但不构成合同违约。": "negative-boundary-tail",
        }

        for text, expected_label in samples.items():
            with self.subTest(text=text):
                findings = protective_findings(text)
                self.assertEqual([item.label for item in findings], [expected_label])
                self.assertEqual(findings[0].severity, "medium")

    def test_common_business_negatives_are_not_flagged(self) -> None:
        samples = [
            "截至7月31日，26件事项尚在办理。",
            "事故原因正在调查中。",
            "4次异常均已恢复，未发现数据丢失。",
            "各科室不得迟报、漏报。",
            "业务处验收时间待确认。",
            "信息中心于8月15日前完成测试，测试通过后再确定上线时间。",
            "经会议研究，决定于8月5日启用新接口。",
            "该行为不构成合同违约。",
            "未经批准不得作出决定。",
            "未按规定作出决定的，应当重新履行程序。",
            "未在会议上作出决定。",
        ]

        for text in samples:
            with self.subTest(text=text):
                self.assertEqual(protective_findings(text), [])

    def test_hints_apply_to_body_in_both_delivery_modes(self) -> None:
        samples = {
            "异常原因尚未形成正式结论。": "unresolved-conclusion-tail",
            "设备已经恢复，但尚不能据此认定问题已经彻底消除。": "protective-negative-inference",
            "页面已恢复，这不代表异常已经根本解决。": "negative-boundary-tail",
        }
        for text, label in samples.items():
            with self.subTest(label=label):
                self.assertEqual(protective_findings(text, delivery_mode="generic"), [])
                self.assertEqual(protective_findings(text, delivery_mode="review-only"), [])
                body = protective_findings(text, delivery_mode="draft-body")
                allowed = protective_findings(text, delivery_mode="gap-note-allowed")
                self.assertEqual(allowed, body)
                self.assertEqual([item.label for item in body], [label])
                self.assertEqual(body[0].severity, "medium")

    def test_explicit_postscript_is_exempt_but_business_headings_keep_body_hints(self) -> None:
        tail = "异常原因尚未形成正式结论。"
        for heading in ("文后提示", "正文外提示", "待确认事项（正文外）"):
            with self.subTest(note=heading):
                text = f"已完成核对。\n\n{heading}\n{tail}"
                self.assertEqual(protective_findings(text, delivery_mode="gap-note-allowed"), [])
                findings = protective_findings(text, delivery_mode="draft-body")
                self.assertEqual([item.label for item in findings], ["unresolved-conclusion-tail"])
                self.assertEqual(findings[0].severity, "medium")
                labels = {item.label for item in prose_lint.scan("<test>", text, delivery_mode="draft-body")}
                self.assertIn("unexpected-external-note", labels)
        for heading in ("待确认事项", "风险提醒", "补充信息", "二、待确认事项", "二、风险提醒", "二、补充信息"):
            with self.subTest(business=heading):
                text = f"一、进展\n已完成核对。\n\n{heading}\n{tail}"
                self.assertEqual(prose_lint.body_lines(text.splitlines()), text.splitlines())
                body = protective_findings(text)
                allowed = protective_findings(text, delivery_mode="gap-note-allowed")
                self.assertEqual(allowed, body)
                self.assertEqual([item.label for item in body], ["unresolved-conclusion-tail"])
                self.assertEqual(body[0].line, 5)

    def test_unresolved_phrases_are_locatable_review_signals(self) -> None:
        for text in ("会议尚未形成决定。", "异常原因尚未形成正式结论。", "会议尚未形成具体安排。"):
            with self.subTest(text=text):
                findings = protective_findings(text)
                self.assertEqual(len(findings), 1)
                self.assertEqual(findings[0].label, "unresolved-conclusion-tail")
                self.assertEqual(findings[0].severity, "medium")
                self.assertEqual(findings[0].line, 1)
                self.assertIn(findings[0].match, text)

    def test_unresolved_conclusion_must_end_the_sentence(self) -> None:
        text = "会议尚未形成决定，下一步继续研究。"

        self.assertEqual(protective_findings(text), [])

    def test_clean_corpus_has_no_new_medium_hint(self) -> None:
        corpus = json.loads(
            (ROOT / "maintenance" / "tests" / "fixtures" / "clean_prose_corpus.json").read_text(
                encoding="utf-8"
            )
        )

        for item in corpus["items"]:
            with self.subTest(item=item["id"]):
                self.assertEqual(protective_findings(item["text"]), [])

    def test_cli_medium_gate_is_read_only(self) -> None:
        script = ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py"
        original = "运行记录已经汇总，但尚不能据此认定问题已经彻底消除。"
        with tempfile.TemporaryDirectory() as temp_dir:
            draft = Path(temp_dir) / "draft.txt"
            draft.write_text(original, encoding="utf-8")
            before = draft.read_bytes()
            results = [
                subprocess.run(
                    [sys.executable, str(script), str(draft), "--delivery-mode", mode,
                     "--strict", "--fail-on", "medium"],
                    capture_output=True, text=True, encoding="utf-8",
                )
                for mode in ("draft-body", "gap-note-allowed")
            ]
            after = draft.read_bytes()

        for result in results:
            self.assertEqual(result.returncode, 1)
            self.assertIn("protective-negative-inference", result.stdout)
        self.assertEqual(results[0].stdout, results[1].stdout)
        self.assertEqual(before, after)

    def test_cause_inference_alone_does_not_trigger_lint(self) -> None:
        # 检查机械扫描的边界；这些句子是否适合具体稿件由真实写稿复核。
        for text in (
            "为满足日常办公需要，拟更新2台办公电脑。",
            "现有设备已难以满足日常办公需要，拟更新2台电脑。",
            "更新后可更好支持文档编辑、表格统计及视频会议。",
        ):
            with self.subTest(text=text):
                self.assertEqual(prose_lint.scan("<test>", text, delivery_mode="draft-body"), [])

    def test_all_static_patterns_have_nonempty_advice(self) -> None:
        pattern_groups = [
            prose_lint.PATTERNS,
            prose_lint.FORMAT_PATTERNS,
            prose_lint.DELIVERY_PATTERNS,
            prose_lint.DRAFT_BODY_PATTERNS,
        ]

        for group in pattern_groups:
            for severity, label, pattern, advice in group:
                with self.subTest(label=label, pattern=pattern):
                    self.assertIn(severity, {"low", "medium", "high"})
                    self.assertTrue(label.strip())
                    self.assertTrue(pattern.strip())
                    self.assertTrue(advice.strip())


if __name__ == "__main__":
    unittest.main()
