#!/usr/bin/env python3
"""Build a clean SkillHub package from the tracked canonical Skill."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "chinese-official-writing"
ROOT_LICENSE = ROOT / "LICENSE"
SKILLHUB_LICENSE_NAME = "LICENSE.md"
DEFAULT_SLUG = "chinese-official-writing"
DEFAULT_DISPLAY_NAME = "中文公文写作"
DEFAULT_SUMMARY = "用于中文公文和正式工作材料的起草、改写、压缩与复核，强调文种准确、事实克制、数据可追溯和公文语气自然。"
DEFAULT_TAGS = ("chinese", "official-document", "writing", "gongwen", "ai-compute")
PACKAGE_EXCLUDES = {"agents/openai.yaml", "LICENSE"}
FORBIDDEN_FRONTMATTER_KEYS = {
    "homepage",
    "license",
    "metadata",
    "compatible_agents",
    "qwen_code",
    "openclaw",
    "hermes",
}
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def split_skill(skill_text: str) -> tuple[dict[str, str], str]:
    parts = skill_text.replace("\r\n", "\n").split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError("canonical SKILL.md frontmatter is malformed")

    fields: dict[str, str] = {}
    for line in parts[1].splitlines():
        if not line or line[0].isspace() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"')
    for required in ("name", "description"):
        if not fields.get(required):
            raise ValueError(f"canonical SKILL.md is missing {required}")
    return fields, parts[2].strip()


def tracked_canonical_files() -> list[str]:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "--", "chinese-official-writing"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    prefix = "chinese-official-writing/"
    relative_files: list[str] = []
    for raw in completed.stdout.splitlines():
        path = raw.replace("\\", "/")
        if not path.startswith(prefix):
            continue
        relative = path[len(prefix) :]
        if not relative or relative in PACKAGE_EXCLUDES:
            continue
        parts = Path(relative).parts
        if "__pycache__" in parts or relative.endswith(".pyc"):
            continue
        if Path(relative).is_absolute() or ".." in parts:
            raise ValueError(f"unsafe tracked path: {relative}")
        relative_files.append(Path(relative).as_posix())
    return sorted(set(relative_files))


def skillhub_frontmatter(
    *,
    slug: str,
    version: str,
    display_name: str,
    summary: str,
    name: str,
    description: str,
) -> str:
    tags = ", ".join(DEFAULT_TAGS)
    lines = [
        "---",
        f"slug: {slug}",
        f"version: {json.dumps(version, ensure_ascii=False)}",
        f"displayName: {json.dumps(display_name, ensure_ascii=False)}",
        f"summary: {json.dumps(summary, ensure_ascii=False)}",
        f"tags: [{tags}]",
        f"name: {name}",
        f"description: {description}",
        "---",
    ]
    return "\n".join(lines)


def build_package(
    output: Path,
    *,
    version: str,
    slug: str = DEFAULT_SLUG,
    display_name: str = DEFAULT_DISPLAY_NAME,
    summary: str = DEFAULT_SUMMARY,
) -> dict[str, object]:
    output = output.resolve()
    if output.exists():
        raise FileExistsError(f"output already exists: {output}")
    if not SLUG_PATTERN.fullmatch(slug):
        raise ValueError(f"invalid slug: {slug}")
    if not SEMVER_PATTERN.fullmatch(version):
        raise ValueError(f"invalid version: {version}")

    tracked = tracked_canonical_files()
    if "SKILL.md" not in tracked:
        raise ValueError("tracked canonical package is missing SKILL.md")
    if SKILLHUB_LICENSE_NAME in tracked:
        raise ValueError(f"canonical package unexpectedly owns generated {SKILLHUB_LICENSE_NAME}")

    canonical_text = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
    fields, body = split_skill(canonical_text)
    output.mkdir(parents=True)

    for relative in tracked:
        source = CANONICAL / relative
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if relative == "SKILL.md":
            frontmatter = skillhub_frontmatter(
                slug=slug,
                version=version,
                display_name=display_name,
                summary=summary,
                name=fields["name"],
                description=fields["description"],
            )
            target.write_text(f"{frontmatter}\n\n{body}\n", encoding="utf-8", newline="\n")
        else:
            shutil.copyfile(source, target)

    shutil.copyfile(ROOT_LICENSE, output / SKILLHUB_LICENSE_NAME)

    meta = {"slug": slug, "version": version}
    (output / "_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    skill_fields, packaged_body = split_skill((output / "SKILL.md").read_text(encoding="utf-8"))
    for key in FORBIDDEN_FRONTMATTER_KEYS:
        if key in skill_fields:
            raise RuntimeError(f"forbidden SkillHub frontmatter key: {key}")
    if packaged_body != body:
        raise RuntimeError("packaged SKILL body differs from canonical")
    if (output / SKILLHUB_LICENSE_NAME).read_bytes() != ROOT_LICENSE.read_bytes():
        raise RuntimeError("packaged SkillHub license differs from root MIT license")
    if (output / "LICENSE").exists():
        raise RuntimeError("extensionless LICENSE must stay out of the SkillHub package")

    files = sorted(path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file())
    return {
        "output": str(output),
        "slug": slug,
        "version": version,
        "files": len(files),
        "excluded": sorted(PACKAGE_EXCLUDES),
        "license": SKILLHUB_LICENSE_NAME,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--slug", default=DEFAULT_SLUG)
    parser.add_argument("--display-name", default=DEFAULT_DISPLAY_NAME)
    parser.add_argument("--summary", default=DEFAULT_SUMMARY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_package(
        args.output,
        version=args.version,
        slug=args.slug,
        display_name=args.display_name,
        summary=args.summary,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
