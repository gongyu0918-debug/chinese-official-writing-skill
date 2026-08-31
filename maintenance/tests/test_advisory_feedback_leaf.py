from __future__ import annotations

from pathlib import Path
import unittest

from maintenance.tests.hook_companion_support import HookCompanionTestMixin


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "chinese-official-writing"
LEAF = Path("references/genre-playbook-advisory-feedback.md")
FORMAT = Path("references/format-gbt9704.md")
PERSISTENT_MIRRORS = (
    ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing",
    ROOT / "packages" / "qwen-code" / "skills" / "chinese-official-writing",
    ROOT / "packages" / "qwenwork" / "skills" / "chinese-official-writing",
    ROOT / "packages" / "hermes" / "skills" / "chinese-official-writing",
    ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing",
)


class AdvisoryFeedbackLeafTests(HookCompanionTestMixin, unittest.TestCase):
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

    def test_direct_route_keeps_cooperative_feedback_separate_from_power_guidance(self) -> None:
        skill = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("直达 `references/genre-playbook-advisory-feedback.md`", skill)
        self.assertIn("正式下行指导意见、监督检查意见、安全整改意见和审计纪检建议", skill)

    def test_leaf_preserves_grounded_courtesy_authority_and_common_grouping(self) -> None:
        text = (CANONICAL / LEAF).read_text(encoding="utf-8")

        self.assertIn("有依据的肯定或礼貌铺垫", text)
        self.assertIn("不为“先夸”编造成绩", text)
        self.assertIn("只有被建议方有处置权", text)
        self.assertIn("同一成因、同一处置权和同一处理路径", text)
        self.assertIn("按共性问题或有权主体归并", text)
        self.assertIn("建议审核部门研究明确", text)
        self.assertIn("建议平台建设运营方研究优化", text)

    def test_heading_and_docx_title_rules_are_narrow(self) -> None:
        leaf = (CANONICAL / LEAF).read_text(encoding="utf-8")
        format_text = (CANONICAL / FORMAT).read_text(encoding="utf-8")

        self.assertIn("小标题独立成段，末尾不加句号，正文另起", leaf)
        self.assertIn("段首题、编号正文句或用户模板明确接排时仍按正文标点处理", format_text)
        self.assertIn("显式取消首行、左侧和右侧缩进", format_text)

    def test_leaf_and_format_rule_match_all_public_and_companion_mirrors(self) -> None:
        for relative in (LEAF, FORMAT):
            canonical = (CANONICAL / relative).read_bytes()
            for mirror in self.mirror_roots:
                with self.subTest(relative=relative, mirror=mirror):
                    self.assertEqual((mirror / relative).read_bytes(), canonical)

    def test_candidate_status_is_registered_without_an_active_hold(self) -> None:
        requirements = (ROOT / "maintenance/specs/requirements.md").read_text(encoding="utf-8")
        coverage = (ROOT / "maintenance/specs/coverage.md").read_text(encoding="utf-8")
        roadmap = (ROOT / "maintenance/specs/roadmap.md").read_text(encoding="utf-8")
        todo = (ROOT / "maintenance/docs/待办.md").read_text(encoding="utf-8")
        evidence = (ROOT / "maintenance/docs/evidence/README.md").read_text(encoding="utf-8")
        result = (ROOT / "maintenance/tests/evidence/advisory-feedback-tone-r1/result.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("### WR-025 合作性意见建议与建议反馈", requirements)
        self.assertIn("`WR-025` 合作性意见建议与建议反馈", coverage)
        self.assertIn("`WR-008b` 并列小标题与 DOCX 主标题缩进", coverage)
        self.assertIn("NEXT_VERSION_CANDIDATE_NOT_MERGED", roadmap)
        self.assertIn("`WR-025 / WR-008b`", todo)
        self.assertIn("advisory-feedback-tone-r1/result.md", evidence)
        self.assertIn("R4_R5_R6_TERMINATED", result)
        self.assertIn("无活动 `HOLD`", result)


if __name__ == "__main__":
    unittest.main()
