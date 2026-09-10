#!/usr/bin/env python3
"""Build disposable compatibility packages from the single canonical Skill."""

from __future__ import annotations

import argparse
import json
import shutil
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "chinese-official-writing"
VERSION = "1.6.33"
REPOSITORY_LICENSE = "MIT"
ROOT_LICENSE = ROOT / "LICENSE"
CANONICAL_LICENSE = CANONICAL / "LICENSE"
PACKAGES = ROOT / "output" / "compatibility-packages"
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
        raise FileExistsError(f"output already exists; choose a new output root: {target}")
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


def build_packages(output_root: Path = PACKAGES, modes: tuple[str, ...] | None = None) -> dict[str, Path]:
    """Generate installable copies, without writing to canonical or tracked packages."""
    output_root = Path(output_root).resolve()
    for protected in (CANONICAL.resolve(), (ROOT / "packages").resolve()):
        if output_root == protected or protected in output_root.parents or output_root in protected.parents:
            raise ValueError(f"output overlaps a source directory: {output_root}")
    selected = tuple(TARGETS) if modes is None else modes
    if not selected or any(mode not in TARGETS for mode in selected):
        raise ValueError(f"unknown or empty package selection: {selected}")
    if len(set(selected)) != len(selected):
        raise ValueError("duplicate package selection")
    if not (CANONICAL / "SKILL.md").exists():
        raise FileNotFoundError(f"missing canonical skill: {CANONICAL}")
    if set(TARGET_LICENSES) != set(TARGETS):
        raise RuntimeError("every adapter target must declare an explicit package license")
    if any(license_id != REPOSITORY_LICENSE for license_id in TARGET_LICENSES.values()):
        raise RuntimeError("every GitHub package target must use the repository MIT license")
    targets = {mode: output_root / TARGETS[mode].relative_to(PACKAGES) for mode in selected}
    for target in targets.values():
        if output_root not in target.resolve().parents:
            raise ValueError(f"output escapes build directory: {target}")
        if target.exists():
            raise FileExistsError(f"output already exists; choose a new output root: {target}")
    validate_hook_sources()
    for mode, target in targets.items():
        copy_skill(target, mode)
        guide = ROOT / "packages" / target.parents[1].name / "README.md"
        if guide.is_file():
            shutil.copyfile(guide, target.parents[1] / "README.md")
    return targets


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=PACKAGES, help="Fresh build directory (default: output/compatibility-packages)")
    parser.add_argument("--host", choices=tuple(TARGETS), action="append", help="Build only the selected plain Skill package; repeat for multiple hosts")
    args = parser.parse_args()
    targets = build_packages(args.output_root, tuple(args.host) if args.host else None)
    for mode, target in targets.items():
        print(f"{mode}: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
