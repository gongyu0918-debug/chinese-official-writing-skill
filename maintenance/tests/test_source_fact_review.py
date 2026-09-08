"""Behavioral contracts for bounded source corrections, not model-quality scores."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

GATE = load("source_fact_gate_tests", ROOT / "chinese-official-writing/scripts/review_gate.py")
HOOK = load("source_fact_hook_tests", ROOT / "chinese-official-writing/hooks/core/gate_stop_hook.py")
SOURCE = load("source_fact_contract_tests", ROOT / "chinese-official-writing/hooks/core/source_fact_review.py")

REQUEST = "根据材料写进展说明，保留有据分析，直接给正文。"
MATERIAL = "截至9月4日，业务科正在核对18份附件，其中10份已经核对完成，剩余8份尚未完成。反馈日期未定。"
D0 = "附件核对情况\n\n业务科尚未开展18份附件核对，其中10份已经完成，剩余8份尚未完成。反馈日期未定。核对结果有助于厘清附件归属。"
D1 = D0.replace("尚未开展18份附件核对", "正在核对18份附件")

class SourceFactReviewTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.txn = self.root / "txn"

    def start(self, request=REQUEST, material=MATERIAL, draft=D0):
        for name, text in (("request",request),("source",material),("draft",draft)):
            (self.root / (name+".txt")).write_text(text,encoding="utf-8")
        return GATE.detect_transaction(self.root/"request.txt",self.root/"draft.txt",[self.root/"source.txt"],self.txn,180,180)

    def repair(self, replacement=None, assessment="error"):
        packet=GATE.read_json(self.txn/GATE.REPAIR_PACKET_FILE)
        repairs=[];assessments=[]
        for item in packet["findings"]:
            target=item["target"]
            changed=target.replace("尚未开展18份附件核对","正在核对18份附件") if replacement is None else replacement
            if assessment!="error": changed=target
            repairs.append({"finding_id":item["finding_id"],"target":target,"decision":"KEEP" if changed==target else "REWRITE","replacement":changed})
            if item.get("source_relation"):
                assessments.append({"finding_id":item["finding_id"],"status":assessment,"reason":"按当前材料核对同一附件核对事项的开始状态。"})
        response={"schema_version":GATE.SCHEMA_VERSION,"run_id":packet["run_id"],"request_sha256":packet["request_sha256"],"source_sha256":packet["source_sha256"],"draft_sha256":packet["draft_sha256"],"revision_count":1,"repair_mode":"decisions","repairs":repairs,"source_assessments":assessments}
        path=self.root/"repair.json";GATE.atomic_write_json(path,response)
        return GATE.prepare_transaction(self.txn,path)

    def verdict(self, **changes):
        packet=GATE.read_json(self.txn/GATE.VERIFICATION_PACKET_FILE)
        response={"schema_version":1,**{key:packet[key] for key in ("run_id","request_sha256","source_sha256","draft_sha256","candidate_sha256")},"verdict":"PASS","checks":{key:True for key in packet["required_checks"]},"source_relation_packet_sha256":packet["source_relations"]["packet_sha256"],"source_relations":[{"finding_id":item["finding_id"],"d0_issue_status":"error","d0_issue_resolved":True,"source_relation_supported":True,"other_facts_preserved":True,"reason":"单元测试核验夹具：同一事项进行态更正，其他内容保留。"} for item in packet["source_relations"]["findings"]]}
        response.update(changes)
        path=self.root/"verdict.json";GATE.atomic_write_json(path,response)
        return GATE.finalize_transaction(self.txn,path)

    def test_actual_quote_spans_bind_all_four_inputs(self):
        findings=SOURCE.locate_candidates(REQUEST,MATERIAL,D0)
        self.assertEqual(1,len(findings))
        self.assertEqual("pending",findings[0]["assessment_status"])
        repairs=[{"finding_id":findings[0]["finding_id"],"target":findings[0]["target"],"decision":"REWRITE","replacement":findings[0]["target"].replace("尚未开展18份附件核对","正在核对18份附件")}]
        packet=SOURCE.build_relation_packet(REQUEST,MATERIAL,D0,D1,findings,repairs)
        self.assertEqual(GATE.sha256_text(D1),packet["d1_sha256"])
        self.assertIsNone(packet["findings"][0]["resolved"])
        findings[0]["source_relation"]["evidence"][0]["quote"]="材料并不存在的引句"
        with self.assertRaises(ValueError): SOURCE.build_relation_packet(REQUEST,MATERIAL,D0,D1,findings,repairs)

    def test_outside_target_edit_cannot_enter_relation_packet(self):
        findings=SOURCE.locate_candidates(REQUEST,MATERIAL,D0)
        repairs=[{"finding_id":findings[0]["finding_id"],"target":findings[0]["target"],"decision":"REWRITE","replacement":findings[0]["target"].replace("尚未开展18份附件核对","正在核对18份附件")}]
        with self.assertRaises(ValueError): SOURCE.build_relation_packet(REQUEST,MATERIAL,D0,D1.replace("有助于厘清","已经解决"),findings,repairs)

    def test_source_date_omission_is_not_candidate_deletion(self):
        self.start();state=self.repair()
        self.assertEqual(GATE.STATE_AWAITING_VERDICT,state["state"])
        self.assertEqual(D1,GATE.read_text(self.txn/GATE.D1_FILE))
        self.assertNotIn("9月4日",GATE.read_text(self.txn/GATE.D1_FILE))
        packet=GATE.read_json(self.txn/GATE.VERIFICATION_PACKET_FILE)
        self.assertIn("source_fact_corrections_verified",packet["required_checks"])

    def test_new_source_date_does_not_bypass_existing_anchor_contract(self):
        self.start()
        target=SOURCE.locate_candidates(REQUEST,MATERIAL,D0)[0]["target"]
        state=self.repair("截至9月4日，"+target.replace("尚未开展18份附件核对","正在核对18份附件"))
        self.assertEqual("D0",state["selected"])
        self.assertEqual(D0,GATE.emit_transaction(self.txn))

    def test_delta_only_verdict_cannot_approve_original_error_correction(self):
        self.start();self.repair()
        packet=GATE.read_json(self.txn/GATE.VERIFICATION_PACKET_FILE)
        response={"schema_version":1,**{key:packet[key] for key in ("run_id","request_sha256","source_sha256","draft_sha256","candidate_sha256")},"verdict":"PASS","checks":{key:True for key in GATE.SEMANTIC_CHECKS}}
        path=self.root/"verdict.json";GATE.atomic_write_json(path,response)
        state=GATE.finalize_transaction(self.txn,path)
        self.assertEqual("D0",state["selected"])
        report=GATE.source_fact_report(self.txn,GATE.emit_transaction(self.txn))
        self.assertFalse(report["full_draft_fact_verified"])
        self.assertTrue(report["unresolved_ids"])

    def test_unknown_is_not_error_and_keep_is_not_fact_pass(self):
        self.start();state=self.repair(assessment="unknown")
        self.assertEqual("D0",state["selected"])
        report=GATE.source_fact_report(self.txn,D0)
        self.assertTrue(report["delivery_verified"])
        self.assertTrue(report["unknown_ids"])
        self.assertFalse(report["full_draft_fact_verified"])
        self.assertEqual("NOT_RUN",report["candidate_verdict"])

    def test_relation_failure_retains_original_without_quality_pass(self):
        self.start();self.repair()
        state=GATE.read_json(self.txn/GATE.STATE_FILE)
        rows=[{"finding_id":fid,"d0_issue_status":"error","d0_issue_resolved":False,"source_relation_supported":False,"other_facts_preserved":False,"reason":"候选新增已开展状态，关系核验不成立。"} for fid in state["source_relation_ids"]]
        result=self.verdict(verdict="FAIL",source_relations=rows)
        self.assertEqual("D0",result["selected"])
        self.assertEqual(D0,GATE.emit_transaction(self.txn))

    def test_selection_and_observed_delivery_are_separate(self):
        self.start();self.repair();state=self.verdict()
        self.assertEqual("D1",state["selected"])
        report=GATE.source_fact_report(self.txn)
        self.assertIsNone(report["delivery_verified"])
        self.assertIsNone(report["findings"][0]["delivered_issue_resolved"])
        report=GATE.source_fact_report(self.txn,GATE.emit_transaction(self.txn))
        self.assertTrue(report["delivery_verified"])
        self.assertTrue(report["findings"][0]["delivered_issue_resolved"])
        self.assertFalse(GATE.source_fact_report(self.txn,D0)["delivery_verified"])

    def test_malformed_model_rows_still_report_unresolved_d0(self):
        for i,rows in enumerate((None,{"finding_id":"P001"},[{"finding_id":[]}])):
            with self.subTest(rows=rows):
                self.txn=self.root/("malformed-"+str(i))
                self.start();self.repair()
                self.assertEqual("D0",self.verdict(source_relations=rows)["selected"])
                report=GATE.source_fact_report(self.txn,D0)
                self.assertEqual("FAIL_OR_INVALID",report["candidate_verdict"])
                self.assertTrue(report["unresolved_ids"])
                self.assertFalse(report["findings"][0]["delivered_issue_resolved"])
                repair=GATE.read_json(self.txn/GATE.REPAIR_FILE)
                repair["source_assessments"]=None
                GATE.atomic_write_json(self.txn/GATE.REPAIR_FILE,repair)
                self.assertTrue(GATE.source_fact_report(self.txn,D0)["unknown_ids"])

    def test_changed_snapshot_prevents_review_prompt(self):
        self.start()
        self.assertIsNotNone(HOOK._repair_instruction(self.txn))
        (self.txn/GATE.SOURCE_FILE).write_text(MATERIAL+"另加一句。",encoding="utf-8")
        self.assertIsNone(HOOK._repair_instruction(self.txn))

    def test_enclosed_condition_and_existing_finding_use_one_repair(self):
        material = "8盒档案附件归属尚待核实，反馈日期未定。已扫描图像尚未完成抽检，抽检安排已定，完成时间未定。"
        prefix = "目录核对涉及附件归属，验收统计以完成抽检的结果为准。\n\n"
        target = "目前，8盒档案附件归属核实的反馈日期和已扫描图像抽检的完成时间尚未确定；上述时间明确后，目录核对和验收工作可相应推进。"
        draft = prefix + target
        self.start(material=material,draft=draft)
        packet=GATE.read_json(self.txn/GATE.REPAIR_PACKET_FILE)
        findings=packet["findings"]
        self.assertEqual(1,len(findings))
        self.assertTrue(findings[0]["finding_id"].startswith("P"))
        self.assertIn("source-unsupported-prerequisite",findings[0]["labels"])
        self.assertGreater(len(findings[0]["labels"]),1)
        replacement=target.split("；")[0]+"。"
        state=self.repair(replacement=replacement)
        self.assertEqual(GATE.STATE_AWAITING_VERDICT,state["state"])
        self.assertEqual(prefix+replacement,GATE.read_text(self.txn/GATE.D1_FILE))
        self.assertEqual("D1",self.verdict()["selected"])

    def test_unknown_start_and_reasonable_analysis_are_not_auto_errors(self):
        self.assertEqual([],SOURCE.locate_candidates("","抽检未完成，下一步准备抽检。","尚未开展抽检。"))
        self.assertEqual([],SOURCE.locate_candidates("","设备维护停机3天，目前已恢复。","停机可能是当期进度放缓的原因之一，建议继续推进整理。"))

if __name__=="__main__": unittest.main()
