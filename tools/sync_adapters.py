#!/usr/bin/env python3
"""Sync the canonical skill into adapter layouts for other agent tools."""

from __future__ import annotations

import json
import shutil
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "chinese-official-writing"
VERSION = "1.6.0"
FULL_PACKAGE_LICENSE = "MIT"
PURE_SKILL_LICENSE = "MIT-0"
ROOT_LICENSE = ROOT / "LICENSE"
PURE_SKILL_LICENSE_FILE = ROOT / "LICENSE-SKILL"
CANONICAL_LICENSE = CANONICAL / "LICENSE"
ROOT_README = ROOT / "README.md"
CLAUDE_PLUGIN_MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
CODEX_PLUGIN_MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
PACKAGED_CLAUDE_PLUGIN_MANIFEST = CANONICAL / "hooks" / "claude-code" / ".claude-plugin" / "plugin.json"

TARGETS = {
    "claude": ROOT / "skills" / "chinese-official-writing",
    "agents": ROOT / ".agents" / "skills" / "chinese-official-writing",
    "qwen": ROOT / ".qwen" / "skills" / "chinese-official-writing",
    "hermes": ROOT / "hermes" / "skills" / "chinese-official-writing",
}

TARGET_LICENSES = {
    "claude": FULL_PACKAGE_LICENSE,
    "agents": PURE_SKILL_LICENSE,
    "qwen": PURE_SKILL_LICENSE,
    "hermes": PURE_SKILL_LICENSE,
}

STALE_TARGET_FILES = (
    "references/academic-writing.md",
    "references/academic-proposal.md",
    "references/academic-literature-review.md",
    "references/official-writing.md",
    "scripts/gate_stop_hook.py",
)

CODEX_GATE_FILES = (
    "references/delivery-review-gate.md",
    "hooks/AGENT_GLUE.md",
    "hooks/host-capabilities.json",
    "hooks/gate_stop_hook.py",
    "hooks/claude-code/.claude-plugin/plugin.json",
    "hooks/claude-code/hooks/hooks.json",
    "hooks/claude-code/scripts/gate_stop_hook.py",
    "scripts/review_gate.py",
)

TARGET_EXCLUDES = {
    "agents": CODEX_GATE_FILES,
    "qwen": CODEX_GATE_FILES,
    "hermes": CODEX_GATE_FILES,
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


def copy_skill(target: Path, mode: str) -> None:
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "Thumbs.db")
    for relative_path in STALE_TARGET_FILES:
        stale_file = target / relative_path
        if stale_file.exists():
            stale_file.unlink()
    shutil.copytree(CANONICAL, target, ignore=ignore, dirs_exist_ok=True)
    for relative_path in TARGET_EXCLUDES.get(mode, ()):
        packaged_file = target / relative_path
        if packaged_file.exists():
            packaged_file.unlink()
    if TARGET_LICENSES[mode] == PURE_SKILL_LICENSE:
        shutil.copyfile(PURE_SKILL_LICENSE_FILE, target / "LICENSE")


def main() -> int:
    if not (CANONICAL / "SKILL.md").exists():
        raise SystemExit(f"missing canonical skill: {CANONICAL}")
    if set(TARGET_LICENSES) != set(TARGETS):
        raise SystemExit("every adapter target must declare an explicit package license")
    sync_canonical_license()
    update_plugin_manifest(PACKAGED_CLAUDE_PLUGIN_MANIFEST, "packaged Claude", FULL_PACKAGE_LICENSE)
    for mode, target in TARGETS.items():
        copy_skill(target, mode)
        print(f"synced {target.relative_to(ROOT)}")
    update_root_readme()
    print(f"synced {ROOT_README.relative_to(ROOT)}")
    for manifest_path, label in [
        (CLAUDE_PLUGIN_MANIFEST, "Claude"),
        (CODEX_PLUGIN_MANIFEST, "Codex"),
    ]:
        update_plugin_manifest(manifest_path, label, FULL_PACKAGE_LICENSE)
        print(f"synced {manifest_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
