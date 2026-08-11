from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
ACTIVE_SKILL_PATHS = [
    ROOT / "chinese-official-writing" / "SKILL.md",
    ROOT / "packages" / "agent-plugin" / "skills" / "chinese-official-writing" / "SKILL.md",
    ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing" / "SKILL.md",
    ROOT / "packages" / "qwen-code" / "skills" / "chinese-official-writing" / "SKILL.md",
    ROOT / "packages" / "hermes" / "skills" / "chinese-official-writing" / "SKILL.md",
]
OPENCLAW_SKILL = (
    ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing" / "SKILL.md"
)


def read_description(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^description: (.+)$", text, re.M)
    if match is None:
        raise AssertionError(f"missing description: {path}")
    return match.group(1)


class DescriptionNewsTriggerTests(unittest.TestCase):
    def test_active_description_leads_with_capability_and_defers_audience(self) -> None:
        descriptions = [read_description(path) for path in ACTIVE_SKILL_PATHS]
        self.assertEqual(len(set(descriptions)), 1)

        description = descriptions[0]
        self.assertTrue(
            description.startswith(
                "用于中文公文、事务性材料和新闻稿件的起草、改写、压缩和复核；"
            )
        )
        self.assertIn("新闻稿、新闻消息、快讯、活动报道", description)
        self.assertIn("不用于英文、文学、营销、社媒、论文或个人求职。", description)
        self.assertIn("适用于机关、企事业单位、学校、新闻机构。", description)
        self.assertIn("个人求职", description)
        self.assertEqual(len(description), 280)

    def test_openclaw_description_tracks_current_canonical_capability(self) -> None:
        self.assertEqual(read_description(ACTIVE_SKILL_PATHS[0]), read_description(OPENCLAW_SKILL))


if __name__ == "__main__":
    unittest.main()
