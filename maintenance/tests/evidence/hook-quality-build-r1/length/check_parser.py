"""Small deterministic parser controls; report failures without changing fixtures."""
from __future__ import annotations

import json
from run import HERE, RUNTIME, GATE, load, save

runtime = load("length_controls_runtime", HERE / "product/candidate" / RUNTIME)
gate = load("length_controls_gate", HERE / "product/candidate" / GATE)
cases = [
    ("P6", "现在把全文压到700字以内，标题也算在内。", 700, "full"),
    ("M6", "请把最新稿压缩到500字以内，直接发纪要正文。", 500, "full"),
    ("body", "请把正文压到500字以内。", 500, "body"),
    ("quoted_material", "请解释附件中‘请把全文压缩到500字以内’这一条要求。", None, None),
    ("quoted_expression", "请评价“压缩到500字以内”的表述。", None, None),
    ("unquoted_material", "材料写明全文压到500字以内，解释这一条。", None, None),
    ("approx_prefix", "请把全文压缩到约500字以内。", None, None),
    ("approx_suffix", "请把全文压缩到500字以内左右。", None, None),
    ("approx_around", "请把全文压缩到500字以内上下。", None, None),
    ("review_question", "请只审稿，不改写；检查是否需要压缩到500字以内。", None, None),
]
rows = []
for case_id, request, maximum, scope in cases:
    spec = runtime.parse_spec(request)
    bounds = gate._length_bounds(request)
    actual = None if spec is None else spec["maximum"]
    ok = actual == maximum and bounds[1] == maximum
    if spec is not None and scope is not None:
        ok = ok and spec["scope"] == scope
    rows.append({"id": case_id, "request": request, "expected_maximum": maximum,
                 "over_length_spec": spec, "review_gate_bounds": bounds, "pass": ok})
thresholds = []
for count in (110, 111):
    record = {"request": "请把全文压到100字以内。"}
    triggered = runtime.start({"last_assistant_message": "甲" * count}, record) is not None
    thresholds.append({"count": count, "maximum": 100, "ratio": runtime.OVER_TOLERANCE_RATIO,
                       "triggered": triggered, "pass": triggered == (count == 111)})
result = {"scope": "Frozen candidate parser and direct runtime controls; no model and no native Hook.",
          "rows": rows, "tolerance_controls": thresholds,
          "passed": sum(r["pass"] for r in rows + thresholds),
          "failed": sum(not r["pass"] for r in rows + thresholds),
          "status": "HOLD_REVIEW_QUESTION_BOUNDARY" if any(not r["pass"] for r in rows) else "PASS"}
save(HERE / "parser-controls.json", result)
print(json.dumps(result, ensure_ascii=False))
raise SystemExit(1 if result["failed"] else 0)
