#!/usr/bin/env python3
"""Sync the canonical skill into adapter layouts for other agent tools."""

from __future__ import annotations

import json
import shutil
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "chinese-official-writing"
VERSION = "1.6.1"
REPOSITORY_LICENSE = "MIT"
ROOT_LICENSE = ROOT / "LICENSE"
CANONICAL_LICENSE = CANONICAL / "LICENSE"
ROOT_README = ROOT / "README.md"
PACKAGES = ROOT / "packages"
PLUGIN_PACKAGE = PACKAGES / "agent-plugin"
OPENCLAW_PACKAGE = PACKAGES / "openclaw"
CLAUDE_PLUGIN_MANIFEST = PLUGIN_PACKAGE / ".claude-plugin" / "plugin.json"
CODEX_PLUGIN_MANIFEST = PLUGIN_PACKAGE / ".codex-plugin" / "plugin.json"
PACKAGED_CLAUDE_PLUGIN_MANIFEST = CANONICAL / "hooks" / "claude-code" / ".claude-plugin" / "plugin.json"
PACKAGED_CODEX_PLUGIN_MANIFEST = CANONICAL / ".codex-plugin" / "plugin.json"
PACKAGED_WORKBUDDY_PLUGIN_MANIFEST = CANONICAL / ".codebuddy-plugin" / "plugin.json"

TARGETS = {
    "plugin": PLUGIN_PACKAGE / "skills" / "chinese-official-writing",
    "agents": PACKAGES / "agent-skills" / "skills" / "chinese-official-writing",
    "qwen": PACKAGES / "qwen-code" / "skills" / "chinese-official-writing",
    "hermes": PACKAGES / "hermes" / "skills" / "chinese-official-writing",
    "openclaw": OPENCLAW_PACKAGE / "skills" / "chinese_official_writing",
}

TARGET_LICENSES = {
    "plugin": REPOSITORY_LICENSE,
    "agents": REPOSITORY_LICENSE,
    "qwen": REPOSITORY_LICENSE,
    "hermes": REPOSITORY_LICENSE,
    "openclaw": REPOSITORY_LICENSE,
}

CODEX_GATE_FILES = (
    ".codex-plugin/plugin.json",
    ".codebuddy-plugin/plugin.json",
    "references/delivery-review-gate.md",
    "hooks/AGENT_GLUE.md",
    "hooks/host-capabilities.json",
    "hooks/gate_stop_hook.py",
    "hooks/hooks.json",
    "hooks/host_gate_adapter.py",
    "hooks/workbuddy/hooks.json",
    "hooks/claude-code/.claude-plugin/plugin.json",
    "hooks/claude-code/hooks/hooks.json",
    "hooks/claude-code/scripts/gate_stop_hook.py",
    "scripts/review_gate.py",
    "skills/chinese-official-writing/SKILL.md",
)

TARGET_EXCLUDES = {
    "agents": CODEX_GATE_FILES,
    "qwen": CODEX_GATE_FILES,
    "hermes": CODEX_GATE_FILES,
    "openclaw": CODEX_GATE_FILES + ("agents/openai.yaml",),
}


def versioned_text(text: str) -> str:
    text = re.sub(r"chinese-official-writing@\d+\.\d+\.\d+", f"chinese-official-writing@{VERSION}", text)
    text = re.sub(r"--version(?:\s+|=)\d+\.\d+\.\d+", f"--version={VERSION}", text)
    text = re.sub(
        r"^\d+\.\d+\.\d+ \(source: (?:server release metadata and skill frontmatter|repository release metadata and skill frontmatter|skill frontmatter and release candidate metadata)\)",
        f"{VERSION} (source: repository release metadata)",
        text,
        flags=re.M,
    )
    return text


def sync_canonical_license() -> None:
    shutil.copyfile(ROOT_LICENSE, CANONICAL_LICENSE)


def update_plugin_manifest(manifest_path: Path, label: str, license_id: str) -> None:
    if not manifest_path.exists():
        raise RuntimeError(f"missing {label} plugin manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["version"] = VERSION
    manifest["license"] = license_id
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def update_root_readme() -> None:
    ROOT_README.write_text(versioned_text(ROOT_README.read_text(encoding="utf-8")), encoding="utf-8")


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


def copy_skill(target: Path, mode: str) -> None:
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "Thumbs.db")
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(CANONICAL, target, ignore=ignore)
    for relative_path in TARGET_EXCLUDES.get(mode, ()):
        packaged_file = target / relative_path
        if packaged_file.exists():
            packaged_file.unlink()
    shutil.copyfile(ROOT_LICENSE, target / "LICENSE")
    if mode == "openclaw":
        patch_openclaw_frontmatter(target)


def main() -> int:
    if not (CANONICAL / "SKILL.md").exists():
        raise SystemExit(f"missing canonical skill: {CANONICAL}")
    if set(TARGET_LICENSES) != set(TARGETS):
        raise SystemExit("every adapter target must declare an explicit package license")
    if any(license_id != REPOSITORY_LICENSE for license_id in TARGET_LICENSES.values()):
        raise SystemExit("every GitHub package target must use the repository MIT license")
    sync_canonical_license()
    for manifest_path, label in [
        (PACKAGED_CODEX_PLUGIN_MANIFEST, "packaged Codex"),
        (PACKAGED_WORKBUDDY_PLUGIN_MANIFEST, "packaged WorkBuddy"),
        (PACKAGED_CLAUDE_PLUGIN_MANIFEST, "packaged Claude"),
    ]:
        update_plugin_manifest(manifest_path, label, REPOSITORY_LICENSE)
    for mode, target in TARGETS.items():
        copy_skill(target, mode)
        print(f"synced {target.relative_to(ROOT)}")
    update_root_readme()
    print(f"synced {ROOT_README.relative_to(ROOT)}")
    for manifest_path, label in [
        (CLAUDE_PLUGIN_MANIFEST, "Claude"),
        (CODEX_PLUGIN_MANIFEST, "Codex"),
    ]:
        update_plugin_manifest(manifest_path, label, REPOSITORY_LICENSE)
        print(f"synced {manifest_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
