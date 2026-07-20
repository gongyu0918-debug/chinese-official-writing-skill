from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import threading
import time
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "chinese-official-writing" / "scripts" / "review_gate.py"


def load_module():
    spec = importlib.util.spec_from_file_location("review_gate_under_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


review_gate = load_module()


class ReviewGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = (
            "请写一份情况报告，控制在40—220字。材料：7月8日页面出现6次短时空白，"
            "13名用户反映无法登录，异常原因正在调查中。只输出正文。"
        )
        self.draft = (
            "政务服务登录页面异常情况报告\n\n"
            "7月8日，登录页面出现6次短时空白，13名用户反映无法登录，异常原因正在调查中。"
            "技术人员已记录发生时段、恢复情况和用户反馈，相关排查工作正在推进。"
            "尚不能据此直接推定异常已经根本解决。"
        )

    def detection(self, request=None, draft=None, source="", run_id="run-1"):
        detection = review_gate.locate_candidates(request or self.request, draft or self.draft, source)
        detection["run_id"] = run_id
        return detection

    def repair_packet(self, detection, repairs, repair_mode=None):
        packet = {
            "schema_version": 2,
            "run_id": detection["run_id"],
            "request_sha256": detection["request_sha256"],
            "source_sha256": detection["source_sha256"],
            "draft_sha256": detection["draft_sha256"],
            "revision_count": 1,
            "repairs": repairs,
        }
        if repair_mode is not None:
            packet["repair_mode"] = repair_mode
        return packet

    def deletion_packet(self, detection=None):
        detection = detection or self.detection()
        finding = detection["findings"][0]
        return self.repair_packet(
            detection,
            [{"finding_id": finding["finding_id"], "target": finding["target"], "replacement": ""}],
        )

    def begin_transaction(self, temp: Path, request=None, draft=None, source=None):
        request_path = temp / "request.txt"
        draft_path = temp / "draft.txt"
        request_path.write_text(request or self.request, encoding="utf-8")
        draft_path.write_text(draft or self.draft, encoding="utf-8")
        source_paths = []
        if source is not None:
            source_path = temp / "source.txt"
            source_path.write_text(source, encoding="utf-8")
            source_paths.append(source_path)
        txn = temp / "txn"
        state = review_gate.detect_transaction(request_path, draft_path, source_paths, txn, 180)
        return request_path, draft_path, txn, state

    def write_transaction_repair(
        self, temp: Path, txn: Path, replacements=None, repair_mode=None
    ):
        detection = json.loads((txn / "detection.json").read_text(encoding="utf-8"))
        if replacements is None:
            finding = detection["findings"][0]
            replacements = [
                {"finding_id": finding["finding_id"], "target": finding["target"], "replacement": ""}
            ]
        packet = self.repair_packet(detection, replacements, repair_mode)
        path = temp / "repairs.json"
        path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")
        return path

    def write_semantic_verdict(
        self, temp: Path, txn: Path, passed: bool = True, mutate=None
    ) -> Path:
        state = json.loads((txn / "state.json").read_text(encoding="utf-8"))
        checks = {key: True for key in review_gate.SEMANTIC_CHECKS}
        if not passed:
            checks[review_gate.SEMANTIC_CHECKS[0]] = False
        verdict = {
            "schema_version": review_gate.SEMANTIC_VERDICT_SCHEMA_VERSION,
            "run_id": state["run_id"],
            "request_sha256": state["request_sha256"],
            "source_sha256": state["source_sha256"],
            "draft_sha256": state["d0_sha256"],
            "candidate_sha256": state["d1_sha256"],
            "verdict": "PASS" if passed else "FAIL",
            "checks": checks,
        }
        if mutate is not None:
            mutate(verdict)
        path = temp / "semantic-verdict.json"
        path.write_text(json.dumps(verdict, ensure_ascii=False), encoding="utf-8")
        return path

    def guided_case(self) -> tuple[str, str, str]:
        target = "这项补充仅用于说明边界。"
        fallback = (
            "情况报告\n\n"
            "本次核查覆盖运行时段、处置过程和恢复情况，相关数据均已逐项核对。"
            "现场处置和后续复查情况已按时间顺序记录。"
            f"{target}"
        )
        raw = fallback.replace(
            target,
            f"{review_gate.GUIDED_MARKER_OPEN}{target}{review_gate.GUIDED_MARKER_CLOSE}",
        )
        return target, fallback, raw

    def guided_delete_response(self, packet: dict) -> dict:
        repairs = []
        for finding in packet["findings"]:
            guided = finding.get("guided_marker") is True
            repairs.append(
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "decision": (
                        review_gate.DECISION_DELETE
                        if guided
                        else review_gate.DECISION_KEEP
                    ),
                    "replacement": "" if guided else finding["target"],
                }
            )
        return {
            "schema_version": review_gate.SCHEMA_VERSION,
            "run_id": packet["run_id"],
            "request_sha256": packet["request_sha256"],
            "source_sha256": packet["source_sha256"],
            "draft_sha256": packet["draft_sha256"],
            "guided_marker_sha256": packet["guided_marker_sha256"],
            "revision_count": 1,
            "repair_mode": review_gate.REPAIR_MODE_DECISIONS,
            "repairs": repairs,
        }

    def semantic_pass_response(self, packet: dict) -> dict:
        return {
            "schema_version": review_gate.SEMANTIC_VERDICT_SCHEMA_VERSION,
            "run_id": packet["run_id"],
            "request_sha256": packet["request_sha256"],
            "source_sha256": packet["source_sha256"],
            "draft_sha256": packet["draft_sha256"],
            "candidate_sha256": packet["candidate_sha256"],
            "guided_marker_sha256": packet["guided_marker_sha256"],
            "verdict": "PASS",
            "checks": {key: True for key in packet["required_checks"]},
        }

    def test_locator_covers_common_protective_families(self) -> None:
        draft = "\n".join(
            [
                "尚不能据此直接推定全年使用规律。",
                "不将请求量变化直接写成已经确认的原因。",
                "支出和预算不与账号数量混用。",
                "本次请示不涉及确定供应商。",
                "设备是否需要整体更换尚未形成结论。",
                "现有材料仅能确认已经完成一次检查。",
                "采购方式尚未确定，施工窗口仍未明确。",
            ]
        )
        labels = {
            label
            for item in review_gate.locate_candidates("请写报告。", draft)["findings"]
            for label in item["labels"]
        }
        self.assertTrue(
            {
                "inference-disclaimer",
                "writing-self-certification",
                "scope-self-certification",
                "questioned-unresolved",
                "material-reading-narration",
                "peripheral-pending-cluster",
            }.issubset(labels)
        )

    def test_heading_classifier_distinguishes_numbered_sentences(self) -> None:
        self.assertTrue(review_gate._is_heading_line("一、运行情况"))
        self.assertTrue(review_gate._is_heading_line("4. 后续安排"))
        self.assertTrue(review_gate._is_heading_line("四、尚未决定和尚未确定事项"))
        self.assertFalse(review_gate._is_heading_line("1. 申报材料未提供原件且已补正。"))
        self.assertFalse(review_gate._is_heading_line("2. 工程进度滞后的具体原因正在核查。"))

    def test_locator_covers_archived_bare_material_meta_narration(self) -> None:
        samples = (
            "2. 伤员救治进展：材料仅载明伤员已送市人民医院救治，如需在通报中更新伤情和救治情况，请补充。",
            "2. 工程进度滞后的具体原因：材料未提供，正文原因分析部分暂保留待核查口径。",
            "1. 进度滞后的原因分析材料未提供（影响“分析原因”要求落实），建议补充后完善本报告。",
            "注：成文日期材料中未提供，正式报送前需补充。",
        )
        for draft in samples:
            with self.subTest(draft=draft):
                findings = review_gate.locate_candidates("请按现有材料成稿。", draft)["findings"]
                self.assertEqual(len(findings), 1)
                self.assertEqual(findings[0]["labels"], ["material-reading-narration"])

    def test_locator_does_not_flag_numbered_business_material_status(self) -> None:
        samples = (
            "1. 申报材料未提供原件且已补正。",
            "2. 投标材料中未提供分项报价且已处理。",
            "3. 有关材料仅载明设备型号且已归档。",
            "4. 会议材料未提供给参会单位且已补发。",
        )
        for draft in samples:
            with self.subTest(draft=draft):
                self.assertEqual(
                    review_gate.locate_candidates("请写情况报告。", draft)["findings"],
                    [],
                )

    def test_numbered_meta_sentence_rewrite_keeps_heading_structure(self) -> None:
        request = "请写一份情况报告，控制在40—220字。"
        draft = (
            "工程建设进展情况报告\n\n"
            "截至7月10日，项目总体进度为45%，有关进展已按小区分别统计。\n\n"
            "补充以下信息后，文章会更完整：\n\n"
            "2. 工程进度滞后的具体原因：材料未提供，正文原因分析部分暂保留待核查口径。"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        replacement = "2. 工程进度滞后的具体原因正在进一步核查分析。"
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": replacement,
                }
            ],
            review_gate.REPAIR_MODE_REWRITE_SENTENCE,
        )
        result = review_gate.evaluate_candidate(
            request,
            "",
            draft,
            detection["run_id"],
            detection,
            packet,
        )
        self.assertEqual(
            (result.selected, result.reason),
            ("D1", "verified_single_sentence_rewrite"),
        )
        self.assertNotIn("材料未提供", result.text)
        self.assertEqual(review_gate._headings(draft), review_gate._headings(result.text))

    def test_numbered_sentence_extract_keeps_heading_structure(self) -> None:
        request = "请写一份情况报告，控制在40—220字。"
        draft = (
            "运行核查情况报告\n\n"
            "本次共核查15项事项，相关状态已逐项登记，后续核查工作正在推进。\n\n"
            "1. 运行情况已作记录，不将该记录表述为全部完成。"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        replacement = "1. 运行情况已作记录。"
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": replacement,
                }
            ],
            review_gate.REPAIR_MODE_EXTRACT,
        )
        result = review_gate.evaluate_candidate(
            request,
            "",
            draft,
            detection["run_id"],
            detection,
            packet,
        )
        self.assertEqual(
            (result.selected, result.reason),
            ("D1", "verified_single_extractive_revision"),
        )
        self.assertEqual(review_gate._headings(draft), review_gate._headings(result.text))

    def test_numbered_sentence_rewrite_preserves_exact_list_marker(self) -> None:
        request = "请写一份情况报告，控制在40—220字。"
        body = (
            "截至7月10日，项目总体进度为45%，已完成事项和正在推进事项均按小区分别统计，"
            "有关责任单位继续核查施工安排并跟踪现场进度。"
        )
        cases = (
            ("二、", "三、", "D0", "list_marker_changed"),
            ("二、", "二、", "D1", "verified_single_sentence_rewrite"),
            ("（二）", "（三）", "D0", "list_marker_changed"),
            ("（二）", "（二）", "D1", "verified_single_sentence_rewrite"),
        )
        for original_marker, replacement_marker, selected, reason in cases:
            with self.subTest(
                original_marker=original_marker,
                replacement_marker=replacement_marker,
            ):
                target = (
                    f"{original_marker}材料未提供，正文原因分析部分暂保留待核查口径。"
                )
                draft = f"工程建设进展情况报告\n\n{body}\n\n{target}"
                detection = self.detection(request, draft)
                finding = detection["findings"][0]
                replacement = f"{replacement_marker}有关原因正在进一步核查。"
                packet = self.repair_packet(
                    detection,
                    [
                        {
                            "finding_id": finding["finding_id"],
                            "target": finding["target"],
                            "replacement": replacement,
                        }
                    ],
                    review_gate.REPAIR_MODE_REWRITE_SENTENCE,
                )
                result = review_gate.evaluate_candidate(
                    request,
                    "",
                    draft,
                    detection["run_id"],
                    detection,
                    packet,
                )
                self.assertEqual((result.selected, result.reason), (selected, reason))

    def test_sentence_counter_ignores_only_leading_number_marker(self) -> None:
        self.assertFalse(review_gate._replacement_adds_sentence("2. 工程进度正在核查。"))
        self.assertTrue(
            review_gate._replacement_adds_sentence("2. 工程进度正在核查。后续另行报告。")
        )
        self.assertTrue(review_gate._replacement_adds_sentence("情况正在核查。后续另行报告。"))

    def test_locator_does_not_flag_single_business_pending_state(self) -> None:
        draft = "三次离线的共同原因尚未形成结论。施工窗口尚未确定。"
        findings = review_gate.locate_candidates("请写会议纪要。", draft)["findings"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["target"], "三次离线的共同原因尚未形成结论。")
        self.assertEqual(findings[0]["labels"], ["unanchored-unresolved-conclusion"])

    def test_locator_routes_common_unanchored_tail_families(self) -> None:
        draft = "\n".join(
            (
                "本次会议未对维护措施的长期效果作出结论。",
                "具体设备调整方案、责任分工和新增采购安排尚未确定。",
                "目前工程仍在持续推进中，未发生停工、弃建等情况。",
                "下一步整改措施、责任分工和完成时限尚未确定，后续需补充。",
            )
        )
        findings = review_gate.locate_candidates("请按现有材料写报告。", draft)["findings"]
        self.assertEqual(
            [(item["target"], item["labels"]) for item in findings],
            [
                (
                    "本次会议未对维护措施的长期效果作出结论。",
                    ["scope-self-certification"],
                ),
                (
                    "具体设备调整方案、责任分工和新增采购安排尚未确定。",
                    ["multi-object-pending-tail"],
                ),
                (
                    "目前工程仍在持续推进中，未发生停工、弃建等情况。",
                    ["unsupported-negative-claim"],
                ),
                (
                    "下一步整改措施、责任分工和完成时限尚未确定，后续需补充。",
                    ["gap-state-narration", "multi-object-pending-tail"],
                ),
            ],
        )

    def test_locator_keeps_natural_process_states_quiet(self) -> None:
        samples = (
            "事故原因正在调查中。",
            "1个门禁感应点尚未完成处理，目前正在进行远程诊断。",
            "另有2个账号仍处于归属待核实状态。",
            "施工窗口尚未确定。",
        )
        for draft in samples:
            with self.subTest(draft=draft):
                self.assertEqual(
                    review_gate.locate_candidates("请按现有材料写报告。", draft)["findings"],
                    [],
                )

    def test_archived_calibration_task_recall_and_clean_false_positive_rate(self) -> None:
        p0_samples = {
            "P-B1": (
                "工程进度滞后的具体原因尚待进一步核查分析，目前尚未形成正式结论。\n"
                "2. 工程进度滞后的具体原因：材料未提供，正文原因分析部分暂保留待核查口径。"
            ),
            "P-B2": (
                "目前尚未形成工程进度滞后原因的正式结论，具体原因有待进一步核查分析。\n"
                "下一步整改措施、责任分工和完成时限尚未确定，后续需补充。"
            ),
            "P-A2": (
                "2. 伤员救治进展：材料仅载明伤员已送市人民医院救治，"
                "如需在通报中更新伤情和救治情况，请补充。"
            ),
            "P-C1": "目前，故障原因正在组织排查，尚未形成正式结论。",
            "P-C2": "目前，故障原因正在组织排查，尚未形成正式结论。",
            "P-CN": (
                "目前，故障原因正在组织排查，尚未形成结论。\n"
                "注：成文日期材料中未提供，正式报送前需补充。"
            ),
            "P-BN": "目前工程仍在持续推进中，未发生停工、弃建等情况。",
            "P-AE": (
                "2. 伤员救治进展：材料仅载明伤员已送市人民医院救治，"
                "如需在通报中更新伤情和救治情况，请补充。"
            ),
            "P-BE": (
                "1. 进度滞后的原因分析材料未提供（影响分析原因要求落实），"
                "建议补充后完善本报告。"
            ),
        }
        clean_samples = {
            "C-A1": "目前，事故原因正在调查中，善后工作正在有序开展。",
            "C-AN": "目前，事故原因正在调查中，善后工作正在有序开展。",
            "C-CE": "目前，故障原因正在组织排查，我局将跟进排查进展。",
            "C-CR": "目前，故障原因正在组织排查。待原因查明后，我局将及时报告有关情况。",
            "C-AR": "目前，事故原因正在调查中，善后工作正在有序开展。",
        }

        p0_hits = {
            name: bool(review_gate.locate_candidates("请按现有材料成稿。", draft)["findings"])
            for name, draft in p0_samples.items()
        }
        clean_hits = {
            name: bool(review_gate.locate_candidates("请按现有材料成稿。", draft)["findings"])
            for name, draft in clean_samples.items()
        }
        self.assertEqual(sum(p0_hits.values()), 9)
        self.assertEqual(sum(clean_hits.values()), 0)

    def test_locator_deduplicates_multi_label_sentence_and_skips_heading(self) -> None:
        draft = (
            "会议纪要\n\n"
            "四、尚未决定和尚未确定事项\n\n"
            "现有材料仅能确认反馈数量，因此不将反馈事项表述为已经全部解决。"
        )
        findings = review_gate.locate_candidates("请写会议纪要。", draft)["findings"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(
            findings[0]["labels"],
            ["material-reading-narration", "writing-self-certification"],
        )

    def test_locator_finds_common_material_narration_family(self) -> None:
        draft = (
            "设备运行情况报告\n\n"
            "除上述反映外，材料未反映其他设备运行情况。"
            "对失败请求，材料已明确为页面缓存未及时更新。"
            "处理情况以材料记载为准。"
            "上述情况在本报告中据实反映，不作超出试运行记录的分析和判断。"
        )

        findings = review_gate.locate_candidates("请写设备运行情况报告。", draft)["findings"]

        self.assertEqual(len(findings), 4)
        self.assertEqual(
            [item["labels"] for item in findings],
            [
                ["material-reading-narration"],
                ["material-reading-narration"],
                ["material-reading-narration"],
                ["writing-self-certification"],
            ],
        )

    def test_locator_keeps_legitimate_business_material_references_clean(self) -> None:
        draft = (
            "各单位应于7月20日前报送验收材料。"
            "归档材料应与业务系统现行字段保持一致。"
            "会议明确由业务处汇总申请材料，信息中心复核技术参数。"
            "检查组已完成现场核验，相关材料同步归档。"
            "材料已明确申报主体为项目单位。"
            "资料仅记载设备型号和数量。"
            "以材料载明内容为准。"
        )

        findings = review_gate.locate_candidates("请写工作通知。", draft)["findings"]

        self.assertFalse(findings)

    def test_locator_merges_ordinary_and_guided_same_span_once(self) -> None:
        target = "尚不能据此直接推定全年使用规律。"
        draft = f"情况报告\n\n{target}"
        marked = draft.replace(
            target,
            f"{review_gate.GUIDED_MARKER_OPEN}{target}{review_gate.GUIDED_MARKER_CLOSE}",
        )
        guided, verified = review_gate._bind_postdraft_marker_pass(draft, marked)

        self.assertTrue(verified)
        detection = review_gate.locate_candidates(
            "请写情况报告。",
            draft,
            guided_marker_sidecar=guided.sidecar(),
        )

        self.assertEqual(len(detection["findings"]), 1)
        finding = detection["findings"][0]
        self.assertEqual(finding["finding_id"], "G001")
        self.assertTrue(finding["guided_marker"])
        self.assertEqual(finding["marker_id"], "G001")
        self.assertEqual(
            finding["labels"],
            ["guided-drop-marker", "inference-disclaimer"],
        )

    def test_locator_counts_guided_overlap_once_against_budget(self) -> None:
        sentences = [f"第{index}项原因尚未形成结论。" for index in range(1, 13)]
        draft = "情况报告\n\n" + "".join(sentences)
        marked = draft.replace(
            sentences[0],
            f"{review_gate.GUIDED_MARKER_OPEN}{sentences[0]}"
            f"{review_gate.GUIDED_MARKER_CLOSE}",
            1,
        )
        guided, verified = review_gate._bind_postdraft_marker_pass(draft, marked)

        self.assertTrue(verified)
        detection = review_gate.locate_candidates(
            "请写情况报告。",
            draft,
            guided_marker_sidecar=guided.sidecar(),
        )

        self.assertEqual(len(detection["findings"]), review_gate.MAX_FINDINGS)
        self.assertEqual(
            sum(item.get("guided_marker") is True for item in detection["findings"]),
            1,
        )

    def test_exact_explicit_source_sentence_is_read_only(self) -> None:
        sentence = "尚不能据此直接推定全年使用规律。"
        detection = review_gate.locate_candidates("请写报告。", sentence, sentence)
        self.assertTrue(detection["findings"][0]["source_exact"])
        self.assertFalse(detection["findings"][0]["request_exact"])

    def test_request_control_text_is_not_treated_as_source_fact(self) -> None:
        sentence = "尚不能据此直接推定全年使用规律。"
        detection = review_gate.locate_candidates(
            f"请删除这句话：{sentence}", sentence, ""
        )

        self.assertFalse(detection["findings"][0]["source_exact"])
        self.assertTrue(detection["findings"][0]["request_exact"])

    def test_request_text_cannot_license_settled_status_in_repair(self) -> None:
        target = "事项尚未形成结论。"
        replacement = "事项已完成。"
        request = f"请把原句改成：{replacement}"
        draft = f"情况报告\n\n{target}"
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": replacement,
                }
            ],
            review_gate.REPAIR_MODE_REWRITE_SENTENCE,
        )

        result = review_gate.evaluate_candidate(
            request, "", draft, detection["run_id"], detection, packet
        )

        self.assertEqual((result.selected, result.reason), ("D0", "replacement_strengthens_status"))

    def test_valid_sentence_deletion_selects_d1(self) -> None:
        detection = self.detection()
        result = review_gate.evaluate_candidate(
            self.request, "", self.draft, "run-1", detection, self.deletion_packet(detection)
        )
        self.assertEqual(result.selected, "D1")
        self.assertNotIn("尚不能据此直接推定", result.text)

    def test_valid_extractive_clause_selects_d1(self) -> None:
        draft = (
            "事项核验情况报告\n\n"
            "本次核验覆盖15个事项，相关情况已按事项逐项记录。"
            "各事项主管部门正在核对线上线下表述差异。"
            "15个线上线下办理渠道表述不一致问题还有4个待确认，尚不能将未确认内容作为系统更新依据。"
        )
        request = "请写40—220字报告。"
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        replacement = "15个线上线下办理渠道表述不一致问题还有4个待确认。"
        packet = self.repair_packet(
            detection,
            [{"finding_id": finding["finding_id"], "target": finding["target"], "replacement": replacement}],
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D1")
        self.assertIn(replacement, result.text)

    def test_bounded_decision_packet_handles_all_findings_in_one_revision(self) -> None:
        request = (
            "请写一份80—500字会议纪要。材料明确："
            "本次会议未对维护措施的长期效果作出结论。"
        )
        draft = (
            "设备运行专题会议纪要\n\n"
            "会议听取了设备运行、维护记录和后续工作安排汇报，"
            "已完成事项、正在推进事项及有关责任主体均按材料逐项记录。"
            "目前，故障原因正在调查中，尚未形成正式结论。"
            "具体设备调整方案、责任分工和新增采购安排尚未确定。"
            "本次会议未对维护措施的长期效果作出结论。"
        )
        detection = self.detection(request, draft)
        self.assertEqual(len(detection["findings"]), 3)
        repairs = [
            {
                "finding_id": detection["findings"][0]["finding_id"],
                "target": detection["findings"][0]["target"],
                "decision": "REWRITE",
                "replacement": "目前，故障原因正在调查中。",
            },
            {
                "finding_id": detection["findings"][1]["finding_id"],
                "target": detection["findings"][1]["target"],
                "decision": "REWRITE",
                "replacement": "相关事项正在研究中。",
            },
            {
                "finding_id": detection["findings"][2]["finding_id"],
                "target": detection["findings"][2]["target"],
                "decision": "KEEP",
                "replacement": detection["findings"][2]["target"],
            },
        ]
        packet = self.repair_packet(detection, repairs, review_gate.REPAIR_MODE_DECISIONS)
        result = review_gate.evaluate_candidate(
            request, "", draft, detection["run_id"], detection, packet
        )
        self.assertEqual(
            (result.selected, result.reason),
            ("D1", "verified_bounded_decision_packet"),
        )
        self.assertIn("故障原因正在调查中。", result.text)
        self.assertIn("相关事项正在研究中。", result.text)
        self.assertIn("本次会议未对维护措施的长期效果作出结论。", result.text)

    def test_bounded_decisions_cannot_swap_hard_anchors_across_findings(self) -> None:
        request = "请写一份情况报告。"
        draft = (
            "情况报告\n\n"
            "甲事项于7月8日完成记录，尚不能据此直接推定运行稳定。"
            "乙事项涉及13名用户，尚不能据此直接推定影响范围。"
        )
        detection = self.detection(request, draft)
        self.assertEqual(len(detection["findings"]), 2)
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": detection["findings"][0]["finding_id"],
                    "target": detection["findings"][0]["target"],
                    "decision": review_gate.DECISION_REWRITE,
                    "replacement": "甲事项涉及13名用户，相关情况正在核查中。",
                },
                {
                    "finding_id": detection["findings"][1]["finding_id"],
                    "target": detection["findings"][1]["target"],
                    "decision": review_gate.DECISION_REWRITE,
                    "replacement": "乙事项于7月8日完成记录，相关情况正在核查中。",
                },
            ],
            review_gate.REPAIR_MODE_DECISIONS,
        )

        result = review_gate.evaluate_candidate(
            request, "", draft, "run-1", detection, packet
        )

        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "repair_item_hard_anchor_changed")
        self.assertEqual(result.text, draft)

    def test_bounded_decision_packet_requires_one_decision_per_finding(self) -> None:
        request = "请写40—300字报告。"
        draft = (
            "情况报告\n\n"
            "目前，故障原因正在调查中，尚未形成正式结论。"
            "具体设备调整方案、责任分工和新增采购安排尚未确定。"
        )
        detection = self.detection(request, draft)
        first = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": first["finding_id"],
                    "target": first["target"],
                    "decision": "REWRITE",
                    "replacement": "目前，故障原因正在调查中。",
                }
            ],
            review_gate.REPAIR_MODE_DECISIONS,
        )
        result = review_gate.evaluate_candidate(
            request, "", draft, detection["run_id"], detection, packet
        )
        self.assertEqual((result.selected, result.reason), ("D0", "decision_packet_incomplete"))

    def test_bounded_decision_packet_rejects_more_than_twelve_findings(self) -> None:
        request = "请写100—1000字报告。"
        draft = "情况报告\n\n" + "".join(
            f"第{index}项原因尚未形成结论。" for index in range(1, 14)
        )
        detection = self.detection(request, draft)
        self.assertEqual(len(detection["findings"]), 13)
        repairs = [
            {
                "finding_id": finding["finding_id"],
                "target": finding["target"],
                "decision": "KEEP",
                "replacement": finding["target"],
            }
            for finding in detection["findings"]
        ]
        packet = self.repair_packet(detection, repairs, review_gate.REPAIR_MODE_DECISIONS)
        result = review_gate.evaluate_candidate(
            request, "", draft, detection["run_id"], detection, packet
        )
        self.assertEqual((result.selected, result.reason), ("D0", "finding_budget_exceeded"))

    def test_detect_transaction_terminalizes_d0_above_finding_budget(self) -> None:
        draft = "情况报告\n\n" + "".join(
            f"第{index}项原因尚未形成结论。" for index in range(1, 14)
        )
        with tempfile.TemporaryDirectory() as raw:
            temp = Path(raw)
            _, _, txn, state = self.begin_transaction(
                temp, request="请写情况报告。", draft=draft
            )

            self.assertEqual(
                (state["state"], state["selected"], state["reason"]),
                (review_gate.STATE_TERMINAL_D0, "D0", "finding_budget_exceeded"),
            )
            self.assertEqual(state["repair_count"], 0)
            self.assertNotEqual(state["state"], review_gate.STATE_AWAITING_REPAIR)
            self.assertEqual((txn / review_gate.D0_FILE).read_text(encoding="utf-8"), draft)

    def test_bounded_decision_packet_only_allows_keep_for_source_exact_finding(self) -> None:
        sentence = "本次会议未对维护措施的长期效果作出结论。"
        request = "请写会议纪要。"
        draft = f"会议纪要\n\n{sentence}"
        detection = self.detection(request, draft, sentence)
        finding = detection["findings"][0]
        self.assertTrue(finding["source_exact"])
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "decision": "REWRITE",
                    "replacement": "相关事项正在研究中。",
                }
            ],
            review_gate.REPAIR_MODE_DECISIONS,
        )
        result = review_gate.evaluate_candidate(
            request, sentence, draft, detection["run_id"], detection, packet
        )
        self.assertEqual(
            (result.selected, result.reason),
            ("D0", "source_explicit_sentence_is_read_only"),
        )

    def test_extractive_prefix_keeps_existing_meeting_decision(self) -> None:
        request = "请整理一份简短会议纪要。"
        target = "会议决定继续开展测试，尚不能据此确定上线时间。"
        replacement = "会议决定继续开展测试。"
        draft = (
            "专题会议纪要\n\n"
            "会议听取了现阶段测试记录和问题清单汇总情况。"
            "有关单位分别报告了现有测试环境的运行情况。"
            f"{target}"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": replacement,
                }
            ],
        )

        result = review_gate.evaluate_candidate(
            request, "", draft, "run-1", detection, packet
        )

        self.assertEqual(result.selected, "D1")
        self.assertEqual(result.reason, "verified_single_extractive_revision")
        self.assertIn(replacement, result.text)

    def test_non_extractive_rewrite_falls_back(self) -> None:
        detection = self.detection()
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": "相关情况将结合调查结果继续跟进。",
                }
            ],
        )
        result = review_gate.evaluate_candidate(self.request, "", self.draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "replacement_not_safe_prefix")

    def test_explicit_sentence_rewrite_preserves_unresolved_state(self) -> None:
        request = "请写一份简短情况报告。"
        target = "目前只能确认清洗后告警次数减少，尚不能据此确定长期效果。"
        replacement = "清洗后告警次数减少，长期效果仍待观察。"
        draft = f"情况报告\n\n清洗和冷媒检查已经完成。{target}"
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": replacement,
                }
            ],
            review_gate.REPAIR_MODE_REWRITE_SENTENCE,
        )

        result = review_gate.evaluate_candidate(
            request, "", draft, "run-1", detection, packet
        )

        self.assertEqual(result.selected, "D1")
        self.assertEqual(result.reason, "verified_single_sentence_rewrite")
        self.assertIn(replacement, result.text)

    def test_sentence_rewrite_cannot_turn_unresolved_purchase_into_decision(self) -> None:
        request = "请写一份简短情况报告。"
        target = "是否采购50台设备尚未形成结论。"
        draft = (
            "情况报告\n\n"
            "现有设备运行状态已经完成登记，资产台账和现场记录均已整理。"
            f"{target}"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        for replacement in (
            "已经决定采购50台设备。",
            "决定采购50台设备。",
            "确定采购50台设备。",
            "同意采购50台设备。",
            "批准采购50台设备。",
            "实施采购50台设备。",
        ):
            with self.subTest(replacement=replacement):
                packet = self.repair_packet(
                    detection,
                    [
                        {
                            "finding_id": finding["finding_id"],
                            "target": finding["target"],
                            "replacement": replacement,
                        }
                    ],
                    review_gate.REPAIR_MODE_REWRITE_SENTENCE,
                )
                result = review_gate.evaluate_candidate(
                    request, "", draft, "run-1", detection, packet
                )
                self.assertEqual(result.selected, "D0")
                self.assertEqual(result.reason, "replacement_strengthens_status")

    def test_sentence_rewrite_allows_version_dots_in_one_sentence(self) -> None:
        request = "请写一份简短情况报告。"
        target = "设备版本为v1.2.3，目前尚不能据此确定长期效果。"
        replacement = "设备版本为v1.2.3，长期效果仍待观察。"
        draft = f"情况报告\n\n设备升级记录已经归档。{target}"
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": replacement,
                }
            ],
            review_gate.REPAIR_MODE_REWRITE_SENTENCE,
        )

        result = review_gate.evaluate_candidate(
            request, "", draft, "run-1", detection, packet
        )

        self.assertEqual(result.selected, "D1")
        self.assertIn(replacement, result.text)

    def test_sentence_rewrite_preserves_hard_anchor_values(self) -> None:
        request = "请写一份简短情况报告。"
        target = (
            "特别是前两次由重启恢复，第三次随网络恢复自行恢复，"
            "已有事实只能说明每次恢复过程，不能说明三次离线具有相同成因。"
        )
        safe_replacement = "三次离线中，前两次由重启恢复，第三次随网络恢复自行恢复。"
        unsafe_replacement = "前两次由重启恢复，第三次随网络恢复自行恢复。"
        draft = (
            "情况报告\n\n"
            "设备离线情况均已记录，现场恢复时间和恢复方式已分别列入运行台账。"
            "各点位继续按照原有安排开展试运行。"
            "运行记录同时保留每次恢复的时间、方式和当前状态，便于后续复核。"
            f"{target}"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]

        for replacement in (safe_replacement, unsafe_replacement):
            with self.subTest(replacement=replacement):
                packet = self.repair_packet(
                    detection,
                    [
                        {
                            "finding_id": finding["finding_id"],
                            "target": finding["target"],
                            "replacement": replacement,
                        }
                    ],
                    review_gate.REPAIR_MODE_REWRITE_SENTENCE,
                )
                result = review_gate.evaluate_candidate(
                    request, "", draft, "run-1", detection, packet
                )
                self.assertEqual(result.selected, "D1")

    def test_sentence_rewrite_mode_accepts_only_one_nonempty_repair(self) -> None:
        request = "请写一份简短情况报告。"
        draft = (
            "情况报告\n\n"
            "目前只能确认清洗后告警次数减少，尚不能据此确定长期效果。"
            "由于两份报价范围不同，目前尚不能直接比较。"
        )
        detection = self.detection(request, draft)
        repairs = [
            {
                "finding_id": finding["finding_id"],
                "target": finding["target"],
                "replacement": "长期效果仍待观察。",
            }
            for finding in detection["findings"]
        ]
        packet = self.repair_packet(
            detection, repairs, review_gate.REPAIR_MODE_REWRITE_SENTENCE
        )
        result = review_gate.evaluate_candidate(
            request, "", draft, "run-1", detection, packet
        )
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "sentence_rewrite_budget_violation")

        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": "",
                }
            ],
            review_gate.REPAIR_MODE_REWRITE_SENTENCE,
        )
        result = review_gate.evaluate_candidate(
            request, "", draft, "run-1", detection, packet
        )
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "sentence_rewrite_must_be_nonempty")

    def test_sentence_rewrite_rejects_all_recognized_line_separators(self) -> None:
        request = "请写一份简短情况报告。"
        target = "目前只能确认清洗后告警次数减少，尚不能据此确定长期效果。"
        draft = f"情况报告\n\n清洗和冷媒检查已经完成。{target}"
        detection = self.detection(request, draft)
        finding = detection["findings"][0]

        for separator in (
            "\n",
            "\r",
            "\r\n",
            "\v",
            "\f",
            "\x1c",
            "\x1d",
            "\x1e",
            "\x85",
            "\u2028",
            "\u2029",
        ):
            with self.subTest(separator=ascii(separator)):
                packet = self.repair_packet(
                    detection,
                    [
                        {
                            "finding_id": finding["finding_id"],
                            "target": finding["target"],
                            "replacement": f"清洗后告警次数减少，{separator}长期效果仍待观察。",
                        }
                    ],
                    review_gate.REPAIR_MODE_REWRITE_SENTENCE,
                )
                result = review_gate.evaluate_candidate(
                    request, "", draft, "run-1", detection, packet
                )
                self.assertEqual(result.selected, "D0")
                self.assertEqual(result.reason, "replacement_crosses_paragraph_boundary")

    def test_sentence_rewrite_rejects_ascii_sentence_boundaries(self) -> None:
        request = "请写一份简短情况报告。"
        target = "目前只能确认清洗后告警次数减少，尚不能据此确定长期效果。"
        draft = f"情况报告\n\n清洗和冷媒检查已经完成。{target}"
        detection = self.detection(request, draft)
        finding = detection["findings"][0]

        for separator in (".", "!", "?"):
            with self.subTest(separator=separator):
                replacement = f"清洗后告警次数减少{separator}长期效果仍待观察{separator}"
                packet = self.repair_packet(
                    detection,
                    [
                        {
                            "finding_id": finding["finding_id"],
                            "target": finding["target"],
                            "replacement": replacement,
                        }
                    ],
                    review_gate.REPAIR_MODE_REWRITE_SENTENCE,
                )
                result = review_gate.evaluate_candidate(
                    request, "", draft, "run-1", detection, packet
                )
                self.assertEqual(result.selected, "D0")
                self.assertEqual(result.reason, "replacement_adds_sentences")

    def test_sentence_rewrite_uses_actual_nonspace_length(self) -> None:
        request = "请写一份简短情况报告。"
        target = "目前只能确认清洗后告警次数减少，尚不能据此确定长期效果。"
        draft = f"情况报告\n\n清洗和冷媒检查已经完成。{target}"
        detection = self.detection(request, draft)
        finding = detection["findings"][0]

        for replacement in (
            "告警次数减少，长期效果仍待观察" + "🙂" * 40 + "。",
            "告警次数减少" + "，" * 40 + "长期效果仍待观察。",
        ):
            with self.subTest(replacement=replacement):
                packet = self.repair_packet(
                    detection,
                    [
                        {
                            "finding_id": finding["finding_id"],
                            "target": finding["target"],
                            "replacement": replacement,
                        }
                    ],
                    review_gate.REPAIR_MODE_REWRITE_SENTENCE,
                )
                result = review_gate.evaluate_candidate(
                    request, "", draft, "run-1", detection, packet
                )
                self.assertEqual(result.selected, "D0")
                self.assertEqual(result.reason, "body_content_collapsed")

        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": "   ",
                }
            ],
            review_gate.REPAIR_MODE_REWRITE_SENTENCE,
        )
        result = review_gate.evaluate_candidate(
            request, "", draft, "run-1", detection, packet
        )
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "sentence_rewrite_must_be_nonempty")

    def test_sentence_rewrite_allows_bounded_net_expansion_with_hard_anchors(self) -> None:
        request = "请写一个约260—340字的情况报告自然段，保留所有数字和未决状态。"
        target = "截至12时，异常原因、实际影响总量、4个服务事项各自受影响次数和后续处置方案均未形成结论。"
        replacement = "截至12时，异常原因正在调查，实际影响总量及4个服务事项各自受影响次数正在统计，后续处置方案正在研究。"
        draft = (
            "接口在两次重启后恢复，随后仍记录到短时超时。"
            "客服渠道收到21名用户反映，现场处置情况已经逐项记录。"
            f"{target}"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": replacement,
                }
            ],
            review_gate.REPAIR_MODE_REWRITE_SENTENCE,
        )

        result = review_gate.evaluate_candidate(
            request, "", draft, "run-1", detection, packet
        )

        self.assertGreater(
            review_gate._count_length(replacement, "nonspace"),
            review_gate._count_length(target, "nonspace"),
        )
        self.assertEqual(result.selected, "D1")
        self.assertEqual(result.text, draft.replace(target, replacement))

    def test_titleless_single_paragraph_is_body_while_real_title_stays_protected(self) -> None:
        paragraph = (
            "截至12时，异常原因正在调查，实际影响总量和4个服务事项受影响次数"
            "正在统计，后续处置方案正在研究。"
        )
        quoted_paragraph = (
            "本次会议未形成上线决定，唐越指出：“先核实失败请求，再研究上线安排。”"
        )
        titled = f"预约服务接口异常情况报告\n\n{paragraph}"

        self.assertEqual(review_gate._headings(paragraph), [])
        self.assertGreater(review_gate._body_length(paragraph), 0)
        self.assertEqual(review_gate._headings(quoted_paragraph), [])
        self.assertGreater(review_gate._body_length(quoted_paragraph), 0)
        self.assertEqual(
            review_gate._headings(titled), ["预约服务接口异常情况报告"]
        )
        self.assertEqual(
            review_gate._body_length(titled), review_gate._body_length(paragraph)
        )

    def test_titleless_quoted_paragraph_can_be_rewritten_without_title_false_positive(self) -> None:
        request = "请将这段会议情况改得自然一些，只输出一个自然段。"
        target = "尚不能据此直接推定异常已经根本解决，唐越指出：“先核实运行情况，再研究后续安排。”"
        replacement = "异常是否根本解决仍待观察，唐越指出：“先核实运行情况，再研究后续安排。”"
        detection = self.detection(request, target)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": replacement,
                }
            ],
            review_gate.REPAIR_MODE_REWRITE_SENTENCE,
        )

        result = review_gate.evaluate_candidate(
            request, "", target, "run-1", detection, packet
        )

        self.assertEqual(
            (result.selected, result.reason),
            ("D1", "verified_single_sentence_rewrite"),
        )
        self.assertEqual(result.text, replacement)

    def test_sentence_rewrite_rejects_gross_net_expansion(self) -> None:
        request = "请写一份简短情况报告。"
        target = "目前只能确认清洗后告警次数减少，尚不能据此确定长期效果。"
        replacement = (
            "清洗后告警次数减少，长期效果仍待观察，"
            + "后续运行变化继续观察记录，" * 8
            + "相关情况持续跟踪。"
        )
        draft = (
            "情况报告\n\n"
            "前期已完成设备清洗、运行记录整理和告警情况汇总。"
            f"{target}"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": replacement,
                }
            ],
            review_gate.REPAIR_MODE_REWRITE_SENTENCE,
        )

        result = review_gate.evaluate_candidate(
            request, "", draft, "run-1", detection, packet
        )

        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "candidate_length_expansion_exceeded")

    def test_existing_length_violation_may_improve_without_becoming_compliant(self) -> None:
        target = "目前只能确认清洗后告警次数减少，尚不能据此确定长期效果。"
        replacement = "清洗后告警次数减少，长期效果仍待观察。"
        draft = (
            "情况报告\n\n"
            "前期已完成设备清洗、运行记录整理和告警情况汇总，相关记录已经归档。"
            "设备运行时段、现场温度和维护记录均按原有口径持续整理。"
            f"{target}"
        )
        candidate = draft.replace(target, replacement)
        draft_length = review_gate._count_length(draft, "nonspace")
        candidate_length = review_gate._count_length(candidate, "nonspace")
        self.assertLess(candidate_length, draft_length)
        maximum = candidate_length - 1
        request = f"请写一份1—{maximum}字的简短情况报告。"
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": replacement,
                }
            ],
            review_gate.REPAIR_MODE_REWRITE_SENTENCE,
        )

        result = review_gate.evaluate_candidate(
            request, "", draft, "run-1", detection, packet
        )

        self.assertEqual(result.selected, "D1")
        self.assertGreater(candidate_length, maximum)

    def test_sentence_rewrite_allows_minor_length_variance(self) -> None:
        target = "目前只能确认清洗后告警次数减少，尚不能据此确定长期效果。"
        replacement = "长期效果仍待观察。"
        draft = (
            "情况报告\n\n"
            "前期已完成设备清洗、运行记录整理和告警情况汇总，相关记录已经归档。"
            "清洗后设备继续保持运行，工作人员按日记录温度、负荷和告警次数。"
            f"{target}"
        )
        candidate = draft.replace(target, replacement)
        draft_length = review_gate._count_length(draft, "nonspace")
        candidate_length = review_gate._count_length(candidate, "nonspace")
        minimum = candidate_length + 1
        maximum = draft_length + 1
        request = f"请写一份{minimum}—{maximum}字的简短情况报告。"
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": replacement,
                }
            ],
            review_gate.REPAIR_MODE_REWRITE_SENTENCE,
        )

        result = review_gate.evaluate_candidate(
            request, "", draft, "run-1", detection, packet
        )

        self.assertEqual(result.selected, "D1")

    def test_sentence_rewrite_rejects_gross_length_worsening(self) -> None:
        target = (
            "目前只能确认清洗后告警次数减少，尚不能据此确定长期效果，"
            "也不能作为扩大设备数量、确定采购安排或者测算年度预算的依据。"
        )
        replacement = "长期效果仍待观察。"
        draft = "情况报告\n\n" + "设备运行记录已经完成归档。" * 20 + target
        candidate = draft.replace(target, replacement)
        draft_length = review_gate._count_length(draft, "nonspace")
        candidate_length = review_gate._count_length(candidate, "nonspace")
        request = f"请写一份{draft_length}—{draft_length + 20}字的简短情况报告。"
        self.assertGreater(
            draft_length - candidate_length,
            review_gate._length_worsening_tolerance(draft_length, draft_length, draft_length + 20),
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": replacement,
                }
            ],
            review_gate.REPAIR_MODE_REWRITE_SENTENCE,
        )

        result = review_gate.evaluate_candidate(
            request, "", draft, "run-1", detection, packet
        )

        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "prompt_length_compliance_worsened")

    def test_extracted_positive_status_falls_back(self) -> None:
        request = "请写一份简短情况报告。"
        draft = (
            "情况报告\n\n"
            "有关事项仍待确认，现将已掌握情况如实报告。"
            "本报告不将待确认事项表述为已经完成。"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [{"finding_id": finding["finding_id"], "target": finding["target"], "replacement": "已经完成。"}],
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "replacement_not_safe_prefix")

    def test_extraction_cannot_drop_general_negation(self) -> None:
        request = "请写一份简短情况报告。"
        draft = (
            "情况报告\n\n"
            "现场检查工作已经完成，有关情况已作记录。"
            "现有记录没有反映发生重大事故，也不能据此形成其他结论。"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [{"finding_id": finding["finding_id"], "target": finding["target"], "replacement": "发生重大事故。"}],
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "replacement_not_safe_prefix")

    def test_extraction_cannot_turn_unresolved_question_into_assertion(self) -> None:
        request = "请写一份简短情况报告。"
        draft = (
            "情况报告\n\n"
            "设备运行情况和后续安排已按现有记录整理。"
            "已提出采购50台设备的建议，是否采购50台设备尚未形成结论。"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": "已提出采购50台设备的建议。",
                }
            ],
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "replacement_not_safe_prefix")

    def test_unresolved_status_sentence_cannot_be_deleted(self) -> None:
        request = "请写一份简短情况报告。"
        draft = (
            "情况报告\n\n"
            "设备运行情况已按现有记录整理。"
            "是否需要整体更换设备尚未形成结论。"
        )
        detection = self.detection(request, draft)
        result = review_gate.evaluate_candidate(
            request, "", draft, "run-1", detection, self.deletion_packet(detection)
        )
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "full_deletion_not_proven_safe")

    def test_hard_anchor_change_falls_back(self) -> None:
        request = "请写一份简短情况报告。"
        draft = "情况报告\n\n前期工作已作记录。完成检查，尚不能将7月8日有关情况推定为全年结论。"
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [{"finding_id": finding["finding_id"], "target": finding["target"], "replacement": "完成检查。"}],
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "hard_anchor_change_not_redundant")

    def test_only_title_remaining_falls_back(self) -> None:
        request = "请写一份情况报告。"
        draft = "情况报告\n\n尚不能据此直接推定全年使用规律。"
        detection = self.detection(request, draft)
        result = review_gate.evaluate_candidate(
            request, "", draft, "run-1", detection, self.deletion_packet(detection)
        )
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "body_or_section_emptied")

    def test_source_explicit_target_cannot_be_changed(self) -> None:
        sentence = "尚不能据此直接推定全年使用规律。"
        request = "请写报告。"
        detection = self.detection(request, sentence, source=sentence)
        packet = self.deletion_packet(detection)
        result = review_gate.evaluate_candidate(request, sentence, sentence, "run-1", detection, packet)
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "source_explicit_sentence_is_read_only")

    def test_residual_protective_pattern_falls_back(self) -> None:
        request = "请写一份简短情况报告。"
        draft = (
            "情况报告\n\n"
            "有关情况已经按现有记录整理。"
            "不能据此直接推定异常已经根本解决，尚不能据此形成其他结论。"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": "不能据此直接推定异常已经根本解决。",
                }
            ],
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "replacement_retains_protective_pattern")

    def test_request_anchored_unresolved_status_can_be_retained(self) -> None:
        request = "异常原因、影响范围和后续处置均未形成结论。"
        draft = (
            "情况报告\n\n"
            "对于异常原因、影响范围和后续处置等事项，现阶段均未形成结论。"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "decision": review_gate.DECISION_REWRITE,
                    "replacement": "异常原因、影响范围和后续处置均未形成结论。",
                }
            ],
            review_gate.REPAIR_MODE_DECISIONS,
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D1")
        self.assertEqual(result.reason, "verified_bounded_decision_packet")

    def test_request_anchored_status_subset_can_be_retained(self) -> None:
        request = "异常原因、影响范围和后续处置均未形成结论。"
        draft = "情况报告\n\n后续处置事项亦尚未形成结论。"
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "decision": review_gate.DECISION_REWRITE,
                    "replacement": "后续处置尚未形成结论。",
                }
            ],
            review_gate.REPAIR_MODE_DECISIONS,
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D1")
        self.assertEqual(result.reason, "verified_bounded_decision_packet")

    def test_request_anchored_coordinated_status_subset_can_be_retained(self) -> None:
        request = "异常原因、影响范围和后续处置均未形成结论。"
        draft = "情况报告\n\n异常原因、影响范围及其他外围事项尚未形成结论。"
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "decision": review_gate.DECISION_REWRITE,
                    "replacement": "异常原因和影响范围尚未形成结论。",
                }
            ],
            review_gate.REPAIR_MODE_DECISIONS,
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D1")
        self.assertEqual(result.reason, "verified_bounded_decision_packet")

    def test_unanchored_coordinated_status_topic_is_rejected(self) -> None:
        request = "异常原因、影响范围和后续处置均未形成结论。"
        draft = "情况报告\n\n异常原因、采购安排及其他外围事项尚未形成结论。"
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "decision": review_gate.DECISION_REWRITE,
                    "replacement": "异常原因和采购安排尚未形成结论。",
                }
            ],
            review_gate.REPAIR_MODE_DECISIONS,
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "replacement_retains_protective_pattern")

    def test_fact_prefix_and_request_anchored_status_suffix_can_be_retained(self) -> None:
        request = (
            "技术人员于7月8日9时28分、9时47分先后重启；"
            "异常原因、影响范围和后续处置均未形成结论。"
        )
        draft = (
            "情况报告\n\n"
            "除7月8日9时28分、9时47分技术人员先后进行重启外，"
            "现有材料未形成关于异常原因、影响范围及后续处置的结论性意见。"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "decision": review_gate.DECISION_REWRITE,
                    "replacement": (
                        "技术人员于7月8日9时28分、9时47分先后重启；"
                        "异常原因、影响范围和后续处置均未形成结论。"
                    ),
                }
            ],
            review_gate.REPAIR_MODE_DECISIONS,
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D1")
        self.assertEqual(result.reason, "verified_bounded_decision_packet")

    def test_fact_prefix_does_not_authorize_unrelated_status_suffix(self) -> None:
        request = (
            "技术人员于7月8日9时28分、9时47分先后重启；"
            "异常原因、影响范围和后续处置均未形成结论。"
        )
        draft = (
            "情况报告\n\n"
            "除7月8日9时28分、9时47分技术人员先后进行重启外，"
            "现有材料未形成关于采购安排的结论性意见。"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "decision": review_gate.DECISION_REWRITE,
                    "replacement": (
                        "技术人员于7月8日9时28分、9时47分先后重启；"
                        "采购安排尚未形成结论。"
                    ),
                }
            ],
            review_gate.REPAIR_MODE_DECISIONS,
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "replacement_retains_protective_pattern")

    def test_request_modifier_can_qualify_an_anchored_status_topic(self) -> None:
        request = "异常原因、影响范围和后续处置均未形成结论。"
        draft = (
            "情况报告\n\n"
            "7月8日9时12分，登录页面出现间歇性空白。"
            "技术人员于9时28分、9时47分先后重启。"
            "实际影响人数和其他影响事项尚不能据此确定。"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "decision": review_gate.DECISION_REWRITE,
                    "replacement": "异常影响范围尚未形成结论。",
                }
            ],
            review_gate.REPAIR_MODE_DECISIONS,
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D1")
        self.assertEqual(result.reason, "verified_bounded_decision_packet")

    def test_unrelated_modifier_cannot_qualify_an_anchored_status_topic(self) -> None:
        request = "异常原因、影响范围和后续处置均未形成结论。"
        draft = (
            "情况报告\n\n"
            "7月8日9时12分，登录页面出现间歇性空白。"
            "技术人员于9时28分、9时47分先后重启。"
            "实际影响人数和其他影响事项尚不能据此确定。"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "decision": review_gate.DECISION_REWRITE,
                    "replacement": "采购影响范围尚未形成结论。",
                }
            ],
            review_gate.REPAIR_MODE_DECISIONS,
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "replacement_retains_protective_pattern")

    def test_different_request_status_does_not_authorize_replacement(self) -> None:
        request = "异常原因仍在调查中。"
        draft = "情况报告\n\n后续处置事项亦尚未形成结论。"
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "decision": review_gate.DECISION_REWRITE,
                    "replacement": "后续处置尚未形成结论。",
                }
            ],
            review_gate.REPAIR_MODE_DECISIONS,
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "replacement_retains_protective_pattern")

    def test_repeated_request_anchor_can_be_reduced_by_rewrite(self) -> None:
        request = "7月8日页面出现6次短时空白，请写情况报告。"
        draft = (
            "情况报告\n\n"
            "7月8日，页面出现6次短时空白。"
            "技术人员已记录发生时段，登录页面当前可以访问。"
            "7月8日页面出现6次异常，尚不能据此形成其他结论。"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "decision": review_gate.DECISION_REWRITE,
                    "replacement": "相关情况已作记录。",
                }
            ],
            review_gate.REPAIR_MODE_DECISIONS,
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D1")
        self.assertEqual(result.reason, "verified_bounded_decision_packet")

    def test_unique_request_anchor_cannot_be_removed_by_rewrite(self) -> None:
        request = "7月8日页面出现6次短时空白，请写情况报告。"
        draft = "情况报告\n\n7月8日页面出现6次异常，尚不能据此形成其他结论。"
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "decision": review_gate.DECISION_REWRITE,
                    "replacement": "相关情况已作记录。",
                }
            ],
            review_gate.REPAIR_MODE_DECISIONS,
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "hard_anchor_change_not_redundant")

    def test_bounded_p0_repair_may_shorten_draft_already_below_minimum(self) -> None:
        request = "请写一份100—180字的情况报告。"
        draft = (
            "情况报告\n\n"
            "现场检查情况已经完成记录，相关时间节点和处理状态均已纳入本次报告。"
            "检查对象、发现事项和当前状态已分别列明，正文结构保持完整。"
            "尚不能据此直接推定全年使用规律，也不能据此形成新增采购结论。"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "decision": review_gate.DECISION_REWRITE,
                    "replacement": "相关情况已作记录。",
                }
            ],
            review_gate.REPAIR_MODE_DECISIONS,
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D1")
        self.assertEqual(result.reason, "verified_bounded_decision_packet")

    def test_middle_substring_cannot_collapse_double_negation(self) -> None:
        request = "请写一份简短情况报告。"
        draft = "情况报告\n\n现场检查情况已作记录。现有材料不能说明没有问题。"
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [{"finding_id": finding["finding_id"], "target": finding["target"], "replacement": "没有问题。"}],
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "replacement_not_safe_prefix")

    def test_hypothesis_prefix_cannot_be_extracted_as_fact(self) -> None:
        request = "请写一份简短情况报告。"
        draft = "情况报告\n\n当前运行情况已作记录。即使设备恢复，也不足以说明问题已经解决。"
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": "即使设备恢复。",
                }
            ],
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "replacement_not_safe_prefix")

    def test_safe_prefix_cannot_drop_business_fact_before_protective_tail(self) -> None:
        request = "请写一份简短情况报告。"
        draft = (
            "情况报告\n\n"
            "设备运行情况已作记录。"
            "主设备运行正常，另一设备仍处于诊断阶段，尚不能据此形成整体结论。"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": "主设备运行正常。",
                }
            ],
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "replacement_not_safe_prefix")

    def test_short_business_fact_prefix_cannot_be_deleted_with_tail(self) -> None:
        request = "请写一份简短情况报告。"
        draft = "情况报告\n\n相关工作正在推进。设备已恢复，但尚不能据此认定长期稳定。"
        detection = self.detection(request, draft)
        result = review_gate.evaluate_candidate(
            request, "", draft, "run-1", detection, self.deletion_packet(detection)
        )
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "full_deletion_not_proven_safe")

    def test_protective_start_cannot_hide_later_business_fact_in_full_deletion(self) -> None:
        request = "请写一份简短情况报告。"
        source = "检查工作已完成。"
        draft = (
            "情况报告\n\n"
            "设备运行情况已作记录。"
            "尚不能据此认定设备运行长期稳定，但现场检查工作已经完成。"
        )
        detection = self.detection(request, draft, source=source)
        result = review_gate.evaluate_candidate(
            request, source, draft, "run-1", detection, self.deletion_packet(detection)
        )
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "full_deletion_not_proven_safe")

    def test_if_clause_cannot_be_selected_as_complete_business_prefix(self) -> None:
        request = "请写一份简短情况报告。"
        draft = "情况报告\n\n当前运行情况已作记录。如果设备恢复，也不能据此认定运行已经稳定。"
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": "如果设备恢复。",
                }
            ],
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "replacement_not_safe_prefix")

    def test_material_reading_sentence_with_unique_fact_cannot_be_deleted(self) -> None:
        request = "请写一份简短情况报告。"
        source = "检查工作已完成。"
        draft = "情况报告\n\n后续安排正在推进。现有材料仅能确认现场检查已经结束。"
        detection = self.detection(request, draft, source=source)
        result = review_gate.evaluate_candidate(
            request, source, draft, "run-1", detection, self.deletion_packet(detection)
        )
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "full_deletion_not_proven_safe")

    def test_material_reading_tail_with_unique_fact_cannot_be_prefix_deleted(self) -> None:
        request = "请写一份简短情况报告。"
        source = "检查工作已完成。"
        draft = (
            "情况报告\n\n"
            "有关情况已作记录。"
            "设备运行情况已记录，现有材料仅能确认现场检查已经结束。"
        )
        detection = self.detection(request, draft, source=source)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": "设备运行情况已记录。",
                }
            ],
        )
        result = review_gate.evaluate_candidate(request, source, draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "replacement_not_safe_prefix")

    def test_prefix_cannot_drop_second_unresolved_business_question(self) -> None:
        request = "请写一份简短情况报告。"
        draft = (
            "情况报告\n\n"
            "设备运行状态已作记录。"
            "主设备是否恢复仍待核实，是否停用备用设备尚未形成结论，尚不能据此形成总体判断。"
        )
        detection = self.detection(request, draft)
        finding = detection["findings"][0]
        packet = self.repair_packet(
            detection,
            [
                {
                    "finding_id": finding["finding_id"],
                    "target": finding["target"],
                    "replacement": "主设备是否恢复仍待核实。",
                }
            ],
        )
        result = review_gate.evaluate_candidate(request, "", draft, "run-1", detection, packet)
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "replacement_not_safe_prefix")

    def test_mixed_business_fact_and_protective_tail_cannot_be_fully_deleted(self) -> None:
        request = "请写一份简短情况报告。"
        draft = (
            "情况报告\n\n"
            "有关情况已作记录。"
            "7月8日完成现场检查，尚不能据此直接推定全年使用规律。"
        )
        detection = self.detection(request, draft)
        result = review_gate.evaluate_candidate(
            request, "", draft, "run-1", detection, self.deletion_packet(detection)
        )
        self.assertEqual(result.selected, "D0")
        self.assertEqual(result.reason, "full_deletion_not_proven_safe")

    def test_no_finding_transaction_is_terminal_d0(self) -> None:
        clean = "情况报告\n\n7月8日完成检查，异常原因正在调查中。"
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, state = self.begin_transaction(temp, draft=clean)
            self.assertEqual(state["state"], "TERMINAL_D0")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                text = review_gate.emit_transaction(txn)
            self.assertEqual(text, clean)
            self.assertEqual(stdout.getvalue(), clean)

    def test_dispatch_runs_one_repair_one_verdict_and_emits_d1_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            txn = temp / "txn"
            request_path.write_text(self.request, encoding="utf-8")
            draft_path.write_text(self.draft, encoding="utf-8")

            def bridge(_command, phase, packet_path, _timeout):
                packet = json.loads(packet_path.read_text(encoding="utf-8"))
                if phase == "repair":
                    self.assertEqual(
                        packet["response_schema_version"], review_gate.SCHEMA_VERSION
                    )
                    self.assertEqual(packet["response_revision_count"], 1)
                    self.assertEqual(
                        packet["response_repair_mode"], review_gate.REPAIR_MODE_DECISIONS
                    )
                    finding = packet["findings"][0]
                    return {
                        "schema_version": review_gate.SCHEMA_VERSION,
                        "run_id": packet["run_id"],
                        "request_sha256": packet["request_sha256"],
                        "source_sha256": packet["source_sha256"],
                        "draft_sha256": packet["draft_sha256"],
                        "revision_count": 1,
                        "repair_mode": review_gate.REPAIR_MODE_DECISIONS,
                        "repairs": [
                            {
                                "finding_id": finding["finding_id"],
                                "target": finding["target"],
                                "decision": review_gate.DECISION_DELETE,
                                "replacement": "",
                            }
                        ],
                    }
                return {
                    "schema_version": review_gate.SEMANTIC_VERDICT_SCHEMA_VERSION,
                    "run_id": packet["run_id"],
                    "request_sha256": packet["request_sha256"],
                    "source_sha256": packet["source_sha256"],
                    "draft_sha256": packet["draft_sha256"],
                    "candidate_sha256": packet["candidate_sha256"],
                    "verdict": "PASS",
                    "checks": {key: True for key in packet["required_checks"]},
                }

            stdout = io.StringIO()
            with mock.patch.object(review_gate, "_run_bridge", side_effect=bridge) as runner:
                with redirect_stdout(stdout):
                    result = review_gate.dispatch_transaction(
                        request_path, draft_path, [], txn, ["host-bridge"], 180, 180
                    )

            expected = self.draft.replace("尚不能据此直接推定异常已经根本解决。", "")
            state = json.loads((txn / review_gate.STATE_FILE).read_text(encoding="utf-8"))
            self.assertEqual(result, expected)
            self.assertEqual(stdout.getvalue(), expected)
            self.assertEqual(runner.call_count, 2)
            self.assertEqual(
                (state["state"], state["selected"]),
                (review_gate.STATE_TERMINAL_D1, "D1"),
            )
            self.assertEqual(state["repair_agent_call_count"], 1)
            self.assertEqual(state["verdict_agent_call_count"], 1)

            marked_path = temp / "marked.txt"
            marked_path.write_text(self.draft, encoding="utf-8")
            reentry_stdout = io.StringIO()
            with mock.patch.object(review_gate, "_run_bridge", side_effect=bridge) as reentry_runner:
                with redirect_stdout(reentry_stdout):
                    reentry = review_gate.dispatch_transaction(
                        request_path,
                        draft_path,
                        [],
                        txn,
                        ["host-bridge"],
                        180,
                        180,
                        marked_path,
                    )
            self.assertEqual(reentry, self.draft)
            self.assertEqual(reentry_stdout.getvalue(), self.draft)
            self.assertEqual(reentry_runner.call_count, 0)

    def test_dispatch_missing_postdraft_review_emits_complete_original_d0(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            missing_marked_path = temp / "missing-marked.txt"
            txn = temp / "txn"
            request_path.write_text(self.request, encoding="utf-8")
            draft_path.write_text(self.draft, encoding="utf-8")

            stdout = io.StringIO()
            with mock.patch.object(review_gate, "_run_bridge") as runner:
                with redirect_stdout(stdout):
                    result = review_gate.dispatch_transaction(
                        request_path,
                        draft_path,
                        [],
                        txn,
                        ["host-bridge"],
                        180,
                        180,
                        missing_marked_path,
                    )

            self.assertEqual(result, self.draft)
            self.assertEqual(stdout.getvalue(), self.draft)
            self.assertEqual(runner.call_count, 0)

    def test_guided_marker_parser_preserves_duplicate_inner_text_and_spans(self) -> None:
        tail = "尚不能据此形成其他结论。"
        raw = (
            "情况报告\n\n"
            f"第一项事实已经记录。{review_gate.GUIDED_MARKER_OPEN}{tail}"
            f"{review_gate.GUIDED_MARKER_CLOSE}\n"
            f"第二项事实已经记录。{review_gate.GUIDED_MARKER_OPEN}{tail}"
            f"{review_gate.GUIDED_MARKER_CLOSE}"
        )

        parsed = review_gate._parse_guided_draft(raw)

        self.assertEqual(parsed.parse_status, "VALID")
        self.assertEqual(len(parsed.markers), 2)
        self.assertEqual(parsed.fallback_d0.count(tail), 2)
        self.assertFalse(review_gate._has_guided_marker_token(parsed.fallback_d0))
        for marker in parsed.markers:
            self.assertEqual(
                parsed.fallback_d0[marker.span_start : marker.span_end], tail
            )

    def test_guided_marker_parser_invalid_forms_only_strip_tokens(self) -> None:
        cases = {
            "unclosed": f"事实。{review_gate.GUIDED_MARKER_OPEN}尾巴。",
            "orphan_close": f"事实。尾巴。{review_gate.GUIDED_MARKER_CLOSE}",
            "nested": (
                f"事实。{review_gate.GUIDED_MARKER_OPEN}甲"
                f"{review_gate.GUIDED_MARKER_OPEN}乙{review_gate.GUIDED_MARKER_CLOSE}"
                f"{review_gate.GUIDED_MARKER_CLOSE}"
            ),
            "empty": (
                f"事实。{review_gate.GUIDED_MARKER_OPEN}"
                f"{review_gate.GUIDED_MARKER_CLOSE}"
            ),
            "cross_paragraph": (
                f"事实。{review_gate.GUIDED_MARKER_OPEN}甲\n乙。"
                f"{review_gate.GUIDED_MARKER_CLOSE}"
            ),
        }
        for name, raw in cases.items():
            with self.subTest(name=name):
                parsed = review_gate._parse_guided_draft(raw)
                self.assertEqual(parsed.parse_status, "INVALID")
                self.assertEqual(
                    parsed.fallback_d0,
                    review_gate._strip_guided_marker_tokens(raw),
                )
                self.assertFalse(
                    review_gate._has_guided_marker_token(parsed.fallback_d0)
                )

    def test_dispatch_deletes_valid_guided_marker_only_after_semantic_pass(self) -> None:
        target = "尚不能据此直接推定异常已经根本解决。"
        raw = self.draft.replace(
            target,
            f"{review_gate.GUIDED_MARKER_OPEN}{target}{review_gate.GUIDED_MARKER_CLOSE}",
        )
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            txn = temp / "txn"
            request_path.write_text(self.request, encoding="utf-8")
            draft_path.write_text(raw, encoding="utf-8")

            phases: list[str] = []

            def bridge(_command, phase, packet_path, _timeout):
                phases.append(phase)
                packet = json.loads(packet_path.read_text(encoding="utf-8"))
                if phase == "repair":
                    repairs = []
                    for finding in packet["findings"]:
                        guided = finding.get("guided_marker") is True
                        repairs.append(
                            {
                                "finding_id": finding["finding_id"],
                                "target": finding["target"],
                                "decision": (
                                    review_gate.DECISION_DELETE
                                    if guided
                                    else review_gate.DECISION_KEEP
                                ),
                                "replacement": "" if guided else finding["target"],
                            }
                        )
                    return {
                        "schema_version": review_gate.SCHEMA_VERSION,
                        "run_id": packet["run_id"],
                        "request_sha256": packet["request_sha256"],
                        "source_sha256": packet["source_sha256"],
                        "draft_sha256": packet["draft_sha256"],
                        "guided_marker_sha256": packet["guided_marker_sha256"],
                        "revision_count": 1,
                        "repair_mode": review_gate.REPAIR_MODE_DECISIONS,
                        "repairs": repairs,
                    }
                return {
                    "schema_version": review_gate.SEMANTIC_VERDICT_SCHEMA_VERSION,
                    "run_id": packet["run_id"],
                    "request_sha256": packet["request_sha256"],
                    "source_sha256": packet["source_sha256"],
                    "draft_sha256": packet["draft_sha256"],
                    "candidate_sha256": packet["candidate_sha256"],
                    "guided_marker_sha256": packet["guided_marker_sha256"],
                    "verdict": "PASS",
                    "checks": {key: True for key in packet["required_checks"]},
                }

            stdout = io.StringIO()
            with mock.patch.object(review_gate, "_run_bridge", side_effect=bridge):
                with redirect_stdout(stdout):
                    result = review_gate.dispatch_transaction(
                        request_path, draft_path, [], txn, ["host-bridge"], 180, 180
                    )

            state = json.loads((txn / review_gate.STATE_FILE).read_text(encoding="utf-8"))
            sidecar = json.loads(
                (txn / review_gate.GUIDED_MARKER_FILE).read_text(encoding="utf-8")
            )
            expected = self.draft.replace(target, "")
            self.assertEqual(result, expected)
            self.assertEqual(stdout.getvalue(), expected)
            self.assertEqual(state["selected"], "D1")
            self.assertEqual(state["guided_marker_count"], 1)
            self.assertEqual(sidecar["parse_status"], "VALID")
            self.assertEqual(sidecar["markers"][0]["target"], target)
            self.assertEqual(phases, ["repair", "verify"])

    def test_dispatch_invalid_guided_marker_preserves_inner_text_and_emits_no_token(self) -> None:
        target = "尚不能据此直接推定异常已经根本解决。"
        raw = self.draft.replace(target, f"{review_gate.GUIDED_MARKER_OPEN}{target}")
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            txn = temp / "txn"
            request_path.write_text(self.request, encoding="utf-8")
            draft_path.write_text(raw, encoding="utf-8")

            stdout = io.StringIO()
            with mock.patch.object(
                review_gate, "_run_bridge", side_effect=AssertionError("bridge must not run")
            ):
                with redirect_stdout(stdout):
                    result = review_gate.dispatch_transaction(
                        request_path, draft_path, [], txn, ["host-bridge"], 180, 180
                    )

            state = json.loads((txn / review_gate.STATE_FILE).read_text(encoding="utf-8"))
            self.assertEqual(result, self.draft)
            self.assertEqual(stdout.getvalue(), self.draft)
            self.assertEqual(state["reason"], "guided_marker_parse_invalid")
            self.assertFalse(review_gate._has_guided_marker_token(result))

    def test_dispatch_strips_noncanonical_guided_marker_variants(self) -> None:
        cases = {
            "space_before_bracket": (
                "情况报告\n\n事实。⟦OWG-DROP ⟧尾句。⟦/OWG-DROP ⟧",
                "情况报告\n\n事实。尾句。",
            ),
            "lowercase": (
                "情况报告\n\n事实。⟦owg-drop⟧尾句。⟦/owg-drop⟧",
                "情况报告\n\n事实。尾句。",
            ),
            "fullwidth_space": (
                "情况报告\n\n事实。⟦OWG-DROP　⟧尾句。⟦/OWG-DROP　⟧",
                "情况报告\n\n事实。尾句。",
            ),
            "line_break_inside_token": (
                "情况报告\n\n事实。⟦OWG-\nDROP⟧尾句。⟦/OWG-\r\nDROP⟧",
                "情况报告\n\n事实。尾句。",
            ),
            "unclosed_preserves_inner_line_break": (
                "情况报告\n\n事实。⟦OWG-DROP\n尾句。",
                "情况报告\n\n事实。\n尾句。",
            ),
            "unbracketed_preserves_surrounding_blank_lines": (
                "段一。\n\nOWG-DROP尾句。/OWG-DROP\n\n段二。",
                "段一。\n\n尾句。\n\n段二。",
            ),
            "unclosed_fragment": (
                "情况报告\n\n事实。⟦OWG-DROP尾句。",
                "情况报告\n\n事实。尾句。",
            ),
        }
        for name, (raw, expected) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                temp = Path(directory)
                request_path = temp / "request.txt"
                draft_path = temp / "draft.txt"
                txn = temp / "txn"
                request_path.write_text("请写情况报告，只输出正文。", encoding="utf-8")
                draft_path.write_text(raw, encoding="utf-8")

                stdout = io.StringIO()
                with mock.patch.object(
                    review_gate, "_run_bridge", side_effect=AssertionError("bridge must not run")
                ):
                    with redirect_stdout(stdout):
                        result = review_gate.dispatch_transaction(
                            request_path, draft_path, [], txn, ["host-bridge"], 180, 180
                        )

                state = json.loads(
                    (txn / review_gate.STATE_FILE).read_text(encoding="utf-8")
                )
                self.assertEqual(result, expected)
                self.assertEqual(stdout.getvalue(), expected)
                self.assertFalse(review_gate._has_guided_marker_token(result))
                self.assertEqual(state["reason"], "guided_marker_parse_invalid")

    def test_guided_marker_keep_and_semantic_fail_both_preserve_inner_text(self) -> None:
        target = "这项补充仅用于说明边界。"
        fallback = (
            "情况报告\n\n"
            "主要事实已经记录，涉及运行时段、处置过程、恢复情况和用户反馈，"
            f"相关数据均已逐项核对。{target}"
        )
        raw = fallback.replace(
            target,
            f"{review_gate.GUIDED_MARKER_OPEN}{target}{review_gate.GUIDED_MARKER_CLOSE}",
        )
        for decision, semantic_pass, expected_phases in (
            (review_gate.DECISION_KEEP, True, ["repair"]),
            (review_gate.DECISION_DELETE, False, ["repair", "verify"]),
        ):
            with self.subTest(decision=decision, semantic_pass=semantic_pass):
                with tempfile.TemporaryDirectory() as directory:
                    temp = Path(directory)
                    request_path = temp / "request.txt"
                    draft_path = temp / "draft.txt"
                    txn = temp / "txn"
                    request_path.write_text("请写情况报告，只输出正文。", encoding="utf-8")
                    draft_path.write_text(raw, encoding="utf-8")
                    phases: list[str] = []

                    def bridge(_command, phase, packet_path, _timeout):
                        phases.append(phase)
                        packet = json.loads(packet_path.read_text(encoding="utf-8"))
                        if phase == "repair":
                            finding = packet["findings"][0]
                            return {
                                "schema_version": review_gate.SCHEMA_VERSION,
                                "run_id": packet["run_id"],
                                "request_sha256": packet["request_sha256"],
                                "source_sha256": packet["source_sha256"],
                                "draft_sha256": packet["draft_sha256"],
                                "guided_marker_sha256": packet["guided_marker_sha256"],
                                "revision_count": 1,
                                "repair_mode": review_gate.REPAIR_MODE_DECISIONS,
                                "repairs": [
                                    {
                                        "finding_id": finding["finding_id"],
                                        "target": finding["target"],
                                        "decision": decision,
                                        "replacement": (
                                            finding["target"]
                                            if decision == review_gate.DECISION_KEEP
                                            else ""
                                        ),
                                    }
                                ],
                            }
                        checks = {key: True for key in review_gate.SEMANTIC_CHECKS}
                        checks["guided_marker_scope_safe"] = semantic_pass
                        return {
                            "schema_version": review_gate.SEMANTIC_VERDICT_SCHEMA_VERSION,
                            "run_id": packet["run_id"],
                            "request_sha256": packet["request_sha256"],
                            "source_sha256": packet["source_sha256"],
                            "draft_sha256": packet["draft_sha256"],
                            "candidate_sha256": packet["candidate_sha256"],
                            "guided_marker_sha256": packet["guided_marker_sha256"],
                            "verdict": "PASS" if semantic_pass else "FAIL",
                            "checks": checks,
                        }

                    stdout = io.StringIO()
                    with mock.patch.object(review_gate, "_run_bridge", side_effect=bridge):
                        with redirect_stdout(stdout):
                            result = review_gate.dispatch_transaction(
                                request_path,
                                draft_path,
                                [],
                                txn,
                                ["host-bridge"],
                                180,
                                180,
                            )

                    self.assertEqual(result, fallback)
                    self.assertEqual(stdout.getvalue(), fallback)
                    self.assertEqual(phases, expected_phases)
                    self.assertFalse(review_gate._has_guided_marker_token(result))

    def test_guided_duplicate_targets_are_deleted_by_span(self) -> None:
        target = "这项补充仅用于说明边界。"
        raw = (
            "情况报告\n\n"
            "本次核查覆盖运行时段、处置过程和恢复情况，相关数据均已逐项核对。\n"
            f"第一项事实及对应状态已经记录。{review_gate.GUIDED_MARKER_OPEN}{target}"
            f"{review_gate.GUIDED_MARKER_CLOSE}\n"
            f"第二项事实及对应状态已经记录。{review_gate.GUIDED_MARKER_OPEN}{target}"
            f"{review_gate.GUIDED_MARKER_CLOSE}"
        )
        expected = (
            "情况报告\n\n"
            "本次核查覆盖运行时段、处置过程和恢复情况，相关数据均已逐项核对。\n"
            "第一项事实及对应状态已经记录。\n"
            "第二项事实及对应状态已经记录。"
        )
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            txn = temp / "txn"
            request_path.write_text("请写情况报告，只输出正文。", encoding="utf-8")
            draft_path.write_text(raw, encoding="utf-8")

            def bridge(_command, phase, packet_path, _timeout):
                packet = json.loads(packet_path.read_text(encoding="utf-8"))
                if phase == "repair":
                    return {
                        "schema_version": review_gate.SCHEMA_VERSION,
                        "run_id": packet["run_id"],
                        "request_sha256": packet["request_sha256"],
                        "source_sha256": packet["source_sha256"],
                        "draft_sha256": packet["draft_sha256"],
                        "guided_marker_sha256": packet["guided_marker_sha256"],
                        "revision_count": 1,
                        "repair_mode": review_gate.REPAIR_MODE_DECISIONS,
                        "repairs": [
                            {
                                "finding_id": finding["finding_id"],
                                "target": finding["target"],
                                "decision": review_gate.DECISION_DELETE,
                                "replacement": "",
                            }
                            for finding in packet["findings"]
                        ],
                    }
                return {
                    "schema_version": review_gate.SEMANTIC_VERDICT_SCHEMA_VERSION,
                    "run_id": packet["run_id"],
                    "request_sha256": packet["request_sha256"],
                    "source_sha256": packet["source_sha256"],
                    "draft_sha256": packet["draft_sha256"],
                    "candidate_sha256": packet["candidate_sha256"],
                    "guided_marker_sha256": packet["guided_marker_sha256"],
                    "verdict": "PASS",
                    "checks": {key: True for key in packet["required_checks"]},
                }

            with mock.patch.object(review_gate, "_run_bridge", side_effect=bridge):
                with redirect_stdout(io.StringIO()):
                    result = review_gate.dispatch_transaction(
                        request_path, draft_path, [], txn, ["host-bridge"], 180, 180
                    )

            self.assertEqual(result, expected)
            self.assertFalse(review_gate._has_guided_marker_token(result))

    def test_guided_source_exact_peripheral_tail_requires_semantic_pass(self) -> None:
        target = "本次会议未对维护措施的长期效果作出结论。"
        body = (
            "会议听取了设备运行、维护记录和告警变化情况，参会单位分别介绍了现场检查结果。"
            "会议讨论了维护措施，相关意见已作记录。"
        )
        fallback = f"会议纪要\n\n{body}{target}"
        raw = fallback.replace(
            target,
            f"{review_gate.GUIDED_MARKER_OPEN}{target}{review_gate.GUIDED_MARKER_CLOSE}",
        )
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            source_path = temp / "source.txt"
            txn = temp / "txn"
            request_path.write_text("按材料写会议纪要，只输出正文。", encoding="utf-8")
            draft_path.write_text(raw, encoding="utf-8")
            source_path.write_text(f"{body}{target}", encoding="utf-8")

            def bridge(_command, phase, packet_path, _timeout):
                packet = json.loads(packet_path.read_text(encoding="utf-8"))
                if phase == "repair":
                    return self.guided_delete_response(packet)
                return self.semantic_pass_response(packet)

            with mock.patch.object(review_gate, "_run_bridge", side_effect=bridge):
                with redirect_stdout(io.StringIO()):
                    result = review_gate.dispatch_transaction(
                        request_path,
                        draft_path,
                        [source_path],
                        txn,
                        ["host-bridge"],
                        180,
                        180,
                    )

            self.assertEqual(result, f"会议纪要\n\n{body}")

    def test_guided_delete_allows_authoritative_duplicate_structured_anchors(self) -> None:
        cases = (
            (
                "date-time-range",
                "7月16日9时至12时，中心复查18台终端，设备均在线运行。",
                "本次复查结果反映的是7月16日9时至12时的设备状态，"
                "不能据此推定后续运行期间不会再出现故障。",
                "材料：7月16日9时至12时复查18台终端，均在线运行。",
            ),
            (
                "cross-month-date-range",
                "7月31日至8月1日，中心完成设备复查并记录运行状态。",
                "7月31日至8月1日的记录不能据此推定后续不会出现故障。",
                "材料：7月31日至8月1日完成设备复查并记录运行状态。",
            ),
            (
                "chinese-quantity",
                "目前，三次离线的共同原因正在调查，三次恢复过程均已记录。",
                "现有记录还不足以将三次离线归为同一成因，"
                "也不能据此确定具体故障环节或责任主体。",
                "材料：共发生三次离线，三次恢复过程均已记录，共同原因正在调查。",
            ),
            (
                "spaced-number-unit-authority",
                "6月抽查120笔记录，其中113笔时间一致，7笔相差1—3分钟。",
                "本次抽查没有提供7笔时间差异的形成原因，"
                "也不能由120笔抽查记录推断全部业务记录的时间一致情况。",
                "材料：6月抽查 120 笔记录，其中 113 笔时间一致，"
                "7 笔相差 1—3 分钟。",
            ),
            (
                "repeated-expense-count",
                "设备租赁、网络和驻场服务三项试运行支出合计27.8万元。",
                "现有材料仅列三项支出合计，未列分项金额，"
                "不能据此比较各项支出规模。",
                "材料：设备租赁、网络和驻场服务三项试运行支出合计27.8万元。",
            ),
            (
                "unit-followed-by-an-object-name",
                "中心复查18台设备，相关运行状态均已记录。",
                "18台设备的记录不能据此推定后续不会出现故障。",
                "材料：中心复查18台设备，相关运行状态均已记录。",
            ),
            (
                "chinese-unit-followed-by-an-object-name",
                "中心复查三台设备，相关运行状态均已记录。",
                "三台设备的记录不能据此推定后续不会出现故障。",
                "材料：中心复查三台设备，相关运行状态均已记录。",
            ),
        )
        for name, body, target, request in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                temp = Path(directory)
                request_path = temp / "request.txt"
                draft_path = temp / "draft.txt"
                txn = temp / "txn"
                filler = (
                    "后续工作按既定安排推进，相关运行情况继续据实记录。"
                    "责任单位按原有分工做好日常巡检，形成的记录及时归档。"
                    "发现新的运行问题时，仍按现有处置流程跟进处理。"
                    "巡检记录包括检查对象、运行状态和处置情况，由有关人员逐项登记。"
                    "复查工作继续围绕既定范围开展，形成的结果与前期记录衔接保存。"
                )
                fallback = f"情况报告\n\n{body}{target}{filler}"
                raw = fallback.replace(
                    target,
                    f"{review_gate.GUIDED_MARKER_OPEN}{target}"
                    f"{review_gate.GUIDED_MARKER_CLOSE}",
                )
                request_path.write_text(request, encoding="utf-8")
                draft_path.write_text(raw, encoding="utf-8")

                def bridge(_command, phase, packet_path, _timeout):
                    packet = json.loads(packet_path.read_text(encoding="utf-8"))
                    if phase == "repair":
                        return self.guided_delete_response(packet)
                    return self.semantic_pass_response(packet)

                with mock.patch.object(review_gate, "_run_bridge", side_effect=bridge):
                    with redirect_stdout(io.StringIO()):
                        result = review_gate.dispatch_transaction(
                            request_path,
                            draft_path,
                            [],
                            txn,
                            ["host-bridge"],
                            180,
                            180,
                        )

                state = json.loads((txn / "state.json").read_text(encoding="utf-8"))
                self.assertEqual(result, fallback.replace(target, ""), state)
                self.assertEqual(state["selected"], "D1")
                self.assertEqual(state["verify_count"], 1)

    def test_guided_delete_does_not_use_unique_or_different_role_anchors(self) -> None:
        cases = (
            (
                "unique-date-time",
                "中心已经完成设备复查并记录运行状态。",
                "7月16日9时至12时的记录不能据此推定后续不会出现故障。",
                "材料：7月16日9时至12时完成设备复查。",
                None,
            ),
            (
                "same-digits-different-roles",
                "现场有7台设备、16项记录、9名工作人员和12次操作。",
                "7月16日9时至12时的记录不能据此推定后续不会出现故障。",
                "材料：现场有7台设备、16项记录、9名工作人员和12次操作；"
                "7月16日9时至12时完成复查。",
                None,
            ),
            (
                "quote-whitespace-is-significant",
                "会议记录原话为“AB”，相关内容已经归档。",
                "原话“A B”不能据此作为后续安排的依据。",
                "材料原话为“A B”，仅用于记录当时表述。",
                None,
            ),
            (
                "book-title-whitespace-is-significant",
                "会议研究了《AB》，相关内容已经归档。",
                "《A B》不能据此作为后续安排的依据。",
                "材料提到《A B》，仅用于记录当时议题。",
                None,
            ),
            (
                "cross-month-range-needs-the-whole-range",
                "7月31日完成设备检查，8月1日完成台账复核。",
                "7月31日至8月1日的记录不能据此推定后续不会出现故障。",
                "材料：7月31日完成设备检查，8月1日完成台账复核。",
                None,
            ),
            (
                "request-source-boundary-cannot-form-a-range",
                "9时至12时，中心完成设备复查并记录运行状态。",
                "9时至12时的记录不能据此推定后续不会出现故障。",
                "材料说明复查开始于9时",
                "至12时，中心完成设备复查并记录运行状态。",
            ),
            (
                "request-source-boundary-cannot-form-a-unit",
                "检查日期为7日，中心已经记录设备运行状态。",
                "7日的记录不能据此推定后续不会出现故障。",
                "材料说明检查日期为7",
                "日，中心已经记录设备运行状态。",
            ),
            (
                "unit-prefix-cannot-back-a-device-run-count",
                "中心已复查18台设备并记录运行状态。",
                "18台次巡检记录不能据此推定后续不会出现故障。",
                "材料：本轮巡检共计18台次。",
                None,
            ),
            (
                "unit-prefix-cannot-back-a-year-period",
                "项目已形成3年运行记录。",
                "3年期运行记录不能据此推定后续安排。",
                "材料：项目采用3年期运行观察口径。",
                None,
            ),
            (
                "unit-prefix-cannot-back-an-annual-label",
                "2026年已完成设备检查。",
                "2026年度记录不能据此推定后续安排。",
                "材料：2026年度记录已汇总。",
                None,
            ),
            (
                "unit-prefix-cannot-back-a-time-slot",
                "14时完成设备检查。",
                "14时段记录不能据此推定后续不会出现故障。",
                "材料：本次抽查覆盖14时段。",
                None,
            ),
            (
                "unit-prefix-cannot-back-a-working-day-period",
                "中心已形成3个事项清单。",
                "3个工作日记录不能据此推定后续安排。",
                "材料：本次观察期为3个工作日。",
                None,
            ),
            (
                "chinese-unit-prefix-cannot-back-a-device-run-count",
                "中心已复查三台设备并记录运行状态。",
                "三台次巡检记录不能据此推定后续不会出现故障。",
                "材料：本轮巡检共计三台次。",
                None,
            ),
            (
                "chinese-unit-prefix-cannot-back-a-year-period",
                "项目已形成三年运行记录。",
                "三年期运行记录不能据此推定后续安排。",
                "材料：项目采用三年期运行观察口径。",
                None,
            ),
            (
                "chinese-unit-prefix-cannot-back-an-annual-label",
                "二〇二六年已完成设备检查。",
                "二〇二六年度记录不能据此推定后续安排。",
                "材料：二〇二六年度记录已汇总。",
                None,
            ),
            (
                "chinese-unit-prefix-cannot-back-a-working-day-period",
                "中心已形成三个事项清单。",
                "三个工作日记录不能据此推定后续安排。",
                "材料：本次观察期为三个工作日。",
                None,
            ),
        )
        for name, body, target, request, source in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                temp = Path(directory)
                request_path = temp / "request.txt"
                draft_path = temp / "draft.txt"
                source_path = temp / "source.txt"
                txn = temp / "txn"
                filler = (
                    "后续工作按既定安排推进，相关运行情况继续据实记录。"
                    "责任单位按原有分工做好日常巡检，形成的记录及时归档。"
                    "发现新的运行问题时，仍按现有处置流程跟进处理。"
                    "巡检记录包括检查对象、运行状态和处置情况，由有关人员逐项登记。"
                    "复查工作继续围绕既定范围开展，形成的结果与前期记录衔接保存。"
                )
                fallback = f"情况报告\n\n{body}{target}{filler}"
                raw = fallback.replace(
                    target,
                    f"{review_gate.GUIDED_MARKER_OPEN}{target}"
                    f"{review_gate.GUIDED_MARKER_CLOSE}",
                )
                request_path.write_text(request, encoding="utf-8")
                draft_path.write_text(raw, encoding="utf-8")
                source_paths = []
                if source is not None:
                    source_path.write_text(source, encoding="utf-8")
                    source_paths.append(source_path)

                def bridge(_command, phase, packet_path, _timeout):
                    packet = json.loads(packet_path.read_text(encoding="utf-8"))
                    if phase == "repair":
                        return self.guided_delete_response(packet)
                    return self.semantic_pass_response(packet)

                with mock.patch.object(review_gate, "_run_bridge", side_effect=bridge):
                    with redirect_stdout(io.StringIO()):
                        result = review_gate.dispatch_transaction(
                            request_path,
                            draft_path,
                            source_paths,
                            txn,
                            ["host-bridge"],
                            180,
                            180,
                        )

                state = json.loads((txn / "state.json").read_text(encoding="utf-8"))
                self.assertEqual(result, fallback)
                self.assertEqual(state["selected"], "D0")
                self.assertEqual(state["verify_count"], 0)

    def test_structured_anchor_normalization_is_horizontal_and_type_scoped(self) -> None:
        def canonicals(text: str) -> set[str]:
            return {
                occurrence.canonical
                for occurrence in review_gate._structured_anchor_occurrences(text)
            }

        self.assertIn("7日", canonicals("7 日"))
        self.assertIn("120笔", canonicals("120 笔"))
        self.assertIn("7月16日", canonicals("7　月 16　日"))
        self.assertIn("7月13日至15日", canonicals("7 月 13 日至 15 日"))
        self.assertIn("4月1日至6月30日", canonicals("4月1日至6月30日"))
        self.assertIn(
            "2026年12月1日至2027年1月15日",
            canonicals("2026年12月1日至2027年1月15日"),
        )
        self.assertNotIn("7日", canonicals("7\n日"))
        self.assertNotIn("120笔", canonicals("120\n笔"))
        self.assertIn("“A B”", canonicals("“A B”"))
        self.assertIn("《A B》", canonicals("《A B》"))
        self.assertNotEqual(canonicals("“A B”"), canonicals("“AB”"))
        self.assertNotEqual(canonicals("《A B》"), canonicals("《AB》"))

    def test_guided_delete_cannot_use_deleted_or_concatenated_anchor(self) -> None:
        filler = (
            "后续工作按既定安排推进，相关运行情况继续据实记录。"
            "责任单位按原有分工做好日常巡检，形成的记录及时归档。"
            "发现新的运行问题时，仍按现有处置流程跟进处理。"
            "巡检记录包括检查对象、运行状态和处置情况，由有关人员逐项登记。"
            "复查工作继续围绕既定范围开展，形成的结果与前期记录衔接保存。"
        )
        marker_one = "三次离线不能据此推定具有相同成因。"
        marker_two = "三次恢复记录不能据此推定后续不会再次离线。"
        mutual_raw = (
            "情况报告\n\n"
            f"{review_gate.GUIDED_MARKER_OPEN}{marker_one}"
            f"{review_gate.GUIDED_MARKER_CLOSE}"
            f"{review_gate.GUIDED_MARKER_OPEN}{marker_two}"
            f"{review_gate.GUIDED_MARKER_CLOSE}{filler}"
        )
        concatenated_target = "7月16日不能据此推定后续不会再次出现故障。"
        concatenated_raw = (
            "情况报告\n\n设备复查记录为7"
            f"{review_gate.GUIDED_MARKER_OPEN}{concatenated_target}"
            f"{review_gate.GUIDED_MARKER_CLOSE}月16日形成。{filler}"
        )
        cases = (
            (
                "markers-cannot-back-each-other",
                mutual_raw,
                "材料：三次离线和三次恢复过程均已记录。",
            ),
            (
                "deletion-cannot-create-anchor-by-concatenation",
                concatenated_raw,
                "材料：7月16日完成设备复查。",
            ),
        )
        for name, raw, request in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                temp = Path(directory)
                request_path = temp / "request.txt"
                draft_path = temp / "draft.txt"
                txn = temp / "txn"
                request_path.write_text(request, encoding="utf-8")
                draft_path.write_text(raw, encoding="utf-8")

                def bridge(_command, phase, packet_path, _timeout):
                    packet = json.loads(packet_path.read_text(encoding="utf-8"))
                    if phase == "repair":
                        return self.guided_delete_response(packet)
                    return self.semantic_pass_response(packet)

                with mock.patch.object(review_gate, "_run_bridge", side_effect=bridge):
                    with redirect_stdout(io.StringIO()):
                        result = review_gate.dispatch_transaction(
                            request_path,
                            draft_path,
                            [],
                            txn,
                            ["host-bridge"],
                            180,
                            180,
                        )

                state = json.loads((txn / "state.json").read_text(encoding="utf-8"))
                self.assertEqual(state["selected"], "D0")
                self.assertEqual(state["verify_count"], 0)
                self.assertNotIn(review_gate.GUIDED_MARKER_OPEN, result)

    def test_guided_rewrite_keeps_core_state_and_removes_protective_tail(self) -> None:
        target = "事故原因尚不明确，这不代表现场处置已经解决全部问题。"
        replacement = "事故原因正在调查中。"
        body = (
            "事故发生后，现场人员完成服务重启并记录异常时段、恢复情况和用户反馈。"
            "技术人员正在排查故障原因，相关运行数据已汇总。"
        )
        fallback = f"事故情况报告\n\n{body}{target}"
        raw = fallback.replace(
            target,
            f"{review_gate.GUIDED_MARKER_OPEN}{target}{review_gate.GUIDED_MARKER_CLOSE}",
        )
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            source_path = temp / "source.txt"
            txn = temp / "txn"
            request_path.write_text("按材料写事故情况报告，只输出正文。", encoding="utf-8")
            draft_path.write_text(raw, encoding="utf-8")
            source_path.write_text(
                f"{body}事故原因尚不明确。", encoding="utf-8"
            )

            def bridge(_command, phase, packet_path, _timeout):
                packet = json.loads(packet_path.read_text(encoding="utf-8"))
                if phase == "repair":
                    repairs = []
                    for finding in packet["findings"]:
                        guided = finding.get("guided_marker") is True
                        repairs.append(
                            {
                                "finding_id": finding["finding_id"],
                                "target": finding["target"],
                                "decision": (
                                    review_gate.DECISION_REWRITE
                                    if guided
                                    else review_gate.DECISION_KEEP
                                ),
                                "replacement": replacement if guided else finding["target"],
                            }
                        )
                    return {
                        "schema_version": review_gate.SCHEMA_VERSION,
                        "run_id": packet["run_id"],
                        "request_sha256": packet["request_sha256"],
                        "source_sha256": packet["source_sha256"],
                        "draft_sha256": packet["draft_sha256"],
                        "guided_marker_sha256": packet["guided_marker_sha256"],
                        "revision_count": 1,
                        "repair_mode": review_gate.REPAIR_MODE_DECISIONS,
                        "repairs": repairs,
                    }
                return {
                    "schema_version": review_gate.SEMANTIC_VERDICT_SCHEMA_VERSION,
                    "run_id": packet["run_id"],
                    "request_sha256": packet["request_sha256"],
                    "source_sha256": packet["source_sha256"],
                    "draft_sha256": packet["draft_sha256"],
                    "candidate_sha256": packet["candidate_sha256"],
                    "guided_marker_sha256": packet["guided_marker_sha256"],
                    "verdict": "PASS",
                    "checks": {key: True for key in packet["required_checks"]},
                }

            with mock.patch.object(review_gate, "_run_bridge", side_effect=bridge):
                with redirect_stdout(io.StringIO()):
                    result = review_gate.dispatch_transaction(
                        request_path,
                        draft_path,
                        [source_path],
                        txn,
                        ["host-bridge"],
                        180,
                        180,
                    )

            self.assertEqual(result, f"事故情况报告\n\n{body}{replacement}")

    def test_guided_delete_cannot_remove_numbered_decision_anchor(self) -> None:
        target = "会议决定7月20日前完成整改。"
        body = (
            "会议听取了现场检查、设备运行和整改准备情况，参会单位分别报告了工作进展。"
            "有关责任分工和实施条件已在会上逐项核对。"
        )
        fallback = f"会议纪要\n\n{body}{target}"
        raw = fallback.replace(
            target,
            f"{review_gate.GUIDED_MARKER_OPEN}{target}{review_gate.GUIDED_MARKER_CLOSE}",
        )
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            txn = temp / "txn"
            request_path.write_text("写会议纪要，只输出正文。", encoding="utf-8")
            draft_path.write_text(raw, encoding="utf-8")

            def bridge(_command, phase, packet_path, _timeout):
                self.assertEqual(phase, "repair")
                packet = json.loads(packet_path.read_text(encoding="utf-8"))
                finding = packet["findings"][0]
                return {
                    "schema_version": review_gate.SCHEMA_VERSION,
                    "run_id": packet["run_id"],
                    "request_sha256": packet["request_sha256"],
                    "source_sha256": packet["source_sha256"],
                    "draft_sha256": packet["draft_sha256"],
                    "guided_marker_sha256": packet["guided_marker_sha256"],
                    "revision_count": 1,
                    "repair_mode": review_gate.REPAIR_MODE_DECISIONS,
                    "repairs": [
                        {
                            "finding_id": finding["finding_id"],
                            "target": finding["target"],
                            "decision": review_gate.DECISION_DELETE,
                            "replacement": "",
                        }
                    ],
                }

            with mock.patch.object(review_gate, "_run_bridge", side_effect=bridge) as runner:
                with redirect_stdout(io.StringIO()):
                    result = review_gate.dispatch_transaction(
                        request_path, draft_path, [], txn, ["host-bridge"], 180, 180
                    )

            state = json.loads((txn / review_gate.STATE_FILE).read_text(encoding="utf-8"))
            self.assertEqual(result, fallback)
            self.assertEqual(runner.call_count, 1)
            self.assertEqual(state["selected"], "D0")
            self.assertIn("hard_anchor", state["reason"])

    def test_emit_rejects_marker_residue_even_on_forced_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                with self.assertRaises(review_gate.GateInputError):
                    review_gate.emit_transaction(
                        Path(directory) / "txn",
                        retained_d0=(
                            f"正文。{review_gate.GUIDED_MARKER_OPEN}尾巴。"
                            f"{review_gate.GUIDED_MARKER_CLOSE}"
                        ),
                        force_retained_d0=True,
                    )
            self.assertEqual(stdout.getvalue(), "")

    def test_dispatch_serializes_concurrent_calls_to_one_selection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            txn = temp / "txn"
            request_path.write_text(self.request, encoding="utf-8")
            draft_path.write_text(self.draft, encoding="utf-8")
            repair_entered = threading.Event()
            release_repair = threading.Event()
            phases: list[str] = []
            phase_lock = threading.Lock()

            def bridge(_command, phase, packet_path, _timeout):
                packet = json.loads(packet_path.read_text(encoding="utf-8"))
                with phase_lock:
                    phases.append(phase)
                if phase == "repair":
                    repair_entered.set()
                    self.assertTrue(release_repair.wait(2))
                    finding = packet["findings"][0]
                    return {
                        "schema_version": review_gate.SCHEMA_VERSION,
                        "run_id": packet["run_id"],
                        "request_sha256": packet["request_sha256"],
                        "source_sha256": packet["source_sha256"],
                        "draft_sha256": packet["draft_sha256"],
                        "revision_count": 1,
                        "repair_mode": review_gate.REPAIR_MODE_DECISIONS,
                        "repairs": [
                            {
                                "finding_id": finding["finding_id"],
                                "target": finding["target"],
                                "decision": review_gate.DECISION_DELETE,
                                "replacement": "",
                            }
                        ],
                    }
                return {
                    "schema_version": review_gate.SEMANTIC_VERDICT_SCHEMA_VERSION,
                    "run_id": packet["run_id"],
                    "request_sha256": packet["request_sha256"],
                    "source_sha256": packet["source_sha256"],
                    "draft_sha256": packet["draft_sha256"],
                    "candidate_sha256": packet["candidate_sha256"],
                    "verdict": "PASS",
                    "checks": {key: True for key in review_gate.SEMANTIC_CHECKS},
                }

            results: list[str] = []
            failures: list[BaseException] = []

            def run_dispatch() -> None:
                try:
                    results.append(
                        review_gate.dispatch_transaction(
                            request_path, draft_path, [], txn, ["host-bridge"], 2, 2
                        )
                    )
                except BaseException as exc:  # pragma: no cover - assertion reports details
                    failures.append(exc)

            stdout = io.StringIO()
            with mock.patch.object(review_gate, "_run_bridge", side_effect=bridge):
                with mock.patch.object(review_gate.sys, "stdout", stdout):
                    first = threading.Thread(target=run_dispatch)
                    second = threading.Thread(target=run_dispatch)
                    first.start()
                    self.assertTrue(repair_entered.wait(2))
                    second.start()
                    time.sleep(0.05)
                    release_repair.set()
                    first.join(3)
                    second.join(3)

            expected = self.draft.replace("尚不能据此直接推定异常已经根本解决。", "")
            state = json.loads((txn / review_gate.STATE_FILE).read_text(encoding="utf-8"))
            self.assertFalse(first.is_alive())
            self.assertFalse(second.is_alive())
            self.assertEqual(failures, [])
            self.assertEqual(results, [expected, expected])
            self.assertEqual(phases, ["repair", "verify"])
            self.assertEqual(stdout.getvalue(), expected + expected)
            self.assertEqual(state["selected"], "D1")
            self.assertEqual(state["repair_agent_call_count"], 1)
            self.assertEqual(state["verdict_agent_call_count"], 1)

    def test_dispatch_bridge_failure_emits_complete_d0_and_never_retries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            txn = temp / "txn"
            request_path.write_text(self.request, encoding="utf-8")
            draft_path.write_text(self.draft, encoding="utf-8")

            first_stdout = io.StringIO()
            with mock.patch.object(
                review_gate, "_run_bridge", side_effect=RuntimeError("bridge down")
            ) as first_runner, redirect_stdout(first_stdout):
                first = review_gate.dispatch_transaction(
                    request_path, draft_path, [], txn, ["host-bridge"], 180, 180
                )

            second_stdout = io.StringIO()
            with mock.patch.object(review_gate, "_run_bridge") as second_runner:
                with redirect_stdout(second_stdout):
                    second = review_gate.dispatch_transaction(
                        request_path, draft_path, [], txn, ["host-bridge"], 180, 180
                    )

            state = json.loads((txn / review_gate.STATE_FILE).read_text(encoding="utf-8"))
            self.assertEqual(first, self.draft)
            self.assertEqual(second, self.draft)
            self.assertEqual(first_stdout.getvalue(), self.draft)
            self.assertEqual(second_stdout.getvalue(), self.draft)
            self.assertEqual(first_runner.call_count, 1)
            self.assertEqual(second_runner.call_count, 0)
            self.assertEqual(state["reason"], "repair_bridge_failed")
            self.assertEqual(state["repair_agent_call_count"], 1)
            self.assertEqual(state["verdict_agent_call_count"], 0)

    def test_dispatch_real_subprocess_timeout_preserves_guided_inner_text(self) -> None:
        _, fallback, raw = self.guided_case()
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            bridge_path = temp / "bridge.py"
            txn = temp / "txn"
            request_path.write_text("请写情况报告，只输出正文。", encoding="utf-8")
            draft_path.write_text(raw, encoding="utf-8")
            bridge_path.write_text(
                "import time\n"
                "time.sleep(2)\n"
                "print('{}')\n",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            started = time.monotonic()
            with redirect_stdout(stdout):
                result = review_gate.dispatch_transaction(
                    request_path,
                    draft_path,
                    [],
                    txn,
                    [sys.executable, str(bridge_path)],
                    1,
                    1,
                )
            elapsed = time.monotonic() - started

            state = json.loads((txn / review_gate.STATE_FILE).read_text(encoding="utf-8"))
            self.assertEqual(result, fallback)
            self.assertEqual(stdout.getvalue(), fallback)
            self.assertFalse(review_gate._has_guided_marker_token(result))
            self.assertLess(elapsed, 3.5)
            self.assertEqual(state["reason"], "repair_bridge_failed")
            self.assertEqual(state["repair_agent_call_count"], 1)
            self.assertEqual(state["verdict_agent_call_count"], 0)

    def test_dispatch_rejects_malformed_bridge_stdout_without_leaking_it(self) -> None:
        _, fallback, raw = self.guided_case()
        bridge_source = (
            "import sys\n"
            "mode = sys.argv[1]\n"
            "if mode == 'invalid-json':\n"
            "    sys.stdout.write('{broken')\n"
            "elif mode == 'log-plus-json':\n"
            "    sys.stdout.write('bridge-log\\n{}')\n"
            "elif mode == 'oversize':\n"
            "    sys.stdout.write('x' * (1024 * 1024 + 1))\n"
        )
        for mode in ("invalid-json", "log-plus-json", "oversize"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                temp = Path(directory)
                request_path = temp / "request.txt"
                draft_path = temp / "draft.txt"
                bridge_path = temp / "bridge.py"
                txn = temp / "txn"
                request_path.write_text("请写情况报告，只输出正文。", encoding="utf-8")
                draft_path.write_text(raw, encoding="utf-8")
                bridge_path.write_text(bridge_source, encoding="utf-8")

                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    result = review_gate.dispatch_transaction(
                        request_path,
                        draft_path,
                        [],
                        txn,
                        [sys.executable, str(bridge_path), mode],
                        5,
                        5,
                    )

                state = json.loads(
                    (txn / review_gate.STATE_FILE).read_text(encoding="utf-8")
                )
                self.assertEqual(result, fallback)
                self.assertEqual(stdout.getvalue(), fallback)
                self.assertNotIn("bridge-log", stdout.getvalue())
                self.assertNotIn("{broken", stdout.getvalue())
                self.assertFalse(review_gate._has_guided_marker_token(result))
                self.assertEqual(state["reason"], "repair_bridge_failed")
                self.assertEqual(state["repair_agent_call_count"], 1)
                self.assertEqual(state["verdict_agent_call_count"], 0)

    def test_dispatch_sidecar_tamper_preserves_guided_inner_text(self) -> None:
        _, fallback, raw = self.guided_case()
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            txn = temp / "txn"
            request_path.write_text("请写情况报告，只输出正文。", encoding="utf-8")
            draft_path.write_text(raw, encoding="utf-8")
            phases: list[str] = []

            def bridge(_command, phase, packet_path, _timeout):
                phases.append(phase)
                self.assertEqual(phase, "repair")
                packet = json.loads(packet_path.read_text(encoding="utf-8"))
                (packet_path.parent / review_gate.GUIDED_MARKER_FILE).write_text(
                    "{}\n", encoding="utf-8"
                )
                return self.guided_delete_response(packet)

            stdout = io.StringIO()
            with mock.patch.object(review_gate, "_run_bridge", side_effect=bridge):
                with redirect_stdout(stdout):
                    result = review_gate.dispatch_transaction(
                        request_path, draft_path, [], txn, ["host-bridge"], 180, 180
                    )

            state = json.loads((txn / review_gate.STATE_FILE).read_text(encoding="utf-8"))
            self.assertEqual(result, fallback)
            self.assertEqual(stdout.getvalue(), fallback)
            self.assertEqual(phases, ["repair"])
            self.assertFalse(review_gate._has_guided_marker_token(result))
            self.assertEqual(state["selected"], "D0")
            self.assertEqual(state["reason"], "mechanical_verification_failed")
            self.assertEqual(state["verdict_agent_call_count"], 0)

    def test_dispatch_does_not_reuse_d1_across_marker_authorization_changes(self) -> None:
        target = "这项补充仅用于说明边界。"
        prefix = (
            "情况报告\n\n"
            "本次核查覆盖运行时段、处置过程和恢复情况，相关数据均已逐项核对。\n"
        )
        fallback = f"{prefix}第一项事实已经记录。{target}\n第二项事实已经记录。{target}"
        first_raw = (
            f"{prefix}第一项事实已经记录。{review_gate.GUIDED_MARKER_OPEN}{target}"
            f"{review_gate.GUIDED_MARKER_CLOSE}\n第二项事实已经记录。{target}"
        )
        second_raw = (
            f"{prefix}第一项事实已经记录。{target}\n第二项事实已经记录。"
            f"{review_gate.GUIDED_MARKER_OPEN}{target}{review_gate.GUIDED_MARKER_CLOSE}"
        )
        first_expected = f"{prefix}第一项事实已经记录。\n第二项事实已经记录。{target}"
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            txn = temp / "txn"
            request_path.write_text("请写情况报告，只输出正文。", encoding="utf-8")
            draft_path.write_text(first_raw, encoding="utf-8")

            def bridge(_command, phase, packet_path, _timeout):
                packet = json.loads(packet_path.read_text(encoding="utf-8"))
                if phase == "repair":
                    repairs = []
                    for finding in packet["findings"]:
                        guided = finding.get("guided_marker") is True
                        repairs.append(
                            {
                                "finding_id": finding["finding_id"],
                                "target": finding["target"],
                                "decision": (
                                    review_gate.DECISION_DELETE
                                    if guided
                                    else review_gate.DECISION_KEEP
                                ),
                                "replacement": "" if guided else finding["target"],
                            }
                        )
                    return {
                        "schema_version": review_gate.SCHEMA_VERSION,
                        "run_id": packet["run_id"],
                        "request_sha256": packet["request_sha256"],
                        "source_sha256": packet["source_sha256"],
                        "draft_sha256": packet["draft_sha256"],
                        "guided_marker_sha256": packet["guided_marker_sha256"],
                        "revision_count": 1,
                        "repair_mode": review_gate.REPAIR_MODE_DECISIONS,
                        "repairs": repairs,
                    }
                return {
                    "schema_version": review_gate.SEMANTIC_VERDICT_SCHEMA_VERSION,
                    "run_id": packet["run_id"],
                    "request_sha256": packet["request_sha256"],
                    "source_sha256": packet["source_sha256"],
                    "draft_sha256": packet["draft_sha256"],
                    "candidate_sha256": packet["candidate_sha256"],
                    "guided_marker_sha256": packet["guided_marker_sha256"],
                    "verdict": "PASS",
                    "checks": {key: True for key in packet["required_checks"]},
                }

            with mock.patch.object(review_gate, "_run_bridge", side_effect=bridge) as runner:
                with redirect_stdout(io.StringIO()):
                    first = review_gate.dispatch_transaction(
                        request_path, draft_path, [], txn, ["host-bridge"], 180, 180
                    )
                draft_path.write_text(second_raw, encoding="utf-8")
                second_stdout = io.StringIO()
                with redirect_stdout(second_stdout):
                    second = review_gate.dispatch_transaction(
                        request_path, draft_path, [], txn, ["host-bridge"], 180, 180
                    )
                draft_path.write_text(fallback, encoding="utf-8")
                third_stdout = io.StringIO()
                with redirect_stdout(third_stdout):
                    third = review_gate.dispatch_transaction(
                        request_path, draft_path, [], txn, ["host-bridge"], 180, 180
                    )

            self.assertEqual(first, first_expected)
            self.assertEqual(second, fallback)
            self.assertEqual(second_stdout.getvalue(), fallback)
            self.assertEqual(third, fallback)
            self.assertEqual(third_stdout.getvalue(), fallback)
            self.assertEqual(runner.call_count, 2)
            self.assertFalse(review_gate._has_guided_marker_token(second))

            reverse_txn = temp / "reverse-txn"
            reverse_target = "尚不能据此直接推定异常已经根本解决。"
            reverse_marked = self.draft.replace(
                reverse_target,
                f"{review_gate.GUIDED_MARKER_OPEN}{reverse_target}"
                f"{review_gate.GUIDED_MARKER_CLOSE}",
            )
            draft_path.write_text(self.draft, encoding="utf-8")

            def reverse_bridge(_command, phase, packet_path, _timeout):
                packet = json.loads(packet_path.read_text(encoding="utf-8"))
                if phase == "repair":
                    finding = packet["findings"][0]
                    return {
                        "schema_version": review_gate.SCHEMA_VERSION,
                        "run_id": packet["run_id"],
                        "request_sha256": packet["request_sha256"],
                        "source_sha256": packet["source_sha256"],
                        "draft_sha256": packet["draft_sha256"],
                        "revision_count": 1,
                        "repair_mode": review_gate.REPAIR_MODE_DECISIONS,
                        "repairs": [
                            {
                                "finding_id": finding["finding_id"],
                                "target": finding["target"],
                                "decision": review_gate.DECISION_DELETE,
                                "replacement": "",
                            }
                        ],
                    }
                return {
                    "schema_version": review_gate.SEMANTIC_VERDICT_SCHEMA_VERSION,
                    "run_id": packet["run_id"],
                    "request_sha256": packet["request_sha256"],
                    "source_sha256": packet["source_sha256"],
                    "draft_sha256": packet["draft_sha256"],
                    "candidate_sha256": packet["candidate_sha256"],
                    "verdict": "PASS",
                    "checks": {key: True for key in packet["required_checks"]},
                }

            with mock.patch.object(
                review_gate, "_run_bridge", side_effect=reverse_bridge
            ) as reverse_runner:
                with redirect_stdout(io.StringIO()):
                    reverse_first = review_gate.dispatch_transaction(
                        request_path, draft_path, [], reverse_txn, ["host-bridge"], 180, 180
                    )
                draft_path.write_text(reverse_marked, encoding="utf-8")
                reverse_stdout = io.StringIO()
                with redirect_stdout(reverse_stdout):
                    reverse_second = review_gate.dispatch_transaction(
                        request_path, draft_path, [], reverse_txn, ["host-bridge"], 180, 180
                    )

            self.assertNotEqual(reverse_first, self.draft)
            self.assertEqual(reverse_second, self.draft)
            self.assertEqual(reverse_stdout.getvalue(), self.draft)
            self.assertIn(reverse_target, reverse_second)
            self.assertEqual(reverse_runner.call_count, 2)

    def test_dispatch_serializes_concurrent_guided_calls_to_one_selection(self) -> None:
        target, fallback, raw = self.guided_case()
        expected = fallback.replace(target, "")
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            txn = temp / "txn"
            request_path.write_text("请写情况报告，只输出正文。", encoding="utf-8")
            draft_path.write_text(raw, encoding="utf-8")
            repair_entered = threading.Event()
            release_repair = threading.Event()
            phases: list[str] = []
            phase_lock = threading.Lock()

            def bridge(_command, phase, packet_path, _timeout):
                packet = json.loads(packet_path.read_text(encoding="utf-8"))
                with phase_lock:
                    phases.append(phase)
                if phase == "repair":
                    repair_entered.set()
                    self.assertTrue(release_repair.wait(2))
                    return self.guided_delete_response(packet)
                return self.semantic_pass_response(packet)

            results: list[str] = []
            failures: list[BaseException] = []

            def run_dispatch() -> None:
                try:
                    results.append(
                        review_gate.dispatch_transaction(
                            request_path, draft_path, [], txn, ["host-bridge"], 2, 2
                        )
                    )
                except BaseException as exc:  # pragma: no cover - assertion reports details
                    failures.append(exc)

            stdout = io.StringIO()
            with mock.patch.object(review_gate, "_run_bridge", side_effect=bridge):
                with mock.patch.object(review_gate.sys, "stdout", stdout):
                    first = threading.Thread(target=run_dispatch)
                    second = threading.Thread(target=run_dispatch)
                    first.start()
                    self.assertTrue(repair_entered.wait(2))
                    second.start()
                    time.sleep(0.05)
                    release_repair.set()
                    first.join(3)
                    second.join(3)

            state = json.loads((txn / review_gate.STATE_FILE).read_text(encoding="utf-8"))
            self.assertFalse(first.is_alive())
            self.assertFalse(second.is_alive())
            self.assertEqual(failures, [])
            self.assertEqual(results, [expected, expected])
            self.assertEqual(phases, ["repair", "verify"])
            self.assertEqual(stdout.getvalue(), expected + expected)
            self.assertNotIn(review_gate.GUIDED_MARKER_OPEN, stdout.getvalue())
            self.assertEqual(state["selected"], "D1")
            self.assertEqual(state["repair_agent_call_count"], 1)
            self.assertEqual(state["verdict_agent_call_count"], 1)

    def test_dispatch_clean_d0_does_not_call_bridge(self) -> None:
        clean = "情况报告\n\n7月8日完成检查，异常原因正在调查中。"
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            txn = temp / "txn"
            request_path.write_text("请写情况报告。", encoding="utf-8")
            draft_path.write_text(clean, encoding="utf-8")
            stdout = io.StringIO()
            with mock.patch.object(review_gate, "_run_bridge") as runner:
                with redirect_stdout(stdout):
                    result = review_gate.dispatch_transaction(
                        request_path, draft_path, [], txn, ["host-bridge"], 180, 180
                    )

            self.assertEqual(result, clean)
            self.assertEqual(stdout.getvalue(), clean)
            self.assertEqual(runner.call_count, 0)

    def test_dispatch_detect_failure_emits_retained_complete_d0(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            txn = temp / "txn"
            txn.mkdir()
            request_path = txn / "request.txt"
            draft_path = temp / "draft.txt"
            request_path.write_text(self.request, encoding="utf-8")
            draft_path.write_text(self.draft, encoding="utf-8")
            stdout = io.StringIO()

            with mock.patch.object(review_gate, "_run_bridge") as runner:
                with redirect_stdout(stdout):
                    result = review_gate.dispatch_transaction(
                        request_path, draft_path, [], txn, ["host-bridge"], 180, 180
                    )

            self.assertEqual(result, self.draft)
            self.assertEqual(stdout.getvalue(), self.draft)
            self.assertEqual(runner.call_count, 0)

    def test_dispatch_missing_source_emits_retained_complete_d0(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            missing_source = temp / "missing-source.txt"
            txn = temp / "txn"
            request_path.write_text(self.request, encoding="utf-8")
            draft_path.write_text(self.draft, encoding="utf-8")
            stdout = io.StringIO()

            with mock.patch.object(review_gate, "_run_bridge") as runner:
                with redirect_stdout(stdout):
                    result = review_gate.dispatch_transaction(
                        request_path,
                        draft_path,
                        [missing_source],
                        txn,
                        ["host-bridge"],
                        180,
                        180,
                    )

            self.assertEqual(result, self.draft)
            self.assertEqual(stdout.getvalue(), self.draft)
            self.assertEqual(runner.call_count, 0)

    def test_dispatch_invalid_verdict_timeout_emits_retained_complete_d0(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            txn = temp / "txn"
            request_path.write_text(self.request, encoding="utf-8")
            draft_path.write_text(self.draft, encoding="utf-8")
            stdout = io.StringIO()

            with mock.patch.object(review_gate, "_run_bridge") as runner:
                with redirect_stdout(stdout):
                    result = review_gate.dispatch_transaction(
                        request_path, draft_path, [], txn, ["host-bridge"], 180, 0
                    )

            self.assertEqual(result, self.draft)
            self.assertEqual(stdout.getvalue(), self.draft)
            self.assertEqual(runner.call_count, 0)

    def test_dispatch_reused_transaction_never_leaks_old_task_draft(self) -> None:
        old_draft = "旧任务情况报告\n\n7月8日完成检查，相关原因正在调查中。"
        current_draft = "新任务情况报告\n\n7月9日完成复核，相关情况正在核查中。"
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            txn = temp / "txn"
            old_request = temp / "old-request.txt"
            old_draft_path = temp / "old-draft.txt"
            current_request = temp / "current-request.txt"
            current_draft_path = temp / "current-draft.txt"
            old_request.write_text("请写旧任务报告。", encoding="utf-8")
            old_draft_path.write_text(old_draft, encoding="utf-8")
            current_request.write_text("请写新任务报告。", encoding="utf-8")
            current_draft_path.write_text(current_draft, encoding="utf-8")

            with mock.patch.object(review_gate, "_run_bridge") as runner:
                with redirect_stdout(io.StringIO()):
                    review_gate.dispatch_transaction(
                        old_request, old_draft_path, [], txn, ["host-bridge"], 180, 180
                    )
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    result = review_gate.dispatch_transaction(
                        current_request,
                        current_draft_path,
                        [],
                        txn,
                        ["host-bridge"],
                        180,
                        180,
                    )

            state = json.loads((txn / review_gate.STATE_FILE).read_text(encoding="utf-8"))
            self.assertEqual(result, current_draft)
            self.assertEqual(stdout.getvalue(), current_draft)
            self.assertEqual(state["d0_sha256"], review_gate.sha256_text(old_draft))
            self.assertEqual(runner.call_count, 0)

    def test_repair_packet_declares_distinct_response_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, state = self.begin_transaction(temp)
            packet = json.loads(
                (txn / review_gate.REPAIR_PACKET_FILE).read_text(encoding="utf-8")
            )

            self.assertEqual(state["state"], review_gate.STATE_AWAITING_REPAIR)
            self.assertEqual(packet["schema_version"], review_gate.REPAIR_PACKET_SCHEMA_VERSION)
            self.assertEqual(packet["response_schema_version"], review_gate.SCHEMA_VERSION)
            self.assertEqual(packet["response_revision_count"], 1)
            self.assertEqual(packet["response_repair_mode"], review_gate.REPAIR_MODE_DECISIONS)
            self.assertEqual(
                state["detection_sha256"],
                review_gate.sha256_text(
                    (txn / review_gate.DETECTION_FILE).read_text(encoding="utf-8")
                ),
            )

    def test_repair_packet_masks_delete_for_semantic_sensitive_finding(self) -> None:
        draft = (
            "数据接口联调专题会议纪要\n\n"
            "截至本次会议结束，是否转入生产环境、资金来源、服务采购方式和下次会议时间"
            "均未形成确定安排，分别保持尚未决定、尚未确定、待研究和时间未定的状态。"
        )
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, state = self.begin_transaction(
                temp, request="请根据已给会议事实形成纪要。", draft=draft
            )
            packet = json.loads(
                (txn / review_gate.REPAIR_PACKET_FILE).read_text(encoding="utf-8")
            )
            finding = packet["findings"][0]

            self.assertEqual(state["state"], review_gate.STATE_AWAITING_REPAIR)
            self.assertNotIn(review_gate.DECISION_DELETE, finding["allowed_decisions"])
            self.assertEqual(finding["delete_block_reason"], "semantic_sensitive_finding")

    def test_repair_packet_allows_delete_only_for_pure_process_self_certification(self) -> None:
        draft = (
            "设备试运行情况报告\n\n"
            "除上述反映外，材料未反映其他设备运行情况。"
            "对失败请求，材料已明确卡纸8次和网络短时中断5次。"
            "上述情况在本报告中据实反映，不作超出试运行记录的分析和判断。"
            "工作人员对接报问题均已进行处理，处理情况以材料记载为准。"
        )
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, state = self.begin_transaction(
                temp, request="请根据试运行记录形成情况报告。", draft=draft
            )
            packet = json.loads(
                (txn / review_gate.REPAIR_PACKET_FILE).read_text(encoding="utf-8")
            )
            by_target = {item["target"]: item for item in packet["findings"]}

            self.assertEqual(state["state"], review_gate.STATE_AWAITING_REPAIR)
            self.assertIn(
                review_gate.DECISION_DELETE,
                by_target["除上述反映外，材料未反映其他设备运行情况。"]["allowed_decisions"],
            )
            self.assertIn(
                review_gate.DECISION_DELETE,
                by_target[
                    "上述情况在本报告中据实反映，不作超出试运行记录的分析和判断。"
                ]["allowed_decisions"],
            )
            self.assertNotIn(
                review_gate.DECISION_DELETE,
                by_target[
                    "对失败请求，材料已明确卡纸8次和网络短时中断5次。"
                ]["allowed_decisions"],
            )
            self.assertNotIn(
                review_gate.DECISION_DELETE,
                by_target[
                    "工作人员对接报问题均已进行处理，处理情况以材料记载为准。"
                ]["allowed_decisions"],
            )

    def test_semantic_fail_after_allowed_process_delete_returns_exact_d0(self) -> None:
        draft = (
            "设备试运行情况报告\n\n"
            "7月10日至14日，8台设备在办事大厅开展试运行，共收到462次打印请求。"
            "其中成功449次、失败13次，失败请求包括卡纸8次和网络短时中断5次。"
            "工作人员对接报问题均已进行处理，截至7月14日18时设备均可正常使用。"
            "除上述反映外，材料未反映其他设备运行情况。"
            "下一步将继续记录设备运行情况，并于7月31日前汇总本阶段数据。"
        )
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(
                temp, request="请根据试运行记录形成情况报告。", draft=draft
            )
            detection = json.loads(
                (txn / review_gate.DETECTION_FILE).read_text(encoding="utf-8")
            )
            finding = detection["findings"][0]
            repair_path = self.write_transaction_repair(
                temp,
                txn,
                [
                    {
                        "finding_id": finding["finding_id"],
                        "target": finding["target"],
                        "decision": review_gate.DECISION_DELETE,
                        "replacement": "",
                    }
                ],
                review_gate.REPAIR_MODE_DECISIONS,
            )

            prepared = review_gate.prepare_transaction(txn, repair_path)
            self.assertEqual(prepared["state"], review_gate.STATE_AWAITING_VERDICT)
            self.assertNotIn(
                finding["target"],
                (txn / review_gate.D1_FILE).read_text(encoding="utf-8"),
            )

            final = review_gate.finalize_transaction(
                txn, self.write_semantic_verdict(temp, txn, passed=False)
            )
            self.assertEqual(final["state"], review_gate.STATE_TERMINAL_D0)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                review_gate.emit_transaction(txn)
            self.assertEqual(stdout.getvalue(), draft)

    def test_repair_packet_masks_delete_for_mixed_fact_and_protective_tail(self) -> None:
        target = (
            "因而，该数据适合用于说明常态下的总体规模，"
            "尚不足以判断不同日期的负荷波动程度。"
        )
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, state = self.begin_transaction(
                temp, request="请根据观察数据形成调研报告。", draft=f"调研报告\n\n{target}"
            )
            packet = json.loads(
                (txn / review_gate.REPAIR_PACKET_FILE).read_text(encoding="utf-8")
            )
            finding = next(item for item in packet["findings"] if item["target"] == target)

            self.assertEqual(state["state"], review_gate.STATE_AWAITING_REPAIR)
            self.assertNotIn(review_gate.DECISION_DELETE, finding["allowed_decisions"])
            self.assertEqual(
                finding["delete_block_reason"], "mixed_required_and_protective_text"
            )

    def test_repair_packet_masks_delete_for_dependent_guided_clause(self) -> None:
        target = "不以本次请示作为确定具体金额、采购方式、供应商或资金来源的依据。"
        original = (
            "关于开展专业检测工作的请示\n\n"
            f"上述未定事项不属于本次请批内容，{target}\n\n"
            "四、请示事项\n\n妥否，请批示。"
        )
        marked = original.replace(
            target,
            f"{review_gate.GUIDED_MARKER_OPEN}{target}{review_gate.GUIDED_MARKER_CLOSE}",
        )
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            marked_path = temp / "marked.txt"
            txn = temp / "txn"
            request_path.write_text("请起草专业检测工作请示。", encoding="utf-8")
            draft_path.write_text(original, encoding="utf-8")
            marked_path.write_text(marked, encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    review_gate.main(
                        [
                            "detect",
                            "--request",
                            str(request_path),
                            "--draft",
                            str(draft_path),
                            "--marked-draft",
                            str(marked_path),
                            "--txn",
                            str(txn),
                        ]
                    ),
                    0,
                )
            packet = json.loads(
                (txn / review_gate.REPAIR_PACKET_FILE).read_text(encoding="utf-8")
            )
            finding = next(item for item in packet["findings"] if item["guided_marker"])

            self.assertNotIn(review_gate.DECISION_DELETE, finding["allowed_decisions"])
            self.assertEqual(
                finding["delete_block_reason"], "guided_span_not_independent_sentence"
            )

    def test_repair_packet_keeps_delete_for_independent_guided_sentence(self) -> None:
        target, original, marked = self.guided_case()
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            marked_path = temp / "marked.txt"
            txn = temp / "txn"
            request_path.write_text("请根据现有事实形成情况报告。", encoding="utf-8")
            draft_path.write_text(original, encoding="utf-8")
            marked_path.write_text(marked, encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    review_gate.main(
                        [
                            "detect",
                            "--request",
                            str(request_path),
                            "--draft",
                            str(draft_path),
                            "--marked-draft",
                            str(marked_path),
                            "--txn",
                            str(txn),
                        ]
                    ),
                    0,
                )
            packet = json.loads(
                (txn / review_gate.REPAIR_PACKET_FILE).read_text(encoding="utf-8")
            )
            finding = next(
                item for item in packet["findings"] if item.get("target") == target
            )

            self.assertIn(review_gate.DECISION_DELETE, finding["allowed_decisions"])
            self.assertIsNone(finding["delete_block_reason"])

    def test_repair_packet_masks_delete_when_guided_hard_anchor_is_unstructured(self) -> None:
        target = "3项问题由第一食堂2批次标签问题和第二食堂1份记录缺失问题组成。"
        original = (
            "检查情况\n\n"
            "检查发现3项问题：第一食堂2批次标签问题，第二食堂1份记录缺失。"
            f"{target}"
        )
        marked = original.replace(
            target,
            f"{review_gate.GUIDED_MARKER_OPEN}{target}{review_gate.GUIDED_MARKER_CLOSE}",
        )
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            marked_path = temp / "marked.txt"
            txn = temp / "txn"
            request_path.write_text(
                "请根据3项问题形成检查情况，其中第一食堂2批次标签有问题，"
                "第二食堂1份记录缺失。",
                encoding="utf-8",
            )
            draft_path.write_text(original, encoding="utf-8")
            marked_path.write_text(marked, encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    review_gate.main(
                        [
                            "detect",
                            "--request",
                            str(request_path),
                            "--draft",
                            str(draft_path),
                            "--marked-draft",
                            str(marked_path),
                            "--txn",
                            str(txn),
                        ]
                    ),
                    0,
                )
            packet = json.loads(
                (txn / review_gate.REPAIR_PACKET_FILE).read_text(encoding="utf-8")
            )
            finding = next(item for item in packet["findings"] if item["guided_marker"])

            self.assertNotIn(review_gate.DECISION_DELETE, finding["allowed_decisions"])
            self.assertEqual(
                finding["delete_block_reason"],
                "guided_delete_hard_anchor_unstructured",
            )

    def test_dispatch_reentry_uses_timeouts_bound_to_original_transaction(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            txn = temp / "txn"
            request_path.write_text(self.request, encoding="utf-8")
            draft_path.write_text(self.draft, encoding="utf-8")
            review_gate.detect_transaction(
                request_path, draft_path, [], txn, 30, 40
            )
            observed = []

            def bridge(_command, phase, packet_path, timeout):
                observed.append((phase, timeout))
                packet = json.loads(packet_path.read_text(encoding="utf-8"))
                if phase == "repair":
                    finding = packet["findings"][0]
                    return {
                        "schema_version": packet["response_schema_version"],
                        "run_id": packet["run_id"],
                        "request_sha256": packet["request_sha256"],
                        "source_sha256": packet["source_sha256"],
                        "draft_sha256": packet["draft_sha256"],
                        "revision_count": packet["response_revision_count"],
                        "repair_mode": packet["response_repair_mode"],
                        "repairs": [{
                            "finding_id": finding["finding_id"],
                            "target": finding["target"],
                            "decision": "DELETE",
                            "replacement": "",
                        }],
                    }
                return {
                    "schema_version": packet["schema_version"],
                    "run_id": packet["run_id"],
                    "request_sha256": packet["request_sha256"],
                    "source_sha256": packet["source_sha256"],
                    "draft_sha256": packet["draft_sha256"],
                    "candidate_sha256": packet["candidate_sha256"],
                    "verdict": "PASS",
                    "checks": {key: True for key in packet["required_checks"]},
                }

            with mock.patch.object(review_gate, "_run_bridge", side_effect=bridge):
                with redirect_stdout(io.StringIO()):
                    review_gate.dispatch_transaction(
                        request_path, draft_path, [], txn, ["host-bridge"], 1, 2
                    )

            self.assertEqual(observed, [("repair", 30), ("verify", 40)])

    def test_bound_d1_is_recovered_when_state_and_snapshot_backup_are_corrupt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            review_gate.prepare_transaction(txn, self.write_transaction_repair(temp, txn))
            final = review_gate.finalize_transaction(
                txn, self.write_semantic_verdict(temp, txn)
            )
            self.assertEqual(final["state"], review_gate.STATE_TERMINAL_D1)
            expected = (txn / review_gate.D1_FILE).read_text(encoding="utf-8")
            bound_hashes = {
                "request_sha256": review_gate.sha256_text(self.request),
                "source_sha256": review_gate.sha256_text(""),
                "d0_sha256": review_gate.sha256_text(self.draft),
            }
            (txn / review_gate.STATE_FILE).write_text("{broken", encoding="utf-8")
            (txn / review_gate.BACKUP_FILE).write_text("{broken", encoding="utf-8")
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                result = review_gate.emit_transaction(
                    txn,
                    retained_d0=self.draft,
                    bound_input_hashes=bound_hashes,
                )

            self.assertEqual(result, expected)
            self.assertEqual(stdout.getvalue(), expected)
            self.assertNotEqual(result, self.draft)

    def test_conflicting_state_and_backup_never_emit_other_task_d1(self) -> None:
        current_request = "请写另一项任务报告。"
        current_d0 = "另一项任务情况报告\n\n7月9日完成复核，相关情况正在核查中。"
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            review_gate.prepare_transaction(txn, self.write_transaction_repair(temp, txn))
            final = review_gate.finalize_transaction(
                txn, self.write_semantic_verdict(temp, txn)
            )
            self.assertEqual(final["state"], review_gate.STATE_TERMINAL_D1)
            backup = json.loads(
                (txn / review_gate.BACKUP_FILE).read_text(encoding="utf-8")
            )
            bound_hashes = {
                "request_sha256": review_gate.sha256_text(current_request),
                "source_sha256": review_gate.sha256_text(""),
                "d0_sha256": review_gate.sha256_text(current_d0),
            }
            backup.update(bound_hashes)
            review_gate.atomic_write_json(txn / review_gate.BACKUP_FILE, backup)
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                result = review_gate.emit_transaction(
                    txn,
                    retained_d0=current_d0,
                    bound_input_hashes=bound_hashes,
                )

            self.assertEqual(
                review_gate._transaction_binding_status(txn, bound_hashes),
                "conflict",
            )
            self.assertEqual(result, current_d0)
            self.assertEqual(stdout.getvalue(), current_d0)

    def test_bridge_subprocess_returns_one_captured_json_object(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            packet_path = Path(directory) / "packet.json"
            packet_path.write_text("{}", encoding="utf-8")
            payload = review_gate._run_bridge(
                [
                    sys.executable,
                    "-c",
                    "import json; print(json.dumps({'status': 'ok'}))",
                ],
                "repair",
                packet_path,
                10,
            )

            self.assertEqual(payload, {"status": "ok"})

    def test_dispatch_cli_runs_real_two_phase_bridge_and_emits_only_d1(self) -> None:
        bridge_source = r'''
import json
import sys
from pathlib import Path

phase = sys.argv[1]
packet = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
if phase == "repair":
    finding = packet["findings"][0]
    response = {
        "schema_version": packet["response_schema_version"],
        "run_id": packet["run_id"],
        "request_sha256": packet["request_sha256"],
        "source_sha256": packet["source_sha256"],
        "draft_sha256": packet["draft_sha256"],
        "revision_count": packet["response_revision_count"],
        "repair_mode": packet["response_repair_mode"],
        "repairs": [{
            "finding_id": finding["finding_id"],
            "target": finding["target"],
            "decision": "DELETE",
            "replacement": ""
        }]
    }
elif phase == "verify":
    response = {
        "schema_version": packet["schema_version"],
        "run_id": packet["run_id"],
        "request_sha256": packet["request_sha256"],
        "source_sha256": packet["source_sha256"],
        "draft_sha256": packet["draft_sha256"],
        "candidate_sha256": packet["candidate_sha256"],
        "verdict": "PASS",
        "checks": {key: True for key in packet["required_checks"]}
    }
else:
    raise SystemExit(9)
print(json.dumps(response, ensure_ascii=False))
'''.strip()
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            bridge_path = temp / "bridge.py"
            txn = temp / "txn"
            request_path.write_text(self.request, encoding="utf-8")
            draft_path.write_text(self.draft, encoding="utf-8")
            bridge_path.write_text(bridge_source, encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                return_code = review_gate.main(
                    [
                        "dispatch",
                        "--request",
                        str(request_path),
                        "--draft",
                        str(draft_path),
                        "--txn",
                        str(txn),
                        "--bridge-executable",
                        sys.executable,
                        "--bridge-arg",
                        str(bridge_path),
                        "--repair-timeout",
                        "30",
                        "--verdict-timeout",
                        "30",
                    ]
                )

            expected = self.draft.replace("尚不能据此直接推定异常已经根本解决。", "")
            state = json.loads((txn / review_gate.STATE_FILE).read_text(encoding="utf-8"))
            self.assertEqual(return_code, 0)
            self.assertEqual(stdout.getvalue(), expected)
            self.assertEqual(stderr.getvalue(), "")
            self.assertEqual(state["state"], review_gate.STATE_TERMINAL_D1)
            self.assertEqual(state["selected"], "D1")
            self.assertEqual(state["repair_agent_call_count"], 1)
            self.assertEqual(state["verdict_agent_call_count"], 1)

    def test_transaction_finalizes_once_and_terminal_reentry_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, state = self.begin_transaction(temp)
            self.assertEqual(state["state"], "AWAITING_REPAIR")
            repair_path = self.write_transaction_repair(temp, txn)
            prepared = review_gate.prepare_transaction(txn, repair_path)
            self.assertEqual(prepared["state"], "AWAITING_VERDICT")
            verdict_path = self.write_semantic_verdict(temp, txn)
            first = review_gate.finalize_transaction(txn, verdict_path)
            self.assertEqual(first["state"], "TERMINAL_D1")
            self.assertEqual(first["repair_count"], 1)
            self.assertEqual(first["mechanical_check_count"], 1)
            self.assertEqual(first["verify_count"], 1)
            bad_path = temp / "repairs-second.json"
            bad_path.write_text("{}", encoding="utf-8")
            second = review_gate.finalize_transaction(txn, bad_path)
            self.assertEqual(second["output_sha256"], first["output_sha256"])
            self.assertEqual(second["repair_count"], 1)
            self.assertEqual(second["verify_count"], 1)
            self.assertEqual(second["state_trace"], first["state_trace"])
            self.assertEqual(second["reason"], first["reason"])

    def test_bounded_decision_packet_completes_one_fsm_pass(self) -> None:
        request = (
            "请写一份80—500字会议纪要。材料明确："
            "本次会议未对维护措施的长期效果作出结论。"
        )
        draft = (
            "设备运行专题会议纪要\n\n"
            "会议听取了设备运行、维护记录和后续工作安排汇报，"
            "已完成事项、正在推进事项及有关责任主体均按材料逐项记录。"
            "目前，故障原因正在调查中，尚未形成正式结论。"
            "具体设备调整方案、责任分工和新增采购安排尚未确定。"
            "本次会议未对维护措施的长期效果作出结论。"
        )
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, state = self.begin_transaction(temp, request=request, draft=draft)
            self.assertEqual(state["state"], "AWAITING_REPAIR")
            detection = json.loads((txn / "detection.json").read_text(encoding="utf-8"))
            repairs = [
                {
                    "finding_id": detection["findings"][0]["finding_id"],
                    "target": detection["findings"][0]["target"],
                    "decision": "REWRITE",
                    "replacement": "目前，故障原因正在调查中。",
                },
                {
                    "finding_id": detection["findings"][1]["finding_id"],
                    "target": detection["findings"][1]["target"],
                    "decision": "REWRITE",
                    "replacement": "相关事项正在研究中。",
                },
                {
                    "finding_id": detection["findings"][2]["finding_id"],
                    "target": detection["findings"][2]["target"],
                    "decision": "KEEP",
                    "replacement": detection["findings"][2]["target"],
                },
            ]
            repair_path = self.write_transaction_repair(
                temp, txn, repairs, review_gate.REPAIR_MODE_DECISIONS
            )
            prepared = review_gate.prepare_transaction(txn, repair_path)
            self.assertEqual(prepared["state"], "AWAITING_VERDICT")
            final = review_gate.finalize_transaction(
                txn, self.write_semantic_verdict(temp, txn)
            )
            self.assertEqual(final["state"], "TERMINAL_D1")
            self.assertEqual(final["state_trace"].count("MECHANICAL_VERIFYING"), 1)
            self.assertEqual(final["state_trace"].count("SEMANTIC_VERIFYING"), 1)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                emitted = review_gate.emit_transaction(txn)
            self.assertEqual(emitted, stdout.getvalue())
            self.assertIn("相关事项正在研究中。", emitted)
            self.assertNotIn("尚未形成正式结论", emitted)

    def test_semantic_fail_discards_candidate_and_returns_exact_d0(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            prepared = review_gate.prepare_transaction(
                txn, self.write_transaction_repair(temp, txn)
            )
            self.assertEqual(prepared["state"], "AWAITING_VERDICT")
            final = review_gate.finalize_transaction(
                txn, self.write_semantic_verdict(temp, txn, passed=False)
            )
            self.assertEqual(final["state"], "TERMINAL_D0")
            self.assertEqual(final["reason"], "semantic_verdict_failed")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                review_gate.emit_transaction(txn)
            self.assertEqual(stdout.getvalue(), self.draft)

    def test_sentence_rewrite_with_new_action_is_contained_by_semantic_verdict(self) -> None:
        replacement = "我局正会同外部专家开展专项安全评估。"
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            detection = json.loads((txn / "detection.json").read_text(encoding="utf-8"))
            finding = detection["findings"][0]
            repair_path = self.write_transaction_repair(
                temp,
                txn,
                [
                    {
                        "finding_id": finding["finding_id"],
                        "target": finding["target"],
                        "replacement": replacement,
                    }
                ],
                review_gate.REPAIR_MODE_REWRITE_SENTENCE,
            )

            prepared = review_gate.prepare_transaction(txn, repair_path)
            self.assertEqual(prepared["state"], "AWAITING_VERDICT")
            self.assertIn(
                replacement,
                (txn / "d1.candidate.txt").read_text(encoding="utf-8"),
            )

            final = review_gate.finalize_transaction(
                txn, self.write_semantic_verdict(temp, txn, passed=False)
            )
            self.assertEqual(final["state"], "TERMINAL_D0")
            self.assertEqual(final["reason"], "semantic_verdict_failed")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                review_gate.emit_transaction(txn)
            self.assertEqual(stdout.getvalue(), self.draft)

    def test_unverifiable_precreated_claim_never_selects_another_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            review_gate.prepare_transaction(txn, self.write_transaction_repair(temp, txn))
            state = json.loads((txn / "state.json").read_text(encoding="utf-8"))
            candidate = (txn / "d1.candidate.txt").read_text(encoding="utf-8")
            forged = {
                "schema_version": review_gate.SCHEMA_VERSION,
                "run_id": state["run_id"],
                "selected": "D1",
                "output_sha256": state["d1_sha256"],
                "output_b64": review_gate._encode_snapshot(candidate),
                "semantic_receipt_sha256": "0" * 64,
            }
            (txn / "selection.claim.json").write_text(
                json.dumps(forged, ensure_ascii=False), encoding="utf-8"
            )
            verdict = self.write_semantic_verdict(temp, txn, passed=False)
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                return_code = review_gate.main(
                    ["finalize", "--txn", str(txn), "--verdict", str(verdict)]
                )

            self.assertEqual(return_code, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn(
                "selection record exists but cannot be verified", stderr.getvalue()
            )
            self.assertEqual(review_gate.emergency_d0(txn), self.draft)

    def test_semantic_hash_mismatch_returns_d0(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            review_gate.prepare_transaction(txn, self.write_transaction_repair(temp, txn))
            verdict = self.write_semantic_verdict(
                temp,
                txn,
                mutate=lambda value: value.__setitem__("candidate_sha256", "0" * 64),
            )
            final = review_gate.finalize_transaction(txn, verdict)
            self.assertEqual(final["state"], "TERMINAL_D0")
            self.assertEqual(final["reason"], "semantic_verdict_hash_mismatch")

    def test_semantic_report_with_extra_advice_is_invalid_and_returns_d0(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            review_gate.prepare_transaction(txn, self.write_transaction_repair(temp, txn))
            verdict = self.write_semantic_verdict(
                temp,
                txn,
                mutate=lambda value: value.__setitem__("advice", "请再修改一次"),
            )
            final = review_gate.finalize_transaction(txn, verdict)
            self.assertEqual(final["state"], "TERMINAL_D0")
            self.assertEqual(final["reason"], "semantic_verdict_schema_mismatch")

    def test_candidate_mutation_after_prepare_returns_d0(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            review_gate.prepare_transaction(txn, self.write_transaction_repair(temp, txn))
            verdict = self.write_semantic_verdict(temp, txn)
            (txn / "d1.candidate.txt").write_text("被改动的候选稿", encoding="utf-8")
            final = review_gate.finalize_transaction(txn, verdict)
            self.assertEqual(final["state"], "TERMINAL_D0")
            self.assertEqual(final["reason"], "candidate_snapshot_corrupt")

    def test_terminal_d1_remains_identical_if_candidate_file_is_damaged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            review_gate.prepare_transaction(txn, self.write_transaction_repair(temp, txn))
            final = review_gate.finalize_transaction(
                txn, self.write_semantic_verdict(temp, txn)
            )
            self.assertEqual(final["state"], "TERMINAL_D1")
            first_stdout = io.StringIO()
            with redirect_stdout(first_stdout):
                first = review_gate.emit_transaction(txn)
            (txn / "d1.candidate.txt").write_text("损坏候选稿", encoding="utf-8")
            second_stdout = io.StringIO()
            with redirect_stdout(second_stdout):
                second = review_gate.emit_transaction(txn)
            self.assertEqual(second, first)
            self.assertEqual(second_stdout.getvalue(), first_stdout.getvalue())

    def test_terminal_d1_uses_claim_backup_if_primary_claim_and_candidate_are_damaged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            review_gate.prepare_transaction(txn, self.write_transaction_repair(temp, txn))
            final = review_gate.finalize_transaction(
                txn, self.write_semantic_verdict(temp, txn)
            )
            expected_hash = final["output_sha256"]
            (txn / "selection.claim.json").write_text("{broken", encoding="utf-8")
            (txn / "d1.candidate.txt").write_text("损坏候选稿", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                text = review_gate.emit_transaction(txn)
            self.assertEqual(review_gate.sha256_text(text), expected_hash)
            self.assertEqual(stdout.getvalue(), text)

    def test_terminal_d1_survives_corrupt_state_without_switching_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            review_gate.prepare_transaction(txn, self.write_transaction_repair(temp, txn))
            final = review_gate.finalize_transaction(
                txn, self.write_semantic_verdict(temp, txn)
            )
            self.assertEqual(final["state"], "TERMINAL_D1")
            first_stdout = io.StringIO()
            with redirect_stdout(first_stdout):
                first = review_gate.emit_transaction(txn)

            (txn / "state.json").write_text("{broken", encoding="utf-8")
            second_stdout = io.StringIO()
            with redirect_stdout(second_stdout):
                second = review_gate.emit_transaction(txn)

            self.assertEqual(second, first)
            self.assertEqual(second_stdout.getvalue(), first_stdout.getvalue())

    def test_terminal_d1_claim_overrides_valid_older_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            review_gate.prepare_transaction(txn, self.write_transaction_repair(temp, txn))
            older_state = (txn / "state.json").read_text(encoding="utf-8")
            final = review_gate.finalize_transaction(
                txn, self.write_semantic_verdict(temp, txn)
            )
            self.assertEqual(final["state"], "TERMINAL_D1")
            first_stdout = io.StringIO()
            with redirect_stdout(first_stdout):
                first = review_gate.emit_transaction(txn)

            (txn / "state.json").write_text(older_state, encoding="utf-8")
            second_stdout = io.StringIO()
            with redirect_stdout(second_stdout):
                second = review_gate.emit_transaction(txn)

            recovered = json.loads((txn / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(recovered["state"], "TERMINAL_D1")
            self.assertEqual(recovered["selected"], "D1")
            self.assertEqual(second, first)
            self.assertEqual(second_stdout.getvalue(), first_stdout.getvalue())

    def test_old_state_with_broken_d1_evidence_never_switches_to_d0(self) -> None:
        for damage in (
            "missing_verdict",
            "corrupt_verdict",
            "corrupt_snapshot_backup",
        ):
            with self.subTest(damage=damage), tempfile.TemporaryDirectory() as directory:
                temp = Path(directory)
                _, _, txn, _ = self.begin_transaction(temp)
                review_gate.prepare_transaction(
                    txn, self.write_transaction_repair(temp, txn)
                )
                older_state = (txn / "state.json").read_text(encoding="utf-8")
                final = review_gate.finalize_transaction(
                    txn, self.write_semantic_verdict(temp, txn)
                )
                self.assertEqual(final["state"], "TERMINAL_D1")
                first_stdout = io.StringIO()
                with redirect_stdout(first_stdout):
                    expected_d1 = review_gate.emit_transaction(txn)
                self.assertNotEqual(expected_d1, self.draft)

                (txn / "state.json").write_text(older_state, encoding="utf-8")
                if damage == "missing_verdict":
                    (txn / review_gate.VERDICT_FILE).unlink()
                elif damage == "corrupt_verdict":
                    (txn / review_gate.VERDICT_FILE).write_text(
                        "{broken", encoding="utf-8"
                    )
                else:
                    (txn / "snapshot.backup.json").write_text(
                        "{broken", encoding="utf-8"
                    )

                stdout = io.StringIO()
                stderr = io.StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    return_code = review_gate.main(["emit", "--txn", str(txn)])

                self.assertEqual(return_code, 2)
                self.assertEqual(stdout.getvalue(), "")
                self.assertIn(
                    "selection record exists but cannot be verified",
                    stderr.getvalue(),
                )
                self.assertEqual(review_gate.emergency_d0(txn), self.draft)

    def test_missing_state_and_selection_records_after_d1_never_switches_to_d0(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            review_gate.prepare_transaction(txn, self.write_transaction_repair(temp, txn))
            final = review_gate.finalize_transaction(
                txn, self.write_semantic_verdict(temp, txn)
            )
            self.assertEqual(final["state"], "TERMINAL_D1")
            first_stdout = io.StringIO()
            with redirect_stdout(first_stdout):
                review_gate.emit_transaction(txn)

            (txn / "state.json").write_text("{broken", encoding="utf-8")
            (txn / "selection.claim.json").unlink()
            (txn / "selection.claim.backup.json").unlink()
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                return_code = review_gate.main(["emit", "--txn", str(txn)])

            self.assertEqual(return_code, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("selection record is missing after semantic PASS", stderr.getvalue())

    def test_forged_terminal_d1_without_claim_or_verdict_is_never_emitted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, state = self.begin_transaction(temp)
            forged = "任意未经复核的D1"
            (txn / review_gate.D1_FILE).write_text(forged, encoding="utf-8")
            state["state"] = review_gate.STATE_TERMINAL_D1
            state["selected"] = "D1"
            state["d1_sha256"] = review_gate.sha256_text(forged)
            state["output_sha256"] = review_gate.sha256_text(forged)
            review_gate.atomic_write_json(txn / review_gate.STATE_FILE, state)

            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                return_code = review_gate.main(["emit", "--txn", str(txn)])

            self.assertEqual(return_code, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("selection record is missing after semantic PASS", stderr.getvalue())

    def test_all_selected_d1_copies_corrupt_returns_error_without_d0(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            review_gate.prepare_transaction(txn, self.write_transaction_repair(temp, txn))
            final = review_gate.finalize_transaction(
                txn, self.write_semantic_verdict(temp, txn)
            )
            self.assertEqual(final["state"], "TERMINAL_D1")
            (txn / "d1.candidate.txt").write_text("损坏候选稿", encoding="utf-8")
            (txn / "selection.claim.json").write_text("{broken", encoding="utf-8")
            (txn / "selection.claim.backup.json").write_text("{broken", encoding="utf-8")

            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                return_code = review_gate.main(["emit", "--txn", str(txn)])

            self.assertEqual(return_code, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("host must use its retained selected output", stderr.getvalue())

    def test_semantic_verdict_path_inside_transaction_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            review_gate.prepare_transaction(txn, self.write_transaction_repair(temp, txn))
            verdict = txn / "untrusted-verdict.json"
            verdict.write_text("{}", encoding="utf-8")
            final = review_gate.finalize_transaction(txn, verdict)
            self.assertEqual(final["state"], "TERMINAL_D0")
            self.assertEqual(final["reason"], "semantic_verdict_path_inside_transaction")

    def test_repeated_prepare_does_not_consume_another_repair_budget(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            repair = self.write_transaction_repair(temp, txn)
            first = review_gate.prepare_transaction(txn, repair)
            second = review_gate.prepare_transaction(txn, repair)
            self.assertEqual(first["state"], "AWAITING_VERDICT")
            self.assertEqual(second["repair_count"], 1)
            self.assertEqual(second["mechanical_check_count"], 1)
            self.assertEqual(second["state_trace"], first["state_trace"])

    def test_lock_busy_emit_atomically_claims_d0_and_blocks_later_d1(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            repair = self.write_transaction_repair(temp, txn)
            stdout = io.StringIO()
            with mock.patch.object(
                review_gate,
                "transaction_lock",
                side_effect=review_gate.TransactionBusyError("busy"),
            ), redirect_stdout(stdout):
                first_text = review_gate.emit_transaction(txn)
            self.assertEqual(first_text, self.draft)
            self.assertEqual(stdout.getvalue(), self.draft)
            self.assertTrue((txn / "selection.claim.json").exists())
            final = review_gate.prepare_transaction(txn, repair)
            self.assertEqual(final["state"], "TERMINAL_D0")
            second_stdout = io.StringIO()
            with redirect_stdout(second_stdout):
                second_text = review_gate.emit_transaction(txn)
            self.assertEqual(second_text, first_text)
            self.assertEqual(second_stdout.getvalue(), self.draft)

    def test_input_file_mutation_after_detect_cannot_change_d0(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, draft_path, txn, _ = self.begin_transaction(temp)
            draft_path.write_text("被外部改动的文件", encoding="utf-8")
            state = review_gate.prepare_transaction(txn, None)
            self.assertEqual(state["state"], "TERMINAL_D0")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                text = review_gate.emit_transaction(txn)
            self.assertEqual(text, self.draft)

    def test_snapshot_file_mutation_recovers_from_backup(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            (txn / "d0.snapshot.txt").write_text("损坏", encoding="utf-8")
            review_gate.abort_transaction(txn, "test_abort")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                text = review_gate.emit_transaction(txn)
            self.assertEqual(text, self.draft)

    def test_corrupt_snapshot_and_backup_are_never_emitted_as_d0(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            (txn / "d0.snapshot.txt").write_text("损坏稿", encoding="utf-8")
            (txn / "snapshot.backup.json").write_text("{broken", encoding="utf-8")
            self.assertIsNone(review_gate.emergency_d0(txn))

    def test_invalid_repair_json_consumes_budget_and_returns_d0(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            repair_path = temp / "repairs.json"
            repair_path.write_text("{broken", encoding="utf-8")
            state = review_gate.prepare_transaction(txn, repair_path)
            self.assertEqual(state["state"], "TERMINAL_D0")
            self.assertEqual(state["repair_count"], 1)
            self.assertEqual(state["mechanical_check_count"], 1)
            self.assertEqual(state["verify_count"], 0)

    def test_interrupted_verification_cannot_retry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, state = self.begin_transaction(temp)
            state["state"] = "SEMANTIC_VERIFYING"
            state["repair_count"] = 1
            state["verify_count"] = 1
            state["state_trace"].append("SEMANTIC_VERIFYING")
            review_gate.atomic_write_json(txn / "state.json", state)
            recovered = review_gate.finalize_transaction(txn, None)
            self.assertEqual(recovered["state"], "TERMINAL_D0")
            self.assertEqual(recovered["reason"], "interrupted_transaction_recovered")
            self.assertEqual(recovered["repair_count"], 1)

    def test_repeated_detect_does_not_scan_again(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path, draft_path, txn, first = self.begin_transaction(temp)
            second = review_gate.detect_transaction(request_path, draft_path, [], txn, 180)
            self.assertEqual(second["run_id"], first["run_id"])
            self.assertEqual(second["detect_count"], 1)
            self.assertEqual(second["state_trace"], first["state_trace"])

    def test_repeated_detect_rejects_different_inputs_in_same_transaction(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path, draft_path, txn, first = self.begin_transaction(temp)
            request_path.write_text("请写另一项任务的情况报告。", encoding="utf-8")
            draft_path.write_text("另一项任务报告\n\nB事项正在推进。", encoding="utf-8")

            with self.assertRaisesRegex(
                review_gate.GateInputError,
                "transaction is already bound to different request, source, or D0 inputs",
            ):
                review_gate.detect_transaction(request_path, draft_path, [], txn, 180)

            state = json.loads((txn / review_gate.STATE_FILE).read_text(encoding="utf-8"))
            self.assertEqual(state["run_id"], first["run_id"])
            self.assertEqual(state["detect_count"], 1)
            self.assertEqual(review_gate.emergency_d0(txn), self.draft)

    def test_emit_before_finalize_permanently_selects_d0(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                text = review_gate.emit_transaction(txn)
            self.assertEqual(text, self.draft)
            state = json.loads((txn / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["state"], "TERMINAL_D0")
            self.assertEqual(state["reason"], "emit_before_terminal")

    def test_repair_path_inside_transaction_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            repair_path = txn / "external-looking.json"
            repair_path.write_text("{}", encoding="utf-8")
            state = review_gate.prepare_transaction(txn, repair_path)
            self.assertEqual(state["state"], "TERMINAL_D0")
            self.assertEqual(state["reason"], "repair_path_inside_transaction")

    def test_detect_rejects_input_inside_transaction(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            txn = temp / "txn"
            txn.mkdir()
            request_path = txn / "request.txt"
            draft_path = temp / "draft.txt"
            request_path.write_text(self.request, encoding="utf-8")
            draft_path.write_text(self.draft, encoding="utf-8")
            with self.assertRaises(review_gate.GateInputError):
                review_gate.detect_transaction(request_path, draft_path, [], txn, 180)

    def test_cli_detect_rejects_draft_inside_transaction(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            txn = temp / "txn"
            txn.mkdir()
            request_path = temp / "request.txt"
            draft_path = txn / "draft.txt"
            request_path.write_text(self.request, encoding="utf-8")
            draft_path.write_text(
                f"{self.draft}⟦OWG-DROP⟧外围说明。⟦/OWG-DROP⟧",
                encoding="utf-8",
            )
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = review_gate.main(
                    [
                        "detect",
                        "--request",
                        str(request_path),
                        "--draft",
                        str(draft_path),
                        "--txn",
                        str(txn),
                    ]
                )
            self.assertEqual(exit_code, 2)
            self.assertIn(
                "input files must stay outside the transaction directory",
                stderr.getvalue(),
            )
            self.assertFalse((txn / review_gate.STATE_FILE).exists())

    def test_emit_cli_rejects_output_path_option(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, _ = self.begin_transaction(temp)
            review_gate.abort_transaction(txn, "test")
            output = temp / "request.txt"
            stderr = io.StringIO()
            with redirect_stderr(stderr), self.assertRaises(SystemExit):
                review_gate.main(["emit", "--txn", str(txn), "--output", str(output)])
            self.assertEqual(output.read_text(encoding="utf-8"), self.request)
            self.assertIn("unrecognized arguments", stderr.getvalue())

    def test_expired_deadline_selects_d0_without_verification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            _, _, txn, state = self.begin_transaction(temp)
            state["repair_deadline_utc"] = "2000-01-01T00:00:00+00:00"
            review_gate.atomic_write_json(txn / "state.json", state)
            repair_path = self.write_transaction_repair(temp, txn)
            final = review_gate.prepare_transaction(txn, repair_path)
            self.assertEqual(final["state"], "TERMINAL_D0")
            self.assertEqual(final["repair_count"], 0)
            self.assertEqual(final["verify_count"], 0)

    def test_verdict_deadline_uses_its_own_bound_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            txn = temp / "txn"
            request_path.write_text(self.request, encoding="utf-8")
            draft_path.write_text(self.draft, encoding="utf-8")
            state = review_gate.detect_transaction(
                request_path, draft_path, [], txn, 1, 180
            )
            repair_path = self.write_transaction_repair(temp, txn)
            prepared = review_gate.prepare_transaction(txn, repair_path)
            deadline = review_gate.datetime.fromisoformat(
                prepared["verdict_deadline_utc"]
            )
            remaining = (
                deadline - review_gate.datetime.now(review_gate.timezone.utc)
            ).total_seconds()

            self.assertEqual(state["repair_timeout_seconds"], 1)
            self.assertEqual(state["verdict_timeout_seconds"], 180)
            self.assertEqual(prepared["state"], review_gate.STATE_AWAITING_VERDICT)
            self.assertGreater(remaining, 170)

    def test_cli_round_trip_emits_only_selected_draft(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            txn = temp / "txn"
            request_path.write_text(self.request, encoding="utf-8")
            draft_path.write_text(self.draft, encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    review_gate.main(
                        ["detect", "--request", str(request_path), "--draft", str(draft_path), "--txn", str(txn)]
                    ),
                    0,
                )
            repair_path = self.write_transaction_repair(temp, txn)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    review_gate.main(["prepare", "--txn", str(txn), "--repairs", str(repair_path)]),
                    0,
                )
            verdict_path = self.write_semantic_verdict(temp, txn)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    review_gate.main(["finalize", "--txn", str(txn), "--verdict", str(verdict_path)]),
                    0,
                )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(review_gate.main(["emit", "--txn", str(txn)]), 0)
            self.assertEqual(stdout.getvalue(), (txn / "d1.candidate.txt").read_text(encoding="utf-8"))

    def test_cli_guided_draft_fallback_emits_marker_free_d0(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            txn = temp / "txn"
            raw_draft = (
                "设备已恢复运行。"
                "⟦OWG-DROP⟧本次检查未对设备长期运行效果作出结论。⟦/OWG-DROP⟧"
            )
            marker_free_d0 = raw_draft.replace("⟦OWG-DROP⟧", "").replace(
                "⟦/OWG-DROP⟧", ""
            )
            request_path.write_text("请根据现有事实写一段设备恢复情况。", encoding="utf-8")
            draft_path.write_text(raw_draft, encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    review_gate.main(
                        [
                            "detect",
                            "--request",
                            str(request_path),
                            "--draft",
                            str(draft_path),
                            "--txn",
                            str(txn),
                        ]
                    ),
                    0,
                )
                self.assertEqual(
                    review_gate.main(
                        ["abort", "--txn", str(txn), "--reason", "test_fallback"]
                    ),
                    0,
                )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(review_gate.main(["emit", "--txn", str(txn)]), 0)
            self.assertEqual(stdout.getvalue(), marker_free_d0)
            self.assertTrue((txn / review_gate.GUIDED_MARKER_FILE).is_file())
            self.assertNotIn("OWG-DROP", stdout.getvalue())

    def test_cli_postdraft_marker_pass_binds_original_d0(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            marked_path = temp / "marked.txt"
            txn = temp / "txn"
            original = "设备已恢复运行。本次检查未对设备长期运行效果作出结论。"
            marked = (
                "设备已恢复运行。"
                "⟦OWG-DROP⟧本次检查未对设备长期运行效果作出结论。⟦/OWG-DROP⟧"
            )
            request_path.write_text("请根据现有事实写一段设备恢复情况。", encoding="utf-8")
            draft_path.write_text(original, encoding="utf-8")
            marked_path.write_text(marked, encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    review_gate.main(
                        [
                            "detect",
                            "--request",
                            str(request_path),
                            "--draft",
                            str(draft_path),
                            "--marked-draft",
                            str(marked_path),
                            "--txn",
                            str(txn),
                        ]
                    ),
                    0,
                )
            state = json.loads((txn / review_gate.STATE_FILE).read_text(encoding="utf-8"))
            self.assertTrue(state["postdraft_marker_pass_verified"])
            self.assertEqual(state["guided_marker_count"], 1)
            self.assertEqual(state["state"], review_gate.STATE_AWAITING_REPAIR)

            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    review_gate.main(
                        ["abort", "--txn", str(txn), "--reason", "test_fallback"]
                    ),
                    0,
                )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(review_gate.main(["emit", "--txn", str(txn)]), 0)
            self.assertEqual(stdout.getvalue(), original)

    def test_cli_postdraft_marker_pass_text_change_selects_original_d0(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            marked_path = temp / "marked.txt"
            txn = temp / "txn"
            original = "设备已恢复运行。"
            changed = "设备已经恢复运行。"
            request_path.write_text("请根据现有事实写一段设备恢复情况。", encoding="utf-8")
            draft_path.write_text(original, encoding="utf-8")
            marked_path.write_text(changed, encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    review_gate.main(
                        [
                            "detect",
                            "--request",
                            str(request_path),
                            "--draft",
                            str(draft_path),
                            "--marked-draft",
                            str(marked_path),
                            "--txn",
                            str(txn),
                        ]
                    ),
                    0,
                )
            state = json.loads((txn / review_gate.STATE_FILE).read_text(encoding="utf-8"))
            self.assertFalse(state["postdraft_marker_pass_verified"])
            self.assertEqual(state["state"], review_gate.STATE_TERMINAL_D0)
            self.assertEqual(state["reason"], "postdraft_marker_pass_changed_text")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(review_gate.main(["emit", "--txn", str(txn)]), 0)
            self.assertEqual(stdout.getvalue(), original)

    def test_cli_zero_marker_pass_keeps_ordinary_findings_in_fsm(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            request_path = temp / "request.txt"
            draft_path = temp / "draft.txt"
            marked_path = temp / "marked.txt"
            txn = temp / "txn"
            request_path.write_text(self.request, encoding="utf-8")
            draft_path.write_text(self.draft, encoding="utf-8")
            marked_path.write_text(self.draft, encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                self.assertEqual(
                    review_gate.main(
                        [
                            "detect",
                            "--request",
                            str(request_path),
                            "--draft",
                            str(draft_path),
                            "--marked-draft",
                            str(marked_path),
                            "--txn",
                            str(txn),
                        ]
                    ),
                    0,
                )
            state = json.loads((txn / review_gate.STATE_FILE).read_text(encoding="utf-8"))
            self.assertTrue(state["postdraft_marker_pass_verified"])
            self.assertEqual(state["guided_marker_count"], 0)
            self.assertEqual(state["state"], review_gate.STATE_AWAITING_REPAIR)
            self.assertGreater(
                len(json.loads((txn / review_gate.DETECTION_FILE).read_text(encoding="utf-8"))["findings"]),
                0,
            )

    def test_drafting_prompt_does_not_delegate_gate_to_model(self) -> None:
        skill = (ROOT / "chinese-official-writing" / "SKILL.md").read_text(encoding="utf-8")
        information = (
            ROOT / "chinese-official-writing" / "references" / "information-selection.md"
        ).read_text(encoding="utf-8")
        gate = (
            ROOT / "chinese-official-writing" / "references" / "delivery-review-gate.md"
        ).read_text(encoding="utf-8")
        for model_side_gate_instruction in (
            "当前宿主具备命令执行能力且门禁脚本可用时",
            "执行一次写后只标记复看",
            "把两份文本交给 `references/delivery-review-gate.md`",
            "把 `emit` 标准输出逐字作为本轮整条最终回复",
            "⟦OWG-DROP⟧",
            "scripts/review_gate.py",
        ):
            self.assertNotIn(model_side_gate_instruction, skill)
            self.assertNotIn(model_side_gate_instruction, information)
        self.assertIn("先服从用户指定的输出模式", skill)
        self.assertIn("不影响文种功能或办理落地的外围事项，直接省略", information)
        self.assertIn("正文已经承载的状态不在文后重复", information)
        self.assertIn("`--draft` 传入复看前 D0", gate)
        self.assertIn("`--marked-draft` 传入复看稿", gate)
        self.assertIn("任何差异均选择复看前 D0", gate)
        self.assertIn("零标记仍须执行普通检测", gate)
        self.assertIn("存在普通 finding 时继续既有有限状态链", gate)
        self.assertIn("最后统一由 `emit` 交付 D0 或 D1", gate)
        self.assertIn("把本次 `emit` 的标准输出逐字作为整条最终回复，输出后结束回答", gate)
        self.assertIn("门禁不要求模型补写待处理内容", gate)
        self.assertIn("相邻零增量复述", gate)
        self.assertIn("无办理作用复述已经删除或减少", gate)
        self.assertIn("全部删除会使篇幅明显偏离时", gate)
        self.assertIn("不补写新内容凑字数", gate)
        self.assertIn("`repair.packet.json` 含 `guided_marker_sha256` 时", gate)
        self.assertIn('"guided_marker_sha256": "<repair.packet.json 含此字段时逐字复制>"', gate)
        self.assertNotIn("先建立含原始请求、用户材料和 D0 的一次性事务", skill)
        self.assertNotIn("最多提交一个局部补丁包", skill)

    def test_gate_reference_has_no_recursive_transition(self) -> None:
        reference = (
            ROOT / "chinese-official-writing" / "references" / "delivery-review-gate.md"
        ).read_text(encoding="utf-8")
        self.assertIn("每个事务只有一次检测、一次补丁预算、一次机械预检和一次语义确认预算", reference)
        self.assertIn("状态之间没有返回边", reference)
        self.assertIn("最多处理 12 个 finding", reference)
        self.assertIn("每项只选 `KEEP`、`DELETE` 或 `REWRITE`", reference)
        self.assertIn("整个决策包仍只计一次补丁", reference)
        self.assertIn("不拆包、不追加第二轮", reference)
        self.assertIn("语义确认只判定当前 D1，不得返回补丁或触发第二次修改", reference)
        self.assertIn("原子选择凭证立即锁定 D0", reference)
        self.assertIn("`emit` 是唯一终稿读取入口", reference)
        self.assertIn("首次起草调用本身的超时、拒绝或无返回由宿主处理", reference)


if __name__ == "__main__":
    unittest.main()
