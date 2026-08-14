#!/usr/bin/env python3
"""Bounded Stop lifecycle for the protective-expansion delete-only capability."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from types import ModuleType
from typing import Any, Final


PROTECTIVE_CAPABILITY: Final = "protective_expansion"
REPETITION_CAPABILITY: Final = "repetition_cleanup"
SUPPORTED_CAPABILITIES: Final = {PROTECTIVE_CAPABILITY, REPETITION_CAPABILITY}
CAPABILITY_ENV: Final = "COW_GATE_CAPABILITY"
STATE_SCHEMA_VERSION: Final = 1
MAX_OUTPUT_REPROMPTS: Final = 1
MIN_FENCED_JSON_LINES: Final = 3
FAILURE_NOTICE: Final = "纯删除 Hook 未能验证原始稿回显，本次未交付正文。请关闭本任务 Hook 后重试。"
MODULE_PATH: Final = Path(__file__).resolve()
CONTRACT_PATH: Final = MODULE_PATH.with_name("contract.py")


def _allow() -> dict[str, Any]:
    return {"continue": True}


def _block(message: str) -> dict[str, Any]:
    return {"decision": "block", "reason": message}


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _atomic_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def _atomic_write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def _load_contract() -> ModuleType | None:
    try:
        spec = importlib.util.spec_from_file_location("cow_protective_expansion_contract", CONTRACT_PATH)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    except Exception:
        return None
    return module


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


def _selected_capability(record: dict[str, Any]) -> str:
    bound = record.get("protective_capability")
    if bound in SUPPORTED_CAPABILITIES:
        return str(bound)
    selected = os.environ.get(CAPABILITY_ENV)
    return str(selected) if selected in SUPPORTED_CAPABILITIES else PROTECTIVE_CAPABILITY


def _transaction_path(
    data_root: Path, record_path: Path, draft_hash: str, capability: str
) -> Path:
    return (
        data_root
        / f"{capability.replace('_', '-')}-transactions"
        / record_path.parent.name
        / f"{record_path.stem}-{draft_hash[:12]}"
    )


def _contained_path(value: Any, root: Path) -> Path | None:
    if not isinstance(value, str):
        return None
    try:
        path = Path(value).resolve()
    except (OSError, RuntimeError):
        return None
    return path if path.is_relative_to(root.resolve()) else None


def _save_audit(txn: Path, audit: dict[str, Any]) -> None:
    _atomic_write(txn / "audit.json", audit)


def _bind_record(
    record_path: Path,
    record: dict[str, Any],
    txn: Path,
    phase: str,
    original_hash: str,
    capability: str,
) -> None:
    record.update(
        {
            "protective_capability": capability,
            "protective_txn": str(txn.resolve()),
            "protective_phase": phase,
            "protective_original_sha256": original_hash,
            "protective_original_path": str((txn / "original.txt").resolve()),
            "protective_output_reprompts": 0,
        }
    )
    _atomic_write(record_path, record)


def _resume_existing(
    txn: Path,
    record_path: Path,
    record: dict[str, Any],
    draft_hash: str,
    capability: str,
) -> dict[str, Any] | None:
    audit = _read_json(txn / "audit.json")
    if audit is None or audit.get("original_sha256") != draft_hash:
        return None
    phase = audit.get("phase")
    if phase not in {"awaiting_observation", "awaiting_output", "awaiting_original", "awaiting_failure_notice"}:
        return None
    _bind_record(record_path, record, txn, str(phase), draft_hash, capability)
    return audit


def start(
    event: dict[str, Any], record_path: Path, record: dict[str, Any], data_root: Path
) -> dict[str, Any]:
    request = record.get("request")
    draft = event.get("last_assistant_message")
    if not isinstance(request, str) or not isinstance(draft, str):
        return _allow()
    contract = _load_contract()
    if contract is None:
        raise RuntimeError("protective contract unavailable")
    authority_scope = (
        "external_material_observed"
        if record.get("external_material_read") is True
        else "request_only"
    )
    capability = _selected_capability(record)
    packet = contract.build_packet(
        request,
        draft,
        "",
        authority_scope=authority_scope,
        capability=capability,
    )
    if packet.get("status") != "ready":
        raise RuntimeError("protective packet unavailable")
    draft_hash = contract.sha256_text(draft)
    txn = _transaction_path(data_root, record_path, draft_hash, capability)
    if txn.exists():
        audit = _resume_existing(txn, record_path, record, draft_hash, capability)
        if audit is None:
            raise RuntimeError("protective transaction collision")
        return _block(contract.observer_instruction(packet))
    txn.mkdir(parents=True, exist_ok=False)
    _atomic_write_text(txn / "original.txt", draft)
    _atomic_write(txn / "observation.packet.json", packet)
    audit = {
        "schema_version": STATE_SCHEMA_VERSION,
        "capability": capability,
        "phase": "awaiting_observation",
        "authority_scope": authority_scope,
        "request_sha256": packet["request_sha256"],
        "original_sha256": draft_hash,
        "packet_sha256": packet["packet_sha256"],
        "selection": None,
        "delivery_verified": False,
    }
    _save_audit(txn, audit)
    _bind_record(
        record_path, record, txn, "awaiting_observation", draft_hash, capability
    )
    return _block(contract.observer_instruction(packet))


def _load_bound_transaction(
    record: dict[str, Any], data_root: Path
) -> tuple[Path, dict[str, Any], str] | None:
    capability = _selected_capability(record)
    txn = _contained_path(
        record.get("protective_txn"),
        data_root / f"{capability.replace('_', '-')}-transactions",
    )
    if txn is None:
        return None
    audit = _read_json(txn / "audit.json")
    try:
        original = (txn / "original.txt").read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    if audit is None or audit.get("original_sha256") != record.get("protective_original_sha256"):
        return None
    return txn, audit, original


def _select_output(
    event: dict[str, Any], record_path: Path, record: dict[str, Any], txn: Path, audit: dict[str, Any], original: str
) -> dict[str, Any]:
    contract = _load_contract()
    packet = _read_json(txn / "observation.packet.json")
    response = _extract_json_object(event.get("last_assistant_message"))
    if contract is None or packet is None or response is None:
        result = {"status": "fallback", "selection": "E0", "reason": "observation_unavailable", "output": original, "output_sha256": audit["original_sha256"]}
    else:
        result = contract.apply_response(packet, response)
    output = result.get("output") if isinstance(result.get("output"), str) else original
    selection = "E1" if result.get("selection") == "E1" else "E0"
    output_hash = contract.sha256_text(output) if contract is not None else audit["original_sha256"]
    output_path = txn / ("candidate.txt" if selection == "E1" else "original.txt")
    if selection == "E1":
        _atomic_write_text(output_path, output)
    audit.update(
        {
            "phase": "awaiting_output" if selection == "E1" else "awaiting_original",
            "selection": selection,
            "selection_reason": result.get("reason"),
            "selected_output_sha256": output_hash,
            "observer_response_sha256": contract.sha256_text(json.dumps(response, ensure_ascii=False, sort_keys=True)) if contract is not None and response is not None else None,
        }
    )
    _save_audit(txn, audit)
    record.update(
        {
            "protective_phase": audit["phase"],
            "protective_selection": selection,
            "protective_selected_path": str(output_path.resolve()),
            "protective_selected_sha256": output_hash,
        }
    )
    _atomic_write(record_path, record)
    capability = _selected_capability(record)
    label = (
        "重复句观察已形成精确删减稿。"
        if capability == REPETITION_CAPABILITY and selection == "E1"
        else "重复句观察未形成可安全删除项，保留原始完整稿。"
        if capability == REPETITION_CAPABILITY
        else "保护性外扩观察已形成精确删减稿。"
        if selection == "E1"
        else "保护性外扩观察未形成可安全删除项，保留原始完整稿。"
    )
    return _block(label + "请将下列正文逐字作为整条最终回复，不要调用工具、不要加说明：\n" + output)


def _verify_output(
    event: dict[str, Any], record_path: Path, record: dict[str, Any], txn: Path, audit: dict[str, Any], original: str
) -> dict[str, Any]:
    delivered = event.get("last_assistant_message")
    contract = _load_contract()
    delivered_hash = contract.sha256_text(delivered) if contract is not None and isinstance(delivered, str) else None
    if delivered_hash == record.get("protective_selected_sha256"):
        audit.update({"phase": "complete", "delivery_verified": True, "delivery_sha256": delivered_hash})
        record.update({"protective_phase": "complete", "protective_delivery_verified": True})
        _save_audit(txn, audit)
        _atomic_write(record_path, record)
        return _allow()
    if record.get("protective_selection") == "E1":
        record.update(
            {
                "protective_phase": "awaiting_original",
                "protective_selection": "E0",
                "protective_selected_path": str((txn / "original.txt").resolve()),
                "protective_selected_sha256": audit["original_sha256"],
                "protective_output_reprompts": 1,
            }
        )
        audit.update({"phase": "awaiting_original", "selection": "E0", "selection_reason": "e1_echo_mismatch"})
        _save_audit(txn, audit)
        _atomic_write(record_path, record)
        return _block("删减稿回显不一致，已回退原始完整稿。请逐字输出下列正文，不要调用工具、不要加说明：\n" + original)
    reprompts = int(record.get("protective_output_reprompts") or 0)
    if reprompts < MAX_OUTPUT_REPROMPTS:
        record["protective_output_reprompts"] = reprompts + 1
        _atomic_write(record_path, record)
        return _block("原始稿回显不一致。请只逐字输出下列正文，不要调用工具、不要加说明：\n" + original)
    failure_hash = contract.sha256_text(FAILURE_NOTICE) if contract is not None else None
    audit.update({"phase": "awaiting_failure_notice", "delivery_verified": False, "failure_reason": "e0_echo_mismatch", "failure_notice_sha256": failure_hash})
    record.update({"protective_phase": "awaiting_failure_notice", "protective_delivery_verified": False, "protective_failure_notice_sha256": failure_hash})
    _save_audit(txn, audit)
    _atomic_write(record_path, record)
    return _block("请逐字输出下列技术失败通知，不要调用工具、不要加说明：\n" + FAILURE_NOTICE)


def _verify_failure_notice(
    event: dict[str, Any], record_path: Path, record: dict[str, Any], txn: Path, audit: dict[str, Any]
) -> dict[str, Any]:
    contract = _load_contract()
    delivered = event.get("last_assistant_message")
    delivered_hash = contract.sha256_text(delivered) if contract is not None and isinstance(delivered, str) else None
    if delivered_hash == record.get("protective_failure_notice_sha256"):
        audit.update({"phase": "failed_closed", "failure_notice_delivered": True})
        record.update({"protective_phase": "failed_closed", "protective_failure_notice_delivered": True})
        _save_audit(txn, audit)
        _atomic_write(record_path, record)
        return _allow()
    return _block("技术失败通知回显不一致。请逐字输出下列文字：\n" + FAILURE_NOTICE)


def continue_transaction(
    event: dict[str, Any], record_path: Path, record: dict[str, Any], data_root: Path
) -> dict[str, Any]:
    bound = _load_bound_transaction(record, data_root)
    if bound is None:
        raise RuntimeError("protective transaction unavailable")
    txn, audit, original = bound
    phase = record.get("protective_phase")
    if phase == "awaiting_observation":
        return _select_output(event, record_path, record, txn, audit, original)
    if phase in {"awaiting_output", "awaiting_original"}:
        return _verify_output(event, record_path, record, txn, audit, original)
    if phase == "awaiting_failure_notice":
        return _verify_failure_notice(event, record_path, record, txn, audit)
    if phase == "complete":
        return _allow()
    if phase == "failed_closed":
        return _allow()
    raise RuntimeError("unknown protective phase")
