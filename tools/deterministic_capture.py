#!/usr/bin/env python3
"""Freeze and verify the first externally produced assistant body.

This utility never calls a model and never rewrites an existing capture.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal, DecimalException, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any


SCHEMA_VERSION = 2
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _body_sha256(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _write_exclusive(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary_path, path)
    finally:
        try:
            temporary_path.unlink()
        except FileNotFoundError:
            pass


def capture(input_path: Path, output_path: Path) -> dict[str, Any]:
    source = _read_object(input_path)
    task_id = source.get("task_id")
    body = source.get("assistant_body")
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id must be a non-empty string")
    if not isinstance(body, str) or not body.strip():
        raise ValueError("assistant_body must be a non-empty string")

    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        "assistant_body": body,
        "assistant_body_sha256": _body_sha256(body),
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "capture_ordinal": 1,
    }
    request_sha256 = source.get("request_sha256")
    if request_sha256 is not None:
        if not isinstance(request_sha256, str) or not SHA256_RE.fullmatch(request_sha256):
            raise ValueError("request_sha256 must be a lowercase SHA-256 hex string when present")
        receipt["request_sha256"] = request_sha256

    _write_exclusive(output_path, receipt)
    return receipt


def verify(capture_path: Path) -> dict[str, Any]:
    receipt = _read_object(capture_path)
    body = receipt.get("assistant_body")
    expected = receipt.get("assistant_body_sha256")
    issues: list[str] = []
    if receipt.get("schema_version") != SCHEMA_VERSION:
        issues.append("schema_version_mismatch")
    task_id = receipt.get("task_id")
    if not isinstance(task_id, str) or not task_id.strip():
        issues.append("task_id_invalid")
    if receipt.get("capture_ordinal") != 1:
        issues.append("capture_ordinal_not_one")
    request_sha256 = receipt.get("request_sha256")
    if request_sha256 is not None and (
        not isinstance(request_sha256, str) or not SHA256_RE.fullmatch(request_sha256)
    ):
        issues.append("request_sha256_invalid")
    if not isinstance(body, str) or not body.strip():
        issues.append("assistant_body_not_string")
    elif expected != _body_sha256(body):
        issues.append("assistant_body_sha256_mismatch")
    return {"status": "PASS" if not issues else "FAIL", "issues": issues}


def count_non_whitespace(capture_path: Path) -> dict[str, Any]:
    verification = verify(capture_path)
    if verification["status"] != "PASS":
        return verification
    receipt = _read_object(capture_path)
    body = receipt.get("assistant_body")
    if not isinstance(body, str):
        raise ValueError("assistant_body must be a string")
    return {
        "status": "PASS",
        "task_id": receipt.get("task_id"),
        "assistant_body_sha256": _body_sha256(body),
        "unicode_non_whitespace_count": sum(1 for character in body if not character.isspace()),
    }


def _numeric_values(packet: dict[str, Any]) -> dict[str, tuple[Decimal, str, str]]:
    source_text = packet.get("fact_packet_text")
    raw_values = packet.get("values")
    if not isinstance(source_text, str):
        raise ValueError("fact_packet_text must be a string")
    if not isinstance(raw_values, list) or not raw_values:
        raise ValueError("values must be a non-empty array")

    values: dict[str, tuple[Decimal, str, str]] = {}
    for index, item in enumerate(raw_values):
        if not isinstance(item, dict):
            raise ValueError(f"value {index} must be an object")
        name = item.get("id")
        value = item.get("value")
        kind = item.get("kind")
        unit = item.get("unit")
        quote = item.get("source_quote")
        if not isinstance(name, str) or not name:
            raise ValueError(f"value {index} id must be a non-empty string")
        if name in values:
            raise ValueError(f"duplicate value id {name}")
        if not isinstance(value, str):
            raise ValueError(f"value {name} must be a decimal string")
        if kind not in {"money", "scalar"}:
            raise ValueError(f"value {name} kind must be money or scalar")
        if not isinstance(unit, str) or not unit:
            raise ValueError(f"value {name} unit must be a non-empty string")
        if kind == "money" and unit != "CNY":
            raise ValueError(f"money value {name} unit must be CNY")
        if not isinstance(quote, str) or not quote or quote not in source_text:
            raise ValueError(f"value {name} source_quote must occur in fact_packet_text")
        try:
            decimal_value = Decimal(value)
        except InvalidOperation as exc:
            raise ValueError(f"value {name} has an invalid decimal value") from exc
        if not decimal_value.is_finite():
            raise ValueError(f"value {name} must be finite")
        values[name] = (decimal_value, kind, unit)
    return values


def check_amounts(packet_path: Path) -> dict[str, Any]:
    packet_bytes = packet_path.read_bytes()
    packet = json.loads(packet_bytes.decode("utf-8"))
    if not isinstance(packet, dict):
        raise ValueError(f"{packet_path} must contain a JSON object")
    values = _numeric_values(packet)
    raw_assertions = packet.get("assertions")
    if not isinstance(raw_assertions, list) or not raw_assertions:
        raise ValueError("assertions must be a non-empty array")

    results: list[dict[str, Any]] = []
    comparisons = {
        "eq": lambda left, right: left == right,
        "ne": lambda left, right: left != right,
        "lt": lambda left, right: left < right,
        "le": lambda left, right: left <= right,
        "gt": lambda left, right: left > right,
        "ge": lambda left, right: left >= right,
    }
    assertion_ids: set[str] = set()
    for index, assertion in enumerate(raw_assertions):
        if not isinstance(assertion, dict):
            raise ValueError(f"assertion {index} must be an object")
        assertion_id = assertion.get("id")
        operation = assertion.get("op")
        left_name = assertion.get("left")
        right_name = assertion.get("right")
        if not isinstance(assertion_id, str) or not assertion_id:
            raise ValueError(f"assertion {index} id must be a non-empty string")
        if assertion_id in assertion_ids:
            raise ValueError(f"duplicate assertion id {assertion_id}")
        assertion_ids.add(assertion_id)
        if not isinstance(left_name, str) or not isinstance(right_name, str):
            raise ValueError(f"assertion {assertion_id} operands must name values")
        if left_name not in values or right_name not in values:
            raise ValueError(f"assertion {assertion_id} refers to an unknown value")
        left, left_kind, left_unit = values[left_name]
        right, right_kind, right_unit = values[right_name]
        if operation in {"add", "sub", "mul", "div"}:
            expected_name = assertion.get("expected")
            if not isinstance(expected_name, str) or expected_name not in values:
                raise ValueError(f"assertion {assertion_id} expected must name a value")
            expected, expected_kind, expected_unit = values[expected_name]
            if operation in {"add", "sub"}:
                if (left_kind, left_unit) != (right_kind, right_unit):
                    raise ValueError(f"assertion {assertion_id} requires matching operand units")
                actual = left + right if operation == "add" else left - right
                result_kind, result_unit = left_kind, left_unit
            elif operation == "mul":
                kinds = {left_kind, right_kind}
                if kinds != {"money", "scalar"}:
                    raise ValueError(f"assertion {assertion_id} multiplication requires money and scalar")
                actual = left * right
                result_kind = "money"
                result_unit = left_unit if left_kind == "money" else right_unit
            else:
                if left_kind != "money" or right_kind != "scalar":
                    raise ValueError(f"assertion {assertion_id} division requires money divided by scalar")
                if right == 0:
                    raise ValueError(f"assertion {assertion_id} divides by zero")
                actual = left / right
                result_kind, result_unit = left_kind, left_unit
            if (expected_kind, expected_unit) != (result_kind, result_unit):
                raise ValueError(f"assertion {assertion_id} expected unit does not match result")
            passed = actual == expected
            results.append(
                {
                    "id": assertion_id,
                    "op": operation,
                    "status": "PASS" if passed else "FAIL",
                    "actual": format(actual, "f"),
                    "expected": format(expected, "f"),
                }
            )
        elif operation in comparisons:
            if (left_kind, left_unit) != (right_kind, right_unit):
                raise ValueError(f"assertion {assertion_id} comparison requires matching units")
            passed = comparisons[operation](left, right)
            results.append(
                {
                    "id": assertion_id,
                    "op": operation,
                    "status": "PASS" if passed else "FAIL",
                    "left": format(left, "f"),
                    "right": format(right, "f"),
                }
            )
        else:
            raise ValueError(f"assertion {assertion_id} has unsupported op {operation!r}")

    passed = all(item["status"] == "PASS" for item in results)
    return {
        "status": "PASS" if passed else "FAIL",
        "fact_packet_sha256": hashlib.sha256(packet_bytes).hexdigest(),
        "assertions": results,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Freeze and verify first-visible external model outputs."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    capture_parser = subparsers.add_parser("capture")
    capture_parser.add_argument("--input", type=Path, required=True)
    capture_parser.add_argument("--out", type=Path, required=True)

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--capture", type=Path, required=True)

    count_parser = subparsers.add_parser("count")
    count_parser.add_argument("--capture", type=Path, required=True)

    amount_parser = subparsers.add_parser("amount-check")
    amount_parser.add_argument("--fact-packet", type=Path, required=True)
    amount_parser.add_argument("--out", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "capture":
            result = capture(args.input, args.out)
        elif args.command == "verify":
            result = verify(args.capture)
        elif args.command == "count":
            result = count_non_whitespace(args.capture)
        else:
            result = check_amounts(args.fact_packet)
            _write_exclusive(args.out, result)
    except FileExistsError as exc:
        print(json.dumps({"status": "FAIL", "error": "capture_exists", "path": str(exc.filename)}, ensure_ascii=False))
        return 3
    except (OSError, ValueError, json.JSONDecodeError, DecimalException) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False))
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.command != "capture" and result["status"] != "PASS":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
