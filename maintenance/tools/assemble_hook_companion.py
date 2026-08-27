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
SINGLE_PASS_REVIEW_PATH: Final = HOOK_ROOT / "core" / "single_pass_final_review.py"
SHARED_HOST_ADAPTER: Final = ADAPTER_ROOT / "host_gate_adapter.py"


@dataclass(frozen=True)
class HostAdapter:
    name: str
    manifest_target: Path | None
    adapter_source: Path
    adapter_target: Path
    manifest_source: Path | None = None
    hooks_target: Path | None = Path("hooks/hooks.json")
    include_openai_metadata: bool = False
    skill_target: Path = Path("skills/chinese-official-writing")
    capability_target: Path = Path("hook-capability.json")
    extra_files: tuple[tuple[Path, Path], ...] = ()

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
        HostAdapter(
            "zcode",
            Path(".zcode-plugin/plugin.json"),
            ADAPTER_ROOT / "claude-code" / "gate_stop_hook.py",
            Path("scripts/gate_stop_hook.py"),
        ),
        HostAdapter(
            "qwen-code",
            Path("qwen-extension.json"),
            ADAPTER_ROOT / "qwen-code" / "gate_stop_hook.py",
            Path("scripts/gate_stop_hook.py"),
        ),
        HostAdapter(
            "kimi-code",
            Path("kimi.plugin.json"),
            ADAPTER_ROOT / "kimi-code" / "gate_stop_hook.py",
            Path("scripts/gate_stop_hook.py"),
            hooks_target=None,
        ),
        HostAdapter(
            "opencode",
            None,
            ADAPTER_ROOT / "opencode" / "opencode_gate_plugin.js",
            Path(".opencode/plugins/chinese-official-writing-gate.js"),
            hooks_target=None,
            skill_target=Path(".opencode/skills/chinese-official-writing"),
            capability_target=Path(".opencode/hook-capability.json"),
        ),
        HostAdapter(
            "hermes-agent",
            Path("plugin.yaml"),
            ADAPTER_ROOT / "hermes-agent" / "__init__.py",
            Path("__init__.py"),
            manifest_source=ADAPTER_ROOT / "hermes-agent" / "plugin.yaml",
            hooks_target=None,
        ),
        HostAdapter(
            "deepseek-harness",
            Path("package.json"),
            ADAPTER_ROOT / "deepseek-harness" / "index.mjs",
            Path("index.mjs"),
            manifest_source=ADAPTER_ROOT / "deepseek-harness" / "package.json",
            hooks_target=None,
            extra_files=(
                (
                    ADAPTER_ROOT / "deepseek-harness" / "cordis.patch.yml",
                    Path("cordis.patch.yml"),
                ),
            ),
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
        ("zcode", "ZCode"),
        ("qwen-code", "Qwen Code"),
        ("kimi-code", "Kimi Code CLI"),
        ("opencode", "OpenCode"),
        ("hermes-agent", "Hermes Agent"),
        ("deepseek-harness", "DeepSeek Harness"),
    )
}
CAPABILITY_DEFAULT: Final = "delivery_review"
CAPABILITY_CHOICES: Final = (
    CAPABILITY_DEFAULT,
    "protective_expansion",
    "under_length",
    "over_length",
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
    packaged_skill = output / adapter.skill_target
    for source in sorted(path for path in SKILL_ROOT.rglob("*") if path.is_file()):
        relative = source.relative_to(SKILL_ROOT)
        if not _is_excluded(relative, adapter):
            _copy(source, packaged_skill / relative)
    _copy(CORE_PATH, packaged_skill / "hooks" / "gate_stop_hook.py")
    if adapter.name == "hermes-agent":
        _copy(
            SINGLE_PASS_REVIEW_PATH,
            packaged_skill / "hooks" / "single_pass_final_review.py",
        )
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
    expected_manifest = output / adapter.manifest_target if adapter.manifest_target else None
    packaged_skill = output / adapter.skill_target
    required = [
        output / adapter.adapter_target,
        packaged_skill / "SKILL.md",
        packaged_skill / "hooks/gate_stop_hook.py",
        packaged_skill / "hooks/capabilities/protective_expansion/contract.py",
        packaged_skill / "hooks/capabilities/protective_expansion/runtime.py",
        packaged_skill / "hooks/capabilities/under_length/runtime.py",
        packaged_skill / "hooks/capabilities/over_length/runtime.py",
        packaged_skill / "hooks/capabilities/delivery_cleanliness/runtime.py",
        packaged_skill / "hooks/shared/hard_anchors.py",
        packaged_skill / "scripts/review_gate.py",
        output / adapter.capability_target,
        output / "README.md",
        output / "LICENSE",
    ]
    if expected_manifest is not None:
        required.append(expected_manifest)
    if adapter.name == "hermes-agent":
        required.append(packaged_skill / "hooks/single_pass_final_review.py")
    if adapter.hooks_target is not None:
        required.append(output / adapter.hooks_target)
    required.extend(output / target for _, target in adapter.extra_files)
    missing = [path.relative_to(output).as_posix() for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"incomplete Hook companion: {missing}")
    manifest_names = {
        "plugin.json",
        "qwen-extension.json",
        "kimi.plugin.json",
        "plugin.yaml",
        "package.json",
    }
    manifests = sorted(
        path
        for path in output.rglob("*")
        if path.is_file() and path.name in manifest_names
    )
    expected_manifests = [expected_manifest] if expected_manifest is not None else []
    if manifests != expected_manifests:
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
    if host == "hermes-agent" and capability != CAPABILITY_DEFAULT:
        raise ValueError("Hermes Agent currently supports delivery_review only")
    output = output.expanduser().resolve()
    if output.exists():
        raise FileExistsError(f"output already exists: {output}")
    output.mkdir(parents=True)
    try:
        _copy_skill(output, adapter)
        if adapter.manifest_target is not None:
            _copy(
                adapter.manifest_source or adapter.source_root / "manifest.json",
                output / adapter.manifest_target,
            )
        if adapter.hooks_target is not None:
            _copy(adapter.source_root / "hooks.json", output / adapter.hooks_target)
        _copy(adapter.adapter_source, output / adapter.adapter_target)
        for source, target in adapter.extra_files:
            _copy(source, output / target)
        _copy(adapter.source_root / "README.md", output / "README.md")
        _copy(SKILL_ROOT / "LICENSE", output / "LICENSE")
        capability_path = output / adapter.capability_target
        capability_path.parent.mkdir(parents=True, exist_ok=True)
        capability_path.write_text(
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
