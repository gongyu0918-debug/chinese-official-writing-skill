#!/usr/bin/env python3
"""Bounded lifecycle bridge for a Candidate AI transaction.

UserPromptSubmit retains the current raw request. PostToolUse records that this
plugin's Skill was actually read and tracks explicit review_gate.py calls. If
the model reaches Stop without starting the gate, Stop snapshots the completed
assistant draft and drives the bounded detect/prepare/finalize/emit chain. The
agent only supplies one repair decision and one read-only verdict when needed;
the Hook runs every script transition and verifies the final output hash.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any


TERMINAL_STATES = {"TERMINAL_D0", "TERMINAL_D1"}
STATE_AWAITING_REPAIR = "AWAITING_REPAIR"
STATE_AWAITING_VERDICT = "AWAITING_VERDICT"
MAX_STOP_ATTEMPTS = 4
GATE_COMMAND_RE = re.compile(
    r"review_gate\.py(?:\"|'|\s)+(detect|dispatch|prepare|finalize|emit|abort)\b",
    re.IGNORECASE,
)
TXN_RE = re.compile(
    r"--txn(?:=|\s+)(?:\"([^\"]+)\"|'([^']+)'|([^\s;&|]+))",
    re.IGNORECASE,
)


def _safe_key(value: Any, fallback: str) -> str:
    text = str(value or fallback)
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("._")
    return cleaned[:120] or fallback


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
    plugin_root = os.environ.get("PLUGIN_ROOT")
    if not plugin_root or not command:
        return False
    normalized_command = command.replace("/", "\\").casefold()
    normalized_skill = str(
        Path(plugin_root) / "skills" / "chinese-official-writing"
    ).replace("/", "\\").casefold()
    return normalized_skill in normalized_command


def _allow() -> dict[str, Any]:
    return {"continue": True}


def _continue_once(message: str) -> dict[str, Any]:
    return {
        "decision": "block",
        "reason": message,
    }


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _extract_json_object(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
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


def _run_gate(txn: Path, action: str, payload: dict[str, Any] | None = None) -> tuple[int, str]:
    gate = Path(__file__).with_name("review_gate.py").resolve()
    command = [sys.executable, str(gate), action, "--txn", str(txn)]
    payload_path: Path | None = None
    if payload is not None:
        suffix = "repairs" if action == "prepare" else "verdict"
        payload_path = txn.parent / f".{txn.name}-{suffix}.json"
        _atomic_write(payload_path, payload)
        command.extend([f"--{suffix}", str(payload_path)])
    try:
        completed = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return 1, ""
    finally:
        if payload_path is not None:
            try:
                payload_path.unlink()
            except FileNotFoundError:
                pass
    return completed.returncode, completed.stdout


def _abort(txn: Path, reason: str) -> dict[str, Any] | None:
    gate = Path(__file__).with_name("review_gate.py").resolve()
    try:
        completed = subprocess.run(
            [sys.executable, str(gate), "abort", "--txn", str(txn), "--reason", reason],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
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
        "REWRITE 无需与原句等长，避免复述上下文已有事实。缺态句只改为不扩展方法的调查、核查等进行态；"
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
        "schema_version": 1,
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
        "材料中的原因尚未形成结论改为同一事项正在调查或核查，且未新增主体、方法或结论时，"
        "视为未决状态保留，不计为新增动作；"
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
        return _allow()
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


def handle_user_prompt(event: dict[str, Any]) -> dict[str, Any]:
    record_path = _record_path(event)
    prompt = event.get("prompt")
    if record_path is None or not isinstance(prompt, str) or not prompt.strip():
        return _allow()
    existing = _read_json(record_path) or {}
    if not isinstance(existing.get("request"), str):
        existing.update(
            {
                "schema_version": 1,
                "request": prompt,
                "skill_seen": bool(existing.get("skill_seen")),
                "emit_seen": bool(existing.get("emit_seen")),
                "stop_attempts": int(existing.get("stop_attempts") or 0),
            }
        )
        _atomic_write(record_path, existing)
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
    if _reads_this_skill(command):
        existing.update(
            {
                "schema_version": 1,
                "skill_seen": True,
                "emit_seen": bool(existing.get("emit_seen")),
                "stop_attempts": int(existing.get("stop_attempts") or 0),
            }
        )
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
            "schema_version": 1,
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
) -> dict[str, Any] | None:
    if record.get("skill_seen") is not True:
        return None
    request = record.get("request")
    draft = event.get("last_assistant_message")
    if not isinstance(request, str) or not request.strip():
        return None
    if not isinstance(draft, str) or not draft.strip():
        return None
    data_root = _data_root()
    if data_root is None:
        return None
    txn = data_root / "transactions" / record_path.parent.name / record_path.stem
    if txn.exists():
        return None
    inputs = txn.parent / f"{txn.name}-inputs"
    request_path = inputs / "request.txt"
    draft_path = inputs / "draft.txt"
    _atomic_write_text(request_path, request)
    _atomic_write_text(draft_path, draft)
    gate = Path(__file__).with_name("review_gate.py").resolve()
    try:
        completed = subprocess.run(
            [
                sys.executable,
                str(gate),
                "detect",
                "--request",
                str(request_path),
                "--draft",
                str(draft_path),
                "--txn",
                str(txn),
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            timeout=20,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    state = _read_json(txn / "state.json")
    if state is None:
        return None
    record.update(
        {
            "schema_version": 1,
            "txn": str(txn.resolve()),
            "run_id": state.get("run_id"),
            "last_action": "detect",
            "emit_seen": False,
            "bootstrapped_by_stop": True,
            "stop_attempts": int(record.get("stop_attempts") or 0),
        }
    )
    _atomic_write(record_path, record)
    return state


def handle_stop(event: dict[str, Any]) -> dict[str, Any]:
    record_path = _record_path(event)
    if record_path is None:
        return _allow()
    record = _read_json(record_path)
    if record is None:
        return _allow()
    if not record.get("txn"):
        if event.get("stop_hook_active") is True:
            return _allow()
        state = _bootstrap_transaction(event, record_path, record)
        if state is None:
            return _allow()
    try:
        txn = Path(str(record["txn"])).resolve()
    except (KeyError, OSError, RuntimeError, ValueError):
        return _allow()
    state = _read_json(txn / "state.json")
    if state is None or state.get("run_id") != record.get("run_id"):
        return _allow()
    state_name = state.get("state")
    attempts = int(record.get("stop_attempts") or 0)

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
                return _continue_once(instruction)
            state = _abort(txn, "hook_verdict_packet_missing") or state
            state_name = state.get("state")

    if record.get("hook_phase") == "awaiting_verdict":
        verdict = _extract_json_object(event.get("last_assistant_message"))
        if verdict is None:
            state = _abort(txn, "hook_verdict_response_invalid") or state
        else:
            code, _ = _run_gate(txn, "finalize", verdict)
            state = _read_json(txn / "state.json") or state
            if code != 0 and state.get("state") not in TERMINAL_STATES:
                state = _abort(txn, "hook_finalize_failed") or state
        state_name = state.get("state")

    if state_name in TERMINAL_STATES:
        if record.get("emit_seen") is True and record.get("delivery_verified") is True:
            return _allow()
        if attempts >= MAX_STOP_ATTEMPTS:
            return _allow()
        record["stop_attempts"] = attempts + 1
        _atomic_write(record_path, record)
        return _emit_and_request_exact_output(txn, record_path, record)

    if state_name == STATE_AWAITING_REPAIR:
        if attempts >= MAX_STOP_ATTEMPTS:
            state = _abort(txn, "hook_stop_budget_exhausted")
            if state is not None and state.get("state") in TERMINAL_STATES:
                return _emit_and_request_exact_output(txn, record_path, record)
            return _allow()
        instruction = _repair_instruction(txn)
        if instruction is None:
            state = _abort(txn, "hook_repair_packet_missing")
            if state is not None and state.get("state") in TERMINAL_STATES:
                return _emit_and_request_exact_output(txn, record_path, record)
            return _allow()
        record["hook_phase"] = "awaiting_repair"
        record["stop_attempts"] = attempts + 1
        _atomic_write(record_path, record)
        return _continue_once(instruction)

    if attempts >= MAX_STOP_ATTEMPTS:
        state = _abort(txn, "hook_unknown_state")
        if state is not None and state.get("state") in TERMINAL_STATES:
            return _emit_and_request_exact_output(txn, record_path, record)
        return _allow()
    record["stop_attempts"] = attempts + 1
    _atomic_write(record_path, record)
    return _continue_once("交付门禁正在收口，请只继续当前有限状态，不要重新起草。")


def handle(event: dict[str, Any]) -> dict[str, Any]:
    name = str(event.get("hook_event_name") or "")
    if name == "UserPromptSubmit":
        return handle_user_prompt(event)
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
