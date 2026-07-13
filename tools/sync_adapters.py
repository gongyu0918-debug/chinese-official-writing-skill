#!/usr/bin/env python3
"""Sync the canonical skill into adapter layouts for other agent tools."""

from __future__ import annotations

import json
import shutil
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "chinese-official-writing"
VERSION = "1.5.10"
ROOT_README = ROOT / "README.md"
OPENCLAW_MARKETPLACE_README = ROOT / "openclaw" / "marketplace-readme.md"
OPENCLAW_README = ROOT / "openclaw" / "README.md"
OPENCLAW_SKILL_CARD = ROOT / "openclaw" / "skill-card.md"
CLAUDE_PLUGIN_MANIFEST = ROOT / ".claude-plugin" / "plugin.json"

TARGETS = {
    "claude": ROOT / "skills" / "chinese-official-writing",
    "agents": ROOT / ".agents" / "skills" / "chinese-official-writing",
    "qwen": ROOT / ".qwen" / "skills" / "chinese-official-writing",
    "hermes": ROOT / "hermes" / "skills" / "chinese-official-writing",
    "openclaw": ROOT / "openclaw" / "skills" / "chinese_official_writing",
}

STALE_SPLIT_REFERENCES = (
    "references/academic-writing.md",
    "references/academic-proposal.md",
    "references/academic-literature-review.md",
    "references/official-writing.md",
)


def versioned_text(text: str) -> str:
    text = re.sub(r"chinese-official-writing@\d+\.\d+\.\d+", f"chinese-official-writing@{VERSION}", text)
    text = re.sub(r"--version(?:\s+|=)\d+\.\d+\.\d+", f"--version={VERSION}", text)
    text = re.sub(
        r"^\d+\.\d+\.\d+ \(source: server release metadata and skill frontmatter\)",
        f"{VERSION} (source: server release metadata and skill frontmatter)",
        text,
        flags=re.M,
    )
    return text


def versioned_skill_text(text: str) -> str:
    return re.sub(r'version: "\d+\.\d+\.\d+"', f'version: "{VERSION}"', text)


def update_canonical_skill_version() -> None:
    skill_file = CANONICAL / "SKILL.md"
    skill_file.write_text(
        versioned_skill_text(skill_file.read_text(encoding="utf-8")),
        encoding="utf-8",
        newline="\n",
    )


def patch_frontmatter(target: Path, mode: str) -> None:
    skill_file = target / "SKILL.md"
    text = versioned_skill_text(skill_file.read_text(encoding="utf-8"))
    original = text
    if mode == "openclaw":
        text = text.replace("name: chinese-official-writing", "name: chinese_official_writing", 1)
        if "\ncategory: writing\n" not in text.split("---", 2)[1]:
            text = text.replace(
                "license: MIT-0\n",
                "license: MIT-0\ncategory: writing\ntags:\n  - chinese\n  - official-document\n  - writing\n  - gongwen\n  - ai-compute\n",
                1,
            )
        text = re.sub(r"\n  hermes:\n(?:    .+\n)+", "\n", text, count=1)
    elif mode == "hermes":
        if f'\nversion: "{VERSION}"\n' not in text.split("---", 2)[1]:
            text = text.replace("license: MIT-0\n", f'license: MIT-0\nversion: "{VERSION}"\n', 1)
        text = re.sub(r"\n  openclaw:\n(?:    .+\n)+(?=  hermes:)", "\n", text, count=1)
    if text != original:
        skill_file.write_text(text, encoding="utf-8", newline="\n")


def patch_openclaw_skill_body(target: Path) -> None:
    """Keep OpenClaw's executable body identical to the canonical skill.

    User-facing marketplace copy remains in README.md. Do not concatenate it
    into the executable instructions or duplicate the canonical workflow.
    """

    skill_file = target / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise RuntimeError("OpenClaw SKILL.md frontmatter is malformed")
    canonical_parts = (CANONICAL / "SKILL.md").read_text(encoding="utf-8").split("---", 2)
    if len(canonical_parts) < 3:
        raise RuntimeError("canonical SKILL.md frontmatter is malformed")
    canonical_body = canonical_parts[2].strip()
    skill_file.write_text(f"---{parts[1]}---\n\n{canonical_body}\n", encoding="utf-8")


def update_claude_plugin_manifest() -> None:
    if not CLAUDE_PLUGIN_MANIFEST.exists():
        raise RuntimeError(f"missing Claude plugin manifest: {CLAUDE_PLUGIN_MANIFEST}")
    manifest = json.loads(CLAUDE_PLUGIN_MANIFEST.read_text(encoding="utf-8"))
    manifest["version"] = VERSION
    CLAUDE_PLUGIN_MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def update_root_readme() -> None:
    ROOT_README.write_text(versioned_text(ROOT_README.read_text(encoding="utf-8")), encoding="utf-8")


def update_openclaw_readme_sources() -> None:
    OPENCLAW_MARKETPLACE_README.write_text(
        versioned_text(OPENCLAW_MARKETPLACE_README.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    OPENCLAW_README.write_text(
        versioned_text(OPENCLAW_README.read_text(encoding="utf-8")),
        encoding="utf-8",
    )


def update_openclaw_skill_card_source() -> None:
    OPENCLAW_SKILL_CARD.write_text(
        versioned_text(OPENCLAW_SKILL_CARD.read_text(encoding="utf-8")),
        encoding="utf-8",
    )


def copy_skill(target: Path, mode: str) -> None:
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "Thumbs.db")
    for relative_path in STALE_SPLIT_REFERENCES:
        stale_file = target / relative_path
        if stale_file.exists():
            stale_file.unlink()
    shutil.copytree(CANONICAL, target, ignore=ignore, dirs_exist_ok=True)
    patch_frontmatter(target, mode)
    if mode == "openclaw":
        (target / "README.md").write_text(
            versioned_text(OPENCLAW_MARKETPLACE_README.read_text(encoding="utf-8")),
            encoding="utf-8",
        )
        reserved_skill_card = target / "skill-card.md"
        if reserved_skill_card.exists():
            reserved_skill_card.unlink()
        patch_openclaw_skill_body(target)


def main() -> int:
    if not (CANONICAL / "SKILL.md").exists():
        raise SystemExit(f"missing canonical skill: {CANONICAL}")
    update_canonical_skill_version()
    update_openclaw_readme_sources()
    print("synced openclaw README sources")
    for mode, target in TARGETS.items():
        copy_skill(target, mode)
        print(f"synced {target.relative_to(ROOT)}")
    update_root_readme()
    print(f"synced {ROOT_README.relative_to(ROOT)}")
    update_openclaw_skill_card_source()
    print(f"synced {OPENCLAW_SKILL_CARD.relative_to(ROOT)}")
    update_claude_plugin_manifest()
    print(f"synced {CLAUDE_PLUGIN_MANIFEST.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
