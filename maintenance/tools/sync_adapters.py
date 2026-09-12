#!/usr/bin/env python3
"""Sync the canonical skill into adapter layouts for other agent tools."""

from __future__ import annotations

import shutil
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "chinese-official-writing"
VERSION = "1.6.30"
REPOSITORY_LICENSE = "MIT"
ROOT_LICENSE = ROOT / "LICENSE"
CANONICAL_LICENSE = CANONICAL / "LICENSE"
PACKAGES = ROOT / "packages"
OPENCLAW_PACKAGE = PACKAGES / "openclaw"

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
    for mode, target in TARGETS.items():
        copy_skill(target, mode)
        print(f"synced {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
