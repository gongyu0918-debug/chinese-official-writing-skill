from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


prose_lint = load_module(
    "placeholder_blind_spot_prose_lint",
    ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py",
)


def labels(text: str) -> set[str]:
    return {item.label for item in prose_lint.scan("<d2>", text, delivery_mode="draft-body")}


class PlaceholderBlindSpotFixTests(unittest.TestCase):
    def test_xx_followed_by_chinese_is_caught_without_a_category_wordlist(self) -> None:
        for text in [
            "XX类项目检测能力不足",
            "兼容XX系统",
            "XX项指标未达标",
            "覆盖XX业务场景",
            "XX型号设备待采购",
            "XX名称待核实",
        ]:
            with self.subTest(text=text):
                self.assertIn("unfinished-placeholder", labels(text))

    def test_natural_category_words_are_not_false_positived(self) -> None:
        for text in [
            "社会保障类126件",
            "市场主体类82件",
            "公安类76件",
            "税务类64件",
            "检测系统运行正常",
            "业务场景明确",
        ]:
            with self.subTest(text=text):
                self.assertNotIn("unfinished-placeholder", labels(text))

    def test_ascii_and_case_boundary_remain_deliberately_narrow(self) -> None:
        for text in ["ABXX系统", "xx系统", "Xx系统", "ＸＸ系统", "XX发〔2026〕1号"]:
            with self.subTest(text=text):
                self.assertNotIn("unfinished-placeholder", labels(text))

    def test_existing_placeholder_rules_and_clean_corpus_stay_clean(self) -> None:
        for text in ["经费XXXX万元", "完成时间YYYY年MM月DD日", "〔签发日期〕", "（成文日期待确认）"]:
            with self.subTest(text=text):
                self.assertIn("unfinished-placeholder", labels(text))

        corpus = json.loads(
            (ROOT / "tests" / "fixtures" / "clean_prose_corpus.json").read_text(encoding="utf-8")
        )
        items = corpus if isinstance(corpus, list) else corpus.get("items", [])
        for item in items:
            text = item.get("text", "") if isinstance(item, dict) else str(item)
            if text:
                with self.subTest(text=text[:30]):
                    self.assertNotIn("unfinished-placeholder", labels(text))


if __name__ == "__main__":
    unittest.main()
