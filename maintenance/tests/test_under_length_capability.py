from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
CORE_PATH = ROOT / "chinese-official-writing/hooks/core/gate_stop_hook.py"
RUNTIME_PATH = ROOT / "chinese-official-writing/hooks/capabilities/under_length/runtime.py"
SKILL_PATH = ROOT / "chinese-official-writing/SKILL.md"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CORE = load_module("under_length_core", CORE_PATH)
RUNTIME = load_module("under_length_runtime", RUNTIME_PATH)


class UnderLengthCapabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.previous = {
            key: os.environ.get(key)
            for key in ("COW_GATE_HOOK_DATA", "COW_GATE_CAPABILITY")
        }
        os.environ["COW_GATE_HOOK_DATA"] = str(self.root / "data")
        os.environ["COW_GATE_CAPABILITY"] = "under_length"
        self.addCleanup(self.restore_environment)

    def restore_environment(self) -> None:
        for key, value in self.previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def event(self, name: str, **extra) -> dict:
        value = {
            "hook_event_name": name,
            "session_id": "under-session",
            "turn_id": "under-turn",
            "cwd": str(ROOT),
        }
        value.update(extra)
        return value

    def arm(self, request: str) -> None:
        CORE.handle(self.event("UserPromptSubmit", prompt=request))
        CORE.handle(
            self.event(
                "PostToolUse",
                tool_input={"cmd": f'Get-Content "{SKILL_PATH}"'},
                tool_response={"exit_code": 0},
            )
        )

    def record(self) -> dict:
        record_path = next((self.root / "data").rglob("under-turn.json"))
        return json.loads(record_path.read_text(encoding="utf-8"))

    def test_explicit_under_range_completes_hash_bound_d1(self) -> None:
        request = (
            "请起草80—140字通知。事实：组织业务培训，培训内容围绕日常业务，培训安排按既定计划进行；"
            "要求各部门统筹工作与学习，参训人员完成学习任务并学以致用，当前安排保持不变。只输出正文。"
        )
        d0 = "关于开展业务培训的通知\n\n各部门：\n现组织业务培训。"
        d1 = (
            "关于开展业务培训的通知\n\n各部门：\n现组织业务培训。培训内容围绕日常业务，培训安排按既定计划进行；"
            "各部门统筹工作与学习，参训人员完成学习任务并学以致用，当前安排保持不变。"
        )
        self.assertGreaterEqual(RUNTIME.count_text(d1, "full"), 80)
        self.arm(request)
        first = CORE.handle(self.event("Stop", stop_hook_active=False, last_assistant_message=d0))
        self.assertEqual("block", first["decision"])
        second = CORE.handle(self.event("Stop", last_assistant_message=d1))
        self.assertEqual("block", second["decision"])
        state = self.record()["under_length"]
        increments = state["increments"]
        verdict = {
            "schema_version": 1,
            "request_sha256": RUNTIME._sha256_text(request),
            "d0_sha256": RUNTIME._sha256_text(d0),
            "d1_sha256": RUNTIME._sha256_text(d1),
            "verdict": "PASS",
            "checks": {
                "no_new_specific_fact": True,
                "facts_and_states_preserved": True,
                "length_genre_and_naturalness_preserved": True,
            },
            "increments": [{**item, "category": "transparent_derivation"} for item in increments],
            "fact_ledger": self.valid_fact_ledger(request, d0, d1, increments),
        }
        third = CORE.handle(
            self.event("Stop", last_assistant_message=json.dumps(verdict, ensure_ascii=False))
        )
        self.assertIn(d1, third["reason"])
        final = CORE.handle(self.event("Stop", last_assistant_message=d1))
        self.assertTrue(final["continue"])
        redacted = self.record()
        self.assertTrue(redacted["under_length"]["audit"]["delivery_verified"])
        self.assertEqual(CORE.REDACTED_RECORD_STATE, redacted["data_retention_state"])
        self.assertNotIn("request", redacted)
        self.assertNotIn("original", redacted["under_length"])
        self.assertNotIn("candidate", redacted["under_length"])
        self.assertNotIn("increments", redacted["under_length"])

    @staticmethod
    def valid_fact_ledger(request, original, candidate, increments, quote=None):
        item = increments[0]
        quotes = [quote] if quote else [
            "培训安排按既定计划进行",
            "要求各部门统筹工作与学习，参训人员完成学习任务并学以致用，当前安排保持不变",
        ]
        frozen = RUNTIME._fact_ledger_template(request, original, increments)
        span_ids = [
            next(span["id"] for span in frozen["spans"] if source in span["quote"])
            for source in quotes
        ]
        roles = {
            "subject": {"source": "各部门", "candidate": "各部门", "relation": "same"},
            "object": {"source": "工作与学习", "candidate": "工作与学习", "relation": "same"},
            "predicate": {"source": "统筹", "candidate": "统筹", "relation": "same"},
            "status": {"source": "当前安排保持不变", "candidate": "当前安排保持不变", "relation": "same"},
            "intensity": {"source": "按既定计划", "candidate": "按既定计划", "relation": "same"},
        }
        return {
            "schema_version": RUNTIME.FACT_LEDGER_SCHEMA_VERSION,
            "ledger": [{"increment_id": item["id"], "span_ids": span_ids, **roles}],
        }

    def test_fact_ledger_rejects_real_but_unrelated_span(self) -> None:
        request = "材料载明办公室收到三份材料；要求各部门统筹工作与学习，参训人员完成学习任务并学以致用，当前安排保持不变。"
        original = "现组织业务培训。"
        candidate = "现组织业务培训。各部门统筹工作与学习，参训人员完成学习任务并学以致用，当前安排保持不变。"
        increments = RUNTIME._increment_items(original, candidate)
        quote = "办公室收到三份材料"
        packet = self.valid_fact_ledger(
            request, original, candidate, increments, quote=quote,
        )
        packet["ledger"][0]["subject"] = {"source": "办公室", "candidate": "组织", "relation": "same"}
        packet["ledger"][0]["object"] = {"source": "材料", "candidate": "参加", "relation": "same"}
        packet["ledger"][0]["predicate"] = {"source": "收到", "candidate": "参加", "relation": "same"}
        packet["ledger"][0]["status"] = {"source": "", "candidate": "", "relation": "same"}
        packet["ledger"][0]["intensity"] = {"source": "", "candidate": "", "relation": "same"}
        self.assertFalse(RUNTIME._fact_ledger_passes(packet, request, original, candidate, increments))

    def test_fact_ledger_rejects_related_span_with_new_predicate(self) -> None:
        request = "要求各部门统筹工作与学习。"
        original = "各部门统筹工作与学习。"
        candidate = "各部门统筹工作与学习并完成考核。"
        increments = RUNTIME._increment_items(original, candidate)
        quote = "要求各部门统筹工作与学习"
        packet = self.valid_fact_ledger(request, original, candidate, increments, quote=quote)
        packet["ledger"][0]["subject"] = {"source": "各部门", "candidate": "各部门", "relation": "same"}
        packet["ledger"][0]["object"] = {"source": "工作与学习", "candidate": "工作与学习", "relation": "same"}
        packet["ledger"][0]["predicate"] = {"source": "统筹", "candidate": "完成考核", "relation": "transparent_derivation"}
        packet["ledger"][0]["status"] = {"source": "", "candidate": "", "relation": "same"}
        packet["ledger"][0]["intensity"] = {"source": "", "candidate": "", "relation": "same"}
        self.assertFalse(RUNTIME._fact_ledger_passes(packet, request, original, candidate, increments))

    def test_fact_ledger_allows_authority_grounded_restatement(self) -> None:
        request = "组织业务培训，培训活动按计划开展。"
        original = "现组织业务培训。"
        candidate = "现组织业务培训。培训活动按计划组织。"
        increments = RUNTIME._increment_items(original, candidate)
        quote = "组织业务培训，培训活动按计划开展"
        packet = self.valid_fact_ledger(request, original, candidate, increments, quote=quote)
        packet["ledger"][0]["subject"] = {"source": "培训活动", "candidate": "培训活动", "relation": "same"}
        packet["ledger"][0]["object"] = {"source": "", "candidate": "", "relation": "same"}
        packet["ledger"][0]["predicate"] = {"source": "开展", "candidate": "组织", "relation": "restatement"}
        packet["ledger"][0]["status"] = {"source": "", "candidate": "", "relation": "same"}
        packet["ledger"][0]["intensity"] = {"source": "按计划", "candidate": "按计划", "relation": "same"}
        self.assertTrue(RUNTIME._fact_ledger_passes(packet, request, original, candidate, increments))

    def test_fact_ledger_allows_grounded_low_strength_inference(self) -> None:
        request = "材料：办公系统高峰时段响应缓慢，技术排查认为资源承载压力较大，拟扩容系统资源，尚未批准。"
        original = "办公系统高峰时段响应缓慢，拟扩容系统资源，尚未批准。"
        candidate = "办公系统高峰时段响应缓慢，为缓解资源承载压力，拟扩容系统资源，尚未批准。"
        increments = RUNTIME._increment_items(original, candidate)
        quote = "资源承载压力较大，拟扩容系统资源，尚未批准"
        packet = self.valid_fact_ledger(request, original, candidate, increments, quote=quote)
        packet["ledger"][0]["subject"] = {
            "source": "资源", "candidate": "资源", "relation": "same"
        }
        packet["ledger"][0]["object"] = {
            "source": "承载压力", "candidate": "承载压力", "relation": "same"
        }
        packet["ledger"][0]["predicate"] = {
            "source": "压力较大", "candidate": "缓解", "relation": "reasonable_inference"
        }
        packet["ledger"][0]["status"] = {
            "source": "", "candidate": "", "relation": "same"
        }
        packet["ledger"][0]["intensity"] = {
            "source": "", "candidate": "", "relation": "same"
        }
        self.assertTrue(
            RUNTIME._fact_ledger_passes(packet, request, original, candidate, increments)
        )

    def test_fact_ledger_rejects_achieved_effect_laundered_as_inference(self) -> None:
        request = "材料：办公系统高峰时段响应缓慢；技术排查认为资源承载压力较大；信息中心拟扩容系统资源，方案尚未批准。"
        original = "办公系统高峰时段响应缓慢，信息中心拟扩容系统资源，方案尚未批准。"
        candidate = original + "扩容后系统响应速度已明显提升。"
        increments = RUNTIME._increment_items(original, candidate)
        frozen = RUNTIME._fact_ledger_template(request, original, increments)
        authority = next(span for span in frozen["spans"] if "拟扩容系统资源" in span["quote"])
        entry = frozen["ledger"][0]
        entry["span_ids"] = [authority["id"]]
        entry["subject"] = {"source": "系统", "candidate": "系统", "relation": "same"}
        entry["predicate"] = {
            "source": "拟扩容",
            "candidate": "已明显提升",
            "relation": "reasonable_inference",
        }
        entry["object"] = {
            "source": "系统资源",
            "candidate": "系统响应速度",
            "relation": "reasonable_inference",
        }

        self.assertFalse(
            RUNTIME._fact_ledger_passes(
                RUNTIME._compact_fact_ledger_response(frozen),
                request,
                original,
                candidate,
                increments,
            )
        )

    def test_verifier_instruction_does_not_require_verbatim_effect_wording(self) -> None:
        request = "将材料扩写到70—90字：系统高峰响应缓慢，资源承载压力较大，拟扩容但尚未批准。"
        original = "系统高峰响应缓慢，拟扩容但尚未批准。"
        candidate = "系统高峰响应缓慢，为缓解资源承载压力拟扩容，但尚未批准。"
        spec = {"minimum": 70, "maximum": 90, "scope": "full"}
        instruction = RUNTIME._verdict_instruction(
            request, original, candidate, spec,
            RUNTIME._increment_items(original, candidate),
        )

        self.assertIsNotNone(instruction)
        self.assertIn("不要求这些推断逐字出现在材料中", instruction)
        self.assertIn("把预期写成已经取得的成效", instruction)
        self.assertIn("核心角色的 source 应从同一条直接事实", instruction)
        self.assertIn("不要把用户允许推断、允许措辞或强度说明本身填作核心 source", instruction)
        self.assertNotIn("材料未写明的场景、原因、目的、作用、影响", instruction)

    def test_fact_ledger_prompt_prepopulates_one_complete_entry_per_increment(self) -> None:
        request = "材料：培训面向窗口工作人员，内容为系统操作，具体时间尚未确定。"
        original = "办公室拟组织业务培训。"
        candidate = original + "培训面向窗口工作人员，内容为系统操作，具体时间尚未确定。"
        increments = RUNTIME._increment_items(original, candidate)
        packet = RUNTIME._fact_ledger_template(request, original, increments)

        self.assertEqual(len([item for item in increments if item.get("d1_text")]), len(packet["ledger"]))
        self.assertGreater(len(packet["spans"]), 1)
        for entry in packet["ledger"]:
            self.assertEqual([], entry["span_ids"])
            self.assertIn(entry["increment_id"], {item["id"] for item in increments})
            self.assertEqual(
                {"increment_id", "span_ids", "subject", "object", "predicate", "status", "intensity"},
                set(entry),
            )
            self.assertEqual(
                {"source", "candidate", "relation"},
                set(entry["predicate"]),
            )
            self.assertEqual(
                {"source": "", "candidate": "", "relation": "same"},
                entry["status"],
            )
        for span in packet["spans"]:
            source = request if span["origin"] == "request" else original
            self.assertEqual(span["quote"], source[span["start"]:span["end"]])
            self.assertEqual(RUNTIME._sha256_text(span["quote"]), span["sha256"])

    def test_verifier_exposes_only_compact_span_catalog(self) -> None:
        request = "材料：办公系统高峰时段响应缓慢；资源承载压力较大；拟扩容系统资源；尚未批准。请扩写到70—90字。"
        original = "办公系统高峰时段响应缓慢，拟扩容系统资源，尚未批准。"
        candidate = "办公系统高峰时段响应缓慢，为缓解资源承载压力，拟扩容系统资源，尚未批准。"
        increments = RUNTIME._increment_items(original, candidate)
        frozen = RUNTIME._fact_ledger_template(request, original, increments)
        compact = RUNTIME._compact_fact_ledger_response(frozen)
        catalog = RUNTIME._compact_span_catalog(frozen)
        instruction = RUNTIME._verdict_instruction(
            request,
            original,
            candidate,
            {"minimum": 70, "maximum": 90, "scope": "full"},
            increments,
        )

        self.assertEqual({"schema_version", "ledger"}, set(compact))
        self.assertTrue(catalog)
        self.assertTrue(all(set(item) == {"id", "quote"} for item in catalog))
        self.assertIsNotNone(instruction)
        catalog_text = instruction.split("【冻结来源目录】\n", 1)[1].split(
            "\n【D1】", 1
        )[0]
        self.assertNotIn('"origin"', catalog_text)
        self.assertNotIn('"start"', catalog_text)
        self.assertNotIn('"end"', catalog_text)
        self.assertNotIn('"sha256"', catalog_text)
        self.assertEqual(len(catalog), len(catalog_text.splitlines()))
        self.assertTrue(all("\t" in line for line in catalog_text.splitlines()))
        self.assertTrue(all("sha256" in span for span in frozen["spans"]))

    def test_prehashed_spans_support_grounded_inference_without_tools(self) -> None:
        request = "材料：办公系统高峰时段响应缓慢；技术排查认为资源承载压力较大；拟扩容系统资源；尚未批准。"
        original = "办公系统高峰时段响应缓慢，拟扩容系统资源，尚未批准。"
        candidate = "办公系统高峰时段响应缓慢，为缓解资源承载压力，拟扩容系统资源，尚未批准。"
        increments = RUNTIME._increment_items(original, candidate)
        packet = RUNTIME._fact_ledger_template(request, original, increments)
        pressure = next(
            span for span in packet["spans"]
            if "资源承载压力较大" in span["quote"]
        )
        entry = packet["ledger"][0]
        entry["span_ids"] = [pressure["id"]]
        entry["subject"] = {"source": "资源", "candidate": "资源", "relation": "same"}
        entry["object"] = {"source": "承载压力", "candidate": "承载压力", "relation": "same"}
        entry["predicate"] = {
            "source": "压力较大", "candidate": "缓解", "relation": "reasonable_inference"
        }
        entry["status"] = {"source": "", "candidate": "", "relation": "same"}
        entry["intensity"] = {"source": "", "candidate": "", "relation": "same"}

        compact = RUNTIME._compact_fact_ledger_response(packet)
        self.assertTrue(
            RUNTIME._fact_ledger_passes(compact, request, original, candidate, increments)
        )

    def test_fact_ledger_rejects_cross_span_predicate_backing(self) -> None:
        request = "要求各部门统筹工作与学习；培训安排继续组织。"
        original = "各部门统筹工作与学习。"
        candidate = "各部门统筹工作与学习并组织培训。"
        increments = RUNTIME._increment_items(original, candidate)
        quote = "要求各部门统筹工作与学习"
        packet = self.valid_fact_ledger(request, original, candidate, increments, quote=quote)
        packet["ledger"][0]["subject"] = {"source": "各部门", "candidate": "各部门", "relation": "same"}
        packet["ledger"][0]["object"] = {"source": "工作与学习", "candidate": "工作与学习", "relation": "same"}
        packet["ledger"][0]["predicate"] = {"source": "统筹", "candidate": "组织", "relation": "restatement"}
        packet["ledger"][0]["status"] = {"source": "", "candidate": "", "relation": "same"}
        packet["ledger"][0]["intensity"] = {"source": "", "candidate": "", "relation": "same"}
        self.assertFalse(RUNTIME._fact_ledger_passes(packet, request, original, candidate, increments))

    def test_fact_ledger_rejects_actor_action_object_stitched_across_spans(self) -> None:
        request = "我单位组织业务培训；各部门统筹工作与学习。"
        original = "当前安排保持不变。"
        candidate = "当前安排保持不变。各部门组织业务培训。"
        increments = RUNTIME._increment_items(original, candidate)
        frozen = RUNTIME._fact_ledger_template(request, original, increments)
        organization = next(span for span in frozen["spans"] if "我单位组织业务培训" in span["quote"])
        departments = next(span for span in frozen["spans"] if "各部门统筹工作与学习" in span["quote"])
        entry = frozen["ledger"][0]
        entry["span_ids"] = [organization["id"], departments["id"]]
        entry["subject"] = {"source": "各部门", "candidate": "各部门", "relation": "same"}
        entry["object"] = {"source": "业务培训", "candidate": "业务培训", "relation": "same"}
        entry["predicate"] = {"source": "组织", "candidate": "组织", "relation": "same"}

        self.assertFalse(
            RUNTIME._fact_ledger_passes(
                RUNTIME._compact_fact_ledger_response(frozen),
                request,
                original,
                candidate,
                increments,
            )
        )

    def test_fact_ledger_allows_actor_action_object_from_one_span(self) -> None:
        request = "各部门组织业务培训，并统筹工作与学习。"
        original = "当前安排保持不变。"
        candidate = "当前安排保持不变。各部门组织业务培训。"
        increments = RUNTIME._increment_items(original, candidate)
        frozen = RUNTIME._fact_ledger_template(request, original, increments)
        authority = next(span for span in frozen["spans"] if "各部门组织业务培训" in span["quote"])
        entry = frozen["ledger"][0]
        entry["span_ids"] = [authority["id"]]
        entry["subject"] = {"source": "各部门", "candidate": "各部门", "relation": "same"}
        entry["object"] = {"source": "业务培训", "candidate": "业务培训", "relation": "same"}
        entry["predicate"] = {"source": "组织", "candidate": "组织", "relation": "same"}

        self.assertTrue(
            RUNTIME._fact_ledger_passes(
                RUNTIME._compact_fact_ledger_response(frozen),
                request,
                original,
                candidate,
                increments,
            )
        )

    def test_fact_ledger_allows_registered_safe_predicate_restatement(self) -> None:
        request = "材料：培训活动按计划开展；培训面向窗口工作人员；具体时间尚未确定。"
        original = "培训活动按计划开展。"
        candidate = "培训活动按计划进行。"
        increments = RUNTIME._increment_items(original, candidate)
        frozen = RUNTIME._fact_ledger_template(request, original, increments)
        authority = next(span for span in frozen["spans"] if "培训活动按计划开展" in span["quote"])
        entry = frozen["ledger"][0]
        entry["span_ids"] = [authority["id"]]
        entry["predicate"] = {"source": "开展", "candidate": "进行", "relation": "restatement"}

        self.assertTrue(
            RUNTIME._fact_ledger_passes(
                RUNTIME._compact_fact_ledger_response(frozen),
                request,
                original,
                candidate,
                increments,
            )
        )

    def test_fact_ledger_rejects_unregistered_state_upgrade_as_restatement(self) -> None:
        request = "材料：培训活动按计划开展；具体时间尚未确定。"
        original = "培训活动按计划开展。"
        candidate = "培训活动按计划完成。"
        increments = RUNTIME._increment_items(original, candidate)
        frozen = RUNTIME._fact_ledger_template(request, original, increments)
        authority = next(span for span in frozen["spans"] if "培训活动按计划开展" in span["quote"])
        entry = frozen["ledger"][0]
        entry["span_ids"] = [authority["id"]]
        entry["predicate"] = {"source": "开展", "candidate": "完成", "relation": "restatement"}

        self.assertFalse(
            RUNTIME._fact_ledger_passes(
                RUNTIME._compact_fact_ledger_response(frozen),
                request,
                original,
                candidate,
                increments,
            )
        )

    def test_compact_fact_ledger_rejects_unknown_span_id(self) -> None:
        request = "要求各部门统筹工作与学习。"
        original = "各部门统筹工作与学习。"
        candidate = "各部门统筹工作与学习并完成考核。"
        increments = RUNTIME._increment_items(original, candidate)
        packet = self.valid_fact_ledger(
            request,
            original,
            candidate,
            increments,
            quote="要求各部门统筹工作与学习",
        )
        packet["ledger"][0]["span_ids"] = ["R999"]
        self.assertFalse(
            RUNTIME._fact_ledger_passes(
                packet, request, original, candidate, increments
            )
        )

    def test_within_range_material_quote_review_and_opt_out_do_not_start(self) -> None:
        within = "内容" * 70
        for index, request in enumerate(
            (
                "请起草100—180字通知，只输出正文。",
                "请解释制度中正文不少于100字的含义。",
                "请审核这份100—180字通知，不要改正文。",
                "请起草100—180字通知，本次关闭 Hook。",
            )
        ):
            with self.subTest(request=request):
                event = {"session_id": f"s{index}", "turn_id": f"t{index}", "cwd": str(ROOT)}
                CORE.handle({**event, "hook_event_name": "UserPromptSubmit", "prompt": request})
                CORE.handle(
                    {
                        **event,
                        "hook_event_name": "PostToolUse",
                        "tool_input": {"cmd": f'Get-Content "{SKILL_PATH}"'},
                        "tool_response": {"exit_code": 0},
                    }
                )
                result = CORE.handle(
                    {**event, "hook_event_name": "Stop", "stop_hook_active": False, "last_assistant_message": within}
                )
                record_path = next((self.root / "data").rglob(f"t{index}.json"))
                record = json.loads(record_path.read_text(encoding="utf-8"))
                self.assertNotIn("under_length", record)
                if "关闭 Hook" in request:
                    self.assertTrue(result["continue"])

    def test_explicit_permission_to_miss_lower_bound_does_not_start(self) -> None:
        request = (
            "请起草800—900字通知。材料不足时宁可短于下限，不得重复凑字。"
        )
        self.arm(request)
        result = CORE.handle(
            self.event(
                "Stop",
                stop_hook_active=False,
                last_assistant_message="会议通知\n\n各部门：\n定于明日召开会议。特此通知。",
            )
        )
        self.assertIsInstance(result, dict)
        record = self.record()
        self.assertNotIn("under_length", record)
        self.assertEqual("user_allows_shortfall", record["under_length_bypass"])

    def test_material_explanation_is_not_an_output_length_spec(self) -> None:
        self.assertIsNone(RUNTIME.parse_spec("请解释制度中正文不少于100字的含义。"))
        self.assertEqual(
            {"minimum": 280, "maximum": 360, "scope": "full"},
            RUNTIME.parse_spec("请根据材料起草一篇280—360字的新闻消息，只输出正文。"),
        )

    def test_natural_comma_separated_length_specs_are_recognized(self) -> None:
        self.assertEqual(
            {"minimum": 350, "maximum": 450, "scope": "body"},
            RUNTIME.parse_spec(
                "请根据材料起草一份采购请示，只输出正文，350—450字。"
            ),
        )
        self.assertEqual(
            {"minimum": 450, "maximum": 550, "scope": "full"},
            RUNTIME.parse_spec(
                "请根据材料起草一段年度工作总结中的整章总结，450—550字，只输出正文。"
            ),
        )
        self.assertIsNone(
            RUNTIME.parse_spec(
                "请起草情况说明，材料正文300—400字，请压缩材料中的重复表述。"
            )
        )

    def test_mechanical_gate_rejects_new_number_and_status_upgrade(self) -> None:
        spec = {"minimum": 1, "maximum": 0, "scope": "full"}
        self.assertEqual(
            "under_length_number_added_dropped_or_changed",
            RUNTIME.mechanical_reason("正在核查。", "正在核查，共3项。", spec, ""),
        )
        self.assertEqual(
            "under_length_status_upgraded",
            RUNTIME.mechanical_reason("事项正在核查。", "事项核查完成。", spec, ""),
        )

    def test_request_supplied_numbers_and_transparent_count_reach_semantic_verifier(self) -> None:
        spec = {"minimum": 1, "maximum": 0, "scope": "full"}
        request = "起草800—900字通知。会议时间为9月15日9时，议程共四项。"
        original = "会议定于9月15日9时召开。议程如下。"
        candidate = "会议定于9月15日9时召开。本次议程共四项，具体如下。"
        self.assertIsNone(RUNTIME.mechanical_reason(original, candidate, spec, request))
        self.assertEqual(
            "under_length_number_added_dropped_or_changed",
            RUNTIME.mechanical_reason(original, candidate + "共3个环节。", spec, request),
        )

    def test_planned_improvement_equivalent_is_not_mechanically_rejected(self) -> None:
        spec = {"minimum": 1, "maximum": 0, "scope": "full"}
        original = "下一年度拟完善培训安排。"
        candidate = "将在下一年度改进培训安排，并结合既有工作逐步优化培训内容。"
        self.assertIsNone(RUNTIME.mechanical_reason(original, candidate, spec, ""))

    def test_unsupported_added_process_is_rejected_but_request_grounded_action_is_allowed(self) -> None:
        original = "会议安排四项议程。"
        unsafe = "会议安排四项议程。请各部门提前通知参会人员，并保持通讯畅通。"
        unsafe_items = RUNTIME._increment_items(original, unsafe)
        self.assertEqual(
            "under_length_unsupported_added_process",
            RUNTIME._unsupported_added_process("会议安排四项议程。", original, unsafe_items),
        )

        request = "会议安排四项议程，请各部门提前通知参会人员。"
        grounded = original + "请各部门提前通知参会人员。"
        grounded_items = RUNTIME._increment_items(original, grounded)
        self.assertIsNone(
            RUNTIME._unsupported_added_process(request, original, grounded_items)
        )

    def test_ongoing_investigation_equivalent_reaches_semantic_verifier(self) -> None:
        spec = {"minimum": 1, "maximum": 0, "scope": "full"}
        original = "目前，事故原因正在调查中。"
        candidate = "目前，事故原因正在进一步调查中，相关情况将根据调查进展说明。"
        self.assertIsNone(RUNTIME.mechanical_reason(original, candidate, spec, ""))
