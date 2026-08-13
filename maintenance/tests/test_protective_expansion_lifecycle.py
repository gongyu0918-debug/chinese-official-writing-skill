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
CONTRACT_PATH = ROOT / "chinese-official-writing/hooks/capabilities/protective_expansion/contract.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CORE = load_module("protective_lifecycle_core", CORE_PATH)
CONTRACT = load_module("protective_lifecycle_contract", CONTRACT_PATH)


def split_instruction(reason: str) -> tuple[dict, dict]:
    skeleton = reason.split("CLEAR 骨架如下：\n", 1)[1].split(
        "\nDELETE_SPANS 骨架", 1
    )[0]
    packet = reason.split("\n观察包如下：\n", 1)[1]
    return json.loads(skeleton), json.loads(packet)


class ProtectiveExpansionLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.cwd = self.root / "cwd"
        self.cwd.mkdir()
        self.plugin = self.root / "plugin"
        skill = self.plugin / "skills/chinese-official-writing"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: chinese-official-writing\n---\n", encoding="utf-8")
        self.previous = {key: os.environ.get(key) for key in ("COW_GATE_HOOK_DATA", "PLUGIN_ROOT", "COW_GATE_CAPABILITY")}
        os.environ["COW_GATE_HOOK_DATA"] = str(self.root / "data")
        os.environ["PLUGIN_ROOT"] = str(self.plugin)
        os.environ["COW_GATE_CAPABILITY"] = "protective_expansion"
        self.addCleanup(self.restore_environment)

    def restore_environment(self) -> None:
        for key, value in self.previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def event(self, name: str, **extra) -> dict:
        value = {"hook_event_name": name, "session_id": "s1", "turn_id": "t1", "cwd": str(self.cwd)}
        value.update(extra)
        return value

    def arm(self, request: str) -> None:
        CORE.handle(self.event("UserPromptSubmit", prompt=request))
        skill = self.plugin / "skills/chinese-official-writing/SKILL.md"
        CORE.handle(self.event("PostToolUse", tool_input={"cmd": f'Get-Content "{skill}"'}, tool_response={"exit_code": 0}))

    def start(self, request: str, draft: str) -> tuple[dict, dict, dict]:
        self.arm(request)
        result = CORE.handle(self.event("Stop", stop_hook_active=False, last_assistant_message=draft))
        self.assertEqual("block", result["decision"])
        response, packet = split_instruction(result["reason"])
        return result, response, packet

    def select(self, response: dict, packet: dict, target: str) -> dict:
        segment = next(item for item in packet["segments"] if item["text"] == target)
        response.update(
            {
                "decision": "DELETE_SPANS",
                "selections": [
                    {
                        "segment_id": segment["segment_id"],
                        "family": "serial_self_certification",
                        "reason": "当前题面只给出完成事实，该尾句没有独立正文作用。",
                        "assertions": {key: True for key in CONTRACT.REQUIRED_ASSERTIONS},
                    }
                ],
            }
        )
        return response

    def record(self) -> dict:
        value = CORE._read_json(CORE._record_path(self.event("Stop")))
        assert value is not None
        return value

    def test_dirty_draft_observation_exact_delete_and_echo(self) -> None:
        draft = "已归集9项意见。上述意见不构成修改，不表示条文已经调整，尚未形成修订方案。"
        _, response, packet = self.start("起草简报，只写已归集9项意见。", draft)
        response = self.select(response, packet, "上述意见不构成修改，不表示条文已经调整，尚未形成修订方案。")
        second = CORE.handle(self.event("Stop", stop_hook_active=True, last_assistant_message=json.dumps(response, ensure_ascii=False)))
        self.assertEqual("block", second["decision"])
        output = second["reason"].split("不要加说明：\n", 1)[1]
        self.assertEqual("已归集9项意见。", output)
        third = CORE.handle(self.event("Stop", stop_hook_active=True, last_assistant_message=output))
        self.assertTrue(third["continue"])
        record = self.record()
        self.assertEqual("complete", record["protective_phase"])
        self.assertTrue(record["protective_delivery_verified"])
        self.assertNotIn("txn", record)

    def test_clear_observation_echoes_original_and_completes_selected_capability(self) -> None:
        draft = "目前，异常原因尚未查明，技术人员正在核查。"
        _, response, _ = self.start("起草异常情况说明。", draft)
        second = CORE.handle(self.event("Stop", stop_hook_active=True, last_assistant_message=json.dumps(response, ensure_ascii=False)))
        self.assertIn(draft, second["reason"])
        third = CORE.handle(self.event("Stop", stop_hook_active=True, last_assistant_message=draft))
        self.assertTrue(third["continue"])
        self.assertNotIn("txn", self.record())

    def test_external_source_cue_forces_original_even_if_observer_selects(self) -> None:
        draft = "供应商尚未确定、验收尚未实施。"
        _, response, packet = self.start("根据附件起草采购情况说明。", draft)
        response = self.select(response, packet, draft)
        second = CORE.handle(self.event("Stop", stop_hook_active=True, last_assistant_message=json.dumps(response, ensure_ascii=False)))
        self.assertIn(draft, second["reason"])
        self.assertEqual("E0", self.record()["protective_selection"])

    def test_wrong_e1_falls_back_to_original_and_exact_original_allows(self) -> None:
        draft = "已完成32项变更。季度汇总不对业务规定是否合法作出评价。"
        _, response, packet = self.start("起草季度汇总，只写完成32项变更。", draft)
        response = self.select(response, packet, "季度汇总不对业务规定是否合法作出评价。")
        CORE.handle(self.event("Stop", stop_hook_active=True, last_assistant_message=json.dumps(response, ensure_ascii=False)))
        fallback = CORE.handle(self.event("Stop", stop_hook_active=True, last_assistant_message="错误回显"))
        self.assertIn(draft, fallback["reason"])
        allowed = CORE.handle(self.event("Stop", stop_hook_active=True, last_assistant_message=draft))
        self.assertTrue(allowed["continue"])

    def test_repeated_wrong_e0_delivers_bounded_failure_notice(self) -> None:
        draft = "目前，异常原因尚未查明，技术人员正在核查。"
        _, response, _ = self.start("起草异常情况说明。", draft)
        CORE.handle(self.event("Stop", stop_hook_active=True, last_assistant_message=json.dumps(response, ensure_ascii=False)))
        retry = CORE.handle(self.event("Stop", stop_hook_active=True, last_assistant_message="错一"))
        self.assertIn(draft, retry["reason"])
        failed = CORE.handle(self.event("Stop", stop_hook_active=True, last_assistant_message="错二"))
        self.assertIn("技术失败通知", failed["reason"])
        notice = failed["reason"].split("：\n", 1)[1]
        allowed = CORE.handle(self.event("Stop", stop_hook_active=True, last_assistant_message=notice))
        self.assertTrue(allowed["continue"])
        self.assertEqual("failed_closed", self.record()["protective_phase"])

    def test_opt_out_review_only_unread_and_disabled_create_no_protective_transaction(self) -> None:
        cases = (
            ("本次关闭 Hook，起草通知。", True, True),
            ("请审查这份稿件，不要代改。", True, True),
            ("起草通知。", False, True),
            ("起草通知。", True, False),
        )
        for index, (request, read_skill, selected) in enumerate(cases, start=1):
            with self.subTest(request=request, read_skill=read_skill, selected=selected):
                common = {"turn_id": f"case-{index}"}
                if not selected:
                    os.environ.pop("COW_GATE_CAPABILITY", None)
                CORE.handle(self.event("UserPromptSubmit", prompt=request, **common))
                if read_skill:
                    skill = self.plugin / "skills/chinese-official-writing/SKILL.md"
                    CORE.handle(self.event("PostToolUse", tool_input={"cmd": f'Get-Content "{skill}"'}, tool_response={"exit_code": 0}, **common))
                result = CORE.handle(self.event("Stop", stop_hook_active=False, last_assistant_message="通知正文。", **common))
                if not selected and read_skill:
                    self.assertEqual("block", result["decision"])
                else:
                    self.assertTrue(result["continue"])
                record_path = CORE._record_path(self.event("Stop", **common))
                record = CORE._read_json(record_path) if record_path else None
                self.assertNotIn("protective_txn", record or {})
                os.environ["COW_GATE_CAPABILITY"] = "protective_expansion"

    def test_external_material_read_forces_protective_original_selection(self) -> None:
        request = "起草项目进展情况说明。"
        self.arm(request)
        CORE.handle(
            self.event(
                "PostToolUse",
                tool_input={"cmd": 'Get-Content "C:\\materials\\progress.txt"'},
                tool_response={"exit_code": 0},
            )
        )
        result = CORE.handle(
            self.event(
                "Stop",
                stop_hook_active=False,
                last_assistant_message="项目按计划推进。验收尚未完成。",
            )
        )
        self.assertIn("观察包如下", result.get("reason", ""))
        response, packet = split_instruction(result["reason"])
        target = next(item for item in packet["segments"] if item["text"] == "验收尚未完成。")
        response = self.select(response, packet, target["text"])
        second = CORE.handle(
            self.event(
                "Stop",
                stop_hook_active=True,
                last_assistant_message=json.dumps(response, ensure_ascii=False),
            )
        )
        self.assertIn("项目按计划推进。验收尚未完成。", second["reason"])
        self.assertEqual("E0", self.record()["protective_selection"])

    def test_external_material_read_before_skill_is_still_recorded(self) -> None:
        request = "起草项目进展情况说明。"
        CORE.handle(self.event("UserPromptSubmit", prompt=request))
        CORE.handle(
            self.event(
                "PostToolUse",
                tool_input={"cmd": 'Get-Content "C:\\materials\\progress.txt"'},
                tool_response={"exit_code": 0},
            )
        )
        skill = self.plugin / "skills/chinese-official-writing/SKILL.md"
        CORE.handle(
            self.event(
                "PostToolUse",
                tool_input={"cmd": f'Get-Content "{skill}"'},
                tool_response={"exit_code": 0},
            )
        )
        result = CORE.handle(
            self.event(
                "Stop",
                stop_hook_active=False,
                last_assistant_message="项目按计划推进。验收尚未完成。",
            )
        )
        _, packet = split_instruction(result["reason"])
        self.assertEqual("external_material_observed", packet["authority_scope"])
        self.assertTrue(packet["authority_incomplete"])

    def test_runtime_loader_error_uses_exact_original_fallback(self) -> None:
        request = "起草情况说明。"
        self.arm(request)
        original_path = CORE.PROTECTIVE_RUNTIME_PATH
        try:
            CORE.PROTECTIVE_RUNTIME_PATH = self.root / "missing-runtime.py"
            draft = "已完成32项变更。"
            blocked = CORE.handle(
                self.event(
                    "Stop",
                    stop_hook_active=False,
                    last_assistant_message=draft,
                )
            )
            self.assertIn(draft, blocked["reason"])
            allowed = CORE.handle(
                self.event(
                    "Stop",
                    stop_hook_active=True,
                    last_assistant_message=draft,
                )
            )
            self.assertTrue(allowed["continue"])
            self.assertTrue(self.record()["protective_delivery_verified"])
        finally:
            CORE.PROTECTIVE_RUNTIME_PATH = original_path


if __name__ == "__main__":
    unittest.main()
