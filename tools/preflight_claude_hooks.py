#!/usr/bin/env python3
"""Validate the local Claude Code adapter without loading a model or changing config."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLUGIN_DIRECTORY = ROOT / "agent-glue" / "claude-code"
MINIMUM_VERSION = (2, 1, 195)
VERSION_RE = re.compile(r"\b(\d+)\.(\d+)\.(\d+)\b")
EXPECTED_EVENTS = ("UserPromptSubmit", "PostToolUse", "Stop")


def parse_version(value: str) -> tuple[int, int, int] | None:
    match = VERSION_RE.search(value)
    if match is None:
        return None
    return tuple(int(part) for part in match.groups())


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def validate_plugin_layout(plugin_directory: Path) -> list[str]:
    errors: list[str] = []
    manifest = _read_json(plugin_directory / ".claude-plugin" / "plugin.json")
    hooks = _read_json(plugin_directory / "hooks" / "hooks.json")
    script = plugin_directory / "scripts" / "gate_stop_hook.py"
    if manifest is None:
        errors.append("missing or invalid Claude plugin manifest")
    elif manifest.get("name") != "chinese-official-writing-gate":
        errors.append("unexpected Claude plugin name")
    if hooks is None or not isinstance(hooks.get("hooks"), dict):
        errors.append("missing or invalid Claude hook manifest")
        return errors
    hook_groups = hooks["hooks"]
    if tuple(hook_groups.keys()) != EXPECTED_EVENTS:
        errors.append("Claude hook events must be UserPromptSubmit, PostToolUse, Stop")
    post_groups = hook_groups.get("PostToolUse")
    if not isinstance(post_groups, list) or len(post_groups) != 1:
        errors.append("PostToolUse must have exactly one group")
    elif post_groups[0].get("matcher") != "Bash|Read":
        errors.append("PostToolUse matcher must be Bash|Read")
    for event_name in EXPECTED_EVENTS:
        groups = hook_groups.get(event_name)
        if not isinstance(groups, list) or len(groups) != 1:
            errors.append(f"{event_name} must have exactly one hook group")
            continue
        handlers = groups[0].get("hooks")
        if not isinstance(handlers, list) or len(handlers) != 1:
            errors.append(f"{event_name} must have exactly one command hook")
            continue
        handler = handlers[0]
        command = handler.get("command")
        if handler.get("type") != "command" or not isinstance(command, str):
            errors.append(f"{event_name} must use a command hook")
        elif "CLAUDE_PLUGIN_ROOT" not in command or "gate_stop_hook.py" not in command:
            errors.append(f"{event_name} command must load the bundled adapter")
    if not script.is_file():
        errors.append("missing Claude gate adapter")
    return errors


def _local_version(claude_binary: str) -> tuple[int, int, int] | None:
    try:
        completed = subprocess.run(
            [claude_binary, "--version"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    return parse_version(completed.stdout)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--plugin-dir", type=Path, default=DEFAULT_PLUGIN_DIRECTORY)
    parser.add_argument(
        "--version-text",
        help="Test-only replacement for `claude --version`; never runs Claude when supplied.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    version = parse_version(args.version_text) if args.version_text is not None else _local_version(args.claude_bin)
    errors = validate_plugin_layout(args.plugin_dir.resolve())
    if version is None:
        errors.append("could not read a Claude Code version")
    elif version < MINIMUM_VERSION:
        errors.append(
            "Claude Code version must be at least " + ".".join(str(part) for part in MINIMUM_VERSION)
        )
    result = {
        "claude_version": ".".join(str(part) for part in version) if version else None,
        "minimum_version": ".".join(str(part) for part in MINIMUM_VERSION),
        "plugin_directory": str(args.plugin_dir.resolve()),
        "errors": errors,
        "no_model_invocation": True,
        "configuration_mutation": False,
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
