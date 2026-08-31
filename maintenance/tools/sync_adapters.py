#!/usr/bin/env python3
"""Sync the canonical skill into adapter layouts for other agent tools."""

from __future__ import annotations

import json
import shutil
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "chinese-official-writing"
VERSION = "1.6.23"
REPOSITORY_LICENSE = "MIT"
ROOT_LICENSE = ROOT / "LICENSE"
CANONICAL_LICENSE = CANONICAL / "LICENSE"
PACKAGES = ROOT / "packages"
OPENCLAW_PACKAGE = PACKAGES / "openclaw"
HOOKS = CANONICAL / "hooks"
HOOK_ADAPTERS = HOOKS / "adapters"
HOOK_CORE = HOOKS / "core" / "gate_stop_hook.py"
HOOK_EVENT_TIMEOUT_SECONDS = {
    "UserPromptSubmit": 10,
    "PostToolUse": 10,
    "Stop": 30,
}
HOOK_TIMEOUT_FIELDS = {
    "zcode": "timeoutMs",
}
HOOK_TIMEOUT_MILLISECONDS_HOSTS = {"zcode", "qwen-code"}
HOOK_ROUTE_PARAGRAPH = (
    "\n\n用户明确要求处理交付门禁 Hook 时，读取 `hooks/README.md`。"
    "普通起草、改稿、压缩和复核不加载该页，也不自动启用 Hook。"
)

TARGETS = {
    "agents": PACKAGES / "agent-skills" / "skills" / "chinese-official-writing",
    "qwen": PACKAGES / "qwen-code" / "skills" / "chinese-official-writing",
    "qwenwork": PACKAGES / "qwenwork" / "skills" / "chinese-official-writing",
    "hermes": PACKAGES / "hermes" / "skills" / "chinese-official-writing",
    "openclaw": OPENCLAW_PACKAGE / "skills" / "chinese_official_writing",
}

TARGET_LICENSES = {
    "agents": REPOSITORY_LICENSE,
    "qwen": REPOSITORY_LICENSE,
    "qwenwork": REPOSITORY_LICENSE,
    "hermes": REPOSITORY_LICENSE,
    "openclaw": REPOSITORY_LICENSE,
}

OPTIONAL_GATE_FILES = (
    "hooks",
    "references/delivery-review-gate.md",
    "scripts/review_gate.py",
)

TARGET_EXCLUDES = {
    "agents": OPTIONAL_GATE_FILES,
    "qwen": OPTIONAL_GATE_FILES,
    "qwenwork": OPTIONAL_GATE_FILES,
    "hermes": OPTIONAL_GATE_FILES,
    "openclaw": OPTIONAL_GATE_FILES + ("agents/openai.yaml",),
}


def sync_canonical_license() -> None:
    shutil.copyfile(ROOT_LICENSE, CANONICAL_LICENSE)


def patch_openclaw_frontmatter(target: Path) -> None:
    skill_path = target / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise RuntimeError(f"invalid OpenClaw SKILL frontmatter: {skill_path}")
    frontmatter = parts[1]
    frontmatter = re.sub(
        r"^name: chinese-official-writing$",
        "name: chinese_official_writing",
        frontmatter,
        flags=re.M,
    )
    frontmatter = re.sub(
        r"^metadata:\n",
        f'license: {REPOSITORY_LICENSE}\ncategory: writing\nmetadata:\n  version: "{VERSION}"\n',
        frontmatter,
        flags=re.M,
    )
    skill_path.write_text(f"---{frontmatter}---{parts[2]}", encoding="utf-8")


def remove_unavailable_hook_route(target: Path) -> None:
    skill_path = target / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8")
    if text.count(HOOK_ROUTE_PARAGRAPH) != 1:
        raise RuntimeError(f"unexpected Hook route paragraph: {skill_path}")
    skill_path.write_text(text.replace(HOOK_ROUTE_PARAGRAPH, ""), encoding="utf-8")


def _copy_ignore(directory: str, names: list[str]) -> set[str]:
    ignored = {
        name
        for name in names
        if name in {"__pycache__", ".DS_Store", "Thumbs.db"} or name.endswith(".pyc")
    }
    if Path(directory).resolve() == CANONICAL.resolve() and "hooks" in names:
        ignored.add("hooks")
    return ignored


def _remove_packaged_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def copy_skill(
    target: Path, mode: str, *, extra_excludes: tuple[str, ...] = ()
) -> None:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(CANONICAL, target, ignore=_copy_ignore)
    for relative_path in TARGET_EXCLUDES.get(mode, ()) + extra_excludes:
        _remove_packaged_path(target / relative_path)
    shutil.copyfile(ROOT_LICENSE, target / "LICENSE")
    if mode in TARGET_EXCLUDES:
        remove_unavailable_hook_route(target)
    if mode == "openclaw":
        patch_openclaw_frontmatter(target)


def validate_hook_sources() -> None:
    if not HOOK_CORE.is_file():
        raise RuntimeError(f"missing Hook core: {HOOK_CORE}")
    for host in ("codex", "codebuddy", "claude-code", "zcode", "qwen-code"):
        adapter_root = HOOK_ADAPTERS / host
        for required in ("manifest.json", "hooks.json"):
            if not (adapter_root / required).is_file():
                raise RuntimeError(f"missing {host} Hook adapter source: {required}")
        hooks_path = adapter_root / "hooks.json"
        hooks = json.loads(hooks_path.read_text(encoding="utf-8")).get("hooks")
        if not isinstance(hooks, dict) or set(hooks) != set(HOOK_EVENT_TIMEOUT_SECONDS):
            raise RuntimeError(f"unexpected {host} hook events: {hooks_path}")
        for event, expected_timeout in HOOK_EVENT_TIMEOUT_SECONDS.items():
            timeout_field = HOOK_TIMEOUT_FIELDS.get(host, "timeout")
            actual_timeout = hooks[event][0]["hooks"][0].get(timeout_field)
            expected_value = (
                expected_timeout * 1000
                if host in HOOK_TIMEOUT_MILLISECONDS_HOSTS
                else expected_timeout
            )
            if actual_timeout != expected_value:
                raise RuntimeError(
                    f"unexpected {host} {event} timeout: {actual_timeout!r}"
                )
    kimi_root = HOOK_ADAPTERS / "kimi-code"
    for required in ("manifest.json", "gate_stop_hook.py"):
        if not (kimi_root / required).is_file():
            raise RuntimeError(f"missing kimi-code Hook adapter source: {required}")
    manifest = json.loads((kimi_root / "manifest.json").read_text(encoding="utf-8"))
    hooks = manifest.get("hooks")
    if not isinstance(hooks, list):
        raise RuntimeError("unexpected kimi-code inline hooks")
    by_event = {hook.get("event"): hook for hook in hooks if isinstance(hook, dict)}
    if set(by_event) != set(HOOK_EVENT_TIMEOUT_SECONDS):
        raise RuntimeError(f"unexpected kimi-code hook events: {sorted(by_event)}")
    for event, expected_timeout in HOOK_EVENT_TIMEOUT_SECONDS.items():
        actual_timeout = by_event[event].get("timeout")
        if actual_timeout != expected_timeout:
            raise RuntimeError(
                f"unexpected kimi-code {event} timeout: {actual_timeout!r}"
            )


def main() -> int:
    if not (CANONICAL / "SKILL.md").exists():
        raise SystemExit(f"missing canonical skill: {CANONICAL}")
    if set(TARGET_LICENSES) != set(TARGETS):
        raise SystemExit("every adapter target must declare an explicit package license")
    if any(license_id != REPOSITORY_LICENSE for license_id in TARGET_LICENSES.values()):
        raise SystemExit("every GitHub package target must use the repository MIT license")
    sync_canonical_license()
    validate_hook_sources()
    for mode, target in TARGETS.items():
        copy_skill(target, mode)
        print(f"synced {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
