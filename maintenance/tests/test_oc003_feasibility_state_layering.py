from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "chinese-official-writing"
MIRRORS = (
    ROOT / "packages/agent-skills/skills/chinese-official-writing",
    ROOT / "packages/hermes/skills/chinese-official-writing",
    ROOT / "packages/openclaw/skills/chinese_official_writing",
    ROOT / "packages/qwen-code/skills/chinese-official-writing",
)
REFERENCES = (
    "references/ai-compute-docs.md",
    "references/argument-chains.md",
    "references/genre-checklist-feasibility-review.md",
    "references/workflow.md",
)


class FeasibilityStateLayeringTests(unittest.TestCase):
    def test_conditional_advice_is_separate_from_factual_state(self) -> None:
        ai_compute = (CANONICAL / REFERENCES[0]).read_text(encoding="utf-8")
        argument = (CANONICAL / REFERENCES[1]).read_text(encoding="utf-8")
        review = (CANONICAL / REFERENCES[2]).read_text(encoding="utf-8")
        workflow = (CANONICAL / REFERENCES[3]).read_text(encoding="utf-8")

        self.assertIn("可以条件态提出一层", ai_compute)
        self.assertIn("建议与事实状态分开", ai_compute)
        self.assertIn("一层条件性建议与事实状态分开", argument)
        self.assertIn("只恢复该状态", review)
        self.assertIn("不改成“不具备”或“暂不具备”条件", review)
        self.assertIn("只以条件态提出研究建议，不写成既定流程", workflow)

    def test_four_public_mirrors_match_the_canonical_references(self) -> None:
        for relative in REFERENCES:
            canonical = (CANONICAL / relative).read_bytes()
            for mirror in MIRRORS:
                with self.subTest(relative=relative, mirror=mirror):
                    self.assertEqual((mirror / relative).read_bytes(), canonical)


if __name__ == "__main__":
    unittest.main()
