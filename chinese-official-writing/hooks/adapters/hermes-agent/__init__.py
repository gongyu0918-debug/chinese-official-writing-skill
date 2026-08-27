"""Hermes Agent lifecycle bridge for one bounded final-review call."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import logging
import os
from pathlib import Path
import sys
import threading
import time
from typing import Any, Final


# Hermes initializes its central root file handlers after plugins are imported
# and may disable every pre-existing named logger.  The root logger remains the
# supported propagation endpoint for late lifecycle records.
logger = logging.getLogger()
DEBUG_AUDIT: Final = os.getenv("HERMES_PLUGINS_DEBUG", "").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
PLUGIN_ROOT: Final = Path(__file__).resolve().parent
SKILL_ROOT: Final = PLUGIN_ROOT / "skills" / "chinese-official-writing"
PLUGIN_SKILL: Final = "chinese-official-writing-gate:chinese-official-writing"
CAPABILITY_PATH: Final = PLUGIN_ROOT / "hook-capability.json"
SUPPORTED_CAPABILITY: Final = "delivery_review"
PRELOAD_BIND_WINDOW_SECONDS: Final = 30.0
QUERY_FLAGS: Final = frozenset({"-q", "--query"})
QUERY_FILE_FLAG: Final = "--query-file"
RESUME_FLAGS: Final = frozenset({"-r", "--resume", "-c", "--continue"})
ONESHOT_FLAGS: Final = frozenset({"-z", "--oneshot"})

_lock = threading.RLock()
_turns: dict[str, dict[str, Any]] = {}
_active_sessions: set[str] = set()
_pending_cli_preloads: dict[str, float] = {}
_disabled_sessions: set[str] = set()


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load required companion module: {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _selected_capability() -> str:
    try:
        payload = json.loads(CAPABILITY_PATH.read_text(encoding="utf-8"))
    except (OSError, TypeError, json.JSONDecodeError):
        return ""
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        return ""
    value = payload.get("capability")
    return value if isinstance(value, str) else ""


def _session_key(value: Any) -> str:
    return str(value or "__empty_session__")


def _summary(text: str) -> tuple[int, str]:
    return len(text), hashlib.sha256(text.encode("utf-8")).hexdigest()


def _is_new_single_query_cli(argv: list[str] | None = None) -> bool:
    """Accept only a fresh ``hermes chat`` single-query process.

    Hermes 0.20.5-0.20.6 persists the assistant message before
    ``transform_llm_output``.  A transformed D1 is therefore safe only as a
    disposable single-query delivery; resuming that session would replay D0.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    # The supported invocation deliberately keeps ``chat`` as the first
    # command token.  Fail closed instead of mistaking a later argument such
    # as ``gateway chat -q ...`` for the chat subcommand.
    if not args or args[0] != "chat":
        return False
    has_inline_query = any(
        value in QUERY_FLAGS or value.startswith("--query=") for value in args
    )
    has_query_file = any(
        value == QUERY_FILE_FLAG or value.startswith("--query-file=")
        for value in args
    )
    has_resume = any(
        value in RESUME_FLAGS
        or value.startswith("--resume=")
        or value.startswith("--continue=")
        for value in args
    )
    has_oneshot = any(
        value in ONESHOT_FLAGS or value.startswith("--oneshot=") for value in args
    )
    return has_inline_query != has_query_file and not has_resume and not has_oneshot


def _last_assistant_text(history: Any) -> str | None:
    if not isinstance(history, list):
        return None
    for message in reversed(history):
        if not isinstance(message, dict) or message.get("role") != "assistant":
            continue
        content = message.get("content")
        return content if isinstance(content, str) else None
    return None


def _store_expected(key: str, owner: object, text: str, outcome: str) -> bool:
    chars, digest = _summary(text)
    with _lock:
        current = _turns.get(key)
        if (
            current is None
            or current.get("owner") is not owner
            or key in _disabled_sessions
        ):
            return False
        current["expected_chars"] = chars
        current["expected_hash"] = digest
        current["outcome"] = outcome
        return True


def _audit(message: str, *args: Any) -> None:
    """Emit no-raw-text diagnostics through the host's explicit debug mode."""
    if DEBUG_AUDIT:
        rendered = message % args
        logger.warning("plugin debug: %s", rendered)
        sys.stderr.write(f"[chinese-official-writing-gate] {rendered}\n")
    else:
        logger.info(message, *args)


def register(ctx: Any) -> None:
    if _selected_capability() != SUPPORTED_CAPABILITY:
        raise RuntimeError("Hermes companion currently supports delivery_review only")
    skill_md = SKILL_ROOT / "SKILL.md"
    review_core = _load_module(
        "cow_hermes_single_pass_final_review",
        SKILL_ROOT / "hooks" / "single_pass_final_review.py",
    )
    gate_core = _load_module(
        "cow_hermes_gate_stop_contract",
        SKILL_ROOT / "hooks" / "gate_stop_hook.py",
    )
    ctx.register_skill(
        "chinese-official-writing",
        skill_md,
        "Chinese official-writing Skill bundled with its optional Hermes final review.",
    )

    def on_skill_lifecycle(
        action: str = "",
        skill_name: str = "",
        session_id: str = "",
        task_id: str = "",
        **kwargs: Any,
    ) -> None:
        del kwargs
        matched = action == "loaded" and skill_name == PLUGIN_SKILL
        if DEBUG_AUDIT:
            _audit(
                "chinese-official-writing-gate lifecycle action=%s skill=%s "
                "has_session=%s has_task=%s matched=%s",
                action,
                skill_name,
                bool(session_id),
                bool(task_id),
                matched,
            )
        if not matched:
            return
        if session_id:
            if not _is_new_single_query_cli():
                return
            key = _session_key(session_id)
            with _lock:
                _active_sessions.add(key)
            return
        if not _is_new_single_query_cli():
            return
        preload_key = str(task_id or "")
        if not preload_key:
            return
        with _lock:
            _pending_cli_preloads[preload_key] = time.monotonic()

    def on_session_start(
        session_id: str = "",
        platform: str = "",
        **kwargs: Any,
    ) -> None:
        del kwargs
        now = time.monotonic()
        key = _session_key(session_id)
        supported_surface = platform == "cli" and _is_new_single_query_cli()
        with _lock:
            expired = [
                preload_key
                for preload_key, created_at in _pending_cli_preloads.items()
                if now - created_at > PRELOAD_BIND_WINDOW_SECONDS
            ]
            for preload_key in expired:
                _pending_cli_preloads.pop(preload_key, None)
            pending = len(_pending_cli_preloads)
            exact_pending = key in _pending_cli_preloads
            if exact_pending:
                _pending_cli_preloads.pop(key, None)
            bound = bool(session_id) and supported_surface and exact_pending
            if bound:
                _active_sessions.add(key)
            else:
                _active_sessions.discard(key)
        if DEBUG_AUDIT:
            _audit(
                "chinese-official-writing-gate session_start has_session=%s "
                "platform=%s exact_pending=%s pending=%d bound=%s",
                bool(session_id),
                platform,
                exact_pending,
                pending,
                bound,
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
            armed = key in _active_sessions and key not in _disabled_sessions
            conflict = armed and key in _turns
            if conflict:
                _turns.pop(key, None)
                _active_sessions.discard(key)
                _disabled_sessions.add(key)
                armed = False
            elif armed:
                _turns[key] = {
                    "owner": object(),
                    "task_id": str(task_id or ""),
                    "turn_id": str(turn_id or ""),
                    "request": user_message if isinstance(user_message, str) else "",
                    "attempted": False,
                    "armed": True,
                }
        if DEBUG_AUDIT:
            request_chars, request_hash = _summary(
                user_message if isinstance(user_message, str) else ""
            )
            _audit(
                "chinese-official-writing-gate pre_llm_call armed=%s conflict=%s "
                "request_chars=%d request_sha256=%s",
                armed,
                conflict,
                request_chars,
                request_hash,
            )

    def transform(
        response_text: str,
        session_id: str = "",
        **kwargs: Any,
    ) -> str | None:
        del kwargs
        draft = response_text if isinstance(response_text, str) else ""
        key = _session_key(session_id)
        with _lock:
            current = _turns.get(key)
            if (
                key in _disabled_sessions
                or not current
                or not current.get("armed")
                or current.get("attempted")
            ):
                if DEBUG_AUDIT:
                    _audit(
                        "chinese-official-writing-gate transform skipped "
                        "state=%s armed=%s attempted=%s",
                        bool(current),
                        bool(current and current.get("armed")),
                        bool(current and current.get("attempted")),
                    )
                return None
            current["attempted"] = True
            request = str(current.get("request") or "")
            owner = current["owner"]
        if not request.strip() or not draft.strip():
            return None
        if gate_core._requests_hook_opt_out(request) or gate_core._is_review_only_request(
            request
        ):
            _store_expected(key, owner, draft, "SKIP")
            return None

        try:
            result = ctx.llm.complete(
                review_core.build_messages(request, draft),
                temperature=0,
                max_tokens=review_core.max_output_tokens(draft),
                timeout=120,
                purpose="chinese-official-writing bounded final review",
            )
            selection = review_core.parse_selection(result.text, draft, request)
        except Exception as exc:
            _store_expected(key, owner, draft, "FAIL_OPEN")
            logger.warning(
                "chinese-official-writing-gate final review failed open: %s",
                type(exc).__name__,
            )
            return None

        before_chars, before_hash = _summary(draft)
        after_chars, after_hash = _summary(selection.text)
        with _lock:
            current = _turns.get(key)
            if (
                current is not None
                and current.get("owner") is owner
                and key not in _disabled_sessions
            ):
                current["expected_chars"] = after_chars
                current["expected_hash"] = after_hash
                current["outcome"] = selection.action
                _audit(
                    "chinese-official-writing-gate final review action=%s "
                    "reason=%s before_chars=%d after_chars=%d "
                    "before_sha256=%s after_sha256=%s",
                    selection.action,
                    selection.reason,
                    before_chars,
                    after_chars,
                    before_hash,
                    after_hash,
                )
                # The owner recheck, expected-hash commit, audit, and return
                # form one linearized step.  A second pre hook cannot replace
                # the turn state between the check and the D1 decision.
                return selection.text if selection.action == "REPLACE" else None
        _audit(
            "chinese-official-writing-gate final review discarded "
            "owner_lost=true before_chars=%d before_sha256=%s",
            before_chars,
            before_hash,
        )
        return None

    def after(
        session_id: str = "",
        task_id: str = "",
        turn_id: str = "",
        assistant_response: str = "",
        conversation_history: Any = None,
        **kwargs: Any,
    ) -> None:
        del kwargs
        key = _session_key(session_id)
        with _lock:
            current = _turns.pop(key, None)
            _active_sessions.discard(key)
        if not current:
            return

        expected_task = str(current.get("task_id") or "")
        expected_turn = str(current.get("turn_id") or "")
        observed_task = str(task_id or "")
        observed_turn = str(turn_id or "")
        task_match = bool(expected_task) and expected_task == observed_task
        turn_match = bool(expected_turn) and expected_turn == observed_turn
        expected_hash = str(current.get("expected_hash") or "")
        response = assistant_response if isinstance(assistant_response, str) else ""
        response_chars, response_hash = _summary(response)
        response_match = bool(expected_hash) and expected_hash == response_hash
        history_text = _last_assistant_text(conversation_history)
        history_match = (
            None
            if history_text is None or not expected_hash
            else _summary(history_text)[1] == expected_hash
        )
        if not (task_match and turn_match and response_match):
            with _lock:
                _disabled_sessions.add(key)
        _audit(
            "chinese-official-writing-gate post_llm_call outcome=%s "
            "task_match=%s turn_match=%s response_match=%s history_match=%s "
            "response_chars=%d response_sha256=%s",
            str(current.get("outcome") or "UNKNOWN"),
            task_match,
            turn_match,
            response_match,
            "unknown" if history_match is None else history_match,
            response_chars,
            response_hash,
        )

    def close_session(session_id: str = "", **kwargs: Any) -> None:
        del kwargs
        key = _session_key(session_id)
        with _lock:
            _turns.pop(key, None)
            _active_sessions.discard(key)
            _disabled_sessions.discard(key)
            _pending_cli_preloads.pop(key, None)

    ctx.register_hook("on_skill_lifecycle", on_skill_lifecycle)
    ctx.register_hook("on_session_start", on_session_start)
    ctx.register_hook("pre_llm_call", before)
    ctx.register_hook("transform_llm_output", transform)
    ctx.register_hook("post_llm_call", after)
    ctx.register_hook("on_session_finalize", close_session)
    ctx.register_hook("on_session_reset", close_session)
