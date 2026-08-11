from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
SKILLHUB_DETAIL_URL = "https://skillhub.cn/skills/chinese-official-writing"
SKILLHUB_DOWNLOAD_BADGE_URL = (
    "https://img.shields.io/badge/SkillHub%20downloads-37k%2B-2f855a"
)


class ReadmeBadgeTests(unittest.TestCase):
    def test_skillhub_badge_uses_stable_download_floor_and_detail_link(self) -> None:
        readme = README.read_text(encoding="utf-8")
        expected = (
            f"[![SkillHub downloads: 37k+]({SKILLHUB_DOWNLOAD_BADGE_URL})]"
            f"({SKILLHUB_DETAIL_URL})"
        )

        self.assertEqual(1, readme.count(expected))
        self.assertNotIn("dynamic/json", readme)
        self.assertNotIn("inaccessible", readme.lower())
        self.assertNotIn("SkillHub installs", readme)


if __name__ == "__main__":
    unittest.main()
