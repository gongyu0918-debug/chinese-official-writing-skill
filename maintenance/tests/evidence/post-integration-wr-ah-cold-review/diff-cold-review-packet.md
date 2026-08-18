# WR-007 + AH-001 产品 DIFF 冷审包

只审下列固定 DIFF。重点检查：规则是否造成新外扩或过严回退；共享硬锚是否错误处理数量去重、引语、字段、主体/对象/范围/状态关系；异常时是否仍回退 D0；是否出现上帝函数、魔法数字、孤儿路径或普通无 Hook 路径污染。逐项报告 P0—P2；没有问题写 PASS。

```diff
diff --git a/chinese-official-writing/hooks/capabilities/over_length/runtime.py b/chinese-official-writing/hooks/capabilities/over_length/runtime.py
index 0c14b39e..5b4fa88f 100644
--- a/chinese-official-writing/hooks/capabilities/over_length/runtime.py
+++ b/chinese-official-writing/hooks/capabilities/over_length/runtime.py
@@ -47,11 +47,6 @@ MATERIAL_CONTEXT_RE: Final = re.compile(
     r"(?:材料|附件|引语|原文|背景|摘录|写明|载明|提到|如下|制度|合同|条款).{0,18}$"
 )
 APPROXIMATE_LENGTH_RE: Final = re.compile(r"(?:约|左右|上下)")
-NUMBER_RE: Final = re.compile(r"\d+(?:\.\d+)?")
-CJK_QUANTITY_RE: Final = re.compile(
-    r"[一二三四五六七八九十百千万两]+(?:台|件|项|次|个月|年|天|份|人|套|批|元)"
-)
-QUOTE_RE: Final = re.compile(r"[\"“][^\"”\n]+[\"”]")
 RESPONSIBILITY_SUBJECT_RE: Final = re.compile(
     r"(?:^|[，。；;\n])\s*(?P<subject>[\u4e00-\u9fffA-Za-z0-9（）()·]{2,20}?)"
     r"(?:负责|牵头|承担)"
@@ -82,6 +77,7 @@ ARABIC_NUMBERED_ITEM_RE: Final = re.compile(r"^\s*\d+[.、]")
 CONTRACT_PATH: Final = (
     Path(__file__).resolve().parents[1] / "protective_expansion" / "contract.py"
 )
+HARD_ANCHOR_PATH: Final = Path(__file__).resolve().parents[2] / "shared" / "hard_anchors.py"
 
 
 def _sha256_text(value: str) -> str:
@@ -202,6 +198,21 @@ def _load_repetition_contract() -> Any | None:
     return module
 
 
+def _load_hard_anchor_contract() -> Any | None:
+    try:
+        spec = importlib.util.spec_from_file_location(
+            "cow_over_length_hard_anchors", HARD_ANCHOR_PATH
+        )
+        if spec is None or spec.loader is None:
+            return None
+        module = importlib.util.module_from_spec(spec)
+        sys.modules[spec.name] = module
+        spec.loader.exec_module(module)
+    except Exception:
+        return None
+    return module
+
+
 def _extract_json_object(value: Any) -> dict[str, Any] | None:
     if not isinstance(value, str):
         return None
@@ -294,12 +305,19 @@ def mechanical_reason(
 ) -> str | None:
     if not candidate.strip():
         return "over_length_empty_candidate"
-    if set(NUMBER_RE.findall(candidate)) != set(NUMBER_RE.findall(original)):
+    anchors = _load_hard_anchor_contract()
+    if anchors is None:
+        return "over_length_hard_anchor_contract_unavailable"
+    anchor_result = anchors.compare(original, candidate)
+    anchor_reason = anchor_result.get("reason")
+    if anchor_reason == "numbers":
         return "over_length_number_added_dropped_or_changed"
-    if set(CJK_QUANTITY_RE.findall(candidate)) != set(CJK_QUANTITY_RE.findall(original)):
+    if anchor_reason == "quantities":
         return "over_length_quantity_added_dropped_or_changed"
-    if not set(QUOTE_RE.findall(original)).issubset(set(QUOTE_RE.findall(candidate))):
+    if anchor_reason == "quotes":
         return "over_length_quote_dropped_or_changed"
+    if anchor_reason == "fields":
+        return "over_length_field_order_or_name_changed"
     if not _headings(original).issubset(_headings(candidate)):
         return "over_length_outline_heading_dropped"
     transition_reason = _status_transition_reason(original, candidate)
@@ -360,6 +378,12 @@ def _revision_instruction(
 def _verdict_instruction(
     request: str, original: str, candidate: str, spec: dict[str, Any]
 ) -> str:
+    anchors = _load_hard_anchor_contract()
+    anchor_relations = (
+        anchors.compare(original, candidate).get("relation_packet", [])
+        if anchors is not None
+        else []
+    )
     skeleton = {
         "schema_version": SCHEMA_VERSION,
         "request_sha256": _sha256_text(request),
@@ -379,6 +403,8 @@ def _verdict_instruction(
         "只读核验压缩稿相对原始稿的变化，只输出一个JSON对象。"
         "删除零增量复述、客套和胶水可以通过；句式、段落合并可以变化。"
         "遗漏独立事实、状态、主体、职责、关系或必需结构，改变未决强度，或者新增具体内容，均须FAIL。"
+        "候选以等义总量句明确承载同一主体、对象和范围时，不要求重复保留原稿中的范围自证；"
+        "只有范围缩小、主体或对象换位、事项遗漏或状态改变才按关系丢失处理。"
         "还要跨段检查同义重复：前文已经完整列出职责、原因、理由或目的，结尾只换成‘继续做好、持续推进、"
         "有序推进’再次列举而没有新状态、新要求或新关系时，natural_and_non_repetitive必须为false并FAIL。"
         "不要因为更短而降低标准，也不要把正常精简误判为事实缺失；不确定即FAIL。\n"
@@ -386,6 +412,7 @@ def _verdict_instruction(
         + "\n【原请求】\n" + request
         + "\n【原始稿】\n" + original
         + "\n【压缩稿】\n" + candidate
+        + "\n【共享硬锚关系复核项】\n" + json.dumps(anchor_relations, ensure_ascii=False)
         + "\n【篇幅规格】\n" + json.dumps(spec, ensure_ascii=False)
     )
 
diff --git a/chinese-official-writing/hooks/capabilities/under_length/runtime.py b/chinese-official-writing/hooks/capabilities/under_length/runtime.py
index fd774169..bced737e 100644
--- a/chinese-official-writing/hooks/capabilities/under_length/runtime.py
+++ b/chinese-official-writing/hooks/capabilities/under_length/runtime.py
@@ -11,9 +11,12 @@ from __future__ import annotations
 
 from difflib import SequenceMatcher
 import hashlib
+import importlib.util
 import json
 import math
+from pathlib import Path
 import re
+import sys
 from typing import Any, Final
 
 
@@ -60,11 +63,6 @@ EXPLICIT_TITLE_RE: Final = re.compile(
 EXPLICIT_FIELD_RE: Final = re.compile(
     r"(?:字段|栏目)\s*(?:为|包括|：|:)\s*([^。；;\n]+)"
 )
-NUMBER_RE: Final = re.compile(r"\d+(?:\.\d+)?")
-CJK_QUANTITY_RE: Final = re.compile(
-    r"[一二三四五六七八九十百千万两]+(?:台|件|项|次|个月|年|天|份|人|套|批|元)"
-)
-QUOTE_RE: Final = re.compile(r"[\"“][^\"”\n]{1,120}[\"”]")
 STATUS_ANCHOR_RE: Final = re.compile(
     r"(?:在办|正在(?:核查|办理|推进|处理|调查|侦办|抢修|统计)|"
     r"尚未|未(?:完成|确定|实施|形成|办结)|拟(?:议|定|完善|优化|改进)|待(?:定|核)|"
@@ -90,6 +88,22 @@ MARKDOWN_HEADING_RE: Final = re.compile(r"^\s*#{1,6}\s+")
 NUMBERED_HEADING_RE: Final = re.compile(
     r"^\s*(?:[一二三四五六七八九十]+、|\d+[.、])\s*\S+$"
 )
+HARD_ANCHOR_PATH: Final = Path(__file__).resolve().parents[2] / "shared" / "hard_anchors.py"
+
+
+def _load_hard_anchor_contract() -> Any | None:
+    try:
+        spec = importlib.util.spec_from_file_location(
+            "cow_under_length_hard_anchors", HARD_ANCHOR_PATH
+        )
+        if spec is None or spec.loader is None:
+            return None
+        module = importlib.util.module_from_spec(spec)
+        sys.modules[spec.name] = module
+        spec.loader.exec_module(module)
+    except Exception:
+        return None
+    return module
 
 
 def _sha256_text(value: str) -> str:
@@ -219,25 +233,28 @@ def mechanical_reason(
     maximum = int(spec.get("maximum") or 0)
     if maximum and candidate_length > maximum:
         return "under_length_candidate_above_maximum"
-    original_numbers = set(NUMBER_RE.findall(original))
-    candidate_numbers = set(NUMBER_RE.findall(candidate))
-    request_numbers = set(NUMBER_RE.findall(request)) - {
+    anchors = _load_hard_anchor_contract()
+    if anchors is None:
+        return "under_length_hard_anchor_contract_unavailable"
+    ignored_values = {
         str(spec["minimum"]),
         str(spec.get("maximum") or 0),
     }
-    if not original_numbers.issubset(candidate_numbers) or not candidate_numbers.issubset(
-        original_numbers | request_numbers
-    ):
+    anchor_result = anchors.compare(
+        original,
+        candidate,
+        request,
+        ignored_authority_values=ignored_values,
+    )
+    anchor_reason = anchor_result.get("reason")
+    if anchor_reason == "numbers":
         return "under_length_number_added_dropped_or_changed"
-    original_quantities = set(CJK_QUANTITY_RE.findall(original))
-    candidate_quantities = set(CJK_QUANTITY_RE.findall(candidate))
-    request_quantities = set(CJK_QUANTITY_RE.findall(request))
-    if not original_quantities.issubset(
-        candidate_quantities
-    ) or not candidate_quantities.issubset(original_quantities | request_quantities):
+    if anchor_reason == "quantities":
         return "under_length_quantity_added_dropped_or_changed"
-    if not set(QUOTE_RE.findall(original)).issubset(set(QUOTE_RE.findall(candidate))):
+    if anchor_reason == "quotes":
         return "under_length_quote_dropped_or_changed"
+    if anchor_reason == "fields":
+        return "under_length_field_order_or_name_changed"
     for label in _required_labels(request):
         if label not in candidate:
             return "under_length_explicit_title_or_field_dropped"
@@ -324,6 +341,18 @@ def _verdict_instruction(
     spec: dict[str, Any],
     increments: list[dict[str, Any]],
 ) -> str:
+    anchors = _load_hard_anchor_contract()
+    ignored_values = {str(spec["minimum"]), str(spec.get("maximum") or 0)}
+    anchor_relations = (
+        anchors.compare(
+            original,
+            candidate,
+            request,
+            ignored_authority_values=ignored_values,
+        ).get("relation_packet", [])
+        if anchors is not None
+        else []
+    )
     response = {
         "schema_version": SCHEMA_VERSION,
         "request_sha256": _sha256_text(request),
@@ -348,6 +377,8 @@ def _verdict_instruction(
         "决定、结果或状态升级，以及材料未写明的场景、原因、目的、作用、影响、评价、体验、反馈内容、"
         "工作成效、保障作用、资金充分性或规范化目标，必须标 new_specific_fact 并 FAIL。"
         "透明分类和真实归纳不能只因换了概括词而失败，但不得借概括补入新的事实判断。"
+        "候选以等义总量句明确承载同一主体、对象和范围时，不要求重复保留原稿中的范围自证；"
+        "只有范围缩小、主体或对象换位、事项遗漏或状态改变才按关系丢失处理。"
         "以保护性外扩、重复、自证或空话凑字也必须 FAIL。"
         "凡 D1 新增通知、督促、落实、准备、报送方式、会议纪律、协调办法等动作或义务，而原请求或 D0 "
         "没有同一事项授权，均属新增流程或职责，不得标为 restatement。"
@@ -356,6 +387,7 @@ def _verdict_instruction(
         + "\n【原请求】\n" + request
         + "\n【D0】\n" + original
         + "\n【D1】\n" + candidate
+        + "\n【共享硬锚关系复核项】\n" + json.dumps(anchor_relations, ensure_ascii=False)
         + "\n【冻结增量】\n" + json.dumps(increments, ensure_ascii=False)
         + "\n【篇幅规格】\n" + json.dumps(spec, ensure_ascii=False)
     )
diff --git a/chinese-official-writing/hooks/shared/hard_anchors.py b/chinese-official-writing/hooks/shared/hard_anchors.py
new file mode 100644
index 00000000..df86a21d
--- /dev/null
+++ b/chinese-official-writing/hooks/shared/hard_anchors.py
@@ -0,0 +1,205 @@
+#!/usr/bin/env python3
+"""Shared hard-anchor snapshots for bounded Hook revisions."""
+
+from __future__ import annotations
+
+from collections import Counter
+from dataclasses import asdict, dataclass
+import re
+from typing import Any, Final, Iterable
+
+
+NUMBER_RE: Final = re.compile(
+    r"(?<![A-Za-z0-9])\d+(?:\.\d+)?(?:万元|元|年|月|日|时|分|秒|台|件|项|人次|人|页|份|条|个|号)?(?![A-Za-z0-9])"
+)
+CJK_QUANTITY_RE: Final = re.compile(
+    r"[一二三四五六七八九十百千万两]+(?:台|件|项|次|个月|年|天|份|人|套|批|元)"
+)
+QUOTE_RE: Final = re.compile(r"“[^”\n]+”|‘[^’\n]+’|\"[^\"\n]+\"")
+FIELD_RE: Final = re.compile(r"(?m)^(?P<label>[\u4e00-\u9fffA-Za-z][^：:\n]{0,18})[：:]")
+STATE_CUE_RE: Final = re.compile(r"拟|尚未|未形成|正在|仍在|待核实|待审批|待研究")
+CLAUSE_BOUNDARY_RE: Final = re.compile(r"[\n。！？；;]")
+
+
+@dataclass(frozen=True)
+class AnchorOccurrence:
+    kind: str
+    value: str
+    start: int
+    end: int
+    context: str
+
+
+@dataclass(frozen=True)
+class AnchorSnapshot:
+    numbers: tuple[AnchorOccurrence, ...]
+    quantities: tuple[AnchorOccurrence, ...]
+    quotes: tuple[AnchorOccurrence, ...]
+    fields: tuple[str, ...]
+    state_contexts: tuple[str, ...]
+
+    def to_payload(self) -> dict[str, Any]:
+        return {
+            "numbers": [asdict(item) for item in self.numbers],
+            "quantities": [asdict(item) for item in self.quantities],
+            "quotes": [asdict(item) for item in self.quotes],
+            "fields": list(self.fields),
+            "state_contexts": list(self.state_contexts),
+        }
+
+
+def _normalized_clause(text: str, start: int, end: int) -> str:
+    left = max(
+        (match.end() for match in CLAUSE_BOUNDARY_RE.finditer(text, 0, start)),
+        default=0,
+    )
+    right_match = CLAUSE_BOUNDARY_RE.search(text, end)
+    right = right_match.start() if right_match else len(text)
+    return re.sub(r"\s+", "", text[left:right].strip())
+
+
+def _occurrences(
+    text: str, pattern: re.Pattern[str], kind: str
+) -> tuple[AnchorOccurrence, ...]:
+    return tuple(
+        AnchorOccurrence(
+            kind=kind,
+            value=match.group(0),
+            start=match.start(),
+            end=match.end(),
+            context=_normalized_clause(text, match.start(), match.end()),
+        )
+        for match in pattern.finditer(text)
+    )
+
+
+def snapshot(text: str) -> AnchorSnapshot:
+    return AnchorSnapshot(
+        numbers=_occurrences(text, NUMBER_RE, "number"),
+        quantities=_occurrences(text, CJK_QUANTITY_RE, "quantity"),
+        quotes=_occurrences(text, QUOTE_RE, "quote"),
+        fields=tuple(match.group("label").strip() for match in FIELD_RE.finditer(text)),
+        state_contexts=tuple(
+            re.sub(r"\s+", "", clause)
+            for clause in CLAUSE_BOUNDARY_RE.split(text)
+            if STATE_CUE_RE.search(clause)
+        ),
+    )
+
+
+def _counter(items: Iterable[AnchorOccurrence]) -> Counter[str]:
+    return Counter(item.value for item in items)
+
+
+def _filtered_authority_counter(
+    items: Iterable[AnchorOccurrence], ignored_values: set[str]
+) -> Counter[str]:
+    return Counter(item.value for item in items if item.value not in ignored_values)
+
+
+def _contexts_by_value(items: Iterable[AnchorOccurrence]) -> dict[str, list[str]]:
+    result: dict[str, list[str]] = {}
+    for item in items:
+        result.setdefault(item.value, []).append(item.context)
+    return result
+
+
+def _relation_items(
+    original: AnchorSnapshot, candidate: AnchorSnapshot
+) -> list[dict[str, Any]]:
+    relations: list[dict[str, Any]] = []
+    for kind in ("numbers", "quantities", "quotes"):
+        before = _contexts_by_value(getattr(original, kind))
+        after = _contexts_by_value(getattr(candidate, kind))
+        for value in sorted(set(before) & set(after)):
+            if before[value] != after[value]:
+                relations.append(
+                    {
+                        "kind": kind[:-1],
+                        "value": value,
+                        "original_contexts": before[value],
+                        "candidate_contexts": after[value],
+                        "check": "same_subject_object_matter_and_state",
+                    }
+                )
+    if original.state_contexts != candidate.state_contexts:
+        relations.append(
+            {
+                "kind": "state",
+                "original_contexts": list(original.state_contexts),
+                "candidate_contexts": list(candidate.state_contexts),
+                "check": "no_pending_or_planned_state_upgrade",
+            }
+        )
+    return relations
+
+
+def _missing_and_added(
+    original: Iterable[AnchorOccurrence],
+    candidate: Iterable[AnchorOccurrence],
+    authority: Iterable[AnchorOccurrence],
+    ignored_values: set[str],
+) -> tuple[list[str], list[str]]:
+    original_counter = _counter(original)
+    candidate_counter = _counter(candidate)
+    allowed = original_counter | _filtered_authority_counter(authority, ignored_values)
+    missing = sorted(value for value in original_counter if candidate_counter[value] == 0)
+    added = sorted(value for value in candidate_counter if allowed[value] == 0)
+    return missing, added
+
+
+def compare(
+    original_text: str,
+    candidate_text: str,
+    authority_text: str = "",
+    *,
+    ignored_authority_values: Iterable[str] = (),
+) -> dict[str, Any]:
+    original = snapshot(original_text)
+    candidate = snapshot(candidate_text)
+    authority = snapshot(authority_text)
+    ignored = set(ignored_authority_values)
+    violations: dict[str, Any] = {}
+    for kind in ("numbers", "quantities", "quotes"):
+        missing, added = _missing_and_added(
+            getattr(original, kind),
+            getattr(candidate, kind),
+            getattr(authority, kind),
+            ignored,
+        )
+        violations[f"missing_{kind}"] = missing
+        violations[f"added_{kind}"] = added
+    violations["fields_changed"] = candidate.fields != original.fields
+    reason = next(
+        (
+            kind
+            for kind in ("numbers", "quantities", "quotes")
+            if violations[f"missing_{kind}"] or violations[f"added_{kind}"]
+        ),
+        "fields" if violations["fields_changed"] else None,
+    )
+    reductions: list[dict[str, Any]] = []
+    for kind in ("numbers", "quantities", "quotes"):
+        before = _counter(getattr(original, kind))
+        after = _counter(getattr(candidate, kind))
+        reductions.extend(
+            {
+                "kind": kind[:-1],
+                "value": value,
+                "before": count,
+                "after": after[value],
+            }
+            for value, count in sorted(before.items())
+            if 0 < after[value] < count
+        )
+    relations = [] if reason else _relation_items(original, candidate)
+    return {
+        "status": "fallback" if reason else ("semantic_review_required" if relations else "pass"),
+        "mechanical_ok": reason is None,
+        "reason": reason,
+        "violations": violations,
+        "count_reductions": reductions,
+        "relation_packet": relations,
+        "original": original.to_payload(),
+        "candidate": candidate.to_payload(),
+    }
diff --git a/chinese-official-writing/references/anti-ai-patterns.md b/chinese-official-writing/references/anti-ai-patterns.md
index 960f456f..c0b4ad50 100644
--- a/chinese-official-writing/references/anti-ai-patterns.md
+++ b/chinese-official-writing/references/anti-ai-patterns.md
@@ -20,7 +20,7 @@
 - **虚假对比**：两项内容并非相反、替代或递进关系，现有事实只支持其中一项，仍写成强对照或强递进。
 - **机械重复**：同一词、固定搭配、句式骨架或段落开头集中复现，删减或改写不会损失办理逻辑和必要强调。
 
-真实方案比较、法律政策要求、职责边界、风险提示、直接引语和必须统一使用的专业术语不按上述问题处理。模型只对已经确认有问题的局部做语义重写：连续否定按上述方式处理，虚假对比改回材料支持的关系，机械重复按具体事项自然合并或改写。不得自动批量替换，不得为避重复改动事实、引用、术语、否定范围和论断强度；不得把 `未`、`不`、`不得` 移到别的对象，也不得把 `拟`、`建议`、`可` 提升为 `应`、`必须` 或既定结论。
+保留对办理有用的事实、状态、法律政策要求、职责边界、风险提示、直接引语和专业术语。只调整已经确认没有新增办理作用的局部，不得自动批量替换；虚假对比改回材料支持的关系，机械重复合并为一处明确表述。材料没有给出具体后续安排、责任、程序、承诺或效果时，正文写到现有事实和状态为止，不为显得完整另补动作。局部调整以事实单元为界，主体、对象、引用、术语、否定范围和论断强度保持不变；不得把 `未`、`不`、`不得` 移到别的对象，`拟`、`建议`、`可` 不升级为既定结论。
 
 改后逐处回看上下文。未确认有问题的句子、真实比较和必要否定保持原样。用户只要求检测时，严格服从其指定的字段、顺序和格式；未指定时仍按位置、风险层级和修改建议输出，原句和问题依据按需补充，不代写全文。用户要求改写时，只改确认有问题的句子及必要衔接，其余正文保持不动。
 
diff --git a/chinese-official-writing/references/genre-playbook-request.md b/chinese-official-writing/references/genre-playbook-request.md
index f4de19d6..5d702433 100644
--- a/chinese-official-writing/references/genre-playbook-request.md
+++ b/chinese-official-writing/references/genre-playbook-request.md
@@ -14,5 +14,5 @@
 - 骨架：请批事项 -> 依据和必要性 -> 方案/金额/资源 -> 风险控制 -> 请批语。
 - 风险：请示一文一事；申请可保留用户模板和称呼，不因出现“妥否，请批示”就强行改成请示。请示、报告和上报申请的主送机关、发文或申请单位、成文日期属于正式报送结构要素；未知时不编造泛称，也不在正文留未完成占位，按 `information-selection.md` 作为实质缺口处理。
 - 单项采购申请用一至两个自然段连贯呈现已给的品名规格、数量和金额。多品类、分项核算、比价验收、技术附件或明确长篇任务转读 `workflow.md`、`handling-elements.md` 和 `argument-chains.md`；字段表格保持原结构。
-- 材料只写设备老旧时，不推成运行缓慢、性能不足、影响服务或群众体验；材料只写采购正在推进时，用一句保留当前状态，不补依法依规、预算控制、采购流程、完成承诺、效能提升或后续环节。事实不足以撑满字数下限时，按 `information-selection.md` 短而完整地成稿。
+- 材料只写设备老旧时，不推成运行缓慢、性能不足、影响服务或群众体验；材料只写采购正在推进时，用一句保留当前状态，不补依法依规、预算控制、采购流程、完成承诺、效能提升或后续环节。材料只写供应商尚未确定时，正文停在该状态，不补确定后或批准后如何采购、报告、到货、验收、付款。事实不足以撑满字数下限时，按 `information-selection.md` 短而完整地成稿。
 - 补充读取：`argument-chains.md` 的请示和请批附件、`formal-addressing.md`。
```
