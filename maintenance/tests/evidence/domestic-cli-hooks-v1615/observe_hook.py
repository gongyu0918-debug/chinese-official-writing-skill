#!/usr/bin/env python3
"""Record a redacted shape of a real host Hook event without blocking it."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import uuid
from typing import Any


TEXT_FIELDS = ("prompt", "submitted_prompt", "last_assistant_message")
SCALAR_FIELDS = (
    "hook_event_name",
    "session_id",
    "session_title",
    "client_type",
    "cwd",
    "turn_id",
    "tool_name",
    "stop_hook_active",
    "permission_mode",
    "model",
    "source",
)
ENVIRONMENT_FIELDS = (
    "QWEN_PROJECT_DIR",
    "KIMI_CODE_HOME",
    "ZCODE_PLUGIN_ROOT",
    "ZCODE_PLUGIN_DATA",
    "CLAUDE_PLUGIN_ROOT",
    "CLAUDE_PLUGIN_DATA",
)


def _text_summary(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, str):
        return None
    encoded = value.encode("utf-8")
    return {
        "chars": len(value),
        "utf8_bytes": len(encoded),
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "nonempty": bool(value.strip()),
    }


def _event_summary(event: dict[str, Any]) -> dict[str, Any]:
    selected = {
        key: event[key]
        for key in SCALAR_FIELDS
        if isinstance(event.get(key), (str, bool, int, float))
    }
    texts = {
        key: summary
        for key in TEXT_FIELDS
        if (summary := _text_summary(event.get(key))) is not None
    }
    tool_input = event.get("tool_input")
    tool_response = event.get("tool_response")
    return {
        "observed_at_ns": time.time_ns(),
        "event_keys": sorted(event),
        "field_types": {key: type(value).__name__ for key, value in sorted(event.items())},
        "selected": selected,
        "texts": texts,
        "tool_input_keys": sorted(tool_input) if isinstance(tool_input, dict) else None,
        "tool_response_type": type(tool_response).__name__ if "tool_response" in event else None,
        "environment_present": {
            key: bool(os.environ.get(key)) for key in ENVIRONMENT_FIELDS
        },
    }


def _write_summary(output_dir: Path, summary: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    event_name = summary.get("selected", {}).get("hook_event_name", "unknown")
    safe_event = "".join(char if char.isalnum() else "-" for char in str(event_name))
    name = f"{time.time_ns()}-{os.getpid()}-{safe_event}-{uuid.uuid4().hex[:8]}.json"
    target = output_dir / name
    target.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        value = json.load(sys.stdin)
        event = value if isinstance(value, dict) else {}
        _write_summary(args.output_dir, _event_summary(event))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
