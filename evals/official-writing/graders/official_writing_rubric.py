#!/usr/bin/env python3
"""Deterministic Promptfoo assertions for official-writing evals."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
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

APPROVAL_LANGUAGE = re.compile(r"妥否|请批示|请予批复|请予审查|请示|审定|批复")
REPORT_APPROVAL_LEAK = re.compile(r"妥否|请批示|请予批复|提请批复|申请批准|请求批准")
THOUGHT_LEAK = re.compile(r"作为(?:一个)?AI|我是(?:一个)?AI|我的(?:思路|推理|分析)|接下来我会|按你的要求")

GROUPS: dict[str, list[list[str]]] = {
    "通知": [["通知", "现就", "有关事项"], ["报送", "办理", "提交", "反馈"], ["时限", "期限", "日前", "材料", "联系人", "渠道"]],
    "请示": [["请示", "提请", "拟", "申请"], ["依据", "必要", "为推进", "为做好"], ["妥否", "请批示", "请予", "审定", "批复"]],
    "报告": [["报告", "现将", "有关情况"], ["进展", "完成", "情况", "问题"], ["下一步", "建议", "措施", "安排"]],
    "说明": [["说明", "有关情况", "原因"], ["背景", "过程", "必要", "依据"], ["后续", "安排", "整改", "补充"]],
    "方案": [["方案", "目标", "原则"], ["任务", "措施", "路径", "步骤"], ["责任", "时限", "保障", "验收"]],
    "申请": [["申请", "拟申请", "申请事项"], ["依据", "需求", "用途", "计划"], ["承诺", "真实性", "资金", "资源"]],
    "函": [["函", "商请", "请予支持", "征求"], ["贵单位", "有关单位", "相关部门"], ["反馈", "联系人", "期限", "材料"]],
    "复函": [["复函", "来函收悉", "经研究"], ["现函复", "答复", "意见"], ["程序", "条件", "责任", "后续"]],
    "批复": [["批复", "原则同意", "同意"], ["来文", "请示", "申请"], ["范围", "要求", "控制", "程序"]],
    "意见": [["意见", "总体要求", "目标"], ["重点任务", "政策", "措施"], ["组织", "保障", "责任", "落实"]],
    "决定": [["决定", "经研究", "决定如下"], ["依据", "范围", "事项"], ["执行", "责任", "生效", "要求"]],
    "公告": [["公告", "现将", "公众"], ["时间", "地点", "平台", "方式"], ["材料", "程序", "咨询", "渠道"]],
    "公示": [["公示", "拟", "名单", "事项"], ["公示期", "期限", "期间"], ["异议", "反映", "渠道", "材料"]],
    "通报": [["通报", "现将", "检查"], ["情况", "问题", "结果"], ["整改", "要求", "责任", "期限"]],
    "会议纪要": [["会议", "纪要", "会议明确"], ["议定", "责任分工", "事项"], ["时限", "跟踪", "落实", "后续"]],
    "工作要点": [["工作要点", "年度", "阶段"], ["目标", "任务", "重点"], ["机制", "责任", "节点", "成果"]],
    "工作总结": [["总结", "全年", "阶段性"], ["完成", "成效", "进展"], ["问题", "不足", "下一步"]],
    "调研报告": [["调研", "报告", "样本", "走访"], ["现状", "问题", "原因"], ["建议", "对策", "措施"]],
    "可研报告": [["可研", "可行性", "必要性"], ["需求", "建设内容", "技术路线"], ["投资", "成本", "风险", "结论"]],
    "实施方案": [["实施方案", "目标", "步骤"], ["准备", "部署", "试运行", "阶段"], ["责任", "验收", "保障", "时限"]],
    "建设方案": [["建设方案", "建设内容", "需求"], ["运行", "成本", "费用"], ["风险", "交付", "成效", "验收"]],
    "审查材料": [["审查", "审查材料", "审核"], ["依据", "对象", "发现"], ["意见", "整改", "补充", "程序"]],
}

AI_COMPUTE_GROUPS = [
    ["Token", "调用量", "资源", "GPU", "服务器", "并发"],
    ["成本", "费用", "租赁", "云端", "测算"],
    ["SLA", "服务保障", "运维", "安全", "验收", "交付"],
]


def _load_prose_lint():
    spec = importlib.util.spec_from_file_location("official_eval_prose_lint", PROSE_LINT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {PROSE_LINT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _compact(text: str) -> str:
    return re.sub(r"\s+", "", text)


def placeholder_echo_terms(text: str) -> list[str]:
    compact = _compact(text)
    return sorted(term for term in GENERIC_PLACEHOLDERS if term in compact)


def lint_summary(text: str) -> dict[str, Any]:
    prose_lint = _load_prose_lint()
    findings = prose_lint.scan("<promptfoo-output>", text, include_format=True, include_structure=True)
    counts = {"high": 0, "medium": 0, "low": 0}
    labels: dict[str, int] = {}
    for item in findings:
        counts[item.severity] = counts.get(item.severity, 0) + 1
        labels[item.label] = labels.get(item.label, 0) + 1
    risk_weight = counts["high"] * 3 + counts["medium"] * 2 + counts["low"]
    return {
        "counts": counts,
        "labels": labels,
        "risk_weight": risk_weight,
        "findings": [asdict(item) for item in findings],
    }


def _groups_for_genre(genre: str) -> list[list[str]]:
    groups = list(GROUPS.get(genre, [["事项", "工作"], ["责任", "安排"], ["要求", "落实"]]))
    if any(marker in genre for marker in ("算力", "GPU", "服务器", "云端", "技术服务")):
        groups.extend(AI_COMPUTE_GROUPS)
    return groups


def _group_hit(group: list[str], text: str) -> bool:
    compact = _compact(text)
    return any(term.lower() in compact.lower() for term in group)


def required_element_score(genre: str, text: str) -> dict[str, Any]:
    groups = _groups_for_genre(genre)
    hits = [_group_hit(group, text) for group in groups]
    hit_count = sum(1 for hit in hits if hit)
    threshold = max(2, int(len(groups) * 0.5))
    return {
        "required_groups": len(groups),
        "covered_groups": hit_count,
        "coverage": round(hit_count / len(groups), 4) if groups else 1.0,
        "threshold": threshold,
        "pass": hit_count >= threshold,
        "missing_groups": [group for group, hit in zip(groups, hits) if not hit],
    }


def hard_rule_failures(genre: str, text: str) -> list[str]:
    failures: list[str] = []
    compact = _compact(text)
    length = len(compact)
    if not compact:
        failures.append("empty_output")
    if length < 80:
        failures.append("too_short")
    if length > 650:
        failures.append("too_long")
    if placeholder_echo_terms(text):
        failures.append("placeholder_echo")
    if THOUGHT_LEAK.search(text):
        failures.append("thought_leak")
    if genre == "报告" and REPORT_APPROVAL_LEAK.search(text):
        failures.append("report_contains_approval_request")
    if genre == "请示" and not APPROVAL_LANGUAGE.search(text):
        failures.append("request_missing_approval_language")
    if genre == "批复" and not re.search(r"同意|批复|原则同意|不同意", text):
        failures.append("approval_missing_decision")
    if genre == "复函" and not re.search(r"来函收悉|收悉|函复|答复", text):
        failures.append("reply_letter_missing_receipt_or_reply")
    return failures


def score_text(text: str, vars_: dict[str, Any] | None = None) -> dict[str, Any]:
    vars_ = vars_ or {}
    genre = str(vars_.get("genre", "")).strip()
    lint = lint_summary(text)
    element = required_element_score(genre, text)
    placeholders = placeholder_echo_terms(text)
    hard_failures = hard_rule_failures(genre, text)

    hard_pass = not hard_failures
    lint_penalty = min(0.35, lint["counts"]["high"] * 0.18 + lint["counts"]["medium"] * 0.07 + lint["counts"]["low"] * 0.025)
    hard_penalty = 0.35 if hard_failures else 0.0
    score = max(0.0, min(1.0, element["coverage"] * 0.75 + (0.25 if hard_pass else 0.0) - lint_penalty - hard_penalty))

    return {
        "case_id": vars_.get("case_id", ""),
        "genre": genre,
        "length": len(_compact(text)),
        "score": round(score, 4),
        "pass": bool(hard_pass and element["pass"] and score >= 0.55),
        "hard_rule_pass": hard_pass,
        "hard_rule_failures": hard_failures,
        "required_elements": element,
        "placeholder_echo_terms": placeholders,
        "placeholder_echo_count": len(placeholders),
        "lint": lint,
    }


def assert_official_writing(output: str, context: dict[str, Any]) -> dict[str, Any]:
    vars_ = context.get("vars") or {}
    result = score_text(output or "", vars_)
    # Promptfoo should fail the run for invalid provider behavior, not because
    # the baseline intentionally scores poorly in an ablation. Quality gates are
    # enforced by run_eval.py from the structured summary.
    provider_pass = bool((output or "").strip()) and "empty_output" not in result["hard_rule_failures"]
    reason = json.dumps(
        {
            "case_id": result["case_id"],
            "genre": result["genre"],
            "length": result["length"],
            "hard_rule_pass": result["hard_rule_pass"],
            "hard_rule_failures": result["hard_rule_failures"],
            "required_elements": result["required_elements"],
            "placeholder_echo_terms": result["placeholder_echo_terms"],
            "lint_counts": result["lint"]["counts"],
            "lint_labels": result["lint"]["labels"],
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return {"pass": provider_pass, "score": result["score"], "reason": reason}
