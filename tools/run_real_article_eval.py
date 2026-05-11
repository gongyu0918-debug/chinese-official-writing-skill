#!/usr/bin/env python3
"""Evaluate AI drafts against public real-article profiles.

The fixture stores only public titles, URLs, and paraphrased key points. It does
not store raw source articles. Difference rate means required-key-point missing
rate, not literal edit distance.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import importlib.util
import json
from pathlib import Path
import re
from statistics import mean
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PROSE_LINT_PATH = REPO_ROOT / "chinese-official-writing" / "scripts" / "prose_lint.py"


def load_prose_lint():
    spec = importlib.util.spec_from_file_location("prose_lint", PROSE_LINT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {PROSE_LINT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def normalize(text: str) -> str:
    return re.sub(r"\s+", "", text)


def point_covered(point: dict[str, Any], text: str) -> bool:
    compact = normalize(text)
    return all(normalize(term) in compact for term in point["terms"])


def evaluate(profile: dict[str, Any], draft: dict[str, Any], prose_lint) -> dict[str, Any]:
    text = draft["text"]
    points = profile["required_points"]
    covered_labels = [point["label"] for point in points if point_covered(point, text)]
    missing_labels = [point["label"] for point in points if point["label"] not in covered_labels]
    findings = prose_lint.scan(
        f"{draft['id']}:{draft['mode']}",
        text,
        include_format=True,
        include_structure=True,
    )
    format_labels = {
        "halfwidth-punctuation",
        "number-grouping-comma",
        "cn-number-space",
        "emoji-marker",
        "western-bullet",
    }
    duplicate_labels = {"adjacent-duplicate-matter"}
    anti_ai_labels = {"paired-summary", "side-commentary", "thought-leak", "viewpoint-risk", "casual"}
    total = len(points)
    missing = len(missing_labels)
    return {
        "id": draft["id"],
        "genre": profile["genre"],
        "title": profile["title"],
        "mode": draft["mode"],
        "required_points": total,
        "covered_points": len(covered_labels),
        "missing_points": missing,
        "difference_rate": round(missing / total, 4) if total else 0,
        "covered_labels": covered_labels,
        "missing_labels": missing_labels,
        "format_error_count": sum(1 for item in findings if item.label in format_labels),
        "duplicate_error_count": sum(1 for item in findings if item.label in duplicate_labels),
        "anti_ai_risk_count": sum(1 for item in findings if item.label in anti_ai_labels),
        "lint_findings": [item.__dict__ for item in findings],
    }


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_mode: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_mode[row["mode"]].append(row)
    result: dict[str, Any] = {}
    for mode, items in by_mode.items():
        result[mode] = {
            "cases": len(items),
            "avg_difference_rate": round(mean(item["difference_rate"] for item in items), 4),
            "total_missing_points": sum(item["missing_points"] for item in items),
            "total_required_points": sum(item["required_points"] for item in items),
            "format_errors": sum(item["format_error_count"] for item in items),
            "duplicate_errors": sum(item["duplicate_error_count"] for item in items),
            "anti_ai_risks": sum(item["anti_ai_risk_count"] for item in items),
        }
    return result


def write_markdown(rows: list[dict[str, Any]], profiles: list[dict[str, Any]], out_path: Path) -> None:
    agg = aggregate(rows)
    lines = [
        "# 真实样文回归测试摘要",
        "",
        "本测试以公开真实文章为参照，只保存标题、链接和经转述的关键要素，不保存原文正文。",
        "差异率按关键要素缺失率计算：缺失关键要素数 / 应覆盖关键要素数。该指标不衡量逐字相似度。",
        "",
        "## 汇总结果",
        "",
        "| 模式 | 样本数 | 平均差异率 | 缺失要素 | 应覆盖要素 | 格式风险 | 重复事项 | 反 AI 风险 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for mode in sorted(agg):
        item = agg[mode]
        lines.append(
            f"| {mode} | {item['cases']} | {item['avg_difference_rate']:.2%} | "
            f"{item['total_missing_points']} | {item['total_required_points']} | "
            f"{item['format_errors']} | {item['duplicate_errors']} | {item['anti_ai_risks']} |"
        )
    lines.extend(
        [
            "",
            "## 分样本结果",
            "",
            "| 样本 | 文种 | 模式 | 差异率 | 覆盖/应覆盖 | 格式风险 | 重复事项 | 缺失要素 |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in rows:
        missing = "、".join(row["missing_labels"]) if row["missing_labels"] else "无"
        lines.append(
            f"| {row['id']} | {row['genre']} | {row['mode']} | {row['difference_rate']:.2%} | "
            f"{row['covered_points']}/{row['required_points']} | {row['format_error_count']} | "
            f"{row['duplicate_error_count']} | {missing} |"
        )
    lines.extend(["", "## 公开来源", ""])
    for profile in profiles:
        lines.append(f"- {profile['genre']}：[{profile['title']}]({profile['url']})（{profile['source']}）")
    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", default="tests/fixtures/real_article_profiles.json")
    parser.add_argument("--drafts", default="tests/fixtures/real_article_ai_drafts.json")
    parser.add_argument("--out", default="output/real-article-eval")
    args = parser.parse_args()

    profiles = json.loads((REPO_ROOT / args.profiles).read_text(encoding="utf-8"))
    drafts = json.loads((REPO_ROOT / args.drafts).read_text(encoding="utf-8"))
    profile_by_id = {profile["id"]: profile for profile in profiles}
    prose_lint = load_prose_lint()
    rows = [evaluate(profile_by_id[draft["id"]], draft, prose_lint) for draft in drafts]

    out_dir = REPO_ROOT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(
        json.dumps({"aggregate": aggregate(rows), "rows": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_markdown(rows, profiles, out_dir / "summary.md")
    print((out_dir / "summary.md").as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
