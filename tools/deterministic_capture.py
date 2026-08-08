#!/usr/bin/env python3
"""Freeze and verify the first externally produced assistant body.

This utility never calls a model and never rewrites an existing capture.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1


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
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise


def capture(input_path: Path, output_path: Path) -> dict[str, Any]:
    source = _read_object(input_path)
    task_id = source.get("task_id")
    body = source.get("assistant_body")
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task_id must be a non-empty string")
    if not isinstance(body, str):
        raise ValueError("assistant_body must be a string")

    receipt: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        "assistant_body": body,
        "assistant_body_sha256": _body_sha256(body),
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "generation_attempt": 1,
    }
    request_sha256 = source.get("request_sha256")
    if request_sha256 is not None:
        if not isinstance(request_sha256, str) or not request_sha256.strip():
            raise ValueError("request_sha256 must be a non-empty string when present")
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
    if receipt.get("generation_attempt") != 1:
        issues.append("generation_attempt_not_one")
    if not isinstance(body, str):
        issues.append("assistant_body_not_string")
    elif expected != _body_sha256(body):
        issues.append("assistant_body_sha256_mismatch")
    return {"status": "PASS" if not issues else "FAIL", "issues": issues}


def count_non_whitespace(capture_path: Path) -> dict[str, Any]:
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
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "capture":
            result = capture(args.input, args.out)
        elif args.command == "verify":
            result = verify(args.capture)
        else:
            result = count_non_whitespace(args.capture)
    except FileExistsError as exc:
        print(json.dumps({"status": "FAIL", "error": "capture_exists", "path": str(exc.filename)}, ensure_ascii=False))
        return 3
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False))
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.command == "verify" and result["status"] != "PASS":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
