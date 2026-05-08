#!/usr/bin/env python3
"""Build a compact, sanitized packet for DeepSeek ablation review.

The packet is generated from synthetic outputs only. It deliberately avoids
raw user documents, internal project text, local paths, and personal data.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SAMPLE_KEYS = [
    "通知-基础办理",
    "请示-专项推进",
    "报告-年度安排",
    "会议纪要-跨部门协同",
    "可研报告-年度安排",
    "建设方案-整改复核",
    "算力服务可研报告-年度安排",
    "GPU/服务器租赁技术需求-专项推进",
    "云端部署成本对比说明-整改复核",
]


def read_text_auto(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8", "utf-8-sig", "utf-16", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def split_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_key = ""
    current_lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("### "):
            if current_key:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = line[4:].strip()
            current_lines = [line]
        elif current_key:
            current_lines.append(line)
    if current_key:
        sections[current_key] = "\n".join(current_lines).strip()
    return sections


def find_sample(sections: dict[str, str], prefix: str, sample_key: str) -> str:
    for key, value in sections.items():
        if key.startswith(prefix) and sample_key in key:
            return value
    return ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="output/expanded-ablation")
    parser.add_argument("--lint-baseline-json", default="")
    parser.add_argument("--lint-skill-json", default="")
    parser.add_argument("--out", default="output/expanded-ablation/deepseek-eval-packet.md")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    baseline_path = out_dir / "baseline.md"
    skill_path = out_dir / "skill.md"
    baseline = split_sections(baseline_path.read_text(encoding="utf-8"))
    skill = split_sections(skill_path.read_text(encoding="utf-8"))

    baseline_lint = []
    skill_lint = []
    if args.lint_baseline_json:
        baseline_lint = json.loads(read_text_auto(Path(args.lint_baseline_json)))
    if args.lint_skill_json:
        skill_lint = json.loads(read_text_auto(Path(args.lint_skill_json)))

    lines = [
        "# DeepSeek Ablation Evaluation Packet",
        "",
        "This packet contains only synthetic release-test material for a Chinese official-writing Skill.",
        "Do not infer facts about any real organization or project from these samples.",
        "",
        "## Test Design",
        "",
        "- Scope: 22 common Chinese official-document genres and 5 AI-compute technical official-document genres.",
        "- Variants: 6 synthetic tasks per genre, covering short, medium, long, routine, cross-department, annual, and review scenarios.",
        f"- Baseline samples: {len(baseline)} synthetic drafts generated from minimal prompts without skill constraints.",
        f"- Skill samples: {len(skill)} synthetic drafts generated with official-writing constraints.",
        "- Evaluation target: whether the Skill improves genre fit, viewpoint, paragraph logic, official tone, AI-flavor control, and AI-compute argument chains.",
        "",
        "## Lint Summary",
        "",
        f"- Baseline lint findings: {len(baseline_lint)}",
        f"- Skill lint findings: {len(skill_lint)}",
        "",
        "## Representative Samples",
        "",
    ]

    for sample_key in SAMPLE_KEYS:
        lines.extend(
            [
                f"### Sample: {sample_key}",
                "",
                "Baseline:",
                "",
                find_sample(baseline, "Baseline-", sample_key) or "(missing)",
                "",
                "Skill:",
                "",
                find_sample(skill, "Skill-", sample_key) or "(missing)",
                "",
            ]
        )

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
