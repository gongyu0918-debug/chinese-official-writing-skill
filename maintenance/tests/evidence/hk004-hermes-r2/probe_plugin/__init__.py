"""Isolated Hermes R2 lifecycle probe; never shipped as a product plugin."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import threading
import time
from typing import Any


PLUGIN_SKILL = "hk004-hermes-r2:chinese-official-writing"
MARKER_D0 = "HA_R2_D0"
MARKER_D1 = "HA_R2_D1"
ALLOWED_ISSUES = frozenset(
    {
        "NEW_FACT_OR_PROCEDURE",
        "STATE_UPGRADE",
        "SCOPE_EXPANSION",
        "REPETITION_OR_TITLE",
        "WRAPPER_OR_GENRE",
        "STRUCTURE_IMBALANCE",
    }
)
REVIEW_INSTRUCTIONS = """你是中文正式事务文稿的单次写后审稿器。输入含原始任务和完整初稿 D0。

只判断 D0 是否存在下列明确问题：事实、数字、完整日期、主体、范围或未决状态被改变；把拟议、待定、可安排、预期作用写成既成事实；新增材料外程序、责任主体、期限或承诺；文种或发布者角色错位；正文外过程说明、自评、字数、Markdown 围栏；结构明显失衡或不能直接使用。

基于给定事实和常识的一层合理原因、低强度预期作用、必要结论和承接不是天然风险，不得因谨慎而机械删除，也不得为了短而削薄事务性文稿。原稿安全时必须 KEEP。只有存在明确问题且能一次完整、安全修正时才 REPLACE。

逐项检查后再决定，但不要输出检查过程：

1. 合理推断只能从已给需求、现状或活动直接落到一层目的、预期作用或低强度意义；“需求持续增长”“后续业务已有安排”“待确定后另行报批”等新增趋势、程序和承诺，不因听起来常见就成为已给事实。采购材料若只给出利用率、排队、拟购和待定事项，不得另造“设备检修或故障时缺少冗余”“增购后留出冗余”等现状、风险或目的；可以保留与已给事实直接相连的“缓解资源紧张、减少排队、提升任务处理时效”等一层预期作用。
2. 人数、完成环节和单人引语分别约束谓语覆盖范围；材料只支持部分人员完成或一人感受时，“参训人员”“参与人员”“大家”等无数量限定的集合主体按全部参加者理解，不能承接“熟悉、掌握、提升、增强”等成效谓语。应改为材料明确的完成者/部分人员，或改写为活动层面的“提供机会、搭建平台”等低强度作用。
3. 标题检查“关于有关”等叠词；相邻句若只是换词重复同一主体、动作、对象和状态，没有新增原因、影响、结论或办理作用，应合并，不以分项标题加同义正文机械凑长。
4. REPLACE 采用最小修订。含数字、数量、完整日期、引语或“拟、尚未、待定、可安排”等状态硬锚的句子，除删除句内明确错误外，不与相邻句合并、不拆分、不移动，不改变其主体、对象和状态关系。

返回唯一、严格的 JSON 对象，不加 Markdown 围栏或对象外文字。action 只能是 KEEP 或 REPLACE；issues 只能从 NEW_FACT_OR_PROCEDURE、STATE_UPGRADE、SCOPE_EXPANSION、REPETITION_OR_TITLE、WRAPPER_OR_GENRE、STRUCTURE_IMBALANCE 中选择。KEEP 时 issues 必须为空且 final_text 必须与 D0 逐字一致；REPLACE 时 issues 至少一项，final_text 只放可直接使用的完整正文，不附说明、自评、字数、横线或代码围栏。不得虚构输入外事实。"""

_lock = threading.RLock()
_turns: dict[str, dict[str, Any]] = {}
_active_sessions: set[str] = set()
_pending_cli_preloads: dict[str, float] = {}
PRELOAD_BIND_WINDOW_SECONDS = 30.0


def _digest(text: Any) -> dict[str, Any]:
    value = text if isinstance(text, str) else ""
    return {
        "chars": len(value),
        "sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(),
        "has_d0": MARKER_D0 in value,
        "has_d1": MARKER_D1 in value,
    }


def _record(event: str, **fields: Any) -> None:
    raw = os.environ.get("COW_HERMES_R2_EVIDENCE_DIR")
    if not raw:
        return
    root = Path(raw).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    payload = {"event": event, **fields}
    with _lock:
        with (root / "events.jsonl").open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def _capture_text(label: str, session_id: str, text: str) -> None:
    if os.environ.get("COW_HERMES_R2_CAPTURE_RAW") != "1":
        return
    raw = os.environ.get("COW_HERMES_R2_EVIDENCE_DIR")
    if not raw:
        return
    root = Path(raw).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    safe_session = re.sub(r"[^A-Za-z0-9_.-]+", "_", session_id)[:120] or "session"
    (root / f"{safe_session}.{label}.txt").write_text(
        text, encoding="utf-8", newline="\n"
    )


def _session_key(session_id: Any) -> str:
    return str(session_id or "__empty_session__")


def _valid_selection(parsed: Any, d0: str) -> tuple[str, str] | None:
    if not isinstance(parsed, dict):
        return None
    action = parsed.get("action")
    issues = parsed.get("issues")
    final_text = parsed.get("final_text")
    if (
        action not in {"KEEP", "REPLACE"}
        or not isinstance(issues, list)
        or not all(isinstance(item, str) and item in ALLOWED_ISSUES for item in issues)
        or len(set(issues)) != len(issues)
        or not isinstance(final_text, str)
    ):
        return None
    if not final_text.strip() or len(final_text) > max(12000, len(d0) * 2 + 1000):
        return None
    if action == "KEEP" and (issues or final_text != d0):
        return None
    if action == "REPLACE" and not issues:
        return None
    return action, final_text


def register(ctx: Any) -> None:
    raw_skill_root = os.environ.get("COW_HERMES_R2_SKILL_ROOT")
    if not raw_skill_root:
        raise RuntimeError("COW_HERMES_R2_SKILL_ROOT is required")
    skill_md = Path(raw_skill_root).expanduser().resolve() / "SKILL.md"
    ctx.register_skill(
        "chinese-official-writing",
        skill_md,
        "Current-checkout Chinese official-writing Skill for isolated HK-004 R2 tests.",
    )

    def before(
        session_id: str = "",
        task_id: str = "",
        turn_id: str = "",
        user_message: str = "",
        **kwargs: Any,
    ) -> None:
        del kwargs
        key = _session_key(session_id)
        with _lock:
            current = _turns.setdefault(key, {})
            current.update(
                {
                    "task_id": str(task_id or ""),
                    "turn_id": str(turn_id or ""),
                    "request": user_message if isinstance(user_message, str) else "",
                    "attempted": False,
                    "armed": key in _active_sessions,
                }
            )
        _record(
            "pre_llm_call",
            session_id=key,
            task_id=str(task_id or ""),
            turn_id=str(turn_id or ""),
            request=_digest(user_message),
        )

    def skill_lifecycle(
        action: str = "",
        skill_name: str = "",
        provenance: str = "",
        task_id: str = "",
        session_id: str = "",
        **kwargs: Any,
    ) -> None:
        del kwargs
        matched = action == "loaded" and skill_name == PLUGIN_SKILL
        key = _session_key(session_id)
        if matched:
            if session_id:
                with _lock:
                    _active_sessions.add(key)
                    current = _turns.setdefault(key, {})
                    current["armed"] = True
                    current["skill_task_id"] = str(task_id or "")
            else:
                preload_key = str(task_id or "")
                if preload_key:
                    with _lock:
                        _pending_cli_preloads[preload_key] = time.monotonic()
        _record(
            "on_skill_lifecycle",
            session_id=key,
            task_id=str(task_id or ""),
            action=action,
            skill_name=skill_name,
            provenance=provenance,
            matched=matched,
        )

    def session_start(
        session_id: str = "",
        platform: str = "",
        **kwargs: Any,
    ) -> None:
        del kwargs
        key = _session_key(session_id)
        now = time.monotonic()
        with _lock:
            expired = [
                preload_key
                for preload_key, created_at in _pending_cli_preloads.items()
                if now - created_at > PRELOAD_BIND_WINDOW_SECONDS
            ]
            for preload_key in expired:
                _pending_cli_preloads.pop(preload_key, None)
            pending = len(_pending_cli_preloads)
            bound = bool(session_id) and platform == "cli" and key in _pending_cli_preloads
            if bound:
                _pending_cli_preloads.pop(key, None)
                _active_sessions.add(key)
        _record(
            "on_session_start",
            session_id=key,
            platform=platform,
            pending_before=pending,
            bound_preloaded_skill=bound,
        )

    def session_closed(session_id: str = "", **kwargs: Any) -> None:
        del kwargs
        key = _session_key(session_id)
        with _lock:
            _turns.pop(key, None)
            _active_sessions.discard(key)
        _record("session_closed", session_id=key)

    def transform(
        response_text: str,
        session_id: str = "",
        model: str = "",
        platform: str = "",
        **kwargs: Any,
    ) -> str | None:
        del kwargs
        d0 = response_text if isinstance(response_text, str) else ""
        key = _session_key(session_id)
        with _lock:
            current = _turns.get(key)
            if not current or not current.get("armed") or current.get("attempted"):
                _record(
                    "transform_skipped",
                    session_id=key,
                    reason="not_armed_or_already_attempted",
                    response=_digest(d0),
                )
                return None
            current["attempted"] = True
            request = str(current.get("request") or "")

        mode = os.environ.get("COW_HERMES_R2_MODE", "semantic").strip().lower()
        if mode == "fixed":
            fixed_path = os.environ.get("COW_HERMES_R2_FIXED_D0_PATH", "").strip()
            try:
                d0 = Path(fixed_path).expanduser().resolve().read_text(encoding="utf-8")
            except (OSError, RuntimeError):
                _record(
                    "transform_fail_open",
                    session_id=key,
                    reason="fixed_d0_unavailable",
                    response=_digest(d0),
                )
                return None
        if not request:
            _record("transform_fail_open", session_id=key, reason="missing_request", response=_digest(d0))
            return None
        if mode == "marker" and MARKER_D0 not in d0:
            _record("transform_fail_open", session_id=key, reason="marker_d0_missing", response=_digest(d0))
            return None

        if mode == "marker":
            instructions = (
                "Return one JSON object with action REPLACE, issues containing "
                "WRAPPER_OR_GENRE, and final_text exactly "
                f"{MARKER_D1}. Do not add any other characters."
            )
            inputs = [{"type": "text", "text": f"Original response: {d0}"}]
            max_tokens = 128
        else:
            instructions = REVIEW_INSTRUCTIONS
            inputs = [
                {
                    "type": "text",
                    "text": f"原始任务：\n{request}\n\n完整初稿 D0：\n{d0}",
                }
            ]
            max_tokens = 4096

        _record(
            "transform_llm_output",
            session_id=key,
            model=model,
            platform=platform,
            mode=mode,
            response=_digest(d0),
        )
        _capture_text("d0", key, d0)
        try:
            result = ctx.llm.complete(
                [
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": inputs[0]["text"]},
                ],
                temperature=0,
                max_tokens=max_tokens,
                timeout=120,
                purpose="chinese-official-writing bounded final review",
            )
            try:
                parsed = json.loads(result.text.strip())
            except (AttributeError, TypeError, json.JSONDecodeError):
                parsed = None
            selection = _valid_selection(parsed, d0)
            if selection is None:
                _record(
                    "transform_fail_open",
                    session_id=key,
                    reason="invalid_structured_selection",
                    response=_digest(d0),
                )
                return None
            action, final_text = selection
            usage = getattr(result, "usage", None)
            _record(
                "plugin_llm_complete",
                session_id=key,
                action=action,
                provider=getattr(result, "provider", ""),
                model=getattr(result, "model", ""),
                input_tokens=getattr(usage, "input_tokens", 0),
                output_tokens=getattr(usage, "output_tokens", 0),
                total_tokens=getattr(usage, "total_tokens", 0),
                selected=_digest(final_text),
            )
            _capture_text("selected", key, final_text)
            return final_text if final_text != d0 else None
        except Exception as exc:
            _record(
                "transform_fail_open",
                session_id=key,
                reason=type(exc).__name__,
                response=_digest(d0),
            )
            return None

    def after(
        session_id: str = "",
        task_id: str = "",
        turn_id: str = "",
        assistant_response: str = "",
        **kwargs: Any,
    ) -> None:
        del kwargs
        key = _session_key(session_id)
        with _lock:
            current = _turns.pop(key, None)
        _record(
            "post_llm_call",
            session_id=key,
            task_id=str(task_id or ""),
            turn_id=str(turn_id or ""),
            armed=bool(current and current.get("armed")),
            attempted=bool(current and current.get("attempted")),
            response=_digest(assistant_response),
        )

    ctx.register_hook("pre_llm_call", before)
    ctx.register_hook("on_skill_lifecycle", skill_lifecycle)
    ctx.register_hook("on_session_start", session_start)
    ctx.register_hook("transform_llm_output", transform)
    ctx.register_hook("post_llm_call", after)
    ctx.register_hook("on_session_finalize", session_closed)
    ctx.register_hook("on_session_reset", session_closed)
