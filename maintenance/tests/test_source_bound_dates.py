from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "chinese-official-writing/hooks/shared/source_bound_dates.py"
CASES_PATH = (
    ROOT
    / "maintenance/tests/evidence/ah002-news-date-completeness-r1/repair_cases.json"
)


def load_module():
    spec = importlib.util.spec_from_file_location("cow_source_bound_dates_test", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load source-bound date module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DATES = load_module()


class SourceBoundDateTests(unittest.TestCase):
    def test_frozen_natural_omissions_have_exact_mechanical_repairs(self) -> None:
        cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]
        for case in cases:
            with self.subTest(case=case["id"]):
                request = (
                    "请根据材料起草一则活动新闻，只输出可直接使用的正文。\n"
                    + case["material"]
                )
                result = DATES.restore_unique_full_date(request, case["d0"])
                if case["mode"] == "control":
                    self.assertFalse(result["selected"])
                    self.assertEqual(case["d0"], result["output"])
                else:
                    expected = case["d0"].replace(
                        case["short_date"], case["full_date"], 1
                    )
                    self.assertTrue(result["selected"])
                    self.assertEqual("source_bound_full_date_restored", result["reason"])
                    self.assertEqual(expected, result["output"])

    def test_non_news_and_month_day_only_requests_are_unchanged(self) -> None:
        draft = "关于培训安排的通知\n\n9月2日开展培训。"
        cases = (
            "请根据2026年9月2日的安排起草一份内部通知。",
            "请起草一则活动新闻。活动于9月2日举行。",
            "请把材料整理成报告。材料日期为2026年9月2日。",
        )
        for request in cases:
            with self.subTest(request=request):
                result = DATES.restore_unique_full_date(request, draft)
                self.assertFalse(result["selected"])
                self.assertEqual(draft, result["output"])

    def test_explicit_omission_and_negated_news_genre_are_unchanged(self) -> None:
        draft = "培训活动举行\n\n9月2日，培训活动举行。"
        requests = (
            "请起草活动新闻，材料日期为2026年9月2日，省略年份。",
            "请起草活动新闻，材料日期为2026年9月2日，日期不要写。",
            "请起草活动新闻，材料日期为2026年9月2日，日期只保留月日。",
            "请起草活动新闻，材料日期为2026年9月2日，请只写9月2日。",
            "不要写成新闻稿，请起草通知。安排日期为2026年9月2日。",
        )
        for request in requests:
            with self.subTest(request=request):
                self.assertFalse(DATES.restore_unique_full_date(request, draft)["selected"])

    def test_keep_full_date_instruction_does_not_look_like_omission(self) -> None:
        request = "请起草活动新闻。材料日期为2026年9月2日，不要省略年份。"
        draft = "培训活动举行\n\n9月2日，培训活动举行。"
        result = DATES.restore_unique_full_date(request, draft)
        self.assertTrue(result["selected"])
        self.assertIn("2026年9月2日", result["output"])

    def test_conflicting_or_multiple_mappings_are_unchanged(self) -> None:
        cases = (
            (
                "请起草活动新闻。甲事项日期为2025年9月2日，乙事项日期为2026年9月2日。",
                "9月2日，相关活动举行。",
            ),
            (
                "请起草活动新闻。甲事项日期为2026年9月2日，乙事项日期为2026年9月6日。",
                "9月2日举行甲事项。",
            ),
            (
                "请起草活动新闻。甲事项日期为2026年9月2日，乙事项日期为2026年9月6日。",
                "9月2日举行甲事项。9月6日举行乙事项。",
            ),
            (
                "请起草活动新闻。材料日期为2026年9月2日。",
                "2026年9月2日举行活动，9月2日完成复盘。",
            ),
            (
                "请起草活动新闻。材料日期为2026年9月2日。",
                "2025年9月2日举行活动。",
            ),
            (
                "请起草活动新闻。发布日期为2026年9月2日，活动日期为9月2日。",
                "9月2日举行活动。",
            ),
        )
        for request, draft in cases:
            with self.subTest(request=request, draft=draft):
                result = DATES.restore_unique_full_date(request, draft)
                self.assertFalse(result["selected"])
                self.assertEqual(draft, result["output"])

    def test_news_material_used_to_draft_another_genre_is_unchanged(self) -> None:
        request = "请参考2026年9月2日的新闻稿，起草一份情况报告。"
        draft = "情况报告\n\n9月2日，有关活动举行。"
        result = DATES.restore_unique_full_date(request, draft)
        self.assertFalse(result["selected"])
        self.assertEqual(draft, result["output"])


if __name__ == "__main__":
    unittest.main()
