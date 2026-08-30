#!/usr/bin/env python3
"""Bounded lifecycle bridge for a Candidate AI transaction.

UserPromptSubmit temporarily retains the current raw request. PostToolUse
records that this plugin's Skill was actually read and tracks explicit
review_gate.py calls. If the model reaches Stop without starting the gate, Stop
snapshots the completed assistant draft and drives the bounded
detect/prepare/finalize/emit chain. The agent only supplies one repair decision
and one read-only verdict when needed; the Hook runs every script transition,
verifies the final output hash, and redacts raw turn data after terminal Stop.
"""

from __future__ import annotations

import errno
from contextvars import ContextVar
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any


TERMINAL_STATES = {"TERMINAL_D0", "TERMINAL_D1"}
STATE_AWAITING_REPAIR = "AWAITING_REPAIR"
STATE_AWAITING_VERDICT = "AWAITING_VERDICT"
MAX_STOP_ATTEMPTS = 4
STATE_SCHEMA_VERSION = 1
SAFE_KEY_MAX_LENGTH = 120
GATE_SUBPROCESS_TIMEOUT_SECONDS = 20
STOP_SUBPROCESS_BUDGET_SECONDS = 25.0
_STOP_GATE_DEADLINE: ContextVar[float | None] = ContextVar(
    "official_writing_stop_gate_deadline", default=None
)
MIN_FENCED_JSON_LINES = 3
MODULE_PATH = Path(__file__).resolve()
PROTECTIVE_CAPABILITY_NAME = "protective_expansion"
REPETITION_CAPABILITY_NAME = "repetition_cleanup"
UNDER_LENGTH_CAPABILITY_NAME = "under_length"
OVER_LENGTH_CAPABILITY_NAME = "over_length"
OVER_LENGTH_RUNTIME_FAILURE_PHASE = "over_length_runtime_failure_fallback"
OVER_LENGTH_RUNTIME_FAILURE_REPROMPTS = 1
OVER_LENGTH_TERMINAL_PHASES = {
    "over_length_complete",
    "over_length_technical_failure",
}
DELIVERY_CLEANLINESS_CAPABILITY_NAME = "delivery_cleanliness"
DELIVERY_REVIEW_CAPABILITY_NAME = "delivery_review"
PROTECTIVE_CAPABILITY_ENV = "COW_GATE_CAPABILITY"
REDACTED_RECORD_STATE = "raw_turn_data_redacted"
HOST_ABORT_REASONS = {
    "adapter_failure",
    "continuation_failed",
    "host_ceiling",
    "pending_replay",
    "skill_not_loaded",
    "turn_changed",
}
_BOOTSTRAP_BUSY = object()
RAW_RECORD_KEYS = frozenset(
    {
        "candidate",
        "bootstrap_pending",
        "deletions",
        "delivery_cleanliness_selected_output",
        "draft_path",
        "emitted_output",
        "increments",
        "original",
        "over_length_selected_output",
        "protective_original_path",
        "protective_selected_path",
        "protective_txn",
        "repetition_packet",
        "request",
        "request_path",
        "selected_path",
        "source_text",
        "txn",
        "under_length_selected_output",
        "working",
    }
)
CAPABILITY_TERMINAL_PHASES = {
    "under_length": {"under_length_complete", "under_length_technical_failure"},
    "over_length": {"over_length_complete", "over_length_technical_failure"},
    "delivery_cleanliness": {
        "delivery_cleanliness_complete",
        "delivery_cleanliness_technical_failure",
    },
}


def _resolve_skill_root() -> Path:
    """Resolve both the canonical source layout and generated companion layout."""
    for candidate in (MODULE_PATH.parents[2], MODULE_PATH.parents[1]):
        if (candidate / "SKILL.md").is_file() and (
            candidate / "scripts" / "review_gate.py"
        ).is_file():
            return candidate
    return MODULE_PATH.parents[2]


SKILL_ROOT = _resolve_skill_root()
REVIEW_GATE_PATH = SKILL_ROOT / "scripts" / "review_gate.py"
PROTECTIVE_RUNTIME_PATH = (
    SKILL_ROOT / "hooks" / "capabilities" / "protective_expansion" / "runtime.py"
)
UNDER_LENGTH_RUNTIME_PATH = (
    SKILL_ROOT / "hooks" / "capabilities" / "under_length" / "runtime.py"
)
OVER_LENGTH_RUNTIME_PATH = (
    SKILL_ROOT / "hooks" / "capabilities" / "over_length" / "runtime.py"
)
DELIVERY_CLEANLINESS_RUNTIME_PATH = (
    SKILL_ROOT / "hooks" / "capabilities" / "delivery_cleanliness" / "runtime.py"
)
SOURCE_BOUND_DATES_PATH = SKILL_ROOT / "hooks" / "shared" / "source_bound_dates.py"
GATE_COMMAND_RE = re.compile(
    r"review_gate\.py(?:\"|'|\s)+(detect|dispatch|prepare|finalize|emit|abort)\b",
    re.IGNORECASE,
)
TXN_RE = re.compile(
    r"--txn(?:=|\s+)(?:\"([^\"]+)\"|'([^']+)'|([^\s;&|]+))",
    re.IGNORECASE,
)
REVIEW_ACTION_RE = re.compile(r"(?:审稿|审核|审查|检查|复核|核验)")
EXPLICIT_REVIEW_ONLY_RE = re.compile(
    r"(?:只|仅)(?:做)?(?:审稿|审核|审查|检查|复核|核验)(?:不改|不修改(?:全文|正文)?|不代改|不重写(?:全文|正文)?)?"
)
SHORT_REVIEW_ONLY_RE = re.compile(
    r"(?:只|仅)\s*审\s*不\s*(?:改|修改(?:全文|正文)?)"
)
REVIEW_ONLY_NEGATION_RE = re.compile(
    r"(?:不是|并非|不属于)\s*(?:只|仅)?\s*"
    r"(?:审稿模式|审稿|审核|审查|检查|复核|核验|审\s*不\s*(?:改|修改))"
)
QUOTED_REQUEST_TEXT_RE = re.compile(
    r"“[^”\n]*”|‘[^’\n]*’|\"[^\"\n]*\"|'[^'\n]*'"
)
NATURAL_REVIEW_ONLY_RE = re.compile(
    r"(?:"
    r"(?:请|帮我|麻烦)\s*(?:只读)?\s*(?:审核|审稿|审查|检查|复核|核验)(?:一下|下)?"
    r"(?:这份|一下这份|下这份)?(?:稿子?|文稿|材料|正文|报告|通知|请示|申请|方案|制度|纪要|函)?"
    r"|(?:只读\s*)?(?:审核|审稿|审查|检查|复核|核验)(?:一下|下|这份(?:稿子?|文稿|材料|正文|报告|通知|请示|申请|方案|制度|纪要|函))"
    r"|审(?:一下|下)稿"
    r"|(?:看一下|看下|看看)[^。；;\n]{0,30}(?:哪里|有无|是否|有没有)"
    r"[^。；;\n]{0,20}(?:问题|错误|不妥|毛病|需要修改)"
    r"|审稿模式"
    r")"
)
REVIEW_OUTPUT_BOUNDARY_RE = re.compile(
    r"(?:不|不要|无需|无须|别)(?:再)?(?:替我|帮我)?"
    r"(?:代改|改写|重写|修改|改)(?:全文|正文|稿件)?"
)
NON_DRAFT_ARTIFACT_CHANGE_RE = re.compile(
    r"(?:不|不要|无需|无须|别)(?:再)?(?:修改|改动|更改|改)\s*"
    r"(?:任何|本地|现有|工作区(?:内|中)?(?:的)?|"
    r"项目(?:内|中)?(?:的)?|仓库(?:内|中)?(?:的)?)?\s*"
    r"(?:文件|源代码|代码|配置|仓库)"
)
NEGATED_WRITING_ACTION_RE = re.compile(
    r"(?:不需要|无需|无须|不用|不要|不必|没必要|别)(?:再)?\s*"
    r"(?:起草|撰写|编写|拟写|改稿|改好|代改|改写|重写|修改|润色|修订|压缩|合稿)"
)
DIRECT_DRAFT_OR_REVISION_RE = re.compile(
    r"(?:^|[，。；;\n]|请|帮我|为我|代为|需要|要求)(?:先|再|直接)?"
    r"(?:起草|撰写|编写|拟写|改稿|改好|改写|重写|"
    r"修改(?!建议|意见|方案|思路|方向|要点|的(?:地方|位置|内容|问题)|之处)|"
    r"修订(?!建议|意见|方案|思路|方向|要点)|润色|压缩|合稿|改(?:一下|下|成|为))"
)
REVIEW_THEN_REWRITE_RE = re.compile(
    r"(?:审|审稿|审核|审查|检查|复核|核验)[^。；;\n]{0,24}"
    r"(?:再|并|同时|然后|之后|后|完)[^，。；;\n]{0,8}"
    r"(?:起草|撰写|编写|拟写|改好|改稿|代改|改写|重写|修改|修订|润色|压缩|合稿|优化)"
)
DRAFT_DELIVERABLE_RE = re.compile(
    r"(?:写|起草|撰写|编写|拟写|生成|输出|给出)(?:一(?:份|篇|版)|份|篇)?"
    r"(?:正式)?(?:通知|报告|请示|申请|方案|制度|纪要|函|正文|全文|稿件|文稿|成稿|定稿)"
    r"|(?:整理|精简|优化|调整|修改|修订|改)(?:成|为|后(?:的)?)"
    r"(?:一(?:份|版))?(?:正式稿|成稿|定稿|正文|全文|稿件|版本)"
)
REWRITE_ACTION_RE = re.compile(
    r"(?:改好|改稿|代改|改写|重写|润色|压缩|合稿|改(?:一下|下|成|为)"
    r"|修改(?!建议|意见|方案|思路|方向|要点|的(?:地方|位置|内容|问题)|之处)"
    r"|修订(?!建议|意见|方案|思路|方向|要点)"
    r"|优化(?!建议|意见|方案|思路|方向|要点))"
)
HOOK_OPT_OUT_RE = re.compile(
    r"(?:"
    r"(?:本次|这次|当前(?:任务|对话|写作)?)?\s*"
    r"(?:关闭|禁用|停用|不启用|不使用|不要用|无需使用|跳过)\s*"
    r"(?:交付门禁|hooks?)"
    r"|"
    r"(?:交付门禁|hooks?)\s*"
    r"(?:关闭|禁用|停用|不启用|不使用|不要用|不用|跳过)"
    r")",
    re.IGNORECASE,
)
HOOK_KEEP_ENABLED_RE = re.compile(
    r"(?:"
    r"(?:不要|别|无需)\s*(?:关闭|禁用|停用)\s*(?:交付门禁|hooks?)"
    r"|"
    r"(?:继续|保持)\s*(?:启用|使用)?\s*(?:交付门禁|hooks?)"
    r"|"
    r"(?:交付门禁|hooks?)\s*(?:继续|保持)\s*(?:启用|使用)"
    r")",
    re.IGNORECASE,
)


def _safe_key(value: Any, fallback: str) -> str:
    text = str(value or fallback)
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("._")
    return cleaned[:SAFE_KEY_MAX_LENGTH] or fallback


def _data_root() -> Path | None:
    raw = os.environ.get("COW_GATE_HOOK_DATA") or os.environ.get("PLUGIN_DATA")
    if not raw:
        return None
    return Path(raw).expanduser().resolve() / "candidate-ai-gate-hook"


def _record_path(event: dict[str, Any]) -> Path | None:
    root = _data_root()
    if root is None:
        return None
    session = _safe_key(event.get("session_id"), "session")
    turn = _safe_key(event.get("turn_id"), "turn")
    return root / session / f"{turn}.json"


def _skill_seen_marker_path(record_path: Path) -> Path:
    """Keep the monotonic Skill-read fact outside concurrent record rewrites."""
    return record_path.with_suffix(".skill-seen")


def _bootstrap_lock_path(record_path: Path) -> Path:
    return record_path.with_suffix(".bootstrap-lock")


def _acquire_bootstrap_lock(record_path: Path) -> tuple[Path, Any] | None:
    lock_path = _bootstrap_lock_path(record_path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        handle = lock_path.open("a+b")
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
    except OSError:
        try:
            handle.close()
        except (NameError, OSError):
            pass
        raise
    try:
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        try:
            handle.close()
        except OSError:
            pass
        return None
    except OSError as exc:
        try:
            handle.close()
        except OSError:
            pass
        if exc.errno in {errno.EACCES, errno.EAGAIN}:
            return None
        raise
    return lock_path, handle


def _release_bootstrap_lock(lock_path: Path, handle: Any) -> None:
    del lock_path
    if handle.closed:
        return
    try:
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    except OSError:
        pass
    finally:
        handle.close()


def _cleanup_bootstrap_lock_file(record_path: Path) -> None:
    # POSIX flock binds to an inode. Unlinking after unlock can let a contender
    # hold the old inode while a third process creates and locks a new one.
    # Keep the one-byte, non-sensitive sentinel there; Windows denies the
    # conflicting unlink and is safe to clean after a successful probe.
    if os.name != "nt":
        return
    try:
        lock = _acquire_bootstrap_lock(record_path)
    except OSError:
        return
    if lock is None:
        return
    lock_path, handle = lock
    _release_bootstrap_lock(lock_path, handle)
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass
    except OSError:
        pass


def _mark_skill_seen(record_path: Path) -> None:
    marker = _skill_seen_marker_path(record_path)
    marker.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("1\n")
        handle.flush()
        os.fsync(handle.fileno())


def _skill_was_seen(record_path: Path, record: dict[str, Any]) -> bool:
    return record.get("skill_seen") is True or _skill_seen_marker_path(record_path).is_file()


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _atomic_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


def _atomic_write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


def _contained_data_path(raw_path: Any, data_root: Path) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path:
        return None
    try:
        path = Path(raw_path).expanduser().resolve()
        root = data_root.resolve()
    except OSError:
        return None
    if path == root or not path.is_relative_to(root):
        return None
    return path


def _record_is_terminal(record: dict[str, Any]) -> bool:
    if record.get("data_retention_state") == REDACTED_RECORD_STATE:
        return True
    if record.get("hook_phase") in {"complete", "failed_bounded"}:
        return True
    if record.get("protective_phase") in {"complete", "failed_closed"}:
        return True
    for key, phases in CAPABILITY_TERMINAL_PHASES.items():
        state = record.get(key)
        if isinstance(state, dict) and state.get("phase") in phases:
            return True
    return False


def _redact_raw_values(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _redact_raw_values(item)
            for key, item in value.items()
            if key not in RAW_RECORD_KEYS
        }
    if isinstance(value, list):
        return [_redact_raw_values(item) for item in value]
    return value


def _remove_turn_artifact(path: Path, data_root: Path) -> bool:
    try:
        resolved = path.resolve()
        root = data_root.resolve()
    except OSError:
        return False
    if resolved == root or not resolved.is_relative_to(root):
        return False
    try:
        if resolved.is_dir():
            shutil.rmtree(resolved)
        else:
            resolved.unlink(missing_ok=True)
    except OSError:
        return False
    return True


def _redact_turn_data(record_path: Path, record: dict[str, Any]) -> None:
    data_root = _data_root()
    if data_root is None:
        return
    targets: list[Path] = []
    ordinary_txn = _contained_data_path(record.get("txn"), data_root)
    if ordinary_txn is not None:
        targets.extend(
            [ordinary_txn, ordinary_txn.parent / f"{ordinary_txn.name}-inputs"]
        )
    protective_txn = _contained_data_path(record.get("protective_txn"), data_root)
    if protective_txn is not None:
        targets.append(protective_txn)
    fallback = (
        data_root
        / "protective-expansion-fallbacks"
        / record_path.parent.name
        / f"{record_path.stem}.txt"
    )
    targets.append(fallback)
    failures = 0
    for target in dict.fromkeys(targets):
        if target.exists() and not _remove_turn_artifact(target, data_root):
            failures += 1
    try:
        _skill_seen_marker_path(record_path).unlink(missing_ok=True)
    except OSError:
        failures += 1
    redacted = _redact_raw_values(record)
    assert isinstance(redacted, dict)
    redacted["data_retention_state"] = REDACTED_RECORD_STATE
    redacted["raw_artifact_delete_failures"] = failures
    try:
        _atomic_write(record_path, redacted)
    except OSError:
        # Prefer losing the nonessential receipt to retaining the raw turn when
        # the filesystem cannot replace the record after terminal cleanup.
        try:
            record_path.unlink(missing_ok=True)
        except OSError:
            pass
        return
    record.clear()
    record.update(redacted)
    _cleanup_bootstrap_lock_file(record_path)


def _finish_stop_response(
    record_path: Path, record: dict[str, Any], response: dict[str, Any]
) -> dict[str, Any]:
    if response.get("continue") is True and _record_is_terminal(record):
        _redact_turn_data(record_path, record)
    return response


def _command_text(event: dict[str, Any]) -> str:
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return ""
    for key in ("cmd", "command"):
        value = tool_input.get(key)
        if isinstance(value, str):
            return value
    return ""


def _successful_tool_result(event: dict[str, Any]) -> bool:
    for key in ("tool_response", "tool_result", "tool_output"):
        value = event.get(key)
        if not isinstance(value, dict):
            continue
        exit_code = value.get("exit_code")
        if isinstance(exit_code, int):
            return exit_code == 0
        if value.get("is_error") is True or value.get("isError") is True:
            return False
    return True


def _extract_gate_call(command: str, cwd: Path) -> tuple[str, Path] | None:
    action_match = GATE_COMMAND_RE.search(command)
    txn_match = TXN_RE.search(command)
    if action_match is None or txn_match is None:
        return None
    raw_txn = next((part for part in txn_match.groups() if part), "")
    if not raw_txn:
        return None
    txn = Path(raw_txn).expanduser()
    if not txn.is_absolute():
        txn = cwd / txn
    return action_match.group(1).lower(), txn.resolve()


def _reads_this_skill(command: str) -> bool:
    if not command:
        return False
    normalized_command = command.replace("/", "\\").casefold()
    skill_roots = [SKILL_ROOT]
    plugin_root = os.environ.get("PLUGIN_ROOT")
    if plugin_root:
        skill_roots.append(Path(plugin_root) / "skills" / "chinese-official-writing")
    return any(
        str(skill_root).replace("/", "\\").casefold() in normalized_command
        for skill_root in skill_roots
    )


def _is_review_only_request(request: str) -> bool:
    """Mirror the Skill's explicit review-only mode without classifying other tasks."""
    request_without_quotes = QUOTED_REQUEST_TEXT_RE.sub("", request)
    request_for_intent = NON_DRAFT_ARTIFACT_CHANGE_RE.sub("", request_without_quotes)
    if REVIEW_ONLY_NEGATION_RE.search(request_for_intent):
        return False
    if REVIEW_THEN_REWRITE_RE.search(request_for_intent):
        return False
    review_trigger = (
        SHORT_REVIEW_ONLY_RE.search(request_for_intent)
        or EXPLICIT_REVIEW_ONLY_RE.search(request_for_intent)
        or NATURAL_REVIEW_ONLY_RE.search(request_for_intent)
        or (
            REVIEW_ACTION_RE.search(request_for_intent)
            and REVIEW_OUTPUT_BOUNDARY_RE.search(request_for_intent)
        )
    )
    if review_trigger is None:
        return False
    review_remainder = SHORT_REVIEW_ONLY_RE.sub("", request_for_intent)
    review_remainder = EXPLICIT_REVIEW_ONLY_RE.sub("", review_remainder)
    review_remainder = NATURAL_REVIEW_ONLY_RE.sub("", review_remainder)
    review_remainder = REVIEW_OUTPUT_BOUNDARY_RE.sub("", review_remainder)
    review_remainder = NEGATED_WRITING_ACTION_RE.sub("", review_remainder)
    return not bool(
        DIRECT_DRAFT_OR_REVISION_RE.search(review_remainder)
        or DRAFT_DELIVERABLE_RE.search(review_remainder)
        or REWRITE_ACTION_RE.search(review_remainder)
    )


def _requests_hook_opt_out(request: str) -> bool:
    """Recognize an explicit task-level Hook bypass without matching generic cautions."""
    if HOOK_KEEP_ENABLED_RE.search(request):
        return False
    return bool(HOOK_OPT_OUT_RE.search(request))


def _allow() -> dict[str, Any]:
    return {"continue": True}


def _continue_once(message: str) -> dict[str, Any]:
    return {
        "decision": "block",
        "reason": message,
    }


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _load_protective_runtime():
    try:
        spec = importlib.util.spec_from_file_location(
            "cow_protective_expansion_runtime", PROTECTIVE_RUNTIME_PATH
        )
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception:
        return None
    return module


def _load_under_length_runtime():
    try:
        spec = importlib.util.spec_from_file_location(
            "cow_under_length_runtime", UNDER_LENGTH_RUNTIME_PATH
        )
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception:
        return None
    return module


def _load_over_length_runtime():
    try:
        spec = importlib.util.spec_from_file_location(
            "cow_over_length_runtime", OVER_LENGTH_RUNTIME_PATH
        )
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception:
        return None
    return module


def _load_delivery_cleanliness_runtime():
    try:
        spec = importlib.util.spec_from_file_location(
            "cow_delivery_cleanliness_runtime", DELIVERY_CLEANLINESS_RUNTIME_PATH
        )
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception:
        return None
    return module


def _load_source_bound_dates():
    try:
        spec = importlib.util.spec_from_file_location(
            "cow_source_bound_dates", SOURCE_BOUND_DATES_PATH
        )
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception:
        return None
    return module


def _source_bound_date_input(request: str, draft: str) -> tuple[str, dict[str, Any] | None]:
    if os.environ.get(PROTECTIVE_CAPABILITY_ENV) != DELIVERY_REVIEW_CAPABILITY_NAME:
        return draft, None
    module = _load_source_bound_dates()
    if module is None:
        return draft, None
    try:
        result = module.restore_unique_full_date(request, draft)
    except Exception:
        return draft, None
    output = result.get("output") if isinstance(result, dict) else None
    if (
        not isinstance(result, dict)
        or result.get("selected") is not True
        or not isinstance(output, str)
        or not output.strip()
    ):
        return draft, None
    audit = {
        "schema_version": result.get("schema_version"),
        "selected": True,
        "reason": result.get("reason"),
        "original_sha256": result.get("original_sha256"),
        "output_sha256": result.get("output_sha256"),
    }
    return output, audit


def _prepare_gate_draft(record: dict[str, Any], request: str, draft: str) -> str:
    output, audit = _source_bound_date_input(request, draft)
    if audit is not None:
        record["source_bound_date"] = audit
    return output


def _load_review_gate_module():
    try:
        spec = importlib.util.spec_from_file_location("cow_review_gate", REVIEW_GATE_PATH)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    except Exception:
        return None
    return module


def _protective_fallback_path(record_path: Path) -> Path | None:
    root = _data_root()
    if root is None:
        return None
    return root / "protective-expansion-fallbacks" / record_path.parent.name / f"{record_path.stem}.txt"


def _protective_runtime_failure(
    event: dict[str, Any], record_path: Path, record: dict[str, Any]
) -> dict[str, Any]:
    original_path = _protective_fallback_path(record_path)
    if original_path is None:
        return _continue_once("纯删除 Hook 不可用，已停止交付；请关闭本任务 Hook 后重试。")
    original = None
    raw_bound = record.get("protective_original_path")
    if isinstance(raw_bound, str):
        try:
            bound = Path(raw_bound).resolve()
            if bound.is_relative_to((_data_root() or Path.cwd()).resolve()):
                original = bound.read_text(encoding="utf-8")
        except (OSError, RuntimeError, UnicodeError):
            original = None
    if original is None:
        candidate = event.get("last_assistant_message")
        original = candidate if isinstance(candidate, str) else ""
        _atomic_write_text(original_path, original)
        record["protective_original_path"] = str(original_path.resolve())
        record["protective_original_sha256"] = _sha256_text(original)
    delivered = event.get("last_assistant_message")
    if record.get("protective_phase") == "runtime_failure_fallback" and isinstance(delivered, str) and _sha256_text(delivered) == record.get("protective_original_sha256"):
        record["protective_phase"] = "complete"
        record["protective_delivery_verified"] = True
        _atomic_write(record_path, record)
        return _allow()
    record["protective_phase"] = "runtime_failure_fallback"
    record["protective_delivery_verified"] = False
    _atomic_write(record_path, record)
    return _continue_once("纯删除模块不可用，已回退原始完整稿。请逐字输出下列正文，不要调用工具、不要加说明：\n" + original)


def _handle_protective_capability(
    event: dict[str, Any], record_path: Path, record: dict[str, Any]
) -> dict[str, Any] | None:
    active_phase = isinstance(record.get("protective_phase"), str)
    selected = os.environ.get(PROTECTIVE_CAPABILITY_ENV) in {
        PROTECTIVE_CAPABILITY_NAME,
        REPETITION_CAPABILITY_NAME,
    }
    if not active_phase and not selected:
        return None
    if not active_phase:
        request = record.get("request")
        draft = event.get("last_assistant_message")
        eligible = (
            record.get("bypass") != "user_requested"
            and record.get("skill_seen") is True
            and isinstance(request, str)
            and bool(request.strip())
            and not _is_review_only_request(request)
            and not record.get("txn")
            and isinstance(draft, str)
            and bool(draft.strip())
            and event.get("stop_hook_active") is not True
        )
        if not eligible:
            return None
    runtime = _load_protective_runtime()
    data_root = _data_root()
    if runtime is None or data_root is None:
        return _protective_runtime_failure(event, record_path, record)
    try:
        if active_phase:
            return runtime.continue_transaction(event, record_path, record, data_root)
        return runtime.start(event, record_path, record, data_root)
    except (OSError, RuntimeError, ValueError):
        return _protective_runtime_failure(event, record_path, record)


def _handle_under_length_capability(
    event: dict[str, Any], record_path: Path, record: dict[str, Any]
) -> dict[str, Any] | None:
    active = isinstance(record.get("under_length"), dict)
    selected = os.environ.get(PROTECTIVE_CAPABILITY_ENV) == UNDER_LENGTH_CAPABILITY_NAME
    if not active and not selected:
        return None
    runtime = _load_under_length_runtime()
    if runtime is None:
        if not active:
            return None
        original = record.get("under_length", {}).get("original")
        if not isinstance(original, str) or not original:
            return _allow()
        record["under_length"]["phase"] = "under_length_technical_failure"
        record["under_length"]["audit"] = {
            "schema_version": 1,
            "trigger": "under",
            "selection": "D0",
            "reason": "under_length_module_unavailable",
            "original_sha256": _sha256_text(original),
            "delivery_verified": False,
        }
        _atomic_write(record_path, record)
        return _continue_once(
            "篇幅复核模块不可用，已回退原始稿。请逐字输出下列 D0，不要调用工具、不要加说明：\n"
            + original
        )
    if active:
        response = runtime.advance(event, record)
        _atomic_write(record_path, record)
        return response
    eligible = (
        record.get("bypass") != "user_requested"
        and record.get("skill_seen") is True
        and not _is_review_only_request(str(record.get("request") or ""))
        and not record.get("txn")
        and isinstance(event.get("last_assistant_message"), str)
        and bool(str(event.get("last_assistant_message")).strip())
        and event.get("stop_hook_active") is not True
    )
    if not eligible:
        return None
    review_gate = _load_review_gate_module()
    if review_gate is None:
        return None
    before = dict(record)
    response = runtime.start(event, record, review_gate)
    if response is not None or record != before:
        _atomic_write(record_path, record)
    return response


def _handle_over_length_capability(
    event: dict[str, Any], record_path: Path, record: dict[str, Any]
) -> dict[str, Any] | None:
    active = isinstance(record.get("over_length"), dict)
    selected = os.environ.get(PROTECTIVE_CAPABILITY_ENV) == OVER_LENGTH_CAPABILITY_NAME
    if not active and not selected:
        return None
    runtime = _load_over_length_runtime()
    if runtime is None:
        if not active:
            return None
        return _over_length_runtime_failure(event, record_path, record)
    if active:
        response = runtime.advance(event, record)
        _atomic_write(record_path, record)
        return response
    eligible = (
        record.get("bypass") != "user_requested"
        and record.get("skill_seen") is True
        and not _is_review_only_request(str(record.get("request") or ""))
        and not record.get("txn")
        and isinstance(event.get("last_assistant_message"), str)
        and bool(str(event.get("last_assistant_message")).strip())
        and event.get("stop_hook_active") is not True
    )
    if not eligible:
        return None
    response = runtime.start(event, record)
    if response is not None:
        _atomic_write(record_path, record)
    return response


def _over_length_runtime_failure(
    event: dict[str, Any], record_path: Path, record: dict[str, Any]
) -> dict[str, Any]:
    state = record.get("over_length")
    if not isinstance(state, dict):
        return _allow()
    if state.get("phase") in OVER_LENGTH_TERMINAL_PHASES:
        return _allow()
    original = state.get("original")
    if not isinstance(original, str) or not original:
        return _allow()
    original_sha256 = _sha256_text(original)
    if state.get("phase") == OVER_LENGTH_RUNTIME_FAILURE_PHASE:
        delivered = event.get("last_assistant_message")
        if isinstance(delivered, str) and _sha256_text(delivered) == original_sha256:
            state["phase"] = "over_length_complete"
            state["audit"]["delivery_verified"] = True
            _atomic_write(record_path, record)
            return _allow()
        attempts = int(state.get("runtime_failure_reprompts") or 0)
        if attempts >= OVER_LENGTH_RUNTIME_FAILURE_REPROMPTS:
            state["phase"] = "over_length_technical_failure"
            state["audit"].update(
                {
                    "reason": "over_length_d0_echo_mismatch_technical_failure",
                    "delivery_verified": False,
                }
            )
            _atomic_write(record_path, record)
            return _allow()
        state["runtime_failure_reprompts"] = attempts + 1
    else:
        state["phase"] = OVER_LENGTH_RUNTIME_FAILURE_PHASE
        state["runtime_failure_reprompts"] = 0
        state["audit"] = {
            "schema_version": 1,
            "trigger": "over",
            "selection": "D0",
            "reason": "over_length_module_unavailable",
            "original_sha256": original_sha256,
            "delivery_sha256": original_sha256,
            "delivery_verified": False,
        }
    _atomic_write(record_path, record)
    return _continue_once(
        "篇幅收束模块不可用，已回退原始稿。请逐字输出下列 D0，不要调用工具、不要加说明：\n"
        + original
    )


def _handle_delivery_cleanliness_capability(
    event: dict[str, Any], record_path: Path, record: dict[str, Any]
) -> dict[str, Any] | None:
    active = isinstance(record.get("delivery_cleanliness"), dict)
    selected = (
        os.environ.get(PROTECTIVE_CAPABILITY_ENV)
        == DELIVERY_CLEANLINESS_CAPABILITY_NAME
    )
    if not active and not selected:
        return None
    runtime = _load_delivery_cleanliness_runtime()
    if runtime is None:
        if not active:
            return None
        original = record.get("delivery_cleanliness", {}).get("original")
        if not isinstance(original, str) or not original:
            return _allow()
        record["delivery_cleanliness"]["phase"] = (
            "delivery_cleanliness_technical_failure"
        )
        record["delivery_cleanliness"]["audit"] = {
            "schema_version": 1,
            "capability": DELIVERY_CLEANLINESS_CAPABILITY_NAME,
            "selection": "D0",
            "reason": "delivery_cleanliness_module_unavailable",
            "original_sha256": _sha256_text(original),
            "delivery_verified": False,
        }
        _atomic_write(record_path, record)
        return _continue_once(
            "交付洁净度模块不可用，已回退原始稿。请逐字输出下列 D0，不要调用工具、不要加说明：\n"
            + original
        )
    if active:
        response = runtime.advance(event, record)
        _atomic_write(record_path, record)
        return response
    eligible = (
        record.get("bypass") != "user_requested"
        and record.get("skill_seen") is True
        and not _is_review_only_request(str(record.get("request") or ""))
        and not record.get("txn")
        and isinstance(event.get("last_assistant_message"), str)
        and bool(str(event.get("last_assistant_message")).strip())
        and event.get("stop_hook_active") is not True
    )
    if not eligible:
        return None
    response = runtime.start(event, record)
    if response is not None:
        _atomic_write(record_path, record)
    return response


def _extract_json_object(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        if len(lines) >= MIN_FENCED_JSON_LINES:
            text = "\n".join(lines[1:-1]).strip()
    start = text.find("{")
    if start < 0:
        return None
    try:
        payload, end = json.JSONDecoder().raw_decode(text[start:])
    except json.JSONDecodeError:
        return None
    if text[start + end :].strip() or not isinstance(payload, dict):
        return None
    return payload


def _remaining_gate_subprocess_timeout() -> float | None:
    deadline = _STOP_GATE_DEADLINE.get()
    if deadline is None:
        return float(GATE_SUBPROCESS_TIMEOUT_SECONDS)
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        return None
    return min(float(GATE_SUBPROCESS_TIMEOUT_SECONDS), remaining)


def _run_review_gate_subprocess(command: list[str]) -> subprocess.CompletedProcess[str] | None:
    timeout = _remaining_gate_subprocess_timeout()
    if timeout is None:
        return None
    try:
        return subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None


def _run_gate(txn: Path, action: str, payload: dict[str, Any] | None = None) -> tuple[int, str]:
    command = [sys.executable, str(REVIEW_GATE_PATH), action, "--txn", str(txn)]
    payload_path: Path | None = None
    if payload is not None:
        suffix = "repairs" if action == "prepare" else "verdict"
        payload_path = txn.parent / f".{txn.name}-{suffix}.json"
        _atomic_write(payload_path, payload)
        command.extend([f"--{suffix}", str(payload_path)])
    try:
        completed = _run_review_gate_subprocess(command)
    finally:
        if payload_path is not None:
            try:
                payload_path.unlink()
            except FileNotFoundError:
                pass
    if completed is None:
        return 1, ""
    return completed.returncode, completed.stdout


def _abort(txn: Path, reason: str) -> dict[str, Any] | None:
    completed = _run_review_gate_subprocess(
        [sys.executable, str(REVIEW_GATE_PATH), "abort", "--txn", str(txn), "--reason", reason]
    )
    if completed is None:
        return None
    if completed.returncode != 0:
        return None
    return _read_json(txn / "state.json")


def _repair_instruction(txn: Path) -> str | None:
    packet = _read_json(txn / "repair.packet.json")
    if packet is None:
        return None
    response = {
        "schema_version": packet.get("response_schema_version"),
        "run_id": packet.get("run_id"),
        "request_sha256": packet.get("request_sha256"),
        "source_sha256": packet.get("source_sha256"),
        "draft_sha256": packet.get("draft_sha256"),
        "revision_count": packet.get("response_revision_count"),
        "repair_mode": packet.get("response_repair_mode"),
        "repairs": [
            {
                "finding_id": finding.get("finding_id"),
                "target": finding.get("target"),
                "decision": None,
                "replacement": None,
            }
            for finding in packet.get("findings") or []
        ],
    }
    if packet.get("guided_marker_sha256") is not None:
        response["guided_marker_sha256"] = packet.get("guided_marker_sha256")
    return (
        "交付门禁已定位需要语义判断的句子。请只输出一个 JSON 对象，不要输出正文、代码围栏或说明。"
        "逐项保留 finding_id 与 target，只能按 allowed_decisions 选择 KEEP、DELETE 或 REWRITE；"
        "骨架中的 null 不是默认答案，必须逐项完成语义判断：材料明确载明且承担当前文种功能、原写法自然时才 KEEP；"
        "材料未谈到且不影响当前文种功能的外围解释选 DELETE；材料明确未定且与主旨相关、但写成示弱或自证时选 REWRITE。"
        "KEEP 的 replacement 与 target 相同，DELETE 为空，REWRITE 只改该句且不新增事实、主体、动作或承诺；"
        "REWRITE 无需与原句等长，避免复述上下文已有事实。涉及未决状态时保持材料已有的事实和判断强度；"
        "外围未决尾句保留材料已明确的下一步动作，不把未确定事项改成新的研究承诺。"
        "REWRITE 不得保留原命中表达；确需原样保留时选择 KEEP。"
        "必须覆盖全部 finding。响应骨架如下：\n"
        + json.dumps(response, ensure_ascii=False)
        + "\n检测包如下：\n"
        + json.dumps(packet, ensure_ascii=False)
    )


def _verdict_instruction(txn: Path) -> str | None:
    packet = _read_json(txn / "semantic-verification.packet.json")
    if packet is None:
        return None
    response = {
        "schema_version": STATE_SCHEMA_VERSION,
        "run_id": packet.get("run_id"),
        "request_sha256": packet.get("request_sha256"),
        "source_sha256": packet.get("source_sha256"),
        "draft_sha256": packet.get("draft_sha256"),
        "candidate_sha256": packet.get("candidate_sha256"),
        "verdict": "PASS",
        "checks": {
            "no_new_fact_action_or_actor": True,
            "decision_and_unresolved_state_preserved": True,
            "necessary_content_preserved": True,
            "p0_expression_removed_or_reduced": True,
            "genre_structure_and_usability_preserved": True,
        },
    }
    if packet.get("guided_marker_sha256") is not None:
        response["guided_marker_sha256"] = packet.get("guided_marker_sha256")
        response["guided_marker_scope_safe"] = True
    return (
        "请只读核验本次唯一局部候选，并只输出一个 JSON 对象，不要输出正文、代码围栏、建议或说明。"
        "以 D0 为比较基准，只判断 D1 新增的变化；任何一项不能确认时把 verdict 写为 FAIL，"
        "并把对应 check 写为 false。响应骨架如下：\n"
        + json.dumps(response, ensure_ascii=False)
        + "\n核验包如下：\n"
        + json.dumps(packet, ensure_ascii=False)
    )


def _emit_and_request_exact_output(
    txn: Path, record_path: Path, record: dict[str, Any]
) -> dict[str, Any]:
    code, output = _run_gate(txn, "emit")
    if code != 0 or not output.strip():
        output = _recover_selected_output_without_subprocess(txn) or ""
    if not output.strip():
        record.update(
            {
                "last_action": "emit_failed",
                "hook_phase": "failed_bounded",
                "delivery_verified": False,
            }
        )
        _atomic_write(record_path, record)
        _redact_turn_data(record_path, record)
        return _continue_once(
            "交付门禁无法恢复可信初稿，已停止自动交付。请只告知用户关闭本任务 Hook 后重新请求原稿，"
            "不要输出当前核验 JSON、状态包或自行重写的正文。"
        )
    record.update(
        {
            "last_action": "emit",
            "emit_seen": True,
            "hook_phase": "awaiting_final_output",
            "emitted_sha256": _sha256_text(output),
            "emitted_output": output,
        }
    )
    _atomic_write(record_path, record)
    return _continue_once(
        "交付门禁已由 Hook 完成 emit。请将下列终稿逐字作为整条最终回复，不要调用工具、不要加说明：\n"
        + output
    )


def _trusted_d0_snapshot(txn: Path) -> str | None:
    state = _read_json(txn / "state.json") or {}
    if state.get("state") != "TERMINAL_D0" or state.get("selected") != "D0":
        return None
    for filename in (
        "selection.claim.json",
        "selection.claim.backup.json",
        "report.json",
    ):
        claim = _read_json(txn / filename)
        if claim is not None and (
            claim.get("state") == "TERMINAL_D1" or claim.get("selected") == "D1"
        ):
            return None
    backup = _read_json(txn / "snapshot.backup.json") or {}
    expected = state.get("d0_sha256")
    if not isinstance(expected, str):
        return None
    backup_hash = backup.get("d0_sha256")
    if isinstance(backup_hash, str) and backup_hash != expected:
        return None
    try:
        text = (txn / "d0.snapshot.txt").read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    if not text.strip() or _sha256_text(text) != expected:
        return None
    return text


def _recover_selected_output_without_subprocess(txn: Path) -> str | None:
    module = _load_review_gate_module()
    if module is not None:
        resolver = getattr(module, "resolve_selected_output", None)
        try:
            output = resolver(txn) if callable(resolver) else None
        except Exception:
            output = None
        if isinstance(output, str) and output.strip():
            return output
    return _trusted_d0_snapshot(txn)


def handle_user_prompt(event: dict[str, Any]) -> dict[str, Any]:
    record_path = _record_path(event)
    prompt = event.get("prompt")
    if record_path is None or not isinstance(prompt, str) or not prompt.strip():
        return _allow()
    existing = _read_json(record_path) or {}
    if not isinstance(existing.get("request"), str):
        existing.update(
            {
                "schema_version": STATE_SCHEMA_VERSION,
                "request": prompt,
                "bypass": "user_requested" if _requests_hook_opt_out(prompt) else None,
                "skill_seen": _skill_was_seen(record_path, existing),
                "emit_seen": bool(existing.get("emit_seen")),
                "stop_attempts": int(existing.get("stop_attempts") or 0),
            }
        )
        _atomic_write(record_path, existing)
    return _allow()


def handle_host_abort(event: dict[str, Any]) -> dict[str, Any]:
    """Fail open while redacting one exact host-bound turn transaction."""
    record_path = _record_path(event)
    if record_path is None:
        return _allow()
    record = _read_json(record_path)
    if record is None or record.get("data_retention_state") == REDACTED_RECORD_STATE:
        return _allow()
    reason = str(event.get("abort_reason") or "")
    record["host_abort_reason"] = (
        reason if reason in HOST_ABORT_REASONS else "adapter_failure"
    )
    record["hook_phase"] = "failed_open_host_abort"
    _redact_turn_data(record_path, record)
    return _allow()


def handle_post_tool(event: dict[str, Any]) -> dict[str, Any]:
    if not _successful_tool_result(event):
        return _allow()
    cwd = Path(str(event.get("cwd") or os.getcwd())).resolve()
    command = _command_text(event)
    parsed = _extract_gate_call(command, cwd)
    record_path = _record_path(event)
    if record_path is None:
        return _allow()
    existing = _read_json(record_path) or {}
    if existing.get("bypass") == "user_requested":
        return _allow()
    if _reads_this_skill(command):
        _mark_skill_seen(record_path)
        existing.update(
            {
                "schema_version": STATE_SCHEMA_VERSION,
                "skill_seen": True,
                "emit_seen": bool(existing.get("emit_seen")),
                "stop_attempts": int(existing.get("stop_attempts") or 0),
            }
        )
        _atomic_write(record_path, existing)
    elif command:
        skill_seen = _skill_was_seen(record_path, existing)
        existing.update(
            {
                "schema_version": STATE_SCHEMA_VERSION,
                "external_material_read": True,
            }
        )
        if skill_seen:
            existing["skill_seen"] = True
        _atomic_write(record_path, existing)
    if parsed is None:
        return _allow()
    action, txn = parsed
    state = _read_json(txn / "state.json")
    if state is None:
        return _allow()
    existing = _read_json(record_path) or existing
    existing.update(
        {
            "schema_version": STATE_SCHEMA_VERSION,
            "txn": str(txn),
            "run_id": state.get("run_id"),
            "last_action": action,
            "emit_seen": bool(existing.get("emit_seen")) or action == "emit",
            "stop_attempts": int(existing.get("stop_attempts") or 0),
        }
    )
    _atomic_write(record_path, existing)
    return _allow()


def _bootstrap_transaction(
    event: dict[str, Any], record_path: Path, record: dict[str, Any]
) -> object | dict[str, Any] | None:
    if record.get("bypass") == "user_requested":
        return None
    if record.get("skill_seen") is not True:
        return None
    request = record.get("request")
    draft = event.get("last_assistant_message")
    if not isinstance(request, str) or not request.strip():
        return None
    if _is_review_only_request(request):
        return None
    if not isinstance(draft, str) or not draft.strip():
        return None
    try:
        lock = _acquire_bootstrap_lock(record_path)
    except OSError:
        return None
    if lock is None:
        return _BOOTSTRAP_BUSY
    lock_path, lock_handle = lock
    try:
        latest = _read_json(record_path)
        if latest is not None:
            record.clear()
            record.update(latest)
        if record.get("txn"):
            return _read_json(Path(str(record["txn"])) / "state.json")
        return _bootstrap_transaction_locked(record_path, record, draft)
    finally:
        _release_bootstrap_lock(lock_path, lock_handle)


def _bootstrap_transaction_locked(
    record_path: Path,
    record: dict[str, Any],
    draft: str,
) -> dict[str, Any] | None:
    request = record.get("request")
    if not isinstance(request, str) or not request.strip():
        return None
    if _is_review_only_request(request):
        return None
    if (
        record.get("bypass") == "user_requested"
        or record.get("skill_seen") is not True
    ):
        return None
    data_root = _data_root()
    if data_root is None:
        return None
    draft_for_gate = _prepare_gate_draft(record, request, draft)
    txn = data_root / "transactions" / record_path.parent.name / record_path.stem
    if txn.exists():
        return None
    inputs = txn.parent / f"{txn.name}-inputs"
    request_path = inputs / "request.txt"
    draft_path = inputs / "draft.txt"
    record.update(
        {
            "schema_version": STATE_SCHEMA_VERSION,
            "txn": str(txn.resolve()),
            "bootstrap_pending": True,
        }
    )
    _atomic_write(record_path, record)
    try:
        _atomic_write_text(request_path, request)
        _atomic_write_text(draft_path, draft_for_gate)
        completed = _run_review_gate_subprocess(
            [
                sys.executable,
                str(REVIEW_GATE_PATH),
                "detect",
                "--request",
                str(request_path),
                "--draft",
                str(draft_path),
                "--txn",
                str(txn),
            ]
        )
    except OSError:
        return None
    if completed is None:
        return None
    if completed.returncode != 0:
        return None
    state = _read_json(txn / "state.json")
    if state is None:
        return None
    latest = _read_json(record_path) or record
    latest.pop("bootstrap_pending", None)
    latest.update(
        {
            "schema_version": STATE_SCHEMA_VERSION,
            "txn": str(txn.resolve()),
            "run_id": state.get("run_id"),
            "last_action": "detect",
            "emit_seen": False,
            "bootstrapped_by_stop": True,
            "stop_attempts": int(record.get("stop_attempts") or 0),
        }
    )
    record.clear()
    record.update(latest)
    _atomic_write(record_path, record)
    return state


def _bound_transaction(record: dict[str, Any]) -> tuple[Path, dict[str, Any]] | None:
    try:
        txn = Path(str(record["txn"])).resolve()
    except (KeyError, OSError, RuntimeError, ValueError):
        return None
    state = _read_json(txn / "state.json")
    if state is None or state.get("run_id") != record.get("run_id"):
        return None
    return txn, state


def _recover_pending_bootstrap(
    record_path: Path, record: dict[str, Any]
) -> object | tuple[Path, dict[str, Any]] | None:
    try:
        lock = _acquire_bootstrap_lock(record_path)
    except OSError:
        _redact_turn_data(record_path, record)
        return None
    if lock is None:
        return _BOOTSTRAP_BUSY
    lock_path, lock_handle = lock
    try:
        latest = _read_json(record_path)
        if latest is not None:
            record.clear()
            record.update(latest)
        bound = _bound_transaction(record)
        if bound is not None:
            return bound
        if record.get("bootstrap_pending") is True:
            _redact_turn_data(record_path, record)
        return None
    finally:
        _release_bootstrap_lock(lock_path, lock_handle)
        if record.get("data_retention_state") == REDACTED_RECORD_STATE:
            _cleanup_bootstrap_lock_file(record_path)


def _handle_selected_output_echo(
    event: dict[str, Any],
    record_path: Path,
    record: dict[str, Any],
    attempts: int,
) -> dict[str, Any] | None:
    if record.get("hook_phase") == "awaiting_final_output":
        delivered = event.get("last_assistant_message")
        if (
            isinstance(delivered, str)
            and _sha256_text(delivered) == record.get("emitted_sha256")
        ):
            record["delivery_verified"] = True
            record["hook_phase"] = "complete"
            record.pop("emitted_output", None)
            _atomic_write(record_path, record)
            return _allow()
        if attempts >= MAX_STOP_ATTEMPTS:
            record["delivery_verified"] = False
            record["hook_phase"] = "failed_bounded"
            record.pop("emitted_output", None)
            _atomic_write(record_path, record)
            return _allow()
        record["stop_attempts"] = attempts + 1
        _atomic_write(record_path, record)
        return _continue_once(
            "终稿回显与 emit 哈希不一致。请只逐字输出下列已选终稿，不要调用工具、不要加说明：\n"
            + str(record.get("emitted_output") or "")
        )
    return None


def _consume_repair_response(
    event: dict[str, Any],
    txn: Path,
    record_path: Path,
    record: dict[str, Any],
    state: dict[str, Any],
    attempts: int,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    if record.get("hook_phase") == "awaiting_repair":
        repair = _extract_json_object(event.get("last_assistant_message"))
        if repair is None:
            state = _abort(txn, "hook_repair_response_invalid") or state
        else:
            code, _ = _run_gate(txn, "prepare", repair)
            state = _read_json(txn / "state.json") or state
            if code != 0 and state.get("state") not in TERMINAL_STATES:
                state = _abort(txn, "hook_prepare_failed") or state
        state_name = state.get("state")
        if state_name == STATE_AWAITING_VERDICT:
            instruction = _verdict_instruction(txn)
            if instruction is not None and attempts < MAX_STOP_ATTEMPTS:
                record["hook_phase"] = "awaiting_verdict"
                record["last_action"] = "prepare"
                record["stop_attempts"] = attempts + 1
                _atomic_write(record_path, record)
                return state, _continue_once(instruction)
            state = _abort(txn, "hook_verdict_packet_missing") or state
    return state, None


def _consume_verdict_response(
    event: dict[str, Any],
    txn: Path,
    record: dict[str, Any],
    state: dict[str, Any],
) -> dict[str, Any]:
    if record.get("hook_phase") == "awaiting_verdict":
        verdict = _extract_json_object(event.get("last_assistant_message"))
        if verdict is None:
            state = _abort(txn, "hook_verdict_response_invalid") or state
        else:
            code, _ = _run_gate(txn, "finalize", verdict)
            state = _read_json(txn / "state.json") or state
            if code != 0 and state.get("state") not in TERMINAL_STATES:
                state = _abort(txn, "hook_finalize_failed") or state
    return state


def _fail_bounded_and_redact(
    record_path: Path, record: dict[str, Any], reason: str
) -> dict[str, Any]:
    record.update(
        {
            "last_action": "bounded_failure",
            "failure_reason": reason,
            "hook_phase": "failed_bounded",
            "delivery_verified": False,
        }
    )
    _redact_turn_data(record_path, record)
    return _allow()


def _dispatch_ordinary_state(
    txn: Path,
    record_path: Path,
    record: dict[str, Any],
    state: dict[str, Any],
    attempts: int,
) -> dict[str, Any]:
    state_name = state.get("state")
    if state_name in TERMINAL_STATES:
        if record.get("emit_seen") is True and record.get("delivery_verified") is True:
            return _allow()
        if (
            record.get("emit_seen") is True
            and record.get("last_action") == "emit"
            and not isinstance(record.get("emitted_sha256"), str)
        ):
            record["hook_phase"] = "failed_bounded"
            record["delivery_verified"] = False
            _atomic_write(record_path, record)
            return _allow()
        if attempts >= MAX_STOP_ATTEMPTS:
            return _fail_bounded_and_redact(
                record_path, record, "hook_terminal_delivery_budget_exhausted"
            )
        record["stop_attempts"] = attempts + 1
        _atomic_write(record_path, record)
        return _emit_and_request_exact_output(txn, record_path, record)

    if state_name == STATE_AWAITING_REPAIR:
        if attempts >= MAX_STOP_ATTEMPTS:
            state = _abort(txn, "hook_stop_budget_exhausted")
            if state is not None and state.get("state") in TERMINAL_STATES:
                return _emit_and_request_exact_output(txn, record_path, record)
            return _fail_bounded_and_redact(
                record_path, record, "hook_stop_budget_exhausted_abort_failed"
            )
        instruction = _repair_instruction(txn)
        if instruction is None:
            state = _abort(txn, "hook_repair_packet_missing")
            if state is not None and state.get("state") in TERMINAL_STATES:
                return _emit_and_request_exact_output(txn, record_path, record)
            return _fail_bounded_and_redact(
                record_path, record, "hook_repair_packet_missing_abort_failed"
            )
        record["hook_phase"] = "awaiting_repair"
        record["stop_attempts"] = attempts + 1
        _atomic_write(record_path, record)
        return _continue_once(instruction)

    if attempts >= MAX_STOP_ATTEMPTS:
        state = _abort(txn, "hook_unknown_state")
        if state is not None and state.get("state") in TERMINAL_STATES:
            return _emit_and_request_exact_output(txn, record_path, record)
        return _fail_bounded_and_redact(
            record_path, record, "hook_unknown_state_abort_failed"
        )
    record["stop_attempts"] = attempts + 1
    _atomic_write(record_path, record)
    return _continue_once("交付门禁正在收口，请只继续当前有限状态，不要重新起草。")


def _handle_stop(event: dict[str, Any]) -> dict[str, Any]:
    record_path = _record_path(event)
    if record_path is None:
        return _allow()
    record = _read_json(record_path)
    if record is None:
        return _allow()
    if record.get("data_retention_state") == REDACTED_RECORD_STATE:
        return _allow()
    if _skill_was_seen(record_path, record) and record.get("skill_seen") is not True:
        record["skill_seen"] = True
        _atomic_write(record_path, record)
    if record.get("bypass") == "user_requested" and not record.get("txn"):
        _redact_turn_data(record_path, record)
        return _allow()
    delivery_cleanliness = _handle_delivery_cleanliness_capability(event, record_path, record)
    if delivery_cleanliness is not None:
        return _finish_stop_response(record_path, record, delivery_cleanliness)
    protective = _handle_protective_capability(event, record_path, record)
    if protective is not None:
        return _finish_stop_response(record_path, record, protective)
    under_length = _handle_under_length_capability(event, record_path, record)
    if under_length is not None:
        return _finish_stop_response(record_path, record, under_length)
    over_length = _handle_over_length_capability(event, record_path, record)
    if over_length is not None:
        return _finish_stop_response(record_path, record, over_length)
    if not record.get("txn"):
        if event.get("stop_hook_active") is True:
            return _allow()
        bootstrap = _bootstrap_transaction(event, record_path, record)
        if bootstrap is _BOOTSTRAP_BUSY:
            return _continue_once("交付门禁正在启动，请只继续当前有限状态，不要重新起草。")
        if bootstrap is None:
            _redact_turn_data(record_path, record)
            return _allow()
    bound = _bound_transaction(record)
    if bound is None and record.get("bootstrap_pending") is True:
        recovered = _recover_pending_bootstrap(record_path, record)
        if recovered is _BOOTSTRAP_BUSY:
            return _continue_once("交付门禁正在启动，请只继续当前有限状态，不要重新起草。")
        if isinstance(recovered, tuple):
            bound = recovered
        else:
            return _allow()
    if bound is None:
        return _allow()
    txn, state = bound
    attempts = int(record.get("stop_attempts") or 0)
    echo = _handle_selected_output_echo(event, record_path, record, attempts)
    if echo is not None:
        return _finish_stop_response(record_path, record, echo)
    state, response = _consume_repair_response(
        event, txn, record_path, record, state, attempts
    )
    if response is not None:
        return response
    state = _consume_verdict_response(event, txn, record, state)
    response = _dispatch_ordinary_state(txn, record_path, record, state, attempts)
    return _finish_stop_response(record_path, record, response)


def handle_stop(event: dict[str, Any]) -> dict[str, Any]:
    token = _STOP_GATE_DEADLINE.set(
        time.monotonic() + STOP_SUBPROCESS_BUDGET_SECONDS
    )
    try:
        return _handle_stop(event)
    finally:
        _STOP_GATE_DEADLINE.reset(token)


def handle(event: dict[str, Any]) -> dict[str, Any]:
    name = str(event.get("hook_event_name") or "")
    if name == "UserPromptSubmit":
        return handle_user_prompt(event)
    if name == "HostAbort":
        return handle_host_abort(event)
    if name == "PostToolUse":
        return handle_post_tool(event)
    if name == "Stop":
        return handle_stop(event)
    return _allow()


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            payload = {}
        result = handle(payload)
    except Exception:
        result = _allow()
    sys.stdout.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
