from __future__ import annotations

from pathlib import Path
import unittest

from maintenance.tests.hook_companion_support import HookCompanionTestMixin


ROOT = Path(__file__).resolve().parents[2]
PERSISTENT_RUNTIME_ROOTS = [
    ROOT / "chinese-official-writing",
    ROOT / "packages" / "agent-skills" / "skills" / "chinese-official-writing",
    ROOT / "packages" / "qwen-code" / "skills" / "chinese-official-writing",
    ROOT / "packages" / "hermes" / "skills" / "chinese-official-writing",
]


class ShungaoNaturalizationTests(HookCompanionTestMixin, unittest.TestCase):
    def setUp(self) -> None:
        self.setUpHookCompanions()
        self.runtime_roots = [
            PERSISTENT_RUNTIME_ROOTS[0],
            *[
                self.companion_roots[host] / "skills/chinese-official-writing"
                for host in ("codex", "codebuddy", "claude-code", "zcode")
            ],
            *PERSISTENT_RUNTIME_ROOTS[1:],
        ]

    def test_runtime_instructions_use_plain_editing_terms(self) -> None:
        for root in self.runtime_roots:
            texts = [root.joinpath("SKILL.md").read_text(encoding="utf-8")]
            texts.extend(path.read_text(encoding="utf-8") for path in root.joinpath("references").glob("*.md"))
            joined = "\n".join(texts)
            with self.subTest(root=root):
                self.assertNotIn("顺稿", joined)
                self.assertIn("润色修改", joined)

        canonical = ROOT / "chinese-official-writing"
        skill = canonical.joinpath("SKILL.md").read_text(encoding="utf-8")
        workflow = canonical.joinpath("references", "workflow.md").read_text(encoding="utf-8")
        review = canonical.joinpath("references", "review-checklist.md").read_text(encoding="utf-8")
        self.assertIn("压缩、润色修改或去口语化", skill)
        self.assertIn("先处理结构，再润色语言", workflow)
        self.assertIn("旧主送、旧金额、旧日期", canonical.joinpath("references", "proofreading-checklist.md").read_text(encoding="utf-8"))
        self.assertIn("润色修改、报告化或去口语化", review)


if __name__ == "__main__":
    unittest.main()
