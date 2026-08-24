from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
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

    def test_named_completeness_review_stops_before_option_library(self) -> None:
        skill = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        ai_compute = (CANONICAL / REFERENCES[0]).read_text(encoding="utf-8")
        review = (CANONICAL / REFERENCES[2]).read_text(encoding="utf-8")

        self.assertIn("本轮停在 `references/genre-checklist-feasibility-review.md`", skill)
        self.assertIn("不因出现上述术语或点名技术指标等缺项转读本页", skill)
        self.assertIn("解释某一具体技术主张", skill)
        self.assertIn("不自动叠加通用审稿页或去 AI 味页", skill)
        self.assertIn("不是只审既有摘要时的默认缺项清单", ai_compute)
        self.assertIn("只指出点名缺项及需补充的材料类别", ai_compute)
        self.assertIn("由现有事实直接支持的研究、风险控制或验证意见", review)
        self.assertIn("列出直接相关的指标类别、费用构成或依据类别", review)
        self.assertIn("不规定若干家或云端、自建、API 等比较路径", review)
        self.assertIn("不代拟具体单位、部门或第三方", review)

    def test_four_public_mirrors_match_the_canonical_references(self) -> None:
        for relative in REFERENCES:
            canonical = (CANONICAL / relative).read_bytes()
            for mirror in MIRRORS:
                with self.subTest(relative=relative, mirror=mirror):
                    self.assertEqual((mirror / relative).read_bytes(), canonical)


if __name__ == "__main__":
    unittest.main()
