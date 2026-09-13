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

    def test_unresolved_hint_advice_preserves_material_supported_state(self) -> None:
        for text in ("会议尚未形成决定。", "异常原因尚未形成正式结论。", "会议尚未形成具体安排。"):
            with self.subTest(text=text):
                findings = protective_findings(text)
                self.assertEqual(len(findings), 1)
                self.assertEqual(findings[0].label, "unresolved-conclusion-tail")
                self.assertEqual(findings[0].severity, "medium")
                self.assertIn("对照材料核对", findings[0].excerpt)
                self.assertIn("保留原状态", findings[0].excerpt)
                self.assertIn("仅清理与事项无关的重复自我限定", findings[0].excerpt)
                self.assertNotIn("可改为进行态", findings[0].excerpt)

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

    def test_review_and_lint_routes_preserve_evidence_bounded_semantic_choices(self) -> None:
        skill = (ROOT / "chinese-official-writing/SKILL.md").read_text(encoding="utf-8")
        review = (
            ROOT / "chinese-official-writing" / "references" / "writing-rules.md"
        ).read_text(encoding="utf-8")
        usage = (ROOT / "chinese-official-writing/references/prose-lint-usage.md").read_text(encoding="utf-8")

        self.assertIn("`references/writing-rules.md`", skill)
        self.assertIn("`prose-lint-usage.md`", review)
        # 核对迁移后的事实、范围与风险处理职责，不要求恢复旧复核页。
        for phrase in (
            "主体、对象、数字、金额、业务日期、引语、来源及事实状态照实保留",
            "主体、范围和判断强度与依据相称",
            "拟、建议、可选、进行中、待核和未决定按原程度表达",
            "已确认且属于本轮范围的问题交付前修正",
            "实质修改后核对关联内容并复扫，影响篇幅时另测字数",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, review)
        for phrase in (
            "对照风险位置、材料和修改范围修正问题",
            "合理用语及引用经核对可保留",
            "正文实质修改后复扫，最终采用已检查文本",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, usage)
        advice_by_label = {label: advice for _, label, _, advice in prose_lint.DRAFT_BODY_PATTERNS}
        self.assertTrue(LABELS.issubset(advice_by_label))
        self.assertIn("核对这是否为材料明确要求的证据或结论边界", advice_by_label["protective-negative-inference"])
        self.assertIn("保留原状态", advice_by_label["unresolved-conclusion-tail"])
        self.assertIn("核对这是否为必要的法律或决定边界", advice_by_label["negative-boundary-tail"])

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
