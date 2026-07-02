#!/usr/bin/env python3
"""Evaluate AI drafts against public real-article profiles.

Fixtures may keep public source metadata for local traceability, but generated
evidence summaries anonymize article names and links. Difference rate means
required-key-point missing rate, not literal edit distance.
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

GENERIC_PLACEHOLDERS = {
    "发文机关",
    "发文字号",
    "主送单位",
    "主送机关",
    "报告主体",
    "受文机关",
    "报送单位",
    "来函单位",
    "发布单位",
    "通报对象",
    "征求对象",
    "事项背景",
    "法规条款",
}


def load_prose_lint():
    spec = importlib.util.spec_from_file_location("prose_lint", PROSE_LINT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {PROSE_LINT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def normalize(text: str) -> str:
    return re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]+", "", text)


def point_covered(point: dict[str, Any], text: str) -> bool:
    compact = normalize(text)
    return all(normalize(term) in compact for term in point["terms"])


def exact_term_hits(points: list[dict[str, Any]], text: str) -> tuple[list[str], int]:
    compact = normalize(text)
    terms: list[str] = []
    for point in points:
        terms.extend(normalize(term) for term in point["terms"])
    unique_terms = sorted(set(term for term in terms if term))
    return [term for term in unique_terms if term in compact], len(unique_terms)


def placeholder_echo_terms(text: str) -> list[str]:
    compact = normalize(text)
    return sorted(term for term in GENERIC_PLACEHOLDERS if normalize(term) in compact)


def evaluate(profile: dict[str, Any], draft: dict[str, Any], prose_lint) -> dict[str, Any]:
    text = draft["text"]
    points = profile["required_points"]
    covered_labels = [point["label"] for point in points if point_covered(point, text)]
    missing_labels = [point["label"] for point in points if not point_covered(point, text)]
    hit_terms, total_terms = exact_term_hits(points, text)
    placeholder_terms = placeholder_echo_terms(text)
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
        "mode": draft["mode"],
        "required_points": total,
        "covered_points": len(covered_labels),
        "missing_points": missing,
        "difference_rate": round(missing / total, 4) if total else 0,
        "covered_labels": covered_labels,
        "missing_labels": missing_labels,
        "exact_term_hits": len(hit_terms),
        "required_terms": total_terms,
        "keyword_echo_rate": round(len(hit_terms) / total_terms, 4) if total_terms else 0,
        "placeholder_echo_count": len(placeholder_terms),
        "placeholder_echo_terms": placeholder_terms,
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
            "avg_keyword_echo_rate": round(mean(item["keyword_echo_rate"] for item in items), 4),
            "placeholder_echo_cases": sum(1 for item in items if item["placeholder_echo_count"]),
            "placeholder_echo_terms": sum(item["placeholder_echo_count"] for item in items),
            "total_missing_points": sum(item["missing_points"] for item in items),
            "total_required_points": sum(item["required_points"] for item in items),
            "format_errors": sum(item["format_error_count"] for item in items),
            "duplicate_errors": sum(item["duplicate_error_count"] for item in items),
            "anti_ai_risks": sum(item["anti_ai_risk_count"] for item in items),
        }
    return result


def write_markdown(rows: list[dict[str, Any]], profiles: list[dict[str, Any]], out_path: Path) -> None:
    agg = aggregate(rows)
    sample_labels = {profile["id"]: f"sample-{index:02d}" for index, profile in enumerate(profiles, start=1)}
    genre_counts: dict[str, int] = defaultdict(int)
    source_counts: dict[str, int] = defaultdict(int)
    for profile in profiles:
        genre_counts[profile["genre"]] += 1
        source_kind = profile.get("source_kind", "公开政府或公共服务平台")
        source_counts[source_kind] += 1
    lines = [
        "# 真实样文回归测试摘要",
        "",
        "本测试以公开真实文章为参照，摘要只输出匿名样本编号、文种和经转述的关键要素，不输出具体文章标题、链接或原文正文。",
        "差异率按关键要素缺失率计算：缺失关键要素数 / 应覆盖关键要素数。该指标不衡量逐字相似度，主要检查应提事项、格式风险、重复事项和反 AI 风险。该组用于回归检查，不代表真实业务表现。",
        "为避免把精确关键词命中误读为质量证明，本报告同时输出关键词命中率和占位词风险。占位词风险表示草稿直接写入了“发文机关、发文字号、主送单位”等匿名标签，需进入人工或 LLM judge 复核。",
        "",
        "## 汇总结果",
        "",
        "| 模式 | 样本数 | 平均差异率 | 缺失要素 | 应覆盖要素 | 关键词命中率 | 占位词风险样本 | 占位词命中 | 格式风险 | 重复事项 | 反 AI 风险 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for mode in sorted(agg):
        item = agg[mode]
        lines.append(
            f"| {mode} | {item['cases']} | {item['avg_difference_rate']:.2%} | "
            f"{item['total_missing_points']} | {item['total_required_points']} | "
            f"{item['avg_keyword_echo_rate']:.2%} | {item['placeholder_echo_cases']} | "
            f"{item['placeholder_echo_terms']} | "
            f"{item['format_errors']} | {item['duplicate_errors']} | {item['anti_ai_risks']} |"
        )
    lines.extend(
        [
            "",
            "## 分样本结果",
            "",
            "| 样本 | 文种 | 模式 | 差异率 | 覆盖/应覆盖 | 关键词命中率 | 占位词风险 | 格式风险 | 重复事项 | 反 AI 风险 | 缺失要素 |",
            "| --- | --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in rows:
        missing = "、".join(row["missing_labels"]) if row["missing_labels"] else "无"
        placeholders = "、".join(row["placeholder_echo_terms"]) if row["placeholder_echo_terms"] else "无"
        lines.append(
            f"| {sample_labels.get(row['id'], row['id'])} | {row['genre']} | {row['mode']} | {row['difference_rate']:.2%} | "
            f"{row['covered_points']}/{row['required_points']} | {row['keyword_echo_rate']:.2%} | {placeholders} | {row['format_error_count']} | "
            f"{row['duplicate_error_count']} | {row['anti_ai_risk_count']} | {missing} |"
        )
    lines.extend(["", "## 来源类别", ""])
    for genre, count in sorted(genre_counts.items()):
        lines.append(f"- {genre}：{count} 组")
    lines.extend(["", "## 来源类型", ""])
    for source_kind, count in sorted(source_counts.items()):
        lines.append(f"- {source_kind}：{count} 组")
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
