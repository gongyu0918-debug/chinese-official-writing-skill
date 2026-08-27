#!/usr/bin/env python3
"""Host-neutral single-call final-review contract for synchronous adapters."""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any, Final


MODULE_PATH: Final = Path(__file__).resolve()
ALLOWED_ISSUES: Final = frozenset(
    {
        "NEW_FACT_OR_PROCEDURE",
        "STATE_UPGRADE",
        "SCOPE_EXPANSION",
        "REPETITION_OR_TITLE",
        "WRAPPER_OR_GENRE",
        "STRUCTURE_IMBALANCE",
    }
)
REVIEW_INSTRUCTIONS: Final = """你是中文正式事务文稿的单次写后审稿器。输入含原始任务和完整初稿 D0。

只判断 D0 是否存在下列明确问题：事实、数字、完整日期、主体、范围或未决状态被改变；把拟议、待定、可安排、预期作用写成既成事实；新增材料外程序、责任主体、期限或承诺；文种或发布者角色错位；正文外过程说明、自评、字数、Markdown 围栏；结构明显失衡或不能直接使用。

基于给定事实和常识的一层合理原因、低强度预期作用、必要结论和承接不是天然风险，不得因谨慎而机械删除，也不得为了短而削薄事务性文稿。原稿安全时必须 KEEP。只有存在明确问题且能一次完整、安全修正时才 REPLACE。

逐项检查后再决定，但不要输出检查过程：

1. 合理推断只能从已给需求、现状或活动直接落到一层目的、预期作用或低强度意义；“需求持续增长”“后续业务已有安排”“待确定后另行报批”等新增趋势、程序和承诺，不因听起来常见就成为已给事实。采购材料若只给出利用率、排队、拟购和待定事项，不得另造“设备检修或故障时缺少冗余”“增购后留出冗余”等现状、风险或目的；可以保留与已给事实直接相连的“缓解资源紧张、减少排队、提升任务处理时效”等一层预期作用。
2. 人数、完成环节和单人引语分别约束谓语覆盖范围；材料只支持部分人员完成或一人感受时，“参训人员”“参与人员”“大家”等无数量限定的集合主体按全部参加者理解，不能承接“熟悉、掌握、提升、增强”等成效谓语。应改为材料明确的完成者或部分人员，或改写为活动层面的“提供机会、搭建平台”等低强度作用。
3. 标题检查“关于有关”等叠词；相邻句若只是换词重复同一主体、动作、对象和状态，没有新增原因、影响、结论或办理作用，应合并，不以分项标题加同义正文机械凑长。
4. REPLACE 采用最小修订。含数字、数量、完整日期、引语或“拟、尚未、待定、可安排”等状态硬锚的句子，除删除句内明确错误外，不与相邻句合并、不拆分、不移动，不改变其主体、对象和状态关系。

返回唯一、严格的 JSON 对象，不加 Markdown 围栏或对象外文字。action 只能是 KEEP 或 REPLACE；issues 只能从 NEW_FACT_OR_PROCEDURE、STATE_UPGRADE、SCOPE_EXPANSION、REPETITION_OR_TITLE、WRAPPER_OR_GENRE、STRUCTURE_IMBALANCE 中选择。KEEP 时 issues 必须为空且 final_text 必须为空字符串；REPLACE 时 issues 至少一项，final_text 只放可直接使用的完整正文，不附说明、自评、字数、横线或代码围栏。不得虚构输入外事实。"""


@dataclass(frozen=True)
class FinalSelection:
    action: str
    text: str
    issues: tuple[str, ...]
    reason: str


def build_messages(request: str, draft: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": REVIEW_INSTRUCTIONS},
        {
            "role": "user",
            "content": f"原始任务：\n{request}\n\n完整初稿 D0：\n{draft}",
        },
    ]


def max_output_tokens(draft: str) -> int:
    """Leave room for one full replacement while bounding auxiliary spend."""
    return min(16384, max(4096, len(draft) * 2 + 1000))


def _load_hard_anchors() -> Any | None:
    candidates = (
        MODULE_PATH.parent.parent / "shared" / "hard_anchors.py",
        MODULE_PATH.parent / "shared" / "hard_anchors.py",
    )
    path = next((candidate for candidate in candidates if candidate.is_file()), None)
    if path is None:
        return None
    try:
        spec = importlib.util.spec_from_file_location(
            "cow_single_pass_hard_anchors", path
        )
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    except Exception:
        return None


def _ignored_length_values(hard_anchors: Any, request: str) -> set[str]:
    ignored: set[str] = set()
    try:
        occurrences = hard_anchors.snapshot(request).numbers
    except Exception:
        return ignored
    for item in occurrences:
        if not item.is_length_bound:
            continue
        numeric = re.search(r"\d+(?:\.\d+)?", item.value)
        if numeric:
            ignored.add(numeric.group(0))
    return ignored


def _fallback(draft: str, reason: str) -> FinalSelection:
    return FinalSelection("KEEP", draft, (), reason)


def parse_selection(raw: Any, draft: str, request: str) -> FinalSelection:
    """Parse one model decision; any ambiguity returns the immutable D0."""
    if not isinstance(raw, str):
        return _fallback(draft, "non_string_response")
    try:
        payload = json.loads(raw.strip())
    except (TypeError, json.JSONDecodeError):
        return _fallback(draft, "invalid_json")
    if not isinstance(payload, dict) or set(payload) != {
        "action",
        "issues",
        "final_text",
    }:
        return _fallback(draft, "invalid_shape")

    action = payload.get("action")
    issues = payload.get("issues")
    final_text = payload.get("final_text")
    if (
        action not in {"KEEP", "REPLACE"}
        or not isinstance(issues, list)
        or not all(isinstance(item, str) and item in ALLOWED_ISSUES for item in issues)
        or len(set(issues)) != len(issues)
        or not isinstance(final_text, str)
    ):
        return _fallback(draft, "invalid_fields")

    if action == "KEEP":
        if issues or final_text != "":
            return _fallback(draft, "invalid_keep")
        return FinalSelection("KEEP", draft, (), "model_keep")

    if not issues or not final_text.strip() or final_text == draft:
        return _fallback(draft, "invalid_replace")
    if "\x00" in final_text or len(final_text) > max(12000, len(draft) * 2 + 1000):
        return _fallback(draft, "replacement_bounds")

    hard_anchors = _load_hard_anchors()
    if hard_anchors is None:
        return _fallback(draft, "hard_anchor_contract_unavailable")
    try:
        comparison = hard_anchors.compare(
            draft,
            final_text,
            request,
            ignored_authority_values=_ignored_length_values(hard_anchors, request),
        )
    except Exception:
        return _fallback(draft, "hard_anchor_check_failed")
    if not comparison.get("mechanical_ok"):
        return _fallback(draft, "hard_anchor_violation")
    if comparison.get("relation_packet"):
        return _fallback(draft, "anchor_relation_unverified")
    return FinalSelection("REPLACE", final_text, tuple(issues), "model_replace")
