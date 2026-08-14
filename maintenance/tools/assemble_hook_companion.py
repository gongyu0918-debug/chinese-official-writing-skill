#!/usr/bin/env python3
"""Assemble one Hook companion for repository validation or explicit user setup."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import shutil
from typing import Final


ROOT: Final = Path(__file__).resolve().parents[2]
SKILL_ROOT: Final = ROOT / "chinese-official-writing"
HOOK_ROOT: Final = SKILL_ROOT / "hooks"
ADAPTER_ROOT: Final = HOOK_ROOT / "adapters"
CORE_PATH: Final = HOOK_ROOT / "core" / "gate_stop_hook.py"
SHARED_HOST_ADAPTER: Final = ADAPTER_ROOT / "host_gate_adapter.py"


@dataclass(frozen=True)
class HostAdapter:
    name: str
    manifest_target: Path
    adapter_source: Path
    adapter_target: Path
    include_openai_metadata: bool = False

    @property
    def source_root(self) -> Path:
        return ADAPTER_ROOT / self.name


HOST_ADAPTERS: Final = {
    adapter.name: adapter
    for adapter in (
        HostAdapter(
            "codex",
            Path(".codex-plugin/plugin.json"),
            SHARED_HOST_ADAPTER,
            Path("scripts/host_gate_adapter.py"),
            include_openai_metadata=True,
        ),
        HostAdapter(
            "codebuddy",
            Path(".codebuddy-plugin/plugin.json"),
            SHARED_HOST_ADAPTER,
            Path("scripts/host_gate_adapter.py"),
        ),
        HostAdapter(
            "claude-code",
            Path(".claude-plugin/plugin.json"),
            ADAPTER_ROOT / "claude-code" / "gate_stop_hook.py",
            Path("scripts/gate_stop_hook.py"),
        ),
    )
}
SKILL_COPY_EXCLUDES: Final = (
    Path("LICENSE"),
    Path("hooks/adapters"),
    Path("hooks/core"),
)
MARKDOWN_LINK_RE: Final = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
ADAPTER_GUIDE_LINKS: Final = {
    f"[`adapters/{host}/README.md`](adapters/{host}/README.md)": f"`{label}`"
    for host, label in (
        ("codex", "Codex"),
        ("codebuddy", "WorkBuddy / CodeBuddy"),
        ("claude-code", "Claude Code"),
    )
}
CAPABILITY_DEFAULT: Final = "delivery_review"
CAPABILITY_CHOICES: Final = (
    CAPABILITY_DEFAULT,
    "protective_expansion",
    "under_length",
    "delivery_cleanliness",
    "repetition_cleanup",
)


def _is_excluded(relative: Path, adapter: HostAdapter) -> bool:
    if "__pycache__" in relative.parts or relative.suffix == ".pyc":
        return True
    if not adapter.include_openai_metadata and relative == Path("agents/openai.yaml"):
        return True
    return any(relative == excluded or excluded in relative.parents for excluded in SKILL_COPY_EXCLUDES)


def _copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def _copy_skill(output: Path, adapter: HostAdapter) -> None:
    packaged_skill = output / "skills" / "chinese-official-writing"
    for source in sorted(path for path in SKILL_ROOT.rglob("*") if path.is_file()):
        relative = source.relative_to(SKILL_ROOT)
        if not _is_excluded(relative, adapter):
            _copy(source, packaged_skill / relative)
    _copy(CORE_PATH, packaged_skill / "hooks" / "gate_stop_hook.py")
    guide_path = packaged_skill / "hooks" / "README.md"
    guide = guide_path.read_text(encoding="utf-8")
    for source, replacement in ADAPTER_GUIDE_LINKS.items():
        guide = guide.replace(source, replacement)
    guide = guide.replace(
        "## 宿主适配说明\n",
        "## 宿主适配说明\n\n当前 companion 的宿主启用说明见插件根 `README.md`。\n",
        1,
    )
    guide_path.write_text(guide, encoding="utf-8", newline="\n")


def _fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _validate(output: Path, adapter: HostAdapter) -> None:
    expected_manifest = output / adapter.manifest_target
    required = (
        expected_manifest,
        output / "hooks" / "hooks.json",
        output / adapter.adapter_target,
        output / "skills/chinese-official-writing/SKILL.md",
        output / "skills/chinese-official-writing/hooks/gate_stop_hook.py",
        output / "skills/chinese-official-writing/hooks/capabilities/protective_expansion/contract.py",
        output / "skills/chinese-official-writing/hooks/capabilities/protective_expansion/runtime.py",
        output / "skills/chinese-official-writing/hooks/capabilities/under_length/runtime.py",
        output / "skills/chinese-official-writing/hooks/capabilities/delivery_cleanliness/runtime.py",
        output / "skills/chinese-official-writing/scripts/review_gate.py",
        output / "hook-capability.json",
        output / "README.md",
        output / "LICENSE",
    )
    missing = [path.relative_to(output).as_posix() for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"incomplete Hook companion: {missing}")
    manifests = sorted(output.rglob("plugin.json"))
    if manifests != [expected_manifest]:
        raise RuntimeError("Hook companion must contain exactly one host manifest")
    for path in output.rglob("*"):
        if path.is_symlink():
            raise RuntimeError(f"Hook companion cannot contain a symlink: {path}")
        if path.is_file() and "../" in path.read_text(encoding="utf-8", errors="ignore"):
            raise RuntimeError(f"Hook companion contains parent traversal: {path}")
        if path.is_file() and path.suffix.lower() == ".md":
            text = path.read_text(encoding="utf-8")
            for target in MARKDOWN_LINK_RE.findall(text):
                target = target.split("#", 1)[0].strip()
                if not target or target.startswith(("https://", "http://", "mailto:")):
                    continue
                resolved = (path.parent / target).resolve()
                if not resolved.is_relative_to(output) or not resolved.exists():
                    raise RuntimeError(
                        f"Hook companion contains a broken local Markdown link: {path} -> {target}"
                    )


def assemble(
    host: str, output: Path, capability: str = CAPABILITY_DEFAULT
) -> dict[str, object]:
    """Assemble files only; never install, enable, probe hosts, or use the network."""
    adapter = HOST_ADAPTERS.get(host)
    if adapter is None:
        raise ValueError(f"unsupported host: {host}")
    if capability not in CAPABILITY_CHOICES:
        raise ValueError(f"unsupported Hook capability: {capability}")
    output = output.expanduser().resolve()
    if output.exists():
        raise FileExistsError(f"output already exists: {output}")
    output.mkdir(parents=True)
    try:
        _copy_skill(output, adapter)
        _copy(adapter.source_root / "manifest.json", output / adapter.manifest_target)
        _copy(adapter.source_root / "hooks.json", output / "hooks/hooks.json")
        _copy(adapter.adapter_source, output / adapter.adapter_target)
        _copy(adapter.source_root / "README.md", output / "README.md")
        _copy(SKILL_ROOT / "LICENSE", output / "LICENSE")
        (output / "hook-capability.json").write_text(
            json.dumps(
                {"schema_version": 1, "capability": capability},
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        _validate(output, adapter)
    except Exception:
        shutil.rmtree(output, ignore_errors=True)
        raise
    files = sorted(path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file())
    return {
        "host": host,
        "output": str(output),
        "files": len(files),
        "fingerprint": _fingerprint(output),
        "capability": capability,
        "installed": False,
        "enabled": False,
        "network_used": False,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="仓库维护期组装工具：只复制静态兼容文件，不安装、不启用、不联网。"
    )
    parser.add_argument("--host", required=True, choices=tuple(HOST_ADAPTERS))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--capability", choices=CAPABILITY_CHOICES, default=CAPABILITY_DEFAULT
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(
        json.dumps(
            assemble(args.host, args.output, args.capability),
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
