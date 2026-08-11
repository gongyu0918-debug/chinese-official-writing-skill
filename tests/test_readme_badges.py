from __future__ import annotations

from pathlib import Path
from urllib.parse import parse_qs, urlparse
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
SKILLHUB_DETAIL_URL = "https://skillhub.cn/skills/chinese-official-writing"
SKILLHUB_API_URL = "https://api.skillhub.cn/api/v1/skills/chinese-official-writing"


class ReadmeBadgeTests(unittest.TestCase):
    def test_skillhub_badge_reads_downloads_and_links_to_detail_page(self) -> None:
        readme = README.read_text(encoding="utf-8")
        match = re.search(r"\[!\[SkillHub downloads\]\(([^)]+)\)\]\(([^)]+)\)", readme)

        self.assertIsNotNone(match)
        badge_url, detail_url = match.groups()
        parsed = urlparse(badge_url)
        query = parse_qs(parsed.query)

        self.assertEqual("img.shields.io", parsed.netloc)
        self.assertEqual("/badge/dynamic/json", parsed.path)
        self.assertEqual([SKILLHUB_API_URL], query["url"])
        self.assertEqual(["$.skill.stats.downloads"], query["query"])
        self.assertEqual(["SkillHub downloads"], query["label"])
        self.assertEqual(["3600"], query["cacheSeconds"])
        self.assertEqual(SKILLHUB_DETAIL_URL, detail_url)
        self.assertNotIn("installs", badge_url)
        self.assertNotRegex(badge_url, r"37341|53|44")


if __name__ == "__main__":
    unittest.main()
