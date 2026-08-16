#!/usr/bin/env python3
"""Mechanically partition the frozen R3 blind packet without reading its mapping."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PARTITIONS = {
    "a": ["G01", "G03", "G04", "G06", "G07", "G08", "G09"],
    "b": ["G10", "G11", "G12", "G13", "G14", "G15"],
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def atomic_write(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(value)
    temporary.replace(path)


def split_sections(packet: str) -> tuple[str, dict[str, str]]:
    lines = packet.splitlines(keepends=True)
    starts = [index for index, line in enumerate(lines) if line.startswith("## G")]
    if not starts:
        raise RuntimeError("blind packet has no group sections")
    preamble = "".join(lines[: starts[0]])
    sections: dict[str, str] = {}
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        section = "".join(lines[start:end])
        group = section.splitlines()[0].split(" | ", 1)[0].removeprefix("## ")
        if group in sections:
            raise RuntimeError(f"duplicate group: {group}")
        sections[group] = section
    return preamble, sections


def build(packet_path: Path, template_path: Path, output: Path) -> None:
    if output.exists():
        raise RuntimeError(f"output must not exist: {output}")
    packet_bytes = packet_path.read_bytes()
    template_bytes = template_path.read_bytes()
    packet = packet_bytes.decode("utf-8")
    template = json.loads(template_bytes)
    preamble, sections = split_sections(packet)
    template_groups = {item["group"]: item for item in template["groups"]}
    expected = [group for groups in PARTITIONS.values() for group in groups]
    if list(sections) != expected or list(template_groups) != expected:
        raise RuntimeError("source group order does not match frozen partition contract")
    output.mkdir(parents=True)
    manifest = {
        "schema_version": 1,
        "source_packet_sha256": sha256_bytes(packet_bytes),
        "source_template_sha256": sha256_bytes(template_bytes),
        "partitions": {},
    }
    for name, groups in PARTITIONS.items():
        part = output / name
        packet_text = preamble + "\n".join(sections[group].rstrip() for group in groups) + "\n"
        template_value = {
            "schema_version": template["schema_version"],
            "allowed_draft_verdicts": template["allowed_draft_verdicts"],
            "allowed_winners": template["allowed_winners"],
            "groups": [template_groups[group] for group in groups],
        }
        packet_out = part / "blind-packet.md"
        template_out = part / "judge-template.json"
        atomic_write(packet_out, packet_text.encode("utf-8"))
        atomic_write(
            template_out,
            (json.dumps(template_value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )
        manifest["partitions"][name] = {
            "groups": groups,
            "packet_sha256": sha256_bytes(packet_out.read_bytes()),
            "template_sha256": sha256_bytes(template_out.read_bytes()),
        }
    atomic_write(
        output / "partition-manifest.json",
        (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    build(args.packet.resolve(), args.template.resolve(), args.out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
