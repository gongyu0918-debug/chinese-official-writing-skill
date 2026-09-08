"""Source-binding recovery contracts; fake verdicts prove engineering behavior only."""
import copy
import json
import unittest

try:
    from maintenance.tests import test_source_fact_review as fixtures
except ModuleNotFoundError:
    import test_source_fact_review as fixtures

GATE = fixtures.GATE


class SourceFactRecoveryTests(unittest.TestCase):
    setUp = fixtures.SourceFactReviewTests.setUp
    start = fixtures.SourceFactReviewTests.start
    repair = fixtures.SourceFactReviewTests.repair
    verdict = fixtures.SourceFactReviewTests.verdict

    def ready(self):
        self.start()
        state = self.repair()
        self.assertEqual(GATE.STATE_AWAITING_VERDICT, state["state"])
        return state

    def change_state(self, remove=(), **changes):
        state = GATE.read_json(self.txn / GATE.STATE_FILE)
        for key in remove:
            state.pop(key, None)
        state.update(changes)
        GATE.atomic_write_json(self.txn / GATE.STATE_FILE, state)

    def legacy_verdict(self):
        packet = GATE.read_json(self.txn / GATE.VERIFICATION_PACKET_FILE)
        payload = {
            "schema_version": GATE.SEMANTIC_VERDICT_SCHEMA_VERSION,
            **{key: packet[key] for key in (
                "run_id", "request_sha256", "source_sha256", "draft_sha256", "candidate_sha256"
            )},
            "verdict": "PASS",
            "checks": {key: True for key in GATE.SEMANTIC_CHECKS},
        }
        path = self.root / "legacy-verdict.json"
        GATE.atomic_write_json(path, payload)
        return GATE.finalize_transaction(self.txn, path)

    def replace_packet(self, packet, **state_changes):
        GATE.atomic_write_json(self.txn / GATE.VERIFICATION_PACKET_FILE, packet)
        self.change_state(
            verification_packet_sha256=GATE.sha256_text(
                GATE.read_text(self.txn / GATE.VERIFICATION_PACKET_FILE)
            ),
            **state_changes,
        )

    def test_missing_source_state_fields_cannot_accept_legacy_verdict(self):
        for fields in (
            ("source_relation_packet_sha256",),
            ("source_relation_packet_sha256", "source_relation_ids"),
        ):
            with self.subTest(fields=fields):
                self.txn = self.root / ("txn-" + str(len(fields)))
                self.ready()
                self.change_state(remove=fields)
                self.assertEqual("D0", self.legacy_verdict()["selected"])

    def test_missing_ids_cannot_accept_empty_source_verdict(self):
        self.ready()
        self.change_state(remove=("source_relation_ids",))
        self.assertEqual("D0", self.verdict(source_relations=[])["selected"])

    def test_packet_restores_missing_source_fields_for_complete_verdict(self):
        original = self.ready()
        self.change_state(remove=("source_relation_packet_sha256", "source_relation_ids"))
        selected = self.verdict()
        self.assertEqual("D1", selected["selected"])
        self.assertEqual(original["source_relation_packet_sha256"], selected["source_relation_packet_sha256"])
        self.assertEqual(original["source_relation_ids"], selected["source_relation_ids"])

    def test_conflicting_state_binding_rejects_candidate(self):
        self.ready()
        self.change_state(source_relation_packet_sha256="0" * 64)
        self.assertEqual("D0", self.verdict()["selected"])

    def test_missing_outer_packet_hash_cannot_finalize(self):
        self.ready()
        self.change_state(remove=("verification_packet_sha256",))
        self.assertEqual("D0", self.verdict()["selected"])

    def test_all_four_input_hashes_are_cross_checked(self):
        for key in ("request_sha256", "source_sha256", "draft_sha256", "candidate_sha256"):
            with self.subTest(key=key):
                self.txn = self.root / key
                self.ready()
                packet = GATE.read_json(self.txn / GATE.VERIFICATION_PACKET_FILE)
                packet[key] = "0" * 64
                self.replace_packet(packet)
                self.assertEqual("D0", self.verdict()["selected"])

    def test_relation_packet_hash_cannot_be_self_asserted(self):
        self.ready()
        packet = GATE.read_json(self.txn / GATE.VERIFICATION_PACKET_FILE)
        packet["source_relations"]["packet_sha256"] = "0" * 64
        self.replace_packet(packet, source_relation_packet_sha256="0" * 64)
        self.assertEqual("D0", self.verdict()["selected"])

    def test_source_quote_and_origin_cannot_be_replaced_by_draft(self):
        for field, value in (("quote", "不存在的来源引句"), ("origin", "D0")):
            with self.subTest(field=field):
                self.txn = self.root / field
                self.ready()
                packet = GATE.read_json(self.txn / GATE.VERIFICATION_PACKET_FILE)
                relation = packet["source_relations"]
                relation["findings"][0]["source_relation"]["evidence"][0][field] = value
                unsigned = {key: item for key, item in relation.items() if key != "packet_sha256"}
                relation["packet_sha256"] = GATE.sha256_text(json.dumps(
                    unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                ))
                self.replace_packet(packet, source_relation_packet_sha256=relation["packet_sha256"])
                self.assertEqual("D0", self.verdict()["selected"])

    def test_empty_or_duplicate_relation_findings_are_rejected(self):
        for duplicate in (False, True):
            with self.subTest(duplicate=duplicate):
                self.txn = self.root / str(duplicate)
                self.ready()
                packet = GATE.read_json(self.txn / GATE.VERIFICATION_PACKET_FILE)
                rows = packet["source_relations"]["findings"]
                rows[:] = rows + [copy.deepcopy(rows[0])] if duplicate else []
                self.replace_packet(packet)
                self.assertEqual("D0", self.verdict()["selected"])

    def test_ordinary_selected_d1_retains_legacy_recovery_dependencies(self):
        for state_mode in ("terminal", "stale", "missing"):
            with self.subTest(state=state_mode):
                self.txn = self.root / state_mode
                request = "请写一份情况报告，控制在40—220字。材料：7月8日页面出现6次短时空白，13名用户反映无法登录，异常原因正在调查中。只输出正文。"
                expected = ("政务服务登录页面异常情况报告\n\n"
                            "7月8日，登录页面出现6次短时空白，13名用户反映无法登录，异常原因正在调查中。"
                            "技术人员已记录发生时段、恢复情况和用户反馈，相关排查工作正在推进。")
                draft = expected + "尚不能据此直接推定异常已经根本解决。"
                self.start(request=request,material="",draft=draft)
                packet = GATE.read_json(self.txn / GATE.REPAIR_PACKET_FILE)
                self.assertTrue(packet["findings"])
                self.assertFalse(any(row.get("source_relation") for row in packet["findings"]))
                response = {
                    "schema_version": GATE.SCHEMA_VERSION,
                    **{key: packet[key] for key in (
                        "run_id", "request_sha256", "source_sha256", "draft_sha256"
                    )},
                    "revision_count": 1, "repair_mode": "decisions",
                    "repairs": [{"finding_id": row["finding_id"], "target": row["target"],
                                 "decision": "DELETE", "replacement": ""}
                                for row in packet["findings"]],
                }
                path = self.root / "ordinary-repair.json"
                GATE.atomic_write_json(path, response)
                prepared = GATE.prepare_transaction(self.txn, path)
                self.assertEqual(GATE.STATE_AWAITING_VERDICT, prepared["state"], prepared["reason"])
                self.assertEqual("D1", self.legacy_verdict()["selected"])
                candidate = GATE.read_text(self.txn / GATE.D1_FILE)
                self.assertEqual(expected, candidate)
                for filename in (GATE.VERIFICATION_PACKET_FILE, GATE.REPAIR_FILE):
                    (self.txn / filename).unlink()
                # Existing report evidence is sufficient for an ordinary, receipt-bound D1.
                report = GATE.source_fact_report(self.txn, candidate)
                self.assertEqual("PASS", report["candidate_verdict"])
                self.assertTrue(report["delivery_verified"])
                self.assertFalse(report["full_draft_fact_verified"])
                for filename in (GATE.DETECTION_FILE, GATE.D1_FILE):
                    (self.txn / filename).unlink()
                if state_mode == "missing":
                    (self.txn / GATE.STATE_FILE).unlink()
                elif state_mode == "stale":
                    self.change_state(state=GATE.STATE_AWAITING_VERDICT, selected=None,
                                      d1_sha256=None, semantic_pass_receipt_sha256=None)
                self.assertTrue(GATE._potential_semantic_pass(self.txn))
                self.assertEqual(candidate, GATE.emit_transaction(self.txn))
                self.assertEqual("D1", GATE.read_json(self.txn / GATE.SELECTION_FILE)["selected"])

    def test_source_receipt_cannot_be_downgraded_after_state_loss(self):
        self.ready()
        self.verdict()
        verdict = GATE.read_json(self.txn / GATE.VERDICT_FILE)
        verdict.pop("source_relation_packet_sha256")
        verdict.pop("source_relations")
        verdict["checks"] = {key: True for key in GATE.SEMANTIC_CHECKS}
        GATE.atomic_write_json(self.txn / GATE.VERDICT_FILE, verdict)
        (self.txn / GATE.STATE_FILE).unlink()
        (self.txn / GATE.VERIFICATION_PACKET_FILE).unlink()
        with self.assertRaises(GATE.GateInputError):
            GATE.emit_transaction(self.txn)
        with self.assertRaises(GATE.GateInputError):
            GATE.source_fact_report(self.txn, fixtures.D1)
        self.assertEqual("D1", GATE.read_json(self.txn / GATE.SELECTION_FILE)["selected"])

    def test_state_loss_recovers_selected_d1_and_report(self):
        self.ready()
        selected = self.verdict()
        self.assertEqual("D1", selected["selected"])
        (self.txn / GATE.STATE_FILE).unlink()
        self.assertEqual(fixtures.D1, GATE.emit_transaction(self.txn))
        report = GATE.source_fact_report(self.txn)
        self.assertEqual("D1", report["selected"])
        self.assertEqual("PASS", report["candidate_verdict"])
        self.assertEqual(selected["source_relation_packet_sha256"], report["source_relation_packet_sha256"])
        self.assertIsNone(report["delivery_verified"])
        self.assertIsNone(report["findings"][0]["delivered_issue_resolved"])
        report = GATE.source_fact_report(self.txn, fixtures.D1)
        self.assertTrue(report["delivery_verified"])
        self.assertTrue(report["findings"][0]["delivered_issue_resolved"])
        self.assertFalse(GATE.source_fact_report(self.txn, fixtures.D0)["delivery_verified"])
        self.assertNotIn("9月4日", GATE.emit_transaction(self.txn))

    def test_partial_state_loss_does_not_erase_report_binding(self):
        self.ready()
        selected = self.verdict()
        self.change_state(remove=("source_relation_packet_sha256", "source_relation_ids"))
        report = GATE.source_fact_report(self.txn, fixtures.D1)
        self.assertEqual(selected["source_relation_packet_sha256"], report["source_relation_packet_sha256"])
        self.assertEqual("PASS", report["candidate_verdict"])
        self.assertTrue(report["delivery_verified"])

    def test_missing_recovery_packet_does_not_emit_opposite_d0(self):
        self.ready()
        self.verdict()
        (self.txn / GATE.STATE_FILE).unlink()
        (self.txn / GATE.VERIFICATION_PACKET_FILE).unlink()
        with self.assertRaises(GATE.GateInputError):
            GATE.emit_transaction(self.txn)
        claim = GATE.read_json(self.txn / GATE.SELECTION_FILE)
        self.assertEqual("D1", claim["selected"])

    def test_corrupt_packet_cannot_be_reported_as_delivered_correction(self):
        self.ready()
        self.verdict()
        packet = GATE.read_json(self.txn / GATE.VERIFICATION_PACKET_FILE)
        packet["source_relations"]["findings"] = []
        GATE.atomic_write_json(self.txn / GATE.VERIFICATION_PACKET_FILE, packet)
        with self.assertRaises(GATE.GateInputError):
            GATE.source_fact_report(self.txn, fixtures.D1)

    def test_unknown_kept_text_still_is_not_fact_pass(self):
        self.start()
        self.repair(assessment="unknown")
        report = GATE.source_fact_report(self.txn, fixtures.D0)
        self.assertTrue(report["unknown_ids"])
        self.assertFalse(report["full_draft_fact_verified"])
        self.assertEqual("NOT_RUN", report["candidate_verdict"])


if __name__ == "__main__":
    unittest.main()
