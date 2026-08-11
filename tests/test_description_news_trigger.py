from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_SKILL_PATHS = [
    ROOT / "chinese-official-writing" / "SKILL.md",
    ROOT / "skills" / "chinese-official-writing" / "SKILL.md",
    ROOT / ".agents" / "skills" / "chinese-official-writing" / "SKILL.md",
    ROOT / ".qwen" / "skills" / "chinese-official-writing" / "SKILL.md",
    ROOT / "hermes" / "skills" / "chinese-official-writing" / "SKILL.md",
]
FROZEN_OPENCLAW_SKILL = (
    ROOT / "openclaw" / "skills" / "chinese_official_writing" / "SKILL.md"
)


def read_description(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^description: (.+)$", text, re.M)
    if match is None:
        raise AssertionError(f"missing description: {path}")
    return match.group(1)


class DescriptionNewsTriggerTests(unittest.TestCase):
    def test_active_description_is_concise_and_news_first(self) -> None:
        descriptions = [read_description(path) for path in ACTIVE_SKILL_PATHS]
        self.assertEqual(len(set(descriptions)), 1)

        description = descriptions[0]
        self.assertTrue(
            description.startswith(
                "用于中文公文、新闻稿件和机关企事业单位、学校等正式事务材料的起草、改写、压缩和复核；"
            )
        )
        self.assertIn("新闻稿、新闻消息、快讯、活动报道", description)
        self.assertIn("不用于英文、文学、营销、社媒、论文或个人求职。", description)
        self.assertIn("机关企事业单位、学校等", description)
        self.assertIn("个人求职", description)

    def test_openclaw_description_stays_on_frozen_release(self) -> None:
        description = read_description(FROZEN_OPENCLAW_SKILL)
        self.assertNotIn("中文公文、新闻稿件和机关企事业单位", description)


if __name__ == "__main__":
    unittest.main()
