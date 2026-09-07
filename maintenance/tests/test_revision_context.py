"""Bounded native lineage, source precedence, and cleanup input boundaries."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "revision_context_test", ROOT / "chinese-official-writing/hooks/shared/revision_context.py"
)
CONTEXT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTEXT)


class RevisionContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "session.jsonl"
        self.skill = self.root / "skill"
        self.prompts = ["请根据材料写报告：已纳入190项。", "请修改刚才的报告，更正为205项，给我完整稿。"]

    def rows(self, error=False):
        def row(role, content):
            return {"sessionId": "session", "type": role, "message": {"content": content}}
        return [row("user", self.prompts[0]),
                row("assistant", [{"type": "tool_use", "id": "read1", "name": "Read", "input": {"file_path": str(self.skill / "SKILL.md")}}]),
                row("user", [{"type": "tool_result", "tool_use_id": "read1", "is_error": error, "content": "skill"}]),
                row("assistant", "虚构主体已完成审核。"), row("user", self.prompts[1])]

    def recover(self, rows, prompt=None, session="session"):
        self.path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
        return CONTEXT.recover(self.path, session, prompt or self.prompts[-1], self.skill)

    def test_user_only_chronology_and_successful_read(self):
        context = self.recover(self.rows())
        self.assertEqual(context["turn_count"], 2)
        self.assertNotIn("虚构主体", context["source_text"])
        self.assertLess(context["source_text"].index("190"), context["source_text"].index("205"))
        self.assertIn("后续明确更正、删除替代", context["source_text"])
        self.assertIsNone(self.recover(self.rows(error=True)))
        rows = self.rows()
        rows[1]["message"]["content"][0].update(
            name="Bash", input={"command": f'echo "{self.skill}/SKILL.md"'}
        )
        self.assertIsNone(self.recover(rows))
        rows = self.rows()
        rows[1]["message"]["content"][0]["input"]["file_path"] = str(self.skill / ".." / "other" / "SKILL.md")
        self.assertIsNone(self.recover(rows))

    def test_session_current_turn_and_new_task_boundaries(self):
        self.assertIsNone(self.recover(self.rows(), session="another"))
        self.assertIsNone(self.recover(self.rows(), prompt="请修改刚才的报告，全文删除。"))
        rows = self.rows()
        rows[-1]["message"]["content"] = "请另写一份报告。"
        self.assertIsNone(self.recover(rows, prompt="请另写一份报告。"))
        rows = self.rows()
        rows[1]["isSidechain"] = True
        self.assertIsNone(self.recover(rows))

    def test_bounded_input_and_incomplete_transcript(self):
        with patch.object(CONTEXT, "MAX_BYTES", 8):
            self.assertIsNone(self.recover(self.rows()))
        with patch.object(CONTEXT, "MAX_CHARS", 8):
            self.assertIsNone(self.recover(self.rows()))
        self.recover(self.rows())
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write("\n{")
        self.assertIsNone(CONTEXT.recover(self.path, "session", self.prompts[-1], self.skill))

    def test_ordinary_revision_phrases(self):
        cases = json.loads((ROOT / "maintenance/tests/evidence/natural-writing-stability-r1/cases.json").read_text(encoding="utf-8"))
        for case in cases["cases"]:
            self.assertFalse(CONTEXT.is_revision(case["rounds"][0]["prompt"]))
            for turn in case["rounds"][1:]:
                with self.subTest(prompt=turn["prompt"]):
                    self.assertTrue(CONTEXT.is_revision(turn["prompt"]))
        self.assertTrue(CONTEXT.is_revision("以刚才这版为底稿，再把下一步考虑改得更简洁一些。"))
        self.assertFalse(CONTEXT.is_revision("请另写一份报告，修改刚才的结构。"))
        self.assertFalse(CONTEXT.is_revision("这个任务已经结束，请删掉刚才的临时文件。"))
        self.assertFalse(CONTEXT.is_revision("刚才的报告已经定稿。请删除临时文件。"))
        self.assertTrue(CONTEXT.is_revision("刚才的报告已定稿，但请把日期更正为9月6日。"))
        self.assertTrue(CONTEXT.is_revision("请据此更新报告，其他内容保留。"))
        self.assertFalse(CONTEXT.is_revision("请修改下面这份报告，给我完整正文。\n\n乙校的新材料。"))
        self.assertFalse(CONTEXT.is_revision("请修改这份报告，给我完整正文。"))

    def test_core_binds_source_input_and_redacts_it(self):
        spec = importlib.util.spec_from_file_location(
            "revision_source_core", ROOT / "chinese-official-writing/hooks/core/gate_stop_hook.py"
        )
        core = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(core)
        self.skill = core.SKILL_ROOT
        self.recover(self.rows())
        event = {"hook_event_name": "UserPromptSubmit", "session_id": "session", "turn_id": "2",
                 "cwd": str(self.root), "prompt": self.prompts[-1]}
        with patch.dict("os.environ", {"COW_GATE_HOOK_DATA": str(self.root / "data")}):
            core.handle(event)
            record_path = core._record_path(event)
            record = core._read_json(record_path)
            core._bind_revision_context(
                {**event, "hook_event_name": "Stop", "stop_hook_active": False,
                 "revision_transcript": {"format": "claude-code", "path": str(self.path)}},
                record_path, record,
            )
            self.assertTrue(record["skill_seen"])
            inputs = self.root / "inputs"
            self.assertTrue(core._write_bootstrap_inputs(record_path, record, inputs, record["request"], "正文"))
            self.assertEqual((inputs / "source.txt").read_text(encoding="utf-8"), record["source_text"])
            # Terminal record minimization must not retain recovered raw materials.
            record["bypass"] = "user_requested"
            core._write_record(record_path, record)
            core.handle({**event, "hook_event_name": "Stop", "last_assistant_message": "正文", "stop_hook_active": False})
            saved = core._read_json(record_path)
            self.assertNotIn("source_text", saved)
            self.assertNotIn("request", saved)
            self.assertEqual(saved["revision_context"]["turn_count"], 2)


if __name__ == "__main__":
    unittest.main()
