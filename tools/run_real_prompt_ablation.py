#!/usr/bin/env python3
"""Compare real-user prompt coverage between two skill package roots.

This is a deterministic release check. It does not call an LLM. The cases use
realistic user-style prompts and verify whether each skill package contains the
trigger, routing, checklist, handling-element, and lint behavior needed to
support the prompt without relying on ad hoc reviewer judgment.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class PromptCase:
    id: str
    kind: str
    prompt: str
    checks: dict[str, Any] = field(default_factory=dict)


CASES: list[PromptCase] = [
    PromptCase(
        id="P001",
        kind="create",
        prompt="帮我起草一份向各区征求意见的函，附件是管理办法征求意见稿，要求写清反馈期限、邮箱和联系人。",
        checks={
            "description_terms": ["征求意见函"],
            "routing_terms": ["征求意见函", "反馈期限", "反馈方式"],
            "checklist_sections": ["征求意见函"],
            "handling_rows": ["征求意见函"],
        },
    ),
    PromptCase(
        id="P002",
        kind="create",
        prompt="写一份采购公告，项目是办公软件会员服务采购，预算上限 2 万元，要有响应文件提交方式和联系人。",
        checks={
            "description_terms": ["采购公告"],
            "routing_terms": ["采购公告", "预算", "联系方式"],
            "checklist_sections": ["采购公告"],
            "handling_rows": ["采购公告"],
        },
    ),
    PromptCase(
        id="P003",
        kind="create",
        prompt="请起草拟聘用人员公示，公示 5 个工作日，要求写明异议渠道、联系电话和处理规则。",
        checks={
            "description_terms": ["公示"],
            "routing_terms": ["公示", "期限", "异议渠道"],
            "checklist_sections": ["公示"],
            "handling_rows": ["公示"],
        },
    ),
    PromptCase(
        id="P004",
        kind="create",
        prompt="给我写一份年度信息化工作要点，按重点任务、责任机制、时间节点和评价方式组织。",
        checks={
            "description_terms": ["工作要点"],
            "routing_terms": ["工作要点", "时间节点", "评价方式"],
            "checklist_sections": ["工作要点"],
            "handling_rows": ["工作要点"],
        },
    ),
    PromptCase(
        id="P005",
        kind="create",
        prompt="起草一份项目初步设计审查材料，区分审查依据、主要发现、风险、整改要求和审查结论。",
        checks={
            "description_terms": ["审查材料"],
            "routing_terms": ["审查材料", "整改要求", "结论"],
            "checklist_sections": ["审查材料"],
            "handling_rows": ["审查材料"],
        },
    ),
    PromptCase(
        id="P006",
        kind="revise",
        prompt="请把这段顺成正式报告：根据领导要求，项目组已完成风险排查。领导关心的交付节点已纳入每周调度。",
        checks={
            "lint_text": "根据领导要求，项目组已完成风险排查。领导关心的交付节点已纳入每周调度。",
            "lint_absent_labels": ["viewpoint-risk", "casual"],
        },
    ),
    PromptCase(
        id="P007",
        kind="revise",
        prompt="审一下这段能不能进正文：本材料由 AI 起草。根据用户要求修改如下：这版文章将压缩为三段。",
        checks={
            "lint_text": "本材料由 AI 起草。根据用户要求修改如下：这版文章将压缩为三段。",
            "lint_present_labels": ["thought-leak", "viewpoint-risk"],
        },
    ),
    PromptCase(
        id="P008",
        kind="revise",
        prompt="请把纪要里的这句保留成正式表达：会议要求如下，各责任单位每周反馈整改进展。",
        checks={
            "lint_text": "会议要求如下，各责任单位每周反馈整改进展。",
            "lint_absent_labels": ["viewpoint-risk"],
        },
    ),
    PromptCase(
        id="P009",
        kind="revise",
        prompt="在第三部分后增加一个说明数据口径影响的自然段，不要新增小标题，原四个小标题必须保持不变。",
        checks={
            "review_checklist_terms": ["改稿前小标题清单", "改稿后小标题清单", "小标题数量"],
            "heading_lock": {
                "before": """一、整改进展
二、存在问题
三、原因分析
四、下一步安排""",
                "after": """一、整改进展
二、存在问题
三、原因分析
四、下一步安排""",
            },
        },
    ),
    PromptCase(
        id="P010",
        kind="create",
        prompt="写一份情况说明，说明系统维护期间部分数据同步延迟、已恢复、后续加强监测；不要写成请示，也不要加接收方。",
        checks={
            "description_terms": ["说明"],
            "routing_terms": ["说明", "不写成请示"],
            "checklist_sections": ["说明"],
            "handling_rows": ["说明"],
            "file_terms": {
                "chinese-official-writing/references/format-gbt9704.md": ["最终以用户模板和材料属性为准"],
            },
        },
    ),
    PromptCase(
        id="P011",
        kind="create",
        prompt="帮我起草一份内部 WPS 会员采购申请，保留“尊敬的领导：”称呼和两行标题，不要强行改成法定公文格式。",
        checks={
            "description_terms": ["申请"],
            "routing_terms": ["申请", "不因使用请批语就自动改成请示"],
            "checklist_sections": ["申请"],
            "handling_rows": ["申请"],
            "file_terms": {
                "chinese-official-writing/references/genre-checklist.md": ["两行标题", "尊敬的领导"],
                "chinese-official-writing/references/formal-addressing.md": ["不作无依据硬删"],
            },
        },
    ),
    PromptCase(
        id="P012",
        kind="revise",
        prompt="把这份报告改得正式一点，但我明确要求不写主送机关，不要补接收方，也不要加“妥否，请批示”。",
        checks={
            "routing_terms": ["报告", "不以“妥否，请批示”收尾"],
            "review_checklist_terms": ["只有明确要求时才作硬性位置断言"],
            "file_terms": {
                "chinese-official-writing/references/final-review-layers.md": ["用户明确要求是否遗漏", "只有在用户或文种明确要求时"],
                "chinese-official-writing/references/format-gbt9704.md": ["最终以用户模板和材料属性为准"],
            },
        },
    ),
    PromptCase(
        id="P013",
        kind="revise",
        prompt="把这份申请顺一下，保留“尊敬的领导：”、右下落款和“妥否，请批示”结尾，不要改成请示。",
        checks={
            "routing_terms": ["不因使用请批语就自动改成请示"],
            "checklist_sections": ["申请"],
            "file_terms": {
                "chinese-official-writing/references/genre-checklist.md": ["不要只因出现 `妥否，请批示` 就判定为请示"],
                "chinese-official-writing/references/formal-addressing.md": ["申请向上级或领导班子请求批准时", "不要违背用户指定结尾"],
            },
        },
    ),
    PromptCase(
        id="P014",
        kind="revise",
        prompt="审一下这段能不能直接作为正文交付，模型把全文包在代码块里，里面还有项目名称和日期占位。",
        checks={
            "lint_text": "```text\n项目名称为[具体项目名称]，计划于YYYY年MM月DD日完成。\n```",
            "lint_present_labels": ["markdown-code-fence", "unfinished-placeholder"],
        },
    ),
    PromptCase(
        id="P015",
        kind="revise",
        prompt="审一下这段是否还留着未完成占位：维护期限为XXXX年，设备XXXX张，支持XXXX并发请求。",
        checks={
            "lint_text": "维护期限为XXXX年，设备XXXX张，支持XXXX并发请求。",
            "lint_present_labels": ["unfinished-placeholder"],
        },
    ),
]


def read_text(root: Path, relative: str) -> str:
    path = root / relative
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def extract_description(skill_text: str) -> str:
    match = re.search(r"^description:\s*(.+)$", skill_text, re.M)
    return match.group(1) if match else ""


def has_table_row(text: str, row_name: str) -> bool:
    return re.search(rf"^\| {re.escape(row_name)} \|", text, re.M) is not None


HEADING_RE = re.compile(r"^\s*(?:#{1,6}\s+)?([一二三四五六七八九十]+、[^\n#]+?)\s*(?:#+\s*)?$", re.M)


def numbered_headings(text: str) -> list[str]:
    return [match.group(1).strip() for match in HEADING_RE.finditer(text)]


def load_prose_lint(root: Path, label: str):
    path = root / "chinese-official-writing" / "scripts" / "prose_lint.py"
    spec = importlib.util.spec_from_file_location(f"real_prompt_prose_lint_{label}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def evaluate_case(case: PromptCase, root: Path, prose_lint) -> dict[str, Any]:
    skill_text = read_text(root, "chinese-official-writing/SKILL.md")
    description = extract_description(skill_text)
    routing = read_text(root, "chinese-official-writing/references/genre-routing.md")
    checklist = read_text(root, "chinese-official-writing/references/genre-checklist.md")
    elements = read_text(root, "chinese-official-writing/references/handling-elements.md")
    review_checklist = read_text(root, "chinese-official-writing/references/review-checklist.md")

    failures: list[str] = []
    checks = case.checks

    for term in checks.get("description_terms", []):
        if term not in description:
            failures.append(f"description missing {term}")
    for term in checks.get("routing_terms", []):
        if term not in routing:
            failures.append(f"routing missing {term}")
    for section in checks.get("checklist_sections", []):
        if f"## {section}" not in checklist:
            failures.append(f"checklist missing {section}")
    for row in checks.get("handling_rows", []):
        if not has_table_row(elements, row):
            failures.append(f"handling-elements missing {row}")
    for term in checks.get("review_checklist_terms", []):
        if term not in review_checklist:
            failures.append(f"review-checklist missing {term}")
    for relative, terms in checks.get("file_terms", {}).items():
        file_text = read_text(root, relative)
        for term in terms:
            if term not in file_text:
                failures.append(f"{relative} missing {term}")

    heading_lock = checks.get("heading_lock")
    if heading_lock:
        before = numbered_headings(heading_lock["before"])
        after = numbered_headings(heading_lock["after"])
        if before != after:
            failures.append(f"heading list changed: before={before}; after={after}")

    lint_text = checks.get("lint_text")
    lint_labels: list[str] = []
    if lint_text:
        findings = prose_lint.scan(f"{case.id}:{case.kind}", lint_text, include_format=True, include_structure=True)
        lint_labels = sorted({item.label for item in findings})
        for label in checks.get("lint_present_labels", []):
            if label not in lint_labels:
                failures.append(f"lint missing {label}")
        for label in checks.get("lint_absent_labels", []):
            if label in lint_labels:
                failures.append(f"lint false-positive {label}")

    return {
        "id": case.id,
        "kind": case.kind,
        "prompt": case.prompt,
        "passed": not failures,
        "failures": failures,
        "lint_labels": lint_labels,
    }


def evaluate_root(root: Path, label: str) -> list[dict[str, Any]]:
    prose_lint = load_prose_lint(root, re.sub(r"\W+", "_", label))
    return [evaluate_case(case, root, prose_lint) for case in CASES]


def write_summary(out_dir: Path, results: dict[str, list[dict[str, Any]]]) -> None:
    lines = [
        "# 真实用户 Prompt 消融测试摘要",
        "",
        "本测试不调用 LLM，而是用真实用户式起草/改稿 prompt 检查 Skill 包是否具备触发、文种路由、办理要素、清单和 lint 行为支撑。",
        "",
        "| 基线 | 用例数 | 通过 | 失败 | 起草失败 | 改稿失败 |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label, rows in results.items():
        failures = [row for row in rows if not row["passed"]]
        create_failures = [row for row in failures if row["kind"] == "create"]
        revise_failures = [row for row in failures if row["kind"] == "revise"]
        lines.append(
            f"| {label} | {len(rows)} | {len(rows) - len(failures)} | {len(failures)} | "
            f"{len(create_failures)} | {len(revise_failures)} |"
        )
    lines.extend(
        [
            "",
            "## 用例结果",
            "",
            "| 基线 | 用例 | 类型 | 结果 | 失败原因 | Prompt |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for label, rows in results.items():
        for row in rows:
            failures = "; ".join(row["failures"]) if row["failures"] else "无"
            prompt = row["prompt"].replace("|", "｜")
            result = "通过" if row["passed"] else "失败"
            lines.append(f"| {label} | {row['id']} | {row['kind']} | {result} | {failures} | {prompt} |")
    lines.append("")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-root", required=True)
    parser.add_argument("--baseline-label", default="baseline")
    parser.add_argument("--current-root", default=".")
    parser.add_argument("--out", default="output/real-prompt-ablation")
    args = parser.parse_args()

    baseline_root = Path(args.baseline_root).resolve()
    current_root = Path(args.current_root).resolve()
    baseline_label = args.baseline_label
    results = {
        baseline_label: evaluate_root(baseline_root, baseline_label),
        "current": evaluate_root(current_root, "current"),
    }

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    write_summary(out_dir, results)
    print((out_dir / "summary.md").as_posix())
    current_failures = sum(1 for row in results["current"] if not row["passed"])
    baseline_failures = sum(1 for row in results[baseline_label] if not row["passed"])
    return 1 if current_failures > baseline_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
