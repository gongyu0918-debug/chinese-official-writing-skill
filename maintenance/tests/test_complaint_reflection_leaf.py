from __future__ import annotations

from pathlib import Path
import unittest

from maintenance.tests.hook_companion_support import HookCompanionTestMixin


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "chinese-official-writing"
LEAF = Path("references/genre-playbook-complaint-reflection.md")
PERSISTENT_MIRRORS = (
    ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing",
    ROOT / "packages" / "qwen-code" / "skills" / "chinese-official-writing",
    ROOT / "packages" / "qwenwork" / "skills" / "chinese-official-writing",
    ROOT / "packages" / "hermes" / "skills" / "chinese-official-writing",
    ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing",
)


class ComplaintReflectionLeafTests(HookCompanionTestMixin, unittest.TestCase):
    def setUp(self) -> None:
        self.setUpHookCompanions()
        self.mirror_roots = (
            *(
                self.companion_roots[host] / "skills/chinese-official-writing"
                for host in (
                    "codex",
                    "codebuddy",
                    "claude-code",
                    "zcode",
                    "qwen-code",
                    "kimi-code",
                )
            ),
            *PERSISTENT_MIRRORS,
        )

    def test_direct_route_is_separate_from_advisory_and_received_records(self) -> None:
        skill = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        leaf = (CANONICAL / LEAF).read_text(encoding="utf-8")
        formulaic_row = next(
            line for line in skill.splitlines() if line.startswith("| `references/formulaic-language.md`")
        )

        self.assertIn("直达 `references/genre-playbook-complaint-reflection.md`", skill)
        self.assertIn("以本人或本单位亲历方身份", skill)
        self.assertNotIn("情况反映", formulaic_row)
        self.assertNotIn("任务目的在于提出改进主张", leaf)
        self.assertNotIn("整理已收到事项及办理结果", leaf)

    def test_leaf_preserves_request_facts_state_and_first_party_scope(self) -> None:
        text = (CANONICAL / LEAF).read_text(encoding="utf-8")

        self.assertIn("投诉请求不等于解决建议", text)
        self.assertIn("请核实", text)
        self.assertIn("本人、本单位或材料明确覆盖的对象", text)
        self.assertIn("可以归纳材料直接支持的一层实际影响", text)
        self.assertIn("不得补材料未给的经济损失", text)
        self.assertIn("不判断对方违法、失职、故意拖延或服务态度", text)

    def test_leaf_locks_standalone_shape_and_direct_delivery(self) -> None:
        text = (CANONICAL / LEAF).read_text(encoding="utf-8")

        self.assertIn("标题原样置于正文首行", text)
        self.assertIn("不因`只输出正文`而省略", text)
        self.assertIn("不要顺势续写", text)
        self.assertIn("直接交付正文", text)
        self.assertIn("纯文本交付不使用 HTML 空格实体", text)
        self.assertNotIn("固定字数", text)

    def test_leaf_matches_all_public_and_companion_mirrors(self) -> None:
        canonical_leaf = (CANONICAL / LEAF).read_bytes()
        route = "直达 `references/genre-playbook-complaint-reflection.md`"
        for mirror in self.mirror_roots:
            with self.subTest(mirror=mirror):
                self.assertEqual((mirror / LEAF).read_bytes(), canonical_leaf)
                self.assertIn(route, (mirror / "SKILL.md").read_text(encoding="utf-8"))

    def test_candidate_status_and_evidence_are_registered(self) -> None:
        requirements = (ROOT / "maintenance/specs/requirements.md").read_text(encoding="utf-8")
        coverage = (ROOT / "maintenance/specs/coverage.md").read_text(encoding="utf-8")
        roadmap = (ROOT / "maintenance/specs/roadmap.md").read_text(encoding="utf-8")
        todo = (ROOT / "maintenance/docs/待办.md").read_text(encoding="utf-8")
        evidence = (ROOT / "maintenance/docs/evidence/README.md").read_text(encoding="utf-8")
        result = (
            ROOT / "maintenance/tests/evidence/complaint-reflection-r1/result.md"
        ).read_text(encoding="utf-8")

        self.assertIn("### WR-027 投诉与情况反映", requirements)
        self.assertIn("`WR-027` 投诉与情况反映", coverage)
        self.assertIn("WR-027", roadmap)
        self.assertIn("WR-027-COMPLAINT-REFLECTION-R2", todo)
        self.assertIn("complaint-reflection-r1/result.md", evidence)
        self.assertIn(
            "R2_REAL_WRITING_PASSED / ENGINEERING_VERIFIED / MERGED_MAIN_POST_V1.6.25_FROZEN",
            result,
        )
        self.assertIn("complaint-reflection-r1/main-merge.md", evidence)
        self.assertIn("冻结v1.6.25不变", (ROOT / "maintenance/tests/evidence/complaint-reflection-r1/main-merge.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
