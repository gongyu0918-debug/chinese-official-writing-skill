from __future__ import annotations

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
PERSISTENT_SKILL_PATHS = [
    ROOT / "chinese-official-writing" / "SKILL.md",
    ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing" / "SKILL.md",
    ROOT / "packages" / "qwen-code" / "skills" / "chinese-official-writing" / "SKILL.md",
    ROOT / "packages" / "hermes" / "skills" / "chinese-official-writing" / "SKILL.md",
]
OPENCLAW_SKILL = (
    ROOT / "packages" / "openclaw" / "skills" / "chinese_official_writing" / "SKILL.md"
)


def read_description(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    frontmatter = re.match(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", text, re.S)
    if frontmatter is None:
        raise AssertionError(f"missing or unclosed frontmatter: {path}")
    descriptions = re.findall(r"^description:[ \t]*(.*)$", frontmatter.group(1), re.M)
    if len(descriptions) != 1 or not descriptions[0].strip().strip("\"'").strip():
        raise AssertionError(f"expected one nonempty description: {path}")
    return descriptions[0].strip()


class DescriptionNewsTriggerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.active_skill_paths = PERSISTENT_SKILL_PATHS

    def test_active_descriptions_have_frontmatter_and_match(self) -> None:
        descriptions = [read_description(path) for path in self.active_skill_paths]
        self.assertEqual(len(set(descriptions)), 1)

    def test_openclaw_description_matches_canonical(self) -> None:
        self.assertEqual(read_description(self.active_skill_paths[0]), read_description(OPENCLAW_SKILL))


if __name__ == "__main__":
    unittest.main()
