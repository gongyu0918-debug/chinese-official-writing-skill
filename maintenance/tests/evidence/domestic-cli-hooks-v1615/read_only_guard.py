#!/usr/bin/env python3
"""Block mutating or interactive tools during isolated CLI writing tests."""

from __future__ import annotations

import json
import sys


ALLOWED_TOOLS = {"Glob", "Grep", "Read", "ReadFile", "Skill"}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        print("read-only test guard could not parse hook input", file=sys.stderr)
        return 2

    tool_name = payload.get("tool_name") or payload.get("toolName")
    if tool_name in ALLOWED_TOOLS:
        return 0

    print(
        f"read-only real-writing test blocks tool: {tool_name or '<missing>'}",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
